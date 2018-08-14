import xml.etree.ElementTree as ET
from HTMLParser import HTMLParser

## This class is not tested or used
class XMLPostprocess:

	prepend_output = ""

	def __init__(self, file):
		print file
		
		self.file = file
		self.error = ""
		self.root = self.getRoot()
		if self.succeded():
			self.postprocess()
		
	def getH2Replacements(self):
		return [
		{
			'search' : 'Classes',
			'replace': 'Records'
		},
		{
			'search' : 'Here are the classes, structs, unions and interfaces with brief descriptions:',
			'replace': 'Here are the records with brief descriptions:'
		},
		{
			'search' : 'Typedef Documentation',
			'replace': 'Type Documentation'
		},
		{
			'search' : 'Function Documentation',
			'replace': 'Function & Procedure Documentation'
		},
		{
			'search' : 'Functions',
			'replace': 'Functions and Procedures'
		},
		{
			'search' : 'Typedefs',
			'replace': 'Types'
		}]
		
	def postprocess(self):
		repls = self.getH2Replacements()
		for h2node in self.root.findall(".//*[@class='groupheader']"):
			text = ET.tostring(h2node, method="text").strip()
			for repl in repls:
				if text == repl['search']:
					tmpNode = h2node.find('a')
					if tmpNode is None:
						h2node.text = repl['replace']
					else: 
						tmpNode.tail = repl['replace']
					print "match!"
					
	def getRoot(self):
		with open(self.file,"r") as fh:
			lines = fh.readlines()
		content = "".join(lines[2:]) #xmlns-attribute prepend all tags with it's value, remove first two lines and prepend them to output
		content = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">'+"<html>"+content
		
		h = HTMLParser()
		#content = h.unescape(content)
		#content = content.encode('utf-8').decode('ascii','ignore')
		
		#try:
		#root = ET.fromstring(content)
		parser = ET.XMLParser(encoding="utf-8")
		parser.parser.UseForeignDTD(True)
		parser.entity['rarr'] = h.unescape('&rarr;')
		parser.entity['nbsp'] = h.unescape('&nbsp;')
		#root = ET.XML(content,parser=parser)
		root = ET.fromstring(content,parser=parser)
		#except:
		#	root = None
		#	self.error = "Could not parse"
		return root
		
	def getResult(self):
		#prep = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">'
		#prep += '<html xmlns="http://www.w3.org/1999/xhtml">'
		prep = ''
		out = prep + ET.tostring(self.root, encoding="UTF-8", method="html")
		return out
		
	def succeded(self):
		return self.error == ''