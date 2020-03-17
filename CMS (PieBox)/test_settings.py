import logging
import json
import collections
import copy
import pickle
from playlist import Playlist
from settings import Settings

loglevel = logging.DEBUG
logformat = '%(asctime)s [%(levelname)s] %(pathname)s::%(funcName)s(%(lineno)s) - %(message)s'
loghandlers = [logging.FileHandler('test_log.log'), logging.StreamHandler()]
logging.basicConfig(level = loglevel, format = logformat, handlers = loghandlers)

## sample_playlist = '{"content": [{"url": "https://fulgent.sandd.studio/api/v1.0/content/eccd2e1e-a1b6-4cd2-8b99-6a0e18abd5f4.jpg", "content_id": "7afebcc1-67a7-4292-bbec-994243dd5cf2"}, {"url": "https://fulgent.sandd.studio/api/v1.0/content/31a54253-2991-4d22-b093-cb89c3ebda97.jpg", "content_id": "ea320e39-9c1e-4569-bfb0-6ab265a724f0"}, {"url": "https://fulgent.sandd.studio/api/v1.0/content/0fb255f1-0256-4cfd-a379-675ef620db09.jpg", "content_id": "dcd07b26-b6e0-49f8-aab1-c1c4d4831a05"}, {"url": "https://fulgent.sandd.studio/api/v1.0/content/a6583dc5-4cdb-46d3-9bc9-2e34e0784326.mp4", "content_id": "77553d84-2fe3-4f21-8c29-2e750270cf16"}], "sequence": [{"dwell_time": 30, "next_sequence": null, "entrance_actions": [{"parameters": null, "action": "set_screen_brightness", "target": "75"}], "triggers": {"ms": [{"parameters": null, "action": "next_sequence", "target": "e79f98ad-f9ad-4744-a13c-58ba9b1432cb"}]}, "id": "1a578032-ef8d-446f-b0a5-b5683e5b0726", "name": "Satelite", "content_id": "77553d84-2fe3-4f21-8c29-2e750270cf16"}, {"dwell_time": 30, "next_sequence": null, "entrance_actions": [{"parameters": null, "action": "led_cycle", "target": "led02"}, {"parameters": null, "action": "set_screen_brightness", "target": "100"}, {"parameters": null, "action": "led_on", "target": "led01"}, {"parameters": null, "action": "set_volume", "target": "5"}], "triggers": {"pb02": [{"parameters": null, "action": "next_sequence", "target": "beb7f922-c464-4938-bbd5-9f7a400fe897"}]}, "id": "fedd19a0-e8a5-4351-86f2-3771992afb68", "name": "Lazer", "content_id": "ea320e39-9c1e-4569-bfb0-6ab265a724f0"}, {"dwell_time": 30, "next_sequence": null, "entrance_actions": [{"parameters": null, "action": "led_cycle", "target": "led01"}, {"parameters": null, "action": "set_screen_brightness", "target": "100"}, {"parameters": null, "action": "set_volume", "target": "2"}, {"parameters": null, "action": "led_on", "target": "led02"}], "triggers": {"pb01": [{"parameters": null, "action": "next_sequence", "target": "fedd19a0-e8a5-4351-86f2-3771992afb68"}]}, "id": "beb7f922-c464-4938-bbd5-9f7a400fe897", "name": "Galaxy", "content_id": "dcd07b26-b6e0-49f8-aab1-c1c4d4831a05"}, {"dwell_time": 10, "next_sequence": null, "entrance_actions": [{"parameters": null, "action": "led_cycle", "target": "led02"}, {"parameters": null, "action": "set_screen_brightness", "target": "100"}, {"parameters": null, "action": "led_cycle", "target": "led01"}, {"parameters": null, "action": "set_volume", "target": "2"}], "triggers": {"pb02": [{"parameters": null, "action": "next_sequence", "target": "beb7f922-c464-4938-bbd5-9f7a400fe897"}], "pb01": [{"parameters": null, "action": "next_sequence", "target": "fedd19a0-e8a5-4351-86f2-3771992afb68"}]}, "id": "e79f98ad-f9ad-4744-a13c-58ba9b1432cb", "name": "Beach", "content_id": "7afebcc1-67a7-4292-bbec-994243dd5cf2"}], "id": "97bceea2-4c61-4c2c-87c3-99f617da73d7"}'
## playlist = Playlist("https://fulgent.sandd.studio/devices/a9e1c860-532c-4fb4-af2c-00f0e78748a3/playlist",
##                     sample_playlist)


## pickle.dump(sample_playlist, open( "test_save.p", "wb"))
## sample_playlist = pickle.load(open( "settings.p", "rb" ) )
## print(sample_playlist)
## settings.AddContent("content1", "./content1.mp4")
## settings.AddContent("content2", "./content2.mp4")
## settings = Settings()
## settings.SetTopPlaylistSignature("", False)
## settings.AddPlaylist("playlist1", playlist, False)


