import re
from class_convert import Convert

class PPTuple:
	def __init__(self, hpp, cpp):
		self.hpp = hpp
		self.cpp = cpp
		
	def moveGenericFunctionBodiesRecursive(self, cpp_elements):
		for el in cpp_elements:
			if 'childs' in el: self.moveGenericFunctionBodiesRecursive(el['childs'])
			if 'public' in el: self.moveGenericFunctionBodiesRecursive(el['public'])
			if 'private' in el: self.moveGenericFunctionBodiesRecursive(el['private'])
			
			if el['type'] == 'function':
				uri = self.cppToHppUri(el['uri'])
				if uri is None:
					print("Couldnt convert URI")
					return
				el_hpp = self.hpp.getElementByUri(uri)
				if el_hpp is None:
					print("Warning: Couldnt find hpp-element '"+uri+"'")
					return
				el_hpp['function_body'] = Convert.functionBody(el,self.cpp.prefixFunction)
				if 'generic' in el_hpp:
					el['is_hidden'] = True
					
	def cppToHppUri(self,uri):
		p = re.compile('^(ada:\/\/[^\/]+)(_body)(.*)$')
		m = p.match(uri)
		if m is False or m is None: return None
		else: return (m.group(1)+m.group(3))
		
	def exchangePrivateInfoRecursive(self, cpp_elements):
		
		for el_cpp in cpp_elements:
			if 'childs' in el_cpp: self.exchangePrivateInfoRecursive(el_cpp['childs'])
			if 'public' in el_cpp: self.exchangePrivateInfoRecursive(el_cpp['public'])
			if 'private' in el_cpp: self.exchangePrivateInfoRecursive(el_cpp['private'])
			
			if 'uri' in el_cpp:
				uri = self.cppToHppUri(el_cpp['uri'])
				if uri is not None:
					el_hpp = self.hpp.getElementByUri(uri)
					if el_hpp is not None:
						if el_hpp['comment'] != '' and el_cpp['comment'] == '':
							el_cpp['comment'] = ' '
						el_cpp['is_private'] = el_hpp['is_private']
						el_cpp['is_extract'] = el_hpp['is_extract']
