import os,re
from class_convert import Convert
from class_extract import Extract

class PPFile:
	
	def __init__(self,filename,tree,prefixFunction,prefixClass,includePrivate):
		self.root = tree.getroot()
		self.name = self.root.get('def_name')
		self.type = "program"
		self.source = self.root.get('source_file')
		self.filename = filename
		self.filetype = self.filename.split('.')[-1]
		self.file = open(self.filename,"w+")
		self.elements = [] #holds functions, structs and packages
		self.typedefs = []
		self.includes = []
		self.namespaces = []
		self.prefixFunction = prefixFunction
		self.prefixClass = prefixClass
		self.includePrivate = includePrivate
		self.privateUris = []
		
	""" Start parsing tree """
	def parse(self):
		node = self.root.find('unit_declaration_q')
		self._loop(node,self.elements)
		
	""" Recursively loop through each level in the XML-tree """
	def _loop(self,node,elements,parent=None):
		lastNode = None
		
		i = 0
		for child in node:
			element = None
			has_body_declarative_items_ql = False
			if child.tag == 'function_body_declaration' or child.tag == 'procedure_body_declaration':
				element = Extract.getFunction(child,lastNode)
				element['uri'] = child.find('names_ql').find('defining_identifier').get('def')
				has_body_declarative_items_ql = True
			
			elif child.tag == 'procedure_declaration' or child.tag == 'function_declaration':
				element = Extract.getFunctionHead(child,lastNode)
				element['uri'] = child.find('names_ql').find('defining_identifier').get('def')
			
			elif child.tag == 'ordinary_type_declaration':
				element = Extract.getStruct(child,lastNode)
				has_body_declarative_items_ql = True
			
			elif child.tag == 'package_body_declaration':
				element = Extract.getPackage(child,self.prefixClass,lastNode)
				has_body_declarative_items_ql = True
					
			elif child.tag == 'package_declaration':
				element = Extract.getPackage(child,self.prefixClass,lastNode)
				element['public'] = []
				element['private'] = []
				if child.find('visible_part_declarative_items_ql') is not None:
					self._loop(child.find('visible_part_declarative_items_ql'),element['public'])
				if child.find('private_part_declarative_items_ql') is not None:
					self._loop(child.find('private_part_declarative_items_ql'),element['private'])
					
			elif child.tag == 'package_renaming_declaration':
				element = Extract.getRename(child)
				
			if element is not None:
				element['comment'] = Extract.getComment(node,i)
				elements.append(element)
				if has_body_declarative_items_ql and child.find('body_declarative_items_ql') is not None:
					self._loop(child.find('body_declarative_items_ql'),element['childs'])
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
				
	def setPrivates(self,pps):
		if self.filetype == 'hpp': return
		hpp = None
		for pp in pps:
			if self.name == pp.name and pp.filetype == 'hpp': hpp = pp
		if hpp is None:
			print "Warning, no header-file for '"+self.name+"' found. Assuming all members to be public"
			return
		self.setPrivatesRecursive(self.elements,hpp)
		
	def setPrivatesRecursive(self,elements,hpp):
		for el in elements:
			if 'childs' in el: self.setPrivatesRecursive(el['childs'],hpp)
			el['is_private'] = self.isPrivate(el,hpp.root)
			if el['is_private']:
				el['comment'] = ' <b>PRIVATE</b><br/>'+el['comment']
			
	def isPrivate(self,el,hppRoot):
		if 'uri' not in el: return False
		
		p = re.compile('^(ada:\/\/[^\/]+)(_body)(.*)$')
		m = p.match(el['uri'])
		
		if m is False: print "Warning, wierd uri: "+el['uri']
		
		uri = m.group(1)+m.group(3)		
		nodes = hppRoot.iter('private_part_declarative_items_ql')
		
		for node in nodes:
			tmpNode = node.find('.//defining_identifier')
			if tmpNode is not None:
				if uri == tmpNode.get('def'):
					return True
		return False
		
	def isPrivateElement(self,element):
		if 'is_private' in element: return element['is_private']
		return False
			
	""" 
	Write result to the c++ file
	"""
	def write(self):
		out = "/*! @file "+os.path.split(self.filename)[1]+" */"
		for include in self.includes:
			out += "\n"+Convert.include(include)
		for namespace in self.namespaces:
			out += "\n"+Convert.namespace(namespace)
		out += "\n".join(self.typedefs)+"\n\n"
		out += "\n"+self.writeNested(None,self.elements)
		self.file.write(out)
		self.file.close()
	
	def writeNested(self,parent,elements):
		out = ''
		for element in elements:
			if self.includePrivate or self.isPrivateElement(element) is False:
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
				if element['type'] == 'enum':
					out += "\n" + Convert.enum(element) + "\n"
				if element['type'] == 'rename':
					out += "\n" + Convert.rename(element) + "\n"
				elif element['type'] == 'function':
					out += "\n" + Convert.function(element,self.prefixFunction) + "\n"
				
		return out