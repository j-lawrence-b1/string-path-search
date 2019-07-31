#string-path-search
Walk a directory tree, searching for any of a set of strings. Optionally, explore inside 
inside .jar, .tar, or .zip archives.

##Why not just use ***find*** and ***grep***?
* What is this 'grep' you speak of?
* Works on Windows without needing to install a unix work-alike like Cygwin.
* Searches for a bunch of different strings in one go.
* Searches within jar, tar, or zip archives.
* Outputs results in CSV or Excel format. 

##System requirements
* Tested on Windows 10 and Linux. May work on other platforms supported by Python.
* Python 3.4 or later (https://www.python.org/downloads/).
* Pip module appropriate to the installed Python version.
  (https://pip.pypa.io/en/stable/installing/).

##A note about installing python and pip
Some Linux systems (also Cygwin on Windows) come with python 2 pre-installed. You have to install 
python 3 yourself. There
 are gotchas involved:
 1. The "python" and "pip" packages may be reserved for version 2. It may not be as easy as 
 "apt-get install python3" either. The latest package might be called "python3.7" or similar.
  Ditto with pip 3.
 2. Once installed, the python 3 binary may be called "python3", not python. Ditto with pip.
  
##Installation from pypi:
<pre>
$ python -m pip install string_path_search --user 
</pre>

##Installation from GitHub
<pre>
$ git clone git@github.com:j-lawrence-b1/string-path-search.git
$ python string_path_search/setup.py install --user 
</pre>

##Usage
<pre>
    $ python -m string_path_search [OPTIONS] &lt;scan-root&gt; [&lt;search-term&gt; [...]]
    where:
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
##Examples

Perform a caseless search of the test/data directory for any occurrence of
'copyright', 'gpl', 'foo', 'bar', or 'baz' and output the results to a
file called 'scan-&lt;timestamp>.csv' in the current working directory.
<pre>$ python -m string_path_search -i test/data copyright gpl foo bar baz</pre>

Same as example 1, except output to an Excel spreadsheet:
<pre>$ python -m string_path_search -i -e test/data copyright gpl foo bar baz</pre>

##License
string_path_search is distributed under the
[MIT License](http://github.com/j-lawrence-b1/string-path-search/blob/master/LICENSE).

##Disclaimer regarding the test data:

The files in the test/data folder were randomly downloaded from publicly 
available Open Source projects. Distributing these materials with string_path_search as 
test data may or may not be in violation of the applicable licenses.



[MIT License]: https://github.com/j-lawrence-b1/string-path-search/blob/master/LICENSE