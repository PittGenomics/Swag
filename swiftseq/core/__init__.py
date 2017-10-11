"""
The modules and classes in swiftseq.core have to do with the core SwiftSeq functionality of collecting, validating,
and manipulating user input and passing necessary information to the various functions that output swift code, then
running the actual SwiftSeq run.
"""

from copy import copy

from swiftseq.swift.wrappers import *


class SwiftSeqStrings(object):
    wiki_link = 'X'
    help_email = 'help@email.com'
    help_msg = ('\n### Help ###\n'
                'Please carefully review the above error.\n'
                'For assistance running SwiftSeq, visit {wiki_link}. If your '
                'question remains unanswered, email us at {help_email}.').format(
                    wiki_link=wiki_link,
                    help_email=help_email
                )

    app_pool_default = 'primary'

    # For swiftseq.core.input
    patient_out_filename = 'individuals.txt'
    sample_out_filename = 'samples.txt'

    # For swiftseq.core.readgroups
    readgroups_out_filename = 'RGfiles.txt'
    readgroups_ids_out_filename = 'RGIDs.txt'

    # For swiftseq.core.contigs
    contigs_filename = 'contigs.txt'
    contig_unmapped_filename = 'contig_segments_unmapped.txt'

    # Run directory structure setup
    analysis_reference_dir = 'Reference'
    restart_conf_filename = 'restart.conf'
    swift_conf_filename = 'Swift.conf'
    swift_script_filename = 'SwiftSeq.swift'
    paired_analysis_dir = 'pairedAnalyses'
    worker_logging_dir = 'workingLogging'
    wrapper_dir = 'wrapper'

    # For swiftseq.swift.generate
    generate_sort_app = 'RgMergeSort'
    contig_split_bam = 'alnSampleBam'

    # Strings for setuptools
    setup_name = 'SwiftSeq'
    setup_version = '1.0.0'
    setup_description = 'TODO'
    setup_license = 'TODO'
    setup_author = 'Jason Pitt'
    setup_author_email = 'TODO'
    setup_url = 'TODO'


class SwiftSeqSupported(object):
    _supported = {
        'programs': {
            'gatk_post': {'GatkIndelRealignment', 'GatkBqsr'},
            'aligners': {'BwaAln', 'BwaMem', 'Bowtie2'},
            'genotypers': {
                'PlatypusPaired', 'PlatypusGerm', 'HaplotypeCaller', 'Mutect',
                'MpileupPaired', 'UnifiedGenotyper', 'ScalpelPaired', 'ScalpelGerm'
                'Strelka', 'Varscan'
            },
            'structural_variant_callers': {'DellyGerm', 'DellyPaired', 'LumpyGerm', 'LumpyPaired'},
            'remove_duplicates': {'PicardMarkDuplicates'},
            'bam_quality_control': {'SamtoolsFlagstat', 'BedtoolsGenomeCoverage', 'BamutilPerBaseCoverage'},
            'java': {'PicardMarkDuplicates'}
        },
        'types': {
            'run': {'Processing', 'Genotyping', 'Processing_and_Genotyping'},
            'data': {'Germline', 'Tumor_Normal_Pair'},
            'program': {
                'Aligner', 'Genotyper', 'Structural_Variant_Caller',
                'Gatk_Post-processing', 'Duplicate_Removal', 'Bam_Quality_Control'
            }
        },
        'params': {
            'program': {
                'walltime', 'params'}
        }
    }

    @staticmethod
    def programs(grouping_name):
        """
        Get the supported programs from a given grouping. If the name of the grouping is not
        found, return an empty set
        """
        return SwiftSeqSupported._get_supported(grouping_name)

    @ staticmethod
    def types(grouping_name):
        """
        Get the supported types from a given grouping. If the name of the grouping is not
        found, return an empty set
        """
        return SwiftSeqSupported._get_supported(grouping_name, entity='types')

    @staticmethod
    def params(grouping_name='program'):
        """
        Get the supported params from a given grouping. If the name of the grouping is not
        found, return an empty set
        """
        return SwiftSeqSupported._get_supported(grouping_name, entity='params')

    @ staticmethod
    def all():
        """
        Return all supported entities in a single set
        """
        return set.union(
            SwiftSeqSupported.programs('remove_duplicates'),
            SwiftSeqSupported.programs('structural_variant_callers'),
            SwiftSeqSupported.programs('genotypers'),
            SwiftSeqSupported.programs('aligners'),
            SwiftSeqSupported.programs('bam_quality_control')
        )

    @staticmethod
    def _get_supported(grouping_name, entity='programs'):
        return SwiftSeqSupported._supported[entity].get(grouping_name, set())


