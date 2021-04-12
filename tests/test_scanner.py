#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Scanner class unit tests."""

import csv
from hashlib import md5
import logging
import os
from pathlib import Path
import pytest
import shutil
import openpyxl

from .context import CSVOutput, ExcelOutput, Output, Scanner, make_dir_safe

DATA_DIR = "tests/data"
OUTPUT_DIR = "temp"
TEMP_DIR = "tests/temp"


def generate_scan_result(string, path, file):
    """Helper function to generate a Scanner result tuple."""
    with open(os.path.join(path, file), mode="rb") as ffh:
        return (string, md5(ffh.read()).hexdigest(), file, path)


class TestScanner:
    """Scanner class unit test class."""

    @staticmethod
    @pytest.fixture
    def config():
        return dict(
            branding_text=None,
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
            search_strings={"foo", "bar", "baz"},
            exclusions=set(),
        )

    @staticmethod
    def setUp(config):
        """Initialize the configs."""
        for dir in (config["temp_dir"], config["output_dir"]):
            Path(dir).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def tearDown(config):
        """Cleanup after each test."""
        for dir in (config["temp_dir"], config["output_dir"]):
            shutil.rmtree(dir)

    @staticmethod
    def contains_result(actual_results, desired_results, ignore_case=False):
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
        for result in actual_results:
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

        if hits == desired_hits:
            return True
        else:
            return False

    @staticmethod
    def test_instantiation(config):
        obj = Scanner(config)
        assert isinstance(obj, Scanner)

    @staticmethod
    def test_case_sensitive_scan_exact_match(config):
        file_to_scan = "uwaptexit.pas"
        string_to_find = "TVisWaptExit.SetCountDown"
        scan_dir = os.path.join(DATA_DIR, "small")
        expected = [generate_scan_result(string_to_find, scan_dir, file_to_scan)]
        config["scan_root"] = os.path.join(scan_dir, file_to_scan)
        config["search_strings"] = {string_to_find}
        obj = Scanner(config)
        obj.scan()
        actual = obj.get_results()
        assert expected == actual

    def test_case_sensitive_scan_fuzzy_match(self, config):
        file_to_scan = "uwaptexit.pas"
        string_to_find = "TVisWaptExit.SetCountDown".upper()
        scan_dir = os.path.join(DATA_DIR, "small")
        expected = []
        config["scan_root"] = os.path.join(scan_dir, file_to_scan)
        config["search_strings"] = {string_to_find}
        obj = Scanner(config)
        obj.scan()
        actual = obj.get_results()
        expected == actual

    def test_case_insensitive_scan_exact_match(self, config):
        file_to_scan = "uwaptexit.pas"
        string_to_find = "TVisWaptExit.SetCountDown"
        scan_dir = os.path.join(DATA_DIR, "small")
        expected = [generate_scan_result(string_to_find, scan_dir, file_to_scan)]
        config["scan_root"] = os.path.join(scan_dir, file_to_scan)
        config["search_strings"] = {string_to_find}
        config["ignore_case"] = True
        obj = Scanner(config)
        obj.scan()
        actual = obj.get_results()
        expected == actual

    def test_case_insensitive_scan_fuzzy_match(self, config):
        file_to_scan = "uwaptexit.pas"
        string_to_find = "TVisWaptExit.SetCountDown".upper()
        scan_dir = os.path.join(DATA_DIR, "small")
        expected = [generate_scan_result(string_to_find, scan_dir, file_to_scan)]
        config["scan_root"] = os.path.join(scan_dir, file_to_scan)
        config["search_strings"] = {string_to_find}
        config["ignore_case"] = True
        obj = Scanner(config)
        obj.scan()
        actual = obj.get_results()
        expected == actual

    def test_binary_file_scan(self, config):
        file_to_scan = "main.o"
        string_to_find = "(C) Aaron Newman"
        scan_dir = os.path.join(DATA_DIR, "small")
        expected = [generate_scan_result(string_to_find, scan_dir, file_to_scan)]
        config["scan_root"] = os.path.join(scan_dir, file_to_scan)
        config["search_strings"] = {string_to_find}
        obj = Scanner(config)
        obj.scan()
        actual = obj.get_results()
        assert expected == actual

    def test_dir_scan(self, config):
        files_to_scan = [
            "setup.ksh",
            "test_helper.tcl",
            "test_invoice.py",
            "time.c",
        ]
        scan_dir = os.path.join(DATA_DIR, "small/level1/level2/level3")
        string_to_find = "Copyright (c)"
        expected = [
            generate_scan_result(string_to_find, scan_dir, file)
            for file in files_to_scan
        ]
        config["scan_root"] = scan_dir
        config["search_strings"] = {string_to_find}
        config["ignore_case"] = True
        obj = Scanner(config)
        obj.scan()
        actual = obj.get_results()
        assert sorted(expected) == sorted(actual)

    def test_jar_scan(self, config):
        file_to_scan = "sakai-calendar-util-19.2.jar"
        string_to_find = "http://sakaiproject.org/"
        desired_results = {string_to_find: ["pom.xml", "MANIFEST.MF"]}
        config["scan_archives"] = True
        config["scan_root"] = os.path.join(DATA_DIR, "small", file_to_scan)
        config["search_strings"] = {string_to_find}
        obj = Scanner(config)
        obj.scan()
        assert self.contains_result(obj.get_results(), desired_results) is True

    # def test_jar_scan(self, config):
    #    file_to_scan = "sakai-calendar-util-19.2.jar"
    #    string_to_find = "http://sakaiproject.org/"
    #    scan_dir = os.path.join(DATA_DIR, "small")
    #    archive_path = os.path.join(
    #        scan_dir, file_to_scan, "sakai-calendar-util-19.2.jar/META-INF"
    #    )
    #    expected = [generate_scan_result(string_to_find, archive_path, "MANIFEST.MF")]
    #    config["scan_archives"] = True
    #    config["scan_root"] = os.path.join(scan_dir, file_to_scan)
    #    config["search_strings"] = {string_to_find}
    #    obj = Scanner(config)
    #    obj.scan()
    #    actual = obj.get_results()
    #    assert expected == actual

    def test_tgz_scan(self, config):
        file_to_scan = "zfs-1.7.0.tgz"
        string_to_find = "Copyright (c)"
        desired_results = {
            string_to_find: [
                "IDDiskInfoLogger.cpp",
                "IDDiskInfoLogger.hpp",
                "IDException.cpp",
                "IDFileUtils.mm",
                "IDDAHandlerIdle.hpp",
            ]
        }
        config["scan_archives"] = True
        config["scan_root"] = os.path.join(DATA_DIR, "small", file_to_scan)
        config["search_strings"] = {string_to_find}
        obj = Scanner(config)
        obj.scan()
        assert self.contains_result(obj.get_results(), desired_results) is True

    def test_tar_bzip2_scan(self, config):
        file_to_scan = "zfs-1.7.0.tar.bzip2"
        string_to_find = "Copyright (c)"
        desired_results = {
            string_to_find: [
                "IDDiskInfoLogger.cpp",
                "IDDiskInfoLogger.hpp",
                "IDException.cpp",
                "IDFileUtils.mm",
                "IDDAHandlerIdle.hpp",
            ]
        }
        config["scan_archives"] = True
        config["scan_root"] = os.path.join(DATA_DIR, "small", file_to_scan)
        config["search_strings"] = {string_to_find}
        obj = Scanner(config)
        obj.scan()
        assert self.contains_result(obj.get_results(), desired_results) is True

    def test_txz_scan(self, config):
        file_to_scan = "zfs-1.7.0.txz"
        string_to_find = "Copyright (c)"
        desired_results = {
            string_to_find: [
                "IDDiskInfoLogger.cpp",
                "IDDiskInfoLogger.hpp",
                "IDException.cpp",
                "IDFileUtils.mm",
                "IDDAHandlerIdle.hpp",
            ]
        }
        config["scan_archives"] = True
        config["scan_root"] = os.path.join(DATA_DIR, "small", file_to_scan)
        config["search_strings"] = {string_to_find}
        obj = Scanner(config)
        obj.scan()
        assert self.contains_result(obj.get_results(), desired_results) is True

    def test_zip_scan(self, config):
        file_to_scan = "zfs-1.7.0.zip"
        string_to_find = "Copyright (c)"
        desired_results = {
            string_to_find: [
                "IDDiskInfoLogger.cpp",
                "IDDiskInfoLogger.hpp",
                "IDException.cpp",
                "IDFileUtils.mm",
                "IDDAHandlerIdle.hpp",
            ]
        }
        config["scan_archives"] = True
        config["scan_root"] = os.path.join(DATA_DIR, "small", file_to_scan)
        config["search_strings"] = {string_to_find}
        obj = Scanner(config)
        obj.scan()
        assert self.contains_result(obj.get_results(), desired_results) is True

    def test_deep_hierarchy(self, config):
        dir_to_scan = "small/level1"
        string_to_find = "Copyright (c)"
        desired_results = {
            string_to_find: [
                "setup.ksh",
                "test_helper.tcl",
                "test_invoice.py",
                "time.c",
                "reason.ml",
                "rtems.ads",
                "screen_title.c",
                "scroll2.tk",
            ]
        }
        config["scan_root"] = os.path.join(DATA_DIR, dir_to_scan)
        config["search_strings"] = {string_to_find}
        config["ignore_case"] = True
        obj = Scanner(config)
        obj.scan()
        assert self.contains_result(obj.get_results(), desired_results) is True

    def test_exclusion_file(self, config):
        file_to_scan = "zipped-tar-jar.zip"
        string_to_find = "Copyright (c)"
        exclusion_file = Path(config["temp_dir"], "excl.txt")
        make_dir_safe(config["temp_dir"])
        with open(exclusion_file, encoding="utf-8", mode="w") as f_h:
            f_h.write("InFunction.java\nValue.java\n")
        config["exclusions_file"] = exclusion_file
        desired_results = {string_to_find: ["cci_mpf_test_conf_default.vh"]}
        config["scan_root"] = os.path.join(DATA_DIR, "small", file_to_scan)
        config["search_strings"] = {string_to_find}
        config["scan_archives"] = True
        obj = Scanner(config)
        obj.scan()
        assert self.contains_result(obj.get_results(), desired_results) is True

    def test_inner_archive_scan(self, config):
        file_to_scan = "zipped-tar-jar.zip"
        string_to_find = "Copyright (c)"
        desired_results = {
            string_to_find: [
                "InFunction.java",
                "Value.java",
                "cci_mpf_test_conf_default.vh",
            ]
        }
        config["scan_archives"] = True
        config["scan_root"] = os.path.join(DATA_DIR, "small", file_to_scan)
        config["search_strings"] = {string_to_find}
        obj = Scanner(config)
        obj.scan()
        assert self.contains_result(obj.get_results(), desired_results) is True

    @staticmethod
    def test_get_csv_output(config):
        config["excel_output"] = False
        obj = Scanner(config)
        out = Output.get_output(obj.HEADERS, obj.get_results(), config)
        assert isinstance(out, CSVOutput)

    @staticmethod
    def test_get_excel_output(config):
        config["excel_output"] = True
        obj = Scanner(config)
        out = Output.get_output(obj.HEADERS, obj.get_results(), config)
        assert isinstance(out, ExcelOutput)

    def test_csv_output(self, config):
        file_to_scan = "zipped-tar-jar.zip"
        string_to_find = "Copyright (c)"
        config["scan_archives"] = True
        config["scan_root"] = os.path.join(DATA_DIR, "small", file_to_scan)
        config["search_strings"] = {string_to_find}
        scanner = Scanner(config)
        scanner.scan()
        config["excel_output"] = False
        output = Output.get_output(scanner.HEADERS, scanner.get_results(), config)
        output.output()
        with open(
            output.output_file, newline="", encoding="utf-8", mode="r"
        ) as csv_file:
            csv_reader = csv.reader(csv_file, dialect="excel")
            count = 0
            for row in csv_reader:
                count += 1
        assert count - 1 == len(scanner.get_results())

    def test_excel_output(self, config):
        file_to_scan = "zipped-tar-jar.zip"
        string_to_find = "Copyright (c)"
        config["scan_archives"] = True
        config["scan_root"] = os.path.join(DATA_DIR, "small", file_to_scan)
        config["search_strings"] = {string_to_find}
        scanner = Scanner(config)
        scanner.scan()
        config["excel_output"] = True
        output = Output.get_output(scanner.HEADERS, scanner.get_results(), config)
        output.output()
        wb = openpyxl.load_workbook(output.output_file)
        sheet = wb.active
        assert sheet.max_row - 1 == len(scanner.get_results())
