from os import listdir
from os.path import exists
from json import dumps
from json import loads
from requests import put
from requests import get
from base64 import b64encode
from nacl.signing import VerifyKey
from nacl.public import PublicKey
from nacl.public import PrivateKey
from nacl.encoding import HexEncoder
from nacl.exceptions import BadSignatureError
from shsmc.common.key import load_key
from shsmc.common.key import save_key
from shsmc.common.util import reconstruct_signed_message

class Key(object):
    """ Client class for registering message keys and fetching message keys for a username.
    """

    def __init__(self, config, device_signing_key):
        self.config = config
        self.device_signing_key = device_signing_key

        key_path = "%s/device_private_key" % config.key_dir

        if exists(key_path):
            try:
                self.device_private_key = PrivateKey(
                    load_key(key_path),
                    encoder=HexEncoder)
            except TypeError:
                raise TypeError
        else:
            self.device_private_key = PrivateKey.generate()
            save_key(self.device_private_key.encode(encoder=HexEncoder), key_path)


    def add_key(self):
        """ Register message key.
        """

        device_verify_key = self.device_signing_key.verify_key.encode(encoder=HexEncoder)
        device_public_key = self.device_private_key.public_key.encode(encoder=HexEncoder)

        headers = {'device-verify-key': device_verify_key.decode('utf-8')}
        data = {"device_public_key": b64encode(
            self.device_signing_key.sign(device_public_key)).decode('utf-8')}
        url = "%s/users/%s/keys/%s" % (self.config.api_url,
                                       self.config.username,
                                       device_public_key.decode('utf-8'))
        resp = put(url, headers=headers, data=data)
        print(resp.text)

    def get_recipient_keys(self, username):
        """ Get message keys for a user.
        """

        device_verify_key = b64encode(self.device_signing_key.sign(self.device_signing_key.verify_key.encode(encoder=HexEncoder)))

        data = dumps({"device_verify_key": device_verify_key.decode('utf-8'),
                      "destination_username": b64encode(
                          self.device_signing_key.sign(username.encode())).decode('utf-8')})

        url = "%s/users/%s/keys" % (self.config.api_url, username)
        resp = get(url, headers={"device_verify_key": device_verify_key.decode('utf-8')})
        recipient_keys = []

        if username not in listdir("%s/contacts" % self.config.key_dir):
            raise Exception("trying to send message to recipient not in contacts list")
        else:
            for key in listdir("%s/contacts/%s/devices" % (self.config.key_dir, username)):

                device_key = VerifyKey(
                    load_key("%s/contacts/%s/devices/%s/device_verify_key" %
                             (self.config.key_dir, username, key)), encoder=HexEncoder)

                try:
                    for signed_key in loads(resp.text):
                        public_key = reconstruct_signed_message(signed_key)
                        device_key.verify(public_key)
                        recipient_keys.append(PublicKey(public_key.message, encoder=HexEncoder))
                except TypeError:
                    raise TypeError
                except BadSignatureError:
                    raise BadSignatureError

        return recipient_keys
