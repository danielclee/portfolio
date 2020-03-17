import math
import time

class SandTimer:
    def __init__(self, tout, label=None):  # float
        self.timeout = tout
        self.active = False
        self.start = 0
        self.stopwatch = 0
        if label != None:
            self.label = label


    def GetTimeout(self):
        return self.timeout


    def IsActive(self):
        return self.active


    def GetElapsed(self):
        if self.active:
            return time.monotonic() - self.start
        return 0


    def ResetStopwatch(self):
        self.stopwatch = time.monotonic()


    def GetStopwatchElapsed(self):
        return time.monotonic() - self.stopwatch


    def CheckExpired(self):
        if not self.active:
            return False
        if self.GetElapsed() >= self.timeout:
            return True
        return False
        

    def Start(self, tout=0):  # float
        if tout > 0:
            self.Set(tout)
        if self.timeout <= 0:
            return False
        self.active = True
        self.start = time.monotonic()
        self.ResetStopwatch()


    def Stop(self):
        self.active = False


    def Set(self, tout):  # float
        self.timeout = tout


    def Reset(self, tout=0):
        self.Start(tout)


    def Expire(self):
        self.active = True
        self.start = 0


    def SetLabel(self, label):
        self.label = label


    def GetLabel(self):
        return self.label
