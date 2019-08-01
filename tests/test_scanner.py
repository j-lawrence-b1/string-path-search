#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Scanner class unit tests."""

from pathlib import Path
import unittest

from .context import string_path_search

class ScannerTestSuite(unittest.TestCase):
    """Scanner class unit test class."""

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
        'exclusions': set(),
    }

    def setUp(self) -> None:
        obj = string_path_search.Scanner(self.config)
        self.assertIsInstance(obj, "string_path_search.Scanner")






