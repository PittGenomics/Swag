"""
Written by Jason Pitt
Revised by Dominic Fitzgerald on 15 May 2017
"""
import json
from collections import defaultdict

import swiftseq.swift.wrappers
from swiftseq.core import SwiftSeqSupported, SwiftSeqApps
from swiftseq.core.exceptions import WorkflowConfigException


## To-do
# more detailed error checking of aligner, genotypers, etc.
# Look for incompatibilities in the json file

# to avoid error... need a better solution at some point


def compose_workflow_wrappers(workflow, wrapper_config):
    """ Recreate this having it interact with parseWorkflow

    Ideally

    tc entries deprecated  """

    # Base apps

    for base_app_name, base_app_config in SwiftSeqApps.base().items():
        # Skip base app if the exclusion is true
        # Leave this for now as it will be useful
        if base_app_config['exclusion'] != workflow.run_type:
            compose_wrapper = getattr(swiftseq.swift.wrappers, 'compose_{}'.format(base_app_name))
            compose_wrapper(app_name=base_app_name, **wrapper_config)

    # Apps specified in the json workflow
    apps_in_workflow = workflow.programs_in_workflow
    for app_name, app_config in apps_in_workflow.items():
        compose_wrapper = getattr(swiftseq.swift.wrappers, 'compose_{}'.format(app_name))
        # print_wrapper = customApps[app_name]['print']  # custom apps
        compose_wrapper(app_name=app_name, app_parameters=app_config['params'], **wrapper_config)


def params_to_string(param_dict, sep):
    """
    Converts a mapping of key-values to a space separated string in a
    bash style for command line programs.

    :param param_dict: dict Mapping of program parameters to values
    :param sep: str Desired separator in the bash style string
    :return: str Bash style string of parameter-value mappings
    """
    # TODO Remove the additional space after debugging
    # TODO Remove length check after debugging
    if len(param_dict) == 0:
        return ''
    return ' '.join([sep.join((key, val)) for key, val in param_dict.items()]) + ' '


def get_all_programs(workflow_config):
    """
    For all program types proposed in the workflow configuration that are supported by
    SwiftSeq, get program parameters and attributes (such as walltime).

    :param workflow_config: dict Workflow configuration
    :return: dict Map of all supported programs to parameters and attributes
    """
    # Get all program types so all possible programs are caught
    supported_program_types = SwiftSeqSupported.types('program')
    supported_java = SwiftSeqSupported.programs('java')
    programs_dict = defaultdict(dict)

    # Find intersection of proposed program types and supported program types
    proposed_supported_program_types = supported_program_types.intersection(set(workflow_config.keys()))

    # Iterate over all program types proposed in the workflow config
    for supported_program_type in proposed_supported_program_types:
        # Get all programs for each program type
        for program, program_config in workflow_config[supported_program_type].items():
            # Get and record walltime
            programs_dict[program]['walltime'] = program_config['walltime']
            # Ensure correct parameter separator for java programs
            sep = '=' if program in supported_java else ' '

            # compile all params as a string
            # try except because if params not specified through GUI
            # the param string will not be present

            # Strelka will be kept as a dict of param : value
            # this is because Strelka requires param in a config and not
            # passed via the command line
            if program == 'Strelka':
                programs_dict[program]['params'] = program_config.get('params', dict())
            else:
                # Returns a space separated string or empty string if KeyError
                print('Going in: {}'.format(program_config.get('params', dict())))
                programs_dict[program]['params'] = params_to_string(program_config.get('params', dict()), sep)
                print('Coming out: {}'.format(programs_dict[program]['params']))

    return programs_dict


def get_aligner(workflow_config):
    """
    Extracts the alginer from the workflow configuration and, if it's a supported
    aligner, returns the name of the aligner.

    :param workflow_config: dict Workflow configuration
    :return: str The name of the supported aligner
    """
    supported_aligners = SwiftSeqSupported.programs('aligners')
    proposed_aligner_config = workflow_config['Aligner']

    # Check to ensure only one aligner was specified
    if len(proposed_aligner_config) < 1:
        raise WorkflowConfigException('Processing specified but no aligner declared')
    if len(proposed_aligner_config) > 1:
        raise WorkflowConfigException('Processing specified but more than one aligner declared')

    # Get proposed aligner and ensure it's supported
    proposed_aligner, = list(proposed_aligner_config)
    if proposed_aligner in supported_aligners:
        return proposed_aligner

    # If any of the above requirements isn't met, then something went wrong
    raise WorkflowConfigException('Aligner {} is not supported'.format(proposed_aligner))


def get_specified_programs(workflow_config, program_type):
    """
    Return all programs specified by a given top-level attribute of the workflow configuration.

    :param workflow_config: dict Workflow configuration
    :param program_type: str A supported program type
    :return: list All programs listed in the workflow config under program type
    """
    if program_type not in workflow_config:
        return list()
    return [program for program in workflow_config[program_type]]


def get_types(workflow_config, type_str):
    """
    Return a top-level attribute of the workflow configuration.

    :param workflow_config: dict Workflow configuration
    :param type_str: str A supported type of workflow attribute (runType or dataType)
    :return: str The requested workflow attribute
    """
    if type_str not in workflow_config:
        raise WorkflowConfigException('Does not contain {}'.format(type_str))
    return workflow_config[type_str]


