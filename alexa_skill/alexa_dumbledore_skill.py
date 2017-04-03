import logging
import json
from flask_ask import Ask,request,session, question, statement
from flask import Flask
import requests
import datetime


app = Flask(__name__)
ask = Ask(app, "/")
logging.getLogger('flask_ask').setLevel(logging.DEBUG)


@ask.launch
def launch():
    speech_text = 'Hi, I am Dumbledore. I can tell you everything aboout Rooms at Appdynamics'
    return question(speech_text).reprompt(speech_text).simple_card('DumbledoreRespone', speech_text)

@ask.intent('BookingIntent', mapping={'room': 'ROOM', 'fromTime': 'FROMTIME', 'toTime':'TOTIME', 'team':'TEAM' })
def book(room, atTime, duration, team):
    if room == 'this':
        date = datetime.datetime.now().strftime ("%Y:%m:%dT")
        startTime = date + fromTime
        endTime = date + toTime
        resp = requests.post('http://10.91.1.158:3000/listAvailableRooms', json={"startTime": startTime, "endTime": endTime})
        available_rooms = json.loads(resp.text)
        if('saturn' in available_rooms):
            speech_text = "Not prepared for demo"
            return statement(speech_text).simple_card('DumbledoreResponse', speech_text)
        else:
            speech_text = "Sorry, Room is already booked."
            return statement(speech_text).simple_card('DumbledoreResponse', speech_text)
    else :
        date = datetime.datetime.now().strftime ("%Y:%m:%dT")
        startTime = date + fromTime
        endTime = date + toTime
        resp = requests.post('http://10.91.1.158:3000/listAvailableRooms', json={"startTime": startTime, "endTime": endTime})
        available_rooms = json.loads(resp.text)
        if(room in available_rooms):
            resp = requests.post('http://10.91.1.158:3000/bookRoom', json={"organizer": "", "invitees" : "",  "room": "Neptune", "startTime": startTime , "endTime": endTime })
            speech_text = "Booking done for" + room
            return statement(speech_text).simple_card('DumbledoreResponse', speech_text)
        else:
            speech_text = "Sorry, Room is already booked."
            return statement(speech_text).simple_card('DumbledoreResponse', speech_text)
    
    speech_text = "Sorry, I did not get all information"
    return statement(speech_text).simple_card('DumbledoreResponse', speech_text)

@ask.intent('EmptyIntent', mapping={'fromTime': 'FROMTIME', 'toTime':'TOTIME'})
def findEmtpy(fromTime, toTime):
    date = datetime.datetime.now().strftime ("%Y:%m:%dT")
    startTime = date + str(fromTime)
    endTime = date + str(toTime)
    resp = requests.post('http://192.168.43.120:3000/listAvailableRooms', json={"startTime": startTime, "endTime": endTime})
    available_rooms = json.loads(resp.text)
    print available_rooms
    speech_text = "Available Rooms are" + str(available_rooms)
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
