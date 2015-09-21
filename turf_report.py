#!/usr/bin/env python
from datetime import datetime, timedelta
import time, sys, requests, os, argparse
from pprint import pprint

class Zone:
    def __init__(self, zoneId, prevAvg, name, takepoints, pph, longitude, latitude):
        self.zoneId = zoneId
        self.name = name
        self.takepoints = takepoints
        self.pph = pph
        self.prevExpectedPoints = prevAvg
        self.longitude = longitude
        self.latitude = latitude
        self.expectedPoints = None

    def __repr__(self):
        return self.name.ljust(15).encode("utf-8") + " (" + str(self.takepoints).rjust(3) + "/+" + str(self.pph) + ")      "

    def getPoints(self, hoursHeld):
        return self.takepoints + int(hoursHeld * self.pph)

    def getAverage(self, allPoints):
        return int(round(float(sum(allPoints)) / len(allPoints)))

    def matchesDirection(self, direction):
        if direction is None:
            return True
        elif direction == "west":
            return self.longitude < home_longitude
        elif direction == "east":
            return self.longitude > home_longitude
        elif direction == "south":
            return self.latitude < home_latitude
        elif direction == "north":
            return self.latitude > home_latitude
        elif direction == "local":
            long_diff = self.longitude - home_longitude
            lat_diff = self.latitude - home_latitude
            long_measure = abs(long_diff)
            lat_measure = abs(lat_diff) * 1.2 # Wild approximation of earth's curvature :)
            return long_measure < 0.01 and lat_measure < 0.01
        else:
            return True

    def setExpectedPoints(self, rulePeriods):
        if len(rulePeriods) < 2:
            if len(rulePeriods) == 1 and self.prevExpectedPoints is None:
                self.expectedPoints = self.getPoints(rulePeriods[0].getHours())
            if self.prevExpectedPoints is None:
                return

        allPoints = [ self.getPoints(p.getHours()) for p in rulePeriods if p.complete ]
        if self.prevExpectedPoints is not None:
            allPoints.append(self.prevExpectedPoints)
        self.expectedPoints = self.getAverage(allPoints)
        if not rulePeriods[-1].complete:
            incompletePoints = self.getPoints(rulePeriods[-1].getHours())
            if incompletePoints > self.expectedPoints:
                allPoints.append(incompletePoints)
                self.expectedPoints = self.getAverage(allPoints)

    def getExpectedPointsOutput(self):
        txt = "Expected = " + str(self.expectedPoints) if self.expectedPoints else ""
        if self.prevExpectedPoints is not None:
            txt += " (" + str(self.prevExpectedPoints) + ")"
        return txt
 
class User:
    @classmethod
    def getUserInfo(cls, userIds):
        userRequestData = [{ "id" : uid } for uid in userIds.keys() ]
        r = requests.post('http://api.turfgame.com/v4/users', json=userRequestData)
        for userInfo in r.json():
            user = userIds.get(userInfo["id"])
            user.setInfo(userInfo)
        
    def __init__(self, userId=None, userName=None):
        self.userId = userId or self.getUserId(userName)
        self.userName = userName
        self.place = None

    def __hash__(self):
        return self.userId 

    def __eq__(self, other):
        return other is not None and self.userId == other.userId

    def setInfo(self, userInfo):
        self.userName = userInfo["name"]
        self.place = userInfo["place"]

    def getUserId(self, name):
        info = {}
        userRequestData = [{ "name" : name }]
        r = requests.post('http://api.turfgame.com/v4/users', json=userRequestData)
        return r.json()[0]["id"]

    def __repr__(self):
        name = self.userName or str(self.userId)
        nameWithPlace = name + "(" + str(self.place) + ")"
        return str(nameWithPlace.ljust(20).encode("utf-8"))

class RulePeriod:
    def __init__(self, zone, user, startTime, endTime, complete=True):
        self.zone = zone
        self.user = user
        self.startTime = startTime
        self.endTime = endTime
        self.complete = complete

    def dtOut(self, dt):
        return dt.strftime("%Y-%m-%d %H:%M") if dt else ""

    def hoursOut(self, hourFloat):
        wholeHours = int(hourFloat)
        rem = hourFloat - wholeHours
        return str(wholeHours).rjust(2) + ":" + str(int(rem * 60)).rjust(2, "0")

    def getHours(self):
        timeHeld = self.endTime - self.startTime
        return timeHeld.total_seconds() / 3600.0

    def __repr__(self):
        hoursHeld = self.getHours()
        points = self.zone.getPoints(hoursHeld)
        suffix = "" if self.complete else "+"
        hoursText = self.hoursOut(hoursHeld)
        endTimeOut = ""
        if self.complete:
            endTimeOut = self.dtOut(self.endTime)
        return self.dtOut(self.startTime).ljust(20) + endTimeOut.ljust(20) + (hoursText.rjust(6) + suffix).ljust(10) + str(points).rjust(4) + suffix.ljust(5)
            
