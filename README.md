# AdaDoxygen
Ada to c++ converter for use with doxygen

### Usage
**python /path/to/adadoxygen/main.py** [-h] [-p PROJECT_FILE] [-t TEMPORARY_DIR]
               [--prefix-functions PREFIX_FUNCTIONS]
               [--prefix-packages PREFIX_PACKAGES]
               [--post-process POST_PROCESS]
               doxygen_file

**positional arguments**:
  doxygen_file          Doxygen config file

**optional arguments**:
  -h, --help            show this help message and exit
  -p PROJECT_FILE, --project-file PROJECT_FILE
                        Ada project file, mandatory if source files is in
                        different directories
  -t TEMPORARY_DIR, --temporary-dir TEMPORARY_DIR
                        Path to tmp dir, dirs will be created if not exists,
                        default='/path/to/adadoxygen/_tmp'
  --prefix-functions PREFIX_FUNCTIONS
                        Prefix for nested members except packages,
                        default='__'
  --prefix-packages PREFIX_PACKAGES
                        Prefix for packages, default=''
  --post-process POST_PROCESS
                        Post process HTML-files on/off, default='off'
