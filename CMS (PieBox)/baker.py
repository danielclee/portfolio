import logging
import hashlib
import requests
import json
import _thread
import threading
import traceback
import collections
import copy
import datetime
import time
import os
import glob
from time import sleep
from queue import Queue
from threading import Timer
from enum import Enum
from action import Action
from sequence import Sequence
from content import Content
from trigger import Trigger
from playlist import Playlist
from link import Link
from sandtimer import SandTimer
from videoplayer import VideoPlayer
from gpiocontroller import GPIOController
from datastore import DataStore
from delivery import Delivery
from analytics import Analytics
from office import Office
from settings import Settings
from order import Order 
##from threadmonitor import ThreadMonitor 

class Baker:
    class SequenceType(Enum):
        DEFAULT = 1
        NEXT = 2

    class SequenceState(Enum):
        IDLE = 1
        PLAYING = 2


    def __init__(self):
        # Threads
        self._gpiothread = None
        self._deliverythread = None
        self._videothread = None
        self._officeThread = None
        self._analyticsThread = None
        self._orderThread = None

        # Settings
        self._settings = Settings()

        # Setup Qs
        self._videoLink = Link()
        self._gpioLink = Link()
        self._guiLink = Link()
        self._deliveryLink = Link()
        self._officeLink = Link()
        self._analyticsLink = Link()
        self._orderLink = Link()

        # Setup timers
        self._checkInTimer = SandTimer(600.0)
        self._analyticsTimer = SandTimer(600.0)
        self._startPlaylistTimer = SandTimer(1)

        # Playlist and content stuff
        self._currentPlaylist = None
        self._playlists = []
        self._pendingTopPlaylistSignature = ""
        self._downloadingPlaylist = False
        
        # Sequence stuff
        self._currentSequence = None

        # Checkin stuff
        self._checkinProcessing = False

        # Device setup
        self._tokenUrl = 'https://fulgent.sandd.studio/api/v1.0/device/'

        # Office stuff
        self._officeActive = False

        # Misc
        self._LOCAL_SERVER_MODE_ = True
        self._TEST_MODE = True
        self._screenWidth = 0
        self._screenHeight = 0
        self._idle = True
        self._contentDirectory = "./"
        self._totalContentSize = 0

        # Analytics stuff
        self._epoch = datetime.datetime.utcfromtimestamp(0)
        self._timeZoneOffset = time.timezone * 1000
        self._currentMediaStartTimestamp = None
        self._cachedMSAnalyticEvent = None
        self._msActiveTimestamp = None

        # Order (kbd) stuff
        self._quitPattern = "3434"
        self._settingsPattern = "4545"
        self._checkKbdTimer = SandTimer(10.0)

        # Get hardware info
        self._serial = "Unknown"
        self._model = "Unknown"
        self._hardware = "Unknown"
        self._product = "PieBox"
        self._version = "0.5"
        self.GetHdwInfo()
        logging.info("Serial : " + self._serial)
        logging.info("Model : " + self._model)
        logging.info("Hardware : " + self._hardware)
        logging.info("Product : " + self._product)
        logging.info("Version : " + self._version)


    #
    # Start helper threads
    # These run in different threads
    #


    def StartVideoPlayerThread(self):
        logging.info("Starting video player thread")
        player = VideoPlayer(self._videoLink)
        player.Run()


    def StartGPIOThread(self):
        logging.info("Starting GPIO thread")
        gpio = GPIOController(self._gpioLink)
        gpio.Run()


    def StartDeliveryThread(self):
        logging.info("Starting delivery thread")
        delivery = Delivery(self._deliveryLink, self._contentDirectory)
        delivery.Run()


    def StartOfficeThread(self):
        logging.info("Starting office thread")
        office = Office(self._officeLink)
        office.Run()


    def StartAnalyticsThread(self, interval, url):
        logging.info("Starting analytics thread")
        analytics = Analytics(self._analyticsLink, interval, url)
        analytics.Run()


    def StartOrderThread(self, watchlist=None):
        logging.info("Starting order thread")
        order = Order(self._orderLink, watchlist)
        order.Run()


    #
    # Send msgs to threads
    #


    def SendVideoCmd(self, cmd):
        logging.debug(cmd)
        self._videoLink.SendCmd(cmd)


    def SendGPIOCmd(self, cmd):
        logging.debug(cmd)
        self._gpioLink.SendCmd(cmd)


    def SendDeliveryCmd(self, cmd):
        logging.debug(cmd)
        self._deliveryLink.SendCmd(cmd)


    def SendDeliveryBatchCmd(self, cmdlist):
        logging.debug(cmd)
        self._deliveryLink.SendBatchCmd(cmdlist)


    def SendOfficeCmd(self, cmd):
        logging.debug(cmd)
        self._officeLink.SendCmd(cmd)


    def SendAnalyticsCmd(self, cmd):
        logging.debug(cmd)
        self._analyticsLink.SendCmd(cmd)


    def SendOrderCmd(self, cmd):
        self._orderLink.SendCmd(cmd)


    def Quit(self):
        logging.info("Quiting")
        self.running = False
        if self._gpiothread != None:
            self.SendGPIOCmd('{"action":"exit"}')
            self._gpiothread.join()
            self._gpiothread = None
        logging.info("GPIO thread closed")
        if self._deliverythread != None:
            self.SendDeliveryCmd('{"action":"exit"}')
            self._deliverythread.join()
            self._deliverythread = None
        logging.info("Delivery thread closed")
        if self._videothread != None:
            self.SendVideoCmd('{"action":"exit"}')
            self._videothread.join()
            self._videothread = None
        logging.info("Video thread closed")
        if self._officeThread != None:
            self.SendOfficeCmd('{"action":"exit"}')
            self._officeThread.join()
            self._officeThread = None
        logging.info("Office thread closed")
        if self._analyticsThread != None:
            self.SendAnalyticsCmd('{"action":"exit"}')
            self._analyticsThread.join()
            self._analyticsThread = None
        logging.info("Analytics thread closed")
        if self._orderThread != None:
            self.SendOrderCmd('{"action":"exit"}')
            self._orderThread.join()
            self._orderThread = None
        logging.info("Order thread closed")


    #
    # GUI helpers
    #


    def OpenOffice(self):
        if self._officeThread == None:
            logging.debug("Opening office")
            self._officeThread = threading.Thread(name='officethread',
                                                  target=self.StartOfficeThread)
            self._officeThread.start()
            self._officeActive = True

        # Minimize video player
        self.SendVideoCmd(json.dumps({VideoPlayer.ACTION : VideoPlayer.HIDE}))


    def CloseOffice(self):
        if self._officeThread != None:
            self.SendOfficeCmd(json.dumps({Office.ACTION : Office.EXIT}))
            self._officeThread.join()
            self._officeThread = None
            logging.debug("Office closed")
        self._officeActive = False
        self._officeLink.Clear()


    def ShowDeviceInfo(self, uuid):
        self.OpenOffice()
        self.SendOfficeCmd(json.dumps({Office.ACTION : Office.INFO,
                                       Office.SERIAL : self._serial,
                                       Office.HARDWARE : self._model,
                                       Office.MODEL : self._hardware,
                                       Office.PRODUCT : self._product,
                                       Office.VERSION : self._version,
                                       Office.UUID : uuid}))


    def GetUserOption1(self):
        # Stop video
        self.SendVideoCmd(json.dumps({VideoPlayer.ACTION : VideoPlayer.STOP}))
        self._idle = True

        # Show option 1 dialog
        self.OpenOffice()
        self.SendOfficeCmd(json.dumps({Office.ACTION : Office.USEROPTION1}))
        msg = self._officeLink.CheckEventQ(blocking=True, wait=None)  # blocking
        logging.debug(msg)
        event_json = json.loads(msg)
        event = str(event_json[Office.EVENT])
        if event == Office.BTN_SELECTED:
            choice = event_json[Office.BTN_SELECTED]
            if choice == Office.BTN_EXIT:
                return True
            elif choice == Office.BTN_CHANGE_SETTINGS:
                return self.ShowDeviceSettings(str(self._checkInTimer.GetTimeout()),
                                               str(self._analyticsTimer.GetTimeout()),
                                               self._settings.GetIODebounce(),
                                               self._settings.GetIOThrottle())
            elif choice == Office.BTN_CHANGE_DEVICEID:
                return self.ChangeDeviceID(self._settings.GetDeviceID())
        # End if
        self.CloseOffice()
        return False


    def ShowProgress(self, title, progress, max):
        self.OpenOffice()
        self.SendOfficeCmd(json.dumps({Office.ACTION : Office.PROGRESS,
                                       Office.TITLE : title,
                                       Office.PROGRESS : progress,
                                       Office.TOTAL : max}))


    #
    # Check for events
    #


    def CheckVideoEvents(self):
        msg = self._videoLink.CheckEventQ(blocking=False, wait=None)
        if msg == None:
            return
        logging.debug(msg)
        event_json = json.loads(msg)
        event = event_json[VideoPlayer.EVENT]
        if event == VideoPlayer.DONE:
            logging.debug("Video playing is done")
            logging.debug("Clearing media start timestamp")
            logging.debug("Preparing to play next sequence")
            self._idle = True
            self._currentMediaStartTimestamp = None
            self.PlayNextSequence()
        elif event == VideoPlayer.ERROR:
            self._idle = True
            errmsg = str(event_json[VideoPlayer.ERROR])
            raise Exception("Unrecoverable video error!! " + errmsg)


    def CheckOfficeEvents(self):
        if self._officeActive:
            msg = self._officeLink.CheckEventQ(blocking=False, wait=None)
            if msg == None:
                return
            logging.debug(msg)
            event_json = json.loads(msg)
            event = str(event_json[OFFICE.EVENT])
            if event == Office.DONE:
                self.CloseOffice()


    def CheckOrderEvents(self):
        msg = self._orderLink.CheckEventQ(blocking=False, wait=None)
        if msg == None:
            return
        logging.debug(msg)
        event_json = json.loads(msg)
        event = str(event_json[Order.EVENT])
        if event == Order.MATCH:
            ordermatch = event_json[Order.MATCH]
            if ordermatch == self._quitPattern:
                logging.info("Received order to quit, stopping pie bake")
                self.running = False
            elif ordermatch == self._settingsPattern:
                logging.info("Received order to change settings")
        # End if

    # This always needs to be the last check
    def CheckGPIOEvents(self):
        msg = self._gpioLink.CheckEventQ(blocking=True, wait=0.1)
        if msg != None:
            logging.debug(msg)
            event_json = json.loads(msg)
            inputevent = str(event_json[GPIOController.INPUT_EVENT])
            inputtype = str(event_json[GPIOController.TYPE])
            status = str(event_json[GPIOController.STATUS])

            # Process analytics
            self.ProcessAnalytics(inputevent, inputtype, status)

            # Check triggers
            if self._currentSequence != None:
                # See if io tied to action
                triggerslist = self._currentSequence.GetTriggers()
                for trigger in triggerslist:
                    if inputevent == trigger.GetInput():
                        actions = trigger.GetActions()
                        for action in actions:
                            self.ExecuteAction(action)
                        break
                # End for
            # End nested-if
        # End if


    def ProcessAnalytics(self, input, type, status):
        # Cache analytics
            
        now = datetime.datetime.utcnow()
        timestamp = int((now - self._epoch).total_seconds() * 1000)
        played = 0
        if self._currentMediaStartTimestamp != None:
            played = (datetime.datetime.utcnow() - self._currentMediaStartTimestamp).total_seconds() * 1000
        logging.debug("Video played for " + str(played) + "ms")
        duration = 0
        if self._currentSequence != None:
            logging.debug("Current sequence content id : " + self._currentSequence.GetContentId())
            content =  self._currentPlaylist.GetContentObj(self._currentSequence.GetContentId())
            duration = content.GetDuration()
            logging.debug("Content duration is " + str(duration))
        else:
            logging.debug("No current sequence exists")
        self._cachedMSAnalyticEvent = {Analytics.ACTION : Analytics.INPUT,
                                       Analytics.INPUT : input,
                                       Analytics.TYPE : type,
                                       Analytics.PLAYLIST : self._currentPlaylist.GetUUID(),
                                       Analytics.SEQUENCE : self._currentSequence.GetId(),
                                       Analytics.TIMESTAMP : timestamp, 
                                       Analytics.TIMEZONE : self._timeZoneOffset,
                                       Analytics.DWELL : 0,
                                       Analytics.CONTENTURL : self._currentSequence.GetContentId(),
                                       Analytics.PLAYED : played,
                                       Analytics.DURATION : duration,
                                       Analytics.DATETIME : now.isoformat()}
        if type == GPIOController.PUSH_BUTTON:
            logging.debug("Sending pb analytics event")
            self.SendAnalyticsCmd(json.dumps(self._cachedMSAnalyticEvent))
            self._cachedMSAnalyticEvent = None
        elif type == GPIOController.MOTION_SENSOR:
            logging.debug("Processing ms analytics event")
            if status == GPIOController.ACTIVE:  # ms active
                self._msActiveTimestamp = datetime.datetime.utcnow()
                logging.debug("Motion sensor ACTIVE")
            else:  # ms inactive
                if self._msActiveTimestamp != None:
                    logging.debug("Motion sensor DE-ACTIVE")
                    if self._cachedMSAnalyticEvent != None:
                        self._cachedMSAnalyticEvent[Analytics.DWELL] = (datetime.datetime.utcnow() - self._msActiveTimestamp).total_seconds() * 1000
                        self.SendAnalyticsCmd(json.dumps(self._cachedMSAnalyticEvent))
                        logging.debug("Storing analytics data")
                    else:
                        logging.debug("No cached MS analytic event")
                else:
                    logging.debug("No active motion sensor timestamp")
                self._msActiveTimestamp = None
                self._cachedMSAnalyticEvent = None


    #
    # Playlists
    #


    def CheckDeliveryEvents(self):
        try:
            msg = self._deliveryLink.CheckEventQ(blocking=False, wait=None)
            if msg == None:
                return
            logging.debug(msg)
            event_json = json.loads(msg)
            event = str(event_json[Delivery.EVENT])
    
            # Handle json result delivery event

            if event == Delivery.RESULT_TOP_PLAYLIST:
                result = str(event_json[Delivery.RESULT])
                self.ProcessCheckinResponse(result)
    
            # Handle content download progress event

            elif event == Delivery.PROGRESS:
                uuid = str(event_json[Delivery.TITLE])
                progress = str(event_json[Delivery.PROGRESS])
                if progress == Delivery.COMPLETE:  # content downloaded complete
                    logging.debug("Content delivery complete : " + uuid)
                    self.CloseOffice()
                else:
                    downloaded_bytes = event_json[Delivery.INCREMENT]
                    total_bytes = event_json[Delivery.TOTAL]
                    logging.debug(("Content delivery in progress : " + uuid +
                                   "   " + str(downloaded_bytes) +
                                   " / " + str(total_bytes)))
                    if self._currentPlaylist == None:  # only show progress on first activation
                        self.ShowProgress(uuid, downloaded_bytes, total_bytes)

            # All playlists are processed

            elif event == Delivery.PLAYLIST_PROCESS_COMPLETE:
                # Get list of pending playlists and finalize processing
                playlistobjlist = self._deliveryLink.GetObjectCache()
                if playlistobjlist != None:
                    self.PlaylistProcessingComplete(playlistobjlist)
                    logging.info("All playlists processed")
                else:
                    logging.error("Error completing playlist processing")
                self._checkinProcessing = False
                self._startPlaylistTimer.Start(0.1)

            # If error then reset states

            elif event == Delivery.ERROR:
                err = ""
                if event_json.get(Delivery.EXCEPTION):
                    err = event_json[Delivery.EXCEPTION]
                logging.error("Error delivering, exception : " + err)
                self.ErrorRecovery(60.0)
        except Exception as e:
            logging.error("Exception checking delivery events")
            logging.error(e)
            logging.exception(traceback.format_exc())
            self.ErrorRecovery(60.0)


    def Checkin(self, url):
        if self._checkinProcessing == True:
            logging.debug("Still processing last checkin, delay new checkin")
            return
        logging.debug("Checking in")
        self._pendingTopPlaylistSignature = ""
        self.SendDeliveryCmd(json.dumps({Delivery.ACTION : Delivery.GET_TOP_PLAYLIST,
                                         Delivery.URL : url}))


    def ProcessCheckinResponse(self, msg):
        logging.debug("Processing checkin : " + msg)

        # Generate signature for top playlist
        sha1 = hashlib.sha1()
        sha1.update(msg.encode('utf-8'))
        sha1str = str(sha1.hexdigest())
        
        # If signature hasn't changed, then no playlist changes
        if sha1str == self._settings.GetTopPlaylistSignature():
            logging.debug("Top playlist unchanged, aborting checkin")
            self._checkinProcessing = False
            self._pendingTopPlaylistSignature = ""
            return

        # Set processing flag and cache signature
        self._checkinProcessing = True
        self._pendingTopPlaylistSignature = sha1str

        # If top playlist is not active then not licensed
        playlist_json = json.loads(msg)
        if playlist_json[Playlist.ACTIVE] != True:
            logging.debug("Top playlist not active, aborting checkin")
            self._checkinProcessing = False
            self._pendingTopPlaylistSignature = ""
            logging.info("Showing licensing options")  #3434
            return

        # Send to delivery module to handle
        self.SendDeliveryCmd(json.dumps({Delivery.ACTION : Delivery.PROCESS_TOP_PLAYLIST,
                                         Delivery.TOP_PLAYLIST : msg}))


    def PlaylistProcessingComplete(self, pendplaylists):
        logging.debug("Finalizing playlist processing")

        # Stop any playing video
        self.SendVideoCmd('{"action":"stop"}')
        self._idle = True
        self._currentPlaylist = None

        # Cleanup video buffers
        self.SendVideoCmd(json.dumps({VideoPlayer.ACTION : VideoPlayer.CLEAN}))

        # Get content filepaths from all playlists new and old
        oldcontentlist = []
        newcontentlist = []
        for cplaylist in self._playlists:
            for cfilepath in cplaylist.GetContentPathList():
                oldcontentlist.append(cfilepath)
        for pplaylist in pendplaylists:
            for cfilepath in pplaylist.GetContentPathList():
                newcontentlist.append(cfilepath)

        # Clean up any content not in new list
        logging.debug("Cleaning up old content list")
        for c in oldcontentlist:
            if not c in newcontentlist:
                logging.debug("Removing content : " + c)
                os.remove(c)

        # Set new playlist list
        self._playlists.clear()
        self._playlists = pendplaylists
        if len(self._playlists) > 0:
            self._currentPlaylist = self._playlists[0]

        # Save data
        logging.debug("Saving playlists in settings")
        self._settings.ClearPlaylistLut()
        for playlist in self._playlists:
            self._settings.AddPlaylist(playlist.GetUrl(), playlist.GetSource(), False)
        if self._pendingTopPlaylistSignature != "":
            self._settings.SetTopPlaylistSignature(self._pendingTopPlaylistSignature)  # save signature
        self._settings.Save()
        
        # Other cleanup
        logging.debug("Cleaning up")
        self.CloseOffice()
        logging.debug("Playlist processing completed")


    def BlockingGetMediaContent(self, path, playlistobj):
        logging.debug("Blocking getting media content")
        contentobjlist = playlistobj.GetContentList()
        for contentobj in contentobjlist:
            self.SendDeliveryCmd(json.dumps({Delivery.ACTION : Delivery.GET_FILES,
                                             Delivery.PATH : path,
                                             Delivery.UUID : contentobj.GetId(),
                                             Delivery.URL : contentobj.GetResource(),
                                             Delivery.FILE : contentobj.GetFileName()}))
            while True:
                msg = self._deliveryLink.CheckEventQ(blocking=True, wait=None)
                if msg != None:
                    event_json = json.loads(msg)
                    event = str(event_json[Delivery.EVENT])

                    # Show progress
                    if event == Delivery.PROGRESS:
                        progress = str(event_json[Delivery.PROGRESS])
                        uuid = str(event_json[Delivery.TITLE])
                        if progress == Delivery.COMPLETE:  # content downloaded complete
                            duration = int(event_json[Delivery.DURATION])
                            logging.debug("Setting content " + contentobj.GetId() + " duration " + str(duration))
                            playlistobj.SetContentDuration(contentobj.GetId(), duration)
                            logging.debug("Setting content " + contentobj.GetId() + " ready")
                            playlistobj.SetContentReady(contentobj.GetId(), True)
                            self.CloseOffice()
                            logging.debug("Content delivery complete : " + uuid)
                            break
                        else:                              # content download in progress
                            downloaded_bytes = event_json[Delivery.INCREMENT]
                            total_bytes = event_json[Delivery.TOTAL]
                            logging.debug(("Content delivery in progress : " + uuid +
                                           "   " + str(downloaded_bytes) +
                                           " / " + str(total_bytes)))
                            if self._currentPlaylist == None:  # only show progress on first activation
                                self.ShowProgress(uuid, downloaded_bytes, total_bytes)

                    # Delivery error
                    elif event == Delivery.ERROR:
                        err = ""
                        if event_json.get(Delivery.EXCEPTION):
                            err = event_json[Delivery.EXCEPTION]
                        logging.error("Error downloading content, exception : " + err)
                        self.ErrorRecovery(60.0)
                        break
                    # End if-elif
                # End nested if
            # End if
        self.CloseOffice()


    #
    # Sequences
    #


    def PlayDefaultSequence(self):
        if self._currentPlaylist != None:
            self._currentPlaylist.ResetCurrentSequence()
            sequence = self._currentPlaylist.GetDefaultSequence()
            self.PlaySequence(sequence)
        else:
            logging.debug("PlayDefaultSequence : No current playlist")
            self._startPlaylistTimer.Start(1.0)


    def PlayNextSequence(self):
        if self._currentPlaylist != None:
            sequence = self._currentPlaylist.GetNextSequence()
            self.PlaySequence(sequence)
        else:
            logging.debug("PlayNextSequence : No current playlist")
            self._startPlaylistTimer.Start(1.0)


    def PlaySequence(self, sequence):  # Sequence
        # Check playlist is valid
        if self._currentPlaylist == None:
            logging.error("Could not find current playlist!!")
            self.ErrorRecovery(1.0)

        # Check sequence is valid
        if sequence == None:
            logging.error("Could not find valid sequence in current playlist!!")
            self.ErrorRecovery(1.0)

        # Stop any playing video
        self.SendVideoCmd(json.dumps({VideoPlayer.ACTION : VideoPlayer.STOP}))
        self._idle = True

        # Check to make sure content is ready otherwise play default content
        content = self._currentPlaylist.GetContentObj(sequence.GetContentId())
        if not content.GetReady():
            logging.debug("Content not ready")
            self._startPlaylistTimer.Start(1.0)
            return
        
        # Set as current sequence
        self._currentSequence = sequence

        # Get trigger list to setup IO
        # This is needed to set inactive unused GPIO inputs
        # However if playlist contains sequence with motion sensor trigger,
        # always add motion sensor to triggerlist otherwise will never
        # get deactivate event
        triggerslist = []
        for trigger in self._currentSequence.GetTriggers():
            triggerslist.append(trigger.GetInput())
        if self._currentPlaylist.HasMotionSensor():
            if not self._currentSequence.HasMotionSensor():
                triggerslist.append(GPIOController.MOTION_SENSOR)
        # End if
        cmd = '{"action":"setup_io", "throttle":"0.45", "debounce":"3", '
        cmd += '"inputs":"' + ",".join(triggerslist) + '"}'
        self.SendGPIOCmd(cmd)
        
        # Do entrance actions
        entranceactions = self._currentSequence.GetEntranceActions()
        if len(entranceactions) > 0:
            for entranceaction in entranceactions:
                self.ExecuteAction(entranceaction)

        # Play sequence content
        content = self._currentPlaylist.GetContentObj(sequence.GetContentId())
        soundlevel = sequence.GetSoundLevel()
        if content.GetReady():
            fileloc = (self._contentDirectory + self._currentPlaylist.GetUUID() +
                       "/" + content.GetFileName())
            logging.debug("Preparing to play content " + fileloc)
            self._currentMediaStartTimestamp = datetime.datetime.utcnow()
            self.SendVideoCmd(json.dumps({VideoPlayer.ACTION : VideoPlayer.PLAY,
                                          VideoPlayer.FILE : fileloc,
                                          VideoPlayer.SOUND_LEVEL : soundlevel,
                                          VideoPlayer.DWELL : sequence.GetDwellTime()}))
            self._idle = False
        else:
            logging.debug("Content not ready")
            self._idle = True


    def ExecuteAction(self, action):  # Action
        ## pause_play
        ## led_on
        ## led_off
        ## led_flash
        ## led_cycle
        ## sound_on
        ## sound_off
        ## volume_up
        ## volume_down
        ## set_volume
        ## screen_brightness_up
        ## screen_brightness_down
        ## set_screen_brightness
        
        # Do action

        if action.GetAction() == Action.NEXT_SEQUENCE:
            sequence = self._currentPlaylist.GetSequence(action.GetTarget())
            self.PlaySequence(sequence)
        elif action.GetAction() == Action.LED_ON:
            leds = action.GetTarget()
            self.SendGPIOCmd(json.dumps({GPIOController.ACTION : GPIOController.LED_ON,
                                         GPIOController.OUTPUTS : leds}))
        elif action.GetAction() == Action.LED_OFF:
            leds = action.GetTarget()
            self.SendGPIOCmd(json.dumps({GPIOController.ACTION : GPIOController.LED_OFF,
                                         GPIOController.OUTPUTS : leds}))
        elif action.GetAction() == Action.LED_FLASH:
            leds = action.GetTarget()
            self.SendGPIOCmd(json.dumps({GPIOController.ACTION : GPIOController.LED_BLINK,
                                         GPIOController.OUTPUTS : leds,
                                         GPIOController.INTERVAL : 1.0}))
        elif action.GetAction() == Action.LED_CYCLE:
            gg = 0    # 3434 Need to do
        elif action.GetAction() == Action.VOLUME_UP:
            self.SendVideoCmd(json.dumps({VideoPlayer.ACTION : VideoPlayer.VOLUME_UP}))
        elif action.GetAction() == Action.VOLUME_DOWN:
            self.SendVideoCmd(json.dumps({VideoPlayer.ACTION : VideoPlayer.VOLUME_DN}))
        elif action.GetAction() == Action.PAUSE_PLAY:
            gg = 0    # 3434 Need to do


    #
    # New device setup
    #


    def GetNewDeviceToken(self):
        # Get token
        self.SendDeliveryCmd(json.dumps({Delivery.ACTION : Delivery.TOKEN,
                                         Delivery.URL : self._tokenUrl,
                                         Delivery.SERIAL : self._serial,
                                         Delivery.HARDWARE : self._model,
                                         Delivery.MODEL : self._hardware,
                                         Delivery.PRODUCT : self._product,
                                         Delivery.VERSION : self._version}))

        msg = self._deliveryLink.CheckEventQ(blocking=True, wait=None)
        if msg == None:
            logging.error("No token returned")
            return None
        else:
            logging.info("New token returned : " + msg)
            return msg


    def ShowDeviceToken(self, token):
        # Show token
        self.OpenOffice()
        self.SendOfficeCmd(json.dumps({Office.ACTION : Office.TOKEN,
                                       Office.TOKEN : token}))
        nomsg = self._officeLink.CheckEventQ(blocking=True, wait=None)
        self.CloseOffice()


    def ShowDeviceSettings(self, checkin, analytics, iodebounce, iothrottle):
        # Show settings
        self.OpenOffice()
        self.SendOfficeCmd(json.dumps({Office.ACTION : Office.SETTINGS,
                                       Office.CHECKIN : checkin,
                                       Office.ANALYTICS : analytics,
                                       Office.IODEBOUNCE : iodebounce,
                                       Office.IOTHROTTLE: iothrottle}))
        msg = self._officeLink.CheckEventQ(blocking=True, wait=None)
        settings_json = json.loads(msg)
        changed = False
        if (float(settings_json[Office.CHECKIN])) != self._checkInTimer.GetTimeout():
            self._settings.SetCheckinTimerValue(float(settings_json[Office.CHECKIN]), False)
            self._checkInTimer.Set(float(settings_json[Office.CHECKIN]))
            changed = True
        if (float(settings_json[Office.ANALYTICS])) != self._analyticsTimer.GetTimeout():
            self._settings.SetAnalyticsTimerValue(float(settings_json[Office.ANALYTICS]), False)
            self._analyticsTimer.Set(float(settings_json[Office.ANALYTICS]))
            changed = True
        if settings_json[Office.IODEBOUNCE] != self._settings.GetIODebounce():
            self._settings.SetIODebounce(settings_json[Office.IODEBOUNCE], False)
            changed = True
        if settings_json[Office.IOTHROTTLE] != self._settings.GetIOThrottle():
            self._settings.SetIOThrottle(settings_json[Office.IOTHROTTLE], False)
            changed = True
        if changed:
            self._settings.Save()
        self._settings.ToString()
        self.CloseOffice()
        return changed


    def ChangeDeviceID(self, deviceid):
        # Change device ID
        self.OpenOffice()
        self.SendOfficeCmd(json.dumps({Office.ACTION : Office.CHANGE_DEVICEID,
                                       Office.DEVICEID : deviceid}))
        msg = self._officeLink.CheckEventQ(blocking=True, wait=None)
        settings_json = json.loads(msg)
        newdeviceid = settings_json[Office.DEVICEID]
        newdeviceurl = ("https://fulgent.sandd.studio/devices/{d}/playlist".format(d=newdeviceid))
        if newdeviceid == self._settings.GetDeviceID():
            logging.debug("No change or invalid device ID, aborting change")
            return False

        # Make sure url exists
        response = requests.get(newdeviceurl, headers={'accept': 'application/json'})
        if response.status_code != Delivery.HttpResponseStatusCodes.HTTP_RESPONSE_OK.value:
            return False
        resource_json = json.loads(response.text)
        if (len(resource_json['playlists'])==0) or (resource_json[Playlist.ACTIVE]!=True):
            logging.debug("Check active playlist failed during device ID change")
            return False

        # Set new settings
        self._settings.SetDeviceID(newdeviceid, save=False)
        self._settings.SetDeviceResourceURL(newdeviceurl, save=False)
        self._settings.Save()
        self._settings.ToString()
        self.CloseOffice()
        return True


    def ShowMessage(self, msg):
        # Show message
        self.OpenOffice()
        self.SendOfficeCmd(json.dumps({Office.ACTION : Office.MESSAGE,
                                       Office.MESSAGE : msg}))
        nomsg = self._officeLink.CheckEventQ(blocking=True, wait=None)
        self.CloseOffice()


    #
    # Main event loop
    #


    def Bake(self):
        # Flow - https://drive.google.com/drive/folders/0ByG2LbZ_hYrCRlZkMGNabk5Sb2M
        logging.info("Preheating oven, starting modules")
        
        # Startup thread modules

        self._videothread = threading.Thread(name='videoplayerthread',
                                             target=self.StartVideoPlayerThread)
        self._videothread.start()
        self._gpiothread = threading.Thread(name='gpiothread',
                                            target=self.StartGPIOThread)
        self._gpiothread.start()
        self._deliverythread = threading.Thread(name='deliverythread',
                                                target=self.StartDeliveryThread)
        self._deliverythread.start()
        ##self._orderThread = threading.Thread(name='orderthread',
        ##                                     target=self.StartOrderThread,
        ##                                     args=([self._quitPattern, self._settingsPattern],),)
        ##self._orderThread.start()

        # Load settings file

        newdeviceactivation = False
        if self._settings.Load() == True:
            logging.info("Loading saved settings")
            self._settings.ToString()
        
            # Set timers from settings
            self._checkInTimer.Set(self._settings.GetCheckinTimerValue())
            self._analyticsTimer.Set(self._settings.GetAnalyticsTimerValue())

            # Process all saved playlists
            for key, value in self._settings.GetPlaylistLut().items():
                # Process and save playlist
                logging.info("Processing playlist : " + key)
                playlistobj = Playlist(key, value)
                self._playlists.append(playlistobj)

                # Get all content for playlist
                directory = self._contentDirectory + playlistobj.GetUUID()
                self.BlockingGetMediaContent(directory, playlistobj)

            # Set current playlist to 1st playlist in list
            if len(self._playlists) > 0:
                self._currentPlaylist = self._playlists[0]
            else:
                logging.error("No saved playlists found in settings!")
            logging.info("Finish Loading saved settings")
        else:
            logging.info("No settings to load")

        # If have current playlist, then start playlist

        tokenactivated = False
        if (len(self._playlists) > 0) and (self._currentPlaylist != None):
            logging.info("Found starting playlist, setting start playlist timer")
            tokenactivated = True
            self._startPlaylistTimer.Start(0.1)

        # If have token but no playlists then device not registered yet

        elif self._settings.GetToken() != "":
            logging.info("Found unactivated token : " + self._settings.GetToken())
            newdeviceactivation = True
            self.ShowDeviceToken(self._settings.GetToken())

        # If no token or playlist found, start new device setup

        else:
            logging.info("Unregistered device, getting new token")
            newdeviceactivation = True
            msgtoken = self.GetNewDeviceToken()  # Get token from fulgent
            if msgtoken == None:
                logging.error("No token returned")
                raise Exception("No token returned, exiting!")
            token_json = json.loads(msgtoken)
            token = str(token_json[Delivery.TOKEN])
            if token == Delivery.ERROR:
                logging.error("Error getting token")
                raise Exception("Error getting token, extting!")
            self._settings.SetToken(token, False)
            self._settings.SetDeviceResourceURL(str(token_json['resource']), False)
            self._settings.SetDeviceID(str(token_json['id']), False)
            self._settings.Save()
            logging.info("Got new token : " + self._settings.GetToken())
            self.ShowDeviceToken(self._settings.GetToken())
        
        # Check if token has been activated, if not loop until true

        while tokenactivated == False:
            # Check to make sure a playlist is available
            response = requests.get(self._settings.GetDeviceResourceURL(),
                                    headers={'accept': 'application/json'})

            # If no playlist returned, show wait message
            if response.status_code != Delivery.HttpResponseStatusCodes.HTTP_RESPONSE_OK.value:
                logging.error("Check playlist bad response, showing wait message")
                self.ShowMessage("Playlists check failed, press OK when playlists are setup and internet is connected.")
                continue

            # If no active playlist, show wait message
            resource_json = json.loads(response.text)
            if (len(resource_json['playlists']) == 0) or \
               (resource_json[Playlist.ACTIVE] != True):
                logging.error("No active playlists found, showing wait message")
                self.ShowMessage("No active playlists found, press OK when playlists are setup.")
                continue

            # Continue onward
            tokenactivated = True

        # Show settings if first time device activation
        if newdeviceactivation == True:
            self.ShowDeviceSettings(str(self._checkInTimer.GetTimeout()),
                                    str(self._analyticsTimer.GetTimeout()),
                                    self._settings.GetIODebounce(),
                                    self._settings.GetIOThrottle())

        # Start analytics module
        logging.info("Starting analytics module")
        self._analyticsThread = threading.Thread(name='analyticsthread',
                                                 target=self.StartAnalyticsThread,
                                                 args=(self._analyticsTimer.GetTimeout(),
                                                       self._settings.GetDeviceResourceURL() + "/analytics",),)
        self._analyticsThread.start()

        # Start check-in timer
        if self._currentPlaylist == None:
            self._checkInTimer.Start(0.1)
        else:
            self._checkInTimer.Start(self._settings.GetCheckinTimerValue())

        # Main event loop

        self._checkKbdTimer.Start(20.0)
        self.running = True
        while self.running:
            try:
                # Check check-in timer
                if self._checkInTimer.CheckExpired():
                    self.Checkin(self._settings.GetDeviceResourceURL())
                    self._checkInTimer.Reset(self._settings.GetCheckinTimerValue())

                # Check if need to start playlist
                if self._startPlaylistTimer.CheckExpired():
                    logging.info("Set playlist timer expired")
                    if self._currentPlaylist == None:
                        if self._checkinProcessing == False:
                            logging.debug("No playlist to play")
                        self._startPlaylistTimer.Reset(1.0)
                    else:
                        sequence = self._currentPlaylist.GetDefaultSequence()
                        if sequence != None:
                            content =  self._currentPlaylist.GetContentObj(sequence.GetContentId())
                            if content != None:
                                if content.GetReady():
                                    self.PlayDefaultSequence()
                                    self._startPlaylistTimer.Stop()
                                else:
                                    logging.debug("Content not ready")
                                    self._startPlaylistTimer.Reset(1.0)
                            else:
                                logging.error("No content found")
                                self.ErrorRecovery(1.0)
                        else:
                            logging.error("No sequence found")
                            self.ErrorRecovery(1.0)

                # Check video events
                self.CheckVideoEvents()
            
                # Check delivery events
                self.CheckDeliveryEvents()

                # Check for keyboard
                if self._checkKbdTimer.CheckExpired():
                    if self._checkinProcessing == False:
                        if self.KeyboardPresent():
                            if self.GetUserOption1():
                                logging.info("Settings changed, restarting PieBox")
                                self.running = False
                                break
                            else:
                                logging.info("No settings changed, resuming playlist")
                                self._startPlaylistTimer.Start(0.1)
                            # End nested-nested if
                        # End nested if
                    self._checkKbdTimer.Reset()
                # End if
                
                # Check GPIO events
                self.CheckGPIOEvents()  # this blocks for 100 millisecs
            except Exception as e:
                self.running = False
                logging.error(e)
                logging.exception(traceback.format_exc())
                self.Error("Unrecoverable error, check logs for details!!")
            # End try-except
        logging.info("Bake loop finished")
        self.Quit()
        logging.info("Cleanup complete")
        return


    #
    # Error handling
    #


    def Error(self, errmsg, show=True):
        logging.error(errmsg)
        if show:
            self.OpenOffice()
            self.SendOfficeCmd(json.dumps({Office.ACTION : Office.ERROR,
                                           Office.ERROR: errmsg}))
            nomsg = self._officeLink.CheckEventQ(blocking=True, wait=None)
            self.CloseOffice()


    def ErrorRecovery(self, timerval):
        logging.debug("Check-in error recovery started")
        self._pendingTopPlaylistSignature = ""
        self._settings.SetTopPlaylistSignature("")  # auto save
        self._checkinProcessing = False
        self._checkInTimer.Start(timerval)
        self._startPlaylistTimer.Start(0.1)


    #
    # Misc tools
    #


    def GetHdwInfo(self):
        f = None
        try:
            f = open('/proc/cpuinfo','r')
            lines = f.readlines()
            f.close()
            f = None
            for l in range(0, len(lines)):
                if lines[l][0:6]=='Serial':
                    self._serial = lines[l][10:26].strip()
                elif lines[l][0:8]=='Hardware':
                    self._hardware = lines[l][10:18].strip()
                elif lines[l][0:8]=='Revision':
                    self._model = lines[l][10:16].strip()
        except:
            logging.exception(traceback.format_exc())
            if f != None:
                f.close()


    def KeyboardPresent(self):
        # get content of small file
        def content(filename):
            with open(filename, "r") as f:
                return f.read().strip()
        for dev in glob.glob("/sys/bus/usb/devices/*-*:*/bInterfaceClass"):
            if content(dev) == "03" and content(dev[0:-16]+"/bInterfaceProtocol") == "01":
                return True
        return False
# End class Baker

