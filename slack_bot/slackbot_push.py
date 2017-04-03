# Slack client interaction..

import os, time, re, datetime
from slackclient import SlackClient

# smartroom bot
BOT_TOKEN = "xoxb-163800060087-7Q6YN9cy86DdKz2NHRfgSxjz"
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
    print users

    
    for userId in users:
        if users[userId] == BOT_NAME:
            BOT_ID = userId

    #slack_client.api_call("chat.postMessage", channel=U4SFP3DH6, text="Hi. How are you?", as_user=True)
    slack_client.api_call("chat.postMessage", channel='@skjindal93', text="<@U4TPJ1S2K> says you have a meeting booked", as_user=True)

    '''
    if slack_client.rtm_connect():
        print("Bot::" + BOT_NAME + " is connected and running!")
        while True:
            slack_client.api_call("chat.postMessage", channel=channelId, text=response, as_user=True)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")

    '''


    