## settings = Settings()
## settings.SetToken("", false)
## settings.SetDeviceResourceURL("", false)
## settings.SetDeviceID("", false)
## settings.Save()


## settings = Settings()
## settings.SetToken('abc123', False)
## settings.SetDeviceResourceURL('https://fulgent.sandd.studio/api/v1.0/device/a9e1c860-532c-4fb4-af2c-00f0e78748a3', False)
## settings.SetDeviceID('a9e1c860-532c-4fb4-af2c-00f0e78748a3', False)
## playlist_url = 'https://fulgent.sandd.studio/api/v1.0/playlist/59d8de29-c3a3-4464-9ba7-1349ea4edb7d'
## playlist_source = '{"sequence": [{"content_id": "bbdd2e49-f683-4853-b293-4c049bab8923", "next_sequence": null, "entrance_actions": [{"action": "set_volume", "target": "6", "parameters": null}, {"action": "led_on", "target": "led10", "parameters": null}, {"action": "led_on", "target": "led09", "parameters": null}, {"action": "led_cycle", "target": "led02", "parameters": null}, {"action": "led_cycle", "target": "led01", "parameters": null}, {"action": "set_screen_brightness", "target": "70", "parameters": null}], "id": "6f3f89f6-fbcb-47e2-bc17-e9fe25b04544", "name": "Rapids", "triggers": {"pb01": [{"action": "next_sequence", "target": "71957627-c495-4138-b0d7-6d7894259ca5", "parameters": null}], "pb02": [{"action": "next_sequence", "target": "d5fa2f92-c29a-4c4b-8f15-492bd917d295", "parameters": null}], "pb09": [{"action": "volume_up", "target": "1", "parameters": null}], "pb10": [{"action": "volume_down", "target": "1", "parameters": null}]}, "dwell_time": 10}, {"content_id": "ea8127a9-885f-4e54-955f-0b46e55f4c5b", "next_sequence": null, "entrance_actions": [{"action": "led_on", "target": "led10", "parameters": null}, {"action": "set_volume", "target": "10", "parameters": null}, {"action": "set_screen_brightness", "target": "100", "parameters": null}, {"action": "led_on", "target": "led09", "parameters": null}, {"action": "led_on", "target": "led01", "parameters": null}], "id": "71957627-c495-4138-b0d7-6d7894259ca5", "name": "Sound", "triggers": {"pb02": [{"action": "next_sequence", "target": "d5fa2f92-c29a-4c4b-8f15-492bd917d295", "parameters": null}], "pb09": [{"action": "volume_up", "target": "3", "parameters": null}], "pb10": [{"action": "volume_down", "target": "3", "parameters": null}]}, "dwell_time": 10}, {"content_id": "ca01bd1c-99ab-4d5b-9761-a55d208114c1", "next_sequence": null, "entrance_actions": [{"action": "set_volume", "target": "9", "parameters": null}, {"action": "set_screen_brightness", "target": "100", "parameters": null}, {"action": "led_on", "target": "led02", "parameters": null}], "id": "d5fa2f92-c29a-4c4b-8f15-492bd917d295", "name": "Boots", "triggers": {"pb01": [{"action": "next_sequence", "target": "71957627-c495-4138-b0d7-6d7894259ca5", "parameters": null}], "pb09": [{"action": "volume_down", "target": "3", "parameters": null}, {"action": "volume_up", "target": "3", "parameters": null}]}, "dwell_time": 10}], "content": [{"content_id": "bbdd2e49-f683-4853-b293-4c049bab8923", "url": "https://fulgent.sandd.studio/api/v1.0/content/9a0c61cc-7729-474d-a507-5b1324477d5a.mp4"}, {"content_id": "ea8127a9-885f-4e54-955f-0b46e55f4c5b", "url": "https://fulgent.sandd.studio/api/v1.0/content/8d135e28-1073-459d-a891-09fd4b0f511e.mp4"}, {"content_id": "ca01bd1c-99ab-4d5b-9761-a55d208114c1", "url": "https://fulgent.sandd.studio/api/v1.0/content/7608b080-f4f4-4ac0-bd1f-7ff67907b703.mp4"}], "id": "59d8de29-c3a3-4464-9ba7-1349ea4edb7d"}'
## playlistobj = Playlist(playlist_url, playlist_source)
## settings.AddPlaylist(playlist_url, playlistobj, save=False)
## settings.Save()


## token = "p5xwn8e"
## url = "https://fulgent.sandd.studio/api/v1.0/devices/f48d5e3b-a8e5-4251-8895-17eb9f406840"
## id = "f48d5e3b-a8e5-4251-8895-17eb9f406840"


