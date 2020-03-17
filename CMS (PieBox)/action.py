import logging
import json

class Action:
    UNDEFINED = "undefined"
    EMPTY = ""
    NULL = "null"
    ACTION = "action"
    PARAMETER = "parameters"
    # actions
    NEXT_SEQUENCE = "next_sequence"
    TARGET = "target"
    PAUSE_PLAY = "pause_play"
    LED_ON = "led_on"
    LED_OFF = "led_off"
    LED_FLASH = "led_flash"
    LED_CYCLE = "led_cycle"
    SOUND_ON = "sound_on"
    SOUND_OFF = "sound_off"
    VOLUME_UP = "volume_up"
    VOLUME_DOWN = "volume_down"
    SET_VOLUME = "set_volume"
    SCREEN_BRIGHTNESS_UP = "screen_brightness_up"
    SCREEN_BRIGHTNESS_DOWN = "screen_brightness_down"
    SET_SCREEN_BRIGHTNESS = "set_screen_brightness"

    def __init__(self, actionObj):
        self._action = ""
        self._target = ""
        self._parameter = ""
        self._parameters = {}
        self.SetAction(actionObj.get(Action.ACTION, Action.UNDEFINED))
        self.SetTarget(actionObj.get(Action.TARGET, Action.UNDEFINED))
        self.SetParameter(actionObj.get(Action.PARAMETER, Action.UNDEFINED))
        ##3434## self.SetParameters(actionObj.get(Action.PARAMETER, Action.UNDEFINED))


    def SetAction(self, action):
        self._action = action


    def GetAction(self):
        return self._action


    def SetTarget(self, target):
        self._target = target


    def GetTarget(self):
        return self._target


    def SetParameter(self, parameter):
        self._parameter = parameter
        # 3434 Need to parse in future


    def GetParameter(self):
        return self._parameter


    ##3434## def SetParameters(self, parameter):
    ##3434##     if parameter.tolower() != Action.UNDEFINED and \
    ##3434##        parameter.tolower() != Action.EMPTY and \
    ##3434##        parameter.tolower() != Action.NULL:
    ##3434##         paramL = parameter.split("&")
    ##3434##         for param in paramL:
    ##3434##             pl = param.split("=")
    ##3434##             self._parameters[p1[0]] = p1[1]


    def GetParameters(self, key):
        retVal = Action.UNDEFINED
        value = self._parameters.get(key)
        if value != None:
            retVal = value
        return retVal


    def ToJSONObj(self):
        jo = {}
        jo[Action.ACTION] = self.GetAction()
        jo[Action.TARGET] = self.GetTarget()
        param = self.GetParameter()
        if param.tolower() != Action.UNDEFINED:
            jo[Action.PARAMETER] = self.GetParameter()
        return json.loads(jo)


    def ToString(self):
        return json.dumps(self.ToJSONObj())
