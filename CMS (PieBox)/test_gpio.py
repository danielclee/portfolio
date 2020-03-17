import logging
import re
import _thread
import threading
import json
import math
import time
import hashlib
import json
from queue import Queue
from threading import Timer
from time import sleep
from gpiocontroller import GPIOController
from link import Link
from sandtimer import SandTimer

_gpioLink = Link()

def StartGPIOThread():
    gpiothread = GPIOController(_gpioLink)
    gpiothread.Run()


def gpiotest():
    print("Starting gpio test")

    # Start gpio thread
    _gpiothread = threading.Thread(name='gpiothread',
                                   target=StartGPIOThread)
    _gpiothread.start()

    # Listen for gpio events
    _gpioLink.SendCmd('{"action":"setup_io", "inputs":"pb01,pb02", "throttle":"0.35", "debounce":"3"}')
    while True:
        try:
            event = _gpioLink.CheckEventQ(blocking=True, wait=None)
            print(event)
        except:
            break
    _gpioLink.SendCmd('{"action":"exit"}')
    _gpiothread.join()


def gpiotest2():
    global _gpioLink

    print("Starting gpio test, Ctrl-c to exit")
    inputledlut = {"pb01":"led01", "pb02":"led02", "pb03":"led03", "pb04":"led04", "pb05":"led05", "pb06":"led06", "pb07":"led07", "pb08":"led08"}
    _gpiothread = None
    try:
        # Start gpio thread
        _gpiothread = threading.Thread(name='gpiothread',
                                       target=StartGPIOThread)
        _gpiothread.start()
        sleep(1.0)
        
        ledtimerlut = {}
        triggerslist = []
        inputs = input("Enter inputs to activate (i.e. 1[,2,3,4,5,6,7,8,ms] : ")
        for i in inputs.split(","):
            inputstr = ""
            if i == "1":
                inputstr = "pb01"
            elif i == "2":
                inputstr = "pb02"
            elif i == "3":
                inputstr = "pb03"
            elif i == "4":
                inputstr = "pb04"
            elif i == "5":
                inputstr = "pb05"
            elif i == "6":
                inputstr = "pb06"
            elif i == "7":
                inputstr = "pb07"
            elif i == "8":
                inputstr = "pb08"
            elif i == "ms":
                inputstr = GPIOController.MOTION_SENSOR
            else:
                errmsg = "Invalid input : " + inputstr
                raise Exception(errmsg)
            triggerslist.append(inputstr)
            if inputstr in inputledlut:
                ledstr = inputledlut[inputstr]
                ledtimerlut[inputstr] = SandTimer(1.0, ledstr)

        # Setup I/O
        _gpioLink.SendCmd(json.dumps({"action" : "setup_io",
                                      "inputs" : ",".join(triggerslist),
                                      "throttle" : "0.45",
                                      "debounce" : "3"}))

        # Listen for gpio events
        while True:
            # Handle input event
            event = _gpioLink.CheckEventQ(blocking=True, wait=0.1)
            if event != None:
                event_json = json.loads(event)
                input_event = event_json[GPIOController.INPUT_EVENT]
                input_type = event_json[GPIOController.TYPE]
                input_status = event_json[GPIOController.STATUS]
                print("--------------------------------")
                print("input : " + input_event)
                print("type : " + input_type)
                print("status : " + input_status)
                
                if input_event in ledtimerlut:
                    led = inputledlut[input_event]
                    _gpioLink.SendCmd(json.dumps({GPIOController.ACTION : GPIOController.LED_ON,
                                                  GPIOController.OUTPUTS : led}))
                    ledtimerlut[input_event].Start()

            # Check led timers
            for ledtimer in list(ledtimerlut.values()):
                if ledtimer.CheckExpired():
                    _gpioLink.SendCmd(json.dumps({GPIOController.ACTION : GPIOController.LED_OFF,
                                                  GPIOController.OUTPUTS : ledtimer.GetLabel()}))
                    ledtimer.Stop()
    except Exception as e:
        print(str(e) + " -- exitting")
    finally:
        if _gpiothread != None:
            _gpioLink.SendCmd('{"action":"exit"}')
            _gpiothread.join()
            _gpiothread = None


def main():
    loglevel = logging.DEBUG
    logformat = '%(asctime)s [%(levelname)s] %(pathname)s::%(funcName)s(%(lineno)s) - %(message)s'
    loghandlers = [logging.FileHandler('test_log.log'), logging.StreamHandler()]
    logging.basicConfig(level = loglevel, format = logformat, handlers = loghandlers)

    # Test playlist
    ## gpiotest()
    gpiotest2()


if __name__ == "__main__":
    main()
