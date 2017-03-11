''' xxx '''
from urllib2 import build_opener
from urllib2 import Request
from urllib2 import HTTPError
from argparse import ArgumentParser
from os import path
from os import listdir
from os import mkdir
from base64 import b64encode
from base64 import b64decode
from nacl.encoding import HexEncoder
from nacl.encoding import RawEncoder
from nacl.signing import SigningKey
from nacl.signing import VerifyKey
from nacl.signing import SignedMessage
from nacl.public import PrivateKey
from nacl.public import PublicKey
from nacl.public import Box
from nacl.utils import random
from nacl.secret import SecretBox
from nacl.exceptions import BadSignatureError
import json
import nacl.utils
import click

def reconstruct_signed_message(signed_message):
    """ hacky method for reconstructing signed messages as
        a PyNaCl SignedMessage object.
    """

    tmp_encoder = RawEncoder
    try:
        tmp_signed_message = tmp_encoder.encode(b64decode(signed_message))
        recon_signed_message = SignedMessage._from_parts(
            tmp_encoder.encode(
                tmp_signed_message[:nacl.bindings.crypto_sign_BYTES]),
            tmp_encoder.encode(
                tmp_signed_message[nacl.bindings.crypto_sign_BYTES:]),
            tmp_signed_message)
    except TypeError:
        print "Not a valid signed message."

    return recon_signed_message

def post(url, parameters):
    ''' xxx '''

    opener = build_opener()
    req = Request(url)
    req.add_header('Content-Type', 'application/json')
    req.data = parameters
    response = None
    try:
            response = opener.open(req).read()
    except HTTPError, e:
            print e.fp.read()

    return response

def register(username, enc_master_verify_key):
    ''' xxx '''

    data = json.dumps({"username": username, "master_verify_key": enc_master_verify_key})
    url = "%s/user" % serverurl
    post(url, data)

def add_device(username, enc_signed_device_verify_key):

    data = json.dumps({"username": username,
                       "device_verify_key": enc_signed_device_verify_key})
    url = "%s/device" % serverurl
    post(url, data)

def add_key(enc_signed_device_verify_key, enc_signed_device_public_key):

    data = json.dumps({"device_verify_key": enc_signed_device_verify_key,
                       "device_public_key": enc_signed_device_public_key})
    url = "%s/key" % serverurl
    post(url, data)

def get_recipient_keys(keydir, device_signing_key, destination_username):

    device_verify_key = device_signing_key.verify_key.encode(encoder=HexEncoder)
    enc_signed_destination_username = b64encode(device_signing_key.sign(str(destination_username)))

    data = json.dumps({"device_verify_key": device_verify_key,
                       "destination_username": enc_signed_destination_username})

    url = "%s/keylist" % serverurl
    output = post(url, data)
    recipient_keys = []
    if destination_username not in listdir(keydir+"/contacts"):
        print "trying to send message to recipient not in contacts list"
        exit()
    else:
        for key in listdir(keydir+"/contacts/"+destination_username):

            device_key = VerifyKey(load_key(keydir+"/contacts/"+destination_username+"/"+key), encoder=HexEncoder)

            try:
                for signed_key in json.loads(output)['device_public_keys']:
                    public_key = reconstruct_signed_message(signed_key)
                    device_key.verify(public_key)
                    recipient_keys.append(PublicKey(public_key.message, encoder=HexEncoder))
            except TypeError:
                print "bad recipient key, exiting"
                exit()
            except BadSignatureError:
                print "bad signature, exiting"
                exit()

    return recipient_keys

def get_device_keys(device_verify_key, enc_signed_destination_username):

    data = json.dumps({"device_verify_key": device_verify_key,
                       "destination_username": enc_signed_destination_username})

    url = "%s/devicelist" % serverurl
    output = post(url, data)
    device_keys = []
    try:
        for key in json.loads(output)['device_verify_keys']:
            device_keys.append(VerifyKey(key, encoder=HexEncoder))
    except TypeError:
        print "bad device key, exiting"
        exit()

    return device_keys

def send_message(device_verify_key, destination_usernames, message_contents, message_public_key):

    data = json.dumps({"device_verify_key": device_verify_key,
                       "destination_usernames": destination_usernames,
                       "message_contents": message_contents,
                       "message_public_key": message_public_key})
    url = "%s/message" % serverurl
    post(url, data)


def get_messages(enc_signed_device_verify_key):

    data = json.dumps({"signed_device_verify_key": enc_signed_device_verify_key})
    url = "%s/messagelist" % serverurl
    output = post(url, data)

    return json.loads(output)

