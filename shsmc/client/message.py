from json import dumps
from json import loads
from base64 import b64encode
from base64 import b64decode
from nacl.secret import SecretBox
from nacl.public import PrivateKey
from nacl.public import PublicKey
from nacl.public import Box
from nacl.encoding import HexEncoder
from nacl.utils import random
from nacl.exceptions import BadSignatureError
from shsmc.common.url import post

class Message(object):
    def __init__(self, key):
        self.key = key

    def send_message(self, recipients, msg):

        ephemeral_key = PrivateKey.generate()
        enc_ephemeral_public_key = b64encode(
            self.key.device_signing_key.sign(
                ephemeral_key.public_key.encode(encoder=HexEncoder)))

        #TODO:: should sign binary text, no? b"bob"
        enc_dest_usernames = b64encode(
            self.key.device_signing_key.sign(dumps(recipients)))
        symmetric_key = random(SecretBox.KEY_SIZE)
        symmetric_box = SecretBox(symmetric_key)
        nonce = random(SecretBox.NONCE_SIZE)
        msg_manifest = {}
        msg_manifest['recipients'] = {}
        msg_manifest['msg'] = b64encode(symmetric_box.encrypt(str(msg), nonce))

        for destination_username in recipients:

            msg_manifest['recipients'][destination_username] = {}

            try:
                recipient_keys = self.key.get_recipient_keys(destination_username)
            except:
                raise

            for recipient_key in recipient_keys:

                #TODO:: should sign binary text, no?
                crypt_box = Box(ephemeral_key, recipient_key)
                nonce = random(Box.NONCE_SIZE)
                crypt_key = b64encode(crypt_box.encrypt(symmetric_key, nonce))
                dest_key = recipient_key.encode(encoder=HexEncoder)
                msg_manifest['recipients'][destination_username][dest_key] = crypt_key

        enc_signed_crypt_msg = b64encode(self.key.device_signing_key.sign(dumps(msg_manifest)))
        data = dumps({"device_verify_key": self.key.device_signing_key.verify_key.encode(encoder=HexEncoder),
                      "destination_usernames": enc_dest_usernames,
                      "message_contents": enc_signed_crypt_msg,
                      "message_public_key": enc_ephemeral_public_key})
        url = "%s/message" % self.key.config.api_url
        post(url, data)

    def get_messages(self):

        device_verify_key = self.key.device_signing_key.verify_key.encode(encoder=HexEncoder)
        enc_signed_device_verify_key = b64encode(self.key.device_signing_key.sign(device_verify_key))
        data = dumps({"signed_device_verify_key": enc_signed_device_verify_key})
        url = "%s/messagelist" % self.key.config.api_url
        messages = loads(post(url, data))

        decrypted_messages = []

        for message_public_key in messages['messages'].keys():
            try:
                crypto_box = Box(self.key.device_private_key,
                                 PublicKey(b64decode(message_public_key), encoder=HexEncoder))
            except TypeError:
                raise TypeError

            packed_msg = loads(messages['messages'][message_public_key])
            msg_manifest = loads(b64decode(packed_msg['message_manifest']))
            dest_pub_key = self.key.device_private_key.public_key.encode(encoder=HexEncoder)
            symmetric_key = crypto_box.decrypt(
                b64decode(
                    msg_manifest['recipients'][self.key.config.username][dest_pub_key]))
            symmetric_box = SecretBox(symmetric_key)
            decrypted_messages.append({'from': packed_msg['reply_to'], 'message': symmetric_box.decrypt(b64decode(msg_manifest['msg']))})

        return decrypted_messages
