import argparse


def main():
    args = parse_args()
    args.func(args)


def parse_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    init_parser = subparsers.add_parser("init")
    init_parser.set_defaults(func=init)

    return parser.parse_args()


def init(args):
    print("Hello world!")