def parseEndDate(dateStr):
    return datetime.strptime(dateStr + " 12", "%Y-%m-%d %H")

def getUser(userArg):
    if userArg:
        if userArg.isdigit():
            return User(userId=int(userArg))
        else:
            return User(userName=userArg)

currDir = os.path.dirname(os.path.abspath(__file__))
defaultFile = os.path.join(currDir, "curr_turf_data.txt")
configFileName = os.path.join(currDir, "turf_config.txt")
if not os.path.isfile(configFileName):
    sys.stderr.write("ERROR: no config file found at " + configFileName + ": please create!\n")
    sys.exit(1)

configDict = eval(open(configFileName).read())

default_user = configDict.get("username")
home_longitude = configDict.get("home_longitude")
home_latitude = configDict.get("home_latitude")

parser = argparse.ArgumentParser(description='Report turf data')
parser.add_argument('-d', '--direction', help='only show zones in a certain direction from home')
parser.add_argument('-f', '--file', default=defaultFile, help='turf data file to use')
parser.add_argument('-z', '--zonefile', help='file to store zone average data in')
parser.add_argument('-u', '--user', const=default_user, nargs="?", help='user to show data for')

args = parser.parse_args()

now = datetime.now()
tzOffset = now - datetime.utcnow()
finished = False
timeAnalysis = False
if args.file != defaultFile:
    finished = True
    now = parseEndDate(args.file[:10])

showUser = getUser(args.user)

zoneData = eval(open(args.file).read())

staticFile = os.path.join(currDir, "static_zone_data.txt")
staticData = eval(open(staticFile).read())

prevAvgData = {}
prevAvgFile = os.path.join(currDir, "prev_turf_avg.txt")
if os.path.isfile(prevAvgFile):
    prevAvgData = eval(open(prevAvgFile).read())

userIds = {}
allRulePeriods = []
rulePeriodsByZone = {}

for zoneId, takeoverInfo in zoneData.items():
    prevAvg = prevAvgData.get(zoneId)
    zone = Zone(zoneId, prevAvg, *staticData.get(zoneId))
    if not zone.matchesDirection(args.direction):
        continue
    prevDt, prevUser = None, None
    for dateStr, userId in takeoverInfo:
        user = userIds.setdefault(userId, User(userId))
        if user == prevUser:
            continue
        dt = datetime.strptime(dateStr[:-5], "%Y-%m-%dT%H:%M:%S")
        dtLocal = dt + tzOffset
        if prevDt:
            rulePeriod = RulePeriod(zone, prevUser, prevDt, dtLocal)
            if showUser is None or showUser == prevUser:
                allRulePeriods.append(rulePeriod)
            rulePeriodsByZone.setdefault(zone, []).append(rulePeriod)
        prevDt = dtLocal
        prevUser = user
  
    if prevDt is not None and (showUser is None or showUser == prevUser):
        rulePeriod = RulePeriod(zone, prevUser, prevDt, now, complete=finished)
        if showUser is None or showUser == prevUser:
            allRulePeriods.append(rulePeriod)
        rulePeriodsByZone.setdefault(zone, []).append(rulePeriod)

for zone, zonePeriods in rulePeriodsByZone.items():
    zone.setExpectedPoints(zonePeriods)

if args.zonefile:
    expectedData = {}
    for zone in rulePeriodsByZone.keys():
        expectedData[zone.zoneId] = zone.expectedPoints
        
    with open(args.zonefile, "w") as f:
        pprint(expectedData, f)


if showUser:
    allRulePeriods.sort(key=lambda rp: rp.startTime)
    for rulePeriod in allRulePeriods:
        print rulePeriod.zone, rulePeriod, rulePeriod.zone.getExpectedPointsOutput()
else:
    User.getUserInfo(userIds)
    for zone in sorted(rulePeriodsByZone.keys(), key=lambda z: z.expectedPoints, reverse=True):
        zonePeriods = rulePeriodsByZone.get(zone)
        print zone, zone.getExpectedPointsOutput()
        for rulePeriod in zonePeriods:
            print "  ", rulePeriod.user, rulePeriod
  
