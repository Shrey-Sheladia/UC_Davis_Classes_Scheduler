from calendar import week
import json
import time
import time
import telebot
import pprint
from threading import Thread
from getVacancyNew import *

pp = pprint.PrettyPrinter(indent=4)


with open('Final_Sorted_Schedule.json') as json_file1:
    SCHEDULE = json.load(json_file1)

with open('userDictionary.json') as json_file2:
    userDict = json.load(json_file2)



pp.pprint(userDict)

weekDict = {
    "Curr": "Today",
    "M" : "Monday",
    "T" : "Tuesday",
    "W" : "Wednesday",
    "R" : "Thursday",
    "F" : "Friday",
    "S" : "Saturday"
}


rooms = []
halls = list(SCHEDULE.keys())

for hall in halls:
    rooms += list(SCHEDULE[hall].keys())

for i in range(len(halls)):
    halls[i] = halls[i].replace(" ", "_")



# API_KEY = "5162485703:AAFzHyu3XWOr8AJ6iAmVdt9YHC7DbxQW0YI" #! Raspberry PI
API_KEY = "5142393526:AAHHUyULXlqobU-ofPZK40pvjnigcX8lh9g" #! Sec Sys

CHAT_ID = 1376498188
bot = telebot.TeleBot(API_KEY)


def add2log(input, message):
    
    currH = str(time.strftime("%H", time.localtime()))
    currM = str(time.strftime("%M", time.localtime()))
    currS = str(time.strftime("%S", time.localtime()))

    for c in [currH, currM, currS]:
        if len(c) < 2:
            c = "0" + c
    currTime = f"{currH}:{currM}:{currS}"



    with open('lofFile.txt', 'a') as log_file:
        log_file.write(f"{currTime}:   FROM: {message.chat.username} | {input}\n")




def start_poll():  
    print("Starting:")
    global bot
    try:
        bot.polling()
    except Exception as e:
        print(str(e))
        time.sleep(6)
        print("Starting Thread Again")
        bot.stop_polling()

        thread = Thread(target=start_poll)
        thread.start()


'''
help - Get Help
get_current - Get a list of ongoing classes in the selected hall.
get_vacancy - Get a list of current vacant rooms in selected hall.
get_schedule - Get daily schedule for any room in selected hall.

'''
@bot.message_handler(commands=["start", "help"])
def start(message):
    global userDict
    if str(message.chat.id) not in userDict:
        userDict[str(message.chat.id)] = {}
        if message.chat.username:
            usrnm = message.chat.username
        else:
            usrnm = message.chat.first_name + " " + message.chat.last_name
            print("Not found")
        userDict[str(message.chat.id)]["Username"] = usrnm
        bot.send_message(CHAT_ID, f"User {usrnm} added")
        
        with open('userDictionary.json', 'w') as outfile:
            json.dump(userDict, outfile)
    userDict[str(message.chat.id)]["Username"] = message.chat.username
    text = f"Select /get_current to receive a list of all ongoing classes in the selected hall.\n\n"
    text += f"Select /get_vacancy to receive a list of all current vacant rooms in the selected hall\n\n"
    text += f"Select /get_schedule to check the daily schedule for a particular room in your selected hall.\n\n"

    bot.send_message(message.chat.id, text)
    add2log(message.text + " Start Options", message)


@bot.message_handler(commands=["get_schedule", "get_vacancy", "get_current"])
def setMode(message):
    global userDict
    if str(message.chat.id) not in userDict:
        print("New user Added")
        userDict[str(message.chat.id)] = {}
        bot.send_message(CHAT_ID, f"User {message.chat.id} added")
        userDict[str(message.chat.id)]["Username"] = message.chat.username

        with open('userDictionary.json', 'w') as outfile:
            json.dump(userDict, outfile)
    
    userDict[str(message.chat.id)]["Username"] = message.chat.username
    userDict[str(message.chat.id)]["Mode"] = message.text[5:]
    

    sendStr = "Select Hall: \n"

    for hall in halls:
        sendStr += f"/{hall} \n" 

    bot.send_message(message.chat.id, sendStr)
    add2log(message.text + " Halls sent", message)
    print("Sent options")


@bot.message_handler(commands=list(weekDict.values()))
def set_day(message):
    global weekDict
    day = list(weekDict.keys())[list(weekDict.values()).index(message.text[1:])]
    print(day)
    userDict["cDay"] = day


@bot.message_handler(commands=["set_Day"])
def send_days(message):
    global weekDict
    sendstr = ""
    for key, val in weekDict.items():
        sendstr += f"/{val}\n"

    bot.send_message(message.chat.id, sendstr)




    pass

