import os,sys,argparse,ntpath,glob
import xml.etree.ElementTree as ET
from subprocess import call
from class_ppfile import PPFile
from class_doxyreader import DoxyReader
from class_commentpreprocess import CommentPreprocess
from class_convert import Convert
from class_htmlpostprocess import HTMLPostprocess
from class_xmlpostprocess import XMLPostprocess

def abs2rel(path): return path.replace(":","",1).strip("/")

script_dir = os.path.dirname(os.path.realpath(sys.argv[0])) + os.sep
default_tmp_dir = os.path.abspath(os.path.join(script_dir,"..","_tmp"))

argparser = argparse.ArgumentParser()
argparser.add_argument('doxygen_file', default="", help="Doxygen config file")
argparser.add_argument('-p', '--project-file', default="", help="Ada project file, mandatory if source files is in different directories")
argparser.add_argument('-t','--temporary-dir', default=default_tmp_dir, help="Path to tmp dir, dirs will be created if not exists, default='"+default_tmp_dir+"'")
argparser.add_argument('--prefix-functions', default="__", help="Prefix for nested members except packages, default='__'")
argparser.add_argument('--prefix-packages', default="", help="Prefix for packages, default=''")
argparser.add_argument('--post-process', default="off", help="Post process HTML-files on/off, default='off'")

args = argparser.parse_args()
doxyReader = DoxyReader(args.doxygen_file)

if os.path.isabs(args.temporary_dir): tmp_dir = args.temporary_dir
else: tmp_dir = os.path.abspath(os.path.join(os.getcwd(),args.temporary_dir))
	
tmp_dir_ada = os.path.join(tmp_dir,"ada")
tmp_dir_xml = os.path.join(tmp_dir,"xml")
tmp_dir_cpp = os.path.join(tmp_dir,"cpp")

adafiles = doxyReader.input_files
preprocfiles = []
xmlfiles = []

doxyReader.printt( "--CONFIGS--" )
doxyReader.printt( "Prefix for functions: '"+args.prefix_functions+"'" )
doxyReader.printt( "Prefix for packages: '"+args.prefix_packages+"'" )
doxyReader.printt( "Extract undocumented members: '"+str(doxyReader.extract_all_bool)+"'" )
doxyReader.printt( "Include private members: '"+str(doxyReader.include_private_bool)+"'" )
doxyReader.printt( "Hide undoc classes: '"+str(doxyReader.hideundoc_classes)+"'" )
doxyReader.printt( "Temporary directory: "+ tmp_dir )
doxyReader.printt( "Doxygen config file: "+ args.doxygen_file )
doxyReader.printt( "Ada project file: "+ args.project_file )
doxyReader.printt( "Post process: "+ args.post_process )
	
if os.path.isdir(tmp_dir_ada) is False: os.makedirs(tmp_dir_ada)
if os.path.isdir(tmp_dir_xml) is False: os.makedirs(tmp_dir_xml)
if os.path.isdir(tmp_dir_cpp) is False: os.makedirs(tmp_dir_cpp)


""" Preprocess ada-comments to pragma """
print "--PREPROCESSING--"
commonpath = os.path.commonprefix(adafiles)
commondir = os.path.dirname(commonpath)
for adafile in adafiles:
	preproc = CommentPreprocess(adafile)
	adafilepath = abs2rel(adafile)
	preprocfilename = os.path.join(tmp_dir_ada,adafilepath)
	preprocdirname = os.path.dirname(preprocfilename)
	if not os.path.exists(preprocdirname): os.makedirs(preprocdirname)
	with open(preprocfilename,"wb") as preprocfile:
		doxyReader.printt( preprocfilename + " created" )
		preprocfile.write(preproc.getResult())
		preprocfiles.append(preprocfilename)


""" Convert ada to XML with gnat2xml """
doxyReader.printt( "--CALLING gnat2xml--" )
gnatArgs = ['gnat2xml','--output-dir='+tmp_dir_xml] + preprocfiles
if args.project_file != '':
	for preprocfile in preprocfiles:
		if ntpath.basename(preprocfile) == ntpath.basename(args.project_file):
			project_file = preprocfile
	doxyReader.printt( "Projekt fil: "+project_file )
	gnatArgs = ['gnat2xml','--output-dir='+tmp_dir_xml,'-P'+project_file,'-U']
doxyReader.printt( " ".join(gnatArgs) )
call(gnatArgs)

""" Convert XML to PP """
doxyReader.printt( "--CONVERTING XML TO PP--" )
pps = []
xmlfiles = glob.glob(os.path.join(tmp_dir_xml,"*.xml"))
doxyReader.printt( "Number of Ada-files: "+str(len(preprocfiles)) )
doxyReader.printt( "Number of XML-files: "+str(len(xmlfiles)) )

for xmlfile in xmlfiles:
	tree = ET.parse((xmlfile).strip("\r"))
	filename, sourcefile = Convert.filename(xmlfile, preprocfiles, tmp_dir_ada, tmp_dir_cpp)
	dirname = os.path.dirname(filename)
	if not os.path.exists(dirname): os.makedirs(dirname)
	pp = PPFile(filename,sourcefile,tree,args.prefix_functions,args.prefix_packages,doxyReader)
	pp.parse()
	pps.append(pp)
	
for pp in pps:
	pp.setIncludes(pps)
	pp.setNamespaces(pps)
	
for pp in pps:
	doxyReader.printt( "Creating "+pp.name+"..." )
	pp.write()

	
""" Run doxygen and override INPUT in config-file """
doxyReader.printt( "--CALLING DOXYGEN--" )
nl = "r\n"
strip = 'STRIP_FROM_PATH='+os.path.join(tmp_dir_cpp,abs2rel(doxyReader.stripfrompath))
doxyCommand = '( cat '+args.doxygen_file+' & echo "INPUT='+tmp_dir_cpp+'" & echo "" & echo "'+strip+'" ) | doxygen -' #& is ; in unix
doxyReader.printt( doxyCommand )
os.system(doxyCommand)


""" Postprocess HTML-files """
if args.post_process == 'on':
	doxyReader.printt( "--POST PROCESSING--" )
	htmlfiles = glob.glob(os.path.join(doxyReader.htmlpath,"*.html"))
	for htmlfile in htmlfiles:
		postproc = XMLPostprocess(htmlfile)
		if postproc.succeded():
			with open(htmlfile,"wb") as fh:
				doxyReader.printt( htmlfile + " post processed" )
				fh.write(postproc.getResult())
		else: print "Failed: "+ htmlfile

sys.exit("Everything done")








