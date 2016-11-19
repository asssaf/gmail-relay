#!/usr/bin/env python

from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from apiclient import errors
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from oauth2client.service_account import ServiceAccountCredentials
from email.MIMEText import MIMEText
import base64
import sys

try:
    import argparse
    parser = argparse.ArgumentParser(parents=[tools.argparser])
    parser.add_argument("--auth", help="Perform auth and exit", action="store_true")
    parser.add_argument("--user_config_dir", help="Directory to read and write config files from",
                        type=str, default=os.path.join(os.path.expanduser('~'), ".gmail-relay"))
    parser.add_argument("--service_config", help="Service account json", type=str)
    parser.add_argument("--service_user", help="User account to send email as when using a service account",
                        type=str)
    flags = parser.parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-relay.json
SCOPES = 'https://www.googleapis.com/auth/gmail.send'
CLIENT_SECRET_FILE = os.path.join(flags.user_config_dir, 'client_secret.json')
CREDENTIALS_PATH= os.path.join(flags.user_config_dir, 'credentials.json')
APPLICATION_NAME = 'Gmail Relay'


def get_user_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    if not os.path.exists(flags.user_config_dir):
        os.makedirs(flags.user_config_dir)

    store = Storage(CREDENTIALS_PATH)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + CREDENTIALS_PATH)
    return credentials


def get_service_credentials():
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        flags.service_config, scopes=SCOPES)

    delegated_credentials = credentials.create_delegated(flags.service_user)
    return delegated_credentials


def send_message(service, user_id, message):
  """Send an email message.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message: Message to be sent.

  Returns:
    Sent Message.
  """
  try:
    message = (service.users().messages().send(userId=user_id, body=message)
               .execute())
    print('Message Id: %s' % message['id'])
    return message
  except errors.HttpError, error:
    print('An error occurred: %s' % error)


def main():
    if flags.service_config:
        if flags.service_user:
            print("Using a service account")
            credentials = get_service_credentials()

        else:
            print("--service_config specified without --service_user")

    elif flags.service_user:
        print("--service_user specified without --service_config")
        sys.exit(1)

    else:
        print("Using a user account")
        credentials = get_user_credentials()

    http = credentials.authorize(httplib2.Http())

    if flags.auth:
        # auth only requested so exiting
        sys.exit(0)

    service = discovery.build('gmail', 'v1', http=http)

    # as a sendmail replacement - create message from standard input
    m = sys.stdin.read()
    message = {'raw': base64.urlsafe_b64encode(m)}
    sent = send_message(service, "me", message)
    if not sent:
        sys.exit(1)

    sys.exit(0)

if __name__ == '__main__':
    main()
