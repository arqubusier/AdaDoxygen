import os,sys,argparse,ntpath
import xml.etree.ElementTree as ET
from subprocess import call
from class_ppfile import PPFile
from class_doxyreader import DoxyReader
from class_commentpreprocess import CommentPreprocess

argparser = argparse.ArgumentParser()
argparser.add_argument('files', nargs='+', help="XML-files for Ada to C++. ADB/ADS-files for comment preprocessing")
argparser.add_argument('-d', '--doxygen-file', default="", help="Doxygen config file")
argparser.add_argument('-p', '--project-file', default="", help="Ada project file")
argparser.add_argument('--prefix-functions', default="__", help="Prefix for nested members except packages, default='__'")
argparser.add_argument('--prefix-packages', default="", help="Prefix for packages, default=''")

args = argparser.parse_args()
doxyReader = DoxyReader(args.doxygen_file)
script_dir = os.path.dirname(os.path.realpath(sys.argv[0])) + os.sep

tmp_dir =  os.path.join(script_dir,"_tmp")
tmp_dir_ada = os.path.join(tmp_dir,"ada")
tmp_dir_xml = os.path.join(tmp_dir,"xml")
tmp_dir_cpp = os.path.join(tmp_dir,"cpp")

adafiles = sorted(args.files,key=len)
preprocfiles = []
xmlfiles = []
cppfiles = []

commonpath = os.path.commonprefix(adafiles)
commondir = os.path.dirname(commonpath)

print "--CONFIGS--"
print "Prefix for functions: '"+args.prefix_functions+"'"
print "Prefix for packages: '"+args.prefix_packages+"'"
print "Include private members: '"+str(doxyReader.include_private_bool)+"'"
print "Temporary directory: "+ tmp_dir
print "Doxygen config file: "+ args.doxygen_file
print "Ada project file: "+ args.project_file

call(['rm','-r',tmp_dir])
call(['mkdir',tmp_dir])
call(['mkdir',tmp_dir_ada])
call(['mkdir',tmp_dir_xml])
call(['mkdir',tmp_dir_cpp])

""" Preprocess ada-comments to pragma """
print "--PREPROCESSING--"
for adafile in adafiles:
	preproc = CommentPreprocess(adafile)
	if adafile.startswith(commondir) is False: 
		sys.exit("Error: '"+adafile+"' does not start with "+commondir)
	adafilepath = adafile[len(commondir)+1:]
	preprocfilename = os.path.join(tmp_dir_ada,adafilepath)
	preprocdirname = os.path.dirname(preprocfilename)
	if not os.path.exists(preprocdirname): os.makedirs(preprocdirname)
	with open(preprocfilename,"w+") as preprocfile:
		print preprocfilename + " created"
		preprocfiles.append(preprocfilename)
		preprocfile.write(preproc.getResult())


""" Convert ada to XML with gnat2xml """
print "--CALLING gnat2xml--"
gnatArgs = ['gnat2xml','--output-dir='+tmp_dir_xml] + preprocfiles
if args.project_file != '':
	gnatArgs = ['gnat2xml','--output-dir='+tmp_dir_xml,'-P'+args.project_file,'-U']

print " ".join(gnatArgs)
call(gnatArgs)

def getXMLFiles(dir):
	xmlfiles = []
	for subdir, dirs, files in os.walk(dir):
		for file in files:
			xmlfiles.append(os.path.join(subdir,file))
	return xmlfiles

""" Convert XML to PP """
print "--CONVERTING XML TO PP--"
pps = []
print "Parsing XML..."
xmlfiles = getXMLFiles(tmp_dir_xml)
for xmlfile in xmlfiles:
	tree = ET.parse((xmlfile).strip("\r"))
	pp = PPFile(xmlfile,tree,args.prefix_functions,args.prefix_packages,doxyReader.include_private_bool,tmp_dir_cpp)
	
	print "Parsing XML from "+xmlfile
	pp.parse()
	pps.append(pp)

print "Set includes, privates and namespaces..."
for pp in pps:
	pp.setIncludes(pps)
	pp.setNamespaces(pps)
	pp.setPrivates(pps)
	
print "Generate PP-files..."
for pp in pps:
	print "Creating "+pp.name+"..."
	pp.write()

	
""" Run doxygen and override INPUT in config-file """
print "--CALLING DOXYGEN--"
doxyCommand = '( cat '+args.doxygen_file+' & echo "INPUT='+tmp_dir_cpp+'" ) | doxygen -' #& is ; in unix
print doxyCommand
os.system(doxyCommand)
sys.exit("Everything done")



