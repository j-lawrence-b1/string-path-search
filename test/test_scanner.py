"""Seupt"""
import os
import string_path_search.scanner

project_root = r'C:\Users\LBarnett.FLEXERASOFTWARE\coding\string-path-search'
scan_root = os.path.join(project_root, r'test\data\small')
out_dir = os.path.join(project_root, r'temp')
branding_logo = os.path.join(project_root, r'resources\citrix_logo.png')
args = ['-a', '-e', '-v',
        ' '.join(('-o', out_dir)), scan_root, 'Copyright (c)']
string_path_search.scanner.main(args)


