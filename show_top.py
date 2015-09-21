#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests, os, sys
from pprint import pprint

def get_user_info(kw):
    r = requests.post('http://api.turfgame.com/v4/users/top', json=kw)
    return r.json()

kw = {"from" : "1", "to" : "100" }
if len(sys.argv) > 1:
    kw["country"] = sys.argv[1]
else:
    kw["region"] = u"Västra Götaland"

for i, userInfo in enumerate(get_user_info(kw)):
    indexStr = str(i + 1).rjust(3) + "."
    name = userInfo["name"].ljust(20).encode("utf-8")
    points = str(userInfo["points"]).rjust(6)
    regionStr = ""
    if len(sys.argv) > 1:
        regionStr = userInfo["region"]["name"].ljust(20)
    zones = (str(len(userInfo["zones"])) + "Z").rjust(8)
    pph = ("+" + str(userInfo["pointsPerHour"])).rjust(8)
    print indexStr, name, points, regionStr, zones, pph
