

def commentPreprocess(adafile):
	lines2 = []
	with open(adafile,'r') as file:
		lines = file.readlines()
	for line in lines:
		line = line.strip("\n\r")
		
		is_comment = False
		is_open = False
		enclose_char = "'"
		was_escaped = False
		was_dash = False
		comment = ''
		
		for c in line:
			if is_comment:
				comment += c
			else:
				if was_escaped == False:
					if is_open:
						if c == enclose_char:
							is_open = False
					elif was_dash and c == '-':
						is_comment = True
					elif c == '"' or c == "'":
						is_open = True
						enclose_char = c
					elif c == '\\':
						was_escaped = True
					elif c == '-':
						was_dash = True
				else:
					was_escaped = False
		if comment != '':
			line = 'pragma Comment ("'+comment+'");\n'+line 
		lines2.append(line)
	with open(adafile+".preproc","w+") as newfile:
		newfile.write("\n".join(lines2))