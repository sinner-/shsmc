from argparse import ArgumentParser
from shsmc.client.user import User
from shsmc.client.device import Device
from shsmc.client.key import Key
from shsmc.client.message import Message
from shsmc.common.config import Configuration

def main():
    ''' SHSM CLI client.
    '''

    parser = ArgumentParser()
    parser.add_argument("-C",
                        "--config-dir",
                        required=True,
                        type=str,
                        dest="config_dir")
    parser.add_argument("-r",
                        "--register",
                        action="store_true",
                        dest="register")
    parser.add_argument("-d",
                        "--add-device",
                        action="store_true",
                        dest="add_device")
    parser.add_argument("-k",
                        "--add-key",
                        action="store_true",
                        dest="add_key")
    parser.add_argument("-c",
                        "--add-contact",
                        type=str,
                        dest="add_contact")
    parser.add_argument("-M",
                        "--send-message",
                        action="store_true",
                        dest="send_message")
    parser.add_argument("-t",
                        "--to",
                        type=str,
                        dest="to")
    parser.add_argument("-m",
                        "--message",
                        type=str,
                        dest="message")
    parser.add_argument("-g",
                        "--get-messages",
                        action="store_true",
                        dest="get_messages")
    args = parser.parse_args()

    config = Configuration("%s/config.ini" % args.config_dir)
    user = User(config)
    device = Device(config, user.master_signing_key)
    key = Key(config, device.device_signing_key)
    message = Message(config, key)

    if args.register:
        user.register()
    elif args.add_device:
        device.add_device()
    elif args.add_key:
        key.add_key()
    elif args.add_contact:
        device.get_device_keys(args.add_contact)
    elif args.send_message:
        if not args.to or not args.message:
            print("You must call --send-message with --to and --message.")
            exit(1)
        try:
            message.send_message(args.to.split(","), args.message)
        except:
            print("error sending message or getting recipient keys")
            exit()
    elif args.get_messages:
        try:
            for message in message.get_messages():
                print("From: %s\nMessage: %s\n" % (message['from'], message['message']))
        except TypeError:
            print("message public key is not valid")
            exit()
