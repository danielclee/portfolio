import logging
import json
import collections
import copy
import pickle
from settings import Settings


print("")
print("---------------------------------------------------------------")
print("")

settings = Settings("piebox_settings.p")
if settings.Load() == True:
    settings.ToScreen()
else:
    print("No settings file")

print("")
print("---------------------------------------------------------------")
print("")
