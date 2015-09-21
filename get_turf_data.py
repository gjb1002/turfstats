#!/usr/bin/env python
# -*- coding: utf-8 -*-


import requests, os
from datetime import datetime
from pprint import pprint

def get_new_zones(user):
    r = requests.post('http://api.turfgame.com/v4/users', json=[{"name" : user}])
    dict = r.json()[0]
    return dict["zones"]

def get_zones_from_list(dataType, info):
    zoneRequestData = [{ dataType : zdat } for zdat in info ]
    r = requests.post('http://api.turfgame.com/v4/zones', json=zoneRequestData)
    return r.json(), r.encoding

currDir = os.path.dirname(os.path.abspath(__file__))
fileName = os.path.join(currDir, "curr_turf_data.txt")
zoneData = eval(open(fileName).read())
zoneIds = zoneData.keys()

configFileName = os.path.join(currDir, "turf_config.txt")
if not os.path.isfile(configFileName):
    sys.stderr.write("ERROR: no config file found at " + configFileName + ": please create!\n")
    sys.exit(1)

configDict = eval(open(configFileName).read())
user = configDict.get("username")
newZoneNames = []
if len(newZoneNames):
    zoneInfoList, _ = get_zones_from_list("name", newZoneNames)
    for zoneInfo in zoneInfoList:
        if zoneInfo["id"] not in zoneIds:
            zoneIds.append(zoneInfo["id"])

staticZoneData = {}
zoneInfoList, encoding = get_zones_from_list("id", zoneIds)
for zoneInfo in zoneInfoList: 
    currId = zoneInfo["id"]
    prevData = None
    staticZoneData[currId] = zoneInfo["name"], zoneInfo["takeoverPoints"], zoneInfo["pointsPerHour"], zoneInfo["longitude"], zoneInfo["latitude"]
    if "dateLastTaken" in zoneInfo and "currentOwner" in zoneInfo:
        dataNow = zoneInfo["dateLastTaken"], zoneInfo["currentOwner"]["id"]
        if currId in zoneData:
            recordsList = zoneData.get(currId)
            if len(recordsList) == 0 or recordsList[-1] != dataNow:
                recordsList.append(dataNow)
        else:
            zoneData[currId] = [ dataNow ]
    else:
        zoneData[currId] = []

with open(fileName, "w") as f:
    pprint(zoneData, f)

staticFile = os.path.join(currDir, "static_zone_data.txt")
with open(staticFile, "w") as f:
    pprint(staticZoneData, f)
