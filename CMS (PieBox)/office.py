import logging
import re
import threading
import json
import math
import time
import hashlib
import collections
import traceback
import tkinter
import tkinter.ttk as ttk
from threading import Timer
from time import sleep
from link import Link
from easygui import *

class Office:
    # Constants
    EVENT = "event"
    EXIT = "exit"
    ERROR = "error"
    USEROPTION1 = "useroption1"
    SETTINGS = "settings"
    TOKEN = "token"
    INFO = "info"
    PROGRESS = "progress"
    MESSAGE = "message"
    STOP = "stop"
    DONE = "done"
    SERIAL = "serial"
    HARDWARE = "hardware"
    MODEL = "model"
    PRODUCT = "product"
    VERSION = "version"
    UUID = "uuid"
    TOTAL = "total"
    ACTION = "action"
    CHECKIN = "checkin"
    ANALYTICS = "analytics"
    IODEBOUNCE = "iodebounce"
    IOTHROTTLE = "iothrottle"
    DEVICEID = "deviceid"
    TITLE = "title"
    BTN_EXIT = "Exit"
    BTN_CHANGE_SETTINGS = "Change Settings"
    BTN_CHANGE_DEVICEID = "Change Device ID"
    BTN_CANCEL = "Cancel"
    BTN_SELECTED = "btn_selected"
    CHANGE_DEVICEID = "change_deviceid"
    NONE = "none"

    def __init__(self, link):
        self._link = link
        self._running = True
        self._tkRoot = None
        self._progressbar = None


    def Cleanup(self):
        if self._progressbar != None:
            self._progressbar.destroy()
            self._progressbar = None
        if self._tkRoot != None:
            self._tkRoot.destroy()
            self._tkRoot = None


    def Run(self):
        self._running = True
        while self._running:
            msg = self._link.CheckCmdQ(blocking=True, wait=0.1)
            if msg != None:
                logging.debug(msg)
                cmd_json = json.loads(msg)
                action = cmd_json[Office.ACTION]
                if action == Office.SETTINGS:
                    self.ShowSettings(cmd_json[Office.CHECKIN],
                                      cmd_json[Office.ANALYTICS],
                                      cmd_json[Office.IODEBOUNCE],
                                      cmd_json[Office.IOTHROTTLE])
                elif action == Office.CHANGE_DEVICEID:
                    self.ChangeDeviceID(cmd_json[Office.DEVICEID])
                elif action == Office.TOKEN:
                    self.ShowToken(cmd_json[Office.TOKEN])
                elif action == Office.MESSAGE:
                    self.ShowMessage(cmd_json[Office.MESSAGE])
                elif action == Office.INFO:
                    self.ShowInfo(cmd_json[Office.SERIAL],
                                  cmd_json[Office.HARDWARE],
                                  cmd_json[Office.MODEL],
                                  cmd_json[Office.PRODUCT],
                                  cmd_json[Office.VERSION],
                                  cmd_json[Office.UUID])
                elif action == Office.PROGRESS:
                    self.ShowProgress(cmd_json[Office.TITLE],
                                      cmd_json[Office.TOTAL],
                                      cmd_json[Office.PROGRESS])
                elif action == Office.USEROPTION1:
                    self.ShowUserOption1()
                elif action == Office.ERROR:
                    self.ShowError(cmd_json[Office.ERROR])
                elif action == Office.EXIT:
                    self._running = False
            # End if
        # End while
        self.Cleanup()


    def ShowProgress(self, title, total, progress):
        if self._progressbar == None:
            self._tkRoot = tkinter.Tk()
            self._tkRoot.geometry('{}x{}'.format(400, 100))
            self._tkRoot.title("Download progress")
            self._progressvar = tkinter.DoubleVar()
            self._progressLabel = tkinter.Label(self._tkRoot, text=title)
            self._progressLabel.pack()
            self._progressbar = ttk.Progressbar(self._tkRoot,
                                                variable=self._progressvar,
                                                maximum=total)
            self._progressbar.pack(fill=tkinter.X, expand=1)
            self._progressbar.pack()
        else:
            self._progressvar.set(progress)
            self._progressLabel['text'] = title
            self._tkRoot.update_idletasks()
            if progress >= total:
                self._progressbar.destroy()
                self._progressbar = None
                self._tkRoot.destroy()
                self._tkRoot = None
                self.SendDone()


    def ShowInfo(self, serial, hardware, model, product, version, uuid):
        msg = "Device Info"
        title = "Device Info"
        info = ("Serial : {s}\nHardware : {h}\nModel : {m}\n"
                "Product : {p}\nVersion : {v}\nUUID : {u}".\
               format(s=serial, h=hardware, m=model,
                      p=product, v=version, u=uuid))
        msgbox(info)
        self.SendDone()


    def ShowToken(self, token):
        msgbox(msg="Please enter token at https://fulgent.sandd.studio/ to activate device\n" + token)
        self.SendDone()


    def ShowMessage(self, msg):
        msgbox(msg)
        self.SendDone()


    def ShowSettings(self, checkin, analytics, iodebounce, iothrottle):
        msg = "Settings"
        title = "Settings"
        checkin_label = ("Check-in rate (secs) [default=86400] [current={c}]".\
                         format(c=checkin))
        analytics_label = ("Send analytics rate (secs) [default=86400] [current={c}]".\
                           format(c=analytics))
        iodebounce_label = ("IO debounce [default=3] [current={c}]".\
                            format(c=iodebounce))
        iothrottle_label = ("IO throttle (millisecs) [default=450] [current={c}]".\
                            format(c=str(float(iothrottle) * 1000)))
        fieldnames = [checkin_label, analytics_label, iodebounce_label, iothrottle_label]
        logging.info(checkin_label)
        logging.info(analytics_label)
        logging.info(iodebounce_label)
        logging.info(iothrottle_label)
        fieldvalues = multenterbox(msg, title, fieldnames)

        # Validate input
        errmsg = ""
        for i, name in enumerate(fieldnames):
            if fieldvalues != None:
                val = fieldvalues[i].strip()
                if val == "":
                    continue
                errorstr = ""
                if name == checkin_label:
                    val = float(val)
                    if (val > 29) and (val < 86401):
                        checkin = val
                    else:
                        errmsg = "Invalid check-in period (30 to 86400 secs)"
                elif name == analytics_label:
                    val = float(val)
                    if (val > 29) and (val < 86401):
                        analytics = val
                    else:
                        errmsg = "Invalid send analytics period (30 to 86400 secs)"
                elif name == iodebounce_label:
                    val = int(val)
                    if (val > 0) and (val < 10):
                        iodebounce = val
                    else:
                        errmsg = "Invalid IO debounce value (1 to 9)"
                elif name == iothrottle_label:
                    val = float(val)
                    if (val > 0) and (val < 1000):
                        iothrottle = float(val) / 1000
                    else:
                        errmsg = "Invalid IO throttle value (1 to 1000 millisecs)"
                if errmsg != "":
                    msgbox(errmsg)
            # End if

        # Send values back
        logging.info("New settings")
        checkin_label = ("Check-in rate (secs) [default=86400] [current={c}]".\
                         format(c=checkin))
        analytics_label = ("Send analytics rate (secs) [default=86400] [current={c}]".\
                           format(c=analytics))
        iodebounce_label = ("IO debounce [default=3] [current={c}]".\
                            format(c=iodebounce))
        iothrottle_label = ("IO throttle (millisecs) [default=450] [current={c}]".\
                            format(c=str(float(iothrottle) * 1000)))
        logging.info(checkin_label)
        logging.info(analytics_label)
        logging.info(iodebounce_label)
        logging.info(iothrottle_label)
        self._link.SendEvent(json.dumps({Office.EVENT : Office.SETTINGS,
                                         Office.CHECKIN : checkin,
                                         Office.ANALYTICS : analytics,
                                         Office.IODEBOUNCE : iodebounce,
                                         Office.IOTHROTTLE: iothrottle}))
        self.SendDone()


    def ShowUserOption1(self):
        msg = "Please select option"
        title = "Keyboard Detected"
        choices = [Office.BTN_CANCEL,
                   Office.BTN_EXIT,
                   Office.BTN_CHANGE_SETTINGS,
                   Office.BTN_CHANGE_DEVICEID]
        reply = buttonbox(msg, choices=choices)
        print(reply)
        if reply == None:
            reply = Office.BTN_CANCEL
        self._link.SendEvent(json.dumps({Office.EVENT : Office.BTN_SELECTED,
                                         Office.BTN_SELECTED : reply}))


    def ChangeDeviceID(self, deviceid):
        msg = "Device ID"
        title = "Device ID"
        deviceid_label = ("Device ID [current={d}]".format(d=deviceid))
        fieldnames = [deviceid_label]
        logging.info(deviceid_label)
        fieldvalues = multenterbox(msg, title, fieldnames)
        print(fieldvalues)

        # Validate input
        if fieldvalues != None:
            for i, name in enumerate(fieldnames):
                val = fieldvalues[i].strip()
                if val == "":
                    continue
                if name == deviceid_label:
                    pattern = re.compile(r'^[a-zA-Z0-9]{8}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{12}$')
                    if re.search(pattern, val):
                        deviceid = val

        # Send done back
        logging.info("New device ID")
        deviceid_label = ("Device ID [current={d}]".format(d=deviceid))
        logging.info(deviceid_label)
        self._link.SendEvent(json.dumps({Office.EVENT : Office.DEVICEID,
                                         Office.DEVICEID : deviceid}))
        self.SendDone()


    def ShowError(self, error):
        msgbox(error)
        self.SendDone()


    def SendDone(self):
        self._link.SendEvent(json.dumps({Office.EVENT : Office.DONE}))
