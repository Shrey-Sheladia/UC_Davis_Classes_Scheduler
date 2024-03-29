import json
import time
import time
import pprint
from threading import Thread

pp = pprint.PrettyPrinter(indent=2)

try:
    with open('Final/Final_Sorted_Schedule.json') as json_file1:
        SCHEDULE = json.load(json_file1)
except:
    with open('Final_Sorted_Schedule.json') as json_file1:
        SCHEDULE = json.load(json_file1)


def convert24(str1):
    if str1[-2:] == "AM" and str1[:2] == "12":
        return "00" + str1[2:-2]

    elif str1[-2:] == "AM":
        return str1[:-2]

    elif str1[-2:] == "PM" and str1[:2] == "12":
        return str1[:-2]

    else:
        return str(int(str1[:2]) + 12) + str1[2:8]


def formatAMPM(startI, endI, m):
    if len(startI) < 5:
        startI = "0" + startI
    if len(endI) < 5:
        endI = "0" + endI

    start, end = startI + ":00 " + m, endI + ":00 " + m

    start24, end24 = convert24(start), convert24(end)
    startH, endH = start24.split(":")[0], end24.split(":")[0]

    # print(startH, endH)
    if startH <= endH:
        return int(start24.strip().replace(":", "")), int(end24.strip().replace(":", ""))

    else:
        start, end = startI + ":00" + " AM", endI + ":00 " + m
        start24, end24 = convert24(start), convert24(end)

        return int(start24.strip().replace(":", "")), int(end24.strip().replace(":", ""))


def convertTimetoInt(timeList):
    timeDict = {}
    for cTime in timeList:
        if cTime == "TBA":
            continue
        cols = cTime.split(" ")
        start, end, m = cols[0], cols[2], cols[3]
        start24, end24 = formatAMPM(start, end, m)

        timeDict[start24] = {
            "End": end24,
            "Original": cTime
        }

    return timeDict
    pass


def getCurrTime():
    curr = time.localtime()
    curr24 = int(time.strftime("%H%M%S", curr))
    currDay = time.strftime("%A", curr)
    if currDay == "Thursday":
        currDay = "R"
    elif currDay == "Sunday":
        currDay = "Sunday"
    else:
        currDay = currDay[0]

    return curr24, currDay


def checkAvailibilty(current, hallDict, inUse=False):
    emptyRooms = []
    inUse = []

    for room in hallDict:
        roomMT = True
        startingTimes = sorted(list(hallDict[room].keys()))

        for index, startTime in enumerate(startingTimes):
            if startTime <= current <= hallDict[room][startTime]["End"]:
                inUse.append((room,hallDict[room][startTime]["Original"] ))
                roomMT = False

        if roomMT:
            emptyRooms.append(room)

    return emptyRooms, inUse


def getNext(current, AvailableRooms, hallInfo, hallName, currDay):
    global SCHEDULE

    nextClass = {}

    for MT_Room in AvailableRooms:
        next = None
        sched = hallInfo[MT_Room]

        for start in sched:
            if current < start:
                next = start
                break

        if next:
            nextStart = hallInfo[MT_Room][next]["Original"]
            nextName = SCHEDULE[hallName][MT_Room][currDay][nextStart]
        else:
            nextStart = "No Classes Left Today"
            nextName = "None"

        nextClass[MT_Room] = {
            "Start": nextStart,
            "Name": nextName
        }

    return nextClass


def getCurr(current, AvailableRooms, hallInfo, hallName, currDay):
    global SCHEDULE

    CurrentClasses = {}

    for (room, original) in AvailableRooms:
        sched = hallInfo[room]
        ongoingClassTime = None

        schedList = list(sched.keys())

        
        if ongoingClassTime == None:
            ongoingClass = SCHEDULE[hallName][room][currDay][original]

            CurrentClasses[room] = {
                "Name" : ongoingClass,
                "Timing": original
            }

    return CurrentClasses

def check_time(command):
    print(command.text)
    if "time:" in command.text.lower():
        selectedTime = command.text.lower()[5:]
        hrs, mins = selectedTime.split(":")[0].strip(), selectedTime.split(":")[1].strip()

        print(hrs, mins)

        return True


def get_info(selectedHall, cDay, cTime):
    roomScheduleInfo = {}

    current, currDay = getCurrTime()
    if cDay != "Curr":
        currDay = cDay

    if cTime != "Curr":
        current = cTime
    
    print(current, type(current))
    
    if currDay == "Sunday":
    
        return "Weekend", {}

    for room in SCHEDULE[selectedHall]:
        todaysSchedule = (SCHEDULE[selectedHall][room][currDay])

        classTimes = list(todaysSchedule.keys())
        roomScheduleInfo[room] = convertTimetoInt(classTimes)

    emptyRooms, inUse = checkAvailibilty(current, roomScheduleInfo)

    nextList = getNext(current, emptyRooms, roomScheduleInfo, selectedHall, currDay)
    CurrList = getCurr(current, inUse, roomScheduleInfo, selectedHall, currDay)
    
    # print("\n\n\n\n\n________________________________________________________________________")
    # pp.pprint(nextList)

    # return {}, {}
    return nextList, CurrList


# get_info("Wright Hall")
# (get_info("Olson Hall"))
print(getCurrTime())
