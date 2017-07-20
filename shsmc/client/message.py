from json import dumps
from json import loads
from base64 import b64encode
from base64 import b64decode
from requests import post
from requests import get
from nacl.signing import VerifyKey
from nacl.secret import SecretBox
from nacl.public import PrivateKey
from nacl.public import PublicKey
from nacl.public import Box
from nacl.encoding import HexEncoder
from nacl.utils import random
from nacl.exceptions import BadSignatureError
from shsmc.common.key import load_key
from shsmc.common.key import save_key
from shsmc.common.util import reconstruct_signed_message
from shsmc.common.config import CONF

class Message(object):
    """ Client class for sending and receiving messages.
    """

    def __init__(self, key):
        self.key = key

    def send_message(self, recipients, msg):
        """ Send a message to recipients.
        """

        ephemeral_key = PrivateKey.generate()
        symmetric_key = random(SecretBox.KEY_SIZE)
        msg_manifest = {}
        msg_manifest['recipients'] = {}
        msg_manifest['device'] = self.key.device_signing_key.verify_key.encode(encoder=HexEncoder).decode('utf-8')
        msg_manifest['msg'] = b64encode(
            SecretBox(symmetric_key).encrypt(msg.encode(), random(Box.NONCE_SIZE))
        ).decode('utf-8')

        for recipient in recipients:

            msg_manifest['recipients'][recipient] = {}

            try:
                recipient_keys = self.key.get_recipient_keys(recipient)
            except:
                raise

            for recipient_key in recipient_keys:
                dest_key = recipient_key.encode(encoder=HexEncoder)
                msg_manifest['recipients'][recipient][dest_key.decode('utf-8')] = b64encode(
                    Box(ephemeral_key, recipient_key).encrypt(
                        symmetric_key,
                        random(Box.NONCE_SIZE)
                    )
                ).decode('utf-8')

        device_verify_key = self.key.device_signing_key.verify_key.encode(encoder=HexEncoder)
        data = {
            "device_verify_key": device_verify_key.decode('utf-8'),
            "destination_usernames": b64encode(
                self.key.device_signing_key.sign(
                    dumps(recipients).encode()
                )
            ).decode('utf-8'),
            "message_contents": b64encode(
                self.key.device_signing_key.sign(
                    dumps(msg_manifest).encode()
                )
            ).decode('utf-8'),
            "message_public_key": b64encode(
                self.key.device_signing_key.sign(
                    ephemeral_key.public_key.encode(encoder=HexEncoder)
                )
            ).decode('utf-8')
        }

        post("%s/message" % CONF.api_url, data=data)

    def get_messages(self):
        """ Get all messages for this device.
        """

        device_verify_key = b64encode(
            self.key.device_signing_key.sign(
                self.key.device_signing_key.verify_key.encode(encoder=HexEncoder)
            )
        )
        messages = loads(
            get(
                "%s/users/%s/devices/%s/messages" % (
                    CONF.api_url,
                    CONF.username,
                    self.key.device_signing_key.verify_key.encode(encoder=HexEncoder).decode('utf-8')
                ),
                headers={"device_verify_key": device_verify_key.decode('utf-8')}
            ).text
        )

        decrypted_messages = []

        for message in messages.keys():

            signed_message_public_key = reconstruct_signed_message(message.encode())
            message_public_key = signed_message_public_key.message
            packed_msg = loads(messages[message])
            signed_message_contents = reconstruct_signed_message(packed_msg['message_manifest'])
            msg_manifest = loads(signed_message_contents.message.decode('utf-8'))

            sender_key = VerifyKey(
                load_key(
                    "%s/contacts/%s/devices/%s/device_verify_key" % (
                        CONF.key_dir,
                        packed_msg['reply_to'],
                        msg_manifest['device']
                    )
                ),
                encoder=HexEncoder
            )
            try:
                sender_key.verify(signed_message_public_key)
                sender_key.verify(signed_message_contents)
            except BadSignatureError:
                raise BadSignatureError

            try:
                crypto_box = Box(self.key.device_private_key,
                                 PublicKey(message_public_key, encoder=HexEncoder))
            except TypeError:
                raise TypeError

            save_key(
                message_public_key,
                "%s/contacts/%s/devices/%s/ephemeral_key" % (
                    CONF.key_dir,
                    packed_msg['reply_to'],
                    msg_manifest['device']
                )
            )

            dest_pub_key = self.key.device_private_key.public_key.encode(encoder=HexEncoder)
            symmetric_key = crypto_box.decrypt(
                b64decode(
                    msg_manifest['recipients'][CONF.username][dest_pub_key.decode('utf-8')]
                )
            )
            symmetric_box = SecretBox(symmetric_key)
            decrypted_messages.append(
                {
                    'from': packed_msg['reply_to'],
                    'message': symmetric_box.decrypt(
                        b64decode(msg_manifest['msg'])
                    ).decode('utf-8')
                }
            )

        return decrypted_messages
