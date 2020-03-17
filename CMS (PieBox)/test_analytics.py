import re
import logging
import _thread
import threading
import json
import math
import datetime
import time
import hashlib
import json
from queue import Queue
from threading import Timer
from time import sleep
from datastore import DataStore
from link import Link
from sandtimer import SandTimer
from analytics import Analytics
from gpiocontroller import GPIOController

_analyticsThread = None
_analyticsLink = Link()
_cachedMSAnalyticEvent = None

def StartAnalyticsThread(interval, url):
    print("Starting analytics thread")
    analytics = Analytics(_analyticsLink, interval, url)
    analytics.Run()


def SendAnalyticsCmd(cmd):
    print(cmd)
    _analyticsLink.SendCmd(cmd)


def testdb():
    print("Starting db test")

    # Start db
    db = DataStore("analytics.sql")

    # Add analytics entries
    db.AddAnalyticsEntry("pb01", "pushbutton", "playlist1", "sequence1",
                         1234589, 1, 5000,
                         "www.url.com", 22222, 12000, 
                         "01/01/01 11:11:11 PM")
    db.AddAnalyticsEntry("pb02", "pushbutton", "playlist1", "sequence2",
                         1234589, 1, 5000,
                         "www.url.com", 22222, 12000, 
                         "01/01/01 11:11:11 PM")
    db.AddAnalyticsEntry("pb03", "pushbutton", "playlist1", "sequence3",
                         1234589, 1, 5000,
                         "www.url.com", 22222, 12000, 
                         "01/01/01 11:11:11 PM")
    db.AddAnalyticsEntry("pb04", "pushbutton", "playlist1", "sequence4",
                         1234589, 1, 5000,
                         "www.url.com", 22222, 12000, 
                         "01/01/01 11:11:11 PM")
    db.AddAnalyticsEntry("pb05", "pushbutton", "playlist1", "sequence5",
                         1234589, 1, 5000,
                         "www.url.com", 22222, 12000, 
                         "01/01/01 11:11:11 PM")
    print("")

    ## lastidx = 0
    ## results = db.GetAnalyticsEntries()
    ## if results != None:
    ##     for row in results:
    ##         print(row)
    ##         lastidx = row[0]
    ## db.SetAnalyticsLastProcessedIndex(lastidx)
    ## 
    ## db.ClearAnalyticsTable(lastidx-2)
    ## 
    ## results = db.GetAnalyticsEntries()
    ## if results != None:
    ##     for row in results:
    ##         print(row)
    ##         lastidx = row[0]
    ## else:
    ##     print("No results to show")
    ## db.SetAnalyticsLastProcessedIndex(lastidx)
    ## print("Last Index")
    ## print(lastidx)
    
    lastidx = 0
    results = db.GetAnalyticsEntries()
    if results != None:
        analyticslist = []
        for row in results:
            print(row)
            lastidx = row[0]
            arow = json.dumps({'input_id' : row[1], 
                               'type' : row[2], 
                               'playlist' : row[3], 
                               'sequence' : row[4], 
                               'timestamp' : str(row[5]), 
                               'timezone' : str(row[6]), 
                               'dwell' : str(row[7]),
                               'content' : row[8], 
                               'played' : str(row[9]),
                               'duration' : str(row[10])})
            analyticslist.append(json.dumps(arow))
        analytics_json = json.dumps({"analytics" : analyticslist})
        print(analytics_json)


def ProcessAnalytics(input, type, status):
    _epoch = datetime.datetime.utcfromtimestamp(0)
    _timeZoneOffset = time.timezone * 1000
    _currentMediaStartTimestamp = None
    _cachedMSAnalyticEvent = None
    _msActiveTimestamp = None

    # Get analytics and send
        
    now = datetime.datetime.utcnow()
    timestamp = int((now - _epoch).total_seconds() * 1000)
    played = 0
    if _currentMediaStartTimestamp != None:
        played = (datetime.datetime.utcnow() - _currentMediaStartTimestamp).total_seconds() * 1000
    print("Video played for " + str(played) + "ms")
    duration = 13
    ## Current sequence stuff
    _cachedMSAnalyticEvent = {Analytics.ACTION : Analytics.INPUT,
                              Analytics.INPUT : input,
                              Analytics.TYPE : type,
                              Analytics.PLAYLIST : "test_playlist1",
                              Analytics.SEQUENCE : "test_sequence1",
                              Analytics.TIMESTAMP : timestamp, 
                              Analytics.TIMEZONE : _timeZoneOffset,
                              Analytics.DWELL : 0,
                              Analytics.CONTENTURL : "test_content1",
                              Analytics.PLAYED : played,
                              Analytics.DURATION : duration,
                              Analytics.DATETIME : now.isoformat()}
    if type == GPIOController.PUSH_BUTTON:
        print("Sending pb analytics event")
        SendAnalyticsCmd(json.dumps(_cachedMSAnalyticEvent))
        _cachedMSAnalyticEvent = None
    elif type == GPIOController.MOTION_SENSOR:
        if status == GPIOController.ACTIVE:  # ms active
            _msActiveTimestamp = datetime.datetime.utcnow()
            print("Motion sensor ACTIVE")
        else:  # ms inactive
            if _msActiveTimestamp != None:
                print("Motion sensor DE-ACTIVE")
                if _cachedMSAnalyticEvent != None:
                    _cachedMSAnalyticEvent[Analytics.DWELL] = (datetime.datetime.utcnow() - _msActiveTimestamp).total_seconds() * 1000
                    SendAnalyticsCmd(json.dumps(_cachedMSAnalyticEvent))
                    print("Storing analytics data")
                else:
                    print("No cached MS analytic event")
            else:
                print("No active motion sensor timestamp")
            _msActiveTimestamp = None
            _cachedMSAnalyticEvent = None


def testanalytics():
    global _analyticsThread

    print("Starting analytics test")

    _deviceUrl = 'https://fulgent.sandd.studio/api/v1.0/device/502e22e6-0bf3-48cc-a4d6-4d5502bf642f/analytics'
    _analyticsTimer = SandTimer(100.0)
    _analyticsThread = threading.Thread(name='analyticsthread',
                                        target=StartAnalyticsThread,
                                        args=(_analyticsTimer.GetTimeout(),
                                              _deviceUrl,),)
    _analyticsThread.start()
    
    ProcessAnalytics("pb01", GPIOController.PUSH_BUTTON, GPIOController.ACTIVE)
    ProcessAnalytics("pb02", GPIOController.PUSH_BUTTON, GPIOController.ACTIVE)
    ProcessAnalytics("pb03", GPIOController.PUSH_BUTTON, GPIOController.ACTIVE)

    SendAnalyticsCmd(json.dumps({Analytics.ACTION : Analytics.PRINT}))

    gg = 0
    while True:
        sleep(1.0)
        gg =+ 1
        if gg > 20:
            break;
    
    
    if _analyticsThread != None:
        SendAnalyticsCmd('{"action":"exit"}')
        _analyticsThread.join()
        _analyticsThread = None
        print("Analytics thread closed")

    
def main():
    loglevel = logging.DEBUG
    logformat = '%(asctime)s [%(levelname)s] %(pathname)s::%(funcName)s(%(lineno)s) - %(message)s'
    loghandlers = [logging.FileHandler('test_analytics.log'), logging.StreamHandler()]
    logging.basicConfig(level = loglevel, format = logformat, handlers = loghandlers)
    
    ##testdb()
    testanalytics()

if __name__ == "__main__":
    main()
