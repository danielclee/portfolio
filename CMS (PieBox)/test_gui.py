import re
import threading
import json
import math
import time
import logging
import logging.handlers
from threading import Timer
from time import sleep
from link import Link
from office import Office
## from tkinter import Tk
import tkinter as tk
import hashlib
import json
import collections
import datetime
from easygui import *

MAX = 10000

_officeLink = Link()

def StartOfficeThread():
    office = Office(_officeLink)
    office.Run()


def testeasygui():
    logging.info('Before msgbox : %s' % datetime.datetime.now())
    msgbox("Hello World")
    logging.info('After msgbox : %s' % datetime.datetime.now())

    ###############################################
    
    ## msg = "Enter your personal information"
    ## title = "Credit Card Application"
    ## fieldNames = ["Name", "Street Address", "City", "State", "ZipCode"]
    ## fieldValues = multenterbox(msg, title, fieldNames)
    ## if fieldValues is None:
    ##     sys.exit(0)
    ## # make sure that none of the fields were left blank
    ## while 1:
    ##     errmsg = ""
    ##     for i, name in enumerate(fieldNames):
    ##         if fieldValues[i].strip() == "":
    ##           errmsg += "{} is a required field.\n\n".format(name)
    ##     if errmsg == "":
    ##         break # no problems found
    ##     fieldValues = multenterbox(errmsg, title, fieldNames, fieldValues)
    ##     if fieldValues is None:
    ##         break
    ## logging.info("Reply was:{}".format(fieldValues))


def testtk():
    root=tk.Tk()
    app=FullScreenApp(root)
    root.mainloop()


def testoffice():
    officethread = threading.Thread(name='officethread',
                                    target=StartOfficeThread)
    officethread.start()


def main():
    logging.info("Starting test_gui.py")

    # Test office
    testoffice()
    
    # Test easy gui
    ## testeasygui()

    # Test tkinter
    ## testtk()

    # Test change device ID
    ## _officeLink.SendCmd(json.dumps({Office.ACTION : Office.USEROPTION1}))
    ## msg = _officeLink.CheckEventQ(blocking=True, wait=None)  # blocking
    ## logging.info(msg)
    ## event_json = json.loads(msg)
    ## event = str(event_json[Office.EVENT])
    ## if event == Office.BTN_SELECTED:
    ##     choice = event_json[Office.BTN_SELECTED]
    ##     if choice == Office.BTN_EXIT:
    ##         logging.info("Exit button pressed")
    ##     elif choice == Office.BTN_CHANGE_DEVICEID:
    ##         _officeLink.SendCmd(json.dumps({Office.ACTION : Office.CHANGE_DEVICEID,
    ##                                         Office.DEVICEID : "502e22e6-0bf3-48cc-a4d6-4d5502bf642f"}))
    ##         msg = _officeLink.CheckEventQ(blocking=True, wait=None)
    ##         logging.info(msg)

    _officeLink.SendCmd(json.dumps({Office.ACTION : Office.TOKEN,
                                    Office.TOKEN : "45G450"}))

    ##_officeLink.SendCmd(json.dumps({Office.ACTION : Office.SETTINGS,
    ##                                Office.CHECKIN : "60",
    ##                                Office.ANALYTICS : "60",
    ##                                Office.IODEBOUNCE : "3",
    ##                                Office.IOTHROTTLE: "500"}))
    
    gg = 0
    shutdown = True
    while True:
        sleep(1.0)
        gg += 1

        
        ################################################################
        ##if gg <= MAX:
        ##    ################################################################
        ##    _officeLink.SendCmd(json.dumps({Office.ACTION : Office.PROGRESS,
        ##                                    Office.TITLE : "test",
        ##                                    Office.PROGRESS : gg,
        ##                                    Office.TOTAL : MAX}))
        ##else:
        ##    if shutdown:
        ##        _officeLink.SendCmd(json.dumps({Office.ACTION : "exit"}))
        ##        shutdown = False

        ################################################################
        ## _officeLink.SendCmd(json.dumps({Office.ACTION : Office.INFO,
        ##                                 Office.UUID : "sdsds-dsd-sddsd-sds"}))

        ################################################################
        ## _officeLink.SendCmd(json.dumps({Office.ACTION : Office.TOKEN,
        ##                                 Office.TOKEN : "45G450"}))

        ################################################################
        ## _officeLink.SendCmd(json.dumps({Office.ACTION : Office.SETTINGS,
        ##                                 Office.CHECKIN : "60",
        ##                                 Office.ANALYTICS : "60",
        ##                                 Office.IODEBOUNCE : "3",
        ##                                 Office.IOTHROTTLE: "500"}))


if __name__ == "__main__":
    logfile = 'test_gui.log'
    logrotatesize = 20971520  # 20mb
    logmaxfiles = 1000
    loglevel = logging.DEBUG
    logformat = '%(asctime)s [%(levelname)s] %(pathname)s::%(funcName)s(%(lineno)s) - %(message)s'
    loghandlers = [logging.StreamHandler(), logging.handlers.RotatingFileHandler(logfile,
                                                        maxBytes=logrotatesize,
                                                        backupCount=logmaxfiles)]
    logging.basicConfig(level = loglevel, format = logformat, handlers = loghandlers)

    main()
    
