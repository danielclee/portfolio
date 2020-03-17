import logging
import json
import collections
import copy
import pickle
import os

class Settings:
    def __init__(self, savefilepath=None):
        self._SETTINGS_VERSION = 1
        self._savedFile = "./piebox_settings.p"
        if savefilepath != None:
            self._savedFile = savefilepath
        self._loaded = False
        logging.info("Pickle jar set to : " + self._savedFile)
        
        # Device setup
        self._deviceID = ""
        self._deviceResourceURL = ""
        self._token = ""

        # IO stuff
        self._ioDebounce = 3
        self._ioThrottle = 0.45

        # Check-in stuff
        self._checkinTimerValue = 600.0  # default 1 day  86400
        self._analyticsTimerValue = 600.0  # default 1 day   86400
        
        # Playlist info
        self._topPlaylist = ""
        self._topPlaylistSignature = ""
        self._playlistLut = {}

        # Content info
        self._contentLut = {}


    def SetDeviceID(self, uuid, save=True):
        self._deviceID = str(uuid)
        if (save):
            self.Save()


    def GetDeviceID(self):
        return self._deviceID


    def SetDeviceResourceURL(self, url, save=True):
        self._deviceResourceURL = str(url)
        if (save):
            self.Save()


    def GetDeviceResourceURL(self):
        return self._deviceResourceURL


    def SetToken(self, token, save=True):
        self._token = str(token)
        if (save):
            self.Save()


    def GetToken(self):
        return self._token


    def SetIODebounce(self, debounce, save=True):
        self._ioDebounce = int(debounce)
        if (save):
            self.Save()


    def GetIODebounce(self):
        return self._ioDebounce


    def SetIOThrottle(self, throttle, save=True):
        self._ioThrottle = float(throttle)
        if (save):
            self.Save()


    def GetIOThrottle(self):
        return self._ioThrottle


    def SetCheckinTimerValue(self, val, save=True):
        self._checkinTimerValue = float(val)
        if (save):
            self.Save()


    def GetCheckinTimerValue(self):
        return float(self._checkinTimerValue)


    def SetAnalyticsTimerValue(self, val, save=True):
        self._analyticsTimerValue = float(val)
        if (save):
            self.Save()


    def GetAnalyticsTimerValue(self):
        return float(self._analyticsTimerValue)


    def SetTopPlaylist(self, topplaylist, save=True):
        self._topPlaylist = topplaylist
        if (save):
            self.Save()


    def GetTopPlaylist(self):
        return(self._topPlaylist)


    def SetTopPlaylistSignature(self, signature, save=True):
        self._topPlaylistSignature = signature
        if (save):
            self.Save()


    def GetTopPlaylistSignature(self):
        return(self._topPlaylistSignature)


    def AddPlaylist(self, url, playlist, save=True):   # string, string
        self._playlistLut[url] = playlist
        if (save):
            self.Save()


    def SetPlaylist(self, playlistlist, save=True):   # list<Playlist>
        self._playlistLut.clear()
        for p in playlistlist:
            self._playlistList[p.GetUrl()] = p.ToString()
        if (save):
            self.Save()


    def GetPlaylistLut(self):
        return self._playlistLut


    def ClearPlaylistLut(self):
        self._playlistLut.clear()


    def SetFile(self, savefilepath=None):
        if savefilepath != None:
            self._savedFile = savefilepath


    def Load(self, savefilepath=None):
        try:
            if savefilepath != None:
                self._savedFile = savefilepath
            if os.path.isfile(self._savedFile):
                # Open and load settings file
                logging.info("Opening pickle jar : " + self._savedFile)
                settings = pickle.load(open(self._savedFile, "rb"))

                # Copy all settings over
                self._deviceID = settings['_deviceID']
                self._deviceResourceURL = settings['_deviceResourceURL']
                self._token = settings['_token']
                self._ioDebounce = settings['_ioDebounce']
                self._ioThrottle = settings['_ioThrottle']
                self._checkinTimerValue = settings['_checkinTimerValue']
                self._analyticsTimerValue = settings['_analyticsTimerValue']
                self._topPlaylistSignature = settings['_topPlaylistSignature']
                self._playlistLut.clear()
                playlists = settings['_playlistLut']
                if len(playlists) > 0:
                    for key, value in playlists.items():
                       self._playlistLut[key] = value
                self._loaded = True
                return True
            else:
                logging.info("No pickle jar : " + self._savedFile)
        except Exception as e:
            logging.exception("Error getting pickles")
            logging.error(e)
        return False


    def Save(self, savefilepath=None):
        try:
            if savefilepath != None:
                self._savedFile = savefilepath
            logging.info("Saving to pickle jar : " + self._savedFile)
            pickle.dump(self.__dict__, open(self._savedFile, "wb"))
            self._loaded = True
        except Exception as e:
            logging.error("Settings file not saved")
            logging.error(e)


    def ToString(self):
        logging.info("Settings for " + self._savedFile)
        logging.info("  Version : " + str(self._SETTINGS_VERSION))
        logging.info("  Device ID : " + self.GetDeviceID())
        logging.info("  Device resource URL : " + str(self.GetDeviceResourceURL()))
        logging.info("  Token : " + self.GetToken())
        logging.info("  IO Debounce : " + str(self.GetIODebounce()))
        logging.info("  Throttle : " + str(self.GetIOThrottle()))
        logging.info("  Check-in : " + str(self.GetCheckinTimerValue()))
        logging.info("  Analytics : " + str(self.GetAnalyticsTimerValue()))
        logging.info("  Top playlist signature : " + str(self._topPlaylistSignature))
        logging.info("  Playlists : ")
        for key, value in self.GetPlaylistLut().items():
            logging.info("      " + str(key) + " - " + str(value))


    def ToScreen(self):
        print("Settings for " + self._savedFile)
        print("  Version : " + str(self._SETTINGS_VERSION))
        print("  Device ID : " + self.GetDeviceID())
        print("  Device resource URL : " + str(self.GetDeviceResourceURL()))
        print("  Token : " + self.GetToken())
        print("  IO Debounce : " + str(self.GetIODebounce()))
        print("  Throttle : " + str(self.GetIOThrottle()))
        print("  Check-in : " + str(self.GetCheckinTimerValue()))
        print("  Analytics : " + str(self.GetAnalyticsTimerValue()))
        print("  Top playlist signature : " + str(self._topPlaylistSignature))
        print("  Playlists : ")
        for key, value in self.GetPlaylistLut().items():
            print("      " + str(key) + " - " + str(value))
