"""
General purpose utilities.
"""

import argparse
import os


def realpath(p):
    return os.path.realpath(os.path.expanduser(p))


def real_file_path(path):
    """
    Check if file exists.

    :param str path: Path to be checked
    :returns: realpath in case the file exists
    :rtype: str
    :raises argparse.ArgumentTypeError: if file does not exist
    """
    path = realpath(path)
    if not os.path.isfile(path):
        raise argparse.ArgumentTypeError
    return path
