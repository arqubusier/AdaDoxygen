# AdaDoxygen
Ada to c++ converter for use with doxygen

### Usage

```
usage: main.py [-h] [-p PROJECT_FILE] [-t TEMPORARY_DIR] [-q] [-v]
               [--prefix-functions PREFIX_FUNCTIONS]
               [--prefix-packages PREFIX_PACKAGES]
               [--prefix-repclause PREFIX_REPCLAUSE] [--hide-repclause]
               [--post-process] [--gnat-options [GNAT_OPTIONS]]
               [--gnat-cargs [GNAT_CARGS]]
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
                        default='C:\Users\Olle\Desktop\AdaDoxygen\_tmp'
  -q, --quiet           Hide AdaDoxygen output
  -v, --verbose         List generated files by AdaDoxygen
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
```

### Dependencies
* python (tested with 2.7)
* doxygen (tested with 1.8.14)
* gnat2xml (tested with 20170515)

### Documentation
To doxygenerate documentation for AdaDoxygen, open a terminal in /path/to/AdaDoxygen/doc and run

> `doxygen adadoxygen_doc_config.txt`

Then open /path/to/AdaDoxygen/doc/html in your browser

### Doxyfile options
Note that the following doxyfile options has 
special meaning for AdaDoxygen:

* INPUT - if same filename exists in different input directories, the first one will be used
* FILE_PATTERNS - The following must be added in order for AdaDoxygen to work: *.ads *.adb
* EXTENSION_MAPPING - The following must be added in order for AdaDoxygen to work: adb=C++ ads=C++
* STRIP_FROM_PATH - Only absolute path is supported.
* HIDE_UNDOC_CLASSES - If set to NO, undocumented packages will be extracted as well.
* LAYOUT_FILE - Is not used. It is overwritten by DoxygenLayout.xml in the src-directory

Options that is not listed above is used as usual by Doxygen (or modified with same behaviour by AdaDoxygen)

### How it works
AdaDoxygen replaces Ada-comments to pragmas.
> `--! Example`
becomes
> `pragma Comment ("Example");`

It saves the results along with other files (not necessarily ada-files) to a temporary directory.

All ada-files in the temporary directory will then be input to gnat2xml if no project file is specified.

AdaDoxygen then extracts information from the XML-files and converts the information to Ada-code (or C++).

AdaDoxygen will then run doxygen for you along with the doxyfile you provided.


