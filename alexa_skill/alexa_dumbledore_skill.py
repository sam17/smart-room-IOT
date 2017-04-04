import logging
import json
from flask_ask import Ask,request,session, question, statement
from flask import Flask
import requests
import datetime

SERVER_IP = "http://ec2-52-221-204-189.ap-southeast-1.compute.amazonaws.com:3000/"
THIS = "Saturn"

app = Flask(__name__)
ask = Ask(app, "/")
logging.getLogger('flask_ask').setLevel(logging.DEBUG)


@ask.launch
def launch():
    speech_text = 'Hi, I am Dumbledore. I can tell you everything aboout Rooms at App Dynamics'
    return question(speech_text).reprompt(speech_text).simple_card('DumbledoreRespone', speech_text)

@ask.intent('BookingIntent', mapping={'room': 'ROOM', 'fromTime': 'FROMTIME', 'toTime':'TOTIME', 'team':'TEAM', 'date':'DATE' }, default={'date': datetime.datetime.now().strftime ("%Y-%m-%d"), 'team': 'Platform' })
def book(room, fromTime, toTime, team, date):
    if room == 'this':
        room = THIS

    startTime = date + "T" + str(fromTime)
    endTime = date + "T" + str(toTime)
    resp = requests.post(SERVER_IP+'listAvailableRooms', json={"startTime": startTime, "endTime": endTime})
    if resp.status_code !=200:
        return statement("Node Server Error, Please check node log").simple_card('DumbledoreResponse', speech_text)
    available_rooms = json.loads(resp.text)
    if(room in available_rooms):
        resp = requests.post(SERVER_IP+'bookRoom', json={"organizer": team, "invitees" : "",  "room": room, "startTime": startTime , "endTime": endTime })
        if resp.status_code !=200:
            return statement("Node Server Error, Please check node log").simple_card('DumbledoreResponse', speech_text)
        speech_text = "Booking done for " + room + " by " + str(team) + " on " + date + " at " + fromTime 
        return statement(speech_text).simple_card('DumbledoreResponse', speech_text)
    else:
        speech_text = "Sorry, Room is already booked."
        return statement(speech_text).simple_card('DumbledoreResponse', speech_text)
    
    speech_text = "Sorry, I did not get all information"
    return statement(speech_text).simple_card('DumbledoreResponse', speech_text)

@ask.intent('EmptyIntent', mapping={'fromTime': 'FROMTIME', 'toTime':'TOTIME','date':'DATE' }, default={'date': datetime.datetime.now().strftime ("%Y-%m-%d") })
def findEmtpy(fromTime, toTime, date):
    startTime = date + "T" + str(fromTime)
    endTime = date + "T" + str(toTime)
    print startTime, endTime
    resp = requests.post(SERVER_IP+'listAvailableRooms', json={"startTime": startTime, "endTime": endTime})
    if resp.status_code !=200:
        return statement("Node Server Error, Please check node log").simple_card('DumbledoreResponse', speech_text)
    available_rooms = json.loads(resp.text)
    print available_rooms
    speech_text = "Available Rooms are " + ", ".join([r.encode('utf-8') for r in available_rooms])
    return statement(speech_text).simple_card('DumbledoreResponse', speech_text)


@ask.intent('AMAZON.HelpIntent')
def help():
    speech_text = 'Ask me about occupancy only now'
    return question(speech_text).reprompt(speech_text).simple_card('DumbledoreResponse', speech_text)

@ask.session_ended
def session_ended():
    return "", 200

if __name__ == '__main__':
    app.run(debug=True)
