#!/usr/bin/env python

import requests, os, sys
from pprint import pprint

def get_event_info(name):
    r = requests.get('http://api.turfgame.com/unstable/events/' + name)
    return r.json()

info = get_event_info(sys.argv[1])
for participantInfo in info["participants"]:
    print str(participantInfo["place"]).rjust(2) + ". " + participantInfo["name"].ljust(20).encode("utf-8"), str(int(participantInfo["points"])).rjust(4)

