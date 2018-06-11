import sys
import json
import requests
import configparser

import logbook
# from logbook import Logger, StreamHandler,TimedRotatingFileHandler

from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

from argparse import ArgumentParser

# Runtime 'storage'
auth_account = {}
auth_accounts_list = list()
auth_accounts_apps_list = list()
auth_accounts_apps_blocks_list = list()
subscribe_list = list()

# Logbook
logger = logbook.Logger('pfunc_mon_')
logger.handlers.append(logbook.FileHandler('pfunc_monitor.log', level='DEBUG'))
logger.handlers.append(logbook.StreamHandler(sys.stdout, level='INFO'))


def my_publish_callback(envelope, status):
    # Check whether request successfully completed or not
    if not status.is_error():
        pass  # Message successfully published to specified channel.
    else:
        pass  # Handle message publish error. Check 'category' property to find out possible issue
        # because of which request did fail.
        # Request can be resent using: [status retry];


class MySubscribeCallback(SubscribeCallback):
    def presence(self, pubnub, presence):
        pass  # handle incoming presence data

    @staticmethod
    def status(pubnub, status):
        if status.category == PNStatusCategory.PNUnexpectedDisconnectCategory:
            pass  # This event happens when radio / connectivity is lost

        elif status.category == PNStatusCategory.PNConnectedCategory:
            # Connect event. You can do stuff like publish, and know you'll get it.
            # Or just use the connected event to confirm you are subscribed for
            # UI / internal notifications, etc
            # pubnub.publish().channel("awesomeChannel").message("hello!!").async(my_publish_callback)
            pass

        elif status.category == PNStatusCategory.PNReconnectedCategory:
            pass
            # Happens as part of our regular operation. This event happens when
            # radio / connectivity is lost, then regained.

        elif status.category == PNStatusCategory.PNDecryptionErrorCategory:
            pass
            # Handle message decryption error. Probably client configured to
            # encrypt messages and on live data feed it received plain text.

    @staticmethod
    def message(pubnub, message):
        print('NEW MESSAGE: {}'.format(message.message))
        logger.info('LOGBOOK:INFO: NEW MESSAGE: {}'.format(message.message))
        logger.warn('LOGBOOK:WARNING: NEW MESSAGE: {}'.format(message.message))
        pass  # Handle new message stored in message.message


