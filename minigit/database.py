import hashlib
import pathlib

GIT_DIR = pathlib.Path(".minigit")
OBJECTS_DIR = GIT_DIR / "objects"
NULL_BYTE = b"\x00"


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

    @staticmethod
    def from_bytes(data_with_type: bytes):
        type, _, data = data_with_type.partition(NULL_BYTE)
        return Object(data=data, type=type)


def init():
    GIT_DIR.mkdir()
    OBJECTS_DIR.mkdir()


def save_object(data: bytes, _type="blob") -> str:
    object = Object(data=data, type=_type)
    with open(OBJECTS_DIR / object.hash, "wb") as f:
        f.write(object.data_with_type)
    return object.hash


def load_object(hash: str) -> bytes:
    with open(OBJECTS_DIR / hash, "rb") as f:
        data_with_type = f.read()
        object = Object.from_bytes(data_with_type)
    return object.data


def set_head(hash: str):
    with open(GIT_DIR / "HEAD", "w") as f:
        f.write(hash)


def get_head():
    fname = GIT_DIR / "HEAD"

    if not fname.is_file():
        return None

    with open(fname, "r") as f:
        return f.read().strip()
