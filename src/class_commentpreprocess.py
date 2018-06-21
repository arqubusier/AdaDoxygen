

class CommentPreprocess:
	
	def __init__(self,adafile):
		with open(adafile,'r') as file:
			self.lines_old = file.readlines()
		self.comments = []
		self.lines_new = []
		self.linenumber = 0
		for line in self.lines_old:
			self.readLine(line)
			
		mergedComments = self.mergeComments()
		self.setNewLines(mergedComments)
			
	def getResult(self): return "\n".join(self.lines_new)
	
	def setDefaultLineState(self):
		self.is_comment = False
		self.is_open = False
		self.enclose_char = "'"
		self.was_escaped = False
		self.was_dash = False
		self.comment = ''
		
			
	def readLine(self,line):
		self.linenumber += 1
		line = line.strip("\n\r")
		self.setDefaultLineState()
		for c in line:
			self.readChar(c)
		if self.comment != '':
			self.comments.append({'text':self.comment,'linenumber':self.linenumber})
		
	def readChar(self,c):
		if self.is_comment:
			self.comment += c
		else:
			if self.was_escaped == False:
				if self.is_open:
					if c == self.enclose_char:
						self.is_open = False
				elif self.was_dash and c == '-':
					self.is_comment = True
				elif c == '"' or c == "'":
					self.is_open = True
					self.enclose_char = c
				elif c == '\\':
					self.was_escaped = True
				elif c == '-':
					self.was_dash = True
			else:
				self.was_escaped = False
		
	def commentToPragma(self,comment): return 'pragma Comment ("'+comment+'");'
	
	def mergeComments(self):
		merged = []
		last_linenumber = -1
		tmp_text_arr = []
		for comment in self.comments:
			if last_linenumber + 1 != comment['linenumber'] and len(tmp_text_arr) > 0:
				text = "<br/>".join(tmp_text_arr)
				merged.append({'text':text,'linenumber':last_linenumber})
				tmp_text_arr = []
			tmp_text_arr.append(comment['text'])
			last_linenumber = comment['linenumber']
		if len(tmp_text_arr) > 0:
			text = "<br/>".join(tmp_text_arr)
			merged.append({'text':text,'linenumber':last_linenumber})
		return merged
	
	def setNewLines(self,mergedComments):
		i = 0
		for line in self.lines_old:
			line = line.strip("\n\r")
			i += 1
			for comment in mergedComments:
				if i == comment['linenumber']:
					line = self.commentToPragma(comment['text']) + "\n" + line
			self.lines_new.append(line)
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			