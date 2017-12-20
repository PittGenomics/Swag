#! /usr/bin/env python
import os
import argparse
import subprocess
import re
from datetime import datetime

import swiftseq.util
from swiftseq.util.path import is_valid_file
from swiftseq.core.exceptions import EnvironmentVariableException
from swiftseq.core import SwiftSeqSupported


def info():
    return ['install-env', None]


def populate_parser(parser):
    parser.add_argument('--name', help='Name of the conda environment created.')
    parser.add_argument('--exe-file-location', default='executables.config',
                        help='Path to write generated executables file.')


def main(args=None):
    # Ensure conda is installed
    if subprocess.call('condda >/dev/null 2>/dev/null', shell=True) != 0:
        print('\'conda\' executable not found, please install it before proceeding by '
              'visiting https://conda.io/miniconda.html')

    # Get arguments if this is being executed directly
    if not args:
        parser = argparse.ArgumentParser(prog='swiftseq restart')
        populate_parser(parser)
        args = vars(parser.parse_args())

    # Get information about environment
    conda_env_name = args['name'] or 'swiftseq_{}'.format(datetime.now().strftime('%d%b%Y'))
    packages = SwiftSeqSupported.conda_install_packages

    # Check for current channels with conda config --show-sources
    show_sources = subprocess.check_output(['conda', 'config', '--show-sources']).decode()
    old_channels = re.findall(r'\s+- (\S+)\n', show_sources)
    new_channels = ['r', 'defaults', 'conda-forge', 'bioconda']

    # Install new channels temporarily
    for channel in new_channels:
        subprocess.call(['conda', 'config', '--add', 'channels', channel])

    # Create new conda environment and install packages
    subprocess.call(['conda', 'create', '--yes', '--name', conda_env_name] + packages)

    # Uninstall new channels
    for channel in new_channels:
        subprocess.call(['conda', 'config', '--remove', 'channels', channel])

    # Reinstate old order of old channels
    for channel in old_channels[::-1]:
        subprocess.call(['conda', 'config', '--add', 'channels', channel])


if __name__ == '__main__':
    main()
