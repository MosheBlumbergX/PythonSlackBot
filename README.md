# PythonSlackBot
Slack Bot written in python 2.x
Worldcup, world cup 2018 python bot

# Steps:
In your broswer:
Create slack app - https://api.slack.com/apps/new , give it name and space, create. 
Add Slack APIs and App Configuration.
Choose "Bot Users" under the "Features" section. After clicking "Add a Bot User", you should choose a display name, choose a default username, and save your choices by clicking "Add Bot User".
Click on the "Install App" under the "Settings" section. The button on this page will install the App. 
Once the App is installed, it displays a bot user oauth access token for authentication as the bot user.
copy the token. 

On your terminal:

```
export SLACK_BOT_TOKEN='your bot user access token here'
pip install slackclient
```
and run the script. 