def should_run_gatk(workflow_config, gatk_str):
    """
    Return a boolean value as to whether GATK should be run as part of this
    workflow configuration.

    :param workflow_config: dict Workflow configuration
    :param gatk_str: str Key specifying GATK program options in the workflow config
    :return: bool Whether GATK should be run in this workflow
    """
    # If GATK doesn't exist in the workflow config, then it shouldn't be run, so False
    if gatk_str not in workflow_config:
        return False

    # Check to make sure all required workflow config entries have values, if so then True
    if (
        workflow_config.get(gatk_str) and
        workflow_config.get('GatkIndelRealignment') and
        workflow_config.get('GatkBqsr')
    ):
        return True

    # If any of the above requirements isn't met, then something went wrong
    raise WorkflowConfigException('Does not contain proper gatk programs')


def should_run_rm_dup(workflow_config, rm_dup_str):
    """
    Return a boolean value as to whether a PCR duplicate removal program should be
    run as a part of this workflow.

    :param workflow_config: dict Workflow configuration
    :param rm_dup_str: str Key specifying duplicate removal program options in the workflow config
    :return: bool Whether PCR duplicate removal should be run in this workflow
    """
    # If duplicate removal doesn't exist in the workflow config, then it shouldn't be run, so False
    if rm_dup_str not in workflow_config:
        return False

    # Get the duplicate removal program and make sure it isn't unset or not a single program
    rm_dup_config_entry = workflow_config.get(rm_dup_str)
    if rm_dup_config_entry == 'default':
        raise WorkflowConfigException('Does not contain proper duplicate removal program')
    if len(rm_dup_config_entry) < 1:
        raise WorkflowConfigException('Duplicate removal specified but no program declared')
    if len(rm_dup_config_entry) > 1:
        raise WorkflowConfigException('Contains more than on duplicate removal program')

    # Get all supported duplicate removal programs and ensure the specified is supported
    supported_rm_dup = SwiftSeqSupported.programs('remove_duplicates')
    proposed_rm_dup_name, = list(rm_dup_config_entry)

    # Check to make sure all required workflow config entries have supported values, if so then True
    if rm_dup_config_entry and (proposed_rm_dup_name in supported_rm_dup):
        return True

    # If any of the above requirements isn't met, then something went wrong
    raise WorkflowConfigException('Does not contain proper duplicate removal program')


def set_align_geno_flags(run_type):
    """
    Based on the run type of this workflow, set flags on whether to run alignment
    and/or genotyping programs.

    :param run_type: str A supported run type string
    :return: (bool, bool) Flags to run alignment and/or genotyping
    """
    run_types = {
        'Processing_and_Genotyping': (True, True),
        'Processing': (True, False),
        'Genotyping': (False, True),
    }

    if run_type not in run_types:
        raise WorkflowConfigException('runType field contains an unsupported value')
    return run_types[run_type]


class Workflow(object):
    GERMLINE, TUMOR_NORMAL_PAIR = 'Germline', 'Tumor_Normal_Pair'

    def __init__(self, workflow_config):
        """
        Needs to contain the following variables
        
        runType, dataType, genotypers, structVarCallers, gatk, rmDup
        """
        self.workflow_config = workflow_config

        # Get workflow specifics - error checking will be performed
        self.run_type = get_types(workflow_config, 'runType')
        self.data_type = get_types(workflow_config, 'dataType')

        # These will be empty if either aren't present
        self.genotypers = get_specified_programs(workflow_config, 'Genotyper')
        self.struct_var_callers = get_specified_programs(workflow_config, 'Structural_Variant_Caller')
        self.bam_quality_control_apps = get_specified_programs(workflow_config, 'Bam_Quality_Control')

        self.has_gatk = should_run_gatk(workflow_config, 'Gatk_Post-processing')
        self.has_rm_dup = should_run_rm_dup(workflow_config, 'Duplicate_Removal')
        """
        The above two attributes are also similar, but not exactly the same
        There may be a way to combine them
        """

        # will return alignment and genotyping bools
        self.has_alignment, self.has_genotyping = set_align_geno_flags(self.run_type)
        self.has_struct_vars = bool(self.struct_var_callers)

        # will be set above
        self.aligner = get_aligner(workflow_config) if self.has_alignment else None
        """
        If aligners are only retrieved when the alignment flag is set, why don't genotypers 
        get the same treatment?
        """

        # All programs in json that need to be printed with params will
        # be in this var
        self.programs_in_workflow = get_all_programs(workflow_config)

    def print_workflow_config(self):
        print(json.dumps(self.workflow_config, indent=4) + '\n\n')

    def checkJsonStructure(self):
        '''Iterate through all fields of the json. Use possibleApps.py to
        determine if all fields are valid
        
        Go all the way down to applications... be sure all fields in params
        & walltime dict are strings. And be sure walltime dict only has len == 1 '''

        pass

    # Implement this soon... may make some of the rules implemented in
    # functions below redundant











