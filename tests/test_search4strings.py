#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Setup the scanner."""

from pathlib import Path
import importlib.util

project_root = Path("..")
bin_dir = Path(project_root / 'bin')
scan_root = Path(project_root / 'tests' / 'data' / 'small')
out_dir = Path(project_root / 'temp')
branding_logo = Path(Path.home() / 'Dropbox/Personal/Robert/Citrix.png')
if not branding_logo.exists():
    print("ERROR: branding_text={0} doesn't exist".format(str(branding_logo)))
branding_text = "this is the branding text. It is really, really important"

spec = importlib.util.spec_from_file_location("search4strings", Path(bin_dir / "search4strings.py"))
search4strings = importlib.util.module_from_spec(spec)
spec.loader.exec_module(search4strings)
args = ['-a', '-e', '-i', '-v', ' '.join(('-B', branding_text)),
        ' '.join(('-o', str(out_dir))), str(scan_root), 'Copyright (c)']
search4strings.main(args)
