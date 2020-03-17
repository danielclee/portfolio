import logging
import requests
import re
import _thread
import threading
import math
import time
from enum import Enum
from queue import Queue
from threading import Timer
from time import sleep
from link import Link
from playlist import Playlist
from delivery import Delivery
import hashlib
import json
import os
from settings import Settings

_deliveryLink = Link()

class DeliveryState(Enum):
    IDLE = 1
    CHECKIN = 2
    GET_PLAYLIST = 3
    GET_CONTENT_INFO = 4
    GET_CONTENT = 5

_deliveryState = DeliveryState.IDLE
_contentDirectory = "./"
_totalContentSize = 0

_serial = "Unknown"
_model = "Unknown"
_hardware = "Unknown"
_product = "PieBox"
_version = "0.5"

_settings = Settings()
_checkinProcessing = False
_pendingTopPlaylistSignature = ""
_contentDurationLut = {}
_currentPlaylist = None
_playlists = []
_contentList = []


def StartDeliveryThread():
    global _deliveryLink
    delivery = Delivery(_deliveryLink, _contentDirectory)
    delivery.Run()


def networktest():
    print("Starting network test")

    global _playlists
    global _currentPlaylist
    
    ## PBox - Content Activity: checkIn################################## https://fulgent.sandd.studio/api/v1.0/device/a9e1c860-532c-4fb4-af2c-00f0e78748a3
    ## PBox - Content Activity: fetchPlayLists: https://fulgent.sandd.studio/api/v1.0/playlist/01e1cd03-8e6f-4dee-8691-1b849011f34d
    ## PBox - Content Activity: fetchContent: https://fulgent.sandd.studio/api/v1.0/content/9a0c61cc-7729-474d-a507-5b1324477d5a.mp4
    ## PBox - Content Activity: fetchContent: https://fulgent.sandd.studio/api/v1.0/content/b1dd8943-c896-4e98-84f8-674d6da07588.mp4
    ## PBox - Content Activity: fetchContent: https://fulgent.sandd.studio/api/v1.0/content/7608b080-f4f4-4ac0-bd1f-7ff67907b703.mp4
    
    ##{"active": true, "resource": "https://fulgent.sandd.studio/api/v1.0/devices/a9e1c860-532c-4fb4-af2c-00f0e78748a3/", "id": "a9e1c860-532c-4fb4-af2c-00f0e78748a3", "playlists": ["https://fulgent.sandd.studio/api/v1.0/playlist/01e1cd03-8e6f-4dee-8691-1b849011f34d"]}
    
    ##url = 'https://fulgent.sandd.studio/api/v1.0/device/a9e1c860-532c-4fb4-af2c-00f0e78748a3'

    #url = 'https://fulgent.sandd.studio/api/v1.0/device/21f93d56-5b2e-489f-853e-1acfba3de7c2'
    url = 'https://fulgent.sandd.studio/api/v1.0/devices/21f93d56-5b2e-489f-853e-1acfba3de7c2/'
    response = requests.get(url, headers={'accept': 'application/json'})
    print(response)
    if response.status_code == 200:
        print(response.text)
        print("")
        print("")
        print("")
        resource_json = json.loads(response.text)

        ## print(resource_json['playlists'])
        ##     print("WOOHOO")
        ## return
        
        if resource_json['active'] is True:
            print(resource_json['id'])
            playlists = resource_json['playlists']
            for p in range(0, len(playlists)):
                playlisturl = playlists[p]
                playlistresponse = requests.get(playlisturl, headers={'accept': 'application/json'})
                if playlistresponse.status_code == 200:
                    print(playlistresponse.text)
                    _playlists.append(Playlist(playlisturl, playlistresponse.text))
            _currentPlaylist = _playlists[0]
    
            # Download content
            contentlist = _currentPlaylist.GetContentList()
            for c in range(0, len(contentlist)):
                fileurl = contentlist[c].GetResource()
                resquesthead = requests.head(fileurl)
                fileresponse = requests.get(fileurl, stream=True)
                size = int(fileresponse.headers['Content-length'])
                contentlist[c].SetSize(size)
    
                directory = "./" + _currentPlaylist.GetUUID()
                if not os.path.exists(directory):
                    os.makedirs(directory)
                target_path = directory + "/" + contentlist[c].GetFileName()
                ## print(target_path)
                handle = open(target_path, "wb")
                bytesdownloaded = int(0)
                for chunk in fileresponse.iter_content(chunk_size=1048576):
                    if chunk:  # filter out keep-alive new chunks
                        handle.write(chunk)
                        bytesdownloaded += 1048576
                        percentage = round((bytesdownloaded / float(contentlist[c].GetSize())) * 100)
                        print(percentage)
                handle.close()
    
            ## response = requests.get(url, stream=True)
            ## handle = open(target_path, "wb")
            ## for chunk in response.iter_content(chunk_size=512):
            ## if chunk:  # filter out keep-alive new chunks
            ##     handle.write(chunk)            
    
            ## MitOpenCourseUrl = "http://www.archive.org/download/MIT6.006F11/MIT6_006F11_lec01_300k.mp4"
            ## resHead = requests.head(MitOpenCourseUrl)
            ## resGet = requests.get(MitOpenCourseUrl,stream=True)
            ## resHead.headers['Content-length'] # output 169
            ## resGet.headers['Content-length'] # output 121291539
                
            ## #
            ## sequence = None;
            ## _currentPlaylist.ResetCurrentSequence()
            ## sequence = _currentPlaylist.GetDefaultSequence()
            ## contentid = sequence.GetContentId()
            ## content = _currentPlaylist.GetContentObj(contentid)
            ## filename = content.GetFile()
            ## videomsg1 = '{"action":"play", "file":"' + filename + '"}'
            ## print(videomsg1)


