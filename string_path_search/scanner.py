"""
For a directory and a list of strings, find the files that match any string.

Usage:
    python3 string_path_search.py [OPTIONS] <scan-root> [<search-string> [...]]
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
    Only handles tar and zip archives.
    Only handles gzip, bzip2, and zip tar compression.
    Only handles compression in archives, not single files.
    Maximum file size and results array length limited by available system RAM
    Maximum archive size limited by available Scanner.temp_dir disk space

Todo:
    Config file
    Pypi deployment
"""

# Import Python standard modules.
from abc import abstractmethod
import codecs
import csv
import hashlib
import getopt
import logging
import os
import random
import re
import shutil
import string
import sys
import tarfile
import time
import unicodedata
import zipfile

# Import 3rd party modules.
import xlsxwriter

# Define constants.
DIR_REGEX = re.compile(r'[/]$')
JAR_REGEX = re.compile(r'\.jar$')
TAR_REGEX = re.compile(r'\.(?:tar|tar.gz|tgz|tar.bzip2|tar.bz2|tbz2)$')
ZIP_REGEX = re.compile(r'\.zip$')
ARCH_REGEX = re.compile(r'\.(?:cab|cpio|ear|jar|rpm|tar|tar.gz|tgz|tar.bzip2'
                        r'|tar.bz2|tbz2|war|zip)$')

# Define global variables.
LOGGER = logging.getLogger(__name__)
LEVEL_STRINGS = {logging.DEBUG: 'DEBUG', logging.INFO: 'INFO',
                 logging.WARNING: 'WARNING', logging.ERROR: 'ERROR',
                 logging.CRITICAL: 'CRITICAL', logging.NOTSET: 'NOTSET'}


# Define global methods.
def eprint(*args, **kwargs):
    """Print to stderr."""
    print(*args, file=sys.stderr, **kwargs)


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
        os.makedirs(path, True)
    except OSError as exc:
        LOGGER.info("ERROR: Path=%s does not exist and cannot be created. Errno=%d", path,
                    exc.errno)
        if raise_errors:
            raise
        path = ''

    return path


