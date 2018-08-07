import os,sys

py_version = str(sys.version_info[0])+"."+str(sys.version_info[1])
if py_version != '2.7':
	print("Warning: You are running Python with version "+py_version+"")
	print("This program is only tested for 2.7")
	print("If you get unexpected result, please run python again with the flag '-2'")
	
import argparse,ntpath,glob
import xml.etree.ElementTree as ET
from subprocess import call

from class_pplist import PPList
from class_ppfile import PPFile
from class_doxyreader import DoxyReader
from class_commentpreprocess import CommentPreprocess
from class_convert import Convert
from class_htmlpostprocess import HTMLPostprocess
from class_xmlpostprocess import XMLPostprocess


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
		
	def getArgs(self):
		argparser = argparse.ArgumentParser()
		argparser.add_argument('doxygen_file', default="", help="Doxygen config file")
		argparser.add_argument('-p', '--project-file', default="", help="Ada project file, mandatory if source files is in different directories")
		argparser.add_argument('-t','--temporary-dir', default=self.default_tmp_dir, help="Path to tmp dir, dirs will be created if not exists, default='"+self.default_tmp_dir+"'")
		argparser.add_argument('--prefix-functions', default="__", help="Prefix for nested members except packages, default='__'")
		argparser.add_argument('--prefix-packages', default="", help="Prefix for packages, default=''")
		argparser.add_argument('--post-process', default="off", help="Post process HTML-files on/off, default='off'")
		return argparser.parse_args()

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

	""" Preprocessing self.adafiles to self.preprocfiles """
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
			
	""" Convert ada to XML with gnat2xml """
	def ada2xml(self):
		self.doxyReader.printt( "--ada2xml--" )
		gnatArgs = ['gnat2xml','--output-dir='+self.tmp_dir_xml] + self.preprocfiles
		if self.args.project_file != '':
			for preprocfile in self.preprocfiles:
				if ntpath.basename(preprocfile) == ntpath.basename(self.args.project_file):
					project_file = preprocfile
			self.doxyReader.printt( "Projekt fil: "+project_file )
			gnatArgs = ['gnat2xml','--output-dir='+self.tmp_dir_xml,'-P'+project_file,'-U']
		self.doxyReader.printt( " ".join(gnatArgs) )
		call(gnatArgs)
		
	""" Convert XML to PP """
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
			pp = PPFile(filename,sourcefile,tree,self.args.prefix_functions,self.args.prefix_packages,self.doxyReader)
			pp.parse()
			pplist.add(pp)
			
		pplist.collectIncludes()
		pplist.setNamespaces()
		pplist.buildTuples()
		pplist.moveGenericFunctionBodies()
		pplist.exchangePrivateInfo()
		pplist.write()
		
			
	""" Run doxygen with the generated pp-files """
	def pp2doxy(self):
		self.doxyReader.printt( "--pp2doxy--" )
		
		echoArr = []
		echoArr.append('INPUT='+self.tmp_dir_cpp)
		echoArr.append('STRIP_FROM_PATH='+os.path.join(self.tmp_dir_cpp,self.abs2rel(self.doxyReader.stripfrompath)))
		echoArr.append('LAYOUT_FILE='+os.path.join(self.src_dir,'DoxygenLayout.xml'))
		
		for i,el in enumerate(echoArr): echoArr[i] = 'echo "'+el+'"'
		doxyCommand = '( cat '+self.args.doxygen_file+' & '+' & echo "" & '.join(echoArr)+' ) | doxygen -'
		self.doxyReader.printt( doxyCommand )
		os.system(doxyCommand)
		
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
		
	def process(self):
		self.comments2pragmas()
		self.ada2xml()
		self.xml2pp()
		self.pp2doxy()
		
	def postprocess(self):
		if self.args.post_process == 'on':
			self.postprocessHTML()
	
if __name__ == '__main__':
	ad = AdaDoxygen()
	ad.printConfigs()
	ad.process()
	ad.postprocess()
	print("adadoxygen done")



