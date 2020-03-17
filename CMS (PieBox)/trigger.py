import logging
import json
from action import Action

class Trigger:
    def __init__(self, actuator, actions):  # string, dict
        self._actions = []
        self._input = actuator;
        self.AddActions(actions);


    def AddActions(self, actions):  # dict
        self._actions.append(Action(actions))


    def GetInput(self):
        return self._input 


    def GetTrigger(self):
        return self.GetInput()


    def GetActions(self):
        return self._actions


    def ActionArrayJSON(self):
        array = []
        for action in self._actions:
            array.append(Action(action))
        return array


    def ToString(self):
        return json.dumps(self.ActionArrayJSON())
