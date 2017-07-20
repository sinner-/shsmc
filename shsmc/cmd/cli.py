import click
from shsmc.client.user import User
from shsmc.client.device import Device
from shsmc.client.key import Key
from shsmc.client.message import Message
from shsmc.common.config import Configuration

CONF = None

@click.command()
@click.option('--configdir', required=True)
@click.option('--action', required=True)
@click.option('--msg')
@click.option('--recipients')
@click.option('--contact')
def main(configdir, action, msg, recipients, contact):
    ''' SHSM CLI client.
    '''

    CONF = Configuration(configdir)

    user = User()
    device = Device(user.master_signing_key)
    key = Key(device.device_signing_key)
    message = Message(key)

    if action == "register":
        user.register()
    if action == "add-device":
        device.add_device()
    if action == "add-key":
        key.add_key()
    if action == "add-contact":
        device.get_device_keys(contact)
    if action == "send-message":
        try:
            message.send_message(recipients.split(","), msg)
        except:
            print("error sending message or getting recipient keys")
            exit()
    if action == "get-messages":
        try:
            for message in message.get_messages():
                print("From: %s\nMessage: %s\n" % (message['from'], message['message']))
        except TypeError:
            print("message public key is not valid")
            exit()
