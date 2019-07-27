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
import os
import re
import shutil
import sys
import tarfile
import unicodedata
import zipfile

# Import 3rd party modules.
import xlsxwriter

# Import project modules.
from .utils import calculate_md5, LOGGER, make_dir_safe, random_string

# Define constants.
DIR_REGEX = re.compile(r'[/]$')
JAR_REGEX = re.compile(r'\.jar$')
TAR_REGEX = re.compile(r'\.(?:tar|tar.gz|tgz|tar.bzip2|tar.bz2|tbz2)$')
ZIP_REGEX = re.compile(r'\.zip$')
ARCH_REGEX = re.compile(r'\.(?:cab|cpio|ear|jar|rpm|tar|tar.gz|tgz|tar.bzip2'
                        r'|tar.bz2|tbz2|war|zip)$')


# pylint: disable=R0902
# R0902 = too-many-instance-attributes
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
        if os.path.isdir(thing):
            yield from self._dir_walk(thing)
        elif self.scan_archives and (ZIP_REGEX.search(thing) or JAR_REGEX.search(thing)):
            yield from self._zip_walk(thing, parent)
        elif self.scan_archives and TAR_REGEX.search(thing):
            yield from self._tar_walk(thing, parent)
        elif ARCH_REGEX.search(thing):
            if self.scan_archives:
                LOGGER.warning("Skipping unsupported archive %s", thing)
        elif not os.path.isfile(thing):
            LOGGER.warning("Thing '%s' is neither a directory nor is it a file", thing)
            return
        else:
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
                elif os.path.basename(name).casefold() in self.exclusions:
                    continue
                elif ARCH_REGEX.search(name):
                    extract_dir = os.path.join(self.temp_dir, random_string())
                    make_dir_safe(extract_dir)
                    inner_archive = os.path.join(extract_dir, name)
                    try:
                        zip_archive.extract(name, extract_dir)
                        if ARCH_REGEX.search(name):
                            yield from self._walk(inner_archive, parent)
                    # pylint: disable=W0703
                    # W0703 = broad-except
                    except BaseException:
                        LOGGER.error("Caught an exception of type=%s "
                                     "while processing inner archive %s",
                                     sys.exc_info()[0], name)
                        continue
                    # pylint: enable=W0703
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
                    # pylint: disable=W0703
                    # W0703 = broad-except
                    except BaseException:
                        LOGGER.error("Caught an exception of type=%s: %s",
                                     sys.exc_info()[0], sys.exc_info()[1])
                    # pylint: enable=W0703

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
                if not entry.isreg():
                    continue
                elif os.path.basename(entry.name).casefold() in self.exclusions:
                    continue
                elif ARCH_REGEX.search(entry.name):
                    extract_dir = os.path.join(self.temp_dir, random_string())
                    make_dir_safe(extract_dir)
                    inner_archive = os.path.join(extract_dir, entry.name)
                    try:
                        tar_archive.extract(entry, extract_dir)
                        if ARCH_REGEX.search(inner_archive):
                            yield from self._walk(inner_archive, parent)
                    # pylint: disable=W0703
                    # W0703 = broad-except
                    except BaseException:
                        LOGGER.error("Caught an exception of type=%s "
                                     "while processing inner archive=%s",
                                     sys.exc_info()[0], entry.name)
                        continue
                    # pylint: enable=W0703
                    finally:
                        shutil.rmtree(extract_dir)

                    continue
                else:
                    try:
                        with tar_archive.extractfile(entry) as fid:
                            file_bytes = fid.read()
                            yield (os.path.basename(entry.name),
                                   '/'.join([self.scan_root, parent, os.path.dirname(entry.name)]),
                                   calculate_md5(file_bytes), file_bytes)
                    # pylint: disable=W0703
                    # W0703 = broad-except
                    except BaseException:
                        LOGGER.error("Caught an exception of type=%s while extracting file=%s",
                                     sys.exc_info()[0], entry.name)
                    # pylint: enable=W0703

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


# pylint: disable=R0903
# R0903 = too-few-public-methods
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

# pylint: enable=R0903