class PNFuncMonitor(object):

    def __init__(self):
        # INIT CONFIG FILE
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

        # READ CONFIG FILE
        self.cfg_defaults = self.config['DEFAULT']

        self.base_uri = self.cfg_defaults['api_base_uri']
        self.auth_account_id = self.cfg_defaults['auth_account_id']
        self.auth_account_token = self.cfg_defaults['auth_account_token']

        # INIT VARS
        self.auth_account = []
        self.accounts = []
        self.apps = []
        self.subscribers = {}

    @staticmethod
    def subscribe(channels, keys):
        print('subscribing now... {c}, {k}'.format(c=channels, k=keys))

        pnconfig = PNConfiguration()
        pnconfig.subscribe_key = keys[0]
        pnconfig.publish_key = keys[1]
        pnconfig.secret_key = keys[2]
        pubnub = PubNub(pnconfig)

        pubnub.add_listener(MySubscribeCallback())
        pubnub.subscribe().channels(channels).execute()

    def auth(self, auth_type=1, u=None, p=None):

        print('auth...')
        if auth_type and self.auth_account_id and self.auth_account_token:
            r = app.auth_token(self.auth_account_id, self.auth_account_token)
        else:
            r = app.auth_cred(u, p)
        return r

    def auth_token(self, auth_id, auth_token):
        print('auth_token - authenticating now. {t}'.format(t=auth_token))

        # GET CONNECTED ACCOUNTS
        headers = {'X-Session-Token': auth_token}
        r = requests.get(self.base_uri + '/api/accounts?user_id=' + auth_id, headers=headers)

        return r

    def auth_cred(self, username, password):
        print('auth_cred - authenticating now. {u}, {p}'.format(u=username, p=password))

        # AUTHENTICATE
        payload = {'email': username, 'password': password}
        headers = {'Content-Type': 'application/json'}
        r = requests.post(self.base_uri + '/api/me', data=json.dumps(payload), headers=headers)

        return r

    def get_data(self):
        headers = {'X-Session-Token': self.auth_account_token}
        r = requests.get(self.base_uri + '/api/accounts?user_id=' + self.auth_account_id, headers=headers)

        if r.status_code is 200:
            self.accounts = r.json()['result']['accounts']
            # print('accounts: {}'.format(accounts))
            for account in self.accounts:
                # print('--> --> account id: {}'.format(account['id']))
                # print('--> --> --> account: {}'.format(account))
                auth_accounts_list.append(account)

                # GET CONNECTED ACCOUNTS APPS
                headers = {'X-Session-Token': self.auth_account_token}
                r = requests.get(self.base_uri + '/api/apps?owner_id=' + str(account['id']), headers=headers)

                if r.status_code is 200:
                    resp = r.json()
                    self.apps = resp['result']
                    print('------------------------------------------------------------------------------------')
                    print('ACCOUNT: {}'.format(account['id']))
                    print('ACCOUNT APPs COUNT: {}'.format(len(self.apps)))

                    for app in self.apps:
                        print('------------------------------------------------------------------------------------')
                        # print('ACCOUNT APP: {}'.format(app))
                        auth_accounts_apps_list.append(app)

                        app_id = app['id']
                        app_name = app['name']
                        app_owner_id = app['owner_id']

                        for key in app['keys']:
                            # print('--> KEY: {}'.format(key))
                            key_id = key['id']
                            key_name = key['properties']['name']
                            key_app_id = key['app_id']
                            key_realtime_analytics_channel = key['properties']['realtime_analytics_channel']
                            publish_key = key['publish_key']
                            subscribe_key = key['subscribe_key']
                            secret_key = key['secret_key']

                            # print('App - Name: {app_name}, ID: {app_id}, OWNER: {app_owner_id}'.format(
                            #     app_name=app_name, app_id=app_id, app_owner_id=app_owner_id))

                            # print('Key - Name:{key_name}, KEY ID:{key_id}, KEY APP ID:{key_app_id}, OWNER:{app_owner_id}'
                            #       .format(key_name=key_name, key_id=key_id, key_app_id=key_app_id,
                            #               app_owner_id=app_owner_id))
                            # print('Key - sub: {subscribe_key}, pub: {publish_key}, sec: {secret_key}'
                            #       .format(subscribe_key=subscribe_key, publish_key=publish_key, secret_key=secret_key))
                            # print('KEY - CHANNELS - key_realtime_analytics_channel: {key_realtime_analytics_channel}'
                            #       .format(key_realtime_analytics_channel=key_realtime_analytics_channel))

                            # GET APPS KEY -> BLOCKS
                            headers = {'X-Session-Token': self.auth_account_token}
                            r = requests.get(self.base_uri + '/api/v1/blocks/key/' + str(key_id) + '/block', headers=headers)

                            if r.status_code is 200:
                                resp = r.json()
                                if resp['status'] is 200:
                                    blocks = resp['payload']

                                    for block in blocks:
                                        print('-- BLOCK')
                                        block_channels = []
                                        # print('-- BLOCK: {}'.format(block))
                                        block_id = block['id']
                                        block_key_id = block['key_id']
                                        block_name = block['name']
                                        block_state = block['state']
                                        block_status = block['status']
                                        block_description = block['description']
                                        block_event_handlers = block['event_handlers']

                                        for eh in block_event_handlers:
                                            eh_id = eh['id']
                                            eh_name = eh['name']
                                            eh_log_level = eh['log_level']
                                            eh_channels = eh['channels']
                                            eh_event = eh['event']
                                            eh_output = eh['output']

                                            ch01 = 'blocks-state-'+key_realtime_analytics_channel+'.'+str(block_id)
                                            ch02 = eh_channels
                                            ch03 = eh_output

                                            block_channels.append(ch01)
                                            block_channels.append(ch02)
                                            block_channels.append(ch03)

                                        # print('block_channels: {}'.format(block_channels))
                                        final_list = list(set(block_channels))
                                        # print('block_channels_final: {}'.format(final_list))

                                        print('subscribe to: {}'.format(final_list))
                                        print('subscribe with: [{}, {}, {}]'.format(subscribe_key, publish_key, secret_key))
                                        print('')

                                        self.subscribers[block['key_id']] = final_list

                                        self.subscribe(final_list, [subscribe_key, publish_key, secret_key])

                                        block_channels = []
                                        final_list = []

    def update_config(self, cfg_section, cfg_key, cfg_value):
        self.config.set(cfg_section, cfg_key, cfg_value)

        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-u", "--user", help="Username for Auth")
    parser.add_argument("-p", "--password", help="Password for Auth")

    app = PNFuncMonitor()

    auth_res = app.auth(auth_type=1)

    if auth_res.status_code is 200:
        print('Success.(0)')
        app.get_data()
    else:
        print('Authenticating using Token failed.')
        args = parser.parse_args()
        print('args: {}'.format(args))

        if args.user and args.password:
            auth_res = app.auth(0, args.user, args.password)

            if auth_res.status_code is 200:
                print('Success.(1)')
                app.update_config('DEFAULT', 'auth_account_id', str(auth_res.json()['result']['user_id']))
                app.update_config('DEFAULT', 'auth_account_token', str(auth_res.json()['result']['token']))
                app.get_data()
        else:
            print('Username & Password must be provided.')
            print('Exiting the script.')
