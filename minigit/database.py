import hashlib
import pathlib

GIT_DIR = pathlib.Path(".minigit")
OBJECTS_DIR = GIT_DIR / "objects"
NULL_BYTE = b"\x00"


def init():
    GIT_DIR.mkdir()
    OBJECTS_DIR.mkdir()


def hash_objects(data: bytes, _type="blob") -> str:
    data_with_type = _type.encode() + NULL_BYTE + data
    oid = hashlib.sha1(data_with_type).hexdigest()
    with open(OBJECTS_DIR / oid, "wb") as f:
        f.write(data_with_type)
    return oid


def cat_file(hash: str) -> bytes:
    return get_object(hash)


def get_object(hash: str) -> bytes:
    with open(OBJECTS_DIR / hash, "rb") as f:
        data_with_type = f.read()

    data_type, _, data = data_with_type.partition(NULL_BYTE)

    # TODO: should we assert type here?

    return data
