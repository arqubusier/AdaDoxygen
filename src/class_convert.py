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
			print(preprocfile)
			print(xmlfile)
			sys.exit("A XML file found that could not be matched with the original Ada-file")
		
		preprocfilepath = os.path.relpath(preprocfile,tmp_dir_ada)
		newfilepathabs = os.path.join(tmp_dir_cpp, preprocfilepath)
		return newfilepathabs,preprocfile
		
	@staticmethod
	def fileext(xmlfile):
		file = ntpath.basename(xmlfile).split('.')
		ext_ada = file[len(file)-2]
		#return '.'+ext_ada
		
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
			out =  Convert.comment(Convert.getPrivateComment(type))
		else:
			c = "<b>Type</b><br/>"+type['plain']
			c += Convert.commentDivider()
			c += Convert.getPrivateComment(type)
			c += type['comment']
			out = Convert.comment(c)
		out += "typedef int "+type['name']+";" + "\n" # */
		#out += "/* @} */"
		return out
		
	@staticmethod
	def getPrivateComment(element):
		if element['comment_add_private']: return "\\private "
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
		if 'is_hidden' in function: return '/* A generic function was here... */'
		function['include_param_dir_comment'] = True
		if (extractAll is False and (function['comment'] == '')):
			out = ''
			function['include_param_dir_comment'] = False
		else:
			c = Convert.getPrivateComment(function)
			c += function['comment']
			out = Convert.comment(c)
			
		out += Convert.functionHead(function)
		if 'body' in function or 'generic' in function: 
			out += Convert.functionBody(function,prefix)
		else: out += ';'
		return out	
		
	@staticmethod
	def functionHead(function):
		if 'function_head' in function: return function['function_head']
		out = ""
		if 'generic' in function:
			out += Convert.generic(function['generic'])+" "
		out += function['output'] + " " + function['name']
		out += " ("+Convert.params(function)+")"
		return out
		
	@staticmethod
	def functionBody(function,prefix):
		if 'function_body' in function: return function['function_body']
		out = ' {\n'
		out += Convert.namespaces(function,prefix)
		for var in function['body']['variables']:
			out += var['type'] + " " + var['name'] + ";\n"
		for call in function['body']['calls']:
			if call['is_void'] is False: out += "(void)"
			out += call['name']+"("+(",".join(call['params']))+");\n"
		out += "\n}"
		return out
	
	@staticmethod
	def generic(types):
		arr = []
		for type in types:
			arr.append("typename "+type)
		out = "template <" + (",".join(arr)) + ">"
		return out
		
	@staticmethod
	def params(function):
		paramStrings = []
		for p in function['params']:
			str = p['type']+" "+p['name']
			if 'include_param_dir_comment' in function and function['include_param_dir_comment']:
				str += " /**< ["+p['dir']+"] */"
			paramStrings.append(str)
		return (",\n".join(paramStrings))
		
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
		