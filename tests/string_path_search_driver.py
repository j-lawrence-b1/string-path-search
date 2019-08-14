#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Setup the scanner."""

import os
from pathlib import Path
import importlib.util

import string_path_search

project_root = Path("..")
module_dir = Path(project_root / 'string_path_search')
scan_root = Path(project_root / 'tests' / 'data' / 'small' / 'level1')
out_dir = Path(project_root / 'temp')
temp_dir = Path(project_root / 'tests' / 'temp')
string_path_search.utils.make_dir_safe(temp_dir)
#exclusion_file = str(temp_dir) + r'\excl.txt'
#with open(exclusion_file, encoding='utf-8', mode='w') as f_h:
#    f_h.write('InFunction.java\nValue.java\n')

branding_text = "this is the branding text. It is really, really important"

spec = importlib.util.spec_from_file_location("sps_main", Path(module_dir / "__main__.py"))
sps_main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sps_main)
#args = ['-a', '-e', '-v', ' '.join(('-B', str(branding_text))), ' '.join(('-x', exclusion_file)),
args = ['-a', '-v', ' '.join(('-o', str(out_dir))), str(scan_root), 'Copyright (c)']
for arg in args:
    os.sys.argv.append(arg)
sps_main.main()
