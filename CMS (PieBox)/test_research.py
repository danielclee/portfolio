import pexpect
import re
import _thread
import threading
import json
import math
import time
from queue import Queue
from threading import Timer
from time import sleep
from videoplayer import VideoPlayer
from gpiocontroller import GPIOController
from datastore import DataStore
from playlist import Playlist
from link import Link
import hashlib
import json


_videoLink = Link()
_gpioLink = Link()

def StartVideoPlayerThread():
    player = VideoPlayer(_videoLink)
    player.Run()


def StartGPIOThread(self):
    gpio = GPIOController(_gpioLink)
    gpio.Run()


def test():
    # Start threads
    videothread = threading.Thread(name='videoplayerthread', target=StartVideoPlayerThread)
    videothread.start()
    gpiothread = threading.Thread(name='gpiothread', target=StartGPIOThread)
    gpiothread.start()

    # Start db
    db = DataStore()

    f = './big_buck_bunny_720p_30mb.mp4'

    vidplaymsg = '{"action":"play", "file":"./big_buck_bunny_720p_30mb.mp4"}'
    vidstopmsg = '{"action":"stop"}'
    gpiomsg1 = '{"action":"reset"}'
    gpiomsg2 = '{"action":"setup_input", "inputs":"pb01,pb02", "debounce":"250", "throttle":"1"}'
    gpiomsg3 = '{"action":"led_on", "outputs":"led01,led02"}'
    gpiomsg4 = '{"action":"led_off", "outputs":"led01,led02"}'
    gpiomsg5 = '{"action":"led_blink", "outputs":"led01,led02", "interval":"1.5"}'
    GpioCmdQ.put_nowait('{"action":"exit"}')
    VideoPlayerQ.put_nowait('{"action":"exit"}')
    gpiothread.join()
    videothread.join()
    return

    ######################################################

    gg = 0
    while True:
        sleep(1.0)
        print("sleeping")
        gg += 1

        ## ## GPIO module tests
        ## ## -----------------
        ## if gg == 5:
        ##     GpioCmdQ.put_nowait(gpiomsg5)
        ## 
        ## ## Video module tests
        ## ## ------------------
        ## if gg == 10:
        ##     print(vidplaymsg)
        ##     VideoPlayerQ.put_nowait(vidplaymsg)
        ## if gg == 15:
        ##     VideoPlayerQ.put_nowait(vidstopmsg)
        ## if gg == 20:
        ##     VideoPlayerQ.put_nowait(vidplaymsg)


def main():
    print("Starting pie")

    # Start baker
    baker = Baker()
    baker.Start()


if __name__ == "__main__":
    main()
