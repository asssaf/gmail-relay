#!/usr/bin/env python

import sys

from email.MIMEText import MIMEText

try:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--sender", required=True, help="Message sender address")
    parser.add_argument("-s", "--subject", required=True, help="Message subject")
    parser.add_argument("-t", "--recipient", required=True, help="Message recipient")
    parser.add_argument("-b", "--body", required=True, help="Message body")
    flags = parser.parse_args()
except ImportError:
    flags = None


def create_message(sender, to, subject, message_text):
  """Create a message for an email.

  Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.

  Returns:
    the messge object.
  """
  message = MIMEText(message_text)
  message['to'] = to
  message['from'] = sender
  message['subject'] = subject
  return message

def main():
    message = create_message(flags.sender, flags.recipient, flags.subject, flags.body)
    print(message.as_string())
    sys.exit(0)

if __name__ == '__main__':
    main()
