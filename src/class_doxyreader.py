import os,sys,re,ConfigParser,StringIO

class DoxyReader:

	def __init__(self,file):
		self.file = file
		self.parser = self.getParser()
		
		self.quiet = self.getBool('QUIET')
		self.extract_all_bool = self.getBool('EXTRACT_ALL')
		self.include_private_bool = self.getBool('EXTRACT_PRIVATE')
		self.recursive_bool = self.getBool('RECURSIVE')
		
		if self.get('EXTENSION_MAPPING') != "adb=C++ ads=C++":
			self.printt("Warning: EXTENSION_MAPPING in doxyfile should be 'adb=C++ ads=C++'")
		self.input_files = self.getInputFiles()
		self.stripfrompath = self.get('STRIP_FROM_PATH')
		
		self.hideundoc_classes = self.getBool('HIDE_UNDOC_CLASSES')
		self.htmlpath = os.path.join(os.getcwd(),self.get('HTML_OUTPUT'))
		
			
	def getInputFiles(self):
		res = []
		arr = self.get('INPUT').split(' ')
		doxypath = os.path.dirname(self.file)
		
		self.getInputFilesRecursive(doxypath,arr,res)
		return res
		
	def getInputFilesRecursive(self,current_dir,arr,res,has_traversed=False):
		for el in arr:
			el_abs = os.path.abspath(os.path.join(current_dir,el))
			if os.path.isdir(el_abs):
				if has_traversed is False or self.recursive_bool:
					self.getInputFilesRecursive(el_abs,os.listdir(el_abs),res,True)
			elif os.path.isfile(el_abs):
				fileext = os.path.splitext(el_abs)[1]
				if fileext in ['.adb','.ads','gpr'] and self.fileAlreadyIncluded(res,el_abs) is False:
					res.append(el_abs)
			else: self.printt("Warning: '" + el_abs + "' is not directory or file")

	def fileAlreadyIncluded(self,files,file):
		filename = os.path.basename(file)
		for f in files:
			if filename == os.path.basename(f):
				print('Warning: '+filename+' exists in more then one directory. Choosing the first one selected in doxyfile.')
				return True
		return False
			
	def getBool(self,key):
		if self.get(key) == 'YES': return True
		return False
		
	def getParser(self):
		parser = ConfigParser.ConfigParser()
		with open(self.file) as stream:
			stream = StringIO.StringIO("[root]\n"+stream.read())
			parser.readfp(stream)
		return parser
		
	def get(self,key): return self.parser.get('root',key).strip()
	
	def printt(self,str): 
		if self.quiet is False: print(str)
