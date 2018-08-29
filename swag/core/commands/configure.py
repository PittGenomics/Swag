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
    return ['configure', None]


def populate_parser(parser):
    """
    Can we make the environment variables configurable from the command line?
    :param parser:
    :return:
    """
    parser.add_argument('--data', required=True,
                        help='The data directory containing sequencing data to be run (Required).')
    parser.add_argument('--workflow', required=True,
                        help='The Swag workflow (in .json format) that will be run over input data (Required).')
    # parser.add_argument('--parsl-config', default='Parsl.conf',
    #                     help='Path to a pre-made Parsl configuration file. If this is given, '
    #                          'all other config related parameters will be ignored.')
    parser.add_argument('--ref-config', required=True,
                        help='Configuration file that contains paths to required reference files (Required).')
    parser.add_argument('--exe-config', required=True,
                        help='Configuration file that contains paths algorithm executables (Required).')
    # parser.add_argument('--parsl-path', default='parsl', help='If provided, will use this path as the full path to the '
    #                                                           'Parsl executable; otherwise, defaults to finding Parsl '
    #                                                           'in PATH.')
    parser.add_argument('--run-name', default='Swag_{date}_{id}'.format(
                            date=datetime.now().strftime('%d%b%Y'),
                            id=str(uuid.uuid4())[:8]
                        ),
                        help='The name of the run (Default = Swag_<date>_<id>).')
    """
    Check that runname is saved into restart.conf file
    """
    # The tempfile.gettempdir() directory will first try to set it to the environment variable $TMPDIR, and if that
    # fails then will default to OS-specific temp directory
    parser.add_argument('--tmp', default=gettempdir(),
                        help='Temporary directory for this run.')
    parser.add_argument('--foreach-max', type=int, default=300,
                        help='The maximum number of simultaneous iterations per for loop in Parsl (Default = 300).')
    parser.add_argument('--num-nodes', type=int, default=1,
                        help='The number of worker nodes (per pool) available to Swag for processing (Required).')
    parser.add_argument('--cores-per-node', type=int, default=cpu_count(),
                        help='Number of processing cores available per '
                             'worker node (Default = <num cores on head node>).')
    parser.add_argument('--tasks-per-node', type=int, default=8,
                        help='Number of tasks to pack (run simultaneously) on each worker node (Default = 8).')
    parser.add_argument('--ram-per-node', type=int, default=29000,
                        help='Amount of RAM in megabytes available on each worker node (Default = 29000).')

    parser.add_argument('--heap-max', type=int, default=2500,
                        help='Java max heap size in megabytes for the Parsl process '
                             'running on the headnode (Default = 2500)')
    parser.add_argument('--gc-threads', type=int, default=1,
                        help='Number of threads dedicated for parallel garbage '
                             'collection on the Parsl process (Default = 1)')
    parser.add_argument('--job-time', default='48:00:00',
                        help='The maximum walltime (hh:mm:ss format) for a given '
                             'Parsl coaster block i.e. the max job time (Default = 48:00:00).')
    parser.add_argument('--max-IO', type=int, default=200,
                        help='The maximum number of IO intensive processes to run concurrently (Default = 200).')

    parser.add_argument('--retries', type=int, default=2,
                        help='The number of times an app should be re-executed after a failure (Default = 2)')
    parser.add_argument('--project-id',
                        help='Project ID used to submit and run jobs through a scheduler (Default = None).')
    parser.add_argument('--executor', default='scheduler', choices=['scheduler', 'local'],
                        help='Executor for this Parsl run.')
    parser.add_argument('--job-manager', default='local:pbs',
                        help='Software used to submit and manage jobs [pbs, slurm, sge], only used if --executor is '
                             'set to \'scheduler\'.')
    parser.add_argument('--job-options',
                        help='String that will be provided to jobOptions portion of the parsl json '
                             'config file (Default = None).\nThis string should be a ; separated '
                             'list of job options.')
    parser.add_argument('--queue', help='Queue that will be used by the job-manager for '
                                        'job submissions (Default = None).')
    parser.add_argument('--disable-lazy-errors', action='store_true',
                        help='If a task fails, prevent Swag from continuing with running the remaining '
                             'independent tasks. For any Swag runs with >1 samples this is not recommended.')
    parser.add_argument('--worker-use-tmp', action='store_true',
                        help='Have wrappers use /tmp on the working as temp space. Should assist in reducing '
                             'overall IO burden')
    parser.add_argument('--geno-segment-size', type=int, default=10000000,
                        help='Size of the segment used by any variant calling process (Default = 10000000).')


