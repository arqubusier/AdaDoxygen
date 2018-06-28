import os, sys, ntpath

""" 
The static methods below converts dictionaries to c++ code
"""
class Convert:
	
	@staticmethod
	def filename(xmlfile, preprocfiles, tmp_dir_cpp):
		preprocfile = ""
		for test_file in preprocfiles:
			if ntpath.basename(test_file)+".xml" == ntpath.basename(xmlfile):
				preprocfile = test_file
		if preprocfile == "":
			print preprocfile
			print xmlfile
			sys.exit("A XML file found that could not be matched with the original Ada-file")
		
		commonpath = os.path.commonprefix(preprocfiles)
		commondir = os.path.dirname(commonpath)
		preprocfilepath = preprocfile[len(commondir)+1:]
		ext_pp = Convert.fileext(xmlfile)
		newfilepath = os.path.splitext(preprocfilepath)[0] + ext_pp
		return os.path.join(tmp_dir_cpp, newfilepath),preprocfile
		
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
	def struct(struct):
		out = Convert.comment(struct['comment'])
		out += "struct "+struct['name']+"{\n"
		for prop in struct['props']:
			out += "\t"+prop['type']+" "+prop['name']+";\n"
		out += "};"
		return out
		
	@staticmethod
	def type(type):
		c = "<b>Type</b>"
		c += "<br/>"+type['plain']
		c += Convert.commentDivider()+type['comment']
		out = Convert.comment(c)
		out += "typedef int "+type['name']+";"
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
		