import pathlib
import minigit.database


def write_tree(path: pathlib.Path) -> str:
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
        f"{_type}, {hash}, {name}\n" for name, hash, _type in sorted(entries)
    ).encode()

    return minigit.database.hash_objects(tree)


def is_ignored(path: pathlib.Path) -> bool:
    if path.is_symlink():
        return True

    return ".minigit" in path.parts
