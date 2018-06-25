import sys, ntpath

""" 
The static methods below converts dictionaries to c++ code
"""
class Convert:
	
	@staticmethod
	def filename(filepath):
		file = ntpath.basename(filepath).split('.')
		ext_ada = file[len(file)-2]
		if ext_ada == 'ads': ext_pp = '.hpp'
		elif ext_ada == 'adb': ext_pp = '.cpp'
		else: sys.exit(filepath+" is not ads or adb")
		file = ''.join(file[:len(file)-2])
		return file + ext_pp
	
	@staticmethod
	def struct(struct):
		out = Convert.comment(struct['comment'])
		out += "struct "+struct['name']+"{\n"
		for prop in struct['props']:
			out += "\t"+prop['type']+" "+prop['name']+";\n"
		out += "};"
		return out
		
	@staticmethod
	def enum(enum):
		comment = "<b>Enumaration type</b> ("+",".join(enum['enums'])+")<br/>"+enum['comment']
		print comment
		out = Convert.comment(comment)
		out += "typedef int "+enum['name']+";"
		return out
		
	@staticmethod
	def rename(rename):
		out = Convert.comment(rename['comment'])
		out += "namespace "+rename['name']+"="+("::".join(rename['package_names']))+";"
		return out
	
	@staticmethod
	def namespaces(function,prefix):
		if len(function['childs']) == 0: return ''
		return "using namespace " + prefix + function['name']+";\n"
	
	@staticmethod
	def function(function,prefix):
		out = Convert.comment(function['comment'])
		out += function['output'] + " " + function['name']
		out += " ("+Convert.params(function['params'])+")"
		if 'body' in function:
			out += ' {\n'
			out += Convert.namespaces(function,prefix)
			for var in function['body']['variables']:
				out += var['type'] + " " + var['name'] + ";\n"
			for call in function['body']['calls']:
				if call['is_void'] is False: out += "(void)"
				out += call['name']+"("+(",".join(call['params']))+");\n"
			out += "\n}"
		else:
			out += ';'
		return out	
		
	@staticmethod
	def params(params):
		paramStrings = []
		for p in params:
			paramStrings.append(p['type']+" "+p['name'])
		return (", ".join(paramStrings))
	
	@staticmethod
	def comment(comment):
		out = ''
		if comment != '': out += "/*! "+comment+" */\n"
		return out
		
	@staticmethod
	def include(include):
		return '#include "'+include['file']+'"'
		
	@staticmethod
	def namespace(namespace):
		return 'using namespace '+namespace+';'
		