class SwiftSeqApps(object):
    """

    """
    _custom = {
        'PicardMarkDuplicates': {
            'name': 'PicardMarkDuplicates', 'print': printPicardMarkDuplicates,
            'walltime': '15:00:00', 'pool': 'primary'
        },
        'GatkIndelRealignment': {
            'name': 'GatkIndelRealnment', 'print': printGatkIndelRealnment,  # Misspelling here?
            'walltime': '24:00:00', 'pool': 'primary'
        },
        'GatkBqsr': {
            'name': 'GatkBqsr',
            'print': printGatkBqsr,
            'walltime': '24:00:00', 'pool': 'primary'},
        'DellyGerm': {
            'name': 'DellyGerm',
            'print': printDellyGerm,
            'walltime': '18:00:00', 'pool': 'primary'},
        'DellyPaired': {
            'name': 'DellyPaired',
            'print': printDellyPaired,
            'walltime': '18:00:00', 'pool': 'primary'},
        'SnpEff': {
            'name': 'SnpEff',
            'print': printSnpEff,
            'walltime': '10:00:00', 'pool': 'primary'},
        'BwaAln': {
            'name': 'BwaAln',
            'print': printBwaAln,
            'walltime': '47:00:00', 'pool': 'one'},
        'BwaMem': {
            'name': 'BwaMem',
            'print': printBwaMem,
            'walltime': '47:00:00', 'pool': 'one'},
        'PlatypusGerm': {
            'name': 'PlatypusGerm',
            'print': printPlatypusGerm,
            'walltime': '15:00:00',
                         'pool': 'primary'},
        'PlatypusPaired': {
            'name': 'PlatypusGerm',
            'print': printPlatypusPaired,
            'walltime': '15:00:00',
                           'pool': 'primary'},
        'Mutect': {
            'name': 'Mutect',
            'print': printMutect,
            'walltime': '20:00:00', 'pool': 'primary'},
        'MpileupPaired': {
            'name': 'MpileupPaired',
            'print': printMpileupPaired,
            'walltime': '20:00:00',
                          'pool': 'primary'},
        'HaplotypeCaller': {
            'name': 'HaplotypeCaller',
            'print': printHaplotypeCaller,
            'walltime': '15:00:00',
                            'pool': 'RAM'},
        'ScalpelGerm': {
            'name': 'ScalpelGerm',
            'print': printScalpelGerm,
            'walltime': '20:00:00', 'pool': 'RAM'},
        'ScalpelPaired': {
            'name': 'ScalpelPaired',
            'print': printScalpelPaired,
            'walltime': '20:00:00', 'pool': 'RAM'},
        'Varscan': {
            'name': 'Varscan',
            'print': printVarscan,
            'walltime': '20:00:00', 'pool': 'primary'},
        'Strelka': {
            'name': 'Strelka',
            'print': printStrelka,
            'walltime': '20:00:00', 'pool': 'RAM'},
        'SamtoolsFlagstat': {
            'name': 'SamtoolsFlagstat',
            'print': printSamtoolsFlagstat,
            'exclusion': None,

                             'walltime': '06:00:00', 'pool': 'primary'},
        'BedtoolsGenomeCoverage': {
            'name': 'BedtoolsGenomeCoverage',
            'print': printBedtoolsGenomeCoverage,
            'exclusion': None,
            'walltime': '08:00:00', 'pool': 'primary'},
        'BamutilPerBaseCoverage': {
            'name': 'BamutilPerBaseCoverage',
            'print': printBamutilPerBaseCoverage,
            'exclusion': None,
            'walltime': '12:00:00', 'pool': 'RAM'},
        }

    _base = {
        'GatkBqsrGrpReduce': {
            'name': 'GatkBqsrGrpReduce',
            'print': printGatkBqsrGrpReduce,
            'exclusion': None,

                              'walltime': '03:00:00', 'pool': 'primary'},
        'SamtoolsParseContig': {
            'name': 'SamtoolsParseContig',
            'print': printSamtoolsParseContig,
            'exclusion': None,

                                'walltime': '24:00:00', 'pool': 'IO'},
        'SamtoolsExtractRg': {
            'name': 'SamtoolsExtractRg',
            'print': printSamtoolsExtractRg,
            'exclusion': None,

                              'walltime': '24:00:00', 'pool': 'IO'},
        'ConcatVcf': {
            'name': 'ConcatVcf',
            'print': printConcatVcf,
            'exclusion': None,
            'walltime': '10:00:00',
                      'pool': 'primary'},
        'RgMergeSort': {
            'name': 'RgMergeSort',
            'print': printRgMergeSort,
            'exclusion': None,
            'walltime': '24:00:00',
                        'pool': 'one'},
        'IndexBam': {
            'name': 'IndexBam',
            'print': printIndexBam,
            'exclusion': None,
            'walltime': '08:00:00',
                     'pool': 'IO'},
        'ContigMergeSort': {
            'name': 'ContigMergeSort',
            'print': printContigMergeSort,
            'exclusion': None,

                            'walltime': '24:00:00', 'pool': 'one'}
        }

    @classmethod
    def custom(cls):
        return cls._custom

    @classmethod
    def base(cls):
        return cls._base

    @classmethod
    def all(cls):
        return copy(cls._custom).update(cls._base)