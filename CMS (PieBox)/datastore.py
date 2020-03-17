import logging
import sqlite3

class DataStore:
    def __init__(self, dbfile):
        # DB connection
        self.dbconnection = sqlite3.connect(dbfile)
        self.dbcursor = self.dbconnection.cursor()
        self.analyticsLastProcessedIndex = 0;

        # GENERIC TABLE NAMES
        self.DATABASE_VERSION = 1
        self.TABLE_ANALYTICS = "analytics"
        ## self.DATABASE_NAME = "vivid"
        ## self.TABLE_PLAYLIST = "playlist"
        ## self.TABLE_SEQUENCE = "sequence"
        ## self.TABLE_CONTENT = "content"
        ## self.TABLE_ENTRANCE_ACTIONS = "entrance_actions"
        ## self.TABLE_TRIGGERS = "triggers"
        ## self.TABLE_TRIGGER_ACTIONS = "trigger_actions"

        # GENERIC TABLE COLS
        self.COL_ID = "id"
        ## self.COL_FK_PLAYLIST = "fk_playlist_id"
        ## self.COL_FK_CONTENT = "fk_content_id"
        ## self.COL_FK_SEQUENCE = "fk_sequence_id"
        ## self.COL_FK_TRIGGER = "fk_trigger_id";

        # PLAYLIST TABLE COLS
        ## self.IDX_PLAYLIST_ID = 0
        ## self.COL_PLAYLIST_URL = "url"
        ## self.IDX_PLAYLIST_URL = 1
        ## self.SQL_PLAYLIST = (
        ##     "CREATE TABLE " + self.TABLE_PLAYLIST +
        ##             "( " +
        ##             "  " + self.COL_ID + "  INTEGER PRIMARY KEY AUTOINCREMENT, " +
        ##             "  " + self.COL_PLAYLIST_URL + " TEXT" +
        ##             ");")
        ## print(self.SQL_PLAYLIST)

        # SEQUENCE TABLE COLS
        ## self.IDX_SEQUENCE_ID = 0
        ## self.COL_SEQUENCE_DWELL_TIME = "dwell_time"  # int
        ## self.IDX_SEQUENCE_DWELL_TIME = 1
        ## self.COL_SEQUENCE_DEFAULT_SEQ = "default_seq"  # int
        ## self.IDX_SEQUENCE_DEFAULT_SEQ = 2
        ## self.COL_SEQUENCE_NEXT_SEQ = "next_seq"  # text
        ## self.IDX_SEQUENCE_NEXT_SEQ = 3
        ## self.IDX_SEQUENCE_FK_PLAYLIST = 4
        ## self.IDX_SEQUENCE_FK_CONTENT = 5
        ## self.SQL_SEQUENCE = (
        ##     "CREATE TABLE " + self.TABLE_SEQUENCE +
        ##             "( " +
        ##             "  " + self.COL_ID + " TEXT PRIMARY KEY," +
        ##             "  " + self.COL_SEQUENCE_DWELL_TIME + " INTEGER, " +
        ##             "  " + self.COL_SEQUENCE_DEFAULT_SEQ + " INTEGER, " +
        ##             "  " + self.COL_SEQUENCE_NEXT_SEQ + " TEXT, " +
        ##             "  " + self.COL_FK_PLAYLIST + " INTEGER, " +
        ##             "  " + self.COL_FK_CONTENT + " TEXT, " +
        ##             "  FOREIGN KEY (" + self.COL_FK_PLAYLIST + ") REFERENCES " + self.TABLE_PLAYLIST + "(" + self.COL_ID + ") ON DELETE CASCADE, " +
        ##             "  FOREIGN KEY (" + self.COL_FK_CONTENT + ") REFERENCES " + self.TABLE_CONTENT + "(" + self.COL_ID + ") ON DELETE CASCADE" +
        ##             ")")
        ## print(self.SQL_SEQUENCE)

        # CONTENT TABLE COLS
        ## self.IDX_CONTENT_ID = 0
        ## self.COL_CONTENT_URL = "url"   # text
        ## self.IDX_CONTENT_URL = 1
        ## self.COL_CONTENT_URI = "uri"   # text
        ## self.IDX_CONTENT_URI = 2

        # COL_FK_PLAYLIST
        ## self.IDX_CONTENT_FK_PLAYLIST = 3
        ## self.SQL_CONTENT = (
        ##     "CREATE TABLE " + self.TABLE_CONTENT +
        ##             "( " +
        ##             "  " + self.COL_ID + " TEXT PRIMARY KEY, " +
        ##             "  " + self.COL_CONTENT_URL + " TEXT, " +
        ##             "  " + self.COL_CONTENT_URI + " TEXT, " +
        ##             "  " + self.COL_FK_PLAYLIST + " INTEGER, " +
        ##             "  FOREIGN KEY (" + self.COL_FK_PLAYLIST + ") REFERENCES " + self.TABLE_PLAYLIST + "(" + self.COL_ID + ") ON DELETE CASCADE" +
        ##             ")")
        ## print(self.SQL_CONTENT)

        # ENTRANCE ACTION TABLE COLS
        ## self.IDX_EACTION_ID = 0
        ## self.COL_EACTION_ORDER = "sequence"   # int
        ## self.IDX_EACTION_ORDER = 1
        ## self.COL_EACTION_ACTION = "action"   # text
        ## self.IDX_EACTION_ACTION = 2
        ## self.COL_EACTION_TARGET = "target"   # text
        ## self.IDX_EACTION_TARGET = 3
        ## self.COL_EACTION_PARAMETER = "parameter"   # text
        ## self.IDX_EACTION_PARAMETER = 4
        ## self.IDX_EACTION_FK_SEQUENCE = 5
        ## self.SQL_ACTION = (
        ##     "CREATE TABLE " + self.TABLE_ENTRANCE_ACTIONS +
        ##             "( " +
        ##             "  " + self.COL_ID + " INTEGER PRIMARY KEY AUTOINCREMENT, " +
        ##             "  " + self.COL_EACTION_ORDER + " INTEGER, " +
        ##             "  " + self.COL_EACTION_ACTION + " TEXT, " +
        ##             "  " + self.COL_EACTION_TARGET + " TEXT, " +
        ##             "  " + self.COL_EACTION_PARAMETER + " TEXT, " +
        ##             "  " + self.COL_FK_SEQUENCE + " TEXT, " +
        ##             "  FOREIGN KEY (" + self.COL_FK_SEQUENCE + ") REFERENCES " + self.TABLE_SEQUENCE + "(" + self.COL_ID + ") ON DELETE CASCADE" +
        ##             ")")
        ## print(self.SQL_ACTION)

        # TRIGGERS TABLE COLS
        ## self.IDX_TRIGGER_ID = 0
        ## self.COL_TRIGGER_INPUT = "input"   # text
        ## self.IDX_TRIGGER_INPUT = 1
        ## self.IDX_TRIGGER_FK_SEQUENCE = 2
        ## self.SQL_TRIGGERS = (
        ##     "CREATE TABLE " + self.TABLE_TRIGGERS +
        ##             "( " +
        ##             "  " + self.COL_ID + " INTEGER PRIMARY KEY AUTOINCREMENT, " +
        ##             "  " + self.COL_TRIGGER_INPUT + " TEXT, " +
        ##             "  " + self.COL_FK_SEQUENCE + " TEXT, " +
        ##             "  FOREIGN KEY (" + self.COL_FK_SEQUENCE + ") REFERENCES " + self.TABLE_SEQUENCE + "(" + self.COL_ID + ") ON DELETE CASCADE" +
        ##             ")")
        ## print(self.SQL_TRIGGERS)

        # TRIGGER ACTIONS TABLE COLS
        ## self.IDX_TRIGGER_ACTIONS_ID = 0
        ## self.COL_TRIGGER_ACTIONS_ORDER = "sequence"# int
        ## self.IDX_TRIGGER_ACTIONS_ORDER = 1
        ## self.COL_TRIGGER_ACTIONS_ACTION = "action"# text
        ## self.IDX_TRIGGER_ACTIONS_ACTION = 2
        ## self.COL_TRIGGER_ACTIONS_TARGET = "target"# text
        ## self.IDX_TRIGGER_ACTIONS_TARGET = 3
        ## self.COL_TRIGGER_ACTIONS_PARAMETER = "parameter"# text
        ## self.IDX_TRIGGER_ACTIONS_PARAMETER = 4
        ## self.IDX_TRIGGER_ACTIONS_FK_TRIGGER = 5
        ## self.SQL_TRIGGER_ACTIONS = (
        ##     "CREATE TABLE " + self.TABLE_TRIGGER_ACTIONS +
        ##             "( " +
        ##             "  " + self.COL_ID + " INTEGER PRIMARY KEY AUTOINCREMENT, " +
        ##             "  " + self.COL_TRIGGER_ACTIONS_ORDER + " INTEGER, " +
        ##             "  " + self.COL_TRIGGER_ACTIONS_ACTION + " TEXT, " +
        ##             "  " + self.COL_TRIGGER_ACTIONS_TARGET + " TEXT, " +
        ##             "  " + self.COL_TRIGGER_ACTIONS_PARAMETER + " TEXT, " +
        ##             "  " + self.COL_FK_TRIGGER + " INTEGER, " +
        ##             "  FOREIGN KEY(" + self.COL_FK_TRIGGER + ") REFERENCES " + self.TABLE_TRIGGERS + "(" + self.COL_ID + ") ON DELETE CASCADE" +
        ##             ")")
        ## print(self.SQL_TRIGGER_ACTIONS)

        # ANALYTICS TABLE COLS
        self.IDX_ANALYTICS_ID = 0
        self.COL_ANALYTICS_INPUT = "input_id" # text
        self.COL_ANALYTICS_TYPE = "type" # text
        self.COL_ANALYTICS_PLAYLIST = "playlist" # text
        self.COL_ANALYTICS_SEQUENCE = "sequence" # text
        self.COL_ANALYTICS_TIMESTAMP = "timestamp" # int
        self.COL_ANALYTICS_TIMEZONE_OFFSET = "timezone" # int 
        self.COL_ANALYTICS_DWELL = "dwell" # int
        self.COL_ANALYTICS_CONTENTURL = "content" # text
        self.COL_ANALYTICS_PLAYED = "played" # int
        self.COL_ANALYTICS_DURATION = "duration" # int
        self.COL_ANALYTICS_DATETIME = "datetime" # text
        self.analyticsLastProcessedIndex = 0
        self.SQL_ANALYTICS = (
            "CREATE TABLE " + self.TABLE_ANALYTICS +
                    "( " +
                    "  " + self.COL_ID + " INTEGER PRIMARY KEY AUTOINCREMENT, " +
                    "  " + self.COL_ANALYTICS_INPUT + " TEXT, " +
                    "  " + self.COL_ANALYTICS_TYPE + " TEXT, " +
                    "  " + self.COL_ANALYTICS_PLAYLIST + " TEXT, " +
                    "  " + self.COL_ANALYTICS_SEQUENCE + " TEXT, " +
                    "  " + self.COL_ANALYTICS_TIMESTAMP + " INTEGER, " +
                    "  " + self.COL_ANALYTICS_TIMEZONE_OFFSET + " INTEGER, " +
                    "  " + self.COL_ANALYTICS_DWELL + " INTEGER, " +
                    "  " + self.COL_ANALYTICS_CONTENTURL + " TEXT," +
                    "  " + self.COL_ANALYTICS_PLAYED + " INTEGER, " +
                    "  " + self.COL_ANALYTICS_DURATION + " INTEGER, " +
                    "  " + self.COL_ANALYTICS_DATETIME + " TEXT " +
                    ")")

        # Create tables
        ### self.Wipe()  # debug
        self.ExecSQL(self.SQL_ANALYTICS)
        ## self.ExecSQL(self.SQL_PLAYLIST)
        ## self.ExecSQL(self.SQL_SEQUENCE)
        ## self.ExecSQL(self.SQL_CONTENT)
        ## self.ExecSQL(self.SQL_ACTION)
        ## self.ExecSQL(self.SQL_TRIGGERS)
        ## self.ExecSQL(self.SQL_TRIGGER_ACTIONS)

        # Initialize variables
        self.selectresult = None

    def __del__(self):
        if self.dbcursor:
            self.dbcursor.close()
        if self.dbconnection:
            self.dbconnection.close()


    def Wipe(self):
        try:
            self.dbcursor.execute("DROP TABLE IF EXISTS {t}".format(t=self.TABLE_ANALYTICS))
        except sqlite3.Error as e:
            logging.error("Problem wiping " + e.args[0])


    def ExecSQL(self, sqlcmd):
        logging.debug(sqlcmd)
        try:
            self.dbcursor.execute(sqlcmd)
            if sqlcmd.upper().find("SELECT ") != 0:
                self.dbconnection.commit()
            return True
        except sqlite3.Error as e:
            logging.error("Error executing sql " + e.args[0])
            return False
        # End try-except


    def SelectExecSQL(self, sqlcmd):
        logging.debug(sqlcmd)
        rowsfound = 0
        self.selectresult = None
        try:
            self.dbcursor.execute(sqlcmd)
            self.selectresult = self.dbcursor.fetchall()
            if self.selectresult != None:
                rowsfound = len(self.selectresult)
        except sqlite3.Error as e:
            logging.error("Error executing sql select " + e.args[0])
        return rowsfound


    def ClearAnalyticsLastProcessedIndex(self):
        logging.debug("In ClearAnalyticsLastProcessedIndex")
        self.analyticsLastProcessedIndex = 0
        logging.debug(self.analyticsLastProcessedIndex)


    def SetAnalyticsLastProcessedIndex(self, index):
        logging.debug("In SetAnalyticsLastProcessedIndex")
        self.analyticsLastProcessedIndex = index
        logging.debug(self.analyticsLastProcessedIndex)


    def ClearAnalyticsTable(self, index, clearall=False):
        sqlcmd = ("DELETE FROM {t}".format(t=self.TABLE_ANALYTICS))
        if clearall is False:
            sqlcmd += (" WHERE {i}<={r}".format(i=self.COL_ID, r=index))
        if not self.ExecSQL(sqlcmd):
            logging.debug("SQL error ClearAnalyticsTable")


    def AddAnalyticsEntry(self, input, type, playlist, sequence, timestamp, 
                          timezone, dwell, contenturl, played, duration,
                          datetime):
        sqlcmd = ("INSERT INTO {t} ({c1},{c2},{c3},{c4},{c5},{c6},{c7},{c8},{c9},{c10},{c11}) "
                  "VALUES ('{v1}','{v2}','{v3}','{v4}',{v5},{v6},{v7},'{v8}',{v9},{v10},'{v11}');".\
                  format(t=self.TABLE_ANALYTICS,
                         c1=self.COL_ANALYTICS_INPUT,
                         c2=self.COL_ANALYTICS_TYPE,
                         c3=self.COL_ANALYTICS_PLAYLIST,
                         c4=self.COL_ANALYTICS_SEQUENCE,
                         c5=self.COL_ANALYTICS_TIMESTAMP,
                         c6=self.COL_ANALYTICS_TIMEZONE_OFFSET,
                         c7=self.COL_ANALYTICS_DWELL,
                         c8=self.COL_ANALYTICS_CONTENTURL,
                         c9=self.COL_ANALYTICS_PLAYED,
                         c10=self.COL_ANALYTICS_DURATION,
                         c11=self.COL_ANALYTICS_DATETIME,
                         v1=input,
                         v2=type,
                         v3=playlist,
                         v4=sequence,
                         v5=timestamp,
                         v6=timezone,
                         v7=dwell,
                         v8=contenturl,
                         v9=played,
                         v10=duration,
                         v11=datetime))
        if not self.ExecSQL(sqlcmd):
            logging.error("SQL INSERT ERROR")


    def GetAnalyticsEntries(self):
        sqlcmd = ("SELECT * FROM {t} ORDER BY {i} ASC".\
                  format(t=self.TABLE_ANALYTICS, 
                         i=self.COL_ID))
        rowkount = self.SelectExecSQL(sqlcmd)
        if rowkount == 0:
            logging.debug("No analytics rows found")
            return None
        ## self.analyticsLastProcessedIndex = self.selectresult[-1][0]
        ## print("Last analytics index")
        ## print(self.analyticsLastProcessedIndex)
        return self.selectresult



