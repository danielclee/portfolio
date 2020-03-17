import logging
import traceback
import requests
import re
import _thread
import threading
import math
import time
import json
import os
import datetime
from enum import Enum
from queue import Queue
from threading import Timer
from time import sleep
from datastore import DataStore
from link import Link
from time import sleep
from sandtimer import SandTimer

class Analytics:
    # Constants
    EVENT = "event"
    ACTION = "action"
    SET_INTERVAL = "set_interval"
    INPUT = "input"
    INPUT_ID = "input_id"
    TYPE = "type"
    PLAYLIST = "playlist"
    SEQUENCE = "sequence"
    TIMESTAMP = "timestamp"
    TIMEZONE = "timezone"
    DWELL = "dwell"
    CONTENT = "content"
    CONTENTURL = "contenturl"
    PLAYED = "played"
    DURATION = "duration"
    DWELL = "dwell"
    DATETIME = "datetime"
    PRINT = "print"
    EXIT = "exit"

    def __init__(self, link, interval, url):
        self._link = link
        self._running = True
        logging.debug("Setting analytics timer : " + str(interval))
        self._analyticsTimer = SandTimer(interval)
        logging.debug("Setting analytics URL : " + url)
        self.analyticsURL = url
        
        # Start db
        self._db = DataStore("analytics.sql")


    def Run(self):
        self._analyticsTimer.Start()
        self._running = True
        while self._running:

            # Check for messages
            
            msg = self._link.CheckCmdQ(blocking=True, wait=0.25)
            if msg != None:
                logging.debug(msg)
                cmd_json = json.loads(msg)
                action = cmd_json[Analytics.ACTION]
                if action == Analytics.SET_INTERVAL:
                    interval = float(cmd_json[Analytics.INTERVAL])
                    self._analyticsTimer.Set(interval)
                    self._analyticsTimer.Reset()
                elif action == Analytics.INPUT:
                    self._db.AddAnalyticsEntry(str(cmd_json[Analytics.INPUT]),
                                               str(cmd_json[Analytics.TYPE]),
                                               str(cmd_json[Analytics.PLAYLIST]),  # uuid
                                               str(cmd_json[Analytics.SEQUENCE]),  # uuid
                                               int(cmd_json[Analytics.TIMESTAMP]),  # secs
                                               int(cmd_json[Analytics.TIMEZONE]),  # offset in hours
                                               int(cmd_json[Analytics.DWELL]),  # ms
                                               str(cmd_json[Analytics.CONTENTURL]),
                                               int(cmd_json[Analytics.PLAYED]),  # ms
                                               int(cmd_json[Analytics.DURATION]),  # ms
                                               str(cmd_json[Analytics.DATETIME]))
                elif action == Analytics.PRINT:
                    self.PrintDB()
                elif action == Analytics.EXIT:
                    self._running = False

            # Check analytics timer

            if self._analyticsTimer.CheckExpired():
                logging.info("Sending analytics to fulgent")
                lastidx = int(0)
                results = self._db.GetAnalyticsEntries()
                if results != None:
                    analyticslist = []
                    for row in results:
                        lastidx = int(row[0])
                        arow = {Analytics.INPUT_ID : str(row[1]), 
                                Analytics.TYPE : str(row[2]), 
                                Analytics.PLAYLIST : str(row[3]), 
                                Analytics.SEQUENCE : str(row[4]), 
                                Analytics.TIMESTAMP : str(row[5]), 
                                Analytics.TIMEZONE : str(row[6]), 
                                Analytics.DWELL : str(row[7]),
                                Analytics.CONTENT : str(row[8]), 
                                Analytics.PLAYED : str(row[9]),
                                Analytics.DURATION : str(row[10]),
                                Analytics.DATETIME : str(row[11])}
                        analyticslist.append(arow)
                    analytics_json = json.dumps({"analytics" : analyticslist})

                    # Send to server
                    if lastidx > 0:
                        logging.debug("Sending analytics to " + self.analyticsURL)
                        response = requests.post(self.analyticsURL,
                                                 headers={'accept': 'application/json',
                                                          'content-type': 'application/json'},
                                                 data=analytics_json)
                        if (response.status_code == 204) or \
                           (response.status_code == 200) or \
                           (response.status_code == 201):
                            self._db.ClearAnalyticsTable(lastidx)
                            logging.debug("Cleared analytics table to " + str(lastidx))
                        else:
                            self._db.ClearAnalyticsLastProcessedIndex()
                            logging.debug("Set analytics last processed index to 0")
                # End nested-if
                self._analyticsTimer.Reset()
            # End if
        logging.info("Exiting Analytics")


    def PrintDB(self):
        logging.info("\n\n------------------------------------------------\nAnalytics entries : ")
        lastidx = 0
        results = self._db.GetAnalyticsEntries()
        if results != None:
            analyticslist = []
            for row in results:
                logging.info(row)
                lastidx = row[0]
                arow = {Analytics.INPUT_ID : str(row[1]), 
                        Analytics.TYPE : str(row[2]), 
                        Analytics.PLAYLIST : str(row[3]), 
                        Analytics.SEQUENCE : str(row[4]), 
                        Analytics.TIMESTAMP : str(row[5]), 
                        Analytics.TIMEZONE : str(row[6]), 
                        Analytics.DWELL : str(row[7]),
                        Analytics.CONTENT : str(row[8]), 
                        Analytics.PLAYED : str(row[9]),
                        Analytics.DURATION : str(row[10]),
                        Analytics.DATETIME : str(row[11])}
            # End for
            logging.info("\n\n------------------------------------------------\n\n")


    def ToString(self):
        return ""
