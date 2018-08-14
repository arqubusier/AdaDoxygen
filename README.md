# AdaDoxygen
Ada to c++ converter for use with doxygen

### Usage

To run AdaDoxygen, you have to provide your 
own doxyfile as a positional argument:
> `python main.py myDoxyfile`

To see all options, run
> `python main.py --help`

### Dependencies
* python (tested with 2.7)
* doxygen (tested with 1.8.14)
* gnat2xml (tested with 20170515)

### Documentation
To doxygenerate documentation for AdaDoxygen, 
open a terminal in /path/to/AdaDoxygen/doc and run
> doxygen adadoxygen_doc_config.txt
Then open /path/to/AdaDoxygen/doc/html in your browser

### Doxyfile options
Note that the following doxyfile options has 
special meaning for AdaDoxygen:

* INPUT - if same filename exists in different input directories, the first one will be used
* RECURSIVE - is modified with same behavior 
* FILE_PATTERNS - The following must be added: *.ads *.adb
* EXTENSION_MAPPING - adb=C++ ads=C++
* STRIP_FROM_PATH - is modified so that the tmp-directory is prepepended. Only absolute path is supported.
* EXTRACT_ALL - If set to NO, no system comment will be appended
* EXTRACT_PRIVATE - Only print c++ code that is public if set to NO
* HIDE_UNDOC_CLASSES - If set to NO, undocumented packages will be extracted as well.
* LAYOUT_FILE - Is not used. Overwritten by DoxygenLayout.xml in the src-directory

Options that is not listed above is used as usual by Doxygen

### How it works
AdaDoxygen replaces Ada-comments to pragmas.
> `--! Example`
becomes
> `pragma Comment ("Example");`

It saves the results 
along with other files (not necessarily ada-files)
to a temporary directory.

All ada-files in the temporary directory will then be
input to gnat2xml if no project file is specified.

AdaDoxygen then extracts information from the XML-files
and converts the information to C++.

AdaDoxygen will then run doxygen for you 
along with the doxyfile you provided.


