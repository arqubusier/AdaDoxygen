#!/bin/bash
#
#echo "Ada to XML"
#gnat2xml ../examples/namespace-test/*.ads ../examples/namespace-test/*.adb --output-dir=xmlnstest
echo "XML to C++"
python prog.py ./xmlnstest/*.xml
#python prog.py ./xml/*.xml
#doxygen doxygen_config.txt


python prog.py -d doxygen_config.txt -p ../examples/namespace-test/main.gpr ../examples/namespace-test/*.{adb,ads,gpr} ../examples/namespace-test/package2/*.{adb,ads,gpr} ../examples/namespace-test/package2/package22/*.{adb,ads,gpr}


python prog.py -d doxygen_config.txt ../examples/synth/src/*.ad[sb]


python src/prog.py src/doxygen_config.txt -p examples/namespace-test/main.gpr --post-process off