def save_key(key, filename):
    key_file = open(filename, 'w')
    key_file.write(key)
    key_file.close()

def load_key(filename):
    key_file = open(filename, 'r')
    key = key_file.read()
    key_file.close()
    return key

@click.command()
@click.option('--server', required=True)
@click.option('--username', required=True)
@click.option('--keydir', required=True)
@click.option('--action', required=True)
@click.option('--message')
@click.option('--recipients')
@click.option('--contact')

def init(server, username, keydir, action, message, recipients, contact):
    ''' SHSM CLI client. '''

    global serverurl
    serverurl = server

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

            add_device(username, enc_signed_device_verify_key)

        if action == "add-key":

            enc_device_verify_key = device_signing_key.verify_key.encode(encoder=HexEncoder)

            enc_device_public_key = device_private_key.public_key.encode(encoder=HexEncoder)
            enc_signed_device_public_key = b64encode(device_signing_key.sign(enc_device_public_key))

            add_key(enc_device_verify_key, enc_signed_device_public_key)

        if action == "add-contact":

            enc_device_verify_key = device_signing_key.verify_key.encode(encoder=HexEncoder)
            enc_contact = b64encode(device_signing_key.sign(str(contact)))
            contact_keys = get_device_keys(enc_device_verify_key, enc_contact)
            for key in contact_keys:
                print "Saving contact: " + contact
                if contact not in listdir(keydir+"/contacts/"):
                    mkdir(keydir+"/contacts/"+contact)
                save_key(key.encode(encoder=HexEncoder),
                         keydir+"/contacts/"+contact+"/"+key.encode(encoder=HexEncoder))

        if action == "send-message":

            ephemeral_key = PrivateKey.generate()
            enc_ephemeral_public_key = b64encode(
                device_signing_key.sign(
                    ephemeral_key.public_key.encode(encoder=HexEncoder)))

            #TODO:: should sign binary text, no? b"bob"
            destination_usernames = recipients.split(",")
            enc_dest_usernames = b64encode(
                device_signing_key.sign(
                    json.dumps(destination_usernames)))
            symmetric_key = random(SecretBox.KEY_SIZE)
            symmetric_box = SecretBox(symmetric_key)
            nonce = random(SecretBox.NONCE_SIZE)
            msg_manifest = {}
            msg_manifest['recipients'] = {}
            msg_manifest['msg'] = b64encode(symmetric_box.encrypt(str(message), nonce))

            for destination_username in destination_usernames:

                msg_manifest['recipients'][destination_username] = {}

                for recipient_key in get_recipient_keys(keydir, device_signing_key, destination_username):

                    #TODO:: should sign binary text, no?
                    crypt_box = Box(ephemeral_key, recipient_key)
                    nonce = random(Box.NONCE_SIZE)
                    crypt_key = b64encode(crypt_box.encrypt(symmetric_key, nonce))
                    dest_key = recipient_key.encode(encoder=HexEncoder)
                    msg_manifest['recipients'][destination_username][dest_key] = crypt_key

            enc_signed_crypt_msg = b64encode(device_signing_key.sign(json.dumps(msg_manifest)))

            send_message(device_signing_key.verify_key.encode(encoder=HexEncoder),
                         enc_dest_usernames,
                         enc_signed_crypt_msg,
                         enc_ephemeral_public_key)

        if action == "get-messages":

            enc_device_verify_key = device_signing_key.verify_key.encode(encoder=HexEncoder)
            enc_signed_device_verify_key = b64encode(device_signing_key.sign(enc_device_verify_key))
            messages = get_messages(enc_signed_device_verify_key)

            for message_public_key in messages['messages'].keys():
                try:
                    crypto_box = Box(device_private_key,
                                     PublicKey(b64decode(message_public_key), encoder=HexEncoder))
                except TypeError:
                    print "not a valid public key"
                    exit()
                packed_msg = json.loads(messages['messages'][message_public_key])
                msg_manifest = json.loads(b64decode(packed_msg['message_manifest']))
                dest_pub_key = device_private_key.public_key.encode(encoder=HexEncoder)
                symmetric_key = crypto_box.decrypt(
                    b64decode(
                        msg_manifest['recipients'][username][dest_pub_key]))
                symmetric_box = SecretBox(symmetric_key)
                print ('From: %s\nMessage: %s') % (packed_msg['reply_to'], symmetric_box.decrypt(b64decode(msg_manifest['msg'])))

def main():
    init()