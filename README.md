# string-path-search
Walk a directory tree, searching for any of a set of strings.

Installation:

Usage:
<pre>
    python3 scanner.py [OPTIONS] &lt;scan-root&gt; [&lt;search-term&gt; [...]]
    where:
        -a, --scan-archives = Unpack and scan within archives
            (Default: Skip arhive files. LIMITATIONS: Only zip and tar archives 
            can be scanned. Only bzip2 ('.bz2'), gzip ('.gz'), and lzma ('.xz') tar
            compression methods are supported.
        -B, --branding-text=<branding-text&gt; = A string of text containing
            company or other information to add above the column headers in
            scan reports (Default: no text).
        -b, --branding-logo=<branding-logo&gt; = (MS Excel only) An image
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
        -q, --quiet = Decrease logging verbosity (may repeat). -vvvv will suppress all logging.
        -t, --temp-dir=&lt;temp-dir&gt; = Location for unpacking archives
            (Default: &lt;output_dir&gt;/temp).
        -v, --verbose = Increase logging verbosity.
        -x, --exclusions-file=&lt;exclusion-file&gt; = A file containing (base) filenames to
            exclude from the search results, one per line (Default: Scan all files).
    &lt;scan-root&gt; = Directory to scan (No Default).
    &lt;search-term&gt; ... = One or more terms to search for in &lt;scan-root&gt;.
</pre>
Examples:

Perform a caseless search of the test/data directory for any occurrence of
'copyright', 'gpl', 'foo', 'bar', or 'baz' and output the results to a
file called 'scan-<timestamp>.csv' in the current working directory.
<pre>$ python3 scanner.py -i test/data copyright gpl foo bar baz</pre>

Same as example 1, except output to an Excel spreadsheet:
<pre>$ python3 scanner.py -i -e test/data copyright gpl foo bar baz</pre>


Disclaimer regarding the test data:
 
The files in the test/data folder were randomly downloaded from publicly 
available Open Source projects. Use of these materials as search engine test
 data may or may not be in violation of the applicable licenses.

