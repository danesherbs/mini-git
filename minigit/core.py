import pathlib
import minigit.database


def write_tree(path: pathlib.Path) -> str:
    """
    Creates a file representing the tree at `path` in the object database.
    The tree file is structured like so:

        blob 91a7b14a584645c7b995100223e65f8a5a33b707 cats.txt
        blob fa958e0dd2203e9ad56853a3f51e5945dad317a4 dogs.txt
        tree 53891a3c27b17e0f8fd96c058f968d19e340428d other
    """
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


def read_tree(hash: str) -> None:
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
