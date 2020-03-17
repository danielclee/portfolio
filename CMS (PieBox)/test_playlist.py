import re
import _thread
import threading
import json
import math
import time
from queue import Queue
from threading import Timer
from time import sleep
from datastore import DataStore
from playlist import Playlist
from link import Link
import hashlib
import json
import copy

def playlisttest():
    print("Starting playlist test")
    _playlists = []
    #
    file = open("./playlist/97bceea2-4c61-4c2c-87c3-99f617da73d7.json", "r")
    sample_playlist = file.read()
    ## print(sample_playlist)
    file.close()
    ##'{"content": [{"url": "https://fulgent.sandd.studio/api/v1.0/content/eccd2e1e-a1b6-4cd2-8b99-6a0e18abd5f4.jpg", "content_id": "7afebcc1-67a7-4292-bbec-994243dd5cf2"}, {"url": "https://fulgent.sandd.studio/api/v1.0/content/31a54253-2991-4d22-b093-cb89c3ebda97.jpg", "content_id": "ea320e39-9c1e-4569-bfb0-6ab265a724f0"}, {"url": "https://fulgent.sandd.studio/api/v1.0/content/0fb255f1-0256-4cfd-a379-675ef620db09.jpg", "content_id": "dcd07b26-b6e0-49f8-aab1-c1c4d4831a05"}, {"url": "https://fulgent.sandd.studio/api/v1.0/content/a6583dc5-4cdb-46d3-9bc9-2e34e0784326.mp4", "content_id": "77553d84-2fe3-4f21-8c29-2e750270cf16"}], "sequence": [{"dwell_time": 30, "next_sequence": null, "entrance_actions": [{"parameters": null, "action": "set_screen_brightness", "target": "75"}], "triggers": {"ms": [{"parameters": null, "action": "next_sequence", "target": "e79f98ad-f9ad-4744-a13c-58ba9b1432cb"}]}, "id": "1a578032-ef8d-446f-b0a5-b5683e5b0726", "name": "Satelite", "content_id": "7afebcc1-67a7-4292-bbec-994243dd5cf2"}, {"dwell_time": 30, "next_sequence": null, "entrance_actions": [{"parameters": null, "action": "led_cycle", "target": "led02"}, {"parameters": null, "action": "set_screen_brightness", "target": "100"}, {"parameters": null, "action": "led_on", "target": "led01"}, {"parameters": null, "action": "set_volume", "target": "5"}], "triggers": {"pb02": [{"parameters": null, "action": "next_sequence", "target": "beb7f922-c464-4938-bbd5-9f7a400fe897"}]}, "id": "fedd19a0-e8a5-4351-86f2-3771992afb68", "name": "Lazer", "content_id": "ea320e39-9c1e-4569-bfb0-6ab265a724f0"}, {"dwell_time": 30, "next_sequence": null, "entrance_actions": [{"parameters": null, "action": "led_cycle", "target": "led01"}, {"parameters": null, "action": "set_screen_brightness", "target": "100"}, {"parameters": null, "action": "set_volume", "target": "2"}, {"parameters": null, "action": "led_on", "target": "led02"}], "triggers": {"pb01": [{"parameters": null, "action": "next_sequence", "target": "fedd19a0-e8a5-4351-86f2-3771992afb68"}]}, "id": "beb7f922-c464-4938-bbd5-9f7a400fe897", "name": "Galaxy", "content_id": "dcd07b26-b6e0-49f8-aab1-c1c4d4831a05"}, {"dwell_time": 10, "next_sequence": null, "entrance_actions": [{"parameters": null, "action": "led_cycle", "target": "led02"}, {"parameters": null, "action": "set_screen_brightness", "target": "100"}, {"parameters": null, "action": "led_cycle", "target": "led01"}, {"parameters": null, "action": "set_volume", "target": "2"}], "triggers": {"pb02": [{"parameters": null, "action": "next_sequence", "target": "beb7f922-c464-4938-bbd5-9f7a400fe897"}], "pb01": [{"parameters": null, "action": "next_sequence", "target": "fedd19a0-e8a5-4351-86f2-3771992afb68"}]}, "id": "e79f98ad-f9ad-4744-a13c-58ba9b1432cb", "name": "Beach", "content_id": "77553d84-2fe3-4f21-8c29-2e750270cf16"}], "id": "97bceea2-4c61-4c2c-87c3-99f617da73d7"}'
    playlistvec = []
    playlistvec.append(sample_playlist)

    #
    _playlists.clear()
    for playlist in playlistvec:
        # Get sha1 for playlist
        sha1 = hashlib.sha1()
        sha1.update(playlist.encode('utf-8'))
        sha1str = sha1.hexdigest()
        _playlists.append(Playlist("https://fulgent.sandd.studio/devices/a9e1c860-532c-4fb4-af2c-00f0e78748a3/playlist",
                                   playlist))
        _currentPlaylist = copy.deepcopy(_playlists[0])
        _currentPlaylist3 = copy.deepcopy(_playlists[0])

    #
    sequence = None;
    _currentPlaylist.ResetCurrentSequence()
    sequence = _currentPlaylist.GetDefaultSequence()
    contentid = sequence.GetContentId()
    content = _currentPlaylist.GetContentObj(contentid)
    filename = content.GetFileName()
    videomsg1 = '{"action":"play", "file":"' + filename + '"}'
    print(_currentPlaylist)
    print(videomsg1)

    #
    sequence = _currentPlaylist3.GetNextSequence()
    contentid = sequence.GetContentId()
    content = _currentPlaylist3.GetContentObj(contentid)
    filename = content.GetFileName()
    videomsg2 = '{"action":"play", "file":"' + filename + '"}'
    print(_currentPlaylist3)
    print(videomsg2)


