import argparse
import xml.etree.ElementTree as ET

def printChilds(node):
	for child in node:
		print child.tag, child.attrib

argparser = argparse.ArgumentParser()
argparser.add_argument('filename')
args = argparser.parse_args()


tree = ET.parse(args.filename)

node = tree.getroot()
node = node.find('unit_declaration_q')
node = node.find('procedure_body_declaration')
node = node.find('body_declarative_items_ql')

for functionNode in node.findall('function_body_declaration'):
	functionName = functionNode.find('names_ql').find('defining_identifier').get('def_name')
	print "Funktion '"+functionName+"'"
	for paramNode in functionNode.find('parameter_profile_ql').findall('parameter_specification'):
		param = {}
		param['name'] = paramNode.find('names_ql').find('defining_identifier').get('def_name')
		param['type'] = paramNode.find('object_declaration_view_q').find('identifier').get('ref_name')
		print " - Param: '"+param['name'] + "'. Typ: '" + param['type']+"'"
	output = functionNode.find('result_profile_q').find('identifier').get('ref_name')
	print " - Returtyp: '"+output+"'"



