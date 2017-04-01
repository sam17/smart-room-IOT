import logging
import json
from flask_ask import Ask,request,session, question, statement
from flask import Flask

app = Flask(__name__)
ask = Ask(app, "/")
logging.getLogger('flask_ask').setLevel(logging.DEBUG)


@ask.launch
def launch():
    speech_text = 'Hi, I am Dumbledore. I can tell you everything aboout Rooms at Appdynamics'
    return question(speech_text).reprompt(speech_text).simple_card('DumbledoreRespone', speech_text)

@ask.intent('OccupancyIntent', mapping={'room': 'ROOM'})
def getOccupancy(room):
    if room == 'Saturn':
        speech_text = 'Room capacity is 6'
    else :
        speech_text = "Current available rooms in Tower A, App dynamics are Saturn, Mars and Jupiter"
        
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
