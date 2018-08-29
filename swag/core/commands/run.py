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
import re
import uuid
import json
from datetime import datetime
from multiprocessing import cpu_count
from tempfile import gettempdir

import swag.util
import swag.parsl.wrappers
from swag.core import SwagStrings
from swag.core.input import process_samples, find_data_filepaths
from swag.core.contigs import create_contigs_files
from swag.core.exceptions import EnvironmentVariableException
from swag.core.workflow import Workflow, compose_workflow_wrappers
from swag.parsl.config import create_parsl_config
from swag.parsl.generate import germline_parsl, tumor_normal_parsl
from swag.util.path import is_valid_dir, is_valid_file, is_valid_tmp_dir, mkdirs

FIRST = 0
RAM_POOL_MEM = 7500


# This arg parse will handle all of the details how the workflow runs
# Will not handle details of underlying algorithms (except num cores)
# This latter aspect will be handled by the json and the GUI

# Here we need to think about how to gather all variables required to run
# onBeagle and other locations
# Need to set
# -------------------
# LD_LIBRARY_PATH
# CLASSPATH (for gatk queue) $gatkQueue:$grpReduceDir
# ^ Force these to be our compiled version with queue... having this required
# will be tricky...Talk to Lorenzo about this
# /soft/python/2.7/2.7.3-vanilla/python/lib


"""
Arguments that need to be added to argparse

- restart

"""


def info():
    return ['run', None]


def populate_parser(parser):
    """
    Can we make the environment variables configurable from the command line?
    :param parser:
    :return:
    """
    parser.add_argument('--parsl-config', default='Parsl.conf',
                        help='Path to a pre-made Parsl configuration file. If this is given, '
                             'all other config related parameters will be ignored.')
    parser.add_argument('--parsl-path', default='parsl', help='If provided, will use this path as the full path to the '
                                                              'Parsl executable; otherwise, defaults to finding Parsl '
                                                              'in PATH.')
    parser.add_argument('--parsl-script', default=SwagStrings.parsl_script_filename,
                        help='Path to a Parsl script TODO')
    parser.add_argument('--heap-max', type=int, default=2500,
                        help='Java max heap size in megabytes for the Parsl process '
                             'running on the headnode (Default = 2500)')
    parser.add_argument('--gc-threads', type=int, default=1,
                        help='Number of threads dedicated for parallel garbage '
                             'collection on the Parsl process (Default = 1)')


