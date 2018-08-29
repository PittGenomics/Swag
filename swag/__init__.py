import os
import sys
import argparse
import traceback

from importlib import import_module
from pkgutil import iter_modules

from swag.core import commands


def execute_from_command_line():
    parser = argparse.ArgumentParser(prog='swag')
    parser.add_argument('--debug', action='store_true')
    subparsers = parser.add_subparsers()

    commands_path = os.path.dirname(commands.__file__)
    subprograms = [
        [command] + command.info()
        for command
        in [import_module('swag.core.commands.' + name) for _, name, _ in iter_modules([commands_path])]
    ]

    for module, command, description in subprograms:
        subp = subparsers.add_parser(
            command,
            description=description,
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        subp.set_defaults(func=module.main)
        module.populate_parser(subp)

    args = parser.parse_args()

    # If no subcommand is given, print help and exit
    if not hasattr(args, 'func'):
        parser.print_help()
        sys.exit()

    try:
        args.func(vars(args))
    except Exception as e:
        # TODO More helpful error messages
        sys.stderr.write('An error occured:\n{}\n'.format(repr(e)))
        if args.debug:
            sys.stderr.write('\nTraceback:\n')
            _, _, tb = sys.exc_info()
            traceback.print_tb(tb)
