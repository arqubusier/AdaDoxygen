import re,logging
from convert import Convert

## Manages a tuple of PPFile-objects, 
#  the cpp/adb with the corresponsing hpp/ads
class PPTuple:
	def __init__(self, hpp, cpp):
		self.hpp = hpp
		self.cpp = cpp
	
	## In Ada, a generic function is declared in a ads-file and implemented in a adb-file
	#  In C++, a generic function (template) is declared and implemented in the hpp-file
	#  
	#  So the function body has to be moved from adb/cpp to ads/hpp
	def moveGenericFunctionBodiesRecursive(self, cpp_elements):
		for el in cpp_elements:
			if 'childs' in el: self.moveGenericFunctionBodiesRecursive(el['childs'])
			if 'public' in el: self.moveGenericFunctionBodiesRecursive(el['public'])
			if 'private' in el: self.moveGenericFunctionBodiesRecursive(el['private'])
			
			if el['type'] == 'function':
				uri = self.cppToHppUri(el['uri'])
				if uri is None:
					logging.warning("Couldnt convert URI ("+self.cpp.name+")")
					return
				el_hpp = self.hpp.getElementByUri(uri)
				if el_hpp is None:
					logging.warning("Couldnt find hpp-element '"+uri+"'")
					return
				el_hpp['function_body'] = Convert.functionBody(el,self.cpp.prefixFunction)
				if 'generic' in el_hpp:
					el['is_hidden'] = True
					
	## Convert a body uri to a declaration uri
	def cppToHppUri(self,uri):
		p = re.compile('^(ada:\/\/[^\/]+)(_body)(.*)$')
		m = p.match(uri)
		if m is False or m is None: return None
		else: return (m.group(1)+m.group(3))
		
	## Only the .ads.xml knows if a element is private or not
	#  Therefore the info has to be exchanged to the adb PPFile object.
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
