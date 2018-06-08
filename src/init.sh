#!/bin/bash
#
#echo "Ada to XML"
#gnat2xml ../examples/calculator/calculator.adb --output-dir=xml
echo "XML to C++"
python prog.py ./xml/calculator.adb.xml
#doxygen doxygen_config.txt