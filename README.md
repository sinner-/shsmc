# shsmd: Self Hosted Secure Messaging Daemon

## Overview

How hard is it to develop a secure, client-server style messaging system that supports multiple devices per user and multiple recipients per message?

This is my attempt to find out! 

This repository contains a very crude (STILL IN EARLY DEVELOPMENT) CLI client.

## Installation

### Install necessary OS packages:
  * Fedora:
    * `dnf install redhat-rpm-config python2-devel curl-devel libsodium-devel`
  
### Python setup
  * `git clone https://github.com/sinner-/shsmc`
  * `virtualenv -p /usr/bin/python2.7 shsmc`
  * `cd shsmc`
  * `source bin/activate`
  * `pip install -r requirements.txt`

### Basic run example
```
rm -rf client1
rm -rf client2
rm -rf client3
mkdir -p client1/contacts
mkdir -p client2/contacts
mkdir -p client3/contacts

./shsmc.py --server "http://localhost:5000/api/v1.0" --username sina --keydir client1 --action register
./shsmc.py --server "http://localhost:5000/api/v1.0" --username sina --keydir client1 --action add-device
./shsmc.py --server "http://localhost:5000/api/v1.0" --username sina --keydir client1 --action add-key

./shsmc.py --server "http://localhost:5000/api/v1.0" --username bob --keydir client2 --action register
./shsmc.py --server "http://localhost:5000/api/v1.0" --username bob --keydir client2 --action add-device
./shsmc.py --server "http://localhost:5000/api/v1.0" --username bob --keydir client2 --action add-key

./shsmc.py --server "http://localhost:5000/api/v1.0" --username alice --keydir client3 --action register
./shsmc.py --server "http://localhost:5000/api/v1.0" --username alice --keydir client3 --action add-device
./shsmc.py --server "http://localhost:5000/api/v1.0" --username alice --keydir client3 --action add-key

./shsmc.py --server "http://localhost:5000/api/v1.0" --username sina --keydir client1 --action add-contact --contact bob
./shsmc.py --server "http://localhost:5000/api/v1.0" --username sina --keydir client1 --action add-contact --contact alice

./shsmc.py --server "http://localhost:5000/api/v1.0" --username bob --keydir client2 --action add-contact --contact sina
./shsmc.py --server "http://localhost:5000/api/v1.0" --username bob --keydir client2 --action add-contact --contact alice

./shsmc.py --server "http://localhost:5000/api/v1.0" --username alice --keydir client3 --action add-contact --contact bob
./shsmc.py --server "http://localhost:5000/api/v1.0" --username alice --keydir client3 --action add-contact --contact sina

./shsmc.py --server "http://localhost:5000/api/v1.0" --username sina --keydir client1 --action send-message --message "hello alice & bob from sina" --recipients alice,bob
./shsmc.py --server "http://localhost:5000/api/v1.0" --username bob --keydir client2 --action send-message --message "hello alice & sina from bob" --recipients alice,sina
./shsmc.py --server "http://localhost:5000/api/v1.0" --username alice --keydir client3 --action send-message --message "hello bob & sina from alice" --recipients bob,sina

echo "Messages for Sina:"
echo "-----------------------------"
./shsmc.py --server "http://localhost:5000/api/v1.0" --username sina --keydir client1 --action get-messages
echo "-----------------------------"

echo "Messages for Bob:"
echo "-----------------------------"
./shsmc.py --server "http://localhost:5000/api/v1.0" --username bob --keydir client2 --action get-messages
echo "-----------------------------"


echo "Messages for Alice:"
echo "-----------------------------"
./shsmc.py --server "http://localhost:5000/api/v1.0" --username alice --keydir client3 --action get-messages
echo "-----------------------------"
```
