#!/usr/bin/env python

"""
For a directory and a list of strings, find the files that match any string.

Usage:
    python __main__.py [OPTIONS] <scan-root> [<search-string> [...]]
    where:
        -a, --unpack-archives = Unpack and scan within archives
            (Default: Arhives will NOT be uncompressed and will be scanned
            as a single file). LIMITATIONS: Only zip and tar archives will be
            unpacked. Only gzip and bzip2 tar compression methods are supported.
        -B, --branding-text=<branding-text> = A string of text containing
            company or other information to add above the column headers in
            scan reports (Default: no text).
        -b, --branding-logo=<branding-logo> = (MS Excel only) An image
            file containing a corporate logo or other graphic to add above the
            column headers in scan reports (Default: no logo).
        -h, --help = Print usage information and exit.
        -e, --excel-output = Generate Microsoft Excel 2007 (.xlsx) output
            (Default: Generate comma-separated-value (CSV) text output)
        -i  --ingore-case = Ignore UPPER/lowercase differences when matching strings
            (Default: case differences are significant).
        -o, --output-dir=<output-dir> = Location for output (Default:
            <current working directory>).
        -s, --search-strings=<search-strings> = A file containing strings to
        search for, one per line (No Default).
        -q, --quiet = Decrease logging verbosity (may repeat). -vvvv will suppress all logging.
        -t, --temp-dir=<temp-dir> = Location for unpacking archives
            (Default: <output_dir>/temp).
        -v, --verbose = Increase logging verbosity.
    <scan-root> = Directory to scan (No Default).

Limitations:
    Requires Python 3.4 or later.
    Only handles jar, tar, and zip archives.
    Only handles bzip2, gzip, and xz tar compression.
    Only handles compression in archives, not single files.
    Maximum file size and results array length limited by available system RAM.
    Maximum archive size limited by available Scanner.temp_dir disk space.
"""

# Import Python standard modules.
import getopt
import logging
import os
import sys
import time

# Import 3rd party modules.

# Import project modules.
from string_path_search import Scanner, eprint, LOGGER, make_dir_safe, Output

# Define constants.


# Define global methods.
def print_usage():
    """Print the program usage."""
    usage = \
        """
        $ python -m string_path_search [OPTIONS] <scan-root> [<search-string> [...]]
        or (if the .exe was installed from pypi):
        $ string_path_search.exe [OPTIONS] <scan-root> [<search-string> [...]]
        where:
            -a, --unpack-archives = Unpack and scan within archives
                (Default: Arhives will NOT be uncompressed and will be scanned
                as a single file). Only jar, tar, and zip archives will be
                unpacked. Tar bzip2, gzip, and xz compression is supported.
            -B, --branding-text=<branding-text> = A string of text containing
                company or other information to add above the column headers in
                scan reports (Default: no text).
            -b, --branding-logo=<branding-logo> = (MS Excel only) An image
                file containing a corporate logo or other graphic to add above the
                column headers in scan reports (Default: no logo).
            -h, --help = Print usage information and exit.
            -e, --excel-output = Generate Microsoft Excel 2007 (.xlsx) output
                (Default: Generate comma-separated-value (CSV) text output)
            -i  --ingore-case = Ignore UPPER/lowercase differences when matching strings
                (Default: case differences are significant).
            -o, --output-dir=<output-dir> = Location for output (Default:
                <current working directory>).
            -s, --search-strings-file=<search-strings> = A file containing strings
                to search for, one per line (No Default).
            -q, --quiet = Decrease logging verbosity (may repeat). -qqqq will suppress all logging.
            -t, --temp-dir=<temp-dir> = Location for unpacking archives
                (Default: <output_dir>/temp).
            -v, --verbose = Increase logging verbosity.
            -x, --exclusions-file=<exclusion-file> = A file containing (base) filenames to
                exclude from the search results.
        <scan-root> = Directory to scan (No Default).
        <search-string> ... = One or more terms to search for in <scan-root>.
        """
    eprint(usage)