def playlisttest2():
    print("Starting playlist test 2")

    sample_playlist_url = "https://fulgent.sandd.studio/api/v1.0/playlist/83092fc0-339f-4d49-8250-c3af846fe8f2"
    sample_playlist = '{\"sequence\": [{\"content_id\": \"6ac47168-9f4f-4680-bb9d-2e8552aaebde\", \"next_sequence\": null, \"entrance_actions\": [{\"action\": \"set_volume\", \"target\": \"5\", \"parameters\": \"5\"}], \"id\": \"2c006c32-a63e-4471-bc32-7d65da954660\", \"name\": \"Idle\", \"triggers\": {\"pb01\": [{\"action\": \"next_sequence\", \"target\": \"b0fe18c6-9c4a-4a87-9e68-7db8a1cbc6aa\", \"parameters\": null}], \"pb02\": [{\"action\": \"next_sequence\", \"target\": \"3b788ea8-0716-434e-a32b-1bde9421dc79\", \"parameters\": null}]}, \"dwell_time\": 10}, {\"content_id\": \"98a1beb5-5693-47a3-a70c-fb53b1fbc996\", \"next_sequence\": null, \"entrance_actions\": [{\"action\": \"set_volume\", \"target\": \"10\", \"parameters\": \"10\"}], \"id\": \"b0fe18c6-9c4a-4a87-9e68-7db8a1cbc6aa\", \"name\": \"B1\", \"triggers\": {}, \"dwell_time\": 10}, {\"content_id\": \"a404552e-ea75-4255-9946-84caa8c89956\", \"next_sequence\": null, \"entrance_actions\": [{\"action\": \"set_volume\", \"target\": \"10\", \"parameters\": \"10\"}], \"id\": \"3b788ea8-0716-434e-a32b-1bde9421dc79\", \"name\": \"B2\", \"triggers\": {}, \"dwell_time\": 10}], \"content\": [{\"content_id\": \"6ac47168-9f4f-4680-bb9d-2e8552aaebde\", \"url\": \"https://fulgent.sandd.studio/api/v1.0/content/69e094f4-be0d-4c87-b486-90acf3e56070.mp4\"}, {\"content_id\": \"98a1beb5-5693-47a3-a70c-fb53b1fbc996\", \"url\": \"https://fulgent.sandd.studio/api/v1.0/content/874b8d27-831d-486e-b399-23709b2ed227.mp4\"}, {\"content_id\": \"a404552e-ea75-4255-9946-84caa8c89956\", \"url\": \"https://fulgent.sandd.studio/api/v1.0/content/1e61c48c-792c-4e5d-95d2-c15a72cb7f6a.mp4\"}], \"id\": \"83092fc0-339f-4d49-8250-c3af846fe8f2\"}'

    playlistobj = Playlist(sample_playlist_url, sample_playlist)
    print(playlistobj)


