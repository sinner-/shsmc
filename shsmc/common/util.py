from nacl.encoding import Base64Encoder
from nacl.signing import SignedMessage
from nacl.bindings import crypto_sign_BYTES

def reconstruct_signed_message(signed_message):
    """ hacky method for reconstructing signed messages as
        a PyNaCl SignedMessage object.
    """

    try:
        tmp_signed_message = Base64Encoder.decode(signed_message)
        recon_signed_message = SignedMessage._from_parts(
            tmp_signed_message[:crypto_sign_BYTES],
            tmp_signed_message[crypto_sign_BYTES:],
            tmp_signed_message)
    except TypeError:
        return TypeError

    return recon_signed_message
