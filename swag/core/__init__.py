"""
The modules and classes in swag.core have to do with the core Swag functionality of collecting, validating,
and manipulating user input and passing necessary information to the various functions that output parsl code, then
running the actual Swag run.
"""
import os
import subprocess
from copy import copy

conda_install_packages = [
    'samtools',
    'bcftools',
    'gatk',
    'bamutil',
    'picard',
    'bedtools',
    'delly',
    'snpeff',
    'bwa',
    'platypus-variant',
    'scalpel',
    'varscan',
    'strelka',
    'java-jdk',
    'python=2.7'
]


class SwagStrings(object):
    wiki_link = 'X'
    help_email = 'help@email.com'
    help_msg = ('\n### Help ###\n'
                'Please carefully review the above error.\n'
                'For assistance running Swag, visit {wiki_link}. If your '
                'question remains unanswered, email us at {help_email}.').format(
                    wiki_link=wiki_link,
                    help_email=help_email
                )

    app_pool_default = 'primary'
    app_walltime_default = '24:00:00'

    # For swag.core.input
    patient_out_filename = 'individuals.txt'
    sample_out_filename = 'samples.txt'

    # For swag.core.readgroups
    readgroups_out_filename = 'RGfiles.txt'
    readgroups_ids_out_filename = 'RGIDs.txt'

    # For swag.core.contigs
    contigs_filename = 'contigs.txt'
    contig_unmapped_filename = 'contig_segments_unmapped.txt'
    sample_contigs_filename = 'sampleContigs.txt'

    # Run directory structure setup
    analysis_reference_dir = 'Reference'
    restart_conf_filename = 'restart.conf'
    parsl_conf_filename = 'Parsl.conf'
    parsl_script_filename = 'Swag.parsl'
    paired_analysis_dir = 'pairedAnalyses'
    worker_logging_dir = 'workerLogging'
    wrapper_dir = 'wrapper'

    # For swag.parsl.generate
    generate_sort_app = 'RgMergeSort'
    contig_split_bam = 'alnSampleBam'

    # Strings for setuptools
    setup_name = 'Swag'
    setup_version = '0.1.0'
    setup_description = 'Scalable Workflows for Analyzing Genomes'
    setup_license = 'Apache Software License'
    setup_author = 'Jason Pitt'
    setup_author_email = 'jason.j.pitt@gmail.com'
    setup_url = 'https://github.com/PittGenomics/Swag'


class SwagWorkflowValidation(object):
    @staticmethod
    def get_workflow_schema():
        steps_schema = {}
        for step in SwagSupported.types('program'):
            steps_schema[step] = {'type': 'dict', 'schema': dict()}
            for program in SwagSupported.programs(step):
                steps_schema[step]['schema'][program] = {'type': 'dict', 'schema': 'program-schema'}

        # Contraints for specific workflow steps
        # TODO Connect specific step names with SwagSupported so edits only happen in one place
        steps_schema['aligner'].update({'minlength': 1, 'maxlength': 1})
        steps_schema['duplicate_marking'].update({'minlength': 1, 'maxlength': 1})
        # steps_schema['gatk_post-processing'].update({'minlength': 2, 'maxlength': 2})

        workflow_schema = {
            'data_type': {
                'type': 'string',
                'allowed': list(SwagSupported.types('data')),
                'required': True
            },
            'run_type': {
                'type': 'string',
                'allowed': list(SwagSupported.types('run')),
                'required': True
            }
        }
        workflow_schema.update(steps_schema)

        return workflow_schema

    @staticmethod
    def get_program_schema():
        return {
            'params': {
                'type': 'dict',
                'keyschema': {'type': 'string'},
                'valueschema': {'type': 'string'}
            },
            'walltime': {
                'type': 'string',
                'regex': r'^\d+:\d{2}:\d{2}$',
                'required': True
            }
        }


def install_novosort_license(conda_bin_dir, **kwargs):
    if kwargs.get('novo_license_path'):
        subprocess.call([
            os.path.join(conda_bin_dir, 'bin', 'novoalign-license-register'),
            kwargs.get('novo_license_path')
        ])