@bot.message_handler(commands=halls)
def checkHalls(message):
    global userDict

    if str(message.chat.id) not in userDict:
        print(144)
        start(message)
        return

    hall = message.text.replace("_", " ")[1:]
    userDict[str(message.chat.id)]["Hall"] = hall

    try:
        cDay = userDict[str(message.chat.id)]["cDay"]
    except Exception:
        cDay = "Curr"
    
    try:
        cTime = userDict[str(message.chat.id)]["cTime"]
    except Exception:
        cTime = "Curr"
    
    try:
        mode = userDict[str(message.chat.id)]["Mode"]
    except:
        bot.send_message(message.chat.id, "Select Mode...")
        print(155)
        start(message)

    with open('userDictionary.json', 'w') as outfile:
            json.dump(userDict, outfile)

    if mode == "vacancy":
        sendStr = f"Vacant rooms in {hall}: \n\n\n"

        nextList, inUse = get_info(hall, cDay, cTime)
        if nextList == "Weekend":
            bot.send_message(message.chat.id, "Weekend...")
            add2log(message.text + " Weekend...", message)
            return

        if nextList:
            for room in nextList:
                if nextList[room]["Name"] != "None":
                    sendStr += f"{room}:\nEmpty till {nextList[room]['Start'].split(' ')[0]} \n"
                    sendStr += f"Course: {nextList[room]['Name']}\n\n"
                else:
                    sendStr += f"{room}:\nNo more classes today\n\n"

            bot.send_message(message.chat.id, sendStr)
            add2log(message.text + " Empty Halls sent", message)
            pp.pprint(nextList)
        else:
            bot.send_message(message.chat.id, f"No vacant rooms in {hall}")
            add2log(message.text + f"No vacant rooms in {hall}", message)
            print(f"No vacant rooms in {hall}")

    elif mode == "schedule":
        roomSelect = f"Select room for {hall}: \n"

        rooms = list(SCHEDULE[hall].keys())
        for room in rooms:
            roomSelect += f"/{room} \n" 

        bot.send_message(message.chat.id, roomSelect)
        add2log(message.text + f"Rooms sent - Schedule", message)

    elif mode == "current":

        nextList, inUse = get_info(hall, cDay, cTime)

        if nextList == "Weekend":
            bot.send_message(message.chat.id, "Weekend...")
            add2log(message.text + " Weekend...", message)
            return

        if inUse:
            sendStr = f"Ongoing classes in {hall}: \n\n\n"

            for room in inUse:
                sendStr += f"{room}: {inUse[room]['Name']}\n Timing: {inUse[room]['Timing']}\n\n"
            bot.send_message(message.chat.id, sendStr)
            add2log(message.text + " Ongoing classes sent", message)
            pp.pprint(inUse)

        else:
            bot.send_message(message.chat.id, f"No ongoing classes in {hall}")
            add2log(message.text + f"No ongoing classes in {hall}", message)
            print(f"No ongoing classes in {hall}")



    else:
        print(mode)

@bot.message_handler(func=check_time)
def trial(message):
    selectedTime = message.text.lower()[5:]
    hrs, mins = selectedTime.split(":")[0].strip(), selectedTime.split(":")[1].strip()
    try:
        _, __ = int(hrs), int(mins)
    except Exception:
        bot.send_message(message.chat.id, f"Incorrent Time Format")

    if (0 <= int(hrs) and int(hrs) <= 24) and (0 <= int(mins) and int(mins) <= 60):
        

    print(hrs, mins)

@bot.message_handler(commands=rooms)
def sendReply(message):
    try:
        if userDict[str(message.chat.id)]["Mode"] != "schedule":
            bot.send_message(message.chat.id, f"Room cannot be selected when not in '/get_schedule' mode. Please click on the command and proceed ahead.")
            add2log("Room cannot be selected when not in '/get_schedule' mode. Please click on the command and proceed ahead.", message)
            return
    except:
        print(231)
        start(message)
        return
        
    hall = userDict[str(message.chat.id)]["Hall"]
    with open('userDictionary.json', 'w') as outfile:
            json.dump(userDict, outfile)

    selected_room = message.text[1:]
    print(f"{hall}: Room {selected_room}")

    try:
        roomAvailibity = SCHEDULE[hall][selected_room]
        pp.pprint(roomAvailibity)
    except KeyError as e:
        print(e)
        bot.send_message(message.chat.id, f"Room {selected_room} not found in {hall}")
        add2log(f"Room {selected_room} not found in {hall}", message)
        return 

    

    schedule_send = f"Schedule for {hall} - {selected_room}: \n\n\n"


    for d in roomAvailibity:
        schedule_send += f"{weekDict[d]}:\n"
        if roomAvailibity[d]:
            for timing in roomAvailibity[d]:
                schedule_send += f"{timing} :- {(roomAvailibity[d][timing]).split(' | ')[1]} \n"
        else:
            schedule_send += "No Classes\n"
        
        schedule_send += "\n"  

    bot.send_message(message.chat.id, schedule_send)
    add2log(message.text, message)


bot.send_message(CHAT_ID, "Starting")
bot.send_message(CHAT_ID, "/get_schedule, /get_vacancy, /get_current")

bot.polling()
# thread = Thread(target=start_poll)
# thread.start()