######### TEST ### 3434 #######################################################
## save_settings = Settings("test_settings.p")
## save_settings.SetDeviceID('a9e1c860-532c-4fb4-af2c-00f0e78748a3', False)
## save_settings.SetDeviceResourceURL('https://fulgent.sandd.studio/api/v1.0/device/a9e1c860-532c-4fb4-af2c-00f0e78748a3', False)
## save_settings.SetToken('p5xwn8e', False)
## save_settings.SetIOThrottle(2.5, False)
## save_settings.SetIODebounce(1, False)
## save_settings.SetCheckinTimerValue(34000, False)
## save_settings.SetAnalyticsTimerValue(45000, False)
## save_settings.SetTopPlaylistSignature("abc123", False)
## playlist_url = 'https://fulgent.sandd.studio/api/v1.0/playlist/59d8de29-c3a3-4464-9ba7-1349ea4edb7d'
## playlist_source = '{"sequence": [{"content_id": "bbdd2e49-f683-4853-b293-4c049bab8923", "next_sequence": null, "entrance_actions": [{"action": "set_volume", "target": "6", "parameters": null}, {"action": "led_on", "target": "led10", "parameters": null}, {"action": "led_on", "target": "led09", "parameters": null}, {"action": "led_cycle", "target": "led02", "parameters": null}, {"action": "led_cycle", "target": "led01", "parameters": null}, {"action": "set_screen_brightness", "target": "70", "parameters": null}], "id": "6f3f89f6-fbcb-47e2-bc17-e9fe25b04544", "name": "Rapids", "triggers": {"pb01": [{"action": "next_sequence", "target": "71957627-c495-4138-b0d7-6d7894259ca5", "parameters": null}], "pb02": [{"action": "next_sequence", "target": "d5fa2f92-c29a-4c4b-8f15-492bd917d295", "parameters": null}], "pb09": [{"action": "volume_up", "target": "1", "parameters": null}], "pb10": [{"action": "volume_down", "target": "1", "parameters": null}]}, "dwell_time": 10}, {"content_id": "ea8127a9-885f-4e54-955f-0b46e55f4c5b", "next_sequence": null, "entrance_actions": [{"action": "led_on", "target": "led10", "parameters": null}, {"action": "set_volume", "target": "10", "parameters": null}, {"action": "set_screen_brightness", "target": "100", "parameters": null}, {"action": "led_on", "target": "led09", "parameters": null}, {"action": "led_on", "target": "led01", "parameters": null}], "id": "71957627-c495-4138-b0d7-6d7894259ca5", "name": "Sound", "triggers": {"pb02": [{"action": "next_sequence", "target": "d5fa2f92-c29a-4c4b-8f15-492bd917d295", "parameters": null}], "pb09": [{"action": "volume_up", "target": "3", "parameters": null}], "pb10": [{"action": "volume_down", "target": "3", "parameters": null}]}, "dwell_time": 10}, {"content_id": "ca01bd1c-99ab-4d5b-9761-a55d208114c1", "next_sequence": null, "entrance_actions": [{"action": "set_volume", "target": "9", "parameters": null}, {"action": "set_screen_brightness", "target": "100", "parameters": null}, {"action": "led_on", "target": "led02", "parameters": null}], "id": "d5fa2f92-c29a-4c4b-8f15-492bd917d295", "name": "Boots", "triggers": {"pb01": [{"action": "next_sequence", "target": "71957627-c495-4138-b0d7-6d7894259ca5", "parameters": null}], "pb09": [{"action": "volume_down", "target": "3", "parameters": null}, {"action": "volume_up", "target": "3", "parameters": null}]}, "dwell_time": 10}], "content": [{"content_id": "bbdd2e49-f683-4853-b293-4c049bab8923", "url": "https://fulgent.sandd.studio/api/v1.0/content/9a0c61cc-7729-474d-a507-5b1324477d5a.mp4"}, {"content_id": "ea8127a9-885f-4e54-955f-0b46e55f4c5b", "url": "https://fulgent.sandd.studio/api/v1.0/content/8d135e28-1073-459d-a891-09fd4b0f511e.mp4"}, {"content_id": "ca01bd1c-99ab-4d5b-9761-a55d208114c1", "url": "https://fulgent.sandd.studio/api/v1.0/content/7608b080-f4f4-4ac0-bd1f-7ff67907b703.mp4"}], "id": "59d8de29-c3a3-4464-9ba7-1349ea4edb7d"}'
## playlistobj = Playlist(playlist_url, playlist_source)
## save_settings.AddPlaylist(playlist_url, playlistobj, save=False)
## save_settings.Save()
## save_settings.ToString()
######### TEST ### 3434 #######################################################

print("")
print("-----------------------------------------------------")
print("")

settings = Settings("test_settings.p")
if settings.Load() == True:
    settings.ToString()
else:
    print("No settings file")
