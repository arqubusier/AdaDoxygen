import os,sys,argparse,ntpath,glob
import xml.etree.ElementTree as ET
from subprocess import call
from class_ppfile import PPFile
from class_doxyreader import DoxyReader
from class_commentpreprocess import CommentPreprocess
from class_convert import Convert

argparser = argparse.ArgumentParser()
argparser.add_argument('files', nargs='+', help="XML-files for Ada to C++. ADB/ADS/GPR-files for comment preprocessing")
argparser.add_argument('-d', '--doxygen-file', default="", help="Doxygen config file")
argparser.add_argument('-p', '--project-file', default="", help="Ada project file, mandatory if source files is in different directories")
argparser.add_argument('--prefix-functions', default="__", help="Prefix for nested members except packages, default='__'")
argparser.add_argument('--prefix-packages', default="", help="Prefix for packages, default=''")

args = argparser.parse_args()
doxyReader = DoxyReader(args.doxygen_file)
script_dir = os.path.dirname(os.path.realpath(sys.argv[0])) + os.sep

tmp_dir =  os.path.join(script_dir,"_tmp")
tmp_dir_ada = os.path.join(tmp_dir,"ada")
tmp_dir_xml = os.path.join(tmp_dir,"xml")
tmp_dir_cpp = os.path.join(tmp_dir,"cpp")

adafiles = args.files
preprocfiles = []
xmlfiles = []

print "--CONFIGS--"
print "Prefix for functions: '"+args.prefix_functions+"'"
print "Prefix for packages: '"+args.prefix_packages+"'"
print "Include private members: '"+str(doxyReader.include_private_bool)+"'"
print "Temporary directory: "+ tmp_dir
print "Doxygen config file: "+ args.doxygen_file
print "Ada project file: "+ args.project_file

call(['rm','-r',tmp_dir])
if not os.path.exists(tmp_dir_ada): os.makedirs(tmp_dir_ada)
if not os.path.exists(tmp_dir_xml): os.makedirs(tmp_dir_xml)
if not os.path.exists(tmp_dir_cpp): os.makedirs(tmp_dir_cpp)


""" Preprocess ada-comments to pragma """
print "--PREPROCESSING--"
commonpath = os.path.commonprefix(adafiles)
commondir = os.path.dirname(commonpath)
for adafile in adafiles:
	preproc = CommentPreprocess(adafile)
	if adafile.startswith(commondir) is False: 
		sys.exit("Error: '"+adafile+"' does not start with "+commondir)
	adafilepath = adafile[len(commondir)+1:]
	preprocfilename = os.path.join(tmp_dir_ada,adafilepath)
	preprocdirname = os.path.dirname(preprocfilename)
	if not os.path.exists(preprocdirname): os.makedirs(preprocdirname)
	with open(preprocfilename,"wb") as preprocfile:
		print preprocfilename + " created"
		preprocfile.write(preproc.getResult())
		#print preproc.getResult()
		preprocfiles.append(preprocfilename)


""" Convert ada to XML with gnat2xml """
print "--CALLING gnat2xml--"
gnatArgs = ['gnat2xml','--output-dir='+tmp_dir_xml] + preprocfiles
if args.project_file != '':
	for preprocfile in preprocfiles:
		if ntpath.basename(preprocfile) == ntpath.basename(args.project_file):
			project_file = preprocfile
	print "Projekt fil: "+project_file
	gnatArgs = ['gnat2xml','--output-dir='+tmp_dir_xml,'-P'+project_file,'-U']
print " ".join(gnatArgs)
call(gnatArgs)


""" Convert XML to PP """
print "--CONVERTING XML TO PP--"
pps = []
xmlfiles = glob.glob(os.path.join(tmp_dir_xml,"*.xml"))
print "Number of Ada-files: "+str(len(preprocfiles))
print "Number of XML-files: "+str(len(xmlfiles))

for xmlfile in xmlfiles:
	tree = ET.parse((xmlfile).strip("\r"))
	filename = Convert.filename(xmlfile, preprocfiles, tmp_dir_cpp)
	dirname = os.path.dirname(filename)
	if not os.path.exists(dirname): os.makedirs(dirname)
	pp = PPFile(filename,tree,args.prefix_functions,args.prefix_packages,doxyReader.include_private_bool)
	pp.parse()
	pps.append(pp)
	
for pp in pps:
	pp.setIncludes(pps)
	pp.setNamespaces(pps)
	pp.setPrivates(pps)
	
for pp in pps:
	print "Creating "+pp.name+"..."
	pp.write()

	
""" Run doxygen and override INPUT in config-file """
print "--CALLING DOXYGEN--"
doxyCommand = '( cat '+args.doxygen_file+' & echo "INPUT='+tmp_dir_cpp+'" ) | doxygen -' #& is ; in unix
print doxyCommand
os.system(doxyCommand)
sys.exit("Everything done")



