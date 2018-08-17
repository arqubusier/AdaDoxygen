# AdaDoxygen
Ada to c++ converter for use with doxygen

## Usage

```
usage: main.py [-h] [-p PROJECT_FILE] [-t TEMPORARY_DIR] [-r]
               [-l LOGGING_LEVEL] [--prefix-functions PREFIX_FUNCTIONS]
               [--prefix-packages PREFIX_PACKAGES]
               [--prefix-repclause PREFIX_REPCLAUSE] [--hide-repclause]
               [--post-process] [--gnat-options [GNAT_OPTIONS]]
               [--gnat-cargs [GNAT_CARGS]] [--path-gnat2xml [PATH_GNAT2XML]]
               [--path-doxygen [PATH_DOXYGEN]]
               doxygen_file

positional arguments:
  doxygen_file          Your doxyfile, generate one by running 'doxygen -g'

optional arguments:
  -h, --help            show this help message and exit
  -p PROJECT_FILE, --project-file PROJECT_FILE
                        Ada project file, mandatory if source files is in
                        different directories
  -t TEMPORARY_DIR, --temporary-dir TEMPORARY_DIR
                        Path to tmp dir, dirs will be created if not exists,
                        default='_tmp'
  -r, --remove-temporary-dir
                        Remove temporary dir when AdaDoxygen is done
  -l LOGGING_LEVEL, --logging-level LOGGING_LEVEL
                        debug/info/warning/error/critical, default='warning'
  --prefix-functions PREFIX_FUNCTIONS
                        Prefix for nested members except packages,
                        default='__'
  --prefix-packages PREFIX_PACKAGES
                        Prefix for packages, default=''
  --prefix-repclause PREFIX_REPCLAUSE
                        Prefix for representation clauses, default='_rep_'
  --hide-repclause      Remove 'for x use y'-clause as code block comment on
                        original type
  --post-process        Post process HTML-files
  --gnat-options [GNAT_OPTIONS]
                        gnat2xml options. If more then one, wrap with quotes
  --gnat-cargs [GNAT_CARGS]
                        gnat2xml cargs. If more then one, wrap with quotes
  --path-gnat2xml [PATH_GNAT2XML]
                        Path to gnat2xml, default='gnat2xml'
  --path-doxygen [PATH_DOXYGEN]
                        Path to doxygen, default='doxygen'
```

For a working example, run
> ` python src/main.py examples/doxyfile.ini -r -l info`

## Dependencies
* python (tested with 2.7)
* doxygen (tested with 1.8.14)
* gnat2xml (tested with 20170515)

## Generate documentation for AdaDoxygen itself
To generate documentation for AdaDoxygen, open a terminal in /path/to/AdaDoxygen/doc and run

> `doxygen adadoxygen_doc_config.txt`

Then open /path/to/AdaDoxygen/doc/html in your browser

## Doxyfile options
Note that the following doxyfile options has 
special meaning for AdaDoxygen:

* INPUT - if same filename exists in different input directories, the first one will be used
* FILE_PATTERNS - The following must be added in order for AdaDoxygen to work: *.ads *.adb
* EXTENSION_MAPPING - The following must be added in order for AdaDoxygen to work: adb=C++ ads=C++
* STRIP_FROM_PATH - Only absolute path is supported.
* HIDE_UNDOC_CLASSES - If set to NO, undocumented packages will be extracted as well.
* LAYOUT_FILE - Is not used. It is overwritten by doxygenlayout.xml in the src-directory

Options that is not listed above is used as usual by Doxygen (or modified with same behaviour by AdaDoxygen)

## How it works
AdaDoxygen replaces Ada-comments to pragmas.
> `--! Example`
becomes
> `pragma Comment ("Example");`

It saves the results along with other files (not necessarily ada-files) to a temporary directory.

All ada-files in the temporary directory will then be input to gnat2xml if no project file is specified.

AdaDoxygen then extracts information from the XML-files and converts the information to Ada-code (or C++).

AdaDoxygen will then run doxygen for you along with the doxyfile you provided.

## Notes

### Arguments to gnat2xml problem
If you got problems with passing arguments to gnat2xml with `--gnat-options` or `--gnat-args`, 
try to add a space inside the argument string value like

> ```main.py doxyfile.txt --gnat-options ' -q --compact'```

This is a known and debated bug in argparse for python 2.7.

### Controlling output
* To hide output from gnat2xml, pass the ` -q` flag with `--gnat-options`
* To hide output from doxygen, set QUIET to YES in your doxyfile
* To control output from adadoxygen, 
pass the `-l` or `--logging-level` along with pythons logging module level. 
`debug` is verbose and `critical` is quiet.

## Development
### How to list unsupported elements
* Set gnat2xml and doxygen to quiet
* AdaDoxygen will log `Not parsed: <element-tag-name>` on info level
* To print more information about the unparsed element, change the last elif-statement in PPFile.parseRecursive

### How to add support for a unparsed element
* Add a extract handler for your xml node tag in PPFile.parseRecursive that extracts data from xml to a python dict
* Add a convert handler in PPFile.writeRecursive that converts your python dict to plain text with C++ syntax
















