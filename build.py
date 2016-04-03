#-*-coding:utf-8-*-

import os
import sys
import string
import xml.etree.ElementTree as ET

reload(sys)
sys.setdefaultencoding("utf-8")

OUTPUT = 'output'
DOT = 'D:\\Program Files (x86)\\Graphviz2.38\\bin\\dot.exe'

def output2file(filename, content):
	filename = OUTPUT + '/' + filename
	dir = os.path.dirname(filename)
	if not os.path.exists(dir):
		os.mkdir(dir)
	fp = open(filename, 'w')
	fp.write(content)
	fp.close()
	return filename
	
def build_main(main):
	md = '# ' + main.attrib['title'] + '\n'
	md += '\n![](main.gv.png)\n'
	for group in main.findall('group'):
		md += '\n### Group ' + group.attrib['name'] + ' `' + group.attrib['scope'] + '`\n\n'
		for module in group.findall('module'):
			md += '* [' + module.attrib['name'] + '](' + group.attrib['id'] + '/' + module.attrib['id'] + '.md)\n'
	output2file('Home.md', md);
	
def build_module(main, group, module):
	md = '# [' + main.attrib['title'] + '](../Home.md) - ' + module.attrib['name'] + '\n'
	md += '\n![](' + module.attrib['id'] + '.gv.png)\n'
	for action in module.content.findall('./actions/action'):
		interface_id = action.attrib['interface']
		interface = module.content.find("./interfaces/interface[@id='" + interface_id + "']")
		md += '\n### Action ' + action.attrib['name'] + '\n\n'
		md += '> From ' + interface.attrib['name']
		if interface.attrib.has_key('type'):
			md += ' `' + interface.attrib['type'] + '`'
		if interface.attrib.has_key('front'):
			md += ' `' + interface.attrib['front'] + '`'
		md += '\n\n'
		for a_function in action.findall('function'):
			function_id = a_function.attrib['id']
			function = module.content.find("./functions/function[@id='" + function_id + "']")
			md += '* Function: ' + function.attrib['name'] + '\n'
		for a_interface in action.findall('interface'):
			interface_to = a_interface.attrib['to']
			ifarr = string.split(interface_to, '.')
			to_group_id = ifarr[0]
			to_group = main.find("./group[@id='" + to_group_id + "']")
			to_module_id = ifarr[1]
			to_module = to_group.find("./module[@id='" + to_module_id + "']")
			to_interface_id = ifarr[2]
			to_interface = to_module.content.find("./interfaces/interface[@id='" + to_interface_id + "']")
			to_module_path = '../' + to_group_id + '/' + to_module_id + '.md'
			md += '* Interface: [' + to_interface.attrib['name'] + '](' + to_module_path + ')\n'
	output2file(group.attrib['id'] + '/' + module.attrib['id'] + '.md', md);

class ArchGraph:
	id = 0
	gv = ''
	name = ''
	title = ''
	def __init__(self, name, title):
		self.name = name
		self.title = title
		self.gv += 'label = "' + self.title + '";\n'
	def getNode(self):
		node = self.name + '_node_' + str(self.id)
		self.id += 1
		return node
	def addStarter(self):
		n = self.getNode()
		self.gv += n + '[shape=circle, width=.2, style=filled, label=""];\n'
		return n
	def addModule(self, label):
		n = self.getNode()
		self.gv += n + '[shape=box, label="' + label + '"];\n'
		return n
	def addCurrentModule(self, label):
		n = self.getNode()
		self.gv += n + '[shape=box, peripheries=2, label="' + label + '"];\n'
		return n
	def addAction(self, module, label):
		n = self.getNode()
		self.gv += n + '[shape=polygon, skew=.5, style=filled, label="' + label + '"];\n'
		self.gv += module + '->' + n + '[style=bold, arrowhead=none];\n'
		return n
	def addInterface(self, module, to, label, type, front):
		if type != None:
			label += '\\n[' + type + ']'
		if front != None:
			n = self.getNode()
			self.gv += n + '[height=.3, fixedsize=true, label="' + front + '"];\n'
			self.gv += n + '->' + to + ';\n'
			to = n
		self.gv += module + '->' + to + '[fontsize=9, label="' + label + '"];\n'
	def addSubGraph(self, graph):
		n = self.getNode()
		self.gv += 'subgraph cluster_' + n + ' {\n'
		self.gv += 'style = filled;\n'
		self.gv += 'color = lightgrey;\n'
		self.gv += graph.get()
		self.gv += '}\n'
		return n
	def get(self):
		return self.gv
	def getGraph(self):
		gv = 'digraph G {\n'
		gv += 'edge[fontname="simsun"];\n'
		gv += 'node[fontname="simsun"];\n'
		gv += 'graph[fontname="simsun"];\n'
		gv += self.gv
		gv += '}'
		return gv
	def output(self, path):
		filename = output2file(path + '.gv', self.getGraph());
		os.system('"' + DOT + '" -Tpng -o' + filename + '.png ' + filename);
		
