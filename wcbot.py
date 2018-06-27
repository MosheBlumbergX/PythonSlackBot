import os
import time
import re
import requests
import sys
import json
from slackclient import SlackClient
import base64


# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "do"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"



def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    #default_response = "Not sure what you mean. Try *{}*.".format(EXAMPLE_COMMAND)
    default_response = "accepted commands are:\nnow\ntoday (for games today)\nteam <FIFA CODE> - example: team ENG\n"
    
    # Finds and executes the given command, filling in response
    response = None
    # This is where you start to implement more commands!
    if command.startswith(EXAMPLE_COMMAND):
        response = "Sure...write some more code then I can do that!"

    if command == 'now':
        x = check()
        response = x

    if command == 'today':
        x = gamestoday()
        response = x

    if command.startswith('team'):
        x = team(command)
        response = x


    # Sends the response back to the channel
    slack_client.api_call(
    "chat.postMessage",
    channel=channel,
    text=response  or default_response
)



'''
This is functions area  
'''

def check():
    currenturl = 'http://worldcup.sfg.io/matches/current'
    response = requests.request("GET", currenturl)
    bb = json.loads(response.text)
    if len(bb) > 0:
        x = current()
        return x
    else:
        response = 'no current game'
        return response

def current():
    list =[]
    currenturl = 'http://worldcup.sfg.io/matches/current'
    response = requests.request("GET", currenturl)
    bb = json.loads(response.text)
    l = 0
    while l < len(bb):
        home_teamname = (bb[l]['home_team']['country']) 
        home_teamscore = (bb[l]['home_team']['goals'])
        home=(home_teamname + " " + str(home_teamscore))
        away_teammname = (bb[l]['away_team']['country']) 
        away_teamscore = (bb[l]['away_team']['goals'])
        away=(away_teammname + " " + str(away_teamscore))
        time=(bb[l]['time'])
        response = home + " " + away + ' Minute: ' + str(time)
        list.append(response)
        l += 1
    response = '\n'.join(list)
    return response

def gamestoday():
    list = []
    gamestoday = 'http://worldcup.sfg.io/matches/today'
    response = requests.request("GET", gamestoday)
    bb = json.loads(response.text)
    l = 0
    while l < len(bb):
        h = (bb[l]['home_team']['country'])
        a = (bb[l]['away_team']['country']) 
        datetime = (bb[l]['datetime'])
        s =(bb[l]['status'])
        if (bb[l]['status']) != 'future':
            hg = (bb[l]['home_team']['goals'])
            ag = (bb[l]['away_team']['goals'])
            response = ('status: ' + s +  ',' + ' ' + h + ' vs ' + a + ' ,Final score: ' + str(hg) +  ':' + str(ag))
            list.append(response)
        else:
            response = ('status: ' + s +  ',' + ' ' + h + ' vs ' + a + '    when:   ' + str(datetime) )
            list.append(response)
        l += 1
        #for i in list:
        #    print(i)
    response = '\n'.join(list)
    return response

def team_results(country):
    check = country
    if check.startswith('team'):
        list = []
        team = check.split(' ')[1]
        url = 'http://worldcup.sfg.io/matches/country?fifa_code='
        urlfull = url + team
        response = requests.request("GET", urlfull)
        bb = json.loads(response.text)
        l = 0
        while l < len(bb):
            s =(bb[l]['status'])
            h =(bb[l]['home_team']['country'])
            a = (bb[l]['away_team']['country'])
            if (bb[l]['status']) != 'future':
                hg = (bb[l]['home_team']['goals'])
                ag = (bb[l]['away_team']['goals'])
                response = ('status: ' + s +  ',' + ' ' + h + ' vs ' + a + ' ,Final score: ' + str(hg) +  ':' + str(ag))
                list.append(response)
            else:
                response = ('status: ' + s +  ',' + ' ' + h + ' vs ' + a)
                list.append(response)
            l += 1
        #for i in list:
        #    print(i)
        response = '\n'.join(list)
        return response
    else:
        response = 'no team'
        return response


def countries():
    list = []
    list2 = []
    url ='http://worldcup.sfg.io/teams/'
    response = requests.request("GET", url)
    bb = json.loads(response.text)
    l = 0
    while l < len(bb):
        country = (bb[l]['country'])
        code = (bb[l]['fifa_code'])
        response = country + ', Use this code: ' + code
        list.append(response)
        list2.append(code)
        l += 1
    response = '\n'.join(list)
    res = list2
    return response, res



def team(country):
    check = country
    if check.startswith('team'):
        list = []
        team = check.split(' ')[1]
        team = team.upper()
        #print(team)
        c = countries()
        if team in c[1]:
            x = team_results(check)
            return x
        else: 
            x = ('Here is a list of countries you can use:\n Use: team <FIFA CODE> - example: team ENG\n' + str(c[0]))
            return x 



'''
This is functions area  ^^^^^
'''

if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")