def SendDeliveryCmd(cmd):
    global _deliveryLink
    _deliveryLink.SendCmd(cmd)


def Checkin(url):
    global _deliveryState
    _deliveryState = DeliveryState.CHECKIN
    SendDeliveryCmd(json.dumps({Delivery.ACTION : Delivery.CMD_JSON,
                                Delivery.URL : url}))


def ProcessCheckinResponse(msg):
    playlist_json = json.loads(msg)
    
    # If main playlist is active, get all playlists
    if playlist_json[Playlist.ACTIVE] == True:
        playlists = playlist_json[Playlist.PLAYLISTS]
        for p in range(0, len(playlists)):
            playlisturl = playlists[p]
            GetPlaylist(playlisturl)
    else:
        print("Playlists is NOT active")   


def GetPlaylist(url):
    global _deliveryState
    _deliveryState = DeliveryState.GET_PLAYLIST
    SendDeliveryCmd(json.dumps({Delivery.ACTION : Delivery.CMD_JSON,
                                Delivery.URL : url}))


def ProcessPlaylist(url, playlist):  # string, string
    global _playlists
    global _currentPlaylist
    global _contentDirectory
    global _totalContentSize
    
    #  Process playlist and set current playlist
    _playlists.append(Playlist(url, playlist))
    _currentPlaylist = _playlists[0]
    
    # Grab all content for playlist
    contentlist = _currentPlaylist.GetContentList()
    if len(contentlist) == 0:
        print("ERROR : no content to download")

    # Setup downloading of all content
    
    directory = _contentDirectory + _currentPlaylist.GetUUID()
    comma = ""
    uuids = ""
    urls = ""
    filenames = ""
    for c in range(0, len(contentlist)):
        uuids += comma + contentlist[c].GetId()
        urls += comma + contentlist[c].GetResource()
        filenames += comma + contentlist[c].GetFileName()
        comma = ","
    GetMediaContent(directory, uuids, urls, filenames)

    
def GetMediaContent(path, uuids, urls, filenames):
    global _deliveryState
    _deliveryState = DeliveryState.GET_CONTENT
    SendDeliveryCmd(json.dumps({Delivery.ACTION : Delivery.GET_FILE,
                                Delivery.PATH : path,
                                Delivery.UUID : uuids,
                                Delivery.URL : urls,
                                Delivery.FILE : filenames}))


def GetMediaContentProgress(msg):
    global _deliveryState
    _deliveryState = DeliveryState.GET_CONTENT


