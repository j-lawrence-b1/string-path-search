#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Scanner class unit tests."""

from pathlib import Path
import logging
import os
import shutil
import unittest

from .context import Scanner

class ScannerTestSuite(unittest.TestCase):
    """Scanner class unit test class."""

    DATA_DIR = "tests/data"
    OUTPUT_DIR = "temp"
    TEMP_DIR = "tests/temp"
    # Set program defaults.
    config = dict(branding_text=None,
                  branding_logo=None,
                  excel_output=True,
                  ignore_case=True,
                  log_level=logging.INFO,
                  output_dir=OUTPUT_DIR,
                  search_strings_file=None,
                  temp_dir=TEMP_DIR,
                  scan_archives=False,
                  scan_root=DATA_DIR,
                  exclusions_file=None,
                  search_strings={'foo', 'bar', 'baz'},
                  exclusions=set())

    def tearDown(self) -> None:
        """Cleanup after each test."""
        if os.path.exists(self.config['temp_dir']):
            shutil.rmtree(self.config['temp_dir'])
        for f in os.listdir(self.config['output_dir']):
            os.remove(os.path.join(self.config['output_dir'], f))

    def test_instantiation(self):
        obj = Scanner(self.config)
        self.assertIsInstance(obj, Scanner)

    def test_text_scan(self):
        self.assertTrue(False)

    def test_binary_scan(self):
        self.assertTrue(False)

    def test_jar_scan(self):
        self.assertTrue(False)

    def test_tar_scan(self):
        self.assertTrue(False)

    def test_zip_scan(self):
        self.assertTrue(False)

    def test_case_insensitive_scan(self):
        self.assertTrue(False)

    def test_exclusion_file(self):
        self.assertTrue(False)

    def test_deep_hierarchy(self):
        self.assertTrue(False)

    def test_inner_archive_scan(self):
        self.assertTrue(False)
