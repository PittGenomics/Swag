"""
Written by Jason Pitt
Revised by Dominic Fitzgerald on 30 May 2017

swiftseq run [args]
The entry point for starting a new SwiftSeq run.
"""
import os
import warnings
from collections import defaultdict
from itertools import product

import six

from swiftseq.core import SwiftSeqStrings
from swiftseq.core.readgroups import create_readgroup_files
from swiftseq.core.workflow import Workflow
from swiftseq.util.path import mkdirs, mksym

ROOT = 0

GERMLINE = 100
TUMOR_NORMAL_PAIRS = 101

PATIENT_NAME = -1
BEFORE_EXTENSION = 0
EXTENSION = 1

""" First just write this so it can find the appropriate files and make
the proper directories. Later, add sanity checks, ability to handle .RG
info, fastqs, etc. """


#########
# TO-DO
#########

# Need to handle if RG ID contains non-ascii
# Need to determine how Picard handles RG ID
# Should likely be writing results to some form of set-up log

"""
Common Functions
"""


def create_analysis_dir(inputdata_type, inputdata_filepaths, inputdata_dir_root, analysis_dir_root):
    """
    Verifies that the root of the directory given as input adheres to the required directory structure
    before the rest of the program proceeds. Anything that violates the requirements are ignored. Everything
    that passed verification is then re-created structurally at a different root; this becomes the
    place where all analysis results will be written to. The inputdata files in the analysis directory
    are replaced with symbolic links back to the original files.

    Side effects: Re-creates the original data file structure using symlinks in place of
    the actual files

    :param data_type: str Either Workflow.TUMOR_NORMAL_PAIR or Workflow.GERMLINE; else will throw an exception
    :param data_filepaths: list Relative paths of the original data files
    :param data_dir_root: str Path to the directory housing all the original data
    :param analysis_dir_root: str Path to the root of the location for the analysis results
    :return: list Relative paths to all symlinks linked to the original data
    """
    # Verify the correct directory structure
    verified_filepaths = list()
    if inputdata_type == Workflow.TUMOR_NORMAL_PAIR:
        for data_filepath in inputdata_filepaths:
            if data_filepath.split('/')[-3] not in {'tumor', 'normal'}:
                warnings.warn('Warning: {} does not adhere to required directory structure. Will be ignored'.format(
                    data_filepath
                ))
                continue
            verified_filepaths.append(data_filepath)
    elif inputdata_type == Workflow.GERMLINE:
        for data_filepath in inputdata_filepaths:
            parent_dir = os.path.join(inputdata_dir_root, os.path.dirname(data_filepath))
            num_bam_files = len(
                [f for f in os.listdir(parent_dir)
                 if os.path.splitext(f)[EXTENSION] == '.bam']
            )

            if num_bam_files > 1:
                warnings.warn('Warning: {} does not adhere to required directory structure (multiple '
                              'seq files in the same directory). Will be ignored'.format(data_filepath))
                continue
            verified_filepaths.append(data_filepath)
    else:
        raise ValueError('Unsupported data type: {}'.format(inputdata_type))

    # Create symlinks in the analysis directory
    verified_symlinks = list()
    for data_filepath in verified_filepaths:
        source_filepath = os.path.join(inputdata_dir_root, data_filepath)
        destination_symlink = os.path.join(analysis_dir_root, data_filepath)
        try:
            mksym(source_filepath, destination_symlink)
        except (os.error, AttributeError):
            warnings.warn('Could not create a symbolic link to {} for {}'.format(
                destination_symlink,
                source_filepath
            ))
            continue
        verified_symlinks.append(destination_symlink)

    return verified_symlinks


def find_data_filepaths(swiftseq_data_dir, suffix):
    """
    Traverses the data directory to find files that end with suffix. Returns a list
    of filepaths relative to the data directory of those ending with suffix.

    Side effects: None

    :param swiftseq_data_dir: str Root of the swiftseq data directory
    :param suffix: str Suffix to search for
    :return: list Relative paths of those files ending with suffix
    """
    filepaths_with_suffix = list()
    for root, dirs, files in os.walk(swiftseq_data_dir, followlinks=True):
        # If no files exist, raise an exception
        # if not files:
        #     raise Exception('No files found in the data directory. '
        #                     'Please check input files and data directory structure.')

        # Add all files found in this directory ending in suffix
        filepaths_with_suffix.extend([
            os.path.join(os.path.relpath(root, swiftseq_data_dir), file_)
            for file_ in files if file_.endswith(suffix)
        ])

    return filepaths_with_suffix


"""
Germline Functions
"""


