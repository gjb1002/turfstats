#!/usr/bin/env python

import requests, os, sys
from pprint import pprint

def get_user_info(user):
    r = requests.post('http://api.turfgame.com/v4/users', json=[{"name" : user}])
    return r.json()[0]

userName = sys.argv[1]
userInfo = get_user_info(userName)
pprint(userInfo)
