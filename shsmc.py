#!bin/python
''' xxx '''
import json
from io import BytesIO
from argparse import ArgumentParser
from os import path
from base64 import b64encode
from base64 import b64decode
from nacl.encoding import HexEncoder
from nacl.signing import SigningKey
from nacl.public import PrivateKey
from nacl.public import PublicKey
from nacl.public import Box
from nacl.utils import random
from nacl.secret import SecretBox
import pycurl

def register(username, enc_master_verify_key):
    ''' xxx '''

    data = json.dumps({"username": username, "master_verify_key": enc_master_verify_key})
    register_url = "http://localhost:5000/api/v1.0/user"

    curl = pycurl.Curl()
    curl.setopt(curl.URL, register_url)
    curl.setopt(pycurl.HTTPHEADER, ['Content-Type: application/json'])
    curl.setopt(pycurl.POST, 1)
    curl.setopt(pycurl.POSTFIELDS, data)
    curl.perform()

def add_device(username, enc_signed_device_verify_key, enc_signed_device_public_key):

    data = json.dumps({"username": username,
                       "device_verify_key": enc_signed_device_verify_key,
                       "device_public_key": enc_signed_device_public_key})

    register_url = "http://localhost:5000/api/v1.0/device"

    curl = pycurl.Curl()
    curl.setopt(curl.URL, register_url)
    curl.setopt(pycurl.HTTPHEADER, ['Content-Type: application/json'])
    curl.setopt(pycurl.POST, 1)
    curl.setopt(pycurl.POSTFIELDS, data)
    curl.perform()

def get_recipient_keys(username, enc_signed_destination_username):

    data = json.dumps({"username": username,
                       "destination_username": enc_signed_destination_username})

    register_url = "http://localhost:5000/api/v1.0/keylist"

    curl = pycurl.Curl()
    curl.setopt(curl.URL, register_url)
    curl.setopt(pycurl.HTTPHEADER, ['Content-Type: application/json'])
    curl.setopt(pycurl.POST, 1)
    curl.setopt(pycurl.POSTFIELDS, data)
    output = BytesIO()
    curl.setopt(curl.WRITEFUNCTION, output.write)
    curl.perform()
    recipient_keys = []
    try:
        for key in json.loads(output.getvalue())['device_public_keys']:
            recipient_keys.append(PublicKey(key, encoder=HexEncoder))
    except TypeError:
        print "bad recipient key, exiting"
        exit()

    return recipient_keys

def send_message(username, destination_usernames, message_contents, message_public_key):

    data = json.dumps({"username": username,
                       "destination_usernames": destination_usernames,
                       "message_contents": message_contents,
                       "message_public_key": message_public_key})

    register_url = "http://localhost:5000/api/v1.0/message"

    curl = pycurl.Curl()
    curl.setopt(curl.URL, register_url)
    curl.setopt(pycurl.HTTPHEADER, ['Content-Type: application/json'])
    curl.setopt(pycurl.POST, 1)
    curl.setopt(pycurl.POSTFIELDS, data)
    curl.perform()

def get_messages(username, enc_signed_device_verify_key):

    data = json.dumps({"username": username,
                       "signed_device_verify_key": enc_signed_device_verify_key})

    register_url = "http://localhost:5000/api/v1.0/messagelist"

    curl = pycurl.Curl()
    curl.setopt(curl.URL, register_url)
    curl.setopt(pycurl.HTTPHEADER, ['Content-Type: application/json'])
    curl.setopt(pycurl.POST, 1)
    curl.setopt(pycurl.POSTFIELDS, data)
    output = BytesIO()
    curl.setopt(curl.WRITEFUNCTION, output.write)
    curl.perform()

    return json.loads(output.getvalue())

def save_key(key, filename):
    key_file = open(filename, 'w')
    key_file.write(key)
    key_file.close()

def load_key(filename):
    key_file = open(filename, 'r')
    key = key_file.read()
    key_file.close()
    return key

