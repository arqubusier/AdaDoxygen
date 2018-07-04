from bs4 import BeautifulSoup

class HTMLPostprocess:
	
	def __init__(self, file):
		print file
		
		self.file = file
		self.soup = self.getSoup()
		
		groupheader_doc_css_select = '.contents h2.groupheader'
		groupheader_header_css_select = '.header .summary a'
		groupheader_table_css_select = '.contents .memberdecls .heading td h2'
		self.replacements = [
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
		
		self.postprocess()
		
		
	def postprocess(self):
		#nodes = self.soup.select(".groupheader")
		nodes = self.soup.find_all("h2")
		print nodes
		for repl in self.replacements:
			for node in nodes:
				if node.string is not None:
					if node.string.strip("\n\r\t") == repl['search']:
						print 'MATCH '+node.string
						node.string = repl['replace']
					else: print "NO "+node.string.strip("\n\r\t") 
		
	
		
	def getSoup(self):
		with open(self.file,'r') as file:
			content = "".join(file.readlines())
		#content = content.encode('utf-8').decode('ascii','ignore')
		return BeautifulSoup(content,"html.parser")
		
	def getResult(self): return self.soup.prettify("utf-8")
	