import os,re,logging
from convert import Convert
from extract import Extract

class PPFile:
	
	def __init__(self,filename,sourcefile,tree,prefixFunction,prefixClass,prefixRepClause,hideRepClause,extractAll,extractPriv,hideUndocPkgs):
		self.root = tree.getroot()
		self.name = self.root.get('def_name')
		
		self.filename = filename
		self.filetype = self.filename.split('.')[-1]
		if self.filetype == 'adb':self.filetype = 'cpp'
		elif self.filetype == 'ads':self.filetype = 'hpp'
		
		self.file = open(self.filename,"w+")
		self.sourcefile = sourcefile
		
		## List of dictionaries with extracted info about functions, structs, packages etc...
		self.elements = [] 
		
		## Some elements (functions) is stored with uri as index
		self.elementsByUris = {}
		
		self.includes = []
		self.namespaces = []
		self.imports = []
		self.prefixFunction = prefixFunction
		self.prefixClass = prefixClass
		self.prefixRepClause = prefixRepClause
		self.hideRepClause = hideRepClause
		self.extractAll = extractAll
		self.extractPriv = extractPriv
		self.hideUndocPkgs = hideUndocPkgs
		self.privateUris = []

	## Start parsing the XML tree
	def parse(self):
		node = self.root.find('unit_declaration_q')
		self.parseRecursive(node,self.elements)
				
	## Recursively loop through each level in the XML-tree
	#  To print more information about unparsed elements, change the last elif-statement
	def parseRecursive(self,node,elements,parent=None,isPrivate=False):
		lastNode = None
		
		i = 0
		for child in node:
			element = None
			has_body_declarative_items_ql = False
			if child.tag in ['procedure_body_declaration','function_body_declaration']:
				element = Extract.getFunction(child,lastNode,self.sourcefile)
			elif child.tag in ['function_declaration','generic_function_declaration','procedure_declaration','generic_procedure_declaration','single_task_declaration','task_type_declaration','protected_type_declaration','single_protected_declaration']:
				element = Extract.getFunctionHead(child,lastNode,self.sourcefile,self.extractPriv)
			elif child.tag in ['ordinary_type_declaration','subtype_declaration','private_type_declaration']:
				element = self.parseType(child,lastNode,isPrivate,node)
			elif child.tag in ['component_declaration']:
				element = Extract.getRecordComponent(child,self.sourcefile)
			elif child.tag == 'package_body_declaration':
				element = Extract.getPackage(child,self.prefixClass,lastNode)
			elif child.tag in ['generic_package_declaration','package_declaration']:
				element = self.parsePackage(child,lastNode,isPrivate)
			elif child.tag == 'package_renaming_declaration':
				element = Extract.getRename(child)
			elif child.tag in ['attribute_definition_clause','record_representation_clause','enumeration_representation_clause'] and self.hideRepClause is False:
				element = Extract.getRepClause(child,self.prefixRepClause,self.sourcefile)
			elif child.tag in ['import_pragma']:
				self.imports.append(Extract.getImport(child,self.sourcefile))
			elif child.tag not in ['implementation_defined_pragma']: 
				logging.info("Not parsed: "+child.tag)
				
			if element is not None:
				if parent is None: 
					c = Extract.getUnitComment(self.root)
				else: 
					c = Extract.getComment(node,i) 
				element['comment'] = c
				element['is_private'] = isPrivate
				element['is_extract'] = c != '' or self.extractAll or parent == None
				
				if 'uri' in element: self.elementsByUris[element['uri']] = element
				elements.append(element)
				if element['has_childs'] and child.find('body_declarative_items_ql') is not None:
					isPrivateSubLevel = isPrivate
					if element['type'] == 'function': 
						isPrivateSubLevel = True
					self.parseRecursive(child.find('body_declarative_items_ql'),element['childs'],child,isPrivateSubLevel)
	
			i+=1
			lastNode = child
			
	## Parse a package
	def parsePackage(self,child,lastNode,isPrivate):
		
		element = Extract.getPackage(child,self.prefixClass,lastNode)
		element['has_childs'] = False
		element['public'] = []
		element['private'] = []
		if child.find('visible_part_declarative_items_ql') is not None:
			self.parseRecursive(child.find('visible_part_declarative_items_ql'),element['public'],child,isPrivate)
		if child.find('private_part_declarative_items_ql') is not None:
			self.parseRecursive(child.find('private_part_declarative_items_ql'),element['private'],child,True)
		return element
		
	## Parse a type
	def parseType(self,child,lastNode,isPrivate,nodes):
		if child.tag == 'private_type_declaration' and self.extractPriv:
			return None
		recNode = Extract.getRecordNode(child)
		if recNode is None:
			element = Extract.getType(child,self.sourcefile)
		else:
			element = Extract.getRecord(child)
			self.parseRecursive(recNode,element['components'],child,isPrivate)
		return element
					
	## Set namespaces
	def setNamespaces(self):
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
				
	def getElementByUri(self,uri):
		if uri in self.elementsByUris: return self.elementsByUris[uri]
		uri2 = uri.replace("ada://function","ada://generic_function")
		uri2 = uri2.replace("ada://procedure","ada://generic_procedure")
		if uri2 in self.elementsByUris: return self.elementsByUris[uri2]
		return None

	def isPrivateElement(self,element):
		if 'is_private' in element: return element['is_private']
		return False
			
	## Write result to the c++ file
	def write(self):
		logging.debug("Creating "+self.name+"...")
		out = "/*! @file "+os.path.split(self.filename)[1]+" */"
		for include in self.includes:
			out += "\n"+Convert.include(include)
		for namespace in self.namespaces:
			out += "\n"+Convert.namespace(namespace)
		out += "\n"+self.writeRecursive(None,self.elements)
		self.file.write(out)
		self.file.close()
	
	## Get number of visible childs, if EXTRACT_PRIVATE=YES, then the result will be len(childs)
	def getNrVisibleChilds(self,childs):
		if self.extractPriv: return len(childs)
		nr = 0
		for child in childs:
			if child['is_private']: nr += 1
		return nr
	
	## Write result to the c++ file recursively
	def writeRecursive(self,parent,elements):
		out = ''
		for element in elements:
			if element['type'] == 'package':
				out += self.writePackage(element)
			elif self.getNrVisibleChilds(element['childs']) > 0 and self.extractPriv:
				out += "namespace "+self.prefixFunction+element['name']+" {\n"
				out += self.writeRecursive(element,element['childs'])
				out += "\n}"
				
			element['comment_add_private'] = self.isPrivateElement(element)

			if element['type'] == 'record':
				out += "\n" + Convert.record(element,self.extractAll,self.extractPriv) + "\n"
			if element['type'] == 'type':
				out += "\n" + Convert.type(element,self.extractAll,self.extractPriv) + "\n"
			if element['type'] == 'rep_clause':
				out += "\n" + Convert.type(element,self.extractAll,self.extractPriv) + "\n"
			if element['type'] == 'rename':
				out += "\n" + Convert.rename(element) + "\n"
			elif element['type'] == 'function': 
				out += "\n" + Convert.function(element,self.prefixFunction,self.extractAll) + "\n"
			
		return out
		
	## Write a package to file
	def writePackage(self,element):
		out = ''
		comment = element['comment']
		if comment == '' and (self.hideUndocPkgs is False):
			comment = "<b style='display:none;'>HIDE_UNDOC_CLASSES=NO</b>"
		out += Convert.comment(comment)
		out += "namespace "+element['name']+" {\n"
		if 'private' in element: 
			out += self.writeRecursive(element,element['private'])
		if 'public' in element: 
			out += "\n/*Public starts here...*/\n"
			out += self.writeRecursive(element,element['public'])
		out += self.writeRecursive(element,element['childs'])
		out += "\n}"
		return out
		
	