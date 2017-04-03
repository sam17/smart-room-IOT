# Slack client interaction..

import os, time, re, datetime
from slackclient import SlackClient

from nlpsystem import *

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
channels = {}
users_response = {}

# instantiate Slack & Twilio clients
slack_client = SlackClient(BOT_TOKEN)


# extract users' list
def extract_users_list():
    global users, users_response
    api_call = slack_client.api_call("users.list")
    if api_call.get('ok'):
        # retrieve all users
        members = api_call.get('members')
        for user in members:
            if 'name' in user:
                users[user.get('id')] = user.get('name').encode('utf-8')
                users_response[user.get('id')] = ["", datetime.datetime.now()]
    else:
        print("Error: Could not retrieve users' list.. ")


# extract channels' list
def extract_channels_list():
    global channels
    api_call = slack_client.api_call("channels.list")
    if api_call.get('ok'):
        # retrieve all channels
        chs = api_call.get('channels')
        for channel in chs:
            if 'name' in channel:
                channels[channel.get('id')] = channel.get('name').encode('utf-8')
    else:
        print("Error: Could not retrieve channels' list.. ")

 

# The Slack Real Time Messaging API is an events firehose.
# This parsing function returns None unless a message is
# directed at the Bot, based on its ID, in a channel
def parse_slack_output(slack_rtm_output): 
    output_list = slack_rtm_output
    #print output_list
    
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and "<@"+BOT_ID+">" in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'], output['channel'], output['user']
    return None, None, None


# Receives commands directed at the bot and determines if they
# are valid commands. If so, then acts on the commands. If not,
# returns back what it needs for clarification.
def handle_text(text, channelId, userId):
    print users[userId], channels[channelId], text
    
    if channelId != MEETING_CHANNEL_ID:
        response = "Sorry. Not supposed to chat here. Please direct your enquiries in the channel:: <#"+MEETING_CHANNEL_ID+">";
        slack_client.api_call("chat.postMessage", channel=channelId, text=response, as_user=True)
        return

    text = text.replace("<@"+BOT_ID+">", "")
    
    if (datetime.datetime.now() - users_response[userId][1]).total_seconds() > 300:
        users_response[userId][0] = ""
    users_response[userId][0], response = get_response(users_response[userId][0], text, "<@"+userId+">")
    users_response[userId][1] = datetime.datetime.now()
    
    response = "<@" + userId + "> " + response
    
    slack_client.api_call("chat.postMessage", channel=channelId, text=response, as_user=True)




# main function..
if __name__ == '__main__':
    extract_users_list()
    extract_channels_list()
    #init slack users in nlp-system
    init_slackusers(users)

    for userId in users:
        if users[userId] == BOT_NAME:
            BOT_ID = userId

    for channelId in channels:
        if channels[channelId] == MEETING_CHANNEL_NAME:
            MEETING_CHANNEL_ID = channelId

    
    if slack_client.rtm_connect():
        print("Bot::" + BOT_NAME + " is connected and running!")
        while True:
            text, channelId, userId = parse_slack_output(slack_client.rtm_read())
            if text and channelId and userId:
                handle_text(text, channelId, userId)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")

  


    