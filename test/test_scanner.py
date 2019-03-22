"""Seupt"""
import os
import string_path_search.scanner

project_root = r'C:\Users\LBarnett.FLEXERASOFTWARE\PycharmProjects\string' \
               r'-path-search'
scan_root = os.path.join(project_root, r'test\data\small')
out_dir = os.path.join(project_root, r'temp')
branding_logo = os.path.join(project_root, r'resources\citrix_logo.png')
args = [' '.join(('-b', branding_logo)), '-a', '-e', '-v',
        ' '.join(('-o', out_dir)), scan_root, 'Copyright (c)']
string_path_search.scanner.main(args)


