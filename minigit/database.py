import hashlib
import pathlib

GIT_DIR = pathlib.Path(".minigit")
OBJECTS_DIR = GIT_DIR / "objects"
NULL_BYTE = b"\x00"


def init():
    GIT_DIR.mkdir()
    OBJECTS_DIR.mkdir()


def save_object(data: bytes, _type="blob") -> str:
    object = Object(data=data, type=_type)
    with open(OBJECTS_DIR / object.hash, "wb") as f:
        f.write(object.data_with_type)
    return object.hash


class Object:
    def __init__(self, data: bytes, type: str):
        self.data = data
        self.type = type

    @property
    def hash(self):
        return hashlib.sha1(self.data_with_type).hexdigest()

    @property
    def data_with_type(self):
        return self.type.encode() + NULL_BYTE + self.data


def cat_file(hash: str) -> bytes:
    return get_object(hash)


def get_object(hash: str) -> bytes:
    data_with_type = read_hash(hash)
    data_type, data = parse_bytes(data_with_type)
    return data


def read_hash(hash: str):
    with open(OBJECTS_DIR / hash, "rb") as f:
        return f.read()


def parse_bytes(data_with_type: bytes):
    data_type, _, data = data_with_type.partition(NULL_BYTE)
    return data_type, data


def set_head(hash: str):
    with open(GIT_DIR / "HEAD", "w") as f:
        f.write(hash)


def get_head():
    fname = GIT_DIR / "HEAD"

    if not fname.is_file():
        return None

    with open(fname, "r") as f:
        return f.read().strip()
