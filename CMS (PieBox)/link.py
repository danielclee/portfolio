import logging
import re
import json
import enum
import os.path
import threading
import copy
from queue import *
from time import sleep
from threading import Timer
from sandtimer import SandTimer

class Link:
    def __init__(self):
        self._cmdQueue = Queue()
        self._eventQueue = Queue()
        self._cmdLock = threading.Lock()
        self._objectCache = None
        self._objectCacheLock = threading.Lock()


    def CheckCmdQ(self, blocking=False, wait=None):  # bool, sec
        try:
            self._cmdLock.acquire()
            # if block to True, it is timeout that determines if blocking or not
            # - None is wait forever, 0.01 to 1 wait seconds
            # if block to False, then will immediately throw Empty
            msg = self._cmdQueue.get(block=blocking, timeout=wait)
            self._cmdQueue.task_done()
            return msg
        except Empty:
            return None
        finally:
            if self._cmdLock.locked():
                self._cmdLock.release()
        return None


    def CheckEventQ(self, blocking=False, wait=None):  # bool, sec
        try:
            # if block to True, it is timeout that determines if blocking or not
            # if block to False, then will immediately throw Empty
            msg = self._eventQueue.get(block=blocking, timeout=wait)
            self._eventQueue.task_done()
            return msg
        except Empty:
            return None
        return None


    def SendCmd(self, cmd):  # string
        try:
            self._cmdQueue.put_nowait(cmd)
            return True
        except Full:
            return False;


    def SendBatchCmd(self, cmdlist):  # list<string>
        try:
            self._cmdLock.acquire()
            for cmd in cmdlist:
                self._cmdQueue.put_nowait(cmd)
            return True
        except Full:
            return False;
        finally:
            if self._cmdLock.locked():
                self._cmdLock.release()


    def SendEvent(self, event):  # string
        try:
            self._eventQueue.put_nowait(event)
            return True
        except Full:
            return False;


    def Clear(self):
        # Clear cmd Q
        try:
            while not self._cmdQueue.empty():
                msg = self._cmdQueue.get(block=False)
                self._cmdQueue.task_done()
        except Empty:
            logging.error("Error emptying cmd queue")

        # Clear event Q
        try:
            while not self._eventQueue.empty():
                msg = self._eventQueue.get(block=False)
                self._eventQueue.task_done()
        except Empty:
            logging.error("Error emptying event queue")

        # Clear rest
        self._objectCache = None
        if self._cmdLock.locked():
            self._cmdLock.release()
        if self._objectCacheLock.locked():
            self._objectCacheLock.release()


    def SetObjectCache(self, object):
        try:
            self._objectCacheLock.acquire()
            self._objectCache = object
        except Exception as e:
            logging.error(e)
            logging.exception(traceback.format_exc())
        finally:
            if self._objectCacheLock.locked():
                self._objectCacheLock.release()


    def GetObjectCache(self):
        try:
            self._objectCacheLock.acquire()
            if self._objectCache == None:
                return None
            tmp = copy.deepcopy(self._objectCache)
            self._objectCache = None
            return tmp
        except Exception as e:
            logging.error(e)
            logging.exception(traceback.format_exc())
            return None
        finally:
            if self._objectCacheLock.locked():
                self._objectCacheLock.release()
            
        
