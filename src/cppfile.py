from class_convert import Convert
from class_extract import Extract

class CppFile:
	
	def __init__(self,xmlfile,tree,prefixFunction,prefixClass,includePrivate):
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
		self.prefixFunction = prefixFunction
		self.prefixClass = prefixClass
		self.includePrivate = includePrivate
		
	""" Start parsing tree """
	def parse(self):
		node = self.root.find('unit_declaration_q')
		self._loop(node,self.elements)
		
	""" Recursively loop through each level in the XML-tree """
	def _loop(self,node,elements,parent=None):
		lastNode = None
		i = 0
		for child in node:
			
			if child.tag == 'function_body_declaration' or child.tag == 'procedure_body_declaration':
				function = Extract.getFunction(child,lastNode)
				function['comment'] = Extract.getComment(node,i)
				elements.append(function)
				if child.find('body_declarative_items_ql') is not None:
					self._loop(child.find('body_declarative_items_ql'),function['childs'])
			
			elif child.tag == 'procedure_declaration' or child.tag == 'function_declaration':
				function = Extract.getFunctionHead(child,lastNode)
				function['comment'] = Extract.getComment(node,i)
				elements.append(function)
			
			elif child.tag == 'ordinary_type_declaration':
				struct = Extract.getStruct(child,lastNode)
				struct['comment'] = Extract.getComment(node,i)
				elements.append(struct)
				if child.find('body_declarative_items_ql') is not None:
					self._loop(child.find('body_declarative_items_ql'),struct['childs'])
			
			elif child.tag == 'package_body_declaration':
				package = Extract.getPackage(child,self.prefixClass,lastNode)
				package['comment'] = Extract.getComment(node,i)
				elements.append(package)
				nextNode = child.find('body_declarative_items_ql')
				if nextNode is not None:
					self._loop(nextNode,package['childs'])
					
			elif child.tag == 'package_declaration':
				package = Extract.getPackage(child,self.prefixClass,lastNode)
				package['comment'] = Extract.getComment(node,i)
				package['public'] = []
				package['private'] = []
				elements.append(package)
				if child.find('visible_part_declarative_items_ql') is not None:
					self._loop(child.find('visible_part_declarative_items_ql'),package['public'])
				if child.find('private_part_declarative_items_ql') is not None:
					self._loop(child.find('private_part_declarative_items_ql'),package['private'])
			i+=1
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
			name = ".".join(attrs)
			for pp in pps:
				if name == pp.name and pp.filetype == 'hpp':
					self.includes.append({'name':name,'file':pp.filename})
					isIncluded = True
					break
					
	""" Set namespaces """
	def setNamespaces(self,pps):
		node = self.root.find('context_clause_elements_ql')
		if node is None: return
		for nsNode in node.findall('use_package_clause'):
			attrs = Extract.getRefNames(nsNode)
			name = ".".join(attrs)
			isIncluded = False
			for include in self.includes:
				if name == include['name']:
					nsname = self.prefixClass+(("::"+self.prefixClass).join(attrs))
					self.namespaces.append(nsname)
					isIncluded = True
					break
			if isIncluded == False:
				self.namespaces.append("::".join(attrs))
		
	""" 
	Write result to the c++ file
	"""
	def write(self):
		out = "/*! @file "+self.filename+" */"
		for include in self.includes:
			out += "\n"+Convert.include(include)
		for namespace in self.namespaces:
			out += "\n"+Convert.namespace(namespace)
		out += "\n".join(self.typedefs)+"\n\n"
		out += "\n"+self.writeNested(None,self.elements)
		self.file.write(out)
	
	def writeNested(self,parent,elements):
		out = ''
		for element in elements:
			if len(element['childs']) > 0 or element['type'] == 'package':
				if element['type'] == 'package': out += "namespace "+element['name']+" {\n"
				else: out += "namespace "+self.prefixFunction+element['name']+" {\n"
				out += self.writeNested(element,element['childs'])
				
				if 'private' in element and self.includePrivate: 
					out += self.writeNested(element,element['private'])
				if 'public' in element: 
					out += "\n/*Public starts here...*/\n"
					out += self.writeNested(element,element['public'])
					
				out += "\n}"
			if element['type'] == 'struct':
				out += "\n" + Convert.struct(element) + "\n"
			elif element['type'] == 'function':
				out += "\n" + Convert.function(element,self.prefixFunction) + "\n"
			
		return out