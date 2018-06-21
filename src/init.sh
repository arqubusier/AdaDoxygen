#!/bin/bash
#
#echo "Ada to XML"
#gnat2xml ../examples/namespace-test/*.ads ../examples/namespace-test/*.adb --output-dir=xmlnstest
echo "XML to C++"
python prog.py ./xmlnstest/*.xml
#python prog.py ./xml/*.xml
#doxygen doxygen_config.txt



#python prog.py ../examples/namespace-test/*.ads ../examples/namespace-test/*.adb -a Everything