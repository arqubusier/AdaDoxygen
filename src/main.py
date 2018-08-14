import os,sys

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
		self.script_dir = os.path.dirname(os.path.realpath(sys.argv[0])) + os.sep
		self.default_tmp_dir = os.path.abspath(os.path.join(self.script_dir,"..","_tmp"))
		self.args = self.getArgs()
		self.doxyReader = DoxyReader(self.args.doxygen_file)
		self.setDirectoryPaths()
		self.adafiles = self.doxyReader.input_files
		self.preprocfiles = []
		self.xmlfiles = []
		
	## Get command line arguments with argparse
	def getArgs(self):
		argparser = argparse.ArgumentParser()
		argparser.add_argument('doxygen_file', default="", help="Doxygen config file, generate one by running 'doxygen -g'")
		argparser.add_argument('-p', '--project-file', default="", help="Ada project file, mandatory if source files is in different directories")
		argparser.add_argument('-t','--temporary-dir', default=self.default_tmp_dir, help="Path to tmp dir, dirs will be created if not exists, default='"+self.default_tmp_dir+"'")
		argparser.add_argument('--cargs', nargs='?', default="", help="gnat2xml cargs. If more then one, wrap with quotes")
		argparser.add_argument('--prefix-functions', default="__", help="Prefix for nested members except packages, default='__'")
		argparser.add_argument('--prefix-packages', default="", help="Prefix for packages, default=''")
		argparser.add_argument('--prefix-repclause', default="_rep_", help="Prefix for representation clauses, default='_rep_'")
		argparser.add_argument('--extract-repclause', action='store_true', help="Append 'for x use y'-clause as code block comment on original type")
		argparser.add_argument('--post-process', action='store_true', help="Post process HTML-files")
		argparser.add_argument('--hide-gnat-output', action='store_true', help='Output from gnat2xml will be hidden')
		
		return argparser.parse_args()

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
		if self.doxyReader.quiet: return
		print( "--CONFIGS--" )
		print( "Prefix for functions: '"+self.args.prefix_functions+"'" )
		print( "Prefix for packages: '"+self.args.prefix_packages+"'" )
		print( "Extract undocumented members: '"+str(self.doxyReader.extract_all_bool)+"'" )
		print( "Include private members: '"+str(self.doxyReader.include_private_bool)+"'" )
		print( "Hide undoc classes: '"+str(self.doxyReader.hideundoc_classes)+"'" )
		print( "Temporary directory: "+ self.tmp_dir )
		print( "Doxygen config file: "+ self.args.doxygen_file )
		print( "Ada project file: "+ self.args.project_file )
		print( "Post process: "+ self.args.post_process )
		
	def abs2rel(self,path): return path.replace(":","",1).strip("/")

	## Preprocessing self.adafiles to self.preprocfiles
	def comments2pragmas(self):
		self.doxyReader.printt( "--comments2pragmas--" )
		commonpath = os.path.commonprefix(self.adafiles)
		commondir = os.path.dirname(commonpath)
		for adafile in self.adafiles:
			preproc = CommentPreprocess(adafile)
			adafilepath = self.abs2rel(adafile)
			preprocfilename = os.path.join(self.tmp_dir_ada,adafilepath)
			preprocdirname = os.path.dirname(preprocfilename)
			if not os.path.exists(preprocdirname): os.makedirs(preprocdirname)
			with open(preprocfilename,"wb") as preprocfile:
				self.doxyReader.printt(preprocfilename + " created")
				preprocfile.write(preproc.getResult())
				self.preprocfiles.append(preprocfilename)
			
	## Convert ada to XML with gnat2xml
	def ada2xml(self):
		self.doxyReader.printt( "--Calling gnat2xml--" )
		gnatArgs = ['gnat2xml','--output-dir='+self.tmp_dir_xml]
		
		if self.args.project_file == '':
			incDirs = self._getGnat2xmlIncludeDirs()
			gnatArgs = gnatArgs + self._getGnat2xmlFiles() + incDirs
		else:
			for preprocfile in self.preprocfiles:
				if ntpath.basename(preprocfile) == ntpath.basename(self.args.project_file):
					project_file = preprocfile
			self.doxyReader.printt( "Projekt fil: "+project_file )
			gnatArgs = gnatArgs + ['-P'+project_file,'-U']
			
		if self.args.cargs != '':
			gnatArgs.append('-cargs')
			gnatArgs.append(self.args.cargs)
		print( " ".join(gnatArgs) )
		if self.args.hide_gnat_output:
			fnull = open(os.devnull,'w')
			retcode = subprocess.call(gnatArgs, stdout=fnull, stderr=subprocess.STDOUT)
			print("gnat2xml returned with status "+str(retcode))
		else:
			subprocess.call(gnatArgs)
		
	## \private
	def _getGnat2xmlIncludeDirs(self):
		dirArr = []
		for file in self.preprocfiles:
			dir = os.path.dirname(file)
			if dir not in dirArr: 
				dirArr.append('-I'+dir)
		return dirArr
		
	## \private
	def _getGnat2xmlFiles(self):
		files = []
		for file in self.preprocfiles:
			ext = os.path.splitext(file)[1]
			if ext in ['.adb','.ads']:
				files.append(file)
			else:
				preprocfilepath = os.path.relpath(file,self.tmp_dir_ada)
				newfilepathabs = os.path.join(self.tmp_dir_cpp, preprocfilepath)
				if os.path.isfile(newfilepathabs): os.remove(newfilepathabs)
				os.rename(file,newfilepathabs)
				
		return files
		
	## Convert XML to PP files
	def xml2pp(self):
		self.doxyReader.printt( "--xml2pp--" )
		pplist = PPList()
		self.xmlfiles = glob.glob(os.path.join(self.tmp_dir_xml,"*.xml"))
		self.doxyReader.printt( "Number of Ada-files: "+str(len(self.preprocfiles)) )
		self.doxyReader.printt( "Number of XML-files: "+str(len(self.xmlfiles)) )

		for xmlfile in self.xmlfiles:
			tree = ET.parse((xmlfile).strip("\r"))
			filename, sourcefile = Convert.filename(xmlfile, self.preprocfiles, self.tmp_dir_ada, self.tmp_dir_cpp)
			dirname = os.path.dirname(filename)
			if not os.path.exists(dirname): os.makedirs(dirname)
			pp = PPFile(filename,sourcefile,tree,self.args.prefix_functions,self.args.prefix_packages,self.args.prefix_repclause,self.args.extract_repclause,self.doxyReader)
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
		self.doxyReader.printt( "--pp2doxy--" )
		
		echoArr = []
		echoArr.append('INPUT='+self.tmp_dir_cpp)
		echoArr.append('RECURSIVE=YES')
		echoArr.append('STRIP_FROM_PATH='+os.path.join(self.tmp_dir_cpp,self.abs2rel(self.doxyReader.stripfrompath)))
		echoArr.append('LAYOUT_FILE='+os.path.join(self.src_dir,'DoxygenLayout.xml'))
		
		sep = ';'
		if os.name == 'nt': sep = '&'
		
		for i,el in enumerate(echoArr): echoArr[i] = 'echo "'+el+'"'
		impStr = ' '+sep+' echo "" '+sep+' '
		echoStr = impStr.join(echoArr)
		doxyCommand = '( cat '+self.args.doxygen_file+' '+sep+' '+' '+echoStr+' ) | doxygen -'
		self.doxyReader.printt( doxyCommand )
		os.system(doxyCommand)
		
	## Post process the doxygenerated html-files, not tested
	def postprocessHTML(self):
		doxyReader.printt( "--POST PROCESSING--" )
		htmlfiles = glob.glob(os.path.join(doxyReader.htmlpath,"*.html"))
		for htmlfile in htmlfiles:
			postproc = XMLPostprocess(htmlfile)
			if postproc.succeded():
				with open(htmlfile,"wb") as fh:
					doxyReader.printt( htmlfile + " post processed" )
					fh.write(postproc.getResult())
			else: 
				doxyReader.printt( "Failed: "+ htmlfile )
		
	## Main steps for AdaDoxygen
	def process(self):
		self.comments2pragmas()
		self.ada2xml()
		self.xml2pp()
		self.pp2doxy()
		
	## Runs postprocessHTML 
	#  (maybe more postprocess related functions in the future)
	def postprocess(self):
		if self.args.post_process:
			self.postprocessHTML()
	
if __name__ == '__main__':
	ad = AdaDoxygen()
	ad.printConfigs()
	ad.process()
	ad.postprocess()
	print("adadoxygen done")



