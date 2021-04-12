#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Make nose2 happy"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from string_path_search.scanner import Scanner, CSVOutput, ExcelOutput, Output
from string_path_search.utils import (
    random_string,
    calculate_file_md5,
    calculate_md5,
    make_dir_safe,
    eprint,
    get_logger,
)
from string_path_search.__main__ import parse_args, print_usage, main
