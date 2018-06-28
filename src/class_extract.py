""" 
The static methods below extracts data from XML-nodes into dictionaries
"""
class Extract:

	@staticmethod
	def getPackage(packNode,prefix, commentNode):
		elem = Extract.getPackageHead(packNode,prefix,commentNode)
		return elem
		
	@staticmethod
	def getPackageHead(packNode,prefix, commentNode):
		elem = {}
		elem['type'] = 'package'
		elem['name'] = Extract.getPackageName(packNode,prefix)
		elem['childs'] = []
		return elem
		
	@staticmethod
	def getStruct(structNode, commentNode):
		elem = {}
		elem['type'] = 'struct'
		elem['name'] = Extract.getName(structNode)
		elem['props'] = []
		elem['childs'] = []
		tmpNode = structNode.find('type_declaration_view_q').find('record_type_definition')
		if tmpNode is not None:
			tmpNode = tmpNode.find('record_definition_q').find('record_definition').find('record_components_ql')
			for propNode in tmpNode.findall('component_declaration'):
				prop = {}
				prop['name'] = Extract.getName(propNode)
				prop['type'] = propNode.find('object_declaration_view_q').find('component_definition').find('component_definition_view_q').find('subtype_indication').find('subtype_mark_q').find('identifier').get('ref_name')
				elem['props'].append(prop)
		else: return None
		return elem
	
	@staticmethod
	def getType(typeNode,sourcefile):
		elem = {}
		elem['type'] = 'type'
		elem['name'] = Extract.getName(typeNode)
		elem['childs'] = []
		elem['plain'] = Extract.getPlaintext(sourcefile,typeNode)
		return elem
	
	@staticmethod
	def getPlaintext(file,node):
		sloc = node.find('sloc')
		
		startline = int(sloc.get('line'))
		startcol = int(sloc.get('col'))
		endline = int(sloc.get('endline'))
		endcol = int(sloc.get('endcol'))
		
		fh = open(file)
		i_line = 1
		plain = ""
		for line in fh:
			if i_line >= startline and i_line <= endline:
				str = line.strip("\r")
				i_col = 1
				for c in str:
					if i_col >= startcol and i_col <= endcol:
						plain += c
					i_col += 1
			i_line += 1
		return plain
		
	@staticmethod
	def getFunction(functionNode, commentNode):
		elem = Extract.getFunctionHead(functionNode,commentNode)
		elem['body'] = {}
		elem['body']['variables'] = Extract.getVariables(functionNode.find('body_declarative_items_ql').findall('variable_declaration'))
		elem['body']['calls'] = Extract.getCalls(functionNode.find('body_statements_ql'))
		return elem
	
	@staticmethod
	def getFunctionHead(functionNode, commentNode):
		elem = {}
		elem['type'] = 'function'
		elem['name'] = Extract.getName(functionNode)
		elem['params'] = []
		elem['childs'] = []
		for paramNode in functionNode.find('parameter_profile_ql').findall('parameter_specification'):
			param = {}
			param['name'] = Extract.getName(paramNode)
			attrs = Extract.getRefNames(paramNode.find('object_declaration_view_q'))
			param['type'] = "::".join(attrs)
			elem['params'].append(param)
		if functionNode.find('result_profile_q') is None:
			elem['output'] = 'void'
		else:
			attrs = Extract.getRefNames(functionNode.find('result_profile_q'))
			output = "::".join(attrs)
			elem['output'] = output
		#elem['comment'] = Extract.getComment(commentNode)
		return elem
	
	@staticmethod
	def getName(node):
		return node.find('names_ql').find('defining_identifier').get('def_name')
		
	@staticmethod
	def getPackageName(node,prefix):
		if node.find('names_ql').find('defining_identifier') is not None:
			return prefix+Extract.getName(node)
		refNames = Extract.getRefNames(node.find('names_ql'))
		refNames.append(node.find('names_ql').find('defining_expanded_name').get('def_name'))
		for i,refName in enumerate(refNames):
			refNames[i] = prefix+refName
		return "::".join(refNames)
		
	@staticmethod
	def getRename(node):
		elem = {}
		elem['type'] = 'rename'
		elem['name'] = Extract.getName(node)
		elem['package_names'] = Extract.getRefNames(node.find('renamed_entity_q'))
		elem['childs'] = []
		return elem
		
	@staticmethod
	def getComment(nodes,i):
		i2 = 0
		for child in nodes:
			if i2 == (i-1):
				comment = Extract.getCommentAbove(child)
				if comment != '': return comment
			if i2 == (i+1):
				comment = Extract.getCommentBelow(child)
				if comment != '': return comment
			i2 +=1
		return ''
	
	@staticmethod
	def getCommentAbove(commentNode):
		comment = Extract.getCommentValue(commentNode)
		if comment == '': return ''
		if comment[:2] == '"<': return ''
		else: return comment
	
	@staticmethod
	def getCommentBelow(commentNode):
		comment = Extract.getCommentValue(commentNode)
		if comment == '': return ''
		if comment[:2] == '"<': return comment[2:]
		else: return ''
	
	@staticmethod
	def getCommentValue(commentNode):
		if commentNode is None: return ''
		if commentNode.tag != 'implementation_defined_pragma': return ''
		if commentNode.get('pragma_name') != 'Comment': return ''
		comment = commentNode.find('pragma_argument_associations_ql').find('pragma_argument_association').find('actual_parameter_q').find('string_literal').get('lit_val')
		return comment.strip('"')
		
	@staticmethod
	def getVariables(varNodes):
		vars = []
		for varNode in varNodes:
			var = {}
			var['name'] = Extract.getName(varNode)
			var['type'] = varNode.find('object_declaration_view_q').find('subtype_indication').find('subtype_mark_q').find('identifier').get('ref_name')
			vars.append(var)
		return vars;
	
	@staticmethod
	def getCalls(bodyNodes):
		calls = []
		for child in bodyNodes:
			if child.tag == 'procedure_call_statement':
				calls.append({
					'name' : Extract.getCallName(child.find('called_name_q')),
					'params' : Extract.getArgs(child.find('call_statement_parameters_ql').findall('parameter_association')),
					'is_void' : True
				})
			elif child.tag == 'function_call' and Extract.getCallName(child.find('prefix_q')) != '':
				calls.append({#child.find('prefix_q').find('identifier').get('ref_name')
					'name' : Extract.getCallName(child.find('prefix_q')),
					'params' : Extract.getArgs(child.find('function_call_parameters_ql').findall('parameter_association')),
					'is_void' : False
				})
			calls = calls + Extract.getCalls(child)
		return calls
	
	@staticmethod
	def getCallName(callNode): #called_name_q
		if callNode.find('identifier') is not None: return callNode.find('identifier').get('ref_name')
		nodes = callNode.iter('identifier')
		attrs = []
		for idNode in nodes:
			attrs.append(idNode.get('ref_name'))
		return "::".join(attrs) 
		
	@staticmethod
	def getArgs(argNodes):
		args = []
		for argNode in argNodes:
			arg = argNode.find('actual_parameter_q')[0].get('lit_val')
			if arg is not None: args.append(arg)
			else:
				arg = argNode.find('actual_parameter_q')[0].get('ref_name')
				if arg is not None: args.append(arg)
		return args
		
	""" Iterate identifiers and return all ref-name attributes """
	@staticmethod
	def getRefNames(node):
		nodes = node.iter('identifier')
		attrs = []
		for idNode in nodes:
			attrs.append(idNode.get('ref_name'))
		return attrs
		
	
	