# gmail-relay
Simple MTA that uses gmail API using a client OAuth token to send mail.

gmail-relay.py is a python script based on [google-api-python-client](https://github.com/google/google-api-python-client
) to send a message as a sendmail replacement.

gmail-relay.py doesn't do queueing so if you don't want to lose messages you can use a queueing sendmail (such as
nullmailer's nullmailer-inject), then use the provided gmail-relay-process-queue script to process the queue dir.

You can run gmail-relay-process-queue periodically or through systemd triggers to make sure that queued
mail is retried and sent once the failure is resolved.

# Why?
This allows you to use a token instead of writing down your google account password in a config file.
It's also more elegant since the token is only authorized to send email. It can't read or do any other
changes.

In case you create multiple tokens for use by different machine you can easily expire specific tokens
that are not needed anymore without affecting the rest of the machines.

# How?
In order to use gmail-relay the Gmail API needs to be enabled and authorized.
See https://developers.google.com/gmail/api/quickstart/python for instructions.

Authorization happens through the browser so (usually) needs to be run as a normal user.
Once you create an OAuth client ID and download the JSON, rename it `client_secret.json`
and place it in a user accessible directory.

By default gmail-relay.py will look in `~/.gmail-relay/client_secret.json`, but if you use a different
directory you can pass the --config=myconfigdir argument.

gmail-relay.py depends on `google-api-python-client` and `oauth2client`, so run `pip3 install -r requirements.txt` to make sure you have those installed.

Then, run:

    $ gmail-relay.py --auth --config=~/.gmail-relay

You can now send RFC 2822 compliant messages by passing them to gmail-relay.py through stdin

    $ cat message | gmail-relay.py --config=~/.gmail-relay

If you wish to have gmail-relay run as a system service (e.g. by systemd) you'll need to
copy the generated `credentials.json` file to `/etc/gmail-relay/` (and chmod it 600).

### gmail-relay.py
Sends a message passed to it in stdin.
gmail-relay.py doesn't queue. For queuing you can use something like `gmail-relay-process-queue` (see below)

If it doesn't find an existing credentials file under `CONFIG_DIR/credentials.json`, it will attempt to
authorize through the browser. Authorization requires `client_secret.json` to be present in `CONFIG_DIR`.

Pass `--auth` to run autohrization only and exit

Pass `--config=myconfigdir` to use a custom config directory instead of the default `~/.gmail-relay`

### gmail-relay-process-queue
This bash script will go over an existing queue directory, such as nullmailer's `/var/nullmailer/queue`, and
will send each mail item it finds under the directory using `gmail-relay.py`.
It expects the credentials.json for gmail-relay.py to be under `/etc/gmail-relay`

    $ gmail-relay-process-queue /var/nullmailer/queue

### systemd
A timer and path trigger are provided for systemd. This path trigger will execute `gmail-relay-process-queue`
immediately when a new mail is queued, while the timer executes it periodically in case of a failure in a
previous send.

    $ systemctl start gmail-relay.timer
    $ systemctl start gmail-relay.path
    $ systemctl start gmail-relay.service

If you wish them to start after reboot, enable the triggers:

    $ systemctl enable gmail-relay.timer
    $ systemctl enable gmail.relay.path

# Install
## Gentoo
ebuilds are provided at https://github.com/asssaf/portage/tree/master/mail-mta/gmail-relay
