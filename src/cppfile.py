
class CppFile:
	
	#hur gora med "String" : "char[]" ?
	PRIMITIVES = {
		"Integer" : "int",
		"Float" : "float",
		"String" : "char"
	}
	
	def __init__(self,filename):
		self.filename = filename
		self.file = open("cpp/"+filename,"w+")
		self.functions = []
		self.structs = []
	
	def convertPrimitive(self,type):
		if type in self.PRIMITIVES.keys(): return self.PRIMITIVES[type]
		return type
	
	def extractStructs(self, node):
		for structNode in node.findall('ordinary_type_declaration'):
			struct = {}
			struct['name'] = self.getName(structNode)
			struct['props'] = []
			tmpNode = structNode.find('type_declaration_view_q').find('record_type_definition').find('record_definition_q').find('record_definition').find('record_components_ql')
			for propNode in tmpNode.findall('component_declaration'):
				prop = {}
				prop['name'] = self.getName(propNode)
				prop['type'] = propNode.find('object_declaration_view_q').find('component_definition').find('component_definition_view_q').find('subtype_indication').find('subtype_mark_q').find('identifier').get('ref_name')
				struct['props'].append(prop)
			self.structs.append(struct)

	def extractFunctions(self, node):
		for functionNode in (node.findall('function_body_declaration') + node.findall('procedure_body_declaration')):
			function = {}
			function['name'] = self.getName(functionNode)
			function['params'] = []
			for paramNode in functionNode.find('parameter_profile_ql').findall('parameter_specification'):
				param = {}
				param['name'] = self.getName(paramNode)
				param['type'] = paramNode.find('object_declaration_view_q').find('identifier').get('ref_name')
				function['params'].append(param)
			if functionNode.find('result_profile_q') is None:
				function['output'] = 'void'
			else:
				function['output'] = functionNode.find('result_profile_q').find('identifier').get('ref_name')
			self.functions.append(function)
	
	def getName(self,node):
		return node.find('names_ql').find('defining_identifier').get('def_name')
	
	def printFunction(self,function):
		print "Funktion '"+function['name']+"'"
		for param in function['params']: print " - Param: '"+param['name'] + "'. Typ: '" + param['type']+"'"
		print " - Returtyp: '"+function['output']+"'"
	
	def convertStruct(self,struct):
		out = "struct "+struct['name']+"{\n"
		for prop in struct['props']:
			out += "\t"+self.convertPrimitive(prop['type'])+" "+prop['name']+";\n"
		out += "};"
		return out
	
	def convertFunction(self,function):
		out = self.convertPrimitive(function['output']) + " " + function['name']
		out += " ("+self.convertParams(function['params'])+") { }"
		return out
		
	def convertParams(self,params):
		paramStrings = []
		for p in params:
			paramStrings.append(self.convertPrimitive(p['type'])+" "+p['name'])
		return (", ".join(paramStrings))
	
	def write(self):
		out = "/*! @file "+self.filename+" */"
		
		for struct in self.structs:
			out += "\n\n" + self.convertStruct(struct)
		
		for function in self.functions:
			out += "\n\n" + self.convertFunction(function)
		self.file.write(out)