def deliverytest():
    global _deliveryState
    global _totalContentSize
    global _deliveryLink

    print("Starting delivery test")

    _deliverythread = threading.Thread(name='deliverythread',
                                       target=StartDeliveryThread)
    _deliverythread.start()

    _deviceID = 'a9e1c860-532c-4fb4-af2c-00f0e78748a3'
    _deviceResourceURL = 'https://fulgent.sandd.studio/api/v1.0/device/a9e1c860-532c-4fb4-af2c-00f0e78748a3'
    _deliveryState = DeliveryState.IDLE

    # Check-in
    Checkin(_deviceResourceURL)
    
    # Loop
    running = True
    while running:
        msg = _deliveryLink.CheckEventQ(blocking=True, wait=None)
        if msg == None:
            continue
        logging.debug(msg)
        event_json = json.loads(msg)
        event = str(event_json[Delivery.EVENT])
        
        # Handle json result delivery event
        if event == Delivery.RESULT_JSON:
            result = str(event_json[Delivery.RESULT])
            if _deliveryState == DeliveryState.CHECKIN:
                ProcessCheckinResponse(result)
            elif _deliveryState == DeliveryState.GET_PLAYLIST:
                playlisturl = str(event_json[Delivery.URL])
                ProcessPlaylist(playlisturl, result)
            else:       # bad state
                _deliveryState = DeliveryState.IDLE

        # Handle content download progress event
        elif event == Delivery.PROGRESS:
            if _deliveryState == DeliveryState.GET_CONTENT:
                progress = str(event_json[Delivery.PROGRESS])
                uuid = str(event_json[Delivery.UUID])
                if progress == Delivery.COMPLETE:
                    content = _currentPlaylist.GetContentObj(uuid)
                    content.SetReady(True)
                    print("Progress : uuid - " + uuid + " download complete")
                else:
                    download_bytes = int(event_json[Delivery.DOWNLOADED_SIZE])
                    total_bytes = int(event_json[Delivery.TOTAL_SIZE])
                    print("Progress : progress (" + progress + ") uuid (" + uuid + ") downloaded (" + str(download_bytes) + ") total (" + str(total_bytes) + ")")
                    ## 4545 Notify GUI
            else:
                _deliveryState = DeliveryState.IDLE

        # If error then reset states
        elif event == Delivery.ERROR:
            print("Error delivering, event: " + event + ", state: " + str(_deliveryState))
            _deliveryState = DeliveryState.IDLE

    # Close
    if _deliverythread != None:
        SendDeliveryCmd('{"action":"exit"}')
        _deliverythread.join()
        _deliverythread = None


def GetHdwInfo():
    global _serial
    global _model
    global _hardware
    global _product
    global _version

    f = None
    try:
        f = open('/proc/cpuinfo','r')
        lines = f.readlines()
        f.close()
        f = None
        for l in range(0, len(lines)):
            if lines[l][0:6]=='Serial':
                _serial = lines[l][10:26].strip()
            elif lines[l][0:8]=='Hardware':
                _hardware = lines[l][10:18].strip()
            elif lines[l][0:8]=='Revision':
                _model = lines[l][10:16].strip()
    except:
        if f != None:
            f.close()


def GetNewDeviceToken():
    global _deliveryLink
    global _serial
    global _model
    global _hardware
    global _product
    global _version

    # Get token
    tokenurl = 'https://fulgent.sandd.studio/api/v1.0/device/'
    SendDeliveryCmd(json.dumps({Delivery.ACTION : Delivery.TOKEN,
                                Delivery.URL : tokenurl,
                                Delivery.SERIAL : _serial,
                                Delivery.HARDWARE : _model,
                                Delivery.MODEL : _hardware,
                                Delivery.PRODUCT : _product,
                                Delivery.VERSION : _version}))
    msg = _deliveryLink.CheckEventQ(blocking=True, wait=None)
    if msg == None:
        return None
    else:
        return msg


def tokentest():
    print("Starting token test")

    GetHdwInfo()

    _deliverythread = threading.Thread(name='deliverythread',
                                       target=StartDeliveryThread)
    _deliverythread.start()
    msg = GetNewDeviceToken()
    print(msg)

    event_json = json.loads(msg)
    playlisturl = event_json['resource']
    response = requests.get(playlisturl, headers={'accept': 'application/json'})
    print(response)
    if response.status_code == 200:
        print(response.text)
        resource_json = json.loads(response.text)
        if len(resource_json['playlists']) == 0:
            print("Playlists is EMPTY")
        else:
            print("Processing playlist")


