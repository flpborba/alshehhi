from os import mkdir
from os.path import exists, isfile

from alshehhi.key import generate, import_secret_der


def load_secret_der(security_level):
    dir_name = "data"
    filename = f"{dir_name}/sk_{security_level}.der"

    if isfile(filename):
        data = open(filename, "rb").read()
        return import_secret_der(data)

    sk = generate(security_level)

    if not exists(dir_name):
        mkdir(dir_name)

    open(filename, "wb").write(sk.export_der())

    return sk
