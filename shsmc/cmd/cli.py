''' xxx '''

import click
from shsmc.common.config import Configuration
from shsmc.client.user import User
from shsmc.client.device import Device
from shsmc.client.key import Key
from shsmc.client.message import Message
from shsmc.common.key import save_key
from shsmc.common.key import load_key
from shsmc.common.util import reconstruct_signed_message

@click.command()
@click.option('--configdir', required=True)
@click.option('--action', required=True)
@click.option('--msg')
@click.option('--recipients')
@click.option('--contact')
def main(configdir, action, msg, recipients, contact):
    ''' SHSM CLI client. '''

    config = Configuration("%s/config.ini" % configdir)
    user = User(config)
    device = Device(config, user.master_signing_key)
    key = Key(config, device.device_signing_key)
    message = Message(key)

    if action == "register":
        user.register()
    else:
        if action == "add-device":
            device.add_device()
        if action == "add-key":
            key.add_key()
        if action == "add-contact":
            device.get_device_keys(contact)
        if action == "send-message":
            message.send_message(recipients.split(","), msg)
        if action == "get-messages":
            message.get_messages()
