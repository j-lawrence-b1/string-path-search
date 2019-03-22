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
from abc import ABC, abstractmethod
import codecs
import csv
import errno
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
TAR_REGEX = re.compile(r'\.(?:tar|tar.gz|tgz|tar.bzip2|tar.bz2|tbz2)$')
ZIP_REGEX = re.compile(r'\.zip$')
ARCH_REGEX = re.compile(r'\.(?:tar|tar.gz|tgz|tar.bzip2|tar.bz2|tbz2|zip)')

# Define global variables.
logger = logging.getLogger(__name__)

# Define global methods.
def eprint(*args, **kwargs):
    """Print to stderr."""
    print(*args, file=sys.stderr, **kwargs)

def random_string(length=5):
    """Return a random string of the desired length."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits,
                                  k=length))

def calculate_md5(str):
    """Calculate the md5 digest of a string"""
    m = hashlib.md5()
    m.update(str)
    return m.hexdigest()

def make_dir_safe(path, raise_errors=True):
    """Create a directory. Optionally, suppress exceptions.

    Args:
        path -- The directory to create.

    Keyword_args
    """
    if os.path.isdir(path):
        return path
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            return path
        else:
            logger.info("ERROR: Path={0} does not exist and cannot be created. "
                   "Errno={1}".format(path, exc.errno))
            if raise_errors:
                raise
            else:
                return ''

class Scanner:
    """Class to scan a directory tree for a set of strings"""

    HEADERS = ('String', 'MD5 Digest', 'Name', 'Location')

    def __init__(self,
                 scan_root,
                 search_strings,
                 exclusions=None,
                 scan_archives=False,
                 temp_dir=None,
                 ignore_case=False,
                 output_file=None,
                 branding=None):
        """
        Setup the class instance.

        Parameters:
            scan_root -- Root directory of scan, as a string. The scan_root
                         directory must exist.
            search_strings -- A list of strings to match against file contents.
                              At least one search_string must be provided.
            exclusions -- A list of strings to filter file names (Default:
                          scan all files).
            scan_archives -- If True, unpack and explore archives. Currently,
                             only tar (gzip and bzip compression only), and
                             zip archives are supported.(Default: False).
            temp_dir -- With scan_archives == True, the directory for unpacking
                        inner archives (i.e., archives within archives), as a
                        string. The temp_dir will be created if it doesn't
                        already exist (Default: None).
            ignore_case -- If true, ignore capitalization differences when
                           matching text (Default: Treat case as significant).
        """
        if sys.version_info[0] + sys.version_info[1] / 10 < 3.4:
            logger.error("ERROR: This script requires Python 3.4 or greater.")
            sys.exit(-1)

        if not os.path.isdir(scan_root):
            raise ValueError("scan_root {0} is not a directory".format(
                scan_root))
        if not search_strings:
            raise ValueError("No strings to search!")
        if scan_archives:
            make_dir_safe(temp_dir)
        self.scan_root = scan_root
        self.temp_dir = temp_dir
        self.search_strings = []
        for search_string in search_strings:
            normal_string = unicodedata.normalize('NFKD', search_string)
            if ignore_case:
                normal_string = normal_string.casefold()
            self.search_strings.append((normal_string, search_string))
        self.exclusions = exclusions
        self.scan_archives = scan_archives
        self.ignore_case = ignore_case

    def _dir_walk(self, path):
        """Generate file objects from a recursive scan_root scan."""
        if not path:
            path = self.scan_root
        logger.info("Walking directory tree={0}".format(path))
        for entry in os.scandir(path):
            if os.path.basename(entry.path) in self.exclusions:
                continue
            if entry.is_dir(follow_symlinks=False):
                yield from self._dir_walk(entry.path)
            elif self.scan_archives and ZIP_REGEX.search(entry.path):
                yield from self._zip_walk(entry.path)
            elif self.scan_archives and TAR_REGEX.search(entry.path):
                yield from self._tar_walk(entry.path)
            else:
                f = open(entry.path, 'rb')
                file_bytes = f.read()
                yield(os.path.basename(entry.path),
                    os.path.join(self.scan_root, os.path.dirname(entry.path)),
                    calculate_md5(file_bytes), file_bytes)

    def _zip_walk(self, zip_file, parent=None):
        """
        Generate name, filebuf tuples from a recursive zip scan.

        Args:
            zip_file -- The full path to the .zip file to scan.
            parent - The root for the extraction if this is an inner archive.
        """
        logger.info("Walking zip file={0}".format(zip_file))
        # Pseudo-path, don't use os.path.join().
        parent = '/'.join([parent, os.path.basename(zip_file)]) if parent \
            else os.path.basename(zip_file)
        with zipfile.ZipFile(zip_file) as zip_archive:
            for info in zip_archive.infolist():
                name = info.filename
                if DIR_REGEX.search(name):
                    continue
                if os.path.basename(name) in self.exclusions:
                    continue
                if ARCH_REGEX.search(name):
                    extract_dir = os.path.join(self.temp_dir, random_string())
                    make_dir_safe(extract_dir)
                    inner_archive = os.path.join(extract_dir, name )
                    try:
                        zip_archive.extract(name, extract_dir)
                        if TAR_REGEX.search(name):
                            yield from self._tar_walk(inner_archive, parent)
                        elif ZIP_REGEX.search(name):
                            yield from self._zip_walk(inner_archive, parent)
                    except BaseException as exc:
                        # Todo: Catalog actual exceptions and refine this
                        #  clause.
                        logger.error("Caught an exception of type={0} "
                               "while processing inner archive {1}"
                               .format(sys.exc_info()[0], name))
                        continue
                    finally:
                        shutil.rmtree(extract_dir)
                else:
                    f = None
                    try:
                        f = zip_archive.open(name)
                        # Pseudo-path, don't use os.path.join().
                        file_bytes = f.read()
                        yield (os.path.basename(name),
                               '/'.join([self.scan_root, parent,
                                         os.path.dirname(name)]),
                               calculate_md5(file_bytes), file_bytes)
                    except BaseException:
                        logger.error("Caught an exception of type={0}: {1}"
                               .format(sys.exc_info()[0], sys.exc_info()[1]))
                    finally:
                        if f:
                            f.close()


    def _tar_walk(self, tar_file, parent=None):
        """
        Generate name, filebuf tuples from a recursive tar scan.

        Args:
            tar_file -- The name of the .tar (or compressed variant) file
            to scan.
        """
        logger.info("Walking tar file={0}".format(tar_file))
        # Pseudo-path, don't use os.path.join().
        parent = '/'.join([parent, os.path.basename(tar_file)]) if parent \
            else os.path.basename(tar_file)
        with tarfile.open(tar_file, 'r') as tar_archive:
            for entry in tar_archive:
                if entry.isdir():
                    continue
                elif entry.isreg():
                    if os.path.basename(entry.name) in self.exclusions:
                        continue
                    if ARCH_REGEX.search(entry.name):
                        extract_dir = os.path.join(self.temp_dir, random_string())
                        make_dir_safe(extract_dir)
                        inner_archive = os.path.join(extract_dir, entry.name )
                        try:
                            tar_archive.extract(entry, extract_dir)
                            if TAR_REGEX.search(inner_archive):
                                yield from self._tar_walk(inner_archive, parent)
                            elif ZIP_REGEX.search(inner_archive):
                                yield from self._zip_walk(inner_archive, parent)
                        except BaseException as exc:
                            logger.error("Caught an exception of type={0} "
                                         "while processing inner archive {1}"
                                         .format(sys.exc_info()[0], entry.name))
                            continue
                        finally:
                            shutil.rmtree(extract_dir)
                    else:
                        f = None
                        try:
                            f = tar_archive.extractfile(entry)
                            file_bytes = f.read()
                            yield(os.path.basename(entry.name),
                                  '/'.join([self.scan_root, parent,
                                            os.path.dirname(entry.name)]),
                                  calculate_md5(file_bytes), file_bytes)
                        except BaseException:
                            logger.error("Caught an exception of type={0} "
                                         "while extracting file {1}"
                                         .format(sys.exc_info()[0], entry.name))
                        finally:
                            if f:
                                f.close()

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
            return None

        if self.ignore_case:
            file_str = file_str.casefold()
        for normal_str, search_str in self.search_strings:
            if normal_str in file_str:
                yield search_str

    def scan(self):
        """Scan scan_root and print matches."""

        logger.info("Scanning {0}".format(self.scan_root))

        self.scan_results = {}
        md5s = set()
        self.stats = {'files_scanned': 0, 'files_matched': 0}
        for name, path, md5, file_bytes in self._dir_walk(None):
            self.stats['files_scanned'] += 1
            if self.stats['files_scanned'] % 1000 == 0:
                logger.info("Matched {0} of {1} files scanned so " 
                            "far.".format(self.stats['files_matched'],
                                          self.stats['files_scanned']))
            for matched_string in self._scan_file(file_bytes):
                if matched_string not in self.scan_results.keys():
                    self.scan_results[matched_string] = []
                self.scan_results[matched_string].append((name, md5, path))
                logger.debug("Matched String {0}, Name {1}, MD5 Digest {2}, "
                             "Location {3}".format(matched_string, name, md5,
                                                   path))
                if md5 not in md5s:
                    md5s.add(md5)
                    self.stats['files_matched'] += 1

        logger.info("Scan complete. Matched {0} of {1} files.".format(
            self.stats['files_matched'], self.stats['files_scanned']))

    def get_results(self):
        """Flatten search_results into an array of tuples."""
        rows = []
        for string in self.scan_results.keys():
            for name, md5, path in self.scan_results[string]:
                rows.append((string, md5, name, path))
        return rows


class Output:
    """
    Format an output tuple to the desired device.
    """
    def __init__(self, header, rows, output_file=None, branding_text=None,
                 branding_logo=None):
        """
        Set it up.

        Args:
            header - A list of column labels (No Default).
            rows - A list of lists of cell values (No Default).
            output_file - A file for output (Default: Output to the console).
            branding_text - A list of cell values to be output before the header.
            branding_logo - (Excel output only) Optional image to be inserted
            before the header.

        """
        self.rows = rows;
        self.output_file = output_file
        self.header = header
        self.branding_logo = branding_logo
        self.branding_text = branding_text

    @abstractmethod
    def output(self):
        """Output the rows."""
        pass


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
                logger.error("Can't open file={0}".format(self.output_file))
                raise
        csv_writer = csv.writer(out_fh, delimeter=',', quotechar='"',
                                quoting=csv.QUOTE_MINIMAL)
        if self.branding_text:
            csv_writer.writerow(self.branding_text)
        for header_row in self.header:
            csv_writer.writerow(header_row)
        for row in self.rows:
            csv_writer.writerow(row)

        logger.info("Writing output to {0}".format(self.output_file))
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

        logger.info("Writing output to {0}".format(self.output_file))
        workbook.close()

def print_usage():
    usage = \
    """
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
        -s, --search-strings-file=<search-strings> = A file containing strings
            to search for, one per line (No Default).
        -q, --quiet = Decrease logging verbosity (may repeat). -vvvv will suppress all logging.
        -t, --temp-dir=<temp-dir> = Location for unpacking archives
            (Default: <output_dir>/temp).
        -v, --verbose = Increase logging verbosity.
        -x, --exclusions-file=<exclusion-file> = A file containing filenames to
            exclude from the search results.
    <scan-root> = Directory to scan (No Default).
    <search-string> ... = One or more terms to search for in <scan-root>.
    """
    eprint(usage)

def main(sys_args):
    """Process the commandline and initiate a scan."""

    # Set program constants.
    LEVEL_STRINGS = {logging.DEBUG:'DEBUG', logging.INFO:'INFO',
                     logging.WARNING:'WARNING', logging.ERROR:'ERROR',
                     logging.CRITICAL:'CRITICAL', logging.NOTSET:'NOTSET'}

    # Set program defaults.
    branding_text = None
    branding_file = None
    excel_output = True
    ignore_case = True
    log_level = logging.INFO
    output_dir = os.getcwd()
    search_strings_file = None
    temp_dir = os.path.join(os.getcwd(), "temp")
    scan_archives = False
    search_strings_file = None
    exclusions_file = None
    search_strings = set()
    exclusions = set()

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
            branding_text = arg.strip()
        elif opt in ("-b", "--branding-logo"):
            branding_logo = arg.strip()
        elif opt in ("-a", "--unpack-archives"):
            scan_archives = True
        elif opt in ("-e", "--excel-output"):
            excel_output = True
        elif opt in ("-h", "--help"):
            print_usage()
            sys.exit(0)
        elif opt in ("-i", "--ignore-case"):
            ignore_case = True
        elif opt in ("-o", "--output-dir"):
            output_dir = arg.strip()
        elif opt in ("-q", "--quiet"):
            if log_level == logging.CRITICAL:
                log_level = logging.NOTSET
            elif log_level == logging.ERROR:
                log_level = logging.CRITICAL
            elif log_level == logging.WARNING:
                log_level = logging.ERROR
            else:
                log_level = logging.WARNING
        elif opt in ("-s", "--search-string-file"):
            search_strings_file = arg.strip()
        elif opt in ("-t", "--temp-dir"):
            temp_dir = arg.strip()
        elif opt in ("-v", "--verbose"):
            log_level = logging.DEBUG
        elif opt in ("-x", "--exclusions-file"):
            exclusions_file = arg.strip()

    if branding_logo and not os.path.exists(branding_logo):
        eprint("The <branding-logo> , {0}, doesn't exist.".format(
            branding_logo))
        sys.exit(2)

    if not os.path.exists(output_dir) or not os.path.isdir(output_dir):
        eprint("The <output-dir> , {0}, doesn't exist or isn't a "
               "directory.".format(output_dir))
        sys.exit(2)
    make_dir_safe(temp_dir, True)

    if search_strings_file:
        if not os.path.exists(search_strings_file):
            eprint("-s <search-strings-file> argument, {0}, doesn't "
                   "exist".format(search_strings_file))
            sys.exit(2)
        with open(search_strings_file, "rt", encoding="utf-8") as f:
            for line in f:
                search_strings.add(line.strip())

    if exclusions_file:
        if not os.path.exists(exclusions_file):
            eprint("-s <exclusions_file> argument, {0}, doesn't "
                   "exist".format(exclusions_file))
            sys.exit(2)
        with open(exclusions_file, "rt", encoding="utf-8") as f:
            for line in f:
                exclusions.add(line.strip())

    # Process positional parameters.
    if not args:
        eprint("Insufficient arguments on command line")
        print_usage()
        sys.exit(2)
    scan_root = args[0].strip()
    if not os.path.exists(scan_root) or not os.path.isdir(scan_root):
        eprint("The <scan-root> , {0}, doesn't exist or isn't a "
               "directory.".format(scan_root))
        sys.exit(2)

    if len(args) > 1:
        [search_strings.add(_.strip()) for _ in args[1:]]

    if not search_strings:
        eprint("You must specify at least one search string, either via the -s "
               "<search-strings-file> option or as positional commandline "
               "argument.")
        print_usage()
        sys.exit(2)

    # Setup the logger
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(filename)s:%('
                               'funcName)s:%(lineno)s - %('
                               'message)s',
                        datefmt='%d-%b-%y %H:%M:%S', level=log_level)
    eprint("Minimum logging level is {0}".format(LEVEL_STRINGS[log_level]))
    logger.info("Startup")

    scanner = Scanner(scan_root,
                      search_strings,
                      scan_archives=scan_archives,
                      ignore_case=ignore_case,
                      temp_dir=temp_dir,
                      exclusions=exclusions)
    scanner.scan()
    output_file = os.path.join(output_dir,
                               '-'.join(["scan",time.strftime('%Y%m%d%H%M')]))
    if excel_output:
        output_file += ".xlsx"
        output = ExcelOutput(scanner.HEADERS,
                             scanner.get_results(),
                             output_file=output_file,
                             branding_text=branding_text,
                             branding_logo=branding_logo)
    else:
        output_file += ".csv"
        output = CSVOutput(scanner.HEADERS,
                           scanner.get_results(),
                           output_file=output_file,
                           branding_text=branding_text)
    output.output()

if __name__ == '__main__':
    main(sys.argv[1:])