def create_germline_samples_file(germline_samples_filepath, inputdata_symlinks):
    """
    Writes a file to disk mapping patient IDs to the directories containing their data.
    
    Side effects: Writes a file to disk

    :param germline_samples_filepath: str Path to write out germline samples file
    :param inputdata_symlinks: list Relative paths to all symlinks linked to the original data
    """
    # Create a dictionary mapping the relative path of the parent folder with each file
    inputdata_symlinks_dir_file_map = {
        os.path.dirname(k) + '/': os.path.basename(k)
        for k in inputdata_symlinks
    }

    with open(germline_samples_filepath, 'w') as germline_samples:
        # Write out the header
        germline_samples.write('ID dir\n')

        # Write out entry for each patient path
        for inputdata_dir, inputdata_file in six.iteritems(inputdata_symlinks_dir_file_map):
            # TODO Remove trailing slash after debugging
            germline_samples.write('{id} {dir}/\n'.format(
                id=os.path.splitext(inputdata_file)[ROOT],
                dir=inputdata_dir
            ))


"""
Tumor Normal Functions
"""


def create_tn_inputdata_map(inputdata_symlinks):
    """
    Segments each path in the list of inputdata symlinks into a 3-layer dictionary:
        1) Relative path up to and including the patient id
        2) Next segment is either 'tumor' or 'normal'
        3) Name of the sample corresponding to the tissue type
    The value of each innermost key is the filename of the sample file.

    Example:
    (relative/path/to/patient_id)/(tumor)/(sample_123)/(sample_123.bam) becomes
    tn_inputdata_map['relative/path/to/patient_id']['tumor']['sample_123'] = 'sample_123.bam'

    :param inputdata_symlinks: list Relative paths to all symlinks linked to the original data
    :return: dict Mapping of important parts of inputdata symlink paths to the inputdata filename
    """
    tn_inputdata_map = defaultdict(lambda: defaultdict(dict))
    for inputdata_symlink in inputdata_symlinks:
        inputdata_path_parts = inputdata_symlink.strip().split('/')

        # Get parts of the path to split into dictionary keys
        patient_id_relpath = '/'.join(inputdata_path_parts[0:-3])
        tissue, sample, sample_filename = inputdata_path_parts[-3:]

        # Add an entry to the dictionary
        tn_inputdata_map[patient_id_relpath][tissue][sample] = sample_filename

    return tn_inputdata_map


def create_tn_patients_map_file(tn_patients_map_filepath, patient_id_relpaths):
    """
    Given a list of patient id relative paths, map that relative path to the patient id and
    out the mapping to a file.

    Side effects: Creates a file on disk

    :param tn_patients_map_filepath: str Path to the mapping file to be created on disk
    :param patient_id_relpaths: list All patient id relative paths
    """
    with open(tn_patients_map_filepath, 'w') as tn_samples:
        # Write out the header
        tn_samples.write('patient dir\n')

        # Map each patient id relative path to the patient id
        for patient_id_relpath in patient_id_relpaths:
            patient_id = patient_id_relpath.split('/')[PATIENT_NAME]
            # TODO Remove trailing slash after debugging
            tn_samples.write('{patient_id} {patient_id_relpath}/\n'.format(
                patient_id=patient_id,
                patient_id_relpath=patient_id_relpath
            ))


def create_tissue_samples_files(tn_inputdata_map):
    """
    For each patient id and tissue type, creates a file that outlines any samples and
    associated files to that patient id and tissue type. This is to handle the case where
    there's more than one sample associated with a given tissue. ie. 2 files for the tumor

    Side effects: Creates a file on disk

    :param tn_inputdata_map: dict Mapping of important parts of inputdata symlink paths
                                  to the inputdata filename
    """
    # Look at the both tissues for each patient id
    for patient_id_relpath, tissues in six.iteritems(tn_inputdata_map):
        for tissue, samples in six.iteritems(tissues):
            # Get relative path up to and including tissue type ('tumor' or 'normal')
            tissue_relpath = os.path.join(patient_id_relpath, tissue)

            # Write out to a file on disk for each tissue type in that tissue's directory
            sample_out_filepath = os.path.join(tissue_relpath, SwiftSeqStrings.sample_out_filename)
            with open(sample_out_filepath, 'w') as tissue_samples_file:
                # Write out the header
                tissue_samples_file.write('ID sampleDir dir filepath\n')

                # Write out all samples associated with this patient id and tissue
                for sample_dir in samples:
                    associated_sample_filepath = tn_inputdata_map[patient_id_relpath][tissue][sample_dir]
                    tissue_samples_file.write('{id} {sample_dir} {dir} {filepath}\n'.format(
                        id=os.path.splitext(associated_sample_filepath)[BEFORE_EXTENSION],
                        sample_dir=sample_dir,
                        dir=os.path.join(tissue_relpath, sample_dir),
                        filepath=os.path.join(tissue_relpath, sample_dir, associated_sample_filepath)
                    ))