def build_main_graph(main):
	ag = ArchGraph('main', '')
	for group in main.findall('group'):
		subg = ArchGraph(group.attrib['id'], group.attrib['name'])
		for module in group.findall('module'):
			module.graph_node = subg.addModule(module.attrib['name'])
		ag.addSubGraph(subg)
	for group in main.findall('group'):
		for module in group.findall('module'):
			for action in module.content.findall('./actions/action'):
				for a_interface in action.findall('interface'):
					interface_to = a_interface.attrib['to']
					ifarr = string.split(interface_to, '.')
					to_group_id = ifarr[0]
					to_group = main.find("./group[@id='" + to_group_id + "']")
					to_module_id = ifarr[1]
					to_module = to_group.find("./module[@id='" + to_module_id + "']")
					to_interface_id = ifarr[2]
					to_interface = to_module.content.find("./interfaces/interface[@id='" + to_interface_id + "']")
					type = to_interface.attrib.get('type')
					front = to_interface.attrib.get('front')
					ag.addInterface(module.graph_node, to_module.graph_node, to_interface.attrib['name'], type, front)
	ag.output('main')

def build_module_graph(main, group, module):
	ag = ArchGraph(module.attrib['id'], '')
	module_node = ag.addCurrentModule(module.attrib['name'])
	for interface in module.content.findall('./interfaces/interface'):
		starter_node = ag.addStarter()
		label = interface.attrib['name']
		type = interface.attrib.get('type')
		front = interface.attrib.get('front')
		ag.addInterface(starter_node, module_node, label, type, front)
	for action in module.content.findall('./actions/action'):
		action_node = ag.addAction(module_node, action.attrib['name'])
		for a_interface in action.findall('interface'):
			interface_to = a_interface.attrib['to']
			ifarr = string.split(interface_to, '.')
			to_group_id = ifarr[0]
			to_group = main.find("./group[@id='" + to_group_id + "']")
			to_module_id = ifarr[1]
			to_module = to_group.find("./module[@id='" + to_module_id + "']")
			to_interface_id = ifarr[2]
			to_interface = to_module.content.find("./interfaces/interface[@id='" + to_interface_id + "']")
			to_module_node = ag.addModule(to_module.attrib['name'])
			type = to_interface.attrib.get('type')
			front = to_interface.attrib.get('front')
			ag.addInterface(action_node, to_module_node, to_interface.attrib['name'], type, front)
	ag.output(group.attrib['id'] + '/' + module.attrib['id'])
	
if __name__ == '__main__':
	if len(sys.argv) != 2:
		print('Usage: build.py path/to/modules/main.xml')
		sys.exit(-1)
	main_file = sys.argv[1]
	main_dir = os.path.dirname(main_file)
	# load all modules
	print('load main')
	main = ET.parse(main_file).getroot()
	for group in main.findall('group'):
		for module in group.findall('module'):
			module_path = group.attrib['id'] + '/' + module.attrib['id']
			print('load ' + module_path)
			module_file = main_dir + '/' + module_path + '.xml'
			module.content = ET.parse(module_file).getroot()
	# build markdown	
	print('building main')
	build_main(main)
	print('building main graph')
	build_main_graph(main)
	for group in main.findall('group'):
		for module in group.findall('module'):
			print('building ' + module_path)
			build_module(main, group, module)
			print('building ' + module_path + ' graph')
			build_module_graph(main, group, module)
	