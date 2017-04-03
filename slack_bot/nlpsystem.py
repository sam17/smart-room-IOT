import os, time, re
import dateutil.parser, datetime
import requests, json

from wit import Wit
from webcolors import *


slackusers={}
wit_client = Wit(access_token='NR62PZJK63ROIYYXBZ2OSUVVR76ZVIIQ')


server_ipaddr = ""
light_ipaddr = ""


def init_slackusers(users):
	global slackusers
	slackusers = users


def get_response(prev_response, text, userId):
	if 'light' in text:
		if light(text):
			response = "Done"
			return prev_response, response

	users, text = get_users(text)
	prev_response, response = reactions(prev_response, text)

	if (response != None):
		return prev_response, response

	
	if any(key in (prev_response+text).lower() for key in ['book', 'room']):
	    prev_response, response = book_room(prev_response, text, users, userId)

	else:
	    response = "Sorry. I didn't understand. Please be more clear."

	return prev_response, response



#LED lightings
def light(text):
	color = ''

	intensity = {'dim': '#111111', 'bright': '#ffffff', 'medium': '#888888'}

	words = re.findall(r"[\w']+", text.lower())
	for w in words:
		if w in html4_names_to_hex:
			color = html4_names_to_hex[w]
			break
		if w in css3_names_to_hex:
			color = css3_names_to_hex[w]
			break

	if color == '':
		for w in words:
			if w in intensity:
				color = intensity[w]
				break;

	if color == '':
		HEX_COLOR_RE=re.compile(r'^#([a-fA-F0-9]{3}|[a-fA-F0-9]{6})$')
		for w in words:
			if HEX_COLOR_RE.match(w) != None:
				color = HEX_COLOR_RE.match(w).groups()[0]
				break;


	if color != '':
		(r,g,b) = hex_to_rgb(color)
		requests.get("http://" + light_ipaddr + "/" + str(r) + "/" + str(g) + "/" + str(b) + "/")
		return True

	return False



def reactions(prev_response, text):
	reactions = re.findall(":.*:", text)
	for r in reactions:
		text = text.replace(r,"")

	words = re.findall(r"[\w']+", text)
	if len(words) == 0 and len(reactions) > 0:
		return prev_response, " ".join(reactions)
	elif len(words) <= 1 or (len(words) == 2 and any(g in text for g in ['good', 'gud', 'gd', 'thank'])):
		return greeting(prev_response, text.lower())
	else:
		return prev_response, None



def greeting (prev_response, text):

	if prev_response == "" or any(greet in text for greet in ['hi', 'hello', 'up', 'yo', 'morn', 'eve', 'aft']):
		response = "Hi. What can I do for you?"
		return response, response

	elif any(bye in text for bye in ['bye', 'cancel', 'leave', 'night', 'nyt', 'nite', 'n8', 'thank']):
		return "", "Okay. Have a nice day. :slightly_smiling_face:"

	elif prev_response == "Hi. What can I do for you?":
		response = "Sorry. Didn't get you. What is it you want?"
		return response, response

	else:
		return prev_response, None



