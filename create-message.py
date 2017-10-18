#!/usr/bin/env python

import mimetypes
import sys

from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

try:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--sender", required=True, help="Message sender address")
    parser.add_argument("-s", "--subject", required=True, help="Message subject")
    parser.add_argument("-t", "--recipient", required=True, help="Message recipient")
    parser.add_argument("-b", "--body", required=True, help="Message body")
    parser.add_argument("-a", "--attach", help="File to attach")
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

def create_message_with_attachment(sender, to, subject, message_text, attachment):
  """Create a message for an email.

  Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.
    attachment: The name of the file to be attached.

  Returns:
    An object containing a base64url encoded email object.
  """
  message = MIMEMultipart()
  message['to'] = to
  message['from'] = sender
  message['subject'] = subject

  msg = MIMEText(message_text)
  message.attach(msg)

  content_type, encoding = mimetypes.guess_type(attachment)

  if content_type is None or encoding is not None:
    content_type = 'application/octet-stream'
  main_type, sub_type = content_type.split('/', 1)
  if main_type == 'text':
    fp = open(attachment, 'rb')
    msg = MIMEText(fp.read(), _subtype=sub_type)
    fp.close()
  elif main_type == 'image':
    fp = open(attachment, 'rb')
    msg = MIMEImage(fp.read(), _subtype=sub_type)
    fp.close()
  elif main_type == 'audio':
    fp = open(attachment, 'rb')
    msg = MIMEAudio(fp.read(), _subtype=sub_type)
    fp.close()
  else:
    fp = open(attachment, 'rb')
    msg = MIMEBase(main_type, sub_type)
    msg.set_payload(fp.read())
    fp.close()

  msg.add_header('Content-Disposition', 'attachment', filename=attachment)
  message.attach(msg)
  return message

def main():
    if flags.attach:
      message = create_message_with_attachment(flags.sender, flags.recipient, flags.subject, flags.body, flags.attach)
    else:
      message = create_message(flags.sender, flags.recipient, flags.subject, flags.body)

    print(message.as_string())
    sys.exit(0)

if __name__ == '__main__':
    main()
