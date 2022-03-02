import minigit.database
import argparse


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

    return parser.parse_args()


def init(args):
    minigit.database.init()


def hash_object(args):
    with open(args.file, "rb") as f:
        data = f.read()
        obj = minigit.database.hash_objects(data)
    print(obj)


def cat_file(args):
    contents = minigit.database.cat_file(args.hash)
    print(contents)


def write_tree(args):
    minigit.database.write_tree()