def book_room(prev_response, text, users, userId):

	usrs, prev_response = get_users(prev_response)
	users = list(set(users+usrs))

	date_from, time_from, date_to, time_to = get_dateTime(text)
	if time_to == '':
		if time_from != '':
			_, _, date_to, time_to = get_dateTime(prev_response)
		else :
			date_from, time_from, date_to, time_to = get_dateTime(prev_response)
	elif time_from == '':
		date_from, time_from, _, _ = get_dateTime(prev_response)

	rooms = get_rooms(text.lower())
	if len(rooms) == 0:
		rooms = get_rooms(prev_response.lower())


	if time_from == '':
		if time_to != '':
			prev_response = "book rooms " + " ".join(rooms) + " time to " + date_to + " " + time_to + " users " + " ".join(users)
			response = "Please specify the date and time from when you want to book the room."
		else:
			prev_response = "book rooms " + " ".join(rooms) + " users " + " ".join(users)
			response = "Please specify the start and end date-time when you want to book the room."
		return prev_response, response
	elif time_to == '':
		prev_response = "book rooms " + " ".join(rooms) + " time from " + date_from + " " + time_from + " users " + " ".join(users)
		response = "Please specify the date and time till when you want to book the room (use to/till before time)."
		return prev_response, response

	elif len(rooms) == 0:
		rooms = get_available_rooms([], date_from, time_from, date_to, time_to)
		prev_response = "book " + " time from " + date_from + " " + time_from + "to" + date_to + " " + time_to + " users " + " ".join(users)

		if len(rooms) == 0:
			response = "No rooms are available from " + date_from + "::" + time_from + " to " + date_to + "::" + time_to + ". Please choose a different time or date."
		else:
			response = "Which room do you want to book? \nRooms available from " + date_from + "::" + time_from + " to " + date_to + "::" + time_to + " --> " + " ".join(rooms)
		return prev_response, response

	else:
		available_rooms = get_available_rooms(rooms, date_from, time_from, date_to, time_to)

		if isinstance(available_rooms, str):
			response = "Room " + available_rooms + " is booked for you from " + date_from + "::" + time_from + " to " + date_to + "::" + time_to + "."
			if len(users) > 0:
				response = response + "\nInvited people are :: " + " ".join(users)
			prev_response = ""
			
			# post request to server
			resp = requests.post('http://' + server_ipaddr + '/bookRoom', json={"organizer": slackusers[userId[2:-1]]+"@relaxitaxi.xyz", "room": available_rooms, "invitees": ",".join([slackusers[u[2:-1]]+"@relaxitaxi.xyz" for u in users]), "startTime": date_from+"T"+time_from, "endTime": date_to+"T"+time_to})

			return prev_response, response
		
		else:
			prev_response = "book time from " + date_from + " " + time_from + "to" + date_to + " " + time_to + " users " + " ".join(users)
			if len(available_rooms) == 0:
				response = "No rooms are available from " + date_from + "::" + time_from + " to " + date_to + "::" + time_to + ". Please choose a different time or date."
			else:
				response = "The room you wanted to book is not available. \nRooms available from " + date_from + "::" + time_from + " to " + date_to + "::" + time_to + " --> " + " ".join(available_rooms) + "\nWhich room do you want to book? "
			return prev_response, response



def get_dateTime(text):
	if len(text.strip()) == 0:
		return '', '', '', ''
	resp = wit_client.message(text)

	entities = resp['entities']
	if 'datetime' not in entities:
		return '', '', '', ''

	dtString = entities['datetime'][0]
	dt_from = None
	dt_to = None
	
	if 'value' in dtString:
		dtString = dtString['value']
		dt_from = dateutil.parser.parse(dtString).strftime("%Y-%m-%d %H:%M").split(" ")
		if dt_from[1] == '00:00':
			return '', '', '', ''
		return dt_from[0], dt_from[1], '', ''

	if 'from' in dtString:
		dt_from = dateutil.parser.parse(dtString['from']['value'])
	
	if 'to' in dtString:
		dt_to = dateutil.parser.parse(dtString['to']['value']).strftime("%M")

		if str((int(dt_to)-1) % 60) not in text :
			dt_to = (dateutil.parser.parse(dtString['to']['value']) - datetime.timedelta(hours=1))
		else:
			dt_to = (dateutil.parser.parse(dtString['to']['value']) - datetime.timedelta(minutes=1))
	
	if dt_to == None and dt_from == None:
		return '', '', '', ''
	elif dt_to == None:
		date = dt_from.strftime("%Y-%m-%d")
		return date, dt_from.strftime("%H:%M"), '', ''
	elif dt_from == None:
		date = dt_to.strftime("%Y-%m-%d")
		return '', '', date, dt_to.strftime("%H:%M")
	elif dt_to < dt_from:
		date = dt_from.strftime("%Y-%m-%d")
		return date, dt_from.strftime("%H:%M"), date, dt_to.strftime("%H:%M")
	else:
		date = dt_to.strftime("%Y-%m-%d")
		return date, dt_from.strftime("%H:%M"), date, dt_to.strftime("%H:%M")


#get meeting room from text
def get_available_rooms(rooms, date_from, time_from, date_to, time_to):
	
	#post request to server..
	resp = requests.post('http://' + server_ipaddr + '/listAvailableRooms', json={"startTime": date_from+"T"+time_from, "endTime": date_to+"T"+time_to})
	
	available_rooms = json.loads(resp.text)

	result = [r.encode('utf-8') for r in available_rooms if r in rooms]

	if len(result)==0:
		return available_rooms
	else:
		return result[0]


def get_rooms(text):
	rooms = ['Mercury', 'Venus', 'Earth', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto']
	result = [r.capitalize() for r in rooms if r.lower() in text]

	return result


#get mentioned users in text..
def get_users(text):
	users = re.findall("<@\w*>", text)
	for u in users:
		text = text.replace(u,"")
	return users, text