class Scanner:
    """Class to scan a directory tree for a set of strings"""

    HEADERS = ('String', 'MD5 Digest', 'Name', 'Location')

    def __init__(self, configs):
        """
        Setup the class instance.

        Parameters:
            configs -- Dictionary of settings populated from the command line by parse_args()
        """
        self.scan_root = configs['scan_root']
        self.temp_dir = configs['temp_dir']
        self.ignore_case = configs['ignore_case']
        self.search_strings = []
        for search_string in configs['search_strings']:
            normal_string = unicodedata.normalize('NFKD', search_string)
            if self.ignore_case:
                normal_string = normal_string.casefold()
            self.search_strings.append((normal_string, search_string))
        self.exclusions = configs['exclusions']
        self.scan_archives = configs['scan_archives']
        self.scan_results = {}
        self.stats = {}
        if sys.version_info[0] + sys.version_info[1] / 10 < 3.4:
            LOGGER.error("ERROR: This script requires Python 3.4 or greater.")
            sys.exit(-1)
        if not os.path.isdir(configs['scan_root']):
            raise ValueError("scan_root {0} is not a directory".format(
                configs['scan_root']))
        if not self.search_strings:
            raise ValueError("No strings to search!")
        if self.scan_archives:
            make_dir_safe(configs['temp_dir'])

    def _walk(self, thing=None, parent=None):
        """Walk a tree based on thing."""
        if not thing:
            thing = self.scan_root
        if self.scan_archives and ZIP_REGEX.search(thing) or JAR_REGEX.search(thing):
            yield from self._zip_walk(thing, parent)
        elif self.scan_archives and TAR_REGEX.search(thing):
            yield from self._tar_walk(thing, parent)
        elif ARCH_REGEX.search(thing):
            if self.scan_archives:
                LOGGER.warning("Skipping unsupported archive %s", thing)
        elif os.path.isdir(thing):
            yield from self._dir_walk(thing)
        else:
            if not os.path.isfile(thing):
                LOGGER.warning("Thing '%s' is neither a directory nor is it a file", thing)
                return

            try:
                with open(thing, 'rb') as fid:
                    file_bytes = fid.read()
                    yield (os.path.basename(thing),
                           os.path.join(self.scan_root, os.path.dirname(thing)),
                           calculate_md5(file_bytes), file_bytes)
            except FileNotFoundError:
                LOGGER.error("Can't open file=%s", thing)
                return

    def _dir_walk(self, path):
        """Walk a directory."""
        LOGGER.info("Walking dir=%s", path)
        for entry in os.scandir(path):
            if os.path.basename(entry.path).casefold() in self.exclusions:
                continue
            yield from self._walk(entry.path)

    def _zip_walk(self, zip_file, parent=None):
        """
        Generate name, filebuf tuples from a recursive zip scan.

        Args:
            zip_file -- The full path to the .zip file to scan.
            parent - The root for the extraction if this is an inner archive.
        """
        archive_type = 'jar' if JAR_REGEX.search(zip_file) else 'zip'
        LOGGER.info("Walking %s file=%s", archive_type, zip_file)
        # Pseudo-path, don't use os.path.join().
        parent = '/'.join([parent, os.path.basename(zip_file)]) if parent \
            else os.path.basename(zip_file)
        with zipfile.ZipFile(zip_file) as zip_archive:
            for info in zip_archive.infolist():
                name = info.filename
                if DIR_REGEX.search(name):
                    continue
                if os.path.basename(name).casefold() in self.exclusions:
                    continue
                if ARCH_REGEX.search(name):
                    extract_dir = os.path.join(self.temp_dir, random_string())
                    make_dir_safe(extract_dir)
                    inner_archive = os.path.join(extract_dir, name)
                    try:
                        zip_archive.extract(name, extract_dir)
                        if ARCH_REGEX.search(name):
                            yield from self._walk(inner_archive, parent)
                    except BaseException:
                        # Todo: Catalog actual exceptions and refine this
                        #  clause.
                        LOGGER.error("Caught an exception of type=%s "
                                     "while processing inner archive %s",
                                     sys.exc_info()[0], name)
                        continue
                    finally:
                        shutil.rmtree(extract_dir)
                else:
                    fid = None
                    try:
                        with zip_archive.open(name) as fid:
                            # Pseudo-path, don't use os.path.join().
                            file_bytes = fid.read()
                            yield (os.path.basename(name),
                                   '/'.join([self.scan_root, parent,
                                             os.path.dirname(name)]),
                                   calculate_md5(file_bytes), file_bytes)
                    except BaseException:
                        LOGGER.error("Caught an exception of type=%s: %s",
                                     sys.exc_info()[0], sys.exc_info()[1])

    def _tar_walk(self, tar_file, parent=None):
        """
        Generate name, filebuf tuples from a recursive tar scan.

        Args:
            tar_file -- The name of the .tar (or compressed variant) file
            to scan.
        """
        LOGGER.info("Walking tar file=%s", tar_file)
        # Pseudo-path, don't use os.path.join().
        parent = '/'.join([parent, os.path.basename(tar_file)]) if parent \
            else os.path.basename(tar_file)
        with tarfile.open(tar_file, 'r') as tar_archive:
            for entry in tar_archive:
                if entry.isdir():
                    continue
                elif entry.isreg():
                    if os.path.basename(entry.name).casefold() in self.exclusions:
                        continue
                    if ARCH_REGEX.search(entry.name):
                        extract_dir = os.path.join(self.temp_dir, random_string())
                        make_dir_safe(extract_dir)
                        inner_archive = os.path.join(extract_dir, entry.name)
                        try:
                            tar_archive.extract(entry, extract_dir)
                            if ARCH_REGEX.search(inner_archive):
                                yield from self._walk(inner_archive, parent)
                        except BaseException:
                            LOGGER.error("Caught an exception of type=%s "
                                         "while processing inner archive=%s",
                                         sys.exc_info()[0], entry.name)
                            continue
                        finally:
                            shutil.rmtree(extract_dir)
                    else:
                        try:
                            with tar_archive.extractfile(entry) as fid:
                                file_bytes = fid.read()
                                yield (os.path.basename(entry.name),
                                       '/'.join([self.scan_root, parent,
                                                 os.path.dirname(entry.name)]),
                                       calculate_md5(file_bytes), file_bytes)
                        except BaseException:
                            LOGGER.error("Caught an exception of type=%s "
                                         "while extracting file=%s",
                                         sys.exc_info()[0], entry.name)

    def _scan_file(self, file_bytes):
        """
        Generator method that yields matching search_strings.

        Args:
            file_bytes -- The content of a file, as a byte string.
        """
        # Strip out all of the valid utf-8 characters from a byte stream
        # and normalize the result.
        file_str = unicodedata.normalize('NFKD',
                                         codecs.decode(file_bytes,
                                                       'utf-8',
                                                       errors='ignore')
                                         )
        if not file_str:
            return

        if self.ignore_case:
            file_str = file_str.casefold()
        for normal_str, search_str in self.search_strings:
            if normal_str in file_str:
                yield search_str

    def scan(self):
        """Scan scan_root and print matches."""

        LOGGER.info("Scanning %s", self.scan_root)

        self.scan_results = {}
        md5s = set()
        self.stats = {'files_scanned': 0, 'files_matched': 0}
        for name, path, md5, file_bytes in self._walk(None):
            self.stats['files_scanned'] += 1
            if self.stats['files_scanned'] % 1000 == 0:
                LOGGER.info("Matched %d of %d files scanned so far.",
                            self.stats['files_matched'],
                            self.stats['files_scanned'])
            for matched_string in self._scan_file(file_bytes):
                if matched_string not in self.scan_results.keys():
                    self.scan_results[matched_string] = []
                self.scan_results[matched_string].append((name, md5, path))
                LOGGER.debug("Matched String=%s, Name=%s, MD5 Digest=%s, Location=%s",
                             matched_string, name, md5, path)
                if md5 not in md5s:
                    md5s.add(md5)
                    self.stats['files_matched'] += 1

        LOGGER.info("Scan complete. Matched %d of %d files.",
                    self.stats['files_matched'], self.stats['files_scanned'])

    def get_results(self):
        """Flatten search_results into an array of tuples."""
        results = []
        for match_str, result_rows in self.scan_results.items():
            for name, md5, path in result_rows:
                results.append((match_str, md5, name, path))
        return results


