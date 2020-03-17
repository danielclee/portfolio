import logging
import _thread
import threading
import traceback
import collections
import copy
from time import sleep
from threading import Timer
from enum import Enum
from sandtimer import SandTimer
from videoplayer import VideoPlayer
from gpiocontroller import GPIOController
from datastore import DataStore
from delivery import Delivery
from analytics import Analytics
from office import Office
from order import Order 

class ThreadMonitor:
    class ThreadType(Enum):
        VIDEO = 1
        GPIO = 2
        DELIVERY = 3
        OFFICE = 4
        ANALYTICS = 5
        ORDER = 6


    def __init__(self):
        self.threadTimerLut = {}
        self.threadTimerLut[ThreadType.VIDEO] = SandTimer(5.0, "Video")
        self.threadTimerLut[ThreadType.GPIO] = SandTimer(5.0, "GPIO")
        self.threadTimerLut[ThreadType.DELIVERY] = SandTimer(5.0, "Delivery")
        self.threadTimerLut[ThreadType.OFFICE] = SandTimer(5.0, "Office")
        self.threadTimerLut[ThreadType.ANALYTICS] = SandTimer(5.0, "Analytics")
        self.threadTimerLut[ThreadType.ORDER] = SandTimer(5.0, "Order")


    def Reset(self, threadtype):
    timer = self.threadTimerLut.get(threadtype)
        if timer == None:
            logging.error("Threadtype not found!!!!")
            raise
        else:
            timer.Reset()


    def Check(self):
        for t in self.threadTimerLut.values():
            if t.CheckExpired():
                logging.error(t.GetLabel() + " thread timed out")
                return False
        return True
