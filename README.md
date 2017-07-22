# shsmd: Self Hosted Secure Messaging Daemon

## Overview

How hard is it to develop a secure, client-server style messaging system that supports multiple devices per user and multiple recipients per message?

This is my attempt to find out! 

This repository contains a very crude (STILL IN EARLY DEVELOPMENT) CLI client.

## Installation

### Install necessary OS packages:
  * Fedora:
    * `dnf install redhat-rpm-config python3-devel python-virtualenvwrapper`
  
### Python setup (Python >=3.5 ONLY)
  * `git clone https://github.com/sinner-/shsmc`
  * `cd shsmc`
  * `mkvirtualenv -p python3.5 shsmc`
  * `python setup.py install`

### Basic run example
```
#!/usr/bin/env bash
for identity in `echo 'alice bob sina'`;
do
    rm -rf $identity
    mkdir -p $identity/contacts
    cat <<EOF > $identity/config.ini
[general]
debug=False
api_url=http://localhost:5000/api/v1.0
key_dir=$identity
username=$identity
EOF
    shsmc-cli --config-dir $identity --register
    shsmc-cli --config-dir $identity --add-device
    shsmc-cli --config-dir $identity --add-key
done

shsmc-cli --config-dir sina --add-contact bob
shsmc-cli --config-dir sina --add-contact alice

shsmc-cli --config-dir bob --add-contact sina
shsmc-cli --config-dir bob --add-contact alice

shsmc-cli --config-dir alice --add-contact bob
shsmc-cli --config-dir alice --add-contact sina

shsmc-cli --config-dir sina --send-message --message "hello alice & bob from sina" --to alice,bob
shsmc-cli --config-dir bob --send-message --message "hello alice & sina from bob" --to alice,sina
shsmc-cli --config-dir alice --send-message --message "hello bob & sina from alice" --to bob,sina

echo "Messages for Bob:"
echo "-----------------------------"
shsmc-cli --config-dir bob --get-messages
echo "-----------------------------"

echo "Messages for Sina:"
echo "-----------------------------"
shsmc-cli --config-dir sina --get-messages
echo "-----------------------------"

echo "Messages for Alice:"
echo "-----------------------------"
shsmc-cli --config-dir alice --get-messages
echo "-----------------------------"
```
