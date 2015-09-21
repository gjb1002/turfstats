#!/usr/bin/env python

import requests, os, sys
from pprint import pprint

def get_zones_from_list(dataType, info):
    zoneRequestData = [{ dataType : zdat } for zdat in info ]
    r = requests.post('http://api.turfgame.com/v4/zones', json=zoneRequestData)
    return r.json(), r.encoding


zoneName = sys.argv[1]
zoneInfoList, _ = get_zones_from_list("name", [ zoneName ])
pprint(zoneInfoList)