##///////////////////////////////////////////////////////////////////////////////
##///////////////////////////////////////////////////////////////////////////////
##    
##    def PlayListExists(self, playlistobj):
##        selectquery = ("SELECT  * FROM " + self.TABLE_PLAYLIST + " WHERE " + self.COL_PLAYLIST_URL + "=\"" + playlistobj.GetName() + "\"")
##        if self.SelectExecSQL(selectquery) > 0:
##            return True
##        return False
##
##
##    def AddPlaylist(self, playlistobj):
##        if PlayListExists(playlistobj.GetName()):
##            return False
##        self.InsertPlaylist(playlistobj)
##        self.InsertContent(playlistobj)
##        self.InsertSequences(playlistobj)
##        return True
##
##
##    def InsertPlaylist(self, playlistobj):
##        sqlquery = ("INSERT INTO {t} ({c1}) VALUES ({v1});".\
##                    format(t=self.TABLE_PLAYLIST,
##                           c1=self.COL_PLAYLIST_URL,
##                           v1=playlistobj.GetName()))
##        self.ExecSQL(sqlquery)
##        
##
##    def DeletePlaylist(self, playlistobj):
##        sqlquery = ("DELETE FROM {t} WHERE {c1}={v1};".\
##                    format(t=self.TABLE_PLAYLIST, c1=self.COL_PLAYLIST_URL,
##                           v1=playlistobj.GetName()))
##        self.ExecSQL(sqlquery)
##
##
##    def GetPlaylists(self):
##        currentPlaylists = {}
##        selectquery = "SELECT  * FROM " + self.TABLE_PLAYLIST
##        if self.SelectExecSQL(selectquery) > 0:
##            for row in self.selectresult:
##                url = self.selectresult[self.IDX_PLAYLIST_URL]
##                id = self.selectresult[self.IDX_PLAYLIST_ID]
##                currentPlaylists[url] = id
##        return currentPlaylists;
##
##        
##    def ShowPlaylists(self):
##        currentPlaylists = self.GetPlaylists()
##        print(currentPlaylists)
##
##
##    def CleanPlaylists(self, newPlaylist):
##        currentPlaylists = self.GetPlaylists()
##        for key in currentPlaylists.keys():
##            pname = key
##            pid = currentPlaylists[key]
##            if newPlaylist.get(pname) == None:
##                self.DeletePlaylist(pname)
##
##
##    def GetPlaylistId(self, playlistobj):
##        selectquery = ("SELECT " + self.COL_ID + " FROM " + self.TABLE_PLAYLIST + " WHERE " + self.COL_PLAYLIST_URL + " = \"" + playlistobj.GetUrl() + "\"")
##        if self.SelectExecSQL(selectquery) > 0:
##            return int(self.selectresult[0])
##        return -1
##
##
##    def GetContentObjectWithURI(self):
##        vec = []
##        selectquery = ("SELECT * FROM " + self.TABLE_CONTENT + " WHERE " + self.COL_CONTENT_URI + " IS NOT NULL OR TRIM(" + self.COL_CONTENT_URI + ") <> \"\"")
##        if self.SelectExecSQL(selectquery) > 0:
##            for row in self.selectresult:
##                uri = self.selectresult[self.IDX_CONTENT_URI]
##                url = self.selectresult[self.IDX_CONTENT_URL]
##                id = self.selectresult[self.IDX_CONTENT_ID]
##                c = Content()
##                c.SetId(id)
##                c.SetResource(url)
##                c.SetUri(uri)
##                vec.append(c)
##        return vec
##
##
##    def GetContentObjectMissingUri(self):
##        vec = []
##        selectquery = ("SELECT * FROM " + self.TABLE_CONTENT + " WHERE " + self.COL_CONTENT_URI + " IS NULL OR TRIM(" + COL_CONTENT_URI + ") = \"\"")
##        if self.SelectExecSQL(selectquery) > 0:
##            for row in self.selectresult:
##                url = self.selectresult[self.IDX_CONTENT_URL]
##                id = self.selectresult[self.IDX_CONTENT_ID]
##                c = Content()
##                c.SetId(id)
##                c.SetResource(url)
##                c.SetUri("")
##                vec.append(c)
##        return vec
##
##
##    def UpdateURIs(self):
##        goodUris = self.GetContentObjectWithURI()
##        goodLUT = {}
##        for uri in goodUris:
##            goodLUT[uri.GetResource()] = uri
##        noUris = GetContentObjectMissingUri()
##        for uri in noUris:
##            c = uri.Next()
##            k = goodLUT.Get(c.GetResource())
##            if k != None:
##                uri = k.GetUri()
##                this.SetContentURI(c.GetResource(), uri)
##
##
##    def SetContentURIbyID(self, contentid, uri):
##        sqlquery = ("UPDATE {t} SET {c}={v} WHERE {q}={a};".\
##                    format(t=self.TABLE_CONTENT, c=self.COL_CONTENT_URI,
##                           v=uri, q=self.COL_ID, a=contentid))
##        self.ExecSQL(sqlquery)
##
##
##    def InsertContent(self, playlistobj):
##        plId = self.GetPlaylistId(playlistobj)
##        it = playlistobj.GetContentVector()
##        for c in it:
##            sqlquery = ("INSERT INTO {t} ({c1}, {c2}, {c3}) " +
##                        "VALUES ({v1}, {v2}, {v3});".\
##                        format(t=self.TABLE_CONTENT,
##                               c1=self.COL_ID, 
##                               c2=self.COL_CONTENT_URL, 
##                               c3=self.COL_FK_PLAYLIST, 
##                               v1=c.GetId(),
##                               v2=c.GetResource(),
##                               v3=plId))
##            self.ExecSQL(sqlquery)
##            
##
##    def SetContentURI(self, contentid, uri):
##        sqlquery = ("UPDATE {t} SET {c}={v} WHERE {q}={a};".\
##                    format(t=self.TABLE_CONTENT, c=self.COL_CONTENT_URI,
##                           v=uri, q=self.COL_ID, a=contentid))
##        self.ExecSQL(sqlquery)
##
##        
##    def GetContentUri(self, contentid):
##        selectPLidQuery = "SELECT " + self.COL_CONTENT_URI + " FROM " + self.TABLE_CONTENT + " WHERE " + self.COL_ID + " = \"" + contentid + "\""
##        self.SelectExecSQL(selectPLidQuery)
##        if self.selectresult != None:
##            return self.selectresult[0]
##        return ""
##
##
##    def GetContentUrl(self, contentid):
##        selectPLidQuery = "SELECT " + self.COL_CONTENT_URL + " FROM " + self.TABLE_CONTENT + " WHERE " + self.COL_ID + " = \"" + contentid + "\""
##        self.SelectExecSQL(selectPLidQuery)
##        if self.selectresult != None:
##            return self.selectresult[0]
##        return ""
##
##
##    def getContentMissingURI(self):
##        vec = []
##        selectquery = "SELECT * FROM " + self.TABLE_CONTENT + " WHERE " + self.COL_CONTENT_URI + " IS NULL OR TRIM(" + self.COL_CONTENT_URI + ") = \"\""
##        self.SelectExecSQL(selectquery)
##        if self.selectresult != None:
##            uri = self.selectresult[self.IDX_CONTENT_URI]
##            vec.append(self.selectresult[self.IDX_CONTENT_URL])
##        return vec
##
##
##    def AddContentToPlaylist(self, playlistobj, plId):
##        selectquery = "SELECT * FROM " + self.TABLE_CONTENT + "  WHERE " + self.COL_FK_PLAYLIST + " =" + plId
##        self.SelectExecSQL(selectquery)
##        if self.selectresult != None:
##            pl.addContent(self.selectresult(self.IDX_CONTENT_URL),
##                          self.selectresult(self.IDX_CONTENT_ID),
##                          self.selectresult(self.IDX_CONTENT_URI))
##
##
##    def InsertSequences(self, playlistobj):
##        plId = self.GetPlaylistId(playlistobj)
##        sequences = playlistobj.GetSequences()
##        for sequence in sequences:
##            # Insert sequence
##            sqlquery = ("INSERT INTO {t} ({c1}, {c2}, {c3}, {c4}, {c5}, {c6}) " +
##                        "VALUES ({v1}, {v2}, {v3}, {v4}, {v5}, {v6});".\
##                        format(t=self.TABLE_SEQUENCE,
##                               c1=self.COL_ID, 
##                               c2=self.COL_SEQUENCE_DWELL_TIME, 
##                               c3=self.COL_SEQUENCE_DEFAULT_SEQ, 
##                               c4=self.COL_SEQUENCE_NEXT_SEQ, 
##                               c5=self.COL_FK_PLAYLIST, 
##                               c6=self.COL_FK_CONTENT, 
##                               v1=sequence.GetId(),
##                               v2=sequence.GetDwellTime(),
##                               v3=sequence.IsDefaultSequence(),
##                               v4=sequence.GetNextSequence(),
##                               v5=plId,
##                               v6=sequence.GetContentId()))
##            self.ExecSQL(sqlquery)
##
##            # Insert action
##            actions = sequence.GetEntranceActions()
##            for action in actions:
##            sqlquery = ("INSERT INTO {t} ({c1}, {c2}, {c3}, {c4}, {c5}) " +
##                        "VALUES ({v1}, {v2}, {v3}, {v4}, {v5});".\
##                        format(t=self.TABLE_ENTRANCE_ACTIONS,
##                               c1=self.COL_EACTION_ORDER,
##                               c2=self.COL_EACTION_ACTION,
##                               c3=self.COL_EACTION_TARGET,
##                               c4=self.COL_EACTION_PARAMETER,
##                               c5=self.COL_FK_SEQUENCE,
##                               v1='0',
##                               v2=action.GetAction(),
##                               v3=action.GetTarget(),
##                               v4=action.GetParameter(),
##                               v5=sequence.GetId()))
##            if self.ExecSQL(sqlquery):
##                # Insert trigger
##                lastidx = self.dbcursor.lastrowid
##                triggers = sequence.GetTriggers()
##                for trigger in triggers:
##                    sqlquery = ("INSERT INTO {t} ({c1}, {c2}, {c3}, {c4}, {c5}) " +
##                                "VALUES ({v1}, {v2}, {v3}, {v4}, {v5});".\
##                                format(t=self.TABLE_TRIGGER_ACTIONS,
##                                       c1=self.COL_TRIGGER_ACTIONS_ORDER,
##                                       c2=self.COL_TRIGGER_ACTIONS_ACTION,
##                                       c3=self.COL_TRIGGER_ACTIONS_TARGET,
##                                       c4=self.COL_TRIGGER_ACTIONS_PARAMETER,
##                                       c5=self.COL_FK_TRIGGER,
##                                       v1='0',
##                                       v2=action.GetAction(),
##                                       v3=action.GetTarget(),
##                                       v4=action.GetParameter(),
##                                       v5=lastidx))
##                    self.ExecSQL(sqlquery)
##
##
##    def AddEntranceActions(self, sequenceId):
##        entranceActionsQuery = ("SELECT * FROM " + self.TABLE_ENTRANCE_ACTIONS +
##                "  WHERE " + self.COL_FK_SEQUENCE + " =\"" + sequenceId + "\"" +
##                " ORDER BY " + self.COL_EACTION_ORDER + " ASC")
##        entranceActionArray = []
##        if self.SelectExecSQL(entranceActionsQuery) > 0:
##            if self.selectresult != None:
##                for row in self.selectresult:
##                    jsondata = {}  # 3434
##                    jsondata[Playlist.ACTION] = self.selectresult[self.IDX_EACTION_ACTION]
##                    jsondata[Playlist.TARGET] = self.selectresult[self.IDX_EACTION_TARGET]
##                    jsondata[Playlist.PARAMETER] = self.selectresult[self.IDX_EACTION_PARAMETER]
##                    entranceActionArray.append(json.loads(jsondata))
##        return entranceActionArray
##
##
##    def AddTriggerActions(self, triggerId):
##        triggersQuery = ("SELECT * FROM " + self.TABLE_TRIGGER_ACTIONS +
##                         " WHERE " + self.COL_FK_TRIGGER + " = " + triggerId +
##                         " ORDER BY " + self.COL_TRIGGER_ACTIONS_ORDER + " ASC")
##        triggerActionsArray = []
##        if self.SelectExecSQL(triggersQuery) > 0:
##            if self.selectresult != None:
##                for row in self.selectresult:
##                    jsondata = {}  # 3434
##                    jsondata[Playlist.ACTION] = self.selectresult[self.IDX_TRIGGER_ACTIONS_ACTION]
##                    jsondata[Playlist.TARGET] = self.selectresult[self.IDX_TRIGGER_ACTIONS_TARGET]
##                    jsondata[Playlist.PARAMETER] = self.selectresult[self.IDX_TRIGGER_ACTIONS_PARAMETER]
##                    triggerActionsArray.append(json.loads(jsondata))
##        return triggerActionsArray
##
##
##    def AddTriggers(self, sequenceId):
##        triggersQuery = ("SELECT * FROM " + self.TABLE_TRIGGERS +
##                        "  WHERE " + self.COL_FK_SEQUENCE + " =\"" + sequenceId + "\"")
##        triggers = {}  # 3434
##        if self.SelectExecSQL(triggersQuery) > 0:
##            if self.selectresult != None: 
##                triggers[IDX_TRIGGER_INPUT] = self.selectresult[self.IDX_TRIGGER_ID]
##        return json.loads(triggers)
##               
##
##    def AddSequencesToPlaylist(self, playlistobj, plId):
##        seqQuery = ("SELECT * FROM " + self.TABLE_SEQUENCE +
##                    "  WHERE " + self.COL_FK_PLAYLIST + " =" + plId)
##        if self.SelectExecSQL(seqQuery) > 0:
##            if self.selectresult != None: 
##                seqArray = []
##                for row in self.selectresult:
##                    ns = self.selectresult[self.IDX_SEQUENCE_NEXT_SEQ]
##                    ds = self.selectresult[self.IDX_SEQUENCE_DEFAULT_SEQ]
##                    sequence = {}
##                    sequence[Playlist.ID] = self.selectresult[self.IDX_SEQUENCE_ID]
##                    sequence[Playlist.DWELL_TIME] = self.selectresult[self.IDX_SEQUENCE_DWELL_TIME]
##                    if ds == 1:
##                        sequence[Playlist.DEFAULT_SEQUENCE] = "true"
##                    if ns.lower() != Playlist.UNDEFINED:
##                        sequence[Playlist.NEXT_SEQUENCE] = self.selectresult[self.IDX_SEQUENCE_NEXT_SEQ]
##                        sequence[Playlist.CONTENT_ID] = self.selectresult[self.IDX_SEQUENCE_FK_CONTENT]
##                    # Add entrance actions
##                    sequence[Playlist.ENTRANCE_ACTIONS] = self.AddTriggers(self.AddEntranceActions[self.IDX_SEQUENCE_ID])
##                    # Add triggers
##                    sequence[Playlist.TRIGGERS] = self.AddTriggers(self.selectresult[self.IDX_SEQUENCE_ID])
##                    seqArray.append(json.loads(sequence))
##                playlistobj.addSequences(seqArray)
##        retrun playlistobj
##
##
##    def GetPlaylistObject(self, plName):
##        pl = Playlist()
##        pl.SetName(plName)
##        plId = self.GetPlaylistId(plName)
##        self.AddContentToPlaylist(pl, plId);
##        self.AddSequencesToPlaylist(pl, plId);
##        return pl
##
##
##///////////////////////////////////////////////////////////////////////////////
##///////////////////////////////////////////////////////////////////////////////
##
##
##    /**
##     *
##     * @param analyticdata
##     */
##    public void addAnalyticsEntry(AnalyticsData analyticdata)
##    {
##        SQLiteDatabase db = this.getWritableDatabase();
##        ContentValues values = new ContentValues();
##        values.put(COL_ANALYTICS_INPUT, analyticdata.id);
##        values.put(COL_ANALYTICS_TYPE, analyticdata.typestr);
##        values.put(COL_ANALYTICS_PLAYLIST, analyticdata.playlist);
##        values.put(COL_ANALYTICS_SEQUENCE, analyticdata.sequence);
##        values.put(COL_ANALYTICS_TIMESTAMP, analyticdata.timestamp);
##        ////values.put(COL_ANALYTICS_TIMEZONE_OFFSET, analyticdata.timezone);
##        values.put(COL_ANALYTICS_DWELL, analyticdata.dwell);
##        values.put(COL_ANALYTICS_CONTENTURL, analyticdata.contenturl);
##        values.put(COL_ANALYTICS_PLAYED, analyticdata.played);
##        values.put(COL_ANALYTICS_DURATION, analyticdata.duration);
##        values.put(COL_ANALYTICS_DATETIME, analyticdata.datetime);
##
##        long rowidx = db.insert(TABLE_ANALYTICS, null, values);
##        db.close();
##    }
##
##    public void insertAnalyticsData(String id, String typestr, String playlist,
##                                    String sequence, long timestamp, int dwell,
##                                    String contenturl, int played, int duration,
##                                    String datetime){
##        SQLiteDatabase db = this.getWritableDatabase();
##        ContentValues values = new ContentValues();
##        values.put(COL_ANALYTICS_INPUT, id);
##        values.put(COL_ANALYTICS_TYPE, typestr);
##        values.put(COL_ANALYTICS_PLAYLIST, playlist);
##        values.put(COL_ANALYTICS_SEQUENCE, sequence);
##        values.put(COL_ANALYTICS_TIMESTAMP, timestamp);
##        ////values.put(COL_ANALYTICS_TIMEZONE_OFFSET, analyticdata.timezone);
##        values.put(COL_ANALYTICS_DWELL, dwell);
##        values.put(COL_ANALYTICS_CONTENTURL, contenturl);
##        values.put(COL_ANALYTICS_PLAYED, played);
##        values.put(COL_ANALYTICS_DURATION, duration);
##        values.put(COL_ANALYTICS_DATETIME, datetime);
##
##        long rowidx = db.insert(TABLE_ANALYTICS, null, values);
##        db.close();
##    }
##    /**
##     * @param
##     */
##    public JSONObject GetAnalyticsEntries()
##    {
##        SQLiteDatabase db = this.getWritableDatabase();
##        String analyticsQuery = "SELECT * FROM " + TABLE_ANALYTICS + " ORDER BY " + COL_ID + " ASC";
##        Cursor analyticsCursor = db.rawQuery(analyticsQuery, null);
##
##        // Go through analytics rows
##
##        JSONArray analyticsArray = new JSONArray();
##        analyticsLastProcessedIndex = 0;
##        try
##        {
##            if (analyticsCursor.moveToFirst())
##            {
##                do
##                {
##                    JSONObject input = new JSONObject();
##                    input.put(COL_ANALYTICS_INPUT,      analyticsCursor.getString(IDX_ANALYTICS_INPUT));
##                    input.put(COL_ANALYTICS_TYPE,       analyticsCursor.getString(IDX_ANALYTICS_TYPE));
##                    input.put(COL_ANALYTICS_PLAYLIST,   analyticsCursor.getString(IDX_ANALYTICS_PLAYLIST));
##                    input.put(COL_ANALYTICS_SEQUENCE,   analyticsCursor.getString(IDX_ANALYTICS_SEQUENCE));
##                    input.put(COL_ANALYTICS_TIMESTAMP,  analyticsCursor.getString(IDX_ANALYTICS_TIMESTAMP));
##                    input.put(COL_ANALYTICS_TIMEZONE,   analyticsCursor.getString(IDX_ANALYTICS_TIMEZONE));
##                    input.put(COL_ANALYTICS_DWELL,      analyticsCursor.getString(IDX_ANALYTICS_DWELL));
##                    input.put(COL_ANALYTICS_CONTENTURL, analyticsCursor.getString(IDX_ANALYTICS_CONTENTURL));
##                    input.put(COL_ANALYTICS_PLAYED,     analyticsCursor.getString(IDX_ANALYTICS_PLAYED));
##                    input.put(COL_ANALYTICS_DURATION,   analyticsCursor.getString(IDX_ANALYTICS_DURATION));
##                    input.put(COL_ANALYTICS_DATETIME,  analyticsCursor.getString(IDX_ANALYTICS_DATETIME));
##                    analyticsArray.put(input);
##                    analyticsLastProcessedIndex = analyticsCursor.getInt(IDX_ANALYTICS_ID);
##                }
##                while (analyticsCursor.moveToNext());
##            }
##        }
##        catch (JSONException e)
##        {
##            e.printStackTrace();
##        }
##        db.close();
##
##        // Create analytics json object
##
##        JSONObject analyticsobj = null;
##        if (analyticsArray.length() > 0)
##        {
##            try
##            {
##                analyticsobj = new JSONObject();
##                analyticsobj.put("analytics", analyticsArray);
##            }
##            catch (JSONException e)
##            {
##                e.printStackTrace();
##            }
##        }
##        
##        return(analyticsobj);
##    }
##
##    /**
##     * @param all
##     */
##    public void clearAnalyticsTable(boolean all)
##    {
##        SQLiteDatabase db = this.getWritableDatabase();
##
##        if (all)
##        {
##            Log.d(LOG_TAG, "Deleting " + TABLE_ANALYTICS);
##            db.delete(TABLE_ANALYTICS, null, null);
##            analyticsLastProcessedIndex = 0;
##            return;
##        }
##
##        if (analyticsLastProcessedIndex > 0)
##        {
##            Log.d(LOG_TAG, "Deleting " + TABLE_ANALYTICS + " up to index " + analyticsLastProcessedIndex);
##            db.delete(TABLE_ANALYTICS, COL_ID + "<=?", new String[]{Long.toString(analyticsLastProcessedIndex)});
##            analyticsLastProcessedIndex = 0;
##        }
##    }
##
##    /**
##     * @param 
##     */
##    public void clearAnalyticsLastProcessedIndex()
##    {
##        analyticsLastProcessedIndex = 0;
##    }
##    
##///////////////////////////////////////////////////////////////////////////////
##///////////////////////////////////////////////////////////////////////////////
