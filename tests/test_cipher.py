from random import getrandbits

from alshehhi.cipher import Dec, Enc
from alshehhi.hash import SHA3, SHAKE
from alshehhi.io import BYTE_SIZE
from pytest import mark, param

from .util import load_secret_der


@mark.parametrize(
    "security_level",
    [
        128,
        param(192, marks=mark.slow),
        param(256, marks=mark.slow),
    ],
)
def test_pke_perfect_correctness(security_level):
    sk = load_secret_der(security_level)
    pk = sk.public_key()

    hash_algorithm = SHA3(security_level)
    xof_algorithm = SHAKE(security_level)

    enc = Enc(pk, hash_algorithm, xof_algorithm)
    dec = Dec(sk, hash_algorithm, xof_algorithm)

    len = enc.plaintext_len()
    plaintext = bytes(getrandbits(BYTE_SIZE) for _ in range(len))

    ciphertext = enc(plaintext)
    decrypted_message = dec(ciphertext)

    assert plaintext == decrypted_message
