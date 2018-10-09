"""
Written by Jason Pitt
Revised by Dominic Fitzgerald on 15 May 2017
"""
import json
from collections import defaultdict

import six
import cerberus

import swag.parsl.wrappers
from swag.core import SwagSupported, SwagApps, SwagWorkflowValidation
from swag.core.exceptions import WorkflowConfigException


## To-do
# more detailed error checking of aligner, genotypers, etc.
# Look for incompatibilities in the json file

# to avoid error... need a better solution at some point


def compose_workflow_wrappers(workflow, **wrapper_config):
    """ Recreate this having it interact with parseWorkflow

    Ideally

    tc entries deprecated  """

    # Base apps

    for base_app_name, base_app_config in six.iteritems(SwagApps.base()):
        # Skip base app if the exclusion is true
        # Leave this for now as it will be useful
        if base_app_config['exclusion'] != workflow.run_type:
            compose_wrapper = getattr(swag.parsl.wrappers, 'compose_{}'.format(base_app_name))
            compose_wrapper(app_name=base_app_name, **wrapper_config)

    # Apps specified in the json workflow
    apps_in_workflow = workflow.programs_in_workflow
    for app_name, app_config in six.iteritems(apps_in_workflow):
        compose_wrapper = getattr(swag.parsl.wrappers, 'compose_{}'.format(app_name))
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
    # TODO Remove length check after debugging
    if len(param_dict) == 0:
        return ''
    return ' '.join([sep.join((key, val)) for key, val in six.iteritems(param_dict)])


def get_all_programs(workflow_config):
    """
    For all program types proposed in the workflow configuration that are supported by
    Swag, get program parameters and attributes (such as walltime).

    :param workflow_config: dict Workflow configuration
    :return: dict Map of all supported programs to parameters and attributes
    """
    # Get all program types so all possible programs are caught
    supported_program_types = SwagSupported.types('program')
    supported_java = SwagSupported.programs('java')
    programs_dict = defaultdict(dict)

    # Find intersection of proposed program types and supported program types
    proposed_supported_program_types = supported_program_types.intersection(set(workflow_config.keys()))

    # Iterate over all program types proposed in the workflow config
    for supported_program_type in proposed_supported_program_types:
        # Get all programs for each program type
        for program, program_config in six.iteritems(workflow_config[supported_program_type]):
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
                # print('Going in: {}'.format(program_config.get('params', dict())))
                programs_dict[program]['params'] = params_to_string(program_config.get('params', dict()), sep)
                # print('Coming out: {}'.format(programs_dict[program]['params']))

    return programs_dict


def get_specified_programs(workflow_config, program_type):
    """
    Return all programs specified by a given top-level attribute of the workflow configuration.

    :param workflow_config: dict Workflow configuration
    :param program_type: str A supported program type
    :return: list All programs listed in the workflow config under program type
    """
    return [program for program in workflow_config.get(program_type, list())]


class Workflow(object):
    GERMLINE, TUMOR_NORMAL_PAIR = 'germline', 'tumor_normal_pair'

    def __init__(self, workflow_config):
        """
        Needs to contain the following variables
        
        runType, dataType, genotypers, structVarCallers, gatk, rmDup
        """
        self.workflow_config = workflow_config
        self.validate()

        # Get workflow specifics - error checking will be performed
        self.run_type = workflow_config['run_type']
        self.data_type = workflow_config['data_type']

        # These will be empty if either aren't present
        self.genotypers = get_specified_programs(workflow_config, 'genotyper')
        self.struct_var_callers = get_specified_programs(workflow_config, 'structural_variant_caller')
        self.bam_quality_control_apps = get_specified_programs(workflow_config, 'bam_quality_control')
        self.has_gatk = 'gatk_post-processing' in self.workflow_config
        self.has_rm_dup = 'duplicate_removal' in self.workflow_config
        self.has_struct_vars = bool(self.struct_var_callers)
        self.has_alignment, self.has_genotyping = SwagSupported.flags()[self.run_type]
        self.aligner = list(workflow_config['aligner'])[0] if self.has_alignment else None

        # All programs in json that need to be printed with params will
        # be in this var
        self.programs_in_workflow = get_all_programs(workflow_config)

    def print_workflow_config(self):
        print(json.dumps(self.workflow_config, indent=4) + '\n\n')

    def validate(self):
        '''Iterate through all fields of the json. Use possibleApps.py to
        determine if all fields are valid

        Go all the way down to applications... be sure all fields in params
        & walltime dict are strings. And be sure walltime dict only has len == 1 '''

        cerberus.schema_registry.add('program-schema', SwagWorkflowValidation.get_program_schema())
        v = cerberus.Validator()
        if not v.validate(document=self.workflow_config, schema=SwagWorkflowValidation.get_workflow_schema()):
            raise WorkflowConfigException('Workflow failed validation: {}'.format(v.errors))
