#!/usr/bin/env python3

import httplib2
import os

from apiclient import discovery
from apiclient import errors
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import base64
import sys

try:
    import argparse
    parser = argparse.ArgumentParser(parents=[tools.argparser])
    parser.add_argument("--auth", help="Perform auth and exit", action="store_true")
    parser.add_argument("--config", help="Directory to read and write config files from",
                        type=str, default=os.path.join(os.path.expanduser('~'), ".gmail-relay"))
    flags = parser.parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-relay.json
SCOPES = 'https://www.googleapis.com/auth/gmail.send'
CLIENT_SECRET_FILE = os.path.join(flags.config, 'client_secret.json')
CREDENTIALS_PATH= os.path.join(flags.config, 'credentials.json')
APPLICATION_NAME = 'Gmail Relay'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    if not os.path.exists(flags.config):
        os.makedirs(flags.config)

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
  except errors.HttpError as error:
    print('An error occurred: %s' % error)


def main():
    """Shows basic usage of the Gmail API.

    Creates a Gmail API service object and outputs a list of label names
    of the user's Gmail account.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())

    if flags.auth:
        # auth only requested so exiting
        sys.exit(0)

    service = discovery.build('gmail', 'v1', http=http)

    # as a sendmail replacement - create message from standard input
    m = sys.stdin.read()
    message = {'raw': base64.urlsafe_b64encode(m.encode("utf-8")).decode("utf-8")}
    sent = send_message(service, "me", message)
    if not sent:
        sys.exit(1)

    sys.exit(0)

if __name__ == '__main__':
    main()
