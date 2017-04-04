# Slack client interaction..

import os, time, re, datetime, json, requests
from slackclient import SlackClient

# smartroom bot
BOT_TOKEN = "xoxb-163800060087-RyUa3ClBgGFTFVfErd47NG9R"
BOT_NAME = "smartroom"
BOT_ID = ""

# meetingroom channel
MEETING_CHANNEL_NAME = "meetingrooms"
MEETING_CHANNEL_ID = ""

# delay between reading from firehose
READ_WEBSOCKET_DELAY = 1 

# list of users and channels
users = {}

# instantiate Slack & Twilio clients
slack_client = SlackClient(BOT_TOKEN)


server_ipaddr = "http://ec2-52-221-204-189.ap-southeast-1.compute.amazonaws.com:3000"
#server_ipaddr = "http://10.91.1.158:3000"


# extract users' list
def extract_users_list():
    global users
    api_call = slack_client.api_call("users.list")
    if api_call.get('ok'):
        # retrieve all users
        members = api_call.get('members')
        for user in members:
            if 'name' in user:
                users[user.get('id')] = user.get('name').encode('utf-8')
    else:
        print("Error: Could not retrieve users' list.. ")




# main function..
if __name__ == '__main__':
    
    extract_users_list()
    #print users

    
    for userId in users:
        if users[userId] == BOT_NAME:
            BOT_ID = userId

    #slack_client.api_call("chat.postMessage", channel=U4SFP3DH6, text="Hi. How are you?", as_user=True)
    #slack_client.api_call("chat.postMessage", channel='@skjindal93', text="<@U4TPJ1S2K> says you have a meeting booked", as_user=True)

    while True:
        time.sleep(READ_WEBSOCKET_DELAY)
        resp = requests.get(server_ipaddr + '/poll')
        print resp, resp.text

        resp = json.loads(resp.text)
        
        if resp['tosend'] == 'nothing':
            continue

        for a in resp['attendees']:
            aa = a.replace("@relaxitaxi.xyz", "")
            if resp['tosend'] == 'warn':
                slack_client.api_call("chat.postMessage", channel='@'+aa, text="The meeting booked in Room::"+resp['room'].capitalize()+" at time "+str(resp['starttime']) + " will be cancelled in 5 mins if any of you do not go for the meeting.", as_user=True)
            elif resp['tosend'] == 'cancel':
                slack_client.api_call("chat.postMessage", channel='@'+aa, text="The meeting booked in Room::"+resp['room'].capitalize()+" at time "+str(resp['starttime']) +" has been cancelled.", as_user=True)




    '''
    if slack_client.rtm_connect():
        print("Bot::" + BOT_NAME + " is connected and running!")
        while True:
            slack_client.api_call("chat.postMessage", channel=channelId, text=response, as_user=True)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")

    '''


    