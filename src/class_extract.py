""" 
The static methods below extracts data from XML-nodes into dictionaries
"""
class Extract:

	@staticmethod
	def getPackage(packNode,prefix, commentNode):
		elem = Extract.getPackageHead(packNode,prefix,commentNode)
		elem['has_childs'] = True
		return elem
		
	@staticmethod
	def getPackageHead(packNode,prefix, commentNode):
		elem = {}
		elem['type'] = 'package'
		elem['name'] = Extract.getPackageName(packNode,prefix)
		elem['childs'] = []
		return elem
		
	@staticmethod
	def getStruct(structNode, commentNode, sourcefile):
		elem = {}
		elem['type'] = 'struct'
		elem['name'] = Extract.getName(structNode)
		elem['props'] = []
		elem['childs'] = []
		elem['has_childs'] = True
		tmpNode = structNode.find('type_declaration_view_q/record_type_definition/record_definition_q/record_definition/record_components_ql')
		if tmpNode is not None:
			tmpNode = tmpNode.find('record_definition_q').find('record_definition').find('record_components_ql')
			for propNode in tmpNode.findall('component_declaration'):
				prop = {}
				prop['name'] = Extract.getName(propNode)
				tmpNode2 = propNode.find('object_declaration_view_q/component_definition/component_definition_view_q/subtype_indication/subtype_mark_q/identifier')
				if tmpNode2 is not None: prop['type'] = tmpNode2.get('ref_name')
				else: prop['type'] = 'unknown_type_adadoxygen'
				elem['props'].append(prop)
			return elem
		else: 
			return Extract.getType(structNode,sourcefile)
			
			
	@staticmethod
	def getRecordNode(node):
		return node.find('type_declaration_view_q/record_type_definition/record_definition_q/record_definition/record_components_ql')
	
	@staticmethod
	def getRecord(node):
		elem = {}
		elem['type'] = 'record'
		elem['name'] = Extract.getName(node)
		elem['childs'] = []
		elem['components'] = []
		elem['has_childs'] = False
		return elem
		
	@staticmethod
	def getRecordComponent(node,sourcefile):
		elem = {}
		elem['name'] = Extract.getName(node)
		elem['has_childs'] = False
		elem['plain'] = Extract.getPlaintext(sourcefile,node)
		tmpNode = node.find('object_declaration_view_q/component_definition/component_definition_view_q/subtype_indication/subtype_mark_q/identifier')
		if tmpNode is not None: 
			elem['type'] = tmpNode.get('ref_name')
		else: 
			prop['type'] = 'unknown_type_adadoxygen'
		return elem

	
	@staticmethod
	def getType(typeNode,sourcefile):
		elem = {}
		elem['type'] = 'type'
		elem['has_childs'] = False
		elem['name'] = Extract.getName(typeNode)
		elem['childs'] = []
		elem['plain'] = Extract.getPlaintext(sourcefile,typeNode)
		return elem
		
	@staticmethod
	def getRepClause(repNode, prefixRepClause, sourcefile):
		elem = {}
		elem['name'] = Extract.getRepClauseName(repNode,prefixRepClause)
		print(elem['name'])
		elem['type'] = 'rep_clause'
		elem['has_childs'] = False
		elem['childs'] = []
		elem['plain'] = Extract.getPlaintext(sourcefile,repNode)
		return elem
		
	@staticmethod
	def getRepClauseName(node,prefixRepClause):
		nameNode = node.find('representation_clause_name_q')
		tmpNodes = nameNode.iter('identifier')
		name_parts = []
		for tmpNode in tmpNodes:
			name_parts.append(tmpNode.get('ref_name'))
		return prefixRepClause+("_".join(name_parts))
	
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
				#str = line.strip("\r")
				str = line
				i_col = 1
				for c in str:
					if (i_col >= startcol or i_line > startline) and (i_col <= endcol or i_line < endline):
						plain += c
					i_col += 1
			i_line += 1
		return plain
		
	@staticmethod
	def getFunction(functionNode, commentNode, sourcefile):
		elem = Extract.getFunctionHead(functionNode,commentNode,sourcefile)
		elem['has_childs'] = True
		elem['body'] = {}
		elem['body']['variables'] = Extract.getVariables(functionNode.find('body_declarative_items_ql').findall('variable_declaration'))
		elem['body']['calls'] = Extract.getCalls(functionNode.find('body_statements_ql'))
		return elem
	
	@staticmethod
	def getFunctionHead(functionNode, commentNode, sourcefile):
		elem = {}
		genNode = functionNode.find('generic_formal_part_ql')
		if genNode is not None:
			elem['generic'] = Extract.getGeneric(genNode,sourcefile)
		elem['uri'] = functionNode.find('names_ql').find('defining_identifier').get('def')
		elem['type'] = 'function'
		elem['name'] = Extract.getName(functionNode)
		elem['params'] = []
		elem['has_childs'] = False
		elem['childs'] = []
		for paramNode in functionNode.findall('parameter_profile_ql/parameter_specification'):
			elem['params'].append(Extract.getFunctionParam(paramNode))
		elem['output'] = Extract.getFunctionOutput(functionNode)
		if functionNode.tag in ['single_task_declaration','task_type_declaration']:
			elem['plain'] = Extract.getPlaintext(sourcefile,functionNode)
		return elem
		
	@staticmethod
	def getFunctionParam(paramNode):
		param = {}
		param['name'] = Extract.getName(paramNode)
		param['dir'] = Extract.getParamDirection(paramNode)
		attrs = Extract.getRefNames(paramNode.find('object_declaration_view_q'))
		param['type'] = "::".join(attrs)
		return param
		
	@staticmethod
	def getFunctionOutput(functionNode):
		if functionNode.find('result_profile_q') is None:
			if functionNode.tag in ['single_task_declaration','task_type_declaration']:
				return 'Task'
			else:
				return 'Procedure'
		attrs = Extract.getRefNames(functionNode.find('result_profile_q'))
		output = "::".join(attrs)
		return output

	
	@staticmethod
	def getParamDirection(paramNode):
		mode = paramNode.get('mode')
		if mode == 'A_DEFAULT_IN_MODE': return 'in'
		elif mode == 'AN_IN_MODE': return 'in'
		elif mode == 'AN_IN_OUT_MODE': return 'inout'
		elif mode == 'AN_OUT_MODE': return 'out'
		else:
			print("Warning: Mode '"+mode+"' not recognized, setting default mode='in'")
			return 'in'
	
	@staticmethod
	def getName(node):
		return node.find('names_ql').find('defining_identifier').get('def_name')
		
	@staticmethod
	def getGeneric(genNode,sourcefile):
		typeNodes = genNode.findall('formal_type_declaration')
		arr = []
		for typeNode in typeNodes:
			arr.append({'name':Extract.getName(typeNode),'plain':Extract.getPlaintext(sourcefile,typeNode)})
		return arr
		
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
		elem['has_childs'] = False
		elem['name'] = Extract.getName(node)
		elem['package_names'] = Extract.getRefNames(node.find('renamed_entity_q'))
		elem['childs'] = []
		return elem
		
	# Look for pragma comments above and below current node, i-1 and i+1
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
		
	# First pragma comment in file is in a different node in the xml-file
	@staticmethod
	def getUnitComment(rootNode):
		tmpNode = rootNode.find('context_clause_elements_ql')
		if tmpNode is None: return ""
		else: return Extract.getCommentValue(tmpNode.find('implementation_defined_pragma'))
		
	@staticmethod
	def getVariables(varNodes):
		vars = []
		for varNode in varNodes:
			var = {}
			var['name'] = Extract.getName(varNode)
			tmpNode = varNode.find('object_declaration_view_q/subtype_indication/subtype_mark_q/identifier')
			if tmpNode is not None: var['type'] = tmpNode.get('ref_name')
			else: var['type'] = 'UNKNOWN_TYPE'
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
		
	
	