#!/usr/bin/env python3

import os
import requests
from argparse import ArgumentParser
from configparser import RawConfigParser


def read_config(path):
    """
    Function read config file and returns RawConfigParser object.

    :param path: Path to config file
    :type: str
    :return: configparser.RawConfigParser object
    :rtype: configparser.RawConfigParser
    """

    cfg = RawConfigParser()
    if os.path.exists(path):
        cfg.read(path)
        return cfg
    else:
        # Creating 'startup_error.log' if config file cannot be open
        with open('startup_error.log', 'w') as err_file:
            err_file.write('ERROR: Cannot find "{}" file.\n'.format(path))
            raise SystemExit('ERROR: Cannot find "{}" file.'.format(path))


def get_auth(url, login, password):
    """
    Function get authentication token and user ID from Rocket.Chat.

    :param url: Rocket.Chat API login URL
    :type: str
    :param login: Rocket.Chat user login
    :type: str
    :param password: Rocket.Chat user password
    :type: str
    :return: tuple with userID and authToken
    :rtype: tuple
    """

    headers = {'Content-Type': 'application/json'}
    timeout = (1, 3)
    resp = requests.post(url, headers=headers, json={'username': login, 'password': password}, timeout=timeout)

    resp_json = resp.json()

    if resp_json['status'] == 'success':
        return resp_json['data']['userId'], resp_json['data']['authToken']
    else:
        return resp_json['status'], resp_json['error']


def send_message(url, uid, token, to, msg, subj):
    """
    Function send message to Rocket.Chat.

    :param url: Rocket.Chat API url for sending message
    :type: str
    :param uid: Rocket.Chat user ID who sending message
    :type: str
    :param token: Authentication token for sending user
    :type: str
    :param to: Message recipient - user or channel
    :type: str
    :param msg: Message text
    :type: str
    :param subj: Message subject
    :type: str
    :return: True or False
    :rtype: bool
    """

    if DEBUG:
        print('\nSending message info:')
        print('\tSending API URL: {}'.format(url))
        print('\tRecipient name: {}'.format(to))
        print('\tSending subject: {}'.format(subj))
        print('\tSending message: {}'.format(msg))

    headers = {'X-Auth-Token': token, 'X-User-Id': uid, 'Content-Type': 'application/json'}

    if to[0] not in ('@', '#'):
        raise SystemExit('ERROR: Recipient name must stars with "@" or "#" symbol.')

    text_data = """
    *{}*
    {}
    """.format(subj, msg)
    timeout = (1, 3)
    resp = requests.post(url, json={'channel': to, 'text': text_data}, headers=headers, timeout=timeout)

    resp_json = resp.json()
    if DEBUG:
        print('\tResult: {}'.format(resp_json))

    return True if resp_json['success'] else False


if __name__ == '__main__':
    # Current program version
    VERSION = '0.1alpha1'

    # Build parsers
    main_parser = ArgumentParser(description='Send messages from Zabbix to Rocket.Chat', add_help=True)
    # Main parser
    main_parser.add_argument('-v', '--version', action='version', version=VERSION, help='Print version number and exit')
    main_parser.add_argument('-c', '--config', type=str, default='zbx-rc.conf', help='Path to config file')
    main_parser.add_argument('--debug', action='store_true', help='Enable debug mode')

    # Subparsers
    subparsers = main_parser.add_subparsers(help='List of options', dest='command')
    # Authentication to Rocket.Chat
    auth_parser = subparsers.add_parser('auth', help='Authenticate to Rocket.Chat')
    auth_parser.add_argument('-u', '--username', type=str, help='Rocket.Chat username')
    auth_parser.add_argument('-p', '--password', type=str, help='Rocket.Chat password')
    # Send message
    send_parser = subparsers.add_parser('send', help='Send message to Rocket.Chat')
    send_parser.add_argument('to', type=str, help='Message recipient')
    send_parser.add_argument('subject', type=str, help='Message subject')
    send_parser.add_argument('message', type=str, help='Message body text')
    # Parse args
    args = main_parser.parse_args()

    # Debug mode marker
    DEBUG = args.debug

    # Reading config file
    config = read_config(args.config)

    for option in ('uid', 'token'):
        if not config.has_option('RCHAT', option):
            raise SystemExit('CRITICAL: Config file missing "{}" option'.format(option))

    # Rocket.Chat API connection info
    RC_PROTO = config.get('RCHAT', 'protocol', fallback='http')
    RC_SERVER = config.get('RCHAT', 'server', fallback='localhost')
    RC_PORT = config.get('RCHAT', 'port', fallback='3000')
    # Auth info from config
    RC_UID = config.get('RCHAT', 'uid')
    RC_TOKEN = config.get('RCHAT', 'token')

    API_URL = "{proto}://{server}:{port}/api/v1/".format(proto=RC_PROTO, server=RC_SERVER, port=RC_PORT)

    if DEBUG:
        print('Reading config file...')
        print('\tUID: {}'.format(RC_UID))
        print('\tToken: {}'.format(RC_TOKEN))
        print('\tAPI URL: {}'.format(API_URL))
        print('\tUID: {}'.format(RC_UID))
        print('\tToken: {}'.format(RC_TOKEN))

    # Auth
    if args.command == 'auth':
        auth_data = get_auth(API_URL + 'login', args.username, args.password)
        print("Received auth: id '{}'; token '{}'".format(auth_data[0], auth_data[1]))

    # Send message to chat
    if args.command == 'send':
        send_message(API_URL + 'chat.postMessage', RC_UID, RC_TOKEN, to=args.to, msg=args.message, subj=args.subject)
