from collections import namedtuple
import re
from typing import Any, Dict, Union
import os
import pathlib

import minigit.database


# Commit = namedtuple("Commit", ["tree", "parent", "message"])


def save_tree(path: Union[pathlib.Path, None] = None) -> str:
    """
    Creates a file in the object database which encodes the tree at `path`.
    The file is structured like so:

        blob 91a7b14a584645c7b995100223e65f8a5a33b707 cats.txt
        blob fa958e0dd2203e9ad56853a3f51e5945dad317a4 dogs.txt
        tree 53891a3c27b17e0f8fd96c058f968d19e340428d other
    """
    path = get_path(path)
    entries = []

    for p in paths(path):
        if is_ignored(p):
            continue

        if p.is_file():
            hash = save_file(p)
            entries.append((p.name, hash, "blob"))

        if p.is_dir():
            hash = save_tree(p)
            entries.append((p.name, hash, "tree"))

    data = entries_to_bytes(entries)

    return hash_tree(data)


def save_file(path: pathlib.Path):
    data = read_bytes(path)
    return hash_file(data)


def get_path(path: Union[pathlib.Path, None]):
    if path is None:
        path = pathlib.Path(".")

    return path


def entries_to_bytes(entries: list):
    tree = to_tree(entries)
    return to_bytes(tree)


def paths(path: pathlib.Path):
    return path.iterdir()


def read_bytes(path: pathlib.Path):
    with open(path, "rb") as f:
        return f.read()


def hash_file(data: bytes):
    return minigit.database.save_object(data, _type="blob")


def hash_tree(data: bytes):
    return minigit.database.save_object(data, _type="tree")


def to_tree(entries: list):
    return "".join(f"{_type} {hash} {name}\n" for name, hash, _type in sorted(entries))


def to_bytes(s: str):
    return s.encode()


def restore_tree(hash: str):
    pwd = pathlib.Path("")
    delete_all_files_in_directory(pwd)
    for path, hash in load_tree(hash).items():
        path.parent.mkdir(parents=True, exist_ok=True)
        data = minigit.database.load_object(hash)
        with open(path, "wb") as f:
            f.write(data)


def load_tree(hash: str, base_path=pathlib.Path("")) -> dict:
    tree = {}
    tree_file = minigit.database.load_object(hash).decode()

    for line in tree_file.splitlines():
        _type, hash, name = line.split()
        if _type == "blob":
            fpath = base_path / name
            tree[fpath] = hash
        elif _type == "tree":
            pwd = base_path / name
            subtree = load_tree(hash, base_path=pwd)
            tree = {**tree, **subtree}
        else:
            raise ValueError(f'Got unexpected type "{_type}" in tree entry {line}')

    return tree


def is_ignored(path: pathlib.Path) -> bool:
    if path.is_symlink():
        return True

    return ".minigit" in path.parts


def delete_all_files_in_directory(dir: pathlib.Path):
    for path in dir.iterdir():
        if is_ignored(path):
            continue  # skip ignored paths

        if path.is_file():
            os.remove(path)

        if path.is_dir():
            delete_all_files_in_directory(dir / path)


class Commit:
    def __init__(self, tree_hash: str, head: Union[str, None], message: str) -> None:
        self.tree_hash = tree_hash
        self.head = head
        self.message = message

    def __str__(self):
        if not self.head:
            return f"tree {self.tree_hash}\n\n{self.message}\n"

        return f"tree {self.tree_hash}\nparent {self.head}\n\n{self.message}\n"

    def to_bytes(self):
        return str(self).encode()


class CommitParser:
    def __init__(self, data: str):
        self.data = data

    @property
    def commit_regex(self):
        return r"tree (?P<tree>[a-zA-Z0-9]+)\n(parent (?P<parent>[a-zA-Z0-9]+)\n)?\n(?P<message>.*)"

    @property
    def match_object(self):
        return re.match(self.commit_regex, self.data, re.DOTALL)

    def is_valid_commit(self):
        return self.match_object is not None

    def to_commit(self):
        groups = self.match_object.groupdict()
        return Commit(
            tree_hash=groups["tree"],
            head=groups["parent"] if "parent" in groups else None,
            message=groups["message"],
        )


def save_commit(message: str):
    tree_hash = save_tree()
    head = minigit.database.get_head()
    data = Commit(tree_hash, head, message).to_bytes()
    commit_hash = minigit.database.save_object(data, _type="commit")
    minigit.database.set_head(commit_hash)
    return commit_hash


def load_commit(hash: str):
    data = minigit.database.load_object(hash).decode()
    parser = CommitParser(data)

    if not parser.is_valid_commit():
        raise ValueError(f"Got unexpected formatted commit:\n\n{data}")

    return parser.to_commit()


def checkout(hash: str):
    commit = load_commit(hash)
    restore_tree(commit.tree_hash)
    minigit.database.set_head(hash)