def deliverytest2():
    global _deliveryLink
    global _settings
    global _checkinProcessing
    global _pendingTopPlaylistSignature
    global _contentDurationLut
    global _currentPlaylist
    global _playlists
    global _contentList

    _deliverythread = threading.Thread(name='deliverythread',
                                       target=StartDeliveryThread)
    _deliverythread.start()

    # Check-in
    logging.debug("Checking in")
    _deviceID = 'a9e1c860-532c-4fb4-af2c-00f0e78748a3'
    _deviceResourceURL = 'https://fulgent.sandd.studio/api/v1.0/device/a9e1c860-532c-4fb4-af2c-00f0e78748a3'
    SendDeliveryCmd(json.dumps({Delivery.ACTION : Delivery.GET_TOP_PLAYLIST,
                                Delivery.URL : _deviceResourceURL}))

    # Loop
    running = True
    while running:
        msg = _deliveryLink.CheckEventQ(blocking=True, wait=None)
        if msg == None:
            break
        logging.debug(msg)
        event_json = json.loads(msg)
        event = str(event_json[Delivery.EVENT])

        # Handle json result delivery event

        if event == Delivery.RESULT_TOP_PLAYLIST:
            result = str(event_json[Delivery.RESULT])
            ProcessCheckinResponse(result)

        # Handle content download progress event

        elif event == Delivery.PROGRESS:
            progress = str(event_json[Delivery.PROGRESS])
            uuid = str(event_json[Delivery.UUID])
            if progress == Delivery.COMPLETE:  # content downloaded complete
                logging.debug("Content delivery complete : " + uuid)
                _contentDurationLut[uuid] = int(event_json[Delivery.DURATION])
            else:      # content download in progress
                gg = 0
                ## {"total": 10543621, "event": "progress", "progress": 79, "downloaded": 8388608, "uuid": "bbdd2e49-f683-4853-b293-4c049bab8923"}
                total_bytes = event_json[Delivery.TOTAL_SIZE]
                downloaded_bytes = event_json[Delivery.DOWNLOADED_SIZE]
                logging.debug(("Content delivery in progress : " + uuid +
                               "   " + str(downloaded_bytes) +
                               " / " + str(total_bytes)))
                if _currentPlaylist == None:
                    logging.debug("Showing progress")

        # All playlists are processed

        elif event == Delivery.PLAYLIST_PROCESS_COMPLETE:
            PlaylistProcessingComplete(event_json[Delivery.PLAYLISTS],
                                            event_json[Delivery.PLAYLIST_URLS],
                                            event_json[Delivery.CONTENTS])
            logging.info("All playlists processed")

        # If error then reset states

        elif event == Delivery.ERROR:
            errmsg = "Show error delivering, event: " + event
            logging.error(errmsg)
            _checkinProcessing = False
            _pendingTopPlaylistSignature = ""


    # Close
    if _deliverythread != None:
        logging.debug("Closing delivery thread")
        SendDeliveryCmd('{"action":"exit"}')
        _deliverythread.join()
        _deliverythread = None


def ProcessCheckinResponse(msg):
    global _settingsa
    global _checkinProcessing
    global _pendingTopPlaylistSignature
    global _contentDurationLut
    global _currentPlaylist
    global _playlists
    global _contentList

    logging.debug("Processing checkin : " + msg)

    # Generate signature for top playlist
    sha1 = hashlib.sha1()
    sha1.update(msg.encode('utf-8'))
    sha1str = str(sha1.hexdigest())

    # If signature hasn't changed, then no playlist changes
    logging.debug("Settings signature : " + _settings.GetTopPlaylistSignature())
    logging.debug("New signature : " + sha1str)
    if sha1str == _settings.GetTopPlaylistSignature():
        logging.debug("Top playlist unchanged, aborting checkin")
        _checkinProcessing = False
        _pendingTopPlaylistSignature = ""
        return

    # Set processing flag and cache signature
    _checkinProcessing = True
    _pendingTopPlaylistSignature = sha1str
    _contentDurationLut.clear()

    # If top playlist is not active then not licensed
    playlist_json = json.loads(msg)
    if playlist_json[Playlist.ACTIVE] != True:
        logging.debug("Top playlist not active, aborting checkin")
        _checkinProcessing = False
        _pendingTopPlaylistSignature = ""
        logging.info("Showing licensing options")
        return

    # Send to delivery module to handle
    SendDeliveryCmd(json.dumps({Delivery.ACTION : Delivery.PROCESS_TOP_PLAYLIST,
                                Delivery.TOP_PLAYLIST : msg}))


