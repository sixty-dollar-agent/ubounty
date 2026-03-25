import argparse
import sys

from ubounty.commands import browse as browse_cmd


def build_parser():
    parser = argparse.ArgumentParser(
        prog="ubounty",
        description=(
            "ubounty — clear your backlog and earn. "
            "Run 'ubounty <command> --help' for details on each command."
        ),
    )
    subparsers = parser.add_subparsers(dest="command", metavar="<command>")
    subparsers.required = True

    browse_cmd.register_parser(subparsers)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()