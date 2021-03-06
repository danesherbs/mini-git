import pathlib
import argparse
import minigit.database
import minigit.core


def main():
    args = parse_args()
    args.func(args)


def parse_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    init_parser = subparsers.add_parser("init")
    init_parser.set_defaults(func=init)

    hash_object_parser = subparsers.add_parser("hash-object")
    hash_object_parser.set_defaults(func=hash_object)
    hash_object_parser.add_argument("file", type=str)

    cat_file_parser = subparsers.add_parser("cat-file")
    cat_file_parser.set_defaults(func=cat_file)
    cat_file_parser.add_argument("hash", type=str)

    write_tree_parser = subparsers.add_parser("write-tree")
    write_tree_parser.set_defaults(func=write_tree)

    read_tree_parser = subparsers.add_parser("read-tree")
    read_tree_parser.set_defaults(func=read_tree)
    read_tree_parser.add_argument("hash", type=str)

    commit_parser = subparsers.add_parser("commit")
    commit_parser.set_defaults(func=commit)
    commit_parser.add_argument("-m", "--message", type=str, required=True)

    log_parser = subparsers.add_parser("log")
    log_parser.set_defaults(func=log)
    log_parser.add_argument("hash", nargs="?", type=str)

    checkout_parser = subparsers.add_parser("checkout")
    checkout_parser.set_defaults(func=checkout)
    checkout_parser.add_argument("hash", type=str)

    return parser.parse_args()


def init(args):
    minigit.database.init()


def hash_object(args):
    with open(args.file, "rb") as f:
        data = f.read()
        hash = minigit.database.save_object(data)
    print(hash)


def cat_file(args):
    contents = minigit.database.load_object(args.hash)
    print(contents)


def write_tree(args):
    pwd = pathlib.Path(".")
    hash = minigit.core.save_tree(pwd)
    print(hash)


def read_tree(args):
    minigit.core.restore_tree(args.hash)


def commit(args):
    hash = minigit.core.save_commit(args.message)
    print(hash)


def log(args):
    hash = args.hash or minigit.database.get_head()
    while hash:
        cmt = minigit.core.load_commit(hash)
        print(f"\033[93mcommit {cmt.tree_hash}\033[0m\n\n    {cmt.message}")
        hash = cmt.parent


def checkout(args):
    minigit.core.checkout(args.hash)
