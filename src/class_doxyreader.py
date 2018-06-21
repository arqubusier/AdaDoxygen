import sys,re

class DoxyReader:

	def __init__(self,file):
		
		self.include_private_bool = False
		
		if file != '':
			with open(file,'r') as file:
				lines = file.readlines()
			p = re.compile('^EXTRACT_PRIVATE\s+\=\s+(YES|NO)')
			for line in lines:
				str = line.strip("\n\r")
				m = p.match(str)
				if m and m.group(1) == 'YES':
					self.include_private_bool = True
		else:
			sys.exit("Flag '-d DOXYGEN_FILE' is mandatory")