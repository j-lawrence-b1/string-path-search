#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Scanner class unit tests."""

from pathlib import Path
import logging
import os
import shutil
import unittest

from .context import Scanner, make_dir_safe

class ScannerTestSuite(unittest.TestCase):
    """Scanner class unit test class."""

    DATA_DIR = "tests/data"
    OUTPUT_DIR = "temp"
    TEMP_DIR = "tests/temp"
    # Set program defaults.
    config = dict(branding_text=None,
                  branding_logo=None,
                  excel_output=False,
                  ignore_case=False,
                  log_level=logging.INFO,
                  output_dir=OUTPUT_DIR,
                  search_strings_file=None,
                  temp_dir=TEMP_DIR,
                  scan_archives=False,
                  scan_root=DATA_DIR,
                  exclusions_file=None,
                  search_strings={'foo', 'bar', 'baz'},
                  exclusions=set())

    def tearDown(self):
        """Cleanup after each test."""
        if os.path.exists(self.config['temp_dir']):
            shutil.rmtree(self.config['temp_dir'])
        for f in os.listdir(self.config['output_dir']):
            os.remove(os.path.join(self.config['output_dir'], f))

    def contains_result(self, results, desired_results, ignore_case=False):
        """
        Search for a particular match in a set of Scanner results

        Args:
            matched_results: A List of tuples as returned by Scanner.get_results()
            desired_results: A dictionary mapping search strings to a list of file names.
            file_name: A (base) filename that should contain search_string.

        Return:
            True if the result is found; False, otherwise.
        """
        hits = 0
        desired_hits = 0
        for values in desired_results.values():
            desired_hits += len(values)
        for result in results:
            matched_string = result[0]
            matched_file = result[2]
            if ignore_case:
                for desired_result in desired_results:
                    if matched_string.casefold() == desired_result.casefold():
                        if matched_file in desired_results[desired_result]:
                            hits += 1
            else:
                if matched_string in desired_results:
                    if matched_file in desired_results[matched_string]:
                        hits += 1

        #print("matched {0} of {1} results".format(hits, desired_hits))

        if hits == desired_hits:
            return True
        else:
            return False

    def test_instantiation(self):
        obj = Scanner(self.config)
        self.assertIsInstance(obj, Scanner)

    def test_text_file_scan(self):
        file_to_scan = 'uwaptexit.pas'
        string_to_find = 'TVisWaptExit.SetCountDown'
        self.config['scan_root'] = os.path.join(self.DATA_DIR, 'small', file_to_scan)
        self.config['search_strings'] = {string_to_find}
        obj = Scanner(self.config)
        obj.scan()
        self.assertTrue(self.contains_result(obj.get_results(), {string_to_find: [file_to_scan]}))

    def test_case_insensitive_scan(self):
        file_to_scan = 'uwaptexit.pas'
        string_to_find = 'TVisWaptExit.SetCountDown'
        self.config['scan_root'] = os.path.join(self.DATA_DIR, 'small', file_to_scan)
        self.config['search_strings'] = {string_to_find.upper()}
        obj = Scanner(self.config)
        obj.scan()
        self.assertFalse(self.contains_result(obj.get_results(), {string_to_find.upper():[
            file_to_scan]}))
        self.config['ignore_case'] = True
        obj2 = Scanner(self.config)
        obj2.scan()
        self.assertTrue(self.contains_result(obj2.get_results(), {string_to_find:[
            file_to_scan]}, True))

    def test_binary_file_scan(self):
        file_to_scan = 'main.o'
        string_to_find = '(C) Aaron Newman'
        self.config['scan_root'] = os.path.join(self.DATA_DIR, 'small', file_to_scan)
        self.config['search_strings'] = {string_to_find}
        obj = Scanner(self.config)
        obj.scan()
        self.assertTrue(self.contains_result(obj.get_results(), {string_to_find: [file_to_scan]}))

    def test_dir_scan(self):
        dir_to_scan = 'small/level1/level2/level3'
        string_to_find = 'Copyright (c)'
        desired_results = {string_to_find:['setup.ksh', 'test_helper.tcl', 'test_invoice.py',
                           'time.c']}
        self.config['scan_root'] = os.path.join(self.DATA_DIR, dir_to_scan)
        self.config['search_strings'] = {string_to_find}
        obj = Scanner(self.config)
        obj.scan()
        self.assertTrue(self.contains_result(obj.get_results(), desired_results))

    def test_jar_scan(self):
        file_to_scan = 'sakai-calendar-util-19.2.jar'
        string_to_find = 'http://sakaiproject.org/'
        desired_results = {string_to_find:['pom.xml', 'MANIFEST.MF']}
        self.config['scan_archives'] = True
        self.config['scan_root'] = os.path.join(self.DATA_DIR, 'small', file_to_scan)
        self.config['search_strings'] = {string_to_find}
        obj = Scanner(self.config)
        obj.scan()
        self.assertTrue(self.contains_result(obj.get_results(), desired_results))

    def test_tgz_scan(self):
        file_to_scan = 'zfs-1.7.0.tgz'
        string_to_find = 'Copyright (c)'
        desired_results = {string_to_find:['IDDiskInfoLogger.cpp', 'IDDiskInfoLogger.hpp',
                                           'IDException.cpp', 'IDFileUtils.mm',
                                           'IDDAHandlerIdle.hpp']}
        self.config['scan_archives'] = True
        self.config['scan_root'] = os.path.join(self.DATA_DIR, 'small', file_to_scan)
        self.config['search_strings'] = {string_to_find}
        obj = Scanner(self.config)
        obj.scan()
        self.assertTrue(self.contains_result(obj.get_results(), desired_results))

    def test_tar_bzip2_scan(self):
        file_to_scan = 'zfs-1.7.0.tar.bzip2'
        string_to_find = 'Copyright (c)'
        desired_results = {string_to_find:['IDDiskInfoLogger.cpp', 'IDDiskInfoLogger.hpp',
                                           'IDException.cpp', 'IDFileUtils.mm',
                                           'IDDAHandlerIdle.hpp']}
        self.config['scan_archives'] = True
        self.config['scan_root'] = os.path.join(self.DATA_DIR, 'small', file_to_scan)
        self.config['search_strings'] = {string_to_find}
        obj = Scanner(self.config)
        obj.scan()
        self.assertTrue(self.contains_result(obj.get_results(), desired_results))

    def test_txz_scan(self):
        file_to_scan = 'zfs-1.7.0.txz'
        string_to_find = 'Copyright (c)'
        desired_results = {string_to_find:['IDDiskInfoLogger.cpp', 'IDDiskInfoLogger.hpp',
                                           'IDException.cpp', 'IDFileUtils.mm',
                                           'IDDAHandlerIdle.hpp']}
        self.config['scan_archives'] = True
        self.config['scan_root'] = os.path.join(self.DATA_DIR, 'small', file_to_scan)
        self.config['search_strings'] = {string_to_find}
        obj = Scanner(self.config)
        obj.scan()
        self.assertTrue(self.contains_result(obj.get_results(), desired_results))

    def test_zip_scan(self):
        file_to_scan = 'zfs-1.7.0.zip'
        string_to_find = 'Copyright (c)'
        desired_results = {string_to_find:['IDDiskInfoLogger.cpp', 'IDDiskInfoLogger.hpp',
                                           'IDException.cpp', 'IDFileUtils.mm',
                                           'IDDAHandlerIdle.hpp']}
        self.config['scan_archives'] = True
        self.config['scan_root'] = os.path.join(self.DATA_DIR, 'small', file_to_scan)
        self.config['search_strings'] = {string_to_find}
        obj = Scanner(self.config)
        obj.scan()
        self.assertTrue(self.contains_result(obj.get_results(), desired_results))

    def test_deep_hierarchy(self):
        dir_to_scan = 'small/level1'
        string_to_find = 'Copyright (c)'
        desired_results = {string_to_find:['setup.ksh', 'test_helper.tcl', 'test_invoice.py',
                                           'time.c', 'reason.ml', 'rtems.ads', 'screen_title.c',
                                           'scroll2.tk']}
        self.config['scan_root'] = os.path.join(self.DATA_DIR, dir_to_scan)
        self.config['search_strings'] = {string_to_find}
        obj = Scanner(self.config)
        obj.scan()
        self.assertTrue(self.contains_result(obj.get_results(), desired_results))

    def test_exclusion_file(self):
        file_to_scan = 'zipped-tar-jar.zip'
        string_to_find = 'Copyright (c)'
        exclusion_file = Path(self.TEMP_DIR, 'excl.txt')
        make_dir_safe(self.TEMP_DIR)
        with open(exclusion_file, encoding='utf-8', mode='w') as f_h:
            f_h.write('InFunction.java\nValue.java\n')
        self.config['exclusions_file'] = exclusion_file
        desired_results = {string_to_find:['cci_mpf_test_conf_default.vh']}
        self.config['scan_root'] = os.path.join(self.DATA_DIR, 'small', file_to_scan)
        self.config['search_strings'] = {string_to_find}
        self.config['scan_archives'] = True
        obj = Scanner(self.config)
        obj.scan()
        self.assertTrue(self.contains_result(obj.get_results(), desired_results))

    def test_inner_archive_scan(self):
        file_to_scan = 'zipped-tar-jar.zip'
        string_to_find = 'Copyright (c)'
        desired_results = {string_to_find:['InFunction.java', 'Value.java',
                                           'cci_mpf_test_conf_default.vh']}
        self.config['scan_archives'] = True
        self.config['scan_root'] = os.path.join(self.DATA_DIR, 'small', file_to_scan)
        self.config['search_strings'] = {string_to_find}
        obj = Scanner(self.config)
        obj.scan()
        self.assertTrue(self.contains_result(obj.get_results(), desired_results))
