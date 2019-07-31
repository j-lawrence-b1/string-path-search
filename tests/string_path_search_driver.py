#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Setup the scanner."""

from pathlib import Path
import importlib.util

import string_path_search

project_root = Path("..")
module_dir = Path(project_root / 'string_path_search')
scan_root = Path(project_root / 'tests' / 'data' / 'small')
out_dir = Path(project_root / 'temp')
branding_logo = Path(Path.home() / 'Dropbox/Personal/Robert/Citrix.png')
if not branding_logo.exists():
    print("ERROR: branding_text={0} doesn't exist".format(str(branding_logo)))
branding_text = "this is the branding text. It is really, really important"

spec = importlib.util.spec_from_file_location("sps_main", Path(module_dir / "__main__.py"))
sps_main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sps_main)
args = ['-a', '-e', '-i', '-v', ' '.join(('-b', str(branding_logo))),
        ' '.join(('-o', str(out_dir))), str(scan_root), 'Copyright (c)']
sps_main.main(args)
