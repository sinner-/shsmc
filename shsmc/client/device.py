from os.path import exists
from os import listdir
from os import mkdir
from json import dumps
from json import loads
from base64 import b64encode
from nacl.signing import VerifyKey
from nacl.signing import SigningKey
from nacl.encoding import HexEncoder
from shsmc.common.url import post
from shsmc.common.key import load_key
from shsmc.common.key import save_key

class Device(object):
    """ Client class for registering devices and fetching the device keys for a username.
    """

    def __init__(self, config, master_signing_key):
        self.config = config
        self.master_signing_key = master_signing_key

        key_path = "%s/device_signing_key" % config.key_dir

        if exists(key_path):
            try:
                self.device_signing_key = SigningKey(
                    load_key("%s/device_signing_key" % config.key_dir),
                    encoder=HexEncoder)
            except TypeError:
                raise TypeError
        else:
            self.device_signing_key = SigningKey.generate()
            save_key(self.device_signing_key.encode(encoder=HexEncoder),
                     "%s/device_signing_key" % config.key_dir)

    def add_device(self):
        """ Register device.
        """

        device_verify_key = b64encode(
            self.master_signing_key.sign(
                self.device_signing_key.verify_key.encode(encoder=HexEncoder)))

        data = dumps({"username": self.config.username,
                      "device_verify_key": device_verify_key.decode('utf-8')})
        url = "%s/device" % self.config.api_url
        post(url, data)

    def get_device_keys(self, username):
        """ Get device keys for a user.
        """

        enc_username = b64encode(self.device_signing_key.sign(username.encode()))

        device_verify_key = self.device_signing_key.verify_key.encode(encoder=HexEncoder)

        data = dumps({"device_verify_key": device_verify_key.decode('utf-8'),
                      "destination_username": enc_username.decode('utf-8')})

        url = "%s/devicelist" % self.config.api_url
        output = post(url, data)
        contact_keys = []

        try:
            for key in loads(output):
                contact_keys.append(VerifyKey(key.encode(), encoder=HexEncoder))
        except TypeError:
            raise TypeError

        for key in contact_keys:
            if username not in listdir("%s/contacts/" % self.config.key_dir):
                mkdir("%s/contacts/%s" % (self.config.key_dir, username))
                mkdir("%s/contacts/%s/devices" % (self.config.key_dir, username))
            save_key(key.encode(encoder=HexEncoder),
                     "%s/contacts/%s/devices/%s" % (self.config.key_dir,
                                                    username,
                                                    key.encode(encoder=HexEncoder).decode('utf-8')))
