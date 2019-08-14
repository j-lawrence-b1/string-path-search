"""Grab-bag of utility functions."""

# Import Python standard modules.
import hashlib
import logging
import os
import random
import string
import sys

# Import 3rd party modules.

# Define constants.

# Set program constants.
LEVEL_STRINGS = {logging.DEBUG: 'DEBUG', logging.INFO: 'INFO',
                 logging.WARNING: 'WARNING', logging.ERROR: 'ERROR',
                 logging.CRITICAL: 'CRITICAL', logging.NOTSET: 'NOTSET'}
LOGGER = None


def random_string(length=5):
    """Return a random string of the desired length."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


def calculate_md5(my_str):
    """Calculate the md5 digest of a string"""
    md5 = hashlib.md5()
    md5.update(my_str)
    return md5.hexdigest()


def make_dir_safe(path, raise_errors=True):
    """
    Create a directory. Optionally, suppress exceptions.

    Args:
        path -- The directory to create.

    Keyword_args
    """
    if os.path.isdir(path):
        return path

    try:
        os.makedirs(path, mode=0o777, exist_ok=True)
    except OSError as exc:
        eprint("ERROR: Path=%s does not exist and cannot be created. Errno=%d", path,
               exc.errno)
        if raise_errors:
            raise
        path = ''

    return path


def eprint(*args, **kwargs):
    """Print to stderr."""
    print(*args, file=sys.stderr, **kwargs)


def get_logger(log_level=logging.INFO,
               msg_format='%(asctime)s - %(levelname)s - %(filename)s:%(funcName)s:%(lineno)s'
                          '- %(message)s',
               cls_name=__name__):
    """
    Instantiate a new logger.

    Args:
        log_level = One of the log reporting levels defined in the logging module
                    (Default:  logging.INFO)
        cls_name = Class name for this logger (Default: __name__)
    """

    logging.basicConfig(format=msg_format, level=log_level)
    return logging.getLogger(cls_name)


LOGGER = get_logger(cls_name=os.path.basename(sys.argv[0]))
