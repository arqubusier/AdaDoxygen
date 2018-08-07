from class_pptuple import PPTuple

class PPList:

	def __init__(self):
		self.ppobjects = []
		self.tuples = []
		
	def add(self,pp):
		self.ppobjects.append(pp)
	
	""" Set valid includes when all files have been parsed """
	def collectIncludes(self):
		for pp in self.ppobjects:
			node = pp.root.find('context_clause_elements_ql')
			if node is None: return

			for withNode in node.findall('with_clause'):
				idNodes = withNode.iter('identifier')
				attrs = []
				for idNode in idNodes:
					attrs.append(idNode.get('ref_name'))
				name = ".".join(attrs)
				for pp2 in self.ppobjects:
					if name == pp2.name and pp2.filetype == 'hpp':
						pp.includes.append({'name':name,'file':pp2.filename})
						break
						
	""" Set namespaces """
	def setNamespaces(self):
		for pp in self.ppobjects:
			pp.setNamespaces()
		
	""" Build tuples with matching cpp and hpp files """
	def buildTuples(self):
		for hpp in self.ppobjects:
			if hpp.filetype == 'hpp':
				cpp = None
				for cpp_tmp in self.ppobjects:
					if cpp_tmp.filetype == 'cpp' and cpp_tmp.name == hpp.name:
						cpp = cpp_tmp
						break

				if cpp is None:
					print "Warning, no source-file for '"+hpp.name+"' found."
				else:
					self.tuples.append(PPTuple(hpp,cpp))
	
	def moveGenericFunctionBodies(self):
		for tuple in self.tuples:
			tuple.moveGenericFunctionBodiesRecursive(tuple.cpp.elements)
			
	def exchangePrivateInfo(self):
		for tuple in self.tuples:
			tuple.exchangePrivateInfoRecursive(tuple.cpp.elements)
			
	def write(self):
		for pp in self.ppobjects:
			pp.doxyReader.printt( "Creating "+pp.name+"..." )
			pp.write()