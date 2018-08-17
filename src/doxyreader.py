import os,sys,re,ConfigParser,StringIO,logging

## Reads values from a Doxyfile
class DoxyReader:

	def __init__(self,file):
		self.file = file
		self.parser = self.getParser()
		
		self.extract_all_bool = self.getBool('EXTRACT_ALL')
		self.include_private_bool = self.getBool('EXTRACT_PRIVATE')
		self.recursive_bool = self.getBool('RECURSIVE')
		
		if self.get('EXTENSION_MAPPING') != "adb=C++ ads=C++":
			logging.warning("EXTENSION_MAPPING in doxyfile should be 'adb=C++ ads=C++'")
			
		self.input_files = self.getInputFiles()
		logging.info("Number of input files: "+str(len(self.input_files)))
		
		self.stripfrompath = self.get('STRIP_FROM_PATH')
		self.hideundoc_classes = self.getBool('HIDE_UNDOC_CLASSES')
		self.htmlpath = os.path.join(os.getcwd(),self.get('HTML_OUTPUT'))
			
	## Returns list of files selected in INPUT
	def getInputFiles(self):
		res = []
		arr = self.get('INPUT').split(' ')
		doxypath = os.path.dirname(self.file)
		
		self._getInputFilesRecursive(doxypath,arr,res)
		return res
		
	def _getInputFilesRecursive(self,current_dir,arr,res,has_traversed=False):
		for el in arr:
			el_abs = os.path.abspath(os.path.join(current_dir,el))
			if os.path.isdir(el_abs):
				if has_traversed is False or self.recursive_bool:
					self._getInputFilesRecursive(el_abs,os.listdir(el_abs),res,True)
			elif os.path.isfile(el_abs):
				fileext = os.path.splitext(el_abs)[1]
				if self.fileAlreadyIncluded(res,el_abs) is False:
					res.append(el_abs)
			else: 
				logging.warning("'" + el_abs + "' is not directory or file")

	## Check if the basename already exists in a list of files
	def fileAlreadyIncluded(self,files,file):
		filename = os.path.basename(file)
		for f in files:
			if filename == os.path.basename(f):
				logging.warning(''+filename+' exists in more then one directory. Choosing the first one selected in doxyfile.')
				return True
		return False
			
	## Convert doxygen YES/NO to python boolean
	def getBool(self,key):
		if self.get(key) == 'YES': return True
		return False
		
	## Get a config parser to read the doxyfile
	def getParser(self):
		parser = ConfigParser.ConfigParser()
		with open(self.file) as stream:
			stream = StringIO.StringIO("[root]\n"+stream.read())
			parser.readfp(stream)
		return parser
		
	## Get a value by key in the doxyfile
	def get(self,key): return self.parser.get('root',key).strip()
	
	
	
	
	
	