class Output:
    """
    Format an output tuple to the desired device.
    """

    def __init__(self, header, rows, config):
        """
        Set it up.

        Args:
            header - A list of column labels (No Default).
            rows - A list of lists of cell values (No Default).
            config:
                output_file - A file for output (Default: Output to the console).
                branding_text - A list of cell values to be output before the header.
                branding_logo - (Excel output only) Optional image to be inserted
            before the header.

        """
        self.rows = rows
        self.output_file = config['output_file']
        self.header = header
        self.branding_logo = config['branding_logo']
        self.branding_text = config['branding_text']

    @abstractmethod
    def output(self):
        """Output the rows."""


class CSVOutput(Output):
    """
    Outputter for text (CSV) file output.

    Output goes to the console if the file attribute isn't set.
    """

    def output(self):
        """Output the rows."""
        out_fh = sys.stdout
        if self.output_file:
            try:
                make_dir_safe(self.output_file)
                out_fh = open(self.output_file, encoding='utf-8', mode='w')
            except IOError:
                LOGGER.error("Can't open file=%s", self.output_file)
                raise
        csv_writer = csv.writer(out_fh, delimeter=',', quotechar='"',
                                quoting=csv.QUOTE_MINIMAL)
        if self.branding_text:
            csv_writer.writerow(self.branding_text)
        for header_row in self.header:
            csv_writer.writerow(header_row)
        for row in self.rows:
            csv_writer.writerow(row)

        LOGGER.info("Writing output to %s", self.output_file)
        out_fh.close()


class ExcelOutput(Output):
    """Outputter for Microsoft Excel (.xlsx) output."""

    def output(self):
        """Output the rows."""
        workbook = xlsxwriter.Workbook(self.output_file)
        sheet = workbook.add_worksheet()
        row_num = 0
        if self.branding_logo and os.path.exists(self.branding_logo):
            sheet.insert_image(row_num, 0, self.branding_logo)
            row_num += 5
        if self.branding_text:
            for col_num, cell_value in enumerate(self.branding_text):
                sheet.write(row_num, col_num, cell_value)
            row_num += 2

        for col_num, cell_value in enumerate(self.header):
            sheet.write(row_num, col_num, cell_value)

        for row in self.rows:
            row_num += 1
            for col_num, cell_value in enumerate(row):
                sheet.write(row_num, col_num, cell_value)

        LOGGER.info("Writing output to %s", self.output_file)
        workbook.close()


