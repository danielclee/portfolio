import logging
import json
from trigger import Trigger
from action import Action

class Sequence:
    ID = "id"
    CONTENT_ID = "content_id"
    DWELL_TIME = "dwell_time"
    DEFAULT_SEQUENCE = "default_sequence"
    NEXT_SEQUENCE = "next_sequence"
    ENTRANCE_ACTIONS = "entrance_actions"
    TRIGGERS = "triggers"
    UNDEFINED = "undefined"
    MOTION_SENSOR = "ms"
    NULL = 'null'
    
    def __init__(self, sequence):   # dict
        self._id = sequence.get(Sequence.ID)
        self._contentId = sequence.get(Sequence.CONTENT_ID)
        self._dwellTime = int(sequence.get(Sequence.DWELL_TIME, '0'))
        self._defaultSequence = bool(sequence.get(Sequence.DEFAULT_SEQUENCE, 'False'))
        self._nextSequence = sequence.get(Sequence.NEXT_SEQUENCE)
        self._entranceActions = []
        self._triggers = []
        self._soundLevel = 5
        self._hasMotionSensor = False

        # Parse entrance actione
        entrance_actions = sequence[Sequence.ENTRANCE_ACTIONS]
        if entrance_actions is not None:
            self.AddEntranceActions(entrance_actions)

        # Parse triggers
        triggers = sequence[Sequence.TRIGGERS]
        if triggers is not None:
            self.AddTriggers(triggers);


    def AddEntranceActions(self, entranceActionsList):    # JSON list
        for ea in entranceActionsList:
            action = Action(ea)
            if action.GetAction() == Action.SET_VOLUME:
                self._soundLevel = int(action.GetTarget())
            self._entranceActions.append(action)


    def AddTriggers(self, triggers):  # dict
        for key, value in triggers.items():
            self._triggers.append(Trigger(key, value[0]))
            if key == Sequence.MOTION_SENSOR:
                self._hasMotionSensor = True


    def SetAsDefaultSequence(self):
        self._defaultSequence = True


    def GetId(self):
        return self._id


    def GetContentId(self):
        return self._contentId


    def GetActualDwellTime(self):
        return self.GetDwellTime() * 1000


    def GetDwellTime(self):
        return self._dwellTime


    def IsDefaultSequence(self):
        return self._defaultSequence


    def GetNextSequence(self):
        return self._nextSequence


    def GetEntranceActions(self):
        return self._entranceActions


    def GetTriggers(self):
        return self._triggers


    def GetTriggerAction(self, trigger):
        for trigger in self._triggers:
            if trigger.GetTrigger().tolower() == trigger:
                return trigger.GetActions()
        return None


    def GetSoundLevel(self):
        return self._soundLevel


    def HasMotionSensor(self):
        return self._hasMotionSensor


    def ToJSONObj(self):
        jo = {}
        jo[Sequence.ID] = self._id
        jo[Sequence.CONTENT_ID] = self._contentId
        jo[Sequence.DWELL_TIME] = self._dwellTime
        jo[Sequence.DEFAULT_SEQUENCE] = self._defaultSequence
        jo[Sequence.ENTRANCE_ACTIONS] = json_dumps(self._entranceActions)
        jo[Sequence.TRIGGERS] =  json_dumps(self._triggers)
        return json.loads(jo)


    def ToString(self):
        return json.dumps(self.ToJSONObj())