def playlisttest3():
    print("Starting playlist test 3")

    playlists = []
    link = Link()
    sample_playlist_url = "https://fulgent.sandd.studio/api/v1.0/playlist/83092fc0-339f-4d49-8250-c3af846fe8f2"
    sample_playlist = '{\"sequence\": [{\"content_id\": \"6ac47168-9f4f-4680-bb9d-2e8552aaebde\", \"next_sequence\": null, \"entrance_actions\": [{\"action\": \"set_volume\", \"target\": \"5\", \"parameters\": \"5\"}], \"id\": \"2c006c32-a63e-4471-bc32-7d65da954660\", \"name\": \"Idle\", \"triggers\": {\"pb01\": [{\"action\": \"next_sequence\", \"target\": \"b0fe18c6-9c4a-4a87-9e68-7db8a1cbc6aa\", \"parameters\": null}], \"pb02\": [{\"action\": \"next_sequence\", \"target\": \"3b788ea8-0716-434e-a32b-1bde9421dc79\", \"parameters\": null}]}, \"dwell_time\": 10}, {\"content_id\": \"98a1beb5-5693-47a3-a70c-fb53b1fbc996\", \"next_sequence\": null, \"entrance_actions\": [{\"action\": \"set_volume\", \"target\": \"10\", \"parameters\": \"10\"}], \"id\": \"b0fe18c6-9c4a-4a87-9e68-7db8a1cbc6aa\", \"name\": \"B1\", \"triggers\": {}, \"dwell_time\": 10}, {\"content_id\": \"a404552e-ea75-4255-9946-84caa8c89956\", \"next_sequence\": null, \"entrance_actions\": [{\"action\": \"set_volume\", \"target\": \"10\", \"parameters\": \"10\"}], \"id\": \"3b788ea8-0716-434e-a32b-1bde9421dc79\", \"name\": \"B2\", \"triggers\": {}, \"dwell_time\": 10}], \"content\": [{\"content_id\": \"6ac47168-9f4f-4680-bb9d-2e8552aaebde\", \"url\": \"https://fulgent.sandd.studio/api/v1.0/content/69e094f4-be0d-4c87-b486-90acf3e56070.mp4\"}, {\"content_id\": \"98a1beb5-5693-47a3-a70c-fb53b1fbc996\", \"url\": \"https://fulgent.sandd.studio/api/v1.0/content/874b8d27-831d-486e-b399-23709b2ed227.mp4\"}, {\"content_id\": \"a404552e-ea75-4255-9946-84caa8c89956\", \"url\": \"https://fulgent.sandd.studio/api/v1.0/content/1e61c48c-792c-4e5d-95d2-c15a72cb7f6a.mp4\"}], \"id\": \"83092fc0-339f-4d49-8250-c3af846fe8f2\"}'
    playlistobj = Playlist(sample_playlist_url, sample_playlist)
    playlists.append(playlistobj)
    print(type(playlists))
    print(playlists)
    link.SetObjectCache(playlists)

    playlists2 = link.GetObjectCache()
    print(type(playlists2))
    print(playlists2)


def main():
    print("Starting local")

    # Test playlist
    ## playlisttest()
    ## playlisttest2()
    playlisttest3()


if __name__ == "__main__":
    main()
