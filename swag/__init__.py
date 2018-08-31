import os
import sys
import argparse
import traceback
import logging

from importlib import import_module
from pkgutil import iter_modules

from swag.core import commands

logger = logging.getLogger(__name__)

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
            formatter_class=argparse.RawTextHelpFormatter
        )
        subp.set_defaults(func=module.main)
        module.populate_parser(subp)

    args = parser.parse_args()

    # If no subcommand is given, print help and exit
    if not hasattr(args, 'func'):
        parser.print_help()
        sys.exit()

    level = logging.INFO
    if args.debug:
        level = logging.DEBUG
    logger.setLevel(level)
    format = "%(asctime)s %(name)s:%(lineno)d [%(levelname)s]  %(message)s"
    formatter = logging.Formatter(format, datefmt='%Y-%m-%d %H:%M:%S')
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)

    # logger.info("saving log to {0}".format(os.path.join(cfg.workdir, fn)))
    # if not os.path.isdir(cfg.workdir):
    #     os.makedirs(cfg.workdir)
    # fileh = logging.handlers.RotatingFileHandler(os.path.join(cfg.workdir, fn), maxBytes=100e6, backupCount=10)
    # fileh.setFormatter(formatter)
    # fileh.setLevel(logging.INFO)
    # for p in args.plugin.blacklisted_logs():
    #     fileh.addFilter(util.InvertedFilter('lobster.' + p))
    # args.preserve.append(fileh.stream)
    # logger.addHandler(fileh)

    args.func(args)