class SwagSupported(object):
    # Possible keys:
    #    - bioconda_tag: bioconda name and optional version number, fed directly to bioconda
    #    - exe_name: filename of the executable or jar file or whatever is executed
    #    - rel_path: relative path from the conda environment root, not including the name of the executable
    #                or jar file or whatever; defaults to 'bin'
    conda_install_packages = [
        {'bioconda_tag': 'samtools=1.6', 'exe_name': 'samtools'},
        {'bioconda_tag': 'bcftools=1.6', 'exe_name': 'bcftools'},
        {'bioconda_tag': 'gatk4=4.0b6', 'exe_name': 'gatk-package-4.beta.6-local.jar', 'rel_path': 'share/gatk4-4.0b6-*'},
        {'bioconda_tag': 'bamutil=1.0.14', 'exe_name': 'bam'},
        {'bioconda_tag': 'picard=2.15', 'exe_name': 'picard.jar', 'rel_path': 'share/picard-2.15.0-*'},
        {'bioconda_tag': 'bedtools=2.27.1', 'exe_name': 'bedtools'},
        {'bioconda_tag': 'sambamba=0.6.6', 'exe_name': 'sambamba'},
        {'bioconda_tag': 'java-jdk=8.0.112', 'exe_name': 'java'},
        {'bioconda_tag': 'delly=0.7.7', 'exe_name': 'delly'},
        {'bioconda_tag': 'snpeff=4.3.1r', 'exe_name': 'snpEff.jar', 'rel_path': 'share/snpeff-4.3.1r-*'},
        {'bioconda_tag': 'bwa=0.7.17', 'exe_name': 'bwa'},
        {'bioconda_tag': 'platypus-variant=0.8.1.1', 'exe_name': 'Platypus.py',
         'rel_path': 'share/platypus-variant-0.8.1.1-*'},
        {'bioconda_tag': 'scalpel=0.5.3', 'exe_name': 'scalpel-discovery'},
        {'bioconda_tag': 'varscan=2.4.3', 'exe_name': 'VarScan.jar', 'rel_path': 'share/varscan-2.4.3-*'},
        {'bioconda_tag': 'strelka=2.8.4', 'exe_name': 'configureStrelkaSomaticWorkflow.py'},
        {'bioconda_tag': 'python=2.7.13', 'exe_name': 'python'},
        {
            'bioconda_tag': 'novoalign=3.07.00',
            'exe_key': ['novoalign', 'novosort'],
            'exe_name': ['novoalign', 'novosort'],
            'post_hook': install_novosort_license
        },
        {'bioconda_tag': 'bowtie2=2.3.4.1', 'exe_name': 'bowtie2'}
    ]

    _supported = {
        'programs': {
            # 'gatk_post-processing': {'GatkIndelRealignment', 'GatkBqsr'},
            'aligner': {'Bowtie2', 'BwaMem', 'novoalign'},
            # 'aligner': {'BwaAln', 'BwaMem', 'Bowtie2'},  OLD
            # 'genotyper': {
            #     'PlatypusPaired', 'PlatypusGerm', 'HaplotypeCaller', 'Mutect',
            #     'MpileupPaired', 'UnifiedGenotyper', 'ScalpelPaired', 'ScalpelGerm',
            #     'Strelka', 'Varscan'
            # },
            # 'structural_variant_caller': {'DellyGerm', 'DellyPaired', 'LumpyGerm', 'LumpyPaired'},
            'duplicate_marking': {'PicardMarkDuplicates'},
            # 'bam_quality_control': {'SamtoolsFlagstat', 'BedtoolsGenomeCoverage', 'BamutilPerBaseCoverage'},
            # This is here because java has a different way of taking command line arguments
            'java': {'PicardMarkDuplicates'},
            'bam_metrics': {'genomeCoverageBed'},
            'germline_short_variants': {'PlatypusGerm'},
            'germline_structural_variants': {'DellyGerm'},
            'tn_short_variants': {'Varscan', 'ScalpelPaired', 'Mutect'},
            'tn_structural_variants': {'DellyPaired'}
        },
        'types': {
            'run': {'alignment', 'variant_calling', 'alignment_and_variant_calling'},
            'data': {'germline', 'tumor_normal'},
            'program': {
                'aligner', 'bam_metrics', 'duplicate_marking', 'germline_short_variants',
                'germline_structural_variants', 'tn_short_variants', 'tn_structural_variants'
            },
            # 'program': {    OLD
            #     'aligner', 'genotyper', 'structural_variant_caller',
            #     'gatk_post-processing', 'duplicate_removal', 'bam_quality_control'
            # }
        },
        'flags': {
            'alignment_and_variant_calling': (True, True),
            'alignment': (True, False),
            'variant_calling': (False, True)
        },
        'params': {
            'program': {
                'walltime', 'params'
            }
        }
    }

    @staticmethod
    def programs(grouping_name):
        """
        Get the supported programs from a given grouping. If the name of the grouping is not
        found, return an empty set
        """
        return SwagSupported._get_supported(grouping_name)

    @ staticmethod
    def types(grouping_name):
        """
        Get the supported types from a given grouping. If the name of the grouping is not
        found, return an empty set
        """
        return SwagSupported._get_supported(grouping_name, entity='types')

    @staticmethod
    def flags():
        """
        Get the aligner and/or genotyper present flags depending on the run type
        """
        return SwagSupported._supported.get('flags')

    @staticmethod
    def params(grouping_name='program'):
        """
        Get the supported params from a given grouping. If the name of the grouping is not
        found, return an empty set
        """
        return SwagSupported._get_supported(grouping_name, entity='params')

    @ staticmethod
    def all():
        """
        Return all supported entities in a single set
        """
        return set.union(
            SwagSupported.programs('remove_duplicates'),
            SwagSupported.programs('structural_variant_callers'),
            SwagSupported.programs('genotypers'),
            SwagSupported.programs('aligners'),
            SwagSupported.programs('bam_quality_control')
        )

    @staticmethod
    def _get_supported(grouping_name, entity='programs'):
        return SwagSupported._supported[entity].get(grouping_name, set())


