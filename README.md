# string-path-search
 Walk a directory tree, searching for files containing any of a set of text strings.

**Note:** The different naming conventions for projects on GitHub vs packages in Python results 
in some unnecessary confusion: "string-path-search" (with hyphens) is the name of the project on
 GitHub. This project provides the "string_path_search" (with underscores) Python package. 
 Please bear with me.
 
## Why not just use ***find*** and ***grep***?
* Avoids long, hard-to-debug shell commands with lots of backticks and parentheses.
* Works on Windows without needing to install a unix work-alike like Cygwin.
* Searches for a bunch of different strings in one go.
* Searches within (possibly compressed) jar, tar, or zip archives.
* Outputs results in CSV or Excel format. 

## System requirements
* Tested on Windows 10, Linux, and Windows 10/cygwin. May also work on other platforms
 supported by Python.
* Python 3.4 or later (https://www.python.org/downloads/).
* A Python pip module appropriate to the installed Python version
 (https://pip.pypa.io/en/stable/installing/). It is *possible* to install Python packages, 
 including string_path_search, without pip, but it's a lot harder without it.
 
## A note about installing python and pip
Some Linux systems (also Cygwin on Windows) come with python 2
pre-installed. You have to install python 3 yourself. There are gotchas
involved:
1. The "python" and "pip" packages may be reserved for version 2. It may not be as easy as 
 "apt-get install python3" either. The latest package might be called "python3.7" or similar.
  Ditto with pip.
2.  Once installed, the python 3 binary may be called "python3", not
    "python". Ditto with pip.
  
## Installation from pypi:
<pre>
> python -m pip install --user string-path-search 
</pre>

## Installation from GitHub
You can also download string-path-search with your browser as a .zip or .tgz archive from 
https://github.com/j-lawrence-b1/string-path-search/releases/latest 
 into any convenient directory. Once unpacked, you can install string_path_search and its 
 dependencies using the included setup.py script (which uses pip internally!).
<pre>
> chdir &lt;my-downloads-dir&gt;\\string-path-search-0.3.2
> python setup.py build install --user 
</pre>
**Note:** Installing with the '--user' option will install the string_path_search Python package
under your login's HOME directory (C:/Users/<user-name>/.local/Scripts on 
Windows or /home/<user-name>/.local/bin on Linux). If you plan to run the
 provided string_path_search.exe directly, you should add this directory to you
 your shell's execution path.
## Usage
Although you can import and use this package in other Python scripts,
string_path_search is primarily intended to be invoked as a console app:
<pre>
    $ python -m string_path_search [OPTIONS] &lt;scan-root&gt; [&lt;search-term&gt; [...]]
</pre>
or, you can add run the standalone string_path_search.exe directly (see **Note,** above).
<pre>
    $ ~/.local/bin/string_path_search [OPTIONS] &lt;scan-root&gt; [&lt;search-term&gt; [...]]
</pre>
where:
<pre>
    -a, --scan-archives = Unpack and scan within archives
        (Default: Skip arhive files. Only jar, tar, and zip archives will be
            unpacked. Tar bzip2, gzip, and xz compression is supported.
    -B, --branding-text=&lt;branding-text&gt; = A string of text containing
        company or other information to add above the column headers in
        scan reports (Default: no text).
    -b, --branding-logo=&lt;branding-logo&gt; = (MS Excel only) An image
        file containing a corporate logo or other graphic to add above the
        column headers in scan reports (Default: no logo).
    -h, --help = Print usage information and exit.
    -e, --excel-output = Generate Microsoft Excel 2007 (.xlsx) output
        (Default: Generate comma-separated-value (CSV) text output)
    -i  --ingore-case = Ignore UPPER/lowercase differences when matching strings
        (Default: case differences are significant).
    -o, --output-dir=&lt;output-dir&gt; = Location for output (Default:
        &lt;current working directory&gt;).
    -s, --search-strings-file=&lt;search-strings&gt; = A file containing strings to
        search for, one per line (Default: Get search strings from the command line).
    -q, --quiet = Decrease logging verbosity (may repeat). -qqqq will suppress all logging.
    -t, --temp-dir=&lt;temp-dir&gt; = Location for unpacking archives
        (Default: &lt;output_dir&gt;/temp).
    -v, --verbose = Increase logging verbosity.
    -x, --exclusions-file=&lt;exclusion-file&gt; = A file containing (base) filenames to
        exclude from the search results, one per line (Default: Include all results).
&lt;scan-root&gt; = Directory to scan.
&lt;search-term&gt; ... = One or more terms to search for in &lt;scan-root&gt;.
</pre>
## Examples

Perform a caseless search of the test/data directory for any occurrence of
'copyright', 'gpl', 'foo', 'bar', or 'baz' and output the results to a
file called 'scan-&lt;timestamp>.csv' in the current working directory.
<pre>$ python -m string_path_search -i tests/data "copyright (c)" gpl foo bar baz</pre>
 
Same as example 1, except output to an Excel spreadsheet:
<pre>$ python -m string_path_search -i -e tests/data "copyright (c)" gpl foo bar baz</pre>

**Gotcha:** Use double-quotes for multi-word search strings. For some reason,
single quotes screw up the command line parser.
## License
string_path_search is distributed under the
[MIT License](http://github.com/j-lawrence-b1/string-path-search/blob/master/LICENSE).

## Disclaimer regarding the test data:

The files in the test/data folder were randomly downloaded from publicly 
available Open Source projects. Distributing these materials with string_path_search as 
test data may or may not be in violation of the applicable licenses.