def init():
    ''' xxx '''


    parser = ArgumentParser(description='SHSM CLI client.')
    parser.add_argument('username', type=str)
    parser.add_argument('keydir', type=str)
    parser.add_argument('action', type=str)

    args = parser.parse_args()

    username = args.username
    keydir = args.keydir
    action = args.action

    if action == "register":
        master_signing_key = SigningKey.generate()
        device_signing_key = SigningKey.generate()
        device_private_key = PrivateKey.generate()

        enc_master_verify_key = master_signing_key.verify_key.encode(encoder=HexEncoder)
        register(username, enc_master_verify_key)

        #TODO: make sure keydir exists

        save_key(master_signing_key.encode(encoder=HexEncoder), keydir+"/master_signing_key")
        save_key(device_signing_key.encode(encoder=HexEncoder), keydir+"/device_signing_key")
        save_key(device_private_key.encode(encoder=HexEncoder), keydir+"/device_private_key")

    else:
        try:
            master_signing_key = SigningKey(
                load_key(keydir+"/master_signing_key"),
                encoder=HexEncoder)
            device_signing_key = SigningKey(
                load_key(keydir+"/device_signing_key"),
                encoder=HexEncoder)
            device_private_key = PrivateKey(
                load_key(keydir+"/device_private_key"),
                encoder=HexEncoder)
        except TypeError:
            print "bad key, exiting."
            exit()

        if action == "add-device":

            enc_device_verify_key = device_signing_key.verify_key.encode(encoder=HexEncoder)
            enc_signed_device_verify_key = b64encode(master_signing_key.sign(enc_device_verify_key))

            enc_device_public_key = device_private_key.public_key.encode(encoder=HexEncoder)
            enc_signed_device_public_key = b64encode(master_signing_key.sign(enc_device_public_key))

            add_device(username, enc_signed_device_verify_key, enc_signed_device_public_key)

        if action == "send-message":

            ephemeral_key = PrivateKey.generate()
            enc_ephemeral_public_key = b64encode(
                device_signing_key.sign(
                    ephemeral_key.public_key.encode(encoder=HexEncoder)))

            #TODO:: should sign binary text, no? b"bob"
            destination_usernames = ["bob"]
            enc_dest_usernames = b64encode(
                device_signing_key.sign(
                    json.dumps({"destination_usernames": destination_usernames})))
            message = b"haa hello world"
            symmetric_key = random(SecretBox.KEY_SIZE)
            symmetric_box = SecretBox(symmetric_key)
            nonce = random(SecretBox.NONCE_SIZE)
            msg_manifest = {}
            msg_manifest['recipients'] = {}
            msg_manifest['msg'] = b64encode(symmetric_box.encrypt(message, nonce))

            for dest_user in destination_usernames:
                msg_manifest['recipients'][dest_user] = {}

                for recipient_key in get_recipient_keys(username,
                                                        b64encode(
                                                            device_signing_key.sign(
                                                                dest_user))):

                    #TODO:: should sign binary text, no?
                    crypt_box = Box(ephemeral_key, recipient_key)
                    nonce = random(Box.NONCE_SIZE)
                    crypt_key = b64encode(crypt_box.encrypt(symmetric_key, nonce))
                    dest_key = recipient_key.encode(encoder=HexEncoder)
                    msg_manifest['recipients'][dest_user][dest_key] = crypt_key

            enc_signed_crypt_msg = b64encode(device_signing_key.sign(json.dumps(msg_manifest)))

            send_message(username,
                         enc_dest_usernames,
                         enc_signed_crypt_msg,
                         enc_ephemeral_public_key)

        if action == "get-messages":

            enc_device_verify_key = device_signing_key.verify_key.encode(encoder=HexEncoder)
            enc_signed_device_verify_key = b64encode(device_signing_key.sign(enc_device_verify_key))
            messages = get_messages(username, enc_signed_device_verify_key)

            for message_public_key in messages['messages'].keys():
                try:
                    crypto_box = Box(device_private_key,
                                     PublicKey(b64decode(message_public_key), encoder=HexEncoder))
                except TypeError:
                    print "not a valid public key"
                    exit()
                msg_manifest = json.loads(b64decode(messages['messages'][message_public_key]))
                dest_pub_key = device_private_key.public_key.encode(encoder=HexEncoder)
                symmetric_key = crypto_box.decrypt(
                    b64decode(
                        msg_manifest['recipients'][username][dest_pub_key]))
                symmetric_box = SecretBox(symmetric_key)
                print symmetric_box.decrypt(b64decode(msg_manifest['msg']))

if __name__ == '__main__':
    init()
