"""Seupt"""
from pathlib import Path
from string_path_search import scanner


project_root = Path(Path.home() / 'coding' / 'string-path-search')
scan_root = Path(project_root / 'test' / 'data' / 'small')
out_dir = Path(project_root / 'temp')
args = ['-a', '-e', '-v', ' '.join(('-o', str(out_dir))), str(scan_root), 'Copyright (c)']
scanner.main(args)


