
class CppFile:
	
	PRIMITIVES = {
		"Integer" : "int",
		"Float" : "float",
		"void" : "void"
	}
	
	def __init__(self,filename):
		self.filename = filename
		self.file = open("cpp/"+filename,"w+")
		self.elements = [] #holds functions and structs
		self.typedefs = []
		
	""" Recursively loop through each level in the XML-tree """
	def loop(self,node,elements):
		lastNode = None
		for child in node:
			if child.tag == 'function_body_declaration' or child.tag == 'procedure_body_declaration':
				function = self.getFunction(child,lastNode)
				elements.append(function)
				if child.find('body_declarative_items_ql') is not None:
					self.loop(child.find('body_declarative_items_ql'),function['childs'])
			elif child.tag == 'ordinary_type_declaration':
				struct = self.getStruct(child,lastNode)
				elements.append(struct)
				if child.find('body_declarative_items_ql') is not None:
					self.loop(child.find('body_declarative_items_ql'),struct['childs'])
			lastNode = child
			
	""" 
	The functions below extracts the relevant XML-data and returns Python dictionaries
	"""
	def getStruct(self, structNode, commentNode):
		struct = {}
		struct['type'] = 'struct'
		struct['name'] = self.getName(structNode)
		struct['props'] = []
		struct['childs'] = []
		tmpNode = structNode.find('type_declaration_view_q').find('record_type_definition').find('record_definition_q').find('record_definition').find('record_components_ql')
		for propNode in tmpNode.findall('component_declaration'):
			prop = {}
			prop['name'] = self.getName(propNode)
			prop['type'] = propNode.find('object_declaration_view_q').find('component_definition').find('component_definition_view_q').find('subtype_indication').find('subtype_mark_q').find('identifier').get('ref_name')
			prop['type'] = self.convertPrimitive(prop['type'])
			struct['props'].append(prop)
		struct['comment'] = self.getComment(commentNode)
		return struct

	def getFunction(self, functionNode, commentNode):
		function = {}
		function['type'] = 'function'
		function['name'] = self.getName(functionNode)
		function['params'] = []
		function['body'] = {}
		function['body']['variables'] = self.getVariables(functionNode.find('body_declarative_items_ql').findall('variable_declaration'))
		function['body']['calls'] = self.getCalls(functionNode.find('body_statements_ql'))
		function['childs'] = []
		for paramNode in functionNode.find('parameter_profile_ql').findall('parameter_specification'):
			param = {}
			param['name'] = self.getName(paramNode)
			param['type'] = self.convertPrimitive(paramNode.find('object_declaration_view_q').find('identifier').get('ref_name'))
			function['params'].append(param)
		if functionNode.find('result_profile_q') is None:
			function['output'] = 'void'
		else:
			function['output'] = self.convertPrimitive(functionNode.find('result_profile_q').find('identifier').get('ref_name'))
		function['comment'] = self.getComment(commentNode)
		return function
	
	def getName(self,node):
		return node.find('names_ql').find('defining_identifier').get('def_name')
		
	def getComment(self,commentNode):
		if commentNode is None: return ''
		if commentNode.tag != 'implementation_defined_pragma': return ''
		if commentNode.get('pragma_name') != 'Comment': return ''
		return commentNode.find('pragma_argument_associations_ql').find('pragma_argument_association').find('actual_parameter_q').find('string_literal').get('lit_val')
	
	def getVariables(self,varNodes):
		vars = []
		for varNode in varNodes:
			var = {}
			var['name'] = self.getName(varNode)
			var['type'] = varNode.find('object_declaration_view_q').find('subtype_indication').find('subtype_mark_q').find('identifier').get('ref_name')
			var['type'] = self.convertPrimitive(var['type'])
			vars.append(var)
		return vars;
	
	def getCalls(self,bodyNodes):
		calls = []
		for child in bodyNodes:
			if child.tag == 'procedure_call_statement':
				calls.append({
					'name' : child.find('called_name_q').find('identifier').get('ref_name'),
					'params' : self.getArgs(child.find('call_statement_parameters_ql').findall('parameter_association')),
					'is_void' : True
				})
			elif child.tag == 'function_call':
				if child.find('prefix_q') is not None and child.find('prefix_q').find('identifier') is not None:
					calls.append({
						'name' : child.find('prefix_q').find('identifier').get('ref_name'),
						'params' : self.getArgs(child.find('function_call_parameters_ql').findall('parameter_association')),
						'is_void' : False
					})
			calls = calls + self.getCalls(child)
		return calls
		
	def getArgs(self,argNodes):
		args = []
		for argNode in argNodes:
			arg = argNode.find('actual_parameter_q')[0].get('lit_val')
			if arg is not None: args.append(arg)
			else:
				arg = argNode.find('actual_parameter_q')[0].get('ref_name')
				if arg is not None: args.append(arg)
		return args
	
	""" 
	The functions below converts the dictionary data to c++ code 
	"""
	def convertStruct(self,struct):
		out = self.convertComment(struct['comment'])
		out += "struct "+struct['name']+"{\n"
		for prop in struct['props']:
			out += "\t"+prop['type']+" "+prop['name']+";\n"
		out += "};"
		return out
	
	def convertFunction(self,function):
		out = self.convertComment(function['comment'])
		out += function['output'] + " " + function['name']
		out += " ("+self.convertParams(function['params'])+") {\n"
		for var in function['body']['variables']:
			out += var['type'] + " " + var['name'] + ";\n"
		for call in function['body']['calls']:
			if call['is_void'] is False: out += "(void)"
			out += call['name']+"("+(",".join(call['params']))+");\n"
		out += "\n}"
		return out
		
	def convertPrimitive(self,type):
		#check for primitive key-value pair
		if type in self.PRIMITIVES.keys(): 
			return self.PRIMITIVES[type]
		
		#otherwise, add typedef if not exists
		typedef = "unsigned int "+type+";"
		if typedef not in self.typedefs:
			print typedef
			self.typedefs.append(typedef)
		return type
		
	def convertParams(self,params):
		paramStrings = []
		for p in params:
			paramStrings.append(p['type']+" "+p['name'])
		return (", ".join(paramStrings))
	
	def convertComment(self, comment):
		out = ''
		if comment != '': out += "/*! "+comment.strip('"')+" */\n"
		return out
	
	""" 
	Write result to the c++ file
	"""
	def write(self):
		out = "/*! @file "+self.filename+" */\n\n"
		print self.typedefs
		out += "\n".join(self.typedefs)
		out += "\n"+self.writeNested(None,self.elements)
		self.file.write(out)
		
	def writeNested(self,parent,elements):
		out = ''
		for element in elements:
			if element['type'] == 'struct':
				out += "\n" + self.convertStruct(element) + "\n"
			elif element['type'] == 'function':
				out += "\n" + self.convertFunction(element) + "\n"
			if len(element['childs']) > 0:
				out += "namespace "+element['name']+" {\n"
				out += self.writeNested(element,element['childs'])
				out += "\n}"
		return out