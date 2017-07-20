from os.path import exists
from json import dumps
from requests import put
from nacl.signing import SigningKey
from nacl.encoding import HexEncoder
from shsmc.common.key import load_key
from shsmc.common.key import save_key

class User(object):
    """ Client class for registering a username.
    """

    def __init__(self):
        key_path = "%s/master_signing_key" % CONF.key_dir

        if exists(key_path):
            try:
                self.master_signing_key = SigningKey(
                    load_key(key_path),
                    encoder=HexEncoder
                )
            except TypeError:
                print("Invalid master_signing_key file.")
                exit(1)

        else:
            self.master_signing_key = SigningKey.generate()
            save_key(
                self.master_signing_key.encode(encoder=HexEncoder),
                key_path
            )

    def register(self):
        """ Register username.
        """

        master_verify_key = self.master_signing_key.verify_key.encode(encoder=HexEncoder)
        data = {
            "master_verify_key": master_verify_key.decode('utf-8')
        }
        url = "%s/users/%s" % (
            CONF.api_url,
            CONF.username
        )
        resp = put(url, data=data)
        print(resp.text)