class SwagApps(object):
    """

    """
    _custom = {
        'PicardMarkDuplicates': {
            'name': 'PicardMarkDuplicates',
            'walltime': '15:00:00', 'pool': 'primary'
        },
        'GatkIndelRealignment': {
            'name': 'GatkIndelRealnment',
            'walltime': '24:00:00', 'pool': 'primary'
        },
        'GatkBqsr': {
            'name': 'GatkBqsr',
            'walltime': '24:00:00', 'pool': 'primary'},
        'DellyGerm': {
            'name': 'DellyGerm',
            'walltime': '18:00:00', 'pool': 'primary'},
        'DellyPaired': {
            'name': 'DellyPaired',
            'walltime': '18:00:00', 'pool': 'primary'},
        'SnpEff': {
            'name': 'SnpEff',
            'walltime': '10:00:00', 'pool': 'primary'},
        'BwaAln': {
            'name': 'BwaAln',
            'walltime': '47:00:00', 'pool': 'one'},
        'BwaMem': {
            'name': 'BwaMem',
            'walltime': '47:00:00', 'pool': 'one'},
        'PlatypusGerm': {
            'name': 'PlatypusGerm',
            'walltime': '15:00:00',
                         'pool': 'primary'},
        'PlatypusPaired': {
            'name': 'PlatypusGerm',
            'walltime': '15:00:00',
                           'pool': 'primary'},
        'Mutect': {
            'name': 'Mutect',
            'walltime': '20:00:00', 'pool': 'primary'},
        'MpileupPaired': {
            'name': 'MpileupPaired',
            'walltime': '20:00:00',
                          'pool': 'primary'},
        'HaplotypeCaller': {
            'name': 'HaplotypeCaller',
            'walltime': '15:00:00',
                            'pool': 'RAM'},
        'ScalpelGerm': {
            'name': 'ScalpelGerm',
            'walltime': '20:00:00', 'pool': 'RAM'},
        'ScalpelPaired': {
            'name': 'ScalpelPaired',
            'walltime': '20:00:00', 'pool': 'RAM'},
        'Varscan': {
            'name': 'Varscan',
            'walltime': '20:00:00', 'pool': 'primary'},
        'Strelka': {
            'name': 'Strelka',
            'walltime': '20:00:00', 'pool': 'RAM'},
        'SamtoolsFlagstat': {
            'name': 'SamtoolsFlagstat',
            'exclusion': None,

                             'walltime': '06:00:00', 'pool': 'primary'},
        'BedtoolsGenomeCoverage': {
            'name': 'BedtoolsGenomeCoverage',
            'exclusion': None,
            'walltime': '08:00:00', 'pool': 'primary'},
        'BamutilPerBaseCoverage': {
            'name': 'BamutilPerBaseCoverage',
            'exclusion': None,
            'walltime': '12:00:00', 'pool': 'RAM'},
        }

    _base = {
        # 'GatkBqsrGrpReduce': {
        #     'name': 'GatkBqsrGrpReduce',
        #     'exclusion': None,
        #
        #                       'walltime': '03:00:00', 'pool': 'primary'},
        'SamtoolsParseContig': {
            'name': 'SamtoolsParseContig',
            'exclusion': None,

                                'walltime': '24:00:00', 'pool': 'IO'},
        'SamtoolsExtractRg': {
            'name': 'SamtoolsExtractRg',
            'exclusion': None,

                              'walltime': '24:00:00', 'pool': 'IO'},
        'ConcatVcf': {
            'name': 'ConcatVcf',
            'exclusion': None,
            'walltime': '10:00:00',
                      'pool': 'primary'},
        'FilterVcf': {
            'name': 'FilterVcf',
            'exclusion': None,
            'walltime': '10:00:00',
            'pool': 'primary'
        },
        'RgMergeSort': {
            'name': 'RgMergeSort',
            'exclusion': None,
            'walltime': '24:00:00',
                        'pool': 'one'},
        'IndexBam': {
            'name': 'IndexBam',
            'exclusion': None,
            'walltime': '08:00:00',
                     'pool': 'IO'},
        'ContigMergeSort': {
            'name': 'ContigMergeSort',
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
        _custom_copy = copy(cls._custom)
        _custom_copy.update(cls._base)
        return _custom_copy
