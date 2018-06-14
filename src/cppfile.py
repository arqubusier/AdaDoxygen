from class_convert import Convert
from class_extract import Extract

class CppFile:
	
	PRIMITIVES = {
		"Integer" : "int",
		"Float" : "float",
		"void" : "void"
	}
	
	def __init__(self,xmlfile,tree):
		self.root = tree.getroot()
		self.name = self.root.get('def_name')
		self.type = "program"
		self.source = self.root.get('source_file')
		self.filename = Convert.filename(xmlfile)
		self.filetype = self.filename.split('.')[-1]
		self.file = open("cpp/"+self.filename,"w+")
		self.elements = [] #holds functions, structs and packages
		self.typedefs = []
		self.includes = []
		self.namespaces = []
		
	""" Start parsing tree """
	def parse(self):
		node = self.root.find('unit_declaration_q')
		
		if node.find('procedure_body_declaration') is not None:
			self._loop(node,self.elements)
		elif node.find('package_body_declaration') is not None:
			self.type = "package"
			self._loop(node.find('package_body_declaration').find('body_declarative_items_ql'),self.elements)
		elif node.find('package_declaration') is not None:
			self.type = "package"
			self._loop(node.find('package_declaration').find('visible_part_declarative_items_ql'),self.elements)
			
		
	""" Recursively loop through each level in the XML-tree """
	def _loop(self,node,elements,parent=None):
		lastNode = None
		for child in node:
			
			if child.tag == 'function_body_declaration' or child.tag == 'procedure_body_declaration':
				function = Extract.getFunction(child,lastNode)
				elements.append(function)
				if child.find('body_declarative_items_ql') is not None:
					self._loop(child.find('body_declarative_items_ql'),function['childs'])
			
			elif child.tag == 'procedure_declaration' or child.tag == 'function_declaration':
				function = Extract.getFunctionHead(child,lastNode)
				elements.append(function)
			
			elif child.tag == 'ordinary_type_declaration':
				struct = Extract.getStruct(child,lastNode)
				elements.append(struct)
				if child.find('body_declarative_items_ql') is not None:
					self._loop(child.find('body_declarative_items_ql'),struct['childs'])
			
			elif child.tag == 'package_body_declaration':
				package = Extract.getPackage(child,lastNode)
				elements.append(package)
				if child.find('body_declarative_items_ql') is not None:
					self._loop(child.find('body_declarative_items_ql'),package['childs'])
					
			elif child.tag == 'package_declaration':
				package = Extract.getPackage(child,lastNode)
				elements.append(package)
				if child.find('visible_part_declarative_items_ql') is not None:
					self._loop(child.find('visible_part_declarative_items_ql'),package['childs'])
			
			lastNode = child
			
	""" Set valid includes when all files have been parsed """
	def setIncludes(self,pps):
		node = self.root.find('context_clause_elements_ql')
		if node is None: return
		for withNode in node.findall('with_clause'):
			idNodes = withNode.iter('identifier')
			attrs = []
			for idNode in idNodes:
				attrs.append(idNode.get('ref_name'))
			name = "::".join(attrs)
			for pp in pps:
				if name == pp.name and pp.filetype == 'hpp':
					self.includes.append({'name':name,'file':pp.filename})
					break
					
	""" Set namespaces """
	def setNamespaces(self,pps):
		print "implement this"
	
	""" Converts records/datatypes to c++ """
	def convertPrimitive(self,type):
		#check for primitive key-value pair
		if type in self.PRIMITIVES.keys(): 
			return self.PRIMITIVES[type]
		
		#otherwise, add typedef if not exists
		typedef = "typedef unsigned int "+type+";"
		if typedef not in self.typedefs:
			print typedef
			self.typedefs.append(typedef)
		return type	
		
	""" 
	Write result to the c++ file
	"""
	def write(self):
		out = "/*! @file "+self.filename+" */\n\n"
		for include in self.includes:
			out += "\n"+Convert.include(include)
		out += "\n".join(self.typedefs)+"\n\n"
		if self.type == 'package': out += "namespace "+self.name+"\n{"
		out += "\n"+self.writeNested(None,self.elements)
		if self.type == 'package': out += "\n}"
		self.file.write(out)
	
	def writeNested(self,parent,elements):
		out = ''
		for element in elements:
			if len(element['childs']) > 0:
				out += "namespace _"+element['name']+" {\n"
				out += self.writeNested(element,element['childs'])
				out += "\n}"
		
			if element['type'] == 'struct':
				out += "\n" + Convert.struct(element) + "\n"
			elif element['type'] == 'function':
				out += "\n" + Convert.function(element) + "\n"
			
		return out