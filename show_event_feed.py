#!/usr/bin/env python

import requests, os, sys
from pprint import pprint
from datetime import time

def get_event_info(name):
    r = requests.get('http://api.turfgame.com/unstable/events/' + name + '/feed')
    return r.json()

def formatTime(timeStr):
    timeDat = timeStr[11:-5]
    hour, rest = timeDat.split(":", 1)
    actualHour = int(hour) + 2
    return str(actualHour) + ":" + rest

for takeover in reversed(get_event_info(sys.argv[1])):
    print formatTime(takeover["time"]).ljust(10), takeover["zone"]["name"].ljust(20).encode("utf-8"), takeover["currentOwner"]["name"].ljust(20).encode("utf-8")

