import logging
import pexpect
import re
import json
import enum
import os.path
import pygame
import subprocess
from pygame.locals import *
from pathlib import Path
from queue import *
from link import Link
from time import sleep
from sandtimer import SandTimer

class VideoPlayer:
    class VideoPlayerState(enum.Enum):
        IDLE = 1
        PLAYING = 2  # video
        SHOWING = 3  # image

    class DisplayState(enum.Enum):
        UNKNOWN = 1
        MAXIMIZED = 2
        MINIMIZED = 3

    # Constants
    ACTION = "action"
    PLAY = "play"
    STOP = "stop"
    EXIT = "exit"
    VOLUME_UP = "volume_up"
    VOLUME_DN = "volume_dn"
    CLEAN = "clean"
    FILE = "file"
    SOUND_LEVEL = "sound_level"
    DWELL = "dwell"
    EVENT = "event"
    HIDE = "hide"
    DONE = "done"
    ERROR = "error"

    def __init__(self, link):
        self._link = link
        self.videoProcess = None
        self.imageProcess = None
        self.state = self.VideoPlayerState.IDLE
        self.displayState = self.DisplayState.UNKNOWN
        self.playTimer = SandTimer(1.0)
        self.playTimer.Stop()
        self.imageTimer = SandTimer(1.0)
        self.imageTimer.Stop()
        self.videoDurationLut = {}
        self.imageLut = {}
        try:
            pygame.display.init()
            self.screenHeight = pygame.display.Info().current_h
            self.screenWidth = pygame.display.Info().current_w
            logging.debug("Screen width : " + str(self.screenWidth))
            logging.debug("Screen height : " + str(self.screenHeight))
            self.screen = pygame.display.set_mode([self.screenWidth,
                                                   self.screenHeight],
                                                  pygame.FULLSCREEN)
            self.screen.fill([0, 0, 0])
            pygame.mouse.set_visible(False)  # hide mouse
            pygame.display.update()
            self.displayState = self.DisplayState.MAXIMIZED
            self.running = True
        except:
            logging.error("Unable to initialize frame buffer!")
            self.SendError("Error setting up video player!!")
            self.running = False


    def __del__(self):
        logging.debug("Quitting pygame")
        self.Clean()
        pygame.quit()


    def Clean(self):
        self.imageLut.clear()


    def PlayMedia(self, filepath, soundlevel, dwell):
        extension = filepath.rpartition('.')[-1]
        extension = extension.lower()
        if (extension=='mp4') or (extension=='avi') or (extension=='mkv'):
            self.PlayVideo(filepath, soundlevel)
        elif (extension=='jpeg') or (extension=='jpg') or (extension=='png'):
            self.ShowImage(filepath, dwell)


    def PlayVideo(self, filepath, level):
        if self.videoProcess != None:
            logging.debug("Video process detected, shutting down")
            self.videoProcess.send('q')
            self.videoProcess.terminate(True)
            self.videoProcess.close()
            self.videoProcess = None

        logging.debug("Playing video : " + filepath)

        # Get video duration info
        duration = 0
        if filepath in self.videoDurationLut:
            duration = self.videoDurationLut[filepath]
        else:
            self.videoProcess = pexpect.spawn('/usr/bin/omxplayer -i ' + filepath)
            pattern = re.compile(r'Duration: (\d{2}):(\d{2}):(\d{2}).(\d{2,})')
            res = re.search(pattern, self.videoProcess.read().decode('utf-8'))
            if res != None:
                if res.groups() and (len(res.groups()) == 4):
                    hour = int(res.group(1)) * 60 * 60
                    min = int(res.group(2)) * 60
                    sec = int(res.group(3))
                    msec = int(res.group(4))
                    frac = float(msec) / 1000
                    duration = float(hour + min + sec) + frac
                    if duration > 0.0:
                        self.videoDurationLut[filepath] = duration
                    logging.debug("Video has duration of " + str(duration))
        # End if/else
    
        # Set sound level
        millibel = str(int(-6000 + (6000 * (level / 10))))
            
        # Call omxplayer to play video
        self.videoProcess = None
        if duration > 0:
            logging.debug("video starting")
            cmd = ("/usr/bin/omxplayer --threshold 0 --vol {v} {f}".\
                   format(v=millibel, f=filepath))
            self.videoProcess = pexpect.spawn(cmd, timeout=duration)
            self.state = self.VideoPlayerState.PLAYING
            overplayprotection = duration + 3.0
            self.playTimer.Start(overplayprotection)
        else:   # video play error
            logging.error("Video has no duration, aborting video play")
            self.SendError("No duration found for video")
            self.state = self.VideoPlayerState.IDLE
            self.playTimer.Stop()


    def ShowImage(self, filepath, dwell):
        try:
            if self.displayState != self.DisplayState.MAXIMIZED:
                self.screen = pygame.display.set_mode([self.screenWidth,
                                                       self.screenHeight],
                                                      pygame.FULLSCREEN)
                self.screen.fill([0, 0, 0])
                self.displayState = self.DisplayState.MAXIMIZED
            image = self.imageLut.get(filepath)
            if image == None:
                image = pygame.image.load(filepath)
                self.imageLut[filepath] = image
            h = image.get_height()
            w = image.get_width()
            logging.debug("Image width : " + str(w))
            logging.debug("Image height : " + str(h))
            # If the image isn't already the same size as the screen, it needs to be scaled
            if ((h!=self.screenHeight) or (w!=self.screenWidth)):
                scaled_height = int((float(self.screenWidth) / w) * h)
                if (scaled_height > self.screenHeight):
                    scaled_height = self.screenHeight
                    scaled_width = int((float(self.screenHeight) / h) * w)
                else:
                    scaled_width = self.screenWidth
                img_bitsize = image.get_bitsize()
                if (img_bitsize == 24 or img_bitsize == 32):
                    image = pygame.transform.smoothscale(image, [scaled_width, scaled_height])
                else:
                    image = pygame.transform.scale(image, [scaled_width, scaled_height])
                display_x = (self.screenWidth - scaled_width) / 2
                display_y = (self.screenHeight - scaled_height) / 2
            else:
                display_x = 0
                display_y = 0
            self.screen.fill([0, 0, 0])  # blank screen
            self.screen.blit(image, [display_x, display_y])
            pygame.display.update()
            self.state = self.VideoPlayerState.SHOWING
            self.imageTimer.Start(dwell)
            logging.debug("Starting image dwell timer : " + str(dwell))
        except:
            self.screen.fill([0, 0, 0])        
            pygame.display.update()
            logging.error("Error loading image " + filepath)
            self.SendError("Error loading image")
            self.state = self.VideoPlayerState.IDLE
            self.imageTimer.Stop()

        ## Alternative code
        ##  if self.imageProcess != None:
        ##      logging.debug("Image process detected, shutting down")
        ##      self.imageProcess.send('q')
        ##      self.imageProcess.terminate(True)
        ##      self.imageProcess.close()
        ##      self.imageProcess = None
        ##  
        ##  logging.debug("Showing image : " + filepath)
        ##  
        ##  # Call feh to show image
        ##  self.imageProcess = None
        ##  if dwell > 0:
        ##      logging.debug("image starting")
        ##      cmd = ("/usr/bin/feh -F {f}".format(f=filepath))
        ##      self.imageProcess = pexpect.spawn(cmd, timeout=dwell)
        ##      self.state = self.VideoPlayerState.SHOWING
        ##      self.imageTimer.Start(dwell)
        ##      logging.debug("Starting image dwell timer : " + str(dwell))
        ##  else:   # show image error
        ##      logging.error("Image has no dwell, aborting showing image")
        ##      self.SendError("No dwell found for image")
        ##      self.state = self.VideoPlayerState.IDLE
        ##      self.imageTimer.Stop()
        ## Alternative code


    def Stop(self, sendevent=True):
        if self.videoProcess != None:
            self.videoProcess.send('q')
            self.videoProcess.terminate(True)
            self.videoProcess.close()
            self.videoProcess = None
            logging.debug("stopping video")
        ## Alternative code
        ##  if self.imageProcess != None:
        ##      self.imageProcess.send('q')
        ##      self.imageProcess.terminate(True)
        ##      self.imageProcess.close()
        ##      self.imageProcess = None
        ##      logging.debug("stopping image")
        ## Alternative code
        if self.state == self.VideoPlayerState.SHOWING:
            self.screen.fill([0, 0, 0])        
            pygame.display.update()
            logging.debug("stopping showing image")
        self.playTimer.Stop()
        self.imageTimer.Stop()
        self.state = self.VideoPlayerState.IDLE
        if sendevent:
            self._link.SendEvent('{"event":"done"}')


    def CheckVideoPlayingStatus(self):
        try:
            if self.videoProcess == None:
                return
            videostatus = self.videoProcess.expect_exact([pexpect.TIMEOUT, pexpect.EOF,
                                                          'Aborted', 'Segmentation fault'],
                                                         timeout=0.1)
            if videostatus == 0:  # timeout
                if self.playTimer.CheckExpired():
                    logging.debug("Video play timer expired, stopping video play")
                    self.Stop()
                return            # still playing
            elif videostatus == 1:  # eof
                self.Stop()
            elif videostatus == 2:  # Aborted
                self.Stop()
                self.SendError("Video aborted prematurely")
            elif videostatus == 3:  # Seg fault
                self.Stop()
                self.SendError("Video crashed prematurely")
            else:
                self.Stop()
                self.SendError("Unknown video error")
        except pexpect.exceptions.TIMEOUT:
            self.state = self.VideoPlayerState.PLAYING
        except pexpect.exceptions.EOF:
            self.Stop()
        except Exception as e:
            logging.error(e)
            logging.exception(traceback.format_exc())
            self.Stop()


    def CheckImageShowingStatus(self):
        if self.state != self.VideoPlayerState.SHOWING:
            return
        if self.imageTimer.CheckExpired():
            logging.debug("Image showing timer expired, clearing image")
            self.Stop()


    def VolumeUp(self):
        if self.videoProcess != None:
            logging.debug("volume up")
            self.videoProcess.send('+')


    def VolumeDown(self):
        if self.videoProcess != None:
            logging.debug("volume down")
            self.videoProcess.send('-')


    def SendError(self, errmsg):
        self._link.SendEvent(json.dumps({VideoPlayer.EVENT : VideoPlayer.ERROR,
                                         VideoPlayer.ERROR : errmsg}))


    def Hide(self):
        if self.displayState != self.DisplayState.MINIMIZED:
            self.screen = pygame.display.set_mode([1, 1], pygame.NOFRAME)
            self.screen.fill([0, 0, 0])        
            self.displayState = self.DisplayState.MINIMIZED


    def Run(self):
        try:
            while self.running:
                # Check for messages
                msg = self._link.CheckCmdQ(blocking=True, wait=0.05)
                if msg != None:
                    logging.debug(msg)
                    vid_json = json.loads(msg)
                    action = vid_json[VideoPlayer.ACTION]

                    # Always check for these command no matter what state

                    if action == VideoPlayer.HIDE:  # hide
                        self.Hide()
                        continue
                    elif action == VideoPlayer.STOP:  # stop
                        self.Stop(sendevent=False)
                        continue
                    elif action == VideoPlayer.EXIT:   #   exit
                        self.Stop(sendevent=False)
                        self.running = False
                        break
                    elif action == VideoPlayer.CLEAN:   # clean
                        self.Clean()
                        continue
                    
                    
                    # Handle actions based on state

                    if self.state == self.VideoPlayerState.IDLE:  # idle state
                        logging.debug(msg)
                        if action == VideoPlayer.PLAY:  # play
                            f = str(vid_json['file'])
                            slevel = int(vid_json[VideoPlayer.SOUND_LEVEL])
                            dwell = int(vid_json[VideoPlayer.DWELL])
                            if os.path.exists(f):
                                self.PlayMedia(f, slevel, dwell)
                            else:
                                logging.error("Video file not exist : " + f)
                    elif self.state == self.VideoPlayerState.PLAYING:  # playing state
                        logging.debug(msg)
                        if action == VideoPlayer.VOLUME_UP:  # vol up
                            self.VolumeUp()
                        elif action == VideoPlayer.VOLUME_DN:  # vol down
                            self.VolumeDown()
                    # End nested if/elif
                # End if

                # Check video status
                self.CheckVideoPlayingStatus()

                # Check image status
                self.CheckImageShowingStatus()
            # End while
        except Exception as e:
            logging.error(e)
            logging.exception(traceback.format_exc())
        finally:
            logging.info("Exiting video player")
