from base64 import b64decode
from nacl.encoding import RawEncoder
from nacl.signing import SignedMessage
from nacl.bindings import crypto_sign_BYTES

def reconstruct_signed_message(signed_message):
    """ hacky method for reconstructing signed messages as
        a PyNaCl SignedMessage object.
    """

    tmp_encoder = RawEncoder
    try:
        tmp_signed_message = tmp_encoder.encode(b64decode(signed_message))
        recon_signed_message = SignedMessage._from_parts(
            tmp_encoder.encode(
                tmp_signed_message[crypto_sign_BYTES]),
            tmp_encoder.encode(
                tmp_signed_message[crypto_sign_BYTES:]),
            tmp_signed_message)
    except TypeError:
        print "Not a valid signed message."

    return recon_signed_message

