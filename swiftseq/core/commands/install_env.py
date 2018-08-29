#! /usr/bin/env python
import os
import sys
import argparse
import subprocess
import re
from glob import glob
from datetime import datetime

import six

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
    parser.add_argument('--novo-license-path', help='Path to a novocraft software suite license file.')


def get_conda_env_location(conda_path, conda_env_name):
    return [
        env_name.split()[1]
        for env_name in subprocess.check_output([conda_path, 'env', 'list']).decode().split('\n')
        if conda_env_name in env_name
    ][0]


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
    packages = [p['bioconda_tag'] for p in SwiftSeqSupported.conda_install_packages]

    # Check for current channels with conda config --show-sources
    show_sources = subprocess.check_output([conda_path, 'config', '--show-sources']).decode()
    old_channels = re.findall(r'\s+- (\S+)\n', show_sources)
    new_channels = ['r', 'defaults', 'conda-forge', 'bioconda']

    # Install new channels temporarily
    for channel in new_channels:
        subprocess.call([conda_path, 'config', '--add', 'channels', channel])

    # Create new conda environment and install packages
    subprocess.call([conda_path, 'create', '--yes', '--name', conda_env_name] + packages)

    # Uninstall new channels
    for channel in new_channels:
        subprocess.call([conda_path, 'config', '--remove', 'channels', channel])

    # Reinstate old order of old channels
    for channel in old_channels[::-1]:
        subprocess.call([conda_path, 'config', '--add', 'channels', channel])

    # Get path to newly created conda env
    conda_env_dir = get_conda_env_location(conda_path, conda_env_name)

    # Write out executables config
    with open(args['exe_config_location'], 'w') as exe_config:
        # Write out header
        exe_config.write('#' * 15 + '\n')
        exe_config.write('# executables\n')
        exe_config.write('#' * 15 + '\n')

        # conda_dir = os.path.split(os.path.split(conda_path)[0])[0]
        for package_config in SwiftSeqSupported.conda_install_packages:
            executable_key = (
                (
                    [package_config['exe_key']]
                    if isinstance(package_config['exe_key'], six.string_types)
                    else package_config['exe_key']
                )
                if 'exe_key' in package_config
                else [package_config['bioconda_tag'].split('=')[0]]
            )
            # program_name = package_config['bioconda_tag'].split('=')[0]
            executable_names = (
                [package_config['exe_name']]
                if isinstance(package_config['exe_name'], six.string_types)
                else package_config['exe_name']
            )
            for exec_key, exe_name in zip(executable_key, executable_names):
                rel_path = package_config.get('rel_path', 'bin')
                if '*' in rel_path:
                    _rel = glob(os.path.join(conda_env_dir, rel_path))[0]
                else:
                    _rel = os.path.join(conda_env_dir, rel_path)
                exe_path = os.path.join(_rel, exe_name)



                # exe_path = os.path.join(conda_env_dir, package_config.get('rel_path', 'bin'), exe_name)
                exe_config.write('{name}={path}\n'.format(name=exec_key, path=exe_path))

            if 'post_hook' in package_config:
                package_config['post_hook'](conda_env_dir, **args)


if __name__ == '__main__':
    main()
