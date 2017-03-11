from os import listdir
from os.path import exists
from json import dumps
from json import loads
from base64 import b64encode
from nacl.signing import VerifyKey
from nacl.public import PublicKey
from nacl.public import PrivateKey
from nacl.encoding import HexEncoder
from nacl.exceptions import BadSignatureError
from shsmc.common.url import post
from shsmc.common.key import load_key
from shsmc.common.key import save_key
from shsmc.common.util import reconstruct_signed_message

class Key(object):

    def __init__(self, config, device_signing_key):

        self.config = config
        self.device_signing_key = device_signing_key

        key_path = "%s/device_private_key" % config.key_dir

        if exists(key_path):
            try:
                self.device_private_key = PrivateKey(
                    load_key("%s/device_private_key" % config.key_dir),
                    encoder=HexEncoder)
            except TypeError:
                print "bad key, exiting"
                exit()
        else:
            self.device_private_key = PrivateKey.generate()
            save_key(self.device_private_key.encode(encoder=HexEncoder), "%s/device_private_key" % config.key_dir)


    def add_key(self):

        enc_device_verify_key = self.device_signing_key.verify_key.encode(encoder=HexEncoder)

        enc_device_public_key = self.device_private_key.public_key.encode(encoder=HexEncoder)

        enc_signed_device_public_key = b64encode(self.device_signing_key.sign(enc_device_public_key))
        data = dumps({"device_verify_key": enc_device_verify_key,
                      "device_public_key": enc_signed_device_public_key})
        url = "%s/key" % self.config.api_url
        post(url, data)

    def get_recipient_keys(self, destination_username):

        device_verify_key = self.device_signing_key.verify_key.encode(encoder=HexEncoder)
        enc_signed_destination_username = b64encode(self.device_signing_key.sign(str(destination_username)))

        data = dumps({"device_verify_key": device_verify_key,
                           "destination_username": enc_signed_destination_username})

        url = "%s/keylist" % self.config.api_url
        output = post(url, data)
        recipient_keys = []

        if destination_username not in listdir("%s/contacts" % self.config.key_dir):
            print "trying to send message to recipient not in contacts list"
            exit()
        else:
            for key in listdir("%s/contacts/%s" % (self.config.key_dir, destination_username)):

                device_key = VerifyKey(load_key("%s/contacts/%s/%s" % (self.config.key_dir, destination_username, key)), encoder=HexEncoder)

                try:
                    for signed_key in loads(output)['device_public_keys']:
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