def PlaylistProcessingComplete(playlisturls, playlists, contents):
    global _settings
    global _checkinProcessing
    global _pendingTopPlaylistSignature
    global _contentDurationLut
    global _currentPlaylist
    global _playlists
    global _contentList

    logging.debug("Finalizing playlist processing")

    # Stop any playing video
    logging.debug("Stopping all video" + msg)
    _currentPlaylist = None

    # Set new playlists
    _playlists.clear()
    contentlist = []
    for p in range(0, len(playlists)):
        playlistobj = Playlist(playlisturls[p], playlists[p])
        _playlists.append(playlistobj)
        contentlist += playlistobj.GetContentList()
    _currentPlaylist = _playlists[0]

    # Cleanup content
    CleanupContent(contents)
    _contentList.clear()
    _contentList = contents[:]

    # Save data
    _settings.ClearPlaylistLut()
    for playlist in _playlists:
        _settings.AddPlaylist(playlist.GetUrl(), playlist.GetJSON(), false)
    _settings.Save()
    
    # Other cleanup
    _settings.SetTopPlaylistSignature(_pendingTopPlaylistSignature)  # save signature
    _startPlaylistTimer.Start(0.1)
    _checkinProcessing = False


def CleanupContent(newcontentlist):
    global _settings
    global _checkinProcessing
    global _pendingTopPlaylistSignature
    global _contentDurationLut
    global _currentPlaylist
    global _playlists
    global _contentList

    logging.debug("Cleaning up content list")
    if len(newcontentlist) == 0:
        logging.debug("New content list is empty")
        return
    for content in _contentList:
        if not content in newcontentlist:
            logging.debug("Removing content : " + content)
            os.remove(content)


def deliverytest3():
    global _deliveryLink
    global _settings
    global _checkinProcessing
    global _pendingTopPlaylistSignature
    global _contentDurationLut
    global _currentPlaylist
    global _playlists
    global _contentList

    _deliverythread = threading.Thread(name='deliverythread',
                                       target=StartDeliveryThread)
    _deliverythread.start()

    _deviceID = 'a9e1c860-532c-4fb4-af2c-00f0e78748a3'
    _deviceResourceURL = 'https://fulgent.sandd.studio/api/v1.0/device/a9e1c860-532c-4fb4-af2c-00f0e78748a3'

    # Process and save playlist
    key = 'https://fulgent.sandd.studio/api/v1.0/playlist/59d8de29-c3a3-4464-9ba7-1349ea4edb7d'
    value = '{"sequence": [{"content_id": "bbdd2e49-f683-4853-b293-4c049bab8923", "next_sequence": null, "entrance_actions": [{"action": "set_volume", "target": "6", "parameters": null}, {"action": "led_on", "target": "led10", "parameters": null}, {"action": "led_on", "target": "led09", "parameters": null}, {"action": "led_cycle", "target": "led02", "parameters": null}, {"action": "led_cycle", "target": "led01", "parameters": null}, {"action": "set_screen_brightness", "target": "70", "parameters": null}], "id": "6f3f89f6-fbcb-47e2-bc17-e9fe25b04544", "name": "Rapids", "triggers": {"pb01": [{"action": "next_sequence", "target": "71957627-c495-4138-b0d7-6d7894259ca5", "parameters": null}], "pb02": [{"action": "next_sequence", "target": "d5fa2f92-c29a-4c4b-8f15-492bd917d295", "parameters": null}], "pb09": [{"action": "volume_up", "target": "1", "parameters": null}], "pb10": [{"action": "volume_down", "target": "1", "parameters": null}]}, "dwell_time": 10}, {"content_id": "ea8127a9-885f-4e54-955f-0b46e55f4c5b", "next_sequence": null, "entrance_actions": [{"action": "led_on", "target": "led10", "parameters": null}, {"action": "set_volume", "target": "10", "parameters": null}, {"action": "set_screen_brightness", "target": "100", "parameters": null}, {"action": "led_on", "target": "led09", "parameters": null}, {"action": "led_on", "target": "led01", "parameters": null}], "id": "71957627-c495-4138-b0d7-6d7894259ca5", "name": "Sound", "triggers": {"pb02": [{"action": "next_sequence", "target": "d5fa2f92-c29a-4c4b-8f15-492bd917d295", "parameters": null}], "pb09": [{"action": "volume_up", "target": "3", "parameters": null}], "pb10": [{"action": "volume_down", "target": "3", "parameters": null}]}, "dwell_time": 10}, {"content_id": "ca01bd1c-99ab-4d5b-9761-a55d208114c1", "next_sequence": null, "entrance_actions": [{"action": "set_volume", "target": "9", "parameters": null}, {"action": "set_screen_brightness", "target": "100", "parameters": null}, {"action": "led_on", "target": "led02", "parameters": null}], "id": "d5fa2f92-c29a-4c4b-8f15-492bd917d295", "name": "Boots", "triggers": {"pb01": [{"action": "next_sequence", "target": "71957627-c495-4138-b0d7-6d7894259ca5", "parameters": null}], "pb09": [{"action": "volume_down", "target": "3", "parameters": null}, {"action": "volume_up", "target": "3", "parameters": null}]}, "dwell_time": 10}], "content": [{"content_id": "bbdd2e49-f683-4853-b293-4c049bab8923", "url": "https://fulgent.sandd.studio/api/v1.0/content/9a0c61cc-7729-474d-a507-5b1324477d5a.mp4"}, {"content_id": "ea8127a9-885f-4e54-955f-0b46e55f4c5b", "url": "https://fulgent.sandd.studio/api/v1.0/content/8d135e28-1073-459d-a891-09fd4b0f511e.mp4"}, {"content_id": "ca01bd1c-99ab-4d5b-9761-a55d208114c1", "url": "https://fulgent.sandd.studio/api/v1.0/content/7608b080-f4f4-4ac0-bd1f-7ff67907b703.mp4"}], "id": "59d8de29-c3a3-4464-9ba7-1349ea4edb7d"}'

    playlistobj = Playlist(key, value)
    _playlists.append(playlistobj)

    # Check if the content files exist
    comma = ""
    uuids = ""
    urls = ""
    filenames = ""
    directory = _contentDirectory + playlistobj.GetUUID()
    contentlist = playlistobj.GetContentList()

    print("Getting blocking media")
    BlockingGetMediaContent(directory, playlistobj.GetContentList())

    ## for c in range(0, len(contentlist)):
    ##     cfilepath = directory + "/" + contentlist[c].GetFileName()
    ##     if not os.path.isfile(cfilepath):
    ##         uuids += comma + contentlist[c].GetId()
    ##         urls += comma + contentlist[c].GetResource()
    ##         filenames += comma + contentlist[c].GetFileName()
    ##         comma = ","
    ##     self._contentList.append(cfilepath)
    ## 
    ## # If there is content files to download, download them
    ## if len(uuids) > 0:
    ##     self.BlockingGetMediaContent(contentlist[c], directory, uuids,
    ##                                  urls, filenames)



