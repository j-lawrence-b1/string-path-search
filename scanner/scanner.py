"""Scan a directory tree for a set of strings"""
import os
import re
import tarfile
import zipfile

class Scanner:
    """Class to scan a directory tree for a set of strings"""

    TAR_REGEX = re.compile(r'.(?:tar|tar.gz|tgz)$')
    ZIP_REGEX = re.compile(r'.zip$')

    def __init__(self, root_path, search_strings, exclusions):
        if not os.path.isdir(root_path):
            raise ValueError("root_path {0} is not a directory".format(
                root_path))
        if not search_strings:
            raise ValueError("No strings to search!")

        self.root_path = root_path
        self.search_strings = search_strings
        self.exclusions = exclusions if exclusions else []

    def _dir_walk(self, path):
        """ Generate file objects from a recursive root_path scan."""

        if not path:
            path = self.root_path

        for entry in os.scandir(path):
            if entry.is_dir(follow_symlinks=False):
                yield from self._dir_walk(entry.path)
            elif tarfile.is_tarfile(entry.path):
                yield from self._tar_walk(entry.path)
            elif zipfile.is_zipfile(entry.path):
                yield from self._zip_walk(entry.path)
            else:
                f = open(entry.path, 'rb')
                yield entry.path, f.read()

    def _zip_walk(self, zip_file):
        """
        Generate name, filebuf tuples from a recursive zip scan.

        Args:
            zip_file -- The .zip file to scan.
        """
        with zipfile.ZipFile(zip_file) as zip_archive:
            for info in zip_archive.infolist():
                name = info.filename
                if self.ZIP_REGEX.match(name):
                    yield from self._zip_walk(name)
                elif self.TAR_REGEX.match(name):
                    yield from self._tar_walk(name)
                else:
                    with zip_archive.open(name) as f:
                        yield name, f.read()

    def _tar_walk(self, tar_file):
        """
        Generate name, filebuf tuples from a recursive tar scan.

        Args:
            tar_file -- The name of the .tar (or compressed variant) file
            to scan.
        """
        tar_archive = tarfile.open(tar_file, 'r')
        for entry in tar_archive:
            if entry.isreg():
                f = tar_archive.extractfile(entry)
                yield entry.name, f.read()
            elif self.TAR_REGEX.match(entry.name):
                yield from self._tar_walk(entry.name)
            elif self.ZIP_REGEX.match(entry.name):
                yield from self._zip_walk(entry.name)

    def _scan_file(self, file):
        return

    def scan(self):
        """Scan root_path and print matches."""
        for name, buf in self._dir_walk(None):
            try:
                print("name={0}, size{1}".format(name, len(buf)))
            except:
                print("wunga-wunga")



if __name__ == '__main__':
    SEARCH_STRINGS = [
        'foo', 'bar', 'baz',
        'huey', 'looey', 'dooey',
        'donald', 'daisy', 'scrooge',
        ]
    SCANNER = Scanner(r'C:\Users\LBarnett.FLEXERASOFTWARE\scratch',
                      SEARCH_STRINGS, None)
    SCANNER.scan()
