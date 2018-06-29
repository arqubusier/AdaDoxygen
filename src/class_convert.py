import os, sys, ntpath

""" 
The static methods below converts dictionaries to c++ code
"""
class Convert:
	
	@staticmethod
	def filename(xmlfile, preprocfiles, tmp_dir_ada, tmp_dir_cpp):
		preprocfile = ""
		for test_file in preprocfiles:
			if ntpath.basename(test_file)+".xml" == ntpath.basename(xmlfile):
				preprocfile = test_file
		if preprocfile == "":
			print preprocfile
			print xmlfile
			sys.exit("A XML file found that could not be matched with the original Ada-file")
		
		preprocfilepath = os.path.relpath(preprocfile,tmp_dir_ada)
		newfilepathabs = os.path.join(tmp_dir_cpp, preprocfilepath)
		return newfilepathabs,preprocfile
		
	@staticmethod
	def fileext(xmlfile):
		file = ntpath.basename(xmlfile).split('.')
		ext_ada = file[len(file)-2]
		return '.'+ext_ada
		
		if ext_ada == 'ads': ext_pp = '.hpp'
		elif ext_ada == 'adb': ext_pp = '.cpp'
		else: sys.exit(xmlfile+" is not ads or adb")
		return ext_pp
		
	@staticmethod
	def struct(struct,extractAll):
		if extractAll is False and struct['comment'] == '':
			out = ''
		else:
			c = Convert.getPrivateComment(struct)
			c += struct['comment']
			out = Convert.comment(c)

		out += "struct "+struct['name']+"{\n"
		for prop in struct['props']:
			out += "\t"+prop['type']+" "+prop['name']+";\n"
		out += "};"
		return out
		
	@staticmethod
	def type(type,extractAll):
		if extractAll is False and type['comment'] == '':
			out = ''
		else:
			c = "<b>Type</b>"
			c += "<br/>"+type['plain']
			c += Convert.commentDivider()
			c += Convert.getPrivateComment(type)
			c += type['comment']
			out = Convert.comment(c)
		out += "typedef int "+type['name']+";"
		return out
		
	@staticmethod
	def getPrivateComment(element):
		if element['comment_add_private']:
			return '<b>PRIVATE</b>'+Convert.commentDivider()
		return ''
		
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
	def function(function,prefix,extractAll):
		if extractAll is False and function['comment'] == '':
			out = ''
		else:
			c = Convert.getPrivateComment(function)
			c += function['comment']
			out = Convert.comment(c)
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
		c = comment.replace('""','"')
		if c != '': out += "/*! "+c+" */\n"
		return out
		
	@staticmethod
	def commentDivider(): return "<div style='border-top: 1px solid #A8B8D9;'></div>"
		
	@staticmethod
	def include(include):
		return '#include "'+os.path.split(include['file'])[1]+'"'
		
	@staticmethod
	def namespace(namespace):
		return 'using namespace '+namespace+';'
		