def main(args=None):
    if not args:
        parser = argparse.ArgumentParser(prog='swag run')
        populate_parser(parser)
        args = vars(parser.parse_args())

    # Make sure appropriate environment variables are present
    # TODO Is this needed here?
    for environ_var in ('PATH', 'SWIFT_HOME', 'SWIFT_USERHOME', 'LD_LIBRARY_PATH'):
        if environ_var not in os.environ:
            raise EnvironmentVariableException(environ_var)

    # Get bundles util scripts
    util_scripts = swag.util.get_util_scripts()

    # Output welcome to the user
    subprocess.call('$SHELL {cmd}'.format(cmd=util_scripts['util_graphic']), shell=True)
    swag.util.message_to_screen('\nPreparing run...\n')

    # Set some environment variables for future use
    os.environ['SWIFT_HEAP_MAX'] = '{}M'.format(args['heap_max'])
    os.environ['COG_OPTS'] = '-XX:+UseParallelGC -XX:ParallelGCThreads={}'.format(args['gc_threads'])


    # Calculate some option values
    # packing_cores = str(int(args['cores_per_node'] / args['tasks_per_node']))
    # gc_cores = max(0, int((args['cores_per_node'] - args['tasks_per_node']) / args['tasks_per_node']))
    # gc_flag = '-XX:+UseParallelGC -XX:ParallelGCThreads={}'.format(gc_cores) if gc_cores else ''
    # java_mem = '-Xmx{}m'.format(int(args['ram_per_node'] / args['tasks_per_node']))
    # ram_pool_mem = '-Xmx{}m'.format(RAM_POOL_MEM)

    # Parse Workflow
    # workflow = Workflow(json.load(open(args['workflow'])))
    # swag.util.message_to_screen('Executing the following workflow...', banner=True)
    # workflow.print_workflow_config()

    # Compose workflow wrappers
    # workflow_wrappers_options = {
    #     'tmp_dir': args['tmp'],
    #     'env_PATH': os.environ['PATH'],
    #     'env_LD_LIBRARY_PATH': os.environ['LD_LIBRARY_PATH'],
    #     'exe_config': exe_config,
    #     'ref_config': ref_config,
    #     'gc_flag': gc_flag,
    #     'java_mem': java_mem,
    #     'max_cores': args['cores_per_node'],
    #     'max_mem': args['ram_per_node'],
    #     'packing_cores': packing_cores,
    #     'ram_pool_mem': ram_pool_mem,
    #     'wrapper_dir': wrapper_dir,
    #     'worker_has_tmp': args['worker_use_tmp'],
    #     'out_dir': out_dir
    # }
    # workflow_wrappers_options.update(util_scripts)
    # compose_workflow_wrappers(workflow, **workflow_wrappers_options)

    # Gather input files
    # swag.util.message_to_screen('Gathering input files and read group information...', banner=True)
    # individuals_analyzed, samples_analyzed, inputdata_symlinks = process_samples(
    #     inputdata_type=workflow.data_type,
    #     inputdata_filepaths=find_data_filepaths(args['data'], '.bam'),
    #     data_root=args['data'],
    #     analysis_root=out_dir,
    #     samtools_path=exe_config['samtools']
    # )

    # Create contig files
    # contigs_file_filepath = create_contigs_files(
    #     picard_ref_seq_dict=ref_config['refDict'],
    #     contig_interval_size=args['geno_segment_size'],
    #     swag_analysis_dir=out_dir,
    #     swag_inputdata_symlinks=inputdata_symlinks
    # )

    # Use or compose Parsl configuration
    # parsl_conf_filepath = args['parsl_config'] if args['parsl_config'] else create_parsl_config(**{
    #     'wrapper_dir': wrapper_dir,
    #     'tmp_dir': args['tmp'],
    #     'disable_lazy_errors': args['disable_lazy_errors'],
    #     'retries': args['retries'],
    #     'job_manager': args['job_manager'],
    #     'tasks_per_node': args['tasks_per_node'],
    #     'queue': args['queue'],
    #     'num_nodes': args['num_nodes'],
    #     'job_time': args['job_time'],
    #     'work_dir': work_dir,
    #     'project_id': args['project_id'],
    #     'job_options': args['job_options'],
    #     'workflow': workflow
    # })
    #
    # # Compose Parsl script based on run type, output information to user
    # if workflow.data_type == Workflow.GERMLINE:
    #     swag.util.message_to_screen('Number of samples analyzed: {}\n'.format(samples_analyzed))
    #     parsl_script = germline_parsl(workflow, work_dir, contigs_file_filepath, out_dir)
    # else:
    #     swag.util.message_to_screen('Number of individuals to be analyzed: {}\n'.format(individuals_analyzed))
    #     swag.util.message_to_screen(
    #         'Number of samples (cancer and non-cancer) to be analyzed: {}\n'.format(samples_analyzed)
    #     )
    #     parsl_script = tumor_normal_parsl(workflow, work_dir, contigs_file_filepath, out_dir)
    #
    # # Write restart config file
    # with open(SwagStrings.restart_conf_filename, 'w') as restart_conf:
    #     restart_conf.write('\n'.join((
    #         'parsl={}'.format(args['parsl_path']),
    #         'conf={}'.format(parsl_conf_filepath),
    #         'parslScript={}'.format(parsl_script),
    #         'SWIFT_HOME={}'.format(os.environ['SWIFT_HOME']),
    #         'SWIFT_USERHOME={}'.format(os.environ['SWIFT_USERHOME'])
    #     )) + '\n')

    # Execute parsl command
    # TODO See if we can execute this not as a direct shell, for security reasons
    subprocess.call('{parsl_exe} -config {parsl_config} {parsl_script}'.format(
        parsl_exe=args['parsl_path'],
        parsl_config=args['parsl_config'],
        parsl_script=SwagStrings.parsl_script_filename
    ), shell=True)


if __name__ == '__main__':
    main()