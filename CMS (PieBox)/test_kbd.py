import re
import threading
import json
import math
import time
import hashlib
import json
import collections
import tkinter
import datetime
import logging
import traceback
import curses
import atexit
import pygame
import tty
import sys
import termios
import glob
from pygame.locals import *
from threading import Timer
from time import sleep
from link import Link
from order import Order 
from sandtimer import SandTimer

_orderLink = Link()

_currentString = ""

def StartOrderThread(watchlist=None):
    logging.info("Starting order thread")
    order = Order(_orderLink, watchlist)
    order.Run()


def SendOrderCmd(cmd):
    _orderLink.SendCmd(cmd)


def cleanup():
    print("cleaning up")
    curses.nocbreak()
    curses.echo()
    curses.endwin()


def kbdtest1():
    kbinput = input("Enter kbd :")
    print(kbinput)


def kbdtest2():
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    atexit.register(cleanup)
    stdscr.nodelay(1)
    ## stdscr.addstr(0, 23, "Status of gpios 0-31", curses.A_REVERSE)
    while True:
        ## stdscr.refresh()
        time.sleep(0.1)
        c = stdscr.getch()
        if c != curses.ERR:
            print(chr(c))


def kbdtest3():
    _orderthread = threading.Thread(name='orderthread',
                                    target=StartOrderThread)
    _orderthread.start()
    SendOrderCmd(json.dumps({Order.ACTION : Order.KEYWORD,
                              Order.KEYWORD : "3434"}))
    
    # Loop
    running = True
    while running:
        msg = _orderLink.CheckEventQ(blocking=True, wait=None)
        if msg == None:
            continue
        print(msg)
    
    # Close
    if _orderthread != None:
        SendOrderCmd('{"action":"exit"}')
        _orderthread.join()
        _orderthread = None


def kbdtest4():
    _orderthread = threading.Thread(name='orderthread',
                                    target=StartOrderThread)
    _orderthread.start()
    SendOrderCmd(json.dumps({Order.ACTION : Order.KEYWORD,
                              Order.KEYWORD : "3434"}))
    
    # Loop
    running = True
    while running:
        #
        msg = _orderLink.CheckEventQ(blocking=True, wait=0.1)
        if msg != None:
            print(msg)

        # 
        kbinput = input("Enter kbd :")
        print(kbinput)

    # Close
    if _orderthread != None:
        SendOrderCmd('{"action":"exit"}')
        _orderthread.join()
        _orderthread = None


def kbdtest5():
    pygame.init()
    screen = pygame.display.set_mode((480, 360))
    name = ""
    font = pygame.font.Font(None, 50)
    pygame.display.iconify()
    while True:
        for evt in pygame.event.get():
            if evt.type == KEYDOWN:
                if evt.unicode.isalpha():
                    name += evt.unicode
                elif evt.key == K_BACKSPACE:
                    name = name[:-1]
                elif evt.key == K_RETURN:
                    print(name)
                    return
                    name = ""
            elif evt.type == QUIT:
                return
        screen.fill ((0, 0, 0))
        block = font.render(name, True, (255, 255, 255))
        rect = block.get_rect()
        rect.center = screen.get_rect().center
        screen.blit(block, rect)
        pygame.display.flip()
        time.sleep(0.1)
    print("Exitting")
    return


def kbdtest6():
    quitPattern = "3434"
    settingsPattern = "4545"

    _orderthread = threading.Thread(name='orderthread',
                                    target=StartOrderThread,
                                    args=([quitPattern, settingsPattern],),)
    _orderthread.start()

    # Loop
    running = True
    while running:
        msg = _orderLink.CheckEventQ(blocking=True, wait=None)
        if msg == None:
            continue
        event_json = json.loads(msg)
        event = str(event_json[Order.EVENT])
        if event == Order.MATCH:
            ordermatch = event_json[Order.MATCH]
            if ordermatch == quitPattern:
                print("WOOHOO")
                running = False

    # Close
    if _orderthread != None:
        SendOrderCmd('{"action":"exit"}')
        _orderthread.join()
        _orderthread = None


def PollKbdInput():
    global _currentString

    for evt in pygame.event.get():
        if evt.type == KEYDOWN:
            if evt.unicode.isalpha():
                _currentString += evt.unicode
                print("CURRENT : " + _currentString)
        # End if
    # End for


def kbdtest7():
    global _currentString

    _keywordTimer = SandTimer(5.0)
    _keywordTimer.Stop()

    quitPattern = "3434"
    settingsPattern = "4545"
    
    try:
        pygame.init()
        _running = True
        while _running:
            # Poll keyboard
            PollKbdInput()

            # Check for matches
            if _currentString == quitPattern:
                print("Quitting")
                _running = False

            time.sleep(0.1)
        # End while

    except Exception as e:
        logging.exception(traceback.format_exc())
        print("Exitting")


def keyboardPresent():
    # get content of small file
    def content(filename):
        with open(filename, "r") as f:
            return f.read().strip()

    for dev in glob.glob("/sys/bus/usb/devices/*-*:*/bInterfaceClass"):
        if content(dev) == "03" and content(dev[0:-16]+"/bInterfaceProtocol") == "01":
            return True
    return False


def kbdtest8():
    global _currentString

    gg = 0
    while True:
        time.sleep(1.0)
        gg += 1
        if keyboardPresent():
            print("Keyboard is PRESENT")
        else:
            print("Keyboard is MISSING")


def main():
    print("Starting local")
    ## kbdtest1()
    ## kbdtest2()
    ## kbdtest3()
    ## kbdtest4() NOT WORKING
    ## kbdtest5()
    ## kbdtest6()
    ## kbdtest7()
    if kbdtest8():
        print("WOOOHOOO keyboard EXISTS")
    else:
        print("BOOOOOOO keyboard MISSING")


if __name__ == "__main__":
    loglevel = logging.DEBUG
    logformat = '%(asctime)s [%(levelname)s] %(pathname)s::%(funcName)s(%(lineno)s) - %(message)s'
    loghandlers = [logging.FileHandler('test_kb.log'), logging.StreamHandler()]
    logging.basicConfig(level = loglevel, format = logformat, handlers = loghandlers)

    main()
    
