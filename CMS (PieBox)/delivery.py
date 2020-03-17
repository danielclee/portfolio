import logging
import pexpect
import requests
import re
import _thread
import threading
import math
import time
import json
import os
import traceback
from enum import Enum
from queue import Queue
from threading import Timer
from time import sleep
from link import Link
from time import sleep
from playlist import Playlist

class Delivery:
    class HttpResponseStatusCodes(Enum):
        # Informational responses
        HTTP_RESPONSE_CONTINUE = 100
        HTTP_RESPONSE_SWITCH_PROTOCOL = 101
        HTTP_RESPONSE_PROCESSING = 102
        # Success
        HTTP_RESPONSE_OK = 200
        HTTP_RESPONSE_CREATED = 201
        HTTP_RESPONSE_ACCEPTED = 202
        HTTP_RESPONSE_NONAUTH_INFO = 203
        HTTP_RESPONSE_NO_CONTENT = 204
        HTTP_RESPONSE_RESET_CONTENT = 205
        HTTP_RESPONSE_PARTIAL_CONTENT = 206
        HTTP_RESPONSE_MULTI_STATUS = 207
        HTTP_RESPONSE_ALREADY_REPORTED = 208
        HTTP_RESPONSE_IM_USED = 226
        # Redirection
        HTTP_RESPONSE_MULTIPLE_CHOICES = 300
        HTTP_RESPONSE_MOVED_PERMANENTLY = 301
        HTTP_RESPONSE_FOUND = 302
        HTTP_RESPONSE_SEE_OTHER = 303
        HTTP_RESPONSE_NOT_MODIFIED = 304
        HTTP_RESPONSE_USE_PROXY = 305
        HTTP_RESPONSE_SWITCH_PROXY = 306
        HTTP_RESPONSE_TEMP_REDIRECT = 307
        HTTP_RESPONSE_PERMANENT_REDIRECT = 308
        # Client errors
        HTTP_RESPONSE_BAD_REQUEST = 400
        HTTP_RESPONSE_UNAUTHORIZED = 401
        HTTP_RESPONSE_PAYMENT_REQUIRED = 402
        HTTP_RESPONSE_FORBIDDEN = 403
        HTTP_RESPONSE_NOT_FOUND = 404
        HTTP_RESPONSE_METHOD_NOT_ALLOWED = 405
        HTTP_RESPONSE_NOT_ACCEPTABLE = 406
        HTTP_RESPONSE_PROXY_AUTHENTICATION_REQUIRED = 407
        HTTP_RESPONSE_REQUEST_TIMEOUT = 408
        HTTP_RESPONSE_CONFLICT = 409
        HTTP_RESPONSE_GONE = 410
        HTTP_RESPONSE_LENGTH_REQUIRED = 411
        HTTP_RESPONSE_PRECONDITION_FAILED = 412
        HTTP_RESPONSE_PAYLOAD_TOO_LARGE = 413
        HTTP_RESPONSE_URI_TOO_LONG = 414
        HTTP_RESPONSE_UNSUPPORTED_MEDIA_TYPE = 415
        HTTP_RESPONSE_RANGE_NOT_SATISFIABLE = 416
        HTTP_RESPONSE_EXPECTATION_FAILED = 417
        HTTP_RESPONSE_TEAPOT = 418
        HTTP_RESPONSE_MISDIRECTED_REQUEST = 421
        HTTP_RESPONSE_UNPROCESSABLE_ENTITY = 422
        HTTP_RESPONSE_LOCKED = 423
        HTTP_RESPONSE_FAILED_DEPENDENCY = 424
        HTTP_RESPONSE_UPGRADE_REQUIRED = 426
        HTTP_RESPONSE_PRECONDITION_REQUIRED = 428
        HTTP_RESPONSE_TOO_MANY_REQUESTS = 429
        HTTP_RESPONSE_REQUEST_HEADER_FIELDS_TOO_LARGE = 431
        HTTP_RESPONSE_LEGAL_REASONS = 451
        # Server errors
        HTTP_RESPONSE_INTERNAL_SERVER_ERROR = 500
        HTTP_RESPONSE_NOT_IMPLEMENTED = 501
        HTTP_RESPONSE_BAD_GATEWAY = 502
        HTTP_RESPONSE_SERVICE_UNAVAILABLE = 503
        HTTP_RESPONSE_GATEWAY_TIMEOUT = 504
        HTTP_RESPONSE_HTTP_VERSION_NOT_SUPPORTED = 505
        HTTP_RESPONSE_VARIANT_ALSO_NEGOTIATES = 506
        HTTP_RESPONSE_INSUFFICIENT_STORAGE = 507
        HTTP_RESPONSE_LOOP_DETECTED = 508
        HTTP_RESPONSE_NOT_EXTENDED = 510
        HTTP_RESPONSE_NETWORK_AUTHENTICATION_REQUIRED = 511
        # Internet Information Services
        HTTP_RESPONSE_LOGIN_TIMEOUT = 440
        HTTP_RESPONSE_RETRY_WITH = 449
        HTTP_RESPONSE_REDIRECT = 451
        # NGINX
        HTTP_RESPONSE_NO_RESPONSE = 444
        HTTP_RESPONSE_SSL_CERTIFICATE_ERROR = 495
        HTTP_RESPONSE_SSL_CERTIFICATE_REQUIRED = 496
        HTTP_RESPONSE_HTTP_REQUEST_SENT_TO_HTTPS_PORT = 497
        HTTP_RESPONSE_CLIENT_CLOSED_REQUEST = 499
        # Cloudflare
        HTTP_RESPONSE_UNKNOWN_ERROR = 520
        HTTP_RESPONSE_WEB_SERVER_IS_DOWN = 521
        HTTP_RESPONSE_CONNECTION_TIMED_OUT = 522
        HTTP_RESPONSE_ORIGIN_IS_UNREACHABLE = 523
        HTTP_RESPONSE_A_TIMEOUT_OCCURRED = 524
        HTTP_RESPONSE_SSL_HANDSHAKE_FAILED = 525
        HTTP_RESPONSE_INVALID_SSL_CERTIFICATE = 526
        HTTP_RESPONSE_RAILGUN_ERROR = 527

    # Constants
    EVENT = "event"
    RESULT = "result"
    TOKEN = "token"
    SERIAL = "serial"
    HARDWARE = "hardware"
    MODEL = "model"
    PRODUCT = "product"
    VERSION = "version"
    UUID = "uuid"
    RESOURCE = "resource"
    ID = "id"
    URL = "url"
    TITLE = "title"
    RESULT_JSON = "result_json"
    RESULT_SIZE = "result_size"
    CMD_JSON = "get_json"
    GET_FILE_SIZE = "get_file_size"
    GET_FILES = "get_files"
    PROGRESS = "progress"
    COMPLETE = "complete"
    PLAYLIST = "playlist"
    PLAYLISTS = "playlists"
    PLAYLIST_URLS = "playlist_urls"
    CONTENTS = "contents"
    TOP_PLAYLIST = "top_playlist"
    GET_TOP_PLAYLIST = "get_top_playlist"
    RESULT_TOP_PLAYLIST = "result_top_playlist"
    PROCESS_TOP_PLAYLIST = "process_top_playlist"
    PLAYLIST_PROCESS_COMPLETE = "playlist_process_complete"
    CONTENT_COMPLETE = "content_complete"
    ERROR = "error"
    EXCEPTION = "exception"
    ACTION = "action"
    PATH = "path"
    FILE = "file"
    INCREMENT = "increment"
    DOWNLOADED_SIZE = "downloaded"
    TOTAL = "total"
    TOTAL_SIZE = "total"
    DURATION = "duration"
    ERROR = "error"
    EXIT = "exit"

    def __init__(self, link, contentdirectory):
        self._link = link
        self._running = True
        self._contentDirectory = contentdirectory

        # Playlist and content temp variables
        self._playlists = []
        self._totalContentBytes = 0
        logging.info("Deliveries starting")


    def SendDownloadProgress(self, increment, total, title):
        progress = 0
        if total > 0:
            progress = math.floor((increment / float(total)) * 100)
            if progress > 100:
                progress = 100
        self._link.SendEvent(json.dumps({Delivery.EVENT : Delivery.PROGRESS,
                                         Delivery.PROGRESS : progress,
                                         Delivery.TITLE : title,
                                         Delivery.INCREMENT : increment,
                                         Delivery.TOTAL : total}))


    def SendDownloadComplete(self, title, duration):
        self._link.SendEvent(json.dumps({Delivery.EVENT : Delivery.PROGRESS,
                                         Delivery.PROGRESS : Delivery.COMPLETE,
                                         Delivery.TITLE : title,
                                         Delivery.INCREMENT : 100,
                                         Delivery.TOTAL : 100,
                                         Delivery.DURATION : duration}))


    def GetToken(self, url, serial, hardware, model, product, version):
        registration = json.dumps({"sn" : serial,
                                   "make" : hardware,
                                   "model" : model,
                                   "os_ver" : product,
                                   "app_ver" : version})
        response = requests.put(url, headers={'accept': 'application/json'}, data=registration)
        if (response.status_code == Delivery.HttpResponseStatusCodes.HTTP_RESPONSE_OK.value) or \
           (response.status_code == Delivery.HttpResponseStatusCodes.HTTP_RESPONSE_CREATED.value):
            msg = response.text
            response_json = json.loads(msg)
            self._link.SendEvent(json.dumps({Delivery.EVENT : Delivery.TOKEN,
                                             Delivery.TOKEN : response_json[Delivery.TOKEN],
                                             Delivery.RESOURCE : response_json[Delivery.RESOURCE],
                                             Delivery.ID : response_json[Delivery.ID]}))
        else:
            self._link.SendEvent(json.dumps({Delivery.EVENT : Delivery.TOKEN,
                                             Delivery.TOKEN : Delivery.ERROR,
                                             Delivery.RESOURCE : "Error getting resource",
                                             Delivery.ID : "Error getting id"}))
            

    def GetJSON(self, url):
        response = requests.get(url, headers={'accept': 'application/json'})
        if response.status_code != Delivery.HttpResponseStatusCodes.HTTP_RESPONSE_OK.value:
            logging.error("Error getting top playlist")
            return Delivery.ERROR
        return response.text


    def ProcessTopPlaylist(self, strTopPlaylist):
        # Clear all temp variables
        self._playlists.clear()
        self._totalContentBytes = 0

        # Process top playlist
        playlist_json = json.loads(strTopPlaylist)
        playlists = playlist_json[Delivery.PLAYLISTS]

        # Process all child playlists
        logging.debug("Processing all child playlists")
        for p in range(0, len(playlists)):
            self.ProcessPlaylist(playlists[p])

        # Cache playlist objects and send playlist processing complete
        self._link.SetObjectCache(self._playlists)
        self._link.SendEvent(json.dumps({Delivery.EVENT : Delivery.PLAYLIST_PROCESS_COMPLETE}))


    def ProcessPlaylist(self, strPlaylistUrl):
        logging.debug("Retrieving playlist : " + strPlaylistUrl)
        
        # Get playlist from fulgent
        response = requests.get(strPlaylistUrl,
                                headers={'accept': 'application/json'})
        if response.status_code != Delivery.HttpResponseStatusCodes.HTTP_RESPONSE_OK.value:
            errstr = ("Problem getting playlist : " + strPlaylistUrl +
                      " reason : " + str(response.status_code))
            logging.error(errstr)
            return

        # Create playlist object
        logging.debug("Processing playlist : " + response.text)
        playlistobj = Playlist(strPlaylistUrl, response.text)

        # Add to list
        self._playlists.append(playlistobj)
        logging.debug("Adding playlist to pending list : " + playlistobj.GetUUID())

        # Process playlist content
        contentlist = playlistobj.GetContentList()
        if len(contentlist) == 0:
            logging.debug("No content to download for playlist " + playlistobj.GetUUID())
            return
        directory = self._contentDirectory + playlistobj.GetUUID()
        for c in range(0, len(contentlist)):
            contenturl = contentlist[c].GetResource()
            contentuuid = contentlist[c].GetId()
            filename = contentlist[c].GetFileName()
            filepath = directory + "/" + filename
            logging.debug("Content url : " + contenturl)
            logging.debug("Content UUID : " + contentuuid)
            logging.debug("Content filename : " + filename)

            # Get content file
            self.GetFiles(directory, contentuuid, contenturl, filename)

            # Set content video duration
            duration = self.GetVideoDuration(filepath)
            playlistobj.SetContentDuration(contentuuid, duration)
            playlistobj.SetContentReady(contentuuid, True)
            logging.debug("Setting content " + contentuuid + " ready")


    def GetFiles(self, dirpath, uuids, urls, filenames):
        uuidlist = uuids.split(",")
        urllist = urls.split(",")
        filelist = filenames.split(",")

        # If directory doesn't exist then create
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
            
        # Get files
        for c in range(0, len(uuidlist)):
            url = urllist[c]
            uuid = uuidlist[c]
            filename = filelist[c]
            filepath = dirpath + "/" + filename
            totalbytes = int(0)
            downloadedbytes = int(0)

            # If local file exists, make sure it is same size otherwise re-download
            skipdownload = False
            if os.path.isfile(filepath):
                statinfo = os.stat(filepath)
                filesize = self.GetFileSize(url)
                if filesize > 0:
                    if filesize == statinfo.st_size:
                        logging.debug("Local content valid, skipping")
                        skipdownload = True
                    else:
                        logging.debug("Content size mismatch, re-downloading : " + filepath)
                        os.remove(filepath)  # mismatched sizes, re-download media
                        totalbytes += filesize
                else:
                    logging.debug("Assuming local content valid, skipping")
                    skipdownload = True
            else:   # local media file not exist
                filesize = self.GetFileSize(url)
                totalbytes += filesize

            # Local media is valid, skipping
            if skipdownload == True:
                logging.debug("Local content valid, skipping downloading : " + filepath)
                self.SendDownloadComplete(uuid, self.GetVideoDuration(filepath))
                continue;

            # Get file
            response = requests.get(url, stream=True)
            if (response.status_code != Delivery.HttpResponseStatusCodes.HTTP_RESPONSE_OK.value) and \
               (response.status_code != Delivery.HttpResponseStatusCodes.HTTP_RESPONSE_CREATED.value):
                logging.error("Attempted to get file failed, status : " + str(response.status_code))
                continue
            filesize = int(response.headers['Content-length'])
            handle = None
            try:
                # Download and write file
                handle = open(filepath, "wb")
                for chunk in response.iter_content(chunk_size=1048576):
                    if chunk:      # filter out keep-alive new chunks
                        handle.write(chunk)
                        downloadedbytes += 1048576
                        self.SendDownloadProgress(downloadedbytes, totalbytes, uuid)
                handle.close()
                self.SendDownloadComplete(uuid, self.GetVideoDuration(filepath))
            except Exception as e:
                logging.exception(traceback.format_exc())
                self._link.SendEvent(json.dumps({Delivery.EVENT : Delivery.ERROR,
                                                 Delivery.EXCEPTION : e}))
            finally:
                if handle != None:
                    handle.close()
                if response != None:
                    response.close()


    def GetVideoDuration(self, filepath):
        duration = 0
        videoprocess = pexpect.spawn('/usr/bin/omxplayer -i ' + filepath)
        pattern = re.compile(r'Duration: (\d{2}):(\d{2}):(\d{2}).(\d{2,})')
        res = re.search(pattern, videoprocess.read().decode('utf-8'))
        if res != None:
            if res.groups() and (len(res.groups()) == 4):
                hour = int(res.group(1)) * 60 * 60
                min = int(res.group(2)) * 60
                sec = int(res.group(3))
                msec = int(res.group(4))
                frac = float(msec) / 1000
                duration = int(hour + min + sec)
        videoprocess = None
        return duration


    def GetFileSize(self, url):
        response = None
        size = 0
        try:
            response = requests.get(url, stream=True)
            size = int(response.headers['Content-length'])
        except:
            logging.error("Delivery : Error getting file size")
            logging.exception(traceback.format_exc())
        finally:
            if response != None:
                response.close()
        return size


    def Run(self):
        try:
            self._running = True
            while self._running:
                msg = self._link.CheckCmdQ(blocking=True, wait=0.25)
                if msg != None:
                    logging.debug(msg)
                    cmd_json = json.loads(msg)
                    action = cmd_json[Delivery.ACTION]
    
                    # Handle actions
                    
                    if action == Delivery.TOKEN:
                        self.GetToken(cmd_json[Delivery.URL],
                                      cmd_json[Delivery.SERIAL],
                                      cmd_json[Delivery.HARDWARE],
                                      cmd_json[Delivery.MODEL],
                                      cmd_json[Delivery.PRODUCT],
                                      cmd_json[Delivery.VERSION])
                    elif action == Delivery.GET_TOP_PLAYLIST:
                        url = str(cmd_json[Delivery.URL])
                        result = self.GetJSON(url)
                        if result != Delivery.ERROR:
                            self._link.SendEvent(json.dumps({Delivery.EVENT : Delivery.RESULT_TOP_PLAYLIST,
                                                             Delivery.RESULT : result,
                                                             Delivery.URL : url}))
                        else:
                            self._link.SendEvent(json.dumps({Delivery.EVENT : Delivery.ERROR,
                                                             Delivery.EXCEPTION : "No results returned"}))
                    elif action == Delivery.PROCESS_TOP_PLAYLIST:
                        self.ProcessTopPlaylist(cmd_json[Delivery.TOP_PLAYLIST])
                    elif action == Delivery.GET_FILE_SIZE:
                        url = str(cmd_json[Delivery.URL])
                        filesize = self.GetFileSize(url)
                        self._link.SendEvent(json.dumps({Delivery.EVENT : Delivery.RESULT_SIZE,
                                                         Delivery.RESULT : filesize}))
                    elif action == Delivery.GET_FILES:
                        path = str(cmd_json[Delivery.PATH])
                        uuids = str(cmd_json[Delivery.UUID])
                        urls = str(cmd_json[Delivery.URL])
                        files = str(cmd_json[Delivery.FILE])
                        self.GetFiles(path, uuids, urls, files)
                    elif action == Delivery.EXIT:
                        self._running = False
        except Exception as e:
            logging.error(e)
            logging.exception(traceback.format_exc())
        finally:
            logging.info("Exiting Delivery")
