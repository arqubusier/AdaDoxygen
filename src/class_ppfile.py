import os,re
from class_convert import Convert
from class_extract import Extract

class PPFile:
	
	def __init__(self,filename,sourcefile,tree,prefixFunction,prefixClass,doxyReader):
		self.root = tree.getroot()
		self.name = self.root.get('def_name')
		self.type = "program"
		self.source = self.root.get('source_file')
		
		self.filename = filename
		self.filetype = self.filename.split('.')[-1]
		if self.filetype == 'adb':self.filetype = 'cpp'
		elif self.filetype == 'ads':self.filetype = 'hpp'
		
		self.file = open(self.filename,"w+")
		self.sourcefile = sourcefile
		self.elements = [] #holds functions, structs and packages
		self.elementsByUris = {}
		self.typedefs = []
		self.includes = []
		self.namespaces = []
		self.prefixFunction = prefixFunction
		self.prefixClass = prefixClass
		self.doxyReader = doxyReader
		self.privateUris = []
		
	""" Start parsing tree """
	def parse(self):
		node = self.root.find('unit_declaration_q')
		self._loop(node,self.elements)
				
	""" Recursively loop through each level in the XML-tree """
	def _loop(self,node,elements,parent=None,isPrivate=False):
		lastNode = None
		
		i = 0
		for child in node:
			element = None
			has_body_declarative_items_ql = False
			if child.tag == 'function_body_declaration' or child.tag == 'procedure_body_declaration':
				element = Extract.getFunction(child,lastNode)
				element['uri'] = child.find('names_ql').find('defining_identifier').get('def')
				has_body_declarative_items_ql = True
			
			elif child.tag in ['function_declaration','generic_function_declaration','procedure_declaration']:
				element = Extract.getFunctionHead(child,lastNode)
				element['uri'] = child.find('names_ql').find('defining_identifier').get('def')
			
			elif child.tag == 'ordinary_type_declaration':
				element = Extract.getStruct(child,lastNode)
				if element is not None: has_body_declarative_items_ql = True
				else: element = Extract.getType(child,self.sourcefile)
			
			elif child.tag == 'package_body_declaration':
				element = Extract.getPackage(child,self.prefixClass,lastNode)
				has_body_declarative_items_ql = True
					
			elif child.tag == 'package_declaration':
				element = Extract.getPackage(child,self.prefixClass,lastNode)
				element['public'] = []
				element['private'] = []
				if child.find('visible_part_declarative_items_ql') is not None:
					self._loop(child.find('visible_part_declarative_items_ql'),element['public'],child,isPrivate)
				if child.find('private_part_declarative_items_ql') is not None:
					self._loop(child.find('private_part_declarative_items_ql'),element['private'],child,True)
					
			elif child.tag == 'package_renaming_declaration':
				element = Extract.getRename(child)
				
			if element is not None:
				if parent is None: c = Extract.getUnitComment(self.root)
				else: c = Extract.getComment(node,i)
				element['comment'] = c
				element['is_private'] = isPrivate
				element['is_extract'] = c != '' or self.doxyReader.extract_all_bool or parent == None
				
				if 'uri' in element: self.elementsByUris[element['uri']] = element
				
				elements.append(element)
				if has_body_declarative_items_ql and child.find('body_declarative_items_ql') is not None:
					if element['type'] == 'function': 
						isPrivate = True
					self._loop(child.find('body_declarative_items_ql'),element['childs'],child,isPrivate)
	
				
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
				
	""" Get and set function declaration from hpp to cpp file """
	def setFunctionHeads(self,pps):
		if self.filetype == 'hpp': return
		hpp = None
		for pp in pps:
			if self.name == pp.name and pp.filetype == 'hpp': hpp = pp
		if hpp is None:
			print "Warning, no header-file for '"+self.name+"' found."
			return
		self.setFunctionHeadsRecursive(self.elements,hpp)
	
	def setFunctionHeadsRecursive(self,elements,hpp):
		for el in elements:
			if 'childs' in el: self.setFunctionHeadsRecursive(el['childs'],hpp)
			if 'public' in el: self.setFunctionHeadsRecursive(el['public'],hpp)
			if 'private' in el: self.setFunctionHeadsRecursive(el['private'],hpp)
			
			if el['type'] == 'function':
				uri = self.cppToHppUri(el['uri'])
				if uri is None:
					print("Couldnt convert URI")
					return
				el_hpp = hpp.getElementByUri(uri)
				if el_hpp is None:
					print("Warning: Couldnt find hpp-element")
				el['function_head'] = Convert.functionHead(el_hpp)
				
	def getElementByUri(self,uri):
		if uri in self.elementsByUris: return self.elementsByUris[uri]
		return None
		
	def cppToHppUri(self,uri):
		p = re.compile('^(ada:\/\/[^\/]+)(_body)(.*)$')
		m = p.match(uri)
		if m is False: print "Warning, wierd uri: "+uri
		return (m.group(1)+m.group(3))
		
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
		out += "/* \\defgroup types AdaTypes */\n"
		out += "\n"+self.writeNested(None,self.elements)
		self.file.write(out)
		self.file.close()
	
	def getNrVisibleChilds(self,childs):
		if self.doxyReader.include_private_bool: return len(childs)
		nr = 0
		for child in childs:
			if child['is_private']: nr += 1
		return nr
	
	def writeNested(self,parent,elements):
		out = ''
		for element in elements:
			if element['type'] == 'package':
				comment = element['comment']
				if comment == '' and (self.doxyReader.hideundoc_classes is False):
					comment = "<b style='display:none;'>HIDE_UNDOC_CLASSES=NO</b>"
				out += Convert.comment(comment)
				out += "namespace "+element['name']+" {\n"
				if 'private' in element: 
					out += self.writeNested(element,element['private'])
				if 'public' in element: 
					out += "\n/*Public starts here...*/\n"
					out += self.writeNested(element,element['public'])
				out += self.writeNested(element,element['childs'])
				out += "\n}"
				
			elif self.getNrVisibleChilds(element['childs']) > 0 and self.doxyReader.include_private_bool:
				out += "namespace "+self.prefixFunction+element['name']+" {\n"
				out += self.writeNested(element,element['childs'])
				out += "\n}"
				
			element['comment_add_private'] = self.isPrivateElement(element) and self.filetype == 'hpp'
				
			if element['type'] == 'struct':
				out += "\n" + Convert.struct(element,self.doxyReader.extract_all_bool) + "\n"
			if element['type'] == 'type':
				out += "\n" + Convert.type(element,self.doxyReader.extract_all_bool) + "\n"
			if element['type'] == 'rename':
				out += "\n" + Convert.rename(element) + "\n"
			elif element['type'] == 'function':
				out += "\n" + Convert.function(element,self.prefixFunction,self.doxyReader.extract_all_bool) + "\n"
			
		return out