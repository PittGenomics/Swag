"""
Written by Jason Pitt
Modified by Dominic Fitzgerald on 24 May 2017

Notes:
extract_contigs_from_dict() and segment_genomic_regions() have a bit of overlap, especially when it comes to 
reading the Picard Sequence Dictionary
"""
import os
from swiftseq.core import SwiftSeqStrings
from swiftseq.util.path import mkdirs

TAG = 0
CONTIG_FIELD = 1
END_COORD = 2


def create_contigs_files(picard_ref_seq_dict, contig_interval_size,
                         swiftseq_analysis_dir, swiftseq_inputdata_symlinks):
    """
    This function parses a file created by Picard CreateSequenceDictionary (https://goo.gl/Mx5K4q) 
    and extracts out all the defined contigs in the reference genome for this organism.
    
    For every contig a file is created on disk which contains the coordinates of that contig broken 
    up into intervals of size contig_interval_size.
    
    All files are written out to a Reference folder in the analysis directory.
    
    :param picard_ref_seq_dict: str Path to a Picard Sequence Dictionary (*.dict)
    :param contig_interval_size: int Size of each interval for a contig
    :param swiftseq_analysis_dir: str Relative path to the analysis directory
    :param swiftseq_inputdata_symlinks: Relative paths to all symlinks linked to the original data
    :return: str The filepath to the contigs file
    """
    swiftseq_reference_dir = mkdirs(os.path.join(swiftseq_analysis_dir, SwiftSeqStrings.analysis_reference_dir))

    # Parse the given Picard Sequence Dictionary for defined contig names, write out to file
    defined_contigs, contigs_file_fp = extract_contigs_from_dict(picard_ref_seq_dict, swiftseq_reference_dir)

    # Create the contig interval files for each segment
    segment_genomic_regions(picard_ref_seq_dict, contig_interval_size, swiftseq_reference_dir)

    # For every symlink corresponding to input data, do something
    for swiftseq_inputdata_symlink in swiftseq_inputdata_symlinks:
        mk_contigs_file(swiftseq_inputdata_symlink, defined_contigs)

    return contigs_file_fp


def extract_contigs_from_dict(picard_ref_seq_dict, swiftseq_reference_dir):
    """
    Given a Picard Sequence Dictionary, extracts all defined contig names and writes them out 
    to a file in the swiftseq reference directory.
    
    Side effects: Creates a file on disk of the names of all contigs defined in the given 
    Picard Sequence Dictionary.
    
    :param picard_ref_seq_dict: str Path to a Picard Sequence Dictionary (*.dict)
    :param swiftseq_reference_dir: str Parent directory of all contig files
    :return: (list, str) A list of the contigs found in the Picard Sequence Dictionary,
                         filepath to the contigs file
    """
    contigs = list()
    contigs_filepath = os.path.join(swiftseq_reference_dir, SwiftSeqStrings.contigs_filename)
    with open(contigs_filepath, 'w') as contigs_file:
        for record in (line.strip().split('\t') for line in open(picard_ref_seq_dict)):
            if record[TAG] == '@SQ':
                contig = record[CONTIG_FIELD].replace('SN:', '')
                contigs_file.write(contig + '\n')
                contigs.append(contig)
        contigs_file.write('unmapped\n')

    return contigs, contigs_filepath


def segment_genomic_regions(picard_ref_dict, interval_size, swiftseq_reference_dir):
    """
    Given the Sequence Dictionary output from Picard CreateSequenceDictionary (*.dict file) and a desired 
    interval size, outputs a file for each contig in the Sequence Dictionary. The contents of each contig 
    file is a newline separated list of intervals, each of size interval_size (or possible smaller in the 
    case of the last interval), from 1 to the size of the contig. The files are output into the SwiftSeq 
    reference directory.
    
    Side effects: A file containing intervals is created for each defined contig.
    
    :param picard_ref_dict: str Filepath to a Picard Sequence Dictionary
    :param interval_size: int Size of each interval in a contig file
    :param swiftseq_reference_dir: str Parent directory of all contig files
    """
    segment_interval = '{segment_start}-{segment_end}\n'
    for record in (line.strip().split('\t') for line in open(picard_ref_dict)):
        if record[TAG] == '@SQ':
            contig_name = record[CONTIG_FIELD].replace('SN:', '')
            end_coord = int(record[END_COORD].replace('LN:', ''))

            contig_segments_filepath = os.path.join(
                swiftseq_reference_dir,
                'contig_segments_{}.txt'.format(contig_name)
            )

            with open(contig_segments_filepath, 'w') as contig_segment_file:
                # Get all intervals and write them out to this contig segment file
                seg_start, seg_end = 1, 1
                while seg_start < end_coord:
                    # Get end coordinate of the interval
                    seg_end = (seg_start + interval_size - 1
                               if seg_start + interval_size - 1 <= end_coord
                               else end_coord)

                    # Write the interval out to file
                    contig_segment_file.write(segment_interval.format(
                        segment_start=seg_start,
                        segment_end=seg_end
                    ))

                    # Set the start of the new interval
                    seg_start = seg_end + 1

    contig_segments_unmapped = os.path.join(swiftseq_reference_dir, SwiftSeqStrings.contig_unmapped_filename)
    with open(contig_segments_unmapped, 'w') as contigs_unmapped:
        contigs_unmapped.write('no_mapped_reads\n')


# TODO Obviously this whole function needs to be cleaned up
def mk_contigs_file(swiftseq_inputdata_symlink, defined_contigs):
    """ Will create an expected contig file for each symlinked bam.
    The resulting file will be named ContigFiles.txt and will reside
    in the sample directory. Swift will use this file to know what
    The expected output of splits are. 
    
    NOTE: This function may be depricated in the latest version of
    SwiftSeq. Swift may only need to use the Contigs.txt file
    
    Now this function is being used again since bamtools needs it"""

    absOutDir = os.getcwd() + '/'

    # Assumes a bam as the input
    bamPrefix = swiftseq_inputdata_symlink[:-4].split('/')[-1]  # strips off '.bam'
    bamDir = '/'.join(swiftseq_inputdata_symlink.split('/')[0:-1]) + '/'
    # TODO Add this to SwiftSeqStrings
    outFile = open(absOutDir + bamDir + 'sampleContigs.txt', 'w')
    for contig in defined_contigs:
        contigBam = '%s%s.contig.%s.bam' % (absOutDir, bamDir + bamPrefix, contig)
        print >> outFile, contigBam
    # unmapped because this is what bamtools uses
    print >> outFile, '%s%s.contig.%s.bam' % (absOutDir, bamDir + bamPrefix, 'unampped')
    outFile.close()
