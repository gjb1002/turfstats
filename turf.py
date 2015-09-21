#!/usr/bin/env python

import requests, sys, os
from datetime import datetime
from pprint import pprint
currDir = os.path.dirname(os.path.abspath(__file__))
configFileName = os.path.join(currDir, "turf_config.txt")
if not os.path.isfile(configFileName):
    sys.stderr.write("ERROR: no config file found at " + configFileName + ": please create!\n")
    sys.exit(1)

configDict = eval(open(configFileName).read())
user = configDict.get("username")
r = requests.post('http://api.turfgame.com/v4/users', json=[{"name" : user}])
try:
    dict = r.json()[0]
    zoneIds = dict["zones"]
    print "You own", len(zoneIds), "zones!"
    zoneRequestData = [{ "id" : zid } for zid in zoneIds ]
    r = requests.post('http://api.turfgame.com/v4/zones', json=zoneRequestData)
    zonesTaken = []
    for zoneInfo in r.json():
        dateStr = zoneInfo["dateLastTaken"]
        dt = datetime.strptime(dateStr[:-5], "%Y-%m-%dT%H:%M:%S")
        lengthOwned = datetime.utcnow() - dt
        zonesTaken.append((lengthOwned, zoneInfo["name"]))

    zonesTaken.sort(key=lambda x: x[0], reverse=True)
    for lengthOwned, zoneName in zonesTaken:
        print (datetime.now() - lengthOwned).strftime("%Y-%m-%d %H:%M"), ":", zoneName.encode(r.encoding)
except ValueError:
    sys.stderr.write("ERROR: Turf not responding properly\n" + r.reason + "\n")
    sys.exit(1)
