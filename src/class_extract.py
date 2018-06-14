""" 
The static methods below extracts data from XML-nodes into dictionaries
"""
class Extract:

	@staticmethod
	def getPackage(packNode, commentNode):
		elem = Extract.getPackageHead(packNode,commentNode)
		return elem
		
	@staticmethod
	def getPackageHead(packNode, commentNode):
		elem['type'] = 'package'
		elem['name'] = Extract.getName(packNode)

		elem['childs'] = []
		
	@staticmethod
	def getStruct(structNode, commentNode):
		elem = {}
		elem['type'] = 'struct'
		elem['name'] = Extract.getName(structNode)
		elem['props'] = []
		elem['childs'] = []
		tmpNode = structNode.find('type_declaration_view_q').find('record_type_definition').find('record_definition_q').find('record_definition').find('record_components_ql')
		for propNode in tmpNode.findall('component_declaration'):
			prop = {}
			prop['name'] = Extract.getName(propNode)
			prop['type'] = propNode.find('object_declaration_view_q').find('component_definition').find('component_definition_view_q').find('subtype_indication').find('subtype_mark_q').find('identifier').get('ref_name')
			elem['props'].append(prop)
		elem['comment'] = Extract.getComment(commentNode)
		return elem
	
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
			param['type'] = paramNode.find('object_declaration_view_q').find('identifier').get('ref_name')
			elem['params'].append(param)
		if functionNode.find('result_profile_q') is None:
			elem['output'] = 'void'
		else:
			elem['output'] = functionNode.find('result_profile_q').find('identifier').get('ref_name')
		elem['comment'] = Extract.getComment(commentNode)
		return elem
	
	@staticmethod
	def getName(node):
		return node.find('names_ql').find('defining_identifier').get('def_name')
		
	@staticmethod
	def getComment(commentNode):
		if commentNode is None: return ''
		if commentNode.tag != 'implementation_defined_pragma': return ''
		if commentNode.get('pragma_name') != 'Comment': return ''
		return commentNode.find('pragma_argument_associations_ql').find('pragma_argument_association').find('actual_parameter_q').find('string_literal').get('lit_val')
	
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
		
	
	