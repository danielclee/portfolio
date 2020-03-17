import logging
import json
from content import Content
from sequence import Sequence

class Playlist:
    UNDEFINED = "undefined"
    EMPTY = ""
    NULL = "null"
    URL = "url"
    ID = "id"
    DWELL_TIME = "dwell_time"
    DEFAULT_SEQUENCE = "default_sequence"
    NEXT_SEQUENCE = "next_sequence"
    ENTRANCE_ACTIONS = "entrance_actions"
    TRIGGERS = "triggers"
    CONTENT_ID = "content_id"
    TARGET = "target"
    ACTION = "action"
    CONTENT = "content"
    SEQUENCE = "sequence"
    PARAMETER = "parameters"
    DURATION = "duration"
    ACTIVE = "active"
    PLAYLISTS = "playlists"


    def __init__(self, url, playlist, parentdir="./"):  # string, string, string
        self._source = str(playlist)
        self._url = url
        self._uuid = url.rpartition('/')[-1]
        self._playlistDirectory = str(parentdir + self._uuid + "/")
        self._content = {}
        self._contentPathList = []
        self._sequences = []
        self._hasMotionSensor = False
        self.CreatePlaylist(playlist)
        self._currentSequence = self.GetDefaultSequence()


    def CreatePlaylist(self, playlist):  # string
        reader = json.loads(playlist)
        content = reader[Playlist.CONTENT]
        self.AddContents(content)
        sequence = reader[Playlist.SEQUENCE]
        self.AddSequences(sequence)


    def AddContents(self, contentlist):
        for c in contentlist:
            content = Content(c)
            self._content[content.GetId()] = content
            self._contentPathList.append(str(self._playlistDirectory +
                                             content.GetFileName()))


    def AddContent(self, resource, contentId, uri):
        cObj = {}
        cObj[Playlist.URL] = resource
        cObj[Playlist.CONTENT_ID] = contentId
        c = Content(json.loads(cObj))
        c.SetUri(uri)
        self._content[c.GetId()] = c


    def AddSequences(self, sequencelist):
        first = True
        for s in sequencelist:
            sequence = Sequence(s)
            if first:
                sequence.SetAsDefaultSequence()
            self._sequences.append(sequence)
            first = False
            if sequence.HasMotionSensor():
                self._hasMotionSensor = True
            # End if
        # End for


    def SetName(self, url):
        self._url = url
        self.SetUUID(url)


    def SetUUID(self, url):
        parts = self.GetName().split("/")
        self._uuid = parts[len(parts) - 1]


    def GetUUID(self, url):
        return self._uuid


    def GetContentList(self):
        return list(self._content.values())


    def GetContentPathList(self):
        return self._contentPathList


    def GetSequences(self):
        return self._sequences


    def GetDefaultSequence(self):
        for sequence in self._sequences:
            if sequence.IsDefaultSequence():
                return sequence
        return self._sequences[0]


    def GetNextSequence(self):
        sequenceid = self._currentSequence.GetNextSequence()
        if sequenceid == None:
            self.ResetCurrentSequence()
        else:
            self._currentSequence = self.GetSequence(sequenceid)
        return self._currentSequence


    def GetSequence(self, id):
        for sequence in self._sequences:
            if sequence.GetId() == id:
                return sequence
        return None


    def ResetCurrentSequence(self):
        self._currentSequence = self.GetDefaultSequence()


    def GetUrl(self):
        return self._url


    def GetName(self):
        return self.GetUUID()


    def GetUUID(self):
        return self._uuid


    def GetContentObj(self, contentId):
        if not contentId in self._content:
            return None
        return self._content[contentId]


    def AddSequence(self, jo):  # JSON object
        sequence = Sequence(jo)
        self._sequences.append(sequence)


    def ToJSONObj(self):
        jo = {}
        contentArray = []
        for content in self._content.values():
            contentArray.append(content)
        sequenceArray = []
        for sequence in self._sequences:
            sequenceArray.append(sequence)
        jo[Playlist.CONTENT] = contentArray
        jo[Playlist.SEQUENCE] = sequenceArray
        return json.loads(jo)

        
    def ToString(self):
        return json.dumps(self.ToJSONObj())


    def GetSource(self):
        return self._source


    def SetContentDuration(self, contentId, duration):
        if not contentId in self._content:
            return
        self._content[contentId].SetDuration(duration)


    def SetContentReady(self, contentId, ready):
        if not contentId in self._content:
            return
        self._content[contentId].SetReady(ready)


    def HasMotionSensor(self):
        return self._hasMotionSensor
