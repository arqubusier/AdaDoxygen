import sys,argparse,ntpath
import xml.etree.ElementTree as ET
from cppfile import CppFile

argparser = argparse.ArgumentParser()
argparser.add_argument('xmlfiles', nargs='+')
args = argparser.parse_args()

pps = []
print "---PARSING XML---"
for xmlfile in args.xmlfiles:
	tree = ET.parse((xmlfile).strip("\r"))
	print "Parsing XML from "+xmlfile
	pp = CppFile(xmlfile,tree)
	pp.parse()
	pps.append(pp)

print "---SET INCLUDES AND CREATE PP FILES---"
for pp in pps:
	pp.setIncludes(pps)
	print "Includes for "+pp.name+":"
	print pp.includes
	pp.write()
	
sys.exit("klart")
