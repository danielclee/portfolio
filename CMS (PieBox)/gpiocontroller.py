import logging
import re
import json
import enum
import os.path
import atexit
import traceback
import RPi.GPIO as GPIO
from pathlib import Path
from queue import *
from link import Link
from time import sleep
from threading import Timer
from sandtimer import SandTimer

## GPIOs : [ BCM4,  BCM5,  BCM6,  BCM12, BCM13,
##           BCM16, BCM17, BCM18, BCM19, BCM20,
##           BCM21, BCM22, BCM23, BCM24, BCM25,
##           BCM26, BCM27 ]
## 
## PB GPIO : [ BCM6, BCM13, BCM19, BCM26, BCM12, 
##             BCM16, BCM20, BCM21 ]
##
## LED GPIO : [ BCM17, BCM27, BCM22, BCM18, 
##              BCM23, BCM24, BCM25, BCM8 ]
##           
## MS GPIO : [ BCM4 ]
    
class GPIOController:
    # Constants
    ACTION = "action"
    EXIT = "exit"
    MOTION = "motion"
    INPUT = "input"
    INPUT_EVENT = "input_event"
    STATUS = "status"
    ACTIVE = "active"
    INACTIVE = "inactive"
    LED_ON = "led_on"
    LED_OFF = "led_off"
    LED_BLINK = "led_blink"
    INTERVAL = "interval"
    OUTPUTS = "outputs"
    INPUTS = "inputs"
    TYPE = "type"
    PUSH_BUTTON = "pb"
    MOTION_SENSOR = "ms"
    RESET = "reset"
    SETUP_IO = "setup_io"
    
    def __init__(self, link):
        self._link = link;
        self.running = True
        atexit.register(self.Cleanup)
        # Setup I/O
        GPIO.setmode(GPIO.BCM)
        self.inputs = {"pb01":6, "pb02":13, "pb03":19, "pb04":26, "pb05":12, "pb06":16, "pb07":20, "pb08":21}
        self.outputs = {"led01":17, "led02":27, "led03":22, "led04":18, "led05":23, "led06":24, "led07":25, "led08":8}
        self.msinput = {4:GPIOController.MOTION_SENSOR}
        self.msInputPin = 4
        self.activeinputs = {}
        self.blinklut = {}
        self.blinktimer = SandTimer(1)
        self.blinktimer.Stop()
        self.throttletimer = SandTimer(0.35)
        self.throttletimer.Stop()
        self.debouncefilter = 3
        self.debouncekount = 0
        self.motionSensorActive = False
        # Setup GPIO output 
        logging.info("Setup GPIO output")
        for key, value in self.outputs.items():
            GPIO.setup(value, GPIO.OUT)
        self.Reset()


    def Cleanup(self):
        GPIO.cleanup()


    def Reset(self):
        logging.debug("Reset GPIO input/output")
        for key, value in self.inputs.items():
            GPIO.setup(value, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.msInputPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        for key, value in self.outputs.items():
            GPIO.output(value, GPIO.LOW)
        self.activeinputs.clear()
        self.blinklut.clear()
        self.blinktimer.Stop()
        self.motionSensorActive = False


    def Run(self):
        sleep(3.0)
        while self.running:
            # Check IO events
            self.CheckIO()

            # Check for messages
            msg = self._link.CheckCmdQ(blocking=True, wait=0.1)
            if msg != None:
                self.GPIOCmd(msg)
                if self.blinktimer.CheckExpired():
                    self.HandleBlinkTimer()
        logging.info("Exiting GPIOController")


    def GPIOCmd(self, message):
        ##'{"action":"reset"}'
        ##'{"action":"setup_io", "inputs":"pb01,pb02", "debounce":"1", "throttle":"250"}'
        ##'{"action":"led_on", "outputs":"led01,led02"}'
        ##'{"action":"led_off", "outputs":"led01,led02"}'
        ##'{"action":"led_blink", "outputs":"led01,led02", "interval":"1"}'
        ##'{"input_event":"[pb0X | ms]", "type":"pb | ms", "status":"active | inactive"}'
        logging.debug(message)
        io_json = json.loads(message)
        action = io_json['action']
        if action == GPIOController.RESET:
            self.Reset()
        elif action == GPIOController.SETUP_IO:
            self.Reset()
            inputlist = io_json['inputs']

            # Setup any pushbuttons
            for key, value in self.inputs.items():
                if inputlist.find(key) > -1:
                    logging.debug("GPIO pin set active " + key + ", " + str(value))
                    self.activeinputs[key] = value
                    GPIO.setup(value, GPIO.IN)
                else:
                    logging.debug("GPIO pin set INACTIVE " + key + ", " + str(value))
                    GPIO.setup(value, GPIO.IN, pull_up_down=GPIO.PUD_UP)

            # Check for motion sensor and setup
            if GPIOController.MOTION_SENSOR in inputlist:
                logging.debug("GPIO motion sensor pin set active " +
                              GPIOController.MOTION_SENSOR + ", " + str(self.msInputPin))
                self.activeinputs[GPIOController.MOTION_SENSOR] = self.msInputPin
                GPIO.setup(self.msInputPin, GPIO.IN)

            # Set debounce value
            self.debouncefilter = int(io_json['debounce'])
            logging.debug("debounce filter set to : " + str(self.debouncefilter))
            self.debouncekount = self.debouncefilter

            # Set throttle' value
            throttle = float(io_json['throttle'])
            logging.debug("throttle set to : " + str(throttle))
            self.throttletimer.Start(throttle)
        elif action == GPIOController.LED_ON:   # led on
            outputlist = io_json['outputs'].split(",")
            for o in outputlist:
                self.LedAction(o, on=True)
        elif action == GPIOController.LED_OFF:  # led off
            outputlist = io_json['outputs'].split(",")
            for o in outputlist:
                self.LedAction(o, on=False)
        elif action == GPIOController.LED_BLINK:  # led blink
            self.blinklut.clear()
            outputlist = io_json['outputs'].split(",")
            interval = io_json['interval']
            for o in outputlist:
                self.LedAction(o, on=True)
                self.blinklut[o] = True
            self.blinktimer.Start(float(interval));
        elif action == 'exit':
            self.running = False
                

    def CheckIO(self):
        for key, value in self.activeinputs.items():
            if GPIO.input(value):  # input active
                if key == GPIOController.MOTION_SENSOR:
                    if self.motionSensorActive == False:
                        self.motionSensorActive = True
                        self._link.SendEvent(json.dumps({GPIOController.INPUT_EVENT : key,
                                                         GPIOController.TYPE : GPIOController.MOTION_SENSOR,
                                                         GPIOController.STATUS : GPIOController.ACTIVE}))
                else:    # pushbutton
                    self.debouncekount =- 1
                    if self.debouncekount <= 0:
                        if self.throttletimer.CheckExpired():
                            self._link.SendEvent(json.dumps({GPIOController.INPUT_EVENT : key,
                                                             GPIOController.TYPE : GPIOController.PUSH_BUTTON,
                                                             GPIOController.STATUS : GPIOController.ACTIVE}))
                            self.throttletimer.Reset()
                            self.debouncekount = self.debouncefilter
            else:   # input not active
                if key == GPIOController.MOTION_SENSOR:
                    if self.motionSensorActive == True:
                        self.motionSensorActive = False
                        self._link.SendEvent(json.dumps({GPIOController.INPUT_EVENT : key,
                                                         GPIOController.TYPE : GPIOController.MOTION_SENSOR,
                                                         GPIOController.STATUS : GPIOController.INACTIVE}))


    def LedAction(self, led, on):
        if not led in self.outputs:
            logging.debug("Invalid led " + led)
            return
        pin = self.outputs[led]
        if on:
            logging.debug("Set GPIO led " + led + " pin " + str(pin) + " to HIGH")
            GPIO.output(pin, GPIO.HIGH)
        else:
            logging.debug("Set GPIO led " + led + " pin " + str(pin) + " to LOW")
            GPIO.output(pin, GPIO.LOW)


    def HandleBlinkTimer(self):
        logging.debug("Handling blink timer")
        for key, value in self.blinklut.items():
            if value:
                self.LedAction(key, on=False)
                self.blinklut[key] = False
            else:
                self.LedAction(key, on=True)
                self.blinklut[key] = True
