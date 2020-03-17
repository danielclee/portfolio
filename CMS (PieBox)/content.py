import logging
import json

class Content:
    UNDEFINED = "undefined"
    URL = "url"
    CONTENT_ID = "content_id"

    def __init__(self, contentObj):  # json
        self._resource = ""
        self._contentId = ""
        self._uri = ""
        self._size = 0
        self._ready = False
        self._session = 0;
        self.SetResource(contentObj.get(Content.URL, Content.UNDEFINED))
        self.SetId(contentObj.get(Content.CONTENT_ID, Content.UNDEFINED))
        self._extension = self._resource.rpartition('.')[-1]
        self._filename = self._resource.rpartition('/')[-1]
        self._duration = 0  # ms


    def SetResource(self, res):
        self._resource = res


    def GetResource(self):
        return self._resource


    def SetId(self, id):
        self._contentId = id


    def GetId(self):
        return self._contentId


    def SetUri(self, uri):
        self._uri = uri


    def GetUri(self):
        return self._uri 


    def GetFileName(self):
        return self._filename


    def SetSize(self, sizeinbytes):
        self._size = sizeinbytes


    def GetSize(self):
        return self._size


    def SetReady(self, ready):
        self._ready = ready


    def GetReady(self):
        return self._ready


    def SetSession(self, session):
        self._session = session


    def GetSession(self):
        return self._session


    def SetDuration(self, duration):
        self._duration = duration


    def GetDuration(self):
        return self._duration


    def ToJSONObj(self):
        jo = {}
        jo[CONTENT.CONTENT_ID] = self.GetId()
        jo[CONTENT.URL] = self.GetResource()
        return json.loads(jo)


    def ToString(self):
        return json.dumps(self.ToJSONObj())
