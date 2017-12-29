#! /usr/bin/env python
import os
import sys
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
    parser.add_argument('--conda-path', help='Path to the conda executable.')
    parser.add_argument('--exe-config-location', default='executables.config',
                        help='Path to write generated executables file.')


def main(args=None):
    # Get arguments if this is being executed directly
    if not args:
        parser = argparse.ArgumentParser(prog='swiftseq install-env')
        populate_parser(parser)
        args = vars(parser.parse_args())

    # Ensure conda is installed
    check_conda_cmd = '{conda} >/dev/null 2>/dev/null'.format(
        conda=args['conda_path'] or 'conda'
    )
    if subprocess.call(check_conda_cmd, shell=True) != 0:
        print('\'conda\' executable not found, please install it before proceeding by '
              'visiting https://conda.io/miniconda.html')
        sys.exit(1)
    conda_path = args['conda_path'] or subprocess.check_output('which conda', shell=True).strip().decode()

    # Get information about environment
    conda_env_name = args['name'] or 'swiftseq_{}'.format(datetime.now().strftime('%d%b%Y'))
    packages = [p[0] for p in SwiftSeqSupported.conda_install_packages]

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

    # Write out executables config
    with open(args['exe_config_location'], 'w') as exe_config:
        # Write out header
        exe_config.write('#' * 15 + '\n')
        exe_config.write('# executables\n')
        exe_config.write('#' * 15 + '\n')

        for installed_program_tag, conda_bin_name in SwiftSeqSupported.conda_install_packages:
            program_name = installed_program_tag.split('=')[0]
            program_path = os.path.join(conda_path, 'envs', conda_env_name, 'bin', conda_bin_name)
            exe_config.write('{name}={path}\n'.format(name=program_name, path=program_path))


if __name__ == '__main__':
    main()
