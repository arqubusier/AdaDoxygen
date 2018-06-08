import argparse
import ntpath
import xml.etree.ElementTree as ET
from cppfile import CppFile

def printChilds(node):
	for child in node:
		print child.tag, child.attrib


argparser = argparse.ArgumentParser()
argparser.add_argument('filename')
args = argparser.parse_args()

tree = ET.parse((args.filename).strip("\r"))

node = tree.getroot()
node = node.find('unit_declaration_q')
node = node.find('procedure_body_declaration')
node = node.find('body_declarative_items_ql')

cpp_file = ntpath.basename(args.filename).split('.')
cpp_file = ''.join(cpp_file[:len(cpp_file)-2])
cpp_file = cpp_file + ".cpp"
cpp = CppFile(cpp_file)

cpp.extractStructs(node)
cpp.extractFunctions(node)
#cpp.extractProcedures(node)
for function in cpp.functions: cpp.printFunction(function)
cpp.write()