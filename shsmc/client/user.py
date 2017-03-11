from os.path import exists
from json import dumps
from nacl.signing import SigningKey
from nacl.encoding import HexEncoder
from shsmc.common.url import post
from shsmc.common.key import load_key
from shsmc.common.key import save_key

class User(object):

    def __init__(self, config):
        self.config = config

        key_path = "%s/master_signing_key" % config.key_dir

        if exists(key_path):
            try:
                self.master_signing_key = SigningKey(
                    load_key("%s/master_signing_key" % config.key_dir),
                    encoder=HexEncoder)
            except TypeError:
                print "bad key, exiting"
                exit()
        else:
            self.master_signing_key = SigningKey.generate()
            save_key(self.master_signing_key.encode(encoder=HexEncoder), "%s/master_signing_key" % config.key_dir)

    def register(self):
        ''' xxx '''
        enc_master_verify_key = self.master_signing_key.verify_key.encode(encoder=HexEncoder)
        data = dumps({"username": self.config.username, "master_verify_key": enc_master_verify_key})
        url = "%s/user" % self.config.api_url
        post(url, data)

