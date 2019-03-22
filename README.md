# string-path-search
Walk a directory tree, searching for any of a set of strings.

Installation:

Usage:
<pre>
    python3 scanner.py [OPTIONS] <scan-root> [<search-term> [...]]
    where:
        -a, --unpack-archives = Unpack and scan within archives
            (Default: Arhives will NOT be uncompressed and will be scanned
            as a single file). LIMITATIONS: Only zip and tar archives will be
            unpacked. Only gzip and bzip2 tar compression methods are supported.
        -B, --branding-text=<branding-text> = A string of text containing
            company or other information to add above the column headers in
            scan reports (Default: no text).
        -b, --branding-logo=<branding-logo> = (MS Excel only) An image
            file containing a corporate logo or other graphic to add above the
            column headers in scan reports (Default: no logo).
        -h, --help = Print usage information and exit.
        -e, --excel-output = Generate Microsoft Excel 2007 (.xlsx) output
            (Default: Generate comma-separated-value (CSV) text output)
        -i  --ingore-case = Ignore UPPER/lowercase differences when matching strings
            (Default: case differences are significant).
        -o, --output-dir=<output-dir> = Location for output (Default:
            <current working directory>).
        -s, --search-strings-file=<search-strings> = A file containing 
        strings to
        search for, one per line (No Default).
        -q, --quiet = Decrease logging verbosity (may repeat). -vvvv will suppress all logging.
        -t, --temp-dir=<temp-dir> = Location for unpacking archives
            (Default: <output_dir>/temp).
        -v, --verbose = Increase logging verbosity.
        -x, --exclusions-file=<exclusion-file> = A file containing filenames to
            exclude from the search results.
    <scan-root> = Directory to scan (No Default).
    <search-term> ... = One or more terms to search for in <scan-root>.
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

