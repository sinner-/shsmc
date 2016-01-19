# shsmd: Self Hosted Secure Messaging Daemon

## Overview

How hard is it to develop a secure, client-server style messaging system that supports multiple devices per user and multiple recipients per message?

This is my attempt to find out! 

This repository contains a very crude (STILL IN EARLY DEVELOPMENT) CLI client.

Everything is hardcoded, don't use this.

## Installation

### Install necessary OS packages:
  * Fedora:
    * `dnf install redhat-rpm-config python2-devel curl-devel libsodium-devel`
  
### Python setup
  * `git clone https://github.com/sinner-/shsmc`
  * `virtualenv -p /usr/bin/python2.7 shsmc`
  * `cd shsmc`
  * `pip install -r requirements.txt`

### Standalone client (development only)
  * (from inside shsmc directory)
  * `source bin/activate`
  * `mkdir client_keys`
  * `bin/python shsmc.py testuser client_keys register`
  * `bin/python shsmc.py testuser client_keys add-device`
  * `bin/python shsmc.py testuser client_keys send-message`
  * `bin/python shsmc.py testuser client_keys get-messages`
