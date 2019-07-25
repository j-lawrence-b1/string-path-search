#!/usr/bin/env python

"""Setup the scanner."""

from pathlib import Path
import importlib.util
spec = importlib.util.spec_from_file_location("bin.search4strings", "../bin/search4strings.py")
search4strings = importlib.util.module_from_spec(spec)
spec.loader.exec_module(search4strings)
project_root = Path("..")
scan_root = Path(project_root / 'tests' / 'data' / 'small')
out_dir = Path(project_root / 'temp')
args = ['-a', '-e', '-i', '-v', ' '.join(('-o', str(out_dir))), str(scan_root), 'Copyright (c)']
search4strings.main(args)


