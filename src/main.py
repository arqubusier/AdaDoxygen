import os,sys,shutil,logging

py_version = str(sys.version_info[0])+"."+str(sys.version_info[1])
if py_version != '2.7':
	print("Warning: You are running Python with version "+py_version+"")
	print("This program is only tested for 2.7")
	print("If you get unexpected result, please run python again with the flag '-2'")
	
# Import std libs
import argparse,ntpath,glob
import xml.etree.ElementTree as ET
import subprocess

# Import AdaDoxygen classes
from pplist import PPList
from ppfile import PPFile
from doxyreader import DoxyReader
from commentpreprocess import CommentPreprocess
from convert import Convert
from xmlpostprocess import XMLPostprocess

## The main class
class AdaDoxygen:

	def __init__(self):
		self.args = self.getArgs()
		self.setLogging()
		self.doxyReader = DoxyReader(self.args.doxygen_file)
		self.setDirectoryPaths()
		self.preprocfiles = []
		self.xmlfiles = []
		
	## Get command line arguments with argparse
	def getArgs(self):
		argparser = argparse.ArgumentParser()
		argparser.add_argument('doxygen_file', default="", help="Your doxyfile, generate one by running 'doxygen -g'")
		argparser.add_argument('-p', '--project-file', default="", help="Ada project file, mandatory if source files is in different directories")
		argparser.add_argument('-t','--temporary-dir', default="_tmp", help="Path to tmp dir, dirs will be created if not exists, default='_tmp'")
		argparser.add_argument('-r','--remove-temporary-dir', action='store_true', help="Remove temporary dir when AdaDoxygen is done")
		argparser.add_argument('-l', '--logging-level', default="warning", help="debug/info/warning/error/critical, default='warning'")
		argparser.add_argument('--prefix-functions', default="__", help="Prefix for nested members except packages, default='__'")
		argparser.add_argument('--prefix-packages', default="", help="Prefix for packages, default=''")
		argparser.add_argument('--prefix-repclause', default="_rep_", help="Prefix for representation clauses, default='_rep_'")
		argparser.add_argument('--hide-repclause', action='store_true', help="Remove 'for x use y'-clause as code block comment on original type")
		argparser.add_argument('--post-process', action='store_true', help="Post process HTML-files")
		argparser.add_argument('--gnat-options', nargs='?', default="", help="gnat2xml options. If more then one, wrap with quotes")
		argparser.add_argument('--gnat-cargs', nargs='?', default="", help="gnat2xml cargs. If more then one, wrap with quotes")
		argparser.add_argument('--path-gnat2xml', nargs='?', default="gnat2xml", help="Path to gnat2xml, default='gnat2xml'")
		argparser.add_argument('--path-doxygen', nargs='?', default="doxygen", help="Path to doxygen, default='doxygen'")
		
		return argparser.parse_args()
		
	## Set logging level
	def setLogging(self):
		ll = self.args.logging_level
		if ll == "critical": level = logging.CRITICAL
		elif ll == "error": level = logging.ERROR
		elif ll == "warning": level = logging.WARNING
		elif ll == "info": level = logging.INFO
		elif ll == "debug": level = logging.DEBUG
		else: level = logging.WARNING
		logging.basicConfig(format="AdaDoxygen:%(levelname)s: %(message)s",level=level)

	## Setup needed paths and create tmp-dirs if not exists
	def setDirectoryPaths(self):
		self.src_dir = os.path.dirname(os.path.realpath(__file__))
		if os.path.isabs(self.args.temporary_dir): self.tmp_dir = self.args.temporary_dir
		else: self.tmp_dir = os.path.abspath(os.path.join(os.getcwd(),self.args.temporary_dir))
		self.tmp_dir_ada = os.path.join(self.tmp_dir,"ada")
		self.tmp_dir_xml = os.path.join(self.tmp_dir,"xml")
		self.tmp_dir_cpp = os.path.join(self.tmp_dir,"cpp")
		if os.path.isdir(self.tmp_dir_ada) is False: os.makedirs(self.tmp_dir_ada)
		if os.path.isdir(self.tmp_dir_xml) is False: os.makedirs(self.tmp_dir_xml)
		if os.path.isdir(self.tmp_dir_cpp) is False: os.makedirs(self.tmp_dir_cpp)
		
	## Print configs from cmd args and the doxyfile
	def printConfigs(self):
		logging.info( "--CONFIGS--" )
		logging.info( "Prefix for functions: '"+self.args.prefix_functions+"'" )
		logging.info( "Prefix for packages: '"+self.args.prefix_packages+"'" )
		logging.info( "Extract undocumented members: '"+str(self.doxyReader.extract_all_bool)+"'" )
		logging.info( "Include private members: '"+str(self.doxyReader.include_private_bool)+"'" )
		logging.info( "Hide undoc classes: '"+str(self.doxyReader.hideundoc_classes)+"'" )
		logging.info( "Temporary directory: "+ self.tmp_dir )
		logging.info( "Doxygen config file: "+ self.args.doxygen_file )
		logging.info( "Ada project file: "+ self.args.project_file )
		logging.info( "Post process: "+ str(self.args.post_process) )
		
	def abs2rel(self,path): return path.replace(":","",1).strip("/")

	## Preprocessing (and or moving) input files
	def comments2pragmas(self):
		logging.info( "--comments2pragmas--" )
		for original_file in self.doxyReader.input_files:
			ext = os.path.splitext(original_file)[1]
			relpath = self.abs2rel(original_file)
			if ext in ['.adb','.ads']:
				# Only preprocess Ada-files...
				preproc = CommentPreprocess(original_file)
				newfilecontent = preproc.getResult()
				newfile = os.path.join(self.tmp_dir_ada,relpath)
				self.preprocfiles.append(newfile)
			else:
				# ...but move other files to tmp/cpp directly
				with open(original_file) as f:
					newfilecontent = f.read()
				newfile = os.path.join(self.tmp_dir_cpp,relpath)
			
			newfiledirname = os.path.dirname(newfile)
			if not os.path.exists(newfiledirname): os.makedirs(newfiledirname)
			with open(newfile,"wb") as fh:
				logging.debug("Creating "+newfile)
				fh.write(newfilecontent)
			
	## Convert ada to XML with gnat2xml
	def ada2xml(self):
		logging.info("--Calling gnat2xml--")
		gnatArgs = [self.args.path_gnat2xml,'--output-dir='+self.tmp_dir_xml]
		if self.args.gnat_options != '':
			gnatArgs = gnatArgs + self.args.gnat_options.strip().split()
		if self.args.project_file == '':
			incDirs = self._getGnat2xmlIncludeDirs()
			gnatArgs = gnatArgs + self.preprocfiles + incDirs
		else:
			for preprocfile in self.preprocfiles:
				if ntpath.basename(preprocfile) == ntpath.basename(self.args.project_file):
					project_file = preprocfile
			logging.info("Project file: "+project_file)
			gnatArgs = gnatArgs + ['-P'+project_file,'-U']
			
		if self.args.gnat_cargs != '':
			gnatArgs.append('-cargs')
			gnatArgs + self.args.gnat_cargs.strip().split()
		logging.info(" ".join(gnatArgs))
		subprocess.call(gnatArgs)
		
	## \private
	def _getGnat2xmlIncludeDirs(self):
		dirArr = []
		for file in self.preprocfiles:
			dir = os.path.dirname(file)
			if dir not in dirArr: 
				dirArr.append('-I'+dir)
		return dirArr
		
	## Convert XML to PP files
	def xml2pp(self):
		logging.info("--xml2pp--")
		pplist = PPList()
		self.xmlfiles = glob.glob(os.path.join(self.tmp_dir_xml,"*.xml"))
		
		logging.info("Number of input-files: "+str(len(self.doxyReader.input_files)))
		logging.info("Number of Ada-files: "+str(len(self.preprocfiles)))
		logging.info("Number of XML-files: "+str(len(self.xmlfiles)))

		for xmlfile in self.xmlfiles:
			tree = ET.parse((xmlfile).strip("\r"))
			filename, sourcefile = Convert.filename(xmlfile, self.preprocfiles, self.tmp_dir_ada, self.tmp_dir_cpp)
			dirname = os.path.dirname(filename)
			if not os.path.exists(dirname): os.makedirs(dirname)
			
			extractAll = self.doxyReader.extract_all_bool
			extractPriv = self.doxyReader.include_private_bool
			hideUndocPkgs = self.doxyReader.include_private_bool
			
			pp = PPFile(filename,sourcefile,tree,self.args.prefix_functions,self.args.prefix_packages,
						self.args.prefix_repclause,self.args.hide_repclause,
						extractAll,extractPriv,hideUndocPkgs)
			pp.parse()
			pplist.add(pp)
			
		pplist.collectIncludes()
		pplist.setNamespaces()
		pplist.buildTuples()
		pplist.moveGenericFunctionBodies()
		pplist.exchangePrivateInfo()
		pplist.setImports()
		pplist.write()
		
			
	## Run doxygen with the generated pp-files
	def pp2doxy(self):
		logging.info( "--pp2doxy--" )
		
		echoArr = []
		echoArr.append('INPUT='+self.tmp_dir_cpp)
		echoArr.append('RECURSIVE=YES')
		echoArr.append('STRIP_FROM_PATH='+os.path.join(self.tmp_dir_cpp,self.abs2rel(self.doxyReader.stripfrompath)))
		echoArr.append('LAYOUT_FILE='+os.path.join(self.src_dir,'doxygenlayout.xml'))
		
		sep = ';'
		if os.name == 'nt': sep = '&'
		
		for i,el in enumerate(echoArr): echoArr[i] = 'echo "'+el+'"'
		impStr = ' '+sep+' echo "" '+sep+' '
		echoStr = impStr.join(echoArr)
		doxyCommand = '( cat '+self.args.doxygen_file+' '+sep+' '+' '+echoStr+' ) | '+self.args.path_doxygen+' -'
		logging.info(doxyCommand)
		os.system(doxyCommand)
		
	## Post process the doxygenerated html-files, not tested
	def postprocessHTML(self):
		logging.info("--POST PROCESSING HTML--")
		logging.warning("This function has not been tested")
		htmlfiles = glob.glob(os.path.join(self.doxyReader.htmlpath,"*.html"))
		for htmlfile in htmlfiles:
			postproc = XMLPostprocess(htmlfile)
			if postproc.succeded():
				with open(htmlfile,"wb") as fh:
					logging.debug( htmlfile + " post processed" )
					fh.write(postproc.getResult())
			else: 
				logging.warning("Failed: "+htmlfile)
		
	## Main steps for AdaDoxygen
	def process(self):
		self.comments2pragmas()
		self.ada2xml()
		self.xml2pp()
		self.pp2doxy()
		
	## Remove temporary dir and run html post process
	def postprocess(self):
		if self.args.post_process:
			self.postprocessHTML()
		if self.args.remove_temporary_dir:
			shutil.rmtree(self.tmp_dir,ignore_errors=True)
	
if __name__ == '__main__':
	ad = AdaDoxygen()
	ad.printConfigs()
	ad.process()
	ad.postprocess()
	logging.info("adadoxygen done")