# pylint: disable=R0912,R0915
# R0912 = too-many-branches
# R0915 = too-many-statements
def parse_args():
    """Populate the config structure from the command line."""

    # Set program defaults.
    config = {
        'branding_text': None,
        'branding_logo': None,
        'excel_output': False,
        'ignore_case': False,
        'log_level': logging.INFO,
        'output_dir': os.getcwd(),
        'search_strings_file': None,
        'temp_dir': os.path.join(os.getcwd(), "temp"),
        'scan_archives': False,
        'exclusions_file': None,
        'search_strings': set(),
        'exclusions': set(),
    }

    sys_args = sys.argv[1:]

    # Process option flags.
    try:
        opts, args = getopt.getopt(sys_args, "aB:b:ehio:qs:t:vx:",
                                   ["scan_archives",
                                    "branding_text",
                                    "branding_logo",
                                    "excel_output",
                                    "help",
                                    "ignore_case",
                                    "output_dir",
                                    "quiet",
                                    "search-strings-file"
                                    "temp_dir",
                                    "verbose",
                                    "exclusions-file"])
    except getopt.GetoptError as err:
        eprint(err.msg)
        print_usage()
        sys.exit(2)

    if '-v' in opts and '-q' in opts:
        eprint("Improper usage: Use -v or -q, not both.")
        print_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-B", "--branding-text"):
            config['branding_text'] = arg.strip()
        elif opt in ("-b", "--branding-logo"):
            config['branding_logo'] = arg.strip()
        elif opt in ("-a", "--unpack-archives"):
            config['scan_archives'] = True
        elif opt in ("-e", "--excel-output"):
            config['excel_output'] = True
        elif opt in ("-h", "--help"):
            print_usage()
            sys.exit(0)
        elif opt in ("-i", "--ignore-case"):
            config['ignore_case'] = True
        elif opt in ("-o", "--output-dir"):
            config['output_dir'] = arg.strip()
        elif opt in ("-q", "--quiet"):
            if config['log_level'] == logging.CRITICAL:
                config['log_level'] = logging.NOTSET
            elif config['log_level'] == logging.ERROR:
                config['log_level'] = logging.CRITICAL
            elif config['log_level'] == logging.WARNING:
                config['log_level'] = logging.ERROR
            else:
                config['log_level'] = logging.WARNING
        elif opt in ("-s", "--search-string-file"):
            config['search_strings_file'] = arg.strip()
        elif opt in ("-t", "--temp-dir"):
            config['temp_dir'] = arg.strip()
        elif opt in ("-v", "--verbose"):
            config['log_level'] = logging.DEBUG
        elif opt in ("-x", "--exclusions-file"):
            config['exclusions_file'] = arg.strip()

    # Process positional parameters.
    if not args:
        eprint("Insufficient arguments on command line")
        print_usage()
        sys.exit(2)
    config['scan_root'] = args[0].strip()

    if len(args) > 1:
        for _ in args[1:]:
            config['search_strings'].add(_.strip())

    if not config['search_strings']:
        eprint("You must specify at least one search string, either via the -s "
               "<search-strings-file> option or as positional commandline "
               "argument.")
        print_usage()
        sys.exit(2)

    return config
# pylint: enable=R0912,R0915


def main():
    """Instantiate a Scanner and initiate a scan."""

    # In order for the setup.py console_scripts target to work, it must have
    # zero arguments. So, we get them internally.

    # Parse the command line.
    configs = parse_args()

    # Validate some options.
    if configs['branding_logo'] and not os.path.exists(configs['branding_logo']):
        eprint("The <branding-logo> , {0}, doesn't exist.".format(
            configs['branding_logo']))
        sys.exit(2)

    if not os.path.exists(configs['output_dir']) or not os.path.isdir(configs['output_dir']):
        eprint("The <output-dir> , {0}, doesn't exist or isn't a "
               "directory.".format(configs['output_dir']))
        sys.exit(2)
    make_dir_safe(configs['temp_dir'], True)

    if configs['search_strings_file']:
        if not os.path.exists(configs['search_strings_file']):
            eprint("-s <search-strings-file> argument, {0}, doesn't "
                   "exist".format(configs['search_strings_file']))
            sys.exit(2)
        with open(configs['search_strings_file'], "rt", encoding="utf-8") as fid:
            for line in fid:
                configs['search_strings'].add(line.strip())

    if configs['exclusions_file']:
        if not os.path.exists(configs['exclusions_file']):
            eprint("-s <exclusions_file> argument, {0}, doesn't "
                   "exist".format(configs['exclusions_file']))
            sys.exit(2)
        with open(configs['exclusions_file'], "rt", encoding="utf-8") as fid:
            for line in fid:
                configs['exclusions'].add(line.strip().casefold())

    if not os.path.exists(configs['scan_root']):
        eprint("The <scan-root> , {0}, doesn't exist.".format(configs['scan_root']))
        sys.exit(2)

    # Setup the logger
    LOGGER.setLevel(configs['log_level'])
    LOGGER.info('Startup')

    scanner = Scanner(configs)
    scanner.scan()
    output = Output.get_output(scanner.HEADERS, scanner.get_results(), configs)
    output.output()

if __name__ == '__main__':
    main()
