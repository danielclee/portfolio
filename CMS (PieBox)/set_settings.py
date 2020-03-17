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
from settings import Settings
from office import Office
import hashlib
import json
import collections
import datetime
from easygui import *

def StartOfficeThread():
    global _officeLink
    office = Office(_officeLink)
    office.Run()


def main():
    global _officeLink

    # Initialize settings
    settings = Settings("piebox_settings.p")
    if settings.Load() == True:
        logging.info("Found an existing settings file, aborting")
        settings.ToScreen()
        return

    # Set settings
    logging.info("--------------- Setting Settings")
    _officeLink.SendCmd(json.dumps({Office.ACTION : Office.SETTINGS,
                                    Office.CHECKIN : 600.0,
                                    Office.ANALYTICS : 600.0,
                                    Office.IODEBOUNCE : 3,
                                    Office.IOTHROTTLE: 0.45}))
    settings_done = False
    while True:
        msg = _officeLink.CheckEventQ(blocking=True, wait=None)  # blocking
        logging.info(msg)
        settings_json = json.loads(msg)
        event = settings_json[Office.EVENT]
        if event == Office.SETTINGS:
            settings.SetCheckinTimerValue(float(settings_json[Office.CHECKIN]), False)
            settings.SetAnalyticsTimerValue(float(settings_json[Office.ANALYTICS]), False)
            settings.SetIODebounce(settings_json[Office.IODEBOUNCE], False)
            settings.SetIOThrottle(settings_json[Office.IOTHROTTLE], False)
            settings_done = True
        elif event == Office.DONE:
            break
    # End while
    if settings_done == False:
        logging.info("No settings set, aborting")
        return

    # Set device ID
    logging.info("--------------- Setting Device ID")
    _officeLink.SendCmd(json.dumps({Office.ACTION : Office.CHANGE_DEVICEID,
                                    Office.DEVICEID : Office.NONE}))
    settings_done = False
    while True:
        msg = _officeLink.CheckEventQ(blocking=True, wait=None)
        logging.info(msg)
        settings_json = json.loads(msg)
        event = settings_json[Office.EVENT]
        if event == Office.DEVICEID:
            newdeviceid = settings_json[Office.DEVICEID]
            newdeviceurl = ("https://fulgent.sandd.studio/api/v1.0/devices/{d}".format(d=newdeviceid))
            settings.SetDeviceID(newdeviceid, save=False)
            settings.SetDeviceResourceURL(newdeviceurl, save=False)
            settings.SetToken("debug", save=False)
            settings_done = True
        elif event == Office.DONE:
            break
    # End while
    if settings_done == False:
        logging.info("No settings set, aborting")
        return

    # Save settings
    logging.info("Saving settings file")
    settings.Save()
    settings.ToString()


if __name__ == "__main__":
    _officeLink = Link()

    loglevel = logging.DEBUG
    logformat = '%(asctime)s [%(levelname)s] %(pathname)s::%(funcName)s(%(lineno)s) - %(message)s'
    loghandlers = [logging.StreamHandler()]
    logging.basicConfig(level = loglevel, format = logformat, handlers = loghandlers)

    # Start office thread
    logging.info("Starting Office thread")
    _officeThread = threading.Thread(name='officethread', target=StartOfficeThread)
    _officeThread.start()

    # Do stuff
    main()

    # Cleanup
    _officeLink.SendCmd(json.dumps({Office.ACTION : Office.EXIT}))
    _officeThread.join()
    _officeThread = None
