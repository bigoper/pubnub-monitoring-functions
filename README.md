# pubnub-monitoring-functions
Real-time monitoring for PubNub functions

> The script will gather information on your account and use it to generate groups of channels/keys that later we'll subscribe to.

## Requirements
- python 3
- requests
- pubnub

## Installation
1. in the project's root folder, execute the following

```pip install -r requirements.txt```

## Usage
> As default, the script will look for your 'token' in the config file and if exists will try to authenticate with it.
If failes to authenticate it will ask you for your 'username' and 'password'.

1. Execute the script (command line)

- ```python app.py --user=PubNubAccountEmailAddress --password='ThisIsMyPassword'```
- ```python app.py```
> using your login credentials is needed if your 'token' is expired.

Executing the script will trigger the followings
- Connect to PubNub via the [REST API][0]
- Retrieve account info
- Subscribe to all of the channels with respective keys.
- Attach an EventListner to every subscriber with 'SubscribeCallback'
- The callback will notify on the following changes/updates [[PubNub events][1] (presence, status, message)]

## Features
The script will automatically connect to all of the resources (accounts) that it has been granted permissions to.
Meaning that you'll be able to monitor other account's functions as well.

## Testing
1. Login to you [admin][2] and select an APP -> KEY_SET -> FUNCTIONS -> EVENT HANDLER
2. Publish a message (any my message) using the console and look for the update in the script output
3. You can test the 'function status' updates, restart your 'module' (in the admin page) and look for the updates in the script output.
> the script also writes the output to a log file.

## Integration
1. Simple integration would be to send updates to a ['Slack'][3] channel or ['Loggly'][4].

[0]: https://www.pubnub.com/docs/blocks/restful-api
[1]: https://www.pubnub.com/docs/python/pubnub-python-sdk
[2]: https://admin.pubnub.com
[3]: https://github.com/slackapi/python-slackclient
[4]: https://www.loggly.com/docs/python-http/
