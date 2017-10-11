"""
Written by Jason Pitt
Revised by Dominic Fitzgerald on 30 May 2017
"""
import os
import re
import warnings
from subprocess import Popen, PIPE

from swiftseq.core import SwiftSeqStrings

FIRST_RESULT = 0
FIRST_IN_GROUP = 0


def make_readgroup_dict(bam, samtools_path):
    """
    This is a combination of extractReadGroupsStrings() and makeReadGroupDict()
    
    Side effects: None
    :param bam: 
    :param samtools_path: 
    :return: 
    """

    # Get the stdout from a subprocess running samtools to extract only readgroups (@RG)
    samtools_output, _ = Popen(
        [samtools_path, 'view', '-H', bam, '|', 'grep', '\'@RG\''],
        stdout=PIPE
    ).communicate()

    # Add every readgroup line to a list
    readgroup_strings = list()
    for line in samtools_output.split('\n'):
        if line.startswith('@RG'):
            readgroup_strings.append(line.strip().replace(' ', '_'))

    readgroup_ids = dict()
    readgroup_id_re = re.compile(r'ID:(.*?)(\t|$)')
    for readgroup_string in readgroup_strings:
        re_result = readgroup_id_re.findall(readgroup_string)
        if re_result:
            readgroup_id_name = re_result[FIRST_RESULT][FIRST_IN_GROUP]
            readgroup_ids[readgroup_id_name] = readgroup_string

    return readgroup_ids


# TODO Will need to modify this to handle bams already split by RG
def create_readgroup_files(inputdata_symlinks, samtools_path):
    """
    
    Side effects: Creates two files
    :param data_symlinks: list 
    :param samtools: str Path to the samtools executable
    """
    for file_ in inputdata_symlinks:
        dirPath = os.path.dirname(file_)
        readGroupIds = make_readgroup_dict(file_, samtools_path)
        readgroup_out_path = os.path.join(dirPath, SwiftSeqStrings.readgroups_out_filename)
        readgroup_id_out_path = os.path.join(dirPath, SwiftSeqStrings.readgroups_ids_out_filename)

        with open(readgroup_out_path, 'w') as rg_out, open(readgroup_id_out_path, 'w') as rgid_out:
            for readgroup in readGroupIds:
                rg_filename_root, rg_filename_ext = os.path.splitext(file_)
                rg_filename = '.'.join((rg_filename_root, readgroup, rg_filename_ext.strip('.')))
                rg_out.write(rg_filename + '\n')
                rgid_out.write(readgroup + '\n')


def extract_SM(readGroupString):
    ''' Get the SM from the read group string

    If there is no SM, need to decide what to do... could have that file ignored..
    This is likely the best option since a file without RG ID will be ignored
    as well '''

    SMregex = re.compile(r'SM:(.*?)(\t|$)')
    file_ = None
    # Need to handle when one isn't found or if multiples
    try:
        SM = SMregex.findall(readGroupString)[0]
        if len(SM) > 1:
            warnings.warn(('Warning: one or more read groups in %s have multiple SM fields .') % (file_))
    except IndexError:
        warnings.warn(('Warning: %s does not contain an SM field in its read group.') % (file_))
    # Need to make sure it is actually ignored
    # For TN pairs, the entire pair will need ot be ignored

    return SM


def is_uniform_SM_fields(read_group_strings):
    """
    I have no idea what this function does
    It was kind of a function stub
    """
    return len({extract_SM(read_group_string) for read_group_string in read_group_strings}) == 1
