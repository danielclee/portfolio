import logging
import re
import threading
import json
import math
import time
import curses
import traceback
import atexit
import pygame
from pygame.locals import *
from threading import Timer
from time import sleep
from sandtimer import SandTimer
from link import Link

class Order:
    # Constants
    ACTION = "action"
    EVENT = "event"
    EXIT = "exit"
    ERROR = "error"
    KEYWORD = "keyword"
    MATCH = "match"

    def __init__(self, link, watchlist):
        self._link = link
        self._running = True
        self._watchList = []
        self._currentString = ""
        self._maxKeywordLength = 0
        self._keywordTimer = SandTimer(30.0)
        self._keywordTimer.Stop()
        for watch in watchlist:
            self.AddWatch(watch)


    def cleanup(self):
        curses.nocbreak()
        curses.echo()
        curses.endwin()


    def Run(self):
        pygame.init()
        screen = pygame.display.set_mode((480, 360))
        font = pygame.font.Font(None, 50)
        pygame.display.iconify()
        try:
            self._running = True
            while self._running:
                # Check for messages
                msg = self._link.CheckCmdQ(blocking=True, wait=0.1)
                if msg != None:
                    logging.debug(msg)
                    cmd_json = json.loads(msg)
                    action = cmd_json[Order.ACTION]
                    if action == Order.KEYWORD:
                        self.AddWatch(cmd_json[Order.KEYWORD])
                        self._keywordTimer.Start()
                    elif action == Order.EXIT:
                        self._running = False

                # Check timer
                if self._keywordTimer.CheckExpired():
                    self._currentString = ""
                    self._keywordTimer.Stop()

                # Poll keyboard
                self.PollKbdInput()

                # Other stuff
                screen.fill ((0, 0, 0))
                block = font.render(self._currentString, True, (255, 255, 255))
                rect = block.get_rect()
                rect.center = screen.get_rect().center
                screen.blit(block, rect)
                pygame.display.flip()
        except Exception as e:
            logging.exception(traceback.format_exc())
        logging.info("Closing Orders")


    def AddWatch(self, towatch):
        self._watchList.append(towatch)
        if len(towatch) > self._maxKeywordLength:
            self._maxKeywordLength = len(towatch)


    def PollKbdInput(self):
        for evt in pygame.event.get():
            if evt.type == KEYDOWN:
                if evt.unicode.isalpha() or evt.unicode.isdigit():
                    if self._currentString == "":
                        self._keywordTimer.Start()
                    self._currentString += str(evt.unicode)
                elif evt.key == K_BACKSPACE:
                    if len(self._currentString) > 0:
                        self._currentString = self._currentString[:-1]
                elif evt.key == K_RETURN:
                    logging.debug("Kbd input entered : " + self._currentString)
                    if self._currentString in self._watchList:
                        print("Sending match")
                        self._link.SendEvent(json.dumps({Order.EVENT : Order.MATCH,
                                                         Order.MATCH : self._currentString}))
                        self._currentString = ""
                        self._keywordTimer.Stop()
                        break
                    if len(self._currentString) >= self._maxKeywordLength:
                        self._currentString = ""
                        self._keywordTimer.Stop()
