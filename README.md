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

### Standalone client (development only)
  * (from inside shsmc directory)
  * `source bin/activate`
  * `mkdir client_keys`
  * `bin/python shsmc.py --server "http://localhost:5000/api/v1.0" --username testuser --keydir client_keys --action register`
  * `bin/python shsmc.py --server "http://localhost:5000/api/v1.0" --username testuser --keydir client_keys --action add-device`
  * `bin/python shsmc.py --server "http://localhost:5000/api/v1.0" --username testuser --keydir client_keys --action send-message --message "test message foo" --recipients recipient1,recipient2`
  * `bin/python shsmc.py --server "http://localhost:5000/api/v1.0" --username testuser --keydir client_keys --action get-messages`