def create_paired_output_dirs(tn_inputdata_map):
    """
    Inside the directory for each patient id, creates a directory for every pair of tumor and
    normal samples for that patient id.

    Side effects: Creates directories on disk

    :param tn_inputdata_map: dict Mapping of important parts of inputdata symlink paths
                                  to the inputdata filename
    """
    for patient_id_relpath, patient in six.iteritems(tn_inputdata_map):
        # Find all tumor and normal sample directories
        tumor_sample_dirs = [t for t in patient['tumor']]
        normal_sample_dirs = [n for n in patient['normal']]

        # Iterate over the cartesian product of all normal and tumor sample directories
        for tumor_sample, normal_sample in product(tumor_sample_dirs, normal_sample_dirs):
            tn_joined_sample_name = '___'.join((tumor_sample, normal_sample))

            # Create the new directory for this tumor-normal pair
            mkdirs(os.path.join(patient_id_relpath, SwiftSeqStrings.paired_analysis_dir, tn_joined_sample_name))


"""
Main Function
"""


def process_samples(inputdata_type, inputdata_filepaths, data_root, analysis_root, samtools_path):
    """
    Performs the following tasks:
        1) Checks to make sure input data is in the required format
            - Those that don't adhere will not be included in the analysis
        2) Recreates the directory structure of the input files in a separate analysis directory
        3) Creates symbolic links from the original data to their corresponding directories in
           the analysis directory
        4) Creates readgroups files for each sample in the analysis directory as siblings of
           the sample symbolic link
        If this is a Tumor-Normal run:
            5) Creates a file mapping patient id to the relative path housing that patient id's sample
               files at the root of the analysis directory
            6) Creates a file mapping each tissue type to the one or more sample files associated with
               it for each patient id in that tissue's root directory
            7) Creates a new directory <tumor_name>___<normal_name> for every pair of tumor and normal
               sample for every patient id
        Otherwise, this is a Germline run:
            5) Creates a file mapping patient ids to the directories containing their data

    :param inputdata_type: int Either Workflow.GERMLINE or Workflow.TUMOR_NORMAL_PAIR
    :param inputdata_filepaths: list Relative paths to all original data files
    :param data_root: str Path to the directory housing all the original data
    :param analysis_root: str Path to the root of the location for the analysis results
    :param samtools_path: str Path to the samtools executable
    :return: (int, int, list) Number of individuals and samples to be analyzed, relative paths
                              to all symlinks linked to the original data
    """
    # Relative paths to all symlinks linked to the original data
    inputdata_symlinks = create_analysis_dir(
        inputdata_type=inputdata_type,
        inputdata_filepaths=inputdata_filepaths,
        inputdata_dir_root=data_root,
        analysis_dir_root=analysis_root
    )

    # Create readgroups files on disk
    create_readgroup_files(
        inputdata_symlinks=inputdata_symlinks,
        samtools_path=samtools_path
    )

    # Record the number of individuals and samples analyzed
    n_individuals_analyzed = n_samples_analyzed = len(inputdata_symlinks)

    if inputdata_type == Workflow.TUMOR_NORMAL_PAIR:
        # Mapping of important parts of inputdata symlink paths to the inputdata filename
        # Ex. tn_inputdata_map['relative/path/to/patient_id']['tumor']['sample_123'] = 'sample_123.bam'
        tn_inputdata_map = create_tn_inputdata_map(inputdata_symlinks)

        # Create the mapping file from patient id relative paths to patient ids
        # TODO Remove extra slash
        create_tn_patients_map_file(
            tn_patients_map_filepath=os.path.join(analysis_root, SwiftSeqStrings.patient_out_filename),
            patient_id_relpaths=tn_inputdata_map.keys()
        )

        # For each sample file associated with a patient's tumor/normal, creates a mapping file
        # Headers: ID sampleDir dir filepath
        create_tissue_samples_files(tn_inputdata_map)

        # Creates a directory for every pair of tumor and normal samples for each patient id
        create_paired_output_dirs(tn_inputdata_map)

        # Record the number of individuals analyzed
        n_individuals_analyzed = len(tn_inputdata_map)
    elif inputdata_type == Workflow.GERMLINE:
        create_germline_samples_file(
            germline_samples_filepath=os.path.join(analysis_root, SwiftSeqStrings.patient_out_filename),
            inputdata_symlinks=inputdata_symlinks
        )
    else:
        raise ValueError('Unsupported data type: {}'.format(inputdata_type))

    return n_individuals_analyzed, n_samples_analyzed, inputdata_symlinks
