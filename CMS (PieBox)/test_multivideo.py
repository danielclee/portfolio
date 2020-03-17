import pexpect
import re
import _thread
import threading
import json
import math
import time
import logging
from enum import Enum
from queue import Queue
from threading import Timer
from time import sleep
from videoplayer import VideoPlayer
from datastore import DataStore
from link import Link
import hashlib
import json

_videoLink = Link()

class SequenceState(Enum):
    IDLE = 1
    PLAYING = 2

def StartVideoPlayerThread():
    player = VideoPlayer(_videoLink)
    player.Run()


def SendVideoCmd(cmd):
    _videoLink.SendCmd(cmd)


def videotest():
    print("Starting video test")
    
    # Start threads
    videothread = threading.Thread(name='videoplayerthread', target=StartVideoPlayerThread)
    videothread.start()

    ##vidplaymsg = '{"action":"play", "file":"./big_buck_bunny_720p_30mb.mp4"}'
    vidplaymsg = '{"action":"play", "file":"./sandbox/clips/WiegelesHeliSki_DivXPlus_19Mbps.mkv"}'
    vidplaymsg = json.dumps({VideoPlayer.ACTION : VideoPlayer.PLAY, 
                             VideoPlayer.FILE : "./sandbox/clips/WiegelesHeliSki_DivXPlus_19Mbps.mkv", 
                             VideoPlayer.SOUND_LEVEL : 2})
            
    vidstopmsg = '{"action":"stop"}'
    _videoLink.SendCmd(vidplaymsg)
    gg = 0
    while True:
        event = _videoLink.CheckEventQ(blocking=True, wait=1.0)
        gg += 1
        print(gg);
        ##3434## if gg < 21:
        ##3434##     _videoLink.SendCmd(json.dumps({VideoPlayer.ACTION : VideoPlayer.VOLUME_DN}))
        ##3434## elif gg < 15:
        ##3434##     _videoLink.SendCmd(json.dumps({VideoPlayer.ACTION : VideoPlayer.VOLUME_DN}))
        if gg == 20:
            print("Sending video quit")
            _videoLink.SendCmd('{"action":"stop"}')
            _videoLink.SendCmd('{"action":"exit"}')
            videothread.join()
            break


def videotest2():
    print("Starting video test 2")

    # Start threads
    videothread = threading.Thread(name='videoplayerthread', target=StartVideoPlayerThread)
    videothread.start()

    fileloc1 = "./b30d6c94-237e-4a00-be05-8d397a8bb084/16d2b491-e90d-4373-a8d5-46394e96bd4e.mp4"
    fileloc2 = "./b30d6c94-237e-4a00-be05-8d397a8bb084/39de4b17-e0f8-4699-b482-9411eb160f1d.mp4"
    fileloc3 = "./b30d6c94-237e-4a00-be05-8d397a8bb084/7a804db7-6c32-4d11-aa50-5791d4a8ba33.mp4"
    status = SequenceState.IDLE
    while True:
        if status == SequenceState.IDLE:
            print("In idle state")
            ## _videoLink.SendCmd('{"action":"stop"}')
            _videoLink.SendCmd(json.dumps({VideoPlayer.ACTION : VideoPlayer.PLAY,
                                           VideoPlayer.FILE : fileloc1,
                                           VideoPlayer.SOUND_LEVEL : 5}))
            status = SequenceState.PLAYING
            print("PLAYING")

        msg = _videoLink.CheckEventQ(blocking=True, wait=0.1)
        if msg != None:
            print(msg)
            event_json = json.loads(msg)
            event = event_json[VideoPlayer.EVENT]
            if event == VideoPlayer.DONE:
                print("Video playing COMPLETE")
                status = SequenceState.IDLE
            elif event == VideoPlayer.ERROR:
                print("Unrecoverable video error!!")
                break
                
                
def main():
    loglevel = logging.DEBUG
    logformat = '%(asctime)s [%(levelname)s] %(pathname)s::%(funcName)s(%(lineno)s) - %(message)s'
    loghandlers = [logging.FileHandler('test_video.log'), logging.StreamHandler()]
    logging.basicConfig(level = loglevel, format = logformat, handlers = loghandlers)

    print("Starting test video pie")

    # Test video
    ##videotest()
    videotest2()


if __name__ == "__main__":
    main()