def BlockingGetMediaContent(path, contentobjlist):
    logging.debug("Blocking getting media content")
    logging.debug("-----------OPEN OFFICE-----------")
    for contentobj in contentobjlist:
        SendDeliveryCmd(json.dumps({Delivery.ACTION : Delivery.GET_FILES,
                                    Delivery.PATH : path,
                                    Delivery.UUID : contentobj.GetId(),
                                    Delivery.URL : contentobj.GetResource(),
                                    Delivery.FILE : contentobj.GetFileName()}))
        while True:
            msg = _deliveryLink.CheckEventQ(blocking=True, wait=None)
            if msg != None:
                event_json = json.loads(msg)
                event = str(event_json[Delivery.EVENT])
                if event == Delivery.PROGRESS:
                    progress = str(event_json[Delivery.PROGRESS])
                    uuid = str(event_json[Delivery.UUID])
                    if progress == Delivery.COMPLETE:  # content downloaded complete
                        contentobj.SetReady(True)
                        contentobj.SetDuration(int(event_json[Delivery.DURATION]))
                        logging.debug("Content delivery complete : " + uuid)
                        break
                    else:                              # content download in progress
                        total_bytes = event_json[Delivery.TOTAL_SIZE]
                        downloaded_bytes = event_json[Delivery.DOWNLOADED_SIZE]
                        logging.debug(("Content delivery in progress : " + uuid +
                                       "   " + str(downloaded_bytes) +
                                       " / " + str(total_bytes)))
                elif event == Delivery.ERROR:
                    logging.error("Error downloading content")
                    break
            else:
                logging.error("Error downloading content, exiting loop")
                break
    logging.debug("-----------CLOSE OFFICE-----------")


##======================================================================

def main():
    print("Starting local")

    try:
        # Setup logging
    
        loglevel = logging.DEBUG
        logformat = '%(asctime)s [%(levelname)s] %(pathname)s::%(funcName)s(%(lineno)s) - %(message)s'
        loghandlers = [logging.FileHandler('test_network.log'), logging.StreamHandler()]
        logging.basicConfig(level = loglevel, format = logformat, handlers = loghandlers)
    
        # Test token
        ## tokentest()
    
        # Test network
        ## networktest()
    
        # Test delivery
        ## deliverytest()
    
        # Test delivery
        ## deliverytest2()

        # Test delivery
        deliverytest3()
    except:
        gg = 0
    finally:
        logging.shutdown()


if __name__ == "__main__":
    main() 
