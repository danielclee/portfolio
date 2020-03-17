import re
##import _thread
import threading
import json
import math
import time
from threading import Timer
from time import sleep
import hashlib
import json
import collections
import tkinter
import datetime
import logging
import tkinter.ttk as ttk

def misctest():
    triggerslist = []
    for i in range(0,4):
        if i == 1:
            triggerslist.append("pb01")
        elif i == 2:
            triggerslist.append("pb02")
    cmd = '{"action":"setup_io", "throttle":"0.35", "debounce":"3", '
    cmd += '"inputs":"' + ",".join(triggerslist) + '"}'
    print(cmd)


def ordereddicttest():
    print('Regular dictionary:')
    c = {}
    c['a'] = 'A'
    c['b'] = 'B'
    c['c'] = 'C'
    c['d'] = 'D'
    c['e'] = 'E'

    for k, v in c.items():
        print(k, v)

    print('\nOrderedDict:')
    d = collections.OrderedDict()
    d['a'] = 'A'
    d['b'] = 'B'
    d['c'] = 'C'
    d['d'] = 'D'
    d['e'] = 'E'
    
    for k, v in d.items():
        print(k, v)


def stringtest():
    _checkinRate = "86400"
    checkin_label = ("Check-in rate (secs) [default=86400] [current={c}]".\
                     format(c=_checkinRate))
    print(checkin_label)

    _serial = "Unknown"
    _model = "Unknown"
    _hardware = "Unknown"
    _product = "PieBox"
    _version = "0.5"

    uuid = "a9e1c860-532c-4fb4-af2c-00f0e78748a3"
    
    info = ("Serial : {s}\nHardware : {h}\nModel : {m}\n"
            "Product : {p}\nVersion : {v}\nUUID : {u}".\
            format(s=_serial, h=_hardware, m=_model,
                   p=_product, v=_version, u=uuid))

    print(info)


def stringtest2():
    gg = "\'pb01\'"
    print(gg)


def stringtest3():
    sqlcmd = "INSERT INTO analytics (input_id,type,playlist,sequence,timestamp,timezone,dwell,content,played,duration,datetime) VALUES ('pb03','pb','test_playlist1','test_sequence1',1511662294192,0,0,'test_content1',0,13,'2017-11-26T02:11:34.192397')"
    sqlcmd = "SELECT * FROM analytics ORDER BY id ASC"
    print(sqlcmd.upper().find("SELECT "))


def timetest():
    epoch = datetime.datetime.utcfromtimestamp(0)
    now = datetime.datetime.utcnow()
    delta = now - epoch
    print(int(delta.total_seconds() * 1000))
    print(time.timezone)
    print(now.isoformat())

    ## TimeZone tz = TimeZone.getTimeZone("UTC");
    ## DateFormat df = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'");
    ## df.setTimeZone(tz);
    ## String nowAsISO = df.format(new Date());
    ## return nowAsISO;
    
    ## print(datetime.datetime.utcnow())
    ## delta = datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)
    ## print((delta.seconds * 1000))

def jsontest():
    epoch = datetime.datetime.utcfromtimestamp(0)
    timeZoneOffset = time.timezone * 1000
    now = datetime.datetime.utcnow()
    delta = now - epoch
    timestamp = int(delta.total_seconds() * 1000)
    played = -1
    _cachedMSAnalyticEvent = {"action" : "input",
                              "input" : "pb01",
                              "type" : "pb",
                              "playlist" : "playlist1",
                              "sequence" : "sequence1",
                              "timestamp" : timestamp, 
                              "timezone" : timeZoneOffset,
                              "dwell" : 0,
                              "contenturl" : "www.url.com",
                              "played" : played,
                              "duration" : 1000,
                              "datetime" : now.isoformat()}
    print(_cachedMSAnalyticEvent)
    _cachedMSAnalyticEvent["dwell"] = 1234
    print(_cachedMSAnalyticEvent)


def jsontest2():
    ACTION = "action"
    TEST = "test"
    OUTPUT = "output"
    gg = (json.dumps({ACTION :
                      TEST,
                      OUTPUT :
                      "gg"}))
    print(gg)


def jsontest3():
    EVENT = "event"
    ACTION = "action"
    TEST = "test"
    OUTPUT = "output"
    list1 = []
    list2 = []
    list1.append('a')
    list1.append('b')
    list1.append('c')
    list2.append('1')
    list2.append('2')
    list2.append('3')
    gg = (json.dumps({EVENT : ACTION,
                      TEST : list1,
                      OUTPUT : list2}))
    gg2 = json.loads(gg)
    for a in gg2[TEST]:
        print(a)
    for n in gg2[OUTPUT]:
        print(n)


def listtest():
    quitPattern = "3434"
    settingsPattern = "4545"
    gg = [quitPattern, settingsPattern]
    gg.append("1")
    gg.append("2")
    gg.append("3")
    gg.append("4")
    gg.append("5")
    print(gg)
    hh = gg[:]
    if "5" in hh:
        print("found")
    else:
        print("missing")


def listtest2(testlist):
    print(testlist)


def dicttest():
    gg = {}
    gg["1"] = "A"
    gg["2"] = "B"
    gg["3"] = "C"
    gg["4"] = "D"
    gg["5"] = "E"
    numlist = list(gg.keys())
    alphalist = list(gg.values())
    print(numlist)
    print(alphalist)


def dicttest2():
    gg = {}
    gg["A"] = 1
    gg["B"] = 2
    gg["C"] = 3
    gg["D"] = 4
    gg["E"] = 5
    for key, value in gg.items():
        logging.debug("Key : " + key + ", Value : " + str(value))


def dicttest3():
    gg = {}
    gg["1"] = "A"
    gg["2"] = "B"
    gg["3"] = "C"
    gg["4"] = "D"
    gg["5"] = "E"
    numlist = list(gg.keys())
    alphalist = list(gg.values())
    print(numlist)
    print(alphalist)


def vartest(tmp):
    tmp += 10


def main():
    print("Starting local")

    # Test playlist
    ## misctest()
    ## ordereddicttest()
    ## stringtest()
    ## timetest()
    ## jsontest()
    ## jsontest3()
    ##listtest()
    ## dicttest()
    ## dicttest2()
    ## dicttest3()

    ## curr = 0
    ## vartest(curr)
    ## print(curr)
    ## vartest(curr)
    ## print(curr)
    ## stringtest2()
    ## stringtest3()

    quitPattern = "3434"
    settingsPattern = "4545"
    listtest2([quitPattern, settingsPattern])
    
    ## root = tkinter.Tk()
    ## frame = ttk.Frame()
    ## pb = ttk.Progressbar(frame, length=300, mode='determinate')
    ## frame.pack()
    ## pb.pack()
    ## pb.start(25)
    ## root.mainloop()    


if __name__ == "__main__":
    loglevel = logging.DEBUG
    logformat = '%(asctime)s [%(levelname)s] %(pathname)s::%(funcName)s(%(lineno)s) - %(message)s'
    loghandlers = [logging.FileHandler('test_log.log'), logging.StreamHandler()]
    logging.basicConfig(level = loglevel, format = logformat, handlers = loghandlers)

    main()
    
