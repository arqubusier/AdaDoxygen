#!/bin/bash
#
#echo "Ada to XML"
#gnat2xml ../examples/namespace-test/*.ads ../examples/namespace-test/*.adb --output-dir=xmlnstest
echo "XML to C++"
python prog.py ./xmlnstest/*.xml
#python prog.py ./xml/*.xml
#doxygen doxygen_config.txt


python prog.py -d doxygen_config.txt -p ../examples/namespace-test/main.gpr ../examples/namespace-test/*.ad[sb] ../examples/namespace-test/package2/*.ad[sb] ../examples/namespace-test/package2/package22/*.ad[sb]


python prog.py -d doxygen_config.txt ../examples/synth/src/*.ad[sb]