import sys,argparse,ntpath
import xml.etree.ElementTree as ET

from cppfile import CppFile
from class_doxyreader import DoxyReader
from fn_commentpreprocess import commentPreprocess

argparser = argparse.ArgumentParser()
argparser.add_argument('files', nargs='+', help="XML-files for Ada to C++. ADB/ADS-files for comment preprocessing")
argparser.add_argument('-pf', '--prefix-functions', default="__", help="Prefix for nested members except packages, default='__'")
argparser.add_argument('-pp', '--prefix-packages', default="", help="Prefix for packages, default=''")
argparser.add_argument('-d', '--doxygen-file', default="", help="Doxygen config file")
argparser.add_argument('-a', '--action', default="Ada2Cpp", help="Ada2Cpp/CommentPreprocessor/PrintConfig, default='Ada2Cpp'")

args = argparser.parse_args()
doxyReader = DoxyReader(args.doxygen_file)


if args.action == 'PrintConfig':
	""" Prints config """
	print "Prefix for functions: '"+args.prefix_functions+"'"
	print "Prefix for packages: '"+args.prefix_packages+"'"
	print "Include private members: '"+str(doxyReader.include_private_bool)+"'"
	sys.exit("Config-print done")
	
elif args.action == 'CommentPreprocessor':
	""" Preprocess ada-files """
	for adafile in args.files:
		commentPreprocess(adafile)
	sys.exit("CommentPreprocessor done")
	
elif args.action == 'Ada2Cpp':
	""" Convert ada-files to pp-files """
	pps = []
	print "---PARSING XML---"
	for xmlfile in args.files:
		tree = ET.parse((xmlfile).strip("\r"))
		pp = CppFile(xmlfile,tree,args.prefix_functions,args.prefix_packages,doxyReader.include_private_bool)
		
		print "Parsing XML from "+xmlfile
		pp.parse()
		pps.append(pp)

	print "---SET INCLUDES AND NAMESPACES---"
	for pp in pps:
		pp.setIncludes(pps)
		pp.setNamespaces(pps)
		
	print "---GENERATE PP FILES---"
	for pp in pps:
		print "Creating "+pp.name+"..."
		pp.write()
	sys.exit("Ada2Cpp done")

sys.exit("Error: No action named '"+args.action+"'")