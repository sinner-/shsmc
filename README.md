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
    shsmc --configdir $identity --action register
    shsmc --configdir $identity --action add-device
    shsmc --configdir $identity --action add-key
done

shsmc --configdir sina --action add-contact --contact bob
shsmc --configdir sina --action add-contact --contact alice

shsmc --configdir bob --action add-contact --contact sina
shsmc --configdir bob --action add-contact --contact alice

shsmc --configdir alice --action add-contact --contact bob
shsmc --configdir alice --action add-contact --contact sina

shsmc --configdir sina --action send-message --msg "hello alice & bob from sina" --recipients alice,bob
shsmc --configdir bob --action send-message --msg "hello alice & sina from bob" --recipients alice,sina
shsmc --configdir alice --action send-message --msg "hello bob & sina from alice" --recipients bob,sina

echo "Messages for Bob:"
echo "-----------------------------"
shsmc --configdir bob --action get-messages
echo "-----------------------------"

echo "Messages for Sina:"
echo "-----------------------------"
shsmc --configdir sina --action get-messages
echo "-----------------------------"

echo "Messages for Alice:"
echo "-----------------------------"
shsmc --configdir alice --action get-messages
echo "-----------------------------"
```
