import os
import sys
from pkg_resources import Requirement, resource_listdir, resource_filename

FIRST = 0


def message_to_screen(message, banner=False, bannerdashes=57):
    if not banner:
        sys.stderr.write(message + '\n')
    else:
        sys.stderr.write('{dashes}\n{message}\n{dashes}\n'.format(
            message=message,
            dashes='-'*bannerdashes
        ))


def get_util_scripts():
    util_scripts = dict()
    for util_script_filename in resource_listdir(Requirement.parse('swag'), 'swag/util_scripts'):
        util_name = util_script_filename.rsplit('.', 1)[FIRST]
        util_full_filepath = resource_filename(Requirement.parse('swag'), 'swag/util_scripts/{}'.format(
            util_script_filename
        ))
        util_scripts['util_{}'.format(util_name)] = util_full_filepath
    return util_scripts


def parse_config(config_filepath):
    """
    Will parse the algorithm or reference config and return a dict
    connecting algorithm/reference names to filepaths. Will eventually
    need to do some exception handling here

    Could also check to be sure the path given is a file
    """
    config_dict = dict()
    with open(config_filepath) as config_file:
        for line in config_file:
            # Check to make sure the line has content and doesn't start with a hash
            try:
                if line.strip()[0] == '#':
                    # If it's a comment move to the next line
                    continue
            except IndexError:
                # If there's an index error that means the line was blank
                continue

            # Extract key-value pair
            try:
                key, val = line.strip().split('=')
                config_dict[key] = val
            except ValueError:
                raise Exception('Config file {} is malformed.'.format(config_filepath))

    return config_dict


def read_data(filename):
    """ Read data from a file. 

    :param filename: str Path to the file to read
    :return: list of str Stripped lines from the file
    """

    if not os.path.exists(filename):
        raise IOError("File '{}' not found".format(filename))

    with open(filename, 'r') as f:
        return [i.strip() for i in f.readlines()]
        # FIXME shortened for testing
        # return [i.strip() for i in f.readlines()][:2]
