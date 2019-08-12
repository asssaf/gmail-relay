FROM alpine

RUN apk --no-cache add python3
RUN pip3 install google-api-python-client oauth2client

ADD gmail-relay.py /
ADD create-message.py /