def main(args=None):
    if not args:
        parser = argparse.ArgumentParser(prog='swag configure')
        populate_parser(parser)
        args = vars(parser.parse_args())

    # Checks with arguments
    is_valid_dir(args['data'])
    is_valid_tmp_dir(args['tmp'])
    is_valid_file(args['workflow'])
    is_valid_file(args['ref_config'])
    is_valid_file(args['exe_config'])
    if re.match(r'^\d+:\d{2}:\d{2}$', args['job_time']) is None:
        raise ValueError('{} is not in HH:MM:SS format.'.format(args['job_time']))

    # Make sure appropriate environment variables are present
    for environ_var in ('PATH', 'SWIFT_HOME', 'SWIFT_USERHOME', 'LD_LIBRARY_PATH'):
        if environ_var not in os.environ:
            raise EnvironmentVariableException(environ_var)

    # Get bundles util scripts
    util_scripts = swag.util.get_util_scripts()

    # Set some environment variables for future use
    # os.environ['SWIFT_HEAP_MAX'] = '{}M'.format(args['heap_max'])
    # os.environ['COG_OPTS'] = '-XX:+UseParallelGC -XX:ParallelGCThreads={}'.format(args['gc_threads'])

    # Create working logging directory
    mkdirs(os.path.join(os.getcwd(), SwagStrings.worker_logging_dir))

    # Get current directory and parse configs
    work_dir = os.getcwd()  # Absolute path
    # work_dir = '.'  # Relative path
    exe_config = swag.util.parse_config(args['exe_config'])
    ref_config = swag.util.parse_config(args['ref_config'])
    # Makes a new dir in the current directory called 'wrappers'
    wrapper_dir = mkdirs(os.path.join(work_dir, SwagStrings.wrapper_dir))
    out_dir = 'analysis'  # TODO Allow user to change this
    mkdirs(os.path.join(work_dir, out_dir))

    # Calculate some option values
    packing_cores = str(max(1, int(args['cores_per_node'] / args['tasks_per_node'])))
    gc_cores = max(1, int((args['cores_per_node'] - args['tasks_per_node']) / args['tasks_per_node']))
    gc_flag = '-XX:+UseParallelGC -XX:ParallelGCThreads={}'.format(gc_cores) if gc_cores else ''
    java_mem = '-Xmx{}m'.format(int(args['ram_per_node'] / args['tasks_per_node']))
    ram_pool_mem = '-Xmx{}m'.format(RAM_POOL_MEM)

    # Parse Workflow
    workflow = Workflow(json.load(open(args['workflow'])))
    swag.util.message_to_screen('Executing the following workflow...', banner=True)
    workflow.print_workflow_config()

    # Compose workflow wrappers
    workflow_wrappers_options = {
        'tmp_dir': args['tmp'],
        'env_PATH': os.environ['PATH'],
        'env_LD_LIBRARY_PATH': os.environ['LD_LIBRARY_PATH'],
        'exe_config': exe_config,
        'ref_config': ref_config,
        'gc_flag': gc_flag,
        'java_mem': java_mem,
        'max_cores': args['cores_per_node'],
        'max_mem': args['ram_per_node'],
        'packing_cores': packing_cores,
        'ram_pool_mem': ram_pool_mem,
        'wrapper_dir': wrapper_dir,
        'worker_has_tmp': args['worker_use_tmp'],
        'out_dir': out_dir

    }
    workflow_wrappers_options.update(util_scripts)
    compose_workflow_wrappers(workflow, **workflow_wrappers_options)

    # Gather input files
    swag.util.message_to_screen('Gathering input files and read group information...', banner=True)
    individuals_analyzed, samples_analyzed, inputdata_symlinks = process_samples(
        inputdata_type=workflow.data_type,
        inputdata_filepaths=find_data_filepaths(args['data'], '.bam'),
        data_root=args['data'],
        analysis_root=out_dir,
        samtools_path=exe_config['samtools']
    )

    # Create contig files
    contigs_file_filepath = create_contigs_files(
        picard_ref_seq_dict=ref_config['refDict'],
        contig_interval_size=args['geno_segment_size'],
        swag_analysis_dir=out_dir,
        swag_inputdata_symlinks=inputdata_symlinks
    )

    # Use or compose Parsl configuration
    parsl_conf_filepath = create_parsl_config(**{
        'wrapper_dir': wrapper_dir,
        'tmp_dir': args['tmp'],
        'disable_lazy_errors': args['disable_lazy_errors'],
        'retries': args['retries'],
        'job_manager': args['job_manager'],
        'tasks_per_node': args['tasks_per_node'],
        'queue': args['queue'],
        'num_nodes': args['num_nodes'],
        'job_time': args['job_time'],
        'work_dir': work_dir,
        'project_id': args['project_id'],
        'job_options': args['job_options'],
        'workflow': workflow,
        'executor': args['executor']
    })

    # Compose Parsl script based on run type, output information to user
    if workflow.data_type == Workflow.GERMLINE:
        swag.util.message_to_screen('Number of samples analyzed: {}\n'.format(samples_analyzed))
        parsl_script = germline_parsl(workflow, work_dir, contigs_file_filepath, out_dir)
    else:
        swag.util.message_to_screen('Number of individuals to be analyzed: {}\n'.format(individuals_analyzed))
        swag.util.message_to_screen(
            'Number of samples (cancer and non-cancer) to be analyzed: {}\n'.format(samples_analyzed)
        )
        parsl_script = tumor_normal_parsl(workflow, work_dir, contigs_file_filepath, out_dir)

    # Write restart config file
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
    # subprocess.call('{parsl_exe} -config {parsl_config} {parsl_script}'.format(
    #     parsl_exe=args['parsl_path'],
    #     parsl_config=parsl_conf_filepath,
    #     parsl_script=parsl_script
    # ), shell=True)


if __name__ == '__main__':
    main()