def print_usage():
    """Print the program usage."""
    usage = \
        """
        python3 string_path_search.py [OPTIONS] <scan-root> [<search-string> [...]]
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
            -q, --quiet = Decrease logging verbosity (may repeat). -vvvv will suppress all logging.
            -t, --temp-dir=<temp-dir> = Location for unpacking archives
                (Default: <output_dir>/temp).
            -v, --verbose = Increase logging verbosity.
            -x, --exclusions-file=<exclusion-file> = A file containing (base) filenames to
                exclude from the search results.
        <scan-root> = Directory to scan (No Default).
        <search-string> ... = One or more terms to search for in <scan-root>.
        """
    eprint(usage)


def parse_args(sys_args):
    """Populate the config structure from the command line."""

    # Set program defaults.
    config = {
        'branding_text': None,
        'branding_logo': None,
        'excel_output': True,
        'ignore_case': True,
        'log_level': logging.INFO,
        'output_dir': os.getcwd(),
        'search_strings_file': None,
        'temp_dir': os.path.join(os.getcwd(), "temp"),
        'scan_archives': False,
        'exclusions_file': None,
        'search_strings': set(),
        'exclusions': set()}

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


def main(sys_args):
    """Instantiate a Scanner and initiate a scan."""

    # Set program constants.
    config = parse_args(sys_args)

    # Validate some options.
    if config['branding_logo'] and not os.path.exists(config['branding_logo']):
        eprint("The <branding-logo> , {0}, doesn't exist.".format(
            config['branding_logo']))
        sys.exit(2)

    if not os.path.exists(config['output_dir']) or not os.path.isdir(config['output_dir']):
        eprint("The <output-dir> , {0}, doesn't exist or isn't a "
               "directory.".format(config['output_dir']))
        sys.exit(2)
    make_dir_safe(config['temp_dir'], True)

    if config['search_strings_file']:
        if not os.path.exists(config['search_strings_file']):
            eprint("-s <search-strings-file> argument, {0}, doesn't "
                   "exist".format(config['search_strings_file']))
            sys.exit(2)
        with open(config['search_strings_file'], "rt", encoding="utf-8") as fid:
            for line in fid:
                config['search_strings'].add(line.strip())

    if config['exclusions_file']:
        if not os.path.exists(config['exclusions_file']):
            eprint("-s <exclusions_file> argument, {0}, doesn't "
                   "exist".format(config['exclusions_file']))
            sys.exit(2)
        with open(config['exclusions_file'], "rt", encoding="utf-8") as fid:
            for line in fid:
                config['exclusions'].add(line.strip().casefold())

    if not os.path.exists(config['scan_root']) or not os.path.isdir(config['scan_root']):
        eprint("The <scan-root> , {0}, doesn't exist or isn't a "
               "directory.".format(config['scan_root']))
        sys.exit(2)

    # Setup the logger
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(filename)s:%('
                               'funcName)s:%(lineno)s - %('
                               'message)s',
                        datefmt='%d-%b-%y %H:%M:%S', level=config['log_level'])
    eprint("Minimum logging level is {0}".format(LEVEL_STRINGS[config['log_level']]))
    LOGGER.info("Startup")

    scanner = Scanner(config)
    scanner.scan()
    config['output_file'] = os.path.join(config['output_dir'],
                                         '-'.join(["scan", time.strftime('%Y%m%d%H%M')]))
    if config['excel_output']:
        config['output_file'] += ".xlsx"
        output = ExcelOutput(scanner.HEADERS, scanner.get_results(), config)
    else:
        config['output_file'] += ".csv"
        output = CSVOutput(scanner.HEADERS, scanner.get_results(), config)
    output.output()


if __name__ == '__main__':
    main(sys.argv[1:])
