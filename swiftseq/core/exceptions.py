import sys
from swiftseq.core import SwiftSeqStrings


class EnvironmentVariableException(Exception):
    except_msg = ('Environment variable {var} does not exist. Please export {var}=<value> '
                  'and re-execute SwiftSeq\n{help_msg}')

    def __init__(self, environ_var, *args):
        message = EnvironmentVariableException.except_msg.format(
            var=environ_var,
            help_msg=SwiftSeqStrings.help_msg
        )
        super(EnvironmentVariableException, self).__init__(message, *args)


class WorkflowConfigException(Exception):
    except_msg = 'Workflow configuration JSON is malformed. {missing_element}.\n{help_msg}'

    def __init__(self, missing_element, *args):
        message = WorkflowConfigException.except_msg.format(
            missing_element=missing_element,
            help_msg=SwiftSeqStrings.help_msg
        )
        super(WorkflowConfigException, self).__init__(message, *args)
