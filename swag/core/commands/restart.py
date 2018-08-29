#! /usr/bin/env python
import os
import argparse
import subprocess

import swag.util
from swag.util.path import is_valid_file
from swag.core.exceptions import EnvironmentVariableException


def info():
    return ['restart', None]


def populate_parser(parser):
    parser.add_argument('--restart-log', required=True,
                        help='The Swag restart log (rlog). Will be used to determine and '
                             'execute remaining tasks (Required).')
    parser.add_argument('--config', required=True,
                        help='The Swag config log. Contains paths to config files required by Parsl (Required).')
    parser.add_argument('--parsl-path', default='parsl', help='If provided, will use this path as the full path to the '
                                                              'Parsl executable; otherwise, defaults to finding Parsl '
                                                              'in PATH.')
    parser.add_argument('--heap-max', type=int, default=2500,
                            help='Java max heap size in megabytes for the Parsl process '
                                 'running on the headnode (Default = 2500)')
    parser.add_argument('--gc-threads', type=int, default=1,
                            help='Number of threads dedicated for parallel garbage '
                                 'collection on the Parsl process (Default = 1)')


def main(args=None):
    if not args:
        parser = argparse.ArgumentParser(prog='swag restart')
        populate_parser(parser)
        args = vars(parser.parse_args())

    # Checks with arguments
    is_valid_file(args['restart_log'])
    is_valid_file(args['config'])

    # Get bundles util scripts
    util_scripts = swag.util.get_util_scripts()

    # Output welcome to the user
    subprocess.call(util_scripts['util_graphic'], shell=True)
    swag.util.message_to_screen('\nPreparing to restart Swag run...\n')

    # Get config dict
    restart_config = swag.util.parse_config(args['config'])
    required_keys = {'parsl', 'conf', 'parslScript', 'SWIFT_HOME', 'SWIFT_USERHOME'}
    if not required_keys.issubset(restart_config):
        raise KeyError('Required arguments {} not found in config file {}'.format(
            '{{{}}}'.format(', '.join(required_keys.difference(restart_config))),
            args['config'].strip()
        ))

    # Make sure appropriate environment variables are present
    if 'PATH' not in os.environ:
        raise EnvironmentVariableException('PATH')

    # Set environment variables
    os.environ['SWIFT_HEAP_MAX'] = '{}M'.format(args['heap_max'])
    os.environ['COG_OPTS'] = '-XX:+UseParallelGC -XX:ParallelGCThreads={}'.format(args['gc_threads'])
    os.environ['SWIFT_HOME'] = restart_config['SWIFT_HOME']
    os.environ['SWIFT_USERHOME'] = restart_config['SWIFT_USERHOME']

    # Re-run Swag using the configs are rlog provided
    subprocess.call('{parsl_exe} -resume {restart_log} -config {restart_conf} {parsl_script}'.format(
        parsl_exe=args['parsl_path'],
        restart_log=args['restart_log'],
        restart_conf=restart_config['conf'],
        parsl_script=restart_config['parslScript']
    ), shell=True)

if __name__ == '__main__':
    main()
