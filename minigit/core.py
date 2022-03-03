from collections import namedtuple
import re
from typing import Union
import os
import pathlib

from click import command
import minigit.database


Commit = namedtuple("Commit", ["tree", "parent", "message"])


def write_tree(path: Union[pathlib.Path, None] = None) -> str:
    """
    Creates a file in the object database which encodes the tree at `path`.
    The file is structured like so:

        blob 91a7b14a584645c7b995100223e65f8a5a33b707 cats.txt
        blob fa958e0dd2203e9ad56853a3f51e5945dad317a4 dogs.txt
        tree 53891a3c27b17e0f8fd96c058f968d19e340428d other
    """
    if path is None:
        path = pathlib.Path(".")

    entries = []

    for p in path.iterdir():
        if is_ignored(p):
            continue

        if p.is_file():
            with open(p, "rb") as f:
                data = f.read()
                hash = minigit.database.hash_objects(data, _type="blob")
            entries.append((p.name, hash, "blob"))

        if p.is_dir():
            hash = write_tree(p)
            entries.append((p.name, hash, "tree"))

    tree = "".join(
        f"{_type} {hash} {name}\n" for name, hash, _type in sorted(entries)
    ).encode()

    return minigit.database.hash_objects(tree, _type="tree")


def read_tree(hash: str):
    pwd = pathlib.Path("")
    delete_all_files_in_directory(pwd)
    for path, hash in get_tree(hash).items():
        path.parent.mkdir(parents=True, exist_ok=True)
        data = minigit.database.get_object(hash)
        with open(path, "wb") as f:
            f.write(data)


def get_tree(hash: str, base_path=pathlib.Path("")) -> dict:
    tree = {}
    tree_file = minigit.database.get_object(hash).decode()

    for line in tree_file.splitlines():
        _type, hash, name = line.split()
        if _type == "blob":
            fpath = base_path / name
            tree[fpath] = hash
        elif _type == "tree":
            pwd = base_path / name
            subtree = get_tree(hash, base_path=pwd)
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


def commit(message: str):
    data = f"tree {write_tree()}\n"
    head = minigit.database.get_head()
    if head:
        data += f"parent {head}\n"
    data += "\n"
    data += f"{message}\n"
    data = data.encode()
    commit_hash = minigit.database.hash_objects(data, _type="commit")
    minigit.database.set_head(commit_hash)
    return commit_hash


def get_commit(hash: str):
    data = minigit.database.get_object(hash).decode()
    match = re.match(
        r"tree (?P<tree>[a-zA-Z0-9]+)\n(parent (?P<parent>[a-zA-Z0-9]+)\n)?\n(?P<message>.*)",
        data,
        re.MULTILINE | re.DOTALL,
    )

    if not match:
        raise ValueError(f"Got unexpected formatted commit:\n\n{data}")

    groups = match.groupdict()

    return Commit(
        tree=groups["tree"],
        parent=groups["parent"] if "parent" in groups else None,
        message=groups["message"],
    )


def checkout(hash: str):
    cmt = get_commit(hash)
    read_tree(cmt.tree)
    minigit.database.set_head(hash)
