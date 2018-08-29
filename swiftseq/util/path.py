import os
from swiftseq.core import SwiftSeqStrings


def mkdirs(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def mksym(source, destination):
    """
    Creates a symbolic link from source to destination. If the parent folder of
    destination doesn't exist, it's created.
    :return: If successful, the path of the created symlink
    """
    destination_parent_folder = os.path.dirname(destination)

    # If symlink destination folder doesn't exist, create it
    if not os.path.exists(destination_parent_folder):
        mkdirs(destination_parent_folder)

    # Create the symlink
    if not os.path.exists(destination):
        os.symlink(source, destination)
    return destination


def is_valid_file(arg):
    """ Will check that files exists and will raise a parser error if it
    does not. This will not yield true for directories"""

    if not os.path.isfile(arg):
        raise IOError('The provided file {arg} does not exist.\n{help_msg}'.format(
            arg=arg,
            help_msg=SwiftSeqStrings.help_msg
        ))


def is_valid_dir(arg):
    """ Will check that the path exists (is a directory) and also be sure
    that it isn't a file. Will raise a parser error if it is not."""

    if not os.path.exists(arg) or os.path.isfile(arg):
        raise IOError('The provided argument {arg} is not a directory.\n{help_msg}'.format(
            arg=arg,
            help_msg=SwiftSeqStrings.help_msg
        ))


def is_valid_tmp_dir(arg):
    """ Will check that the path exists (is a directory) and also be sure
    that it isn't a file.
    - If the dir does not exist, will try to make it"""

    # if the path does not exist or is a file
    if not os.path.exists(arg) or os.path.isfile(arg):
        try:
            # Note: If a file is supplied a dir with the same path as that file
            # Will be created
            os.mkdir(arg)
        except OSError:
            raise IOError('The provided argument {arg} is not a directory and cannot be created.\n'
                          'Please supply a valid directory or path.\n{help_msg}'.format(
                arg=arg,
                help_msg=SwiftSeqStrings.help_msg
            ))
