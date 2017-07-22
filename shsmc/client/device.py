from os.path import exists
from os import listdir
from os import mkdir
from json import dumps
from json import loads
from requests import put
from requests import get
from base64 import b64encode
from nacl.signing import VerifyKey
from nacl.signing import SigningKey
from nacl.encoding import HexEncoder
from shsmc.common.key import load_key
from shsmc.common.key import save_key

class Device(object):
    """ Client class for registering devices and fetching the device keys for a username.
    """

    def __init__(self, config, master_signing_key):
        self._config = config
        self.master_signing_key = master_signing_key

        key_path = "%s/device_signing_key" % self._config.key_dir

        if exists(key_path):
            try:
                self.device_signing_key = SigningKey(
                    load_key(key_path),
                    encoder=HexEncoder
                )
            except TypeError:
                print("Invalid master_signing_key file.")
                exit(1)
        else:
            self.device_signing_key = SigningKey.generate()
            save_key(
                self.device_signing_key.encode(encoder=HexEncoder),
                key_path
            )

    def add_device(self):
        """ Register device.
        """

        device_verify_key = b64encode(
            self.master_signing_key.sign(
                self.device_signing_key.verify_key.encode(encoder=HexEncoder)
            )
        )
        data = {
            "device_verify_key": device_verify_key.decode('utf-8')
        }
        url = "%s/users/%s/devices/%s" % (
            self._config.api_url,
            self._config.username,
            self.device_signing_key.verify_key.encode(encoder=HexEncoder).decode('utf-8')
        )
        resp = put(url, data=data)
        print(resp.text)

    def get_device_keys(self, username):
        """ Get device keys for a user.
        """

        device_verify_key = b64encode(
            self.device_signing_key.sign(
                self.device_signing_key.verify_key.encode(encoder=HexEncoder)
            )
        )

        url = "%s/users/%s/devices" % (self._config.api_url, username)
        try:
            resp = get(
                url, headers={
                    "device_verify_key": device_verify_key.decode('utf-8')
                }
            )
        except:
            print("Unable to get keys.")
            return

        if not resp or resp.status_code != 200:
            return

        contact_keys = []

        try:
            for key in loads(resp.text):
                contact_keys.append(VerifyKey(key.encode(), encoder=HexEncoder))
        except:
            raise

        for key in contact_keys:
            if username not in listdir("%s/contacts/" % self._config.key_dir):
                mkdir("%s/contacts/%s" % (self._config.key_dir, username))
                mkdir("%s/contacts/%s/devices" % (self._config.key_dir, username))
                mkdir("%s/contacts/%s/devices/%s" % (
                    self._config.key_dir,
                    username,
                    key.encode(encoder=HexEncoder).decode('utf-8'))
                )

            save_key(key.encode(encoder=HexEncoder),
                "%s/contacts/%s/devices/%s/device_verify_key" % (
                    self._config.key_dir,
                    username,
                    key.encode(encoder=HexEncoder).decode('utf-8'))
            )
