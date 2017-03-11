import click
from shsmc.common.config import Configuration
from shsmc.client.user import User
from shsmc.client.device import Device
from shsmc.client.key import Key
from shsmc.client.message import Message

@click.command()
@click.option('--configdir', required=True)
@click.option('--action', required=True)
@click.option('--msg')
@click.option('--recipients')
@click.option('--contact')
def main(configdir, action, msg, recipients, contact):
    ''' SHSM CLI client.
    '''

    config = Configuration("%s/config.ini" % configdir)
    try:
        user = User(config)
    except TypeError:
        print "bad master_verify_key, exiting"
        exit()

    try:
        device = Device(config, user.master_signing_key)
    except TypeError:
        print "bad device_verify_key, exiting"
        exit()

    try:
        key = Key(config, device.device_signing_key)
    except TypeError:
        print "bad device_private_key, exiting"
        exit()

    message = Message(key)

    if action == "register":
        user.register()
    if action == "add-device":
        device.add_device()
    if action == "add-key":
        key.add_key()
    if action == "add-contact":
        try:
            device.get_device_keys(contact)
        except TypeError:
            print "returned device keys are bad, exiting"
            exit()
    if action == "send-message":
        try:
            message.send_message(recipients.split(","), msg)
        except:
            print "error sending message or getting recipient keys"
            exit()
    if action == "get-messages":
        try:

            for message in message.get_messages():

                print ("From: %s\nMessage: %s\n" % (message['from'], message['message']))

        except TypeError:
            print "message public key is not valid"
            exit()
