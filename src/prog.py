import sys,argparse,ntpath
import xml.etree.ElementTree as ET
from cppfile import CppFile

argparser = argparse.ArgumentParser()
argparser.add_argument('files', nargs='+', help="XML-files for Ada to C++. ADB/ADS-files for comment preprocessing")
argparser.add_argument('-p', '--prefix', default="__", help="String to be prepended before nested functions/procedures, default='__'")
argparser.add_argument('-a', '--action', default="Ada2Cpp", help="Ada2Cpp or CommentPreprocessor, default='Ada2Cpp'")
args = argparser.parse_args()

if args.action == 'CommentPreprocessor':
	for adafile in args.files:
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
			
	sys.exit("CommentPreprocessor done")
	
elif args.action == 'Ada2Cpp':
	pps = []
	print "---PARSING XML---"
	for xmlfile in args.files:
		tree = ET.parse((xmlfile).strip("\r"))
		pp = CppFile(xmlfile,tree,args.prefix)
		
		print "Parsing XML from "+xmlfile
		pp.parse()
		pps.append(pp)

	print "---SET INCLUDES AND NAMESPACES---"
	for pp in pps:
		pp.setIncludes(pps)
		pp.setNamespaces(pps)
		
	print "---GENERATE PP FILES---"
	for pp in pps:
		print "Creating "+pp.filename+"..."
		pp.write()
	sys.exit("Ada2Cpp done")

sys.exit("Error: No action named '"+args.action+"'")