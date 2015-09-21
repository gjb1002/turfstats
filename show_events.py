#!/usr/bin/env python

import requests, os, sys
from pprint import pprint

def get_event_info():
    r = requests.get('http://api.turfgame.com/unstable/events')
    return r.json()

pprint(get_event_info())

