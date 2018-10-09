#! /usr/bin/env python

"""
Written by Jason Pitt
    Github: JasonJPitt
Modified by Dominic Fitzgerald on 24 August 2017
    Github: djf604

swag run [args]
The entry point for starting a new Swag run.
"""
from __future__ import print_function

import os
import argparse
import subprocess
import logging
import re
import uuid
import json
from datetime import datetime
from multiprocessing import cpu_count
from tempfile import gettempdir

import parsl

import swag.util
import swag.parsl.wrappers
from swag.core.config import SwagConfig, load_config
from swag.core import SwagStrings
from swag.core.input import process_samples, find_data_filepaths
from swag.core.contigs import create_contigs_files
from swag.core.exceptions import EnvironmentVariableException
from swag.core.workflow import Workflow, compose_workflow_wrappers
from swag.parsl.process import germline, tumor_normal
from swag.util.path import is_valid_dir, is_valid_file, is_valid_tmp_dir, mkdirs

FIRST = 0
RAM_POOL_MEM = 7500

logger = logging.getLogger(__name__)


def info():
    return ['run', None]

def populate_parser(parser):
    parser.add_argument('config',
        help='Path to config file. The Config file should contain one\n'
             'instance of the swag.config.Config class, which has the\n'
             'following parameters.\n\n{}'.format(SwagConfig.__doc__.lstrip('\n    '))
    )

def main(args=None):
    if not args:
        parser = argparse.ArgumentParser(prog='swag run')
        populate_parser(parser)
        args = parser.parse_args()

    config = load_config(args.config)

    # Make sure appropriate environment variables are present
    for environ_var in ('PATH', 'LD_LIBRARY_PATH'):
        if environ_var not in os.environ:
            raise EnvironmentVariableException(environ_var)

    # Get bundles util scripts
    util_scripts = swag.util.get_util_scripts()

    # subprocess.call('$SHELL {cmd}'.format(cmd=util_scripts['util_graphic']), shell=True)
    swag.util.message_to_screen('\nPreparing run...\n')

    # Create working logging directory
    mkdirs(os.path.join(os.getcwd(), SwagStrings.worker_logging_dir))

    # Get current directory and parse configs
    work_dir = os.path.abspath(os.getcwd())  # Absolute path
    exe_config = swag.util.parse_config(config.exe_config)
    ref_config = swag.util.parse_config(config.ref_config)
    # Makes a new dir in the current directory called 'wrappers'
    wrapper_dir = mkdirs(os.path.join(work_dir, SwagStrings.wrapper_dir))
    out_dir = 'analysis'  # TODO Allow user to change this
    mkdirs(os.path.join(work_dir, out_dir))

    # Calculate some option values
    packing_cores = str(max(1, int(config.cores_per_node / config.tasks_per_node)))
    gc_cores = max(1, int((config.cores_per_node - config.tasks_per_node) / config.tasks_per_node))
    gc_flag = '-XX:+UseParallelGC -XX:ParallelGCThreads={}'.format(gc_cores) if gc_cores else ''
    java_mem = '-Xmx{}m'.format(int(config.ram_per_node / config.tasks_per_node))
    ram_pool_mem = '-Xmx{}m'.format(RAM_POOL_MEM)

    # Parse Workflow
    workflow = Workflow(json.load(open(config.workflow)))
    swag.util.message_to_screen('Executing the following workflow...', banner=True)
    workflow.print_workflow_config()

    # Compose workflow wrappers
    workflow_wrappers_options = {
        'tmp_dir': config.tmp,
        'env_PATH': os.environ['PATH'],
        'env_LD_LIBRARY_PATH': os.environ['LD_LIBRARY_PATH'],
        'exe_config': exe_config,
        'ref_config': ref_config,
        'gc_flag': gc_flag,
        'java_mem': java_mem,
        'max_cores': config.cores_per_node,
        'max_mem': config.ram_per_node,
        'packing_cores': packing_cores,
        'ram_pool_mem': ram_pool_mem,
        'wrapper_dir': wrapper_dir,
        'worker_has_tmp': config.worker_use_tmp,
        'out_dir': out_dir

    }
    workflow_wrappers_options.update(util_scripts)
    compose_workflow_wrappers(workflow, **workflow_wrappers_options)

    parsl.load(config.parsl_config)

    # Gather input files
    swag.util.message_to_screen('Gathering input files and read group information...', banner=True)
    individuals_analyzed, samples_analyzed, inputdata_symlinks = process_samples(
        inputdata_type=workflow.data_type,
        inputdata_filepaths=find_data_filepaths(config.data, '.bam'),
        data_root=config.data,
        analysis_root=out_dir,
        samtools_path=exe_config['samtools']
    )

    # Create contig files
    contigs_file_filepath = create_contigs_files(
        picard_ref_seq_dict=ref_config['refDict'],
        contig_interval_size=config.geno_segment_size,
        swag_analysis_dir=out_dir,
        swag_inputdata_symlinks=inputdata_symlinks
    )

    if workflow.data_type == Workflow.GERMLINE:
        swag.util.message_to_screen('Number of samples analyzed: {}\n'.format(samples_analyzed))
        germline(workflow, work_dir, contigs_file_filepath, out_dir)
    else:
        swag.util.message_to_screen('Number of individuals to be analyzed: {}\n'.format(individuals_analyzed))
        swag.util.message_to_screen(
            'Number of samples (cancer and non-cancer) to be analyzed: {}\n'.format(samples_analyzed)
        )
        tumor_normal(workflow, work_dir, contigs_file_filepath, out_dir)

if __name__ == '__main__':
    main()
