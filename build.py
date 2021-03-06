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
	ag = build_main_graph(main)
	info_number = '> Modules`%d` Interfaces`%d` Links`%d`\n' % (ag.mod_num, ag.if_num, ag.link_num)
	info_mc = '> * Module Complexity `%.3f`\n' % (float(ag.if_num) / ag.mod_num)
	info_ic = '> * Interface Complexity `%.3f`\n' % (float(ag.link_num) / ag.if_num)
	info_ac = '> * Architecture Complexity `%.3f`\n' % (float(ag.link_num) / ag.mod_num)
	md = '# ' + main.attrib['title'] + '\n'
	md += '\n' + info_number + '\n' + info_mc +  '\n' + info_ic +  '\n' + info_ac + '\n'
	md += '\n![](main.gv.png)\n'
	for group in main.findall('group'):
		md += '\n### Group ' + group.attrib['name'] + ' `' + group.attrib['scope'] + '`\n\n'
		for module in group.findall('module'):
			md += '* [' + module.attrib['name'] + '](' + group.attrib['id'] + '/' + module.attrib['id'] + '.md)\n'
	output2file('Home.md', md);
	
def build_module(main, group, module):
	ag = build_module_graph(main, group, module)
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
	seq = 0
	gv = ''
	id = ''
	name = ''
	mod_num = 0
	if_num = 0
	link_num = 0
	def __init__(self, id, name):
		self.id = id
		self.name = name
		self.gv += 'label = "' + self.name + '";\n'
	def getNode(self):
		node = self.id + '_node_' + str(self.seq)
		self.seq += 1
		return node
	def addStarter(self):
		n = self.getNode()
		self.gv += n + '[shape=circle, width=.2, style=filled, label=""];\n'
		return n
	def addModule(self, label):
		self.mod_num += 1
		n = self.getNode()
		self.gv += n + '[shape=box, label="' + label + '"];\n'
		return n
	def addCurrentModule(self, label):
		n = self.getNode()
		self.gv += n + '[shape=box, peripheries=2, label="' + label + '"];\n'
		return n
	def addAction(self, module, label):
		n = self.getNode()
		self.gv += n + '[shape=polygon, skew=.5, label="' + label + '"];\n'
		self.gv += module + '->' + n + '[style=bold, arrowhead=none];\n'
		return n
	def addInterface(self, module, front):
		self.if_num += 1
		if front != None:
			n = self.getNode()
			self.gv += n + '[height=.3, fixedsize=true, label="' + front + '"];\n'
			self.gv += n + '->' + module + ';\n'
			return n
		else:
			return module
	def linkInterface(self, module, to, label, type):
		self.link_num += 1
		if type != None:
			label += '\\n[' + type + ']'
		self.gv += module + '->' + to + '[fontsize=9, label="' + label + '"];\n'
	def addSubGraph(self, graph):
		self.mod_num += graph.mod_num
		self.if_num += graph.if_num
		self.link_num += graph.link_num
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
	# draw all modules
	for group in main.findall('group'):
		mg = ArchGraph(group.attrib['id'], group.attrib['name'])
		for module in group.findall('module'):
			module.graph_node = mg.addModule(module.attrib['name'])
			for interface in module.content.findall('./interfaces/interface'):
				front = interface.attrib.get('front')
				interface.graph_node = mg.addInterface(module.graph_node, front)
		ag.addSubGraph(mg)
	# link all interfaces
	for group in main.findall('group'):
		for module in group.findall('module'):
			for [to, output] in module.outputs.items():
				to_interface = output['interface']
				type = to_interface.attrib.get('type')
				ag.linkInterface(module.graph_node, to_interface.graph_node, to_interface.attrib['name'], type)
	ag.output('main')
	return ag

def build_module_graph(main, group, module):
	ag = ArchGraph('module', '')
	mg = ArchGraph(module.attrib['id'], '')
	module_node = mg.addCurrentModule(module.attrib['name'])
	# draw all interfaces
	for interface in module.content.findall('./interfaces/interface'):
		starter_node = ag.addStarter()
		label = interface.attrib['name']
		type = interface.attrib.get('type')
		front = interface.attrib.get('front')
		if_node = ag.addInterface(module_node, front)
		ag.linkInterface(starter_node, if_node, label, type)
	# draw all outputs 
	for [to, output] in module.outputs.items():
		to_module = output['module']
		to_interface = output['interface']
		to_module_node = ag.addModule(to_module.attrib['name'])
		front = to_interface.attrib.get('front')
		to_interface.graph_node = ag.addInterface(to_module_node, front)
	# draw all actions and link to outputs
	for action in module.content.findall('./actions/action'):
		action_node = mg.addAction(module_node, action.attrib['name'])
		for a_interface in action.findall('interface'):
			interface_to = a_interface.attrib['to']
			output = module.outputs[interface_to]
			to_interface = output['interface']
			type = to_interface.attrib.get('type')
			ag.linkInterface(action_node, to_interface.graph_node, to_interface.attrib['name'], type)
	ag.addSubGraph(mg)
	ag.output(group.attrib['id'] + '/' + module.attrib['id'])
	return ag
	
def load_and_parse(main_file):
	main_dir = os.path.dirname(main_file)
	if main_dir == '':
		main_dir = './'
	print('load modules')
	main = ET.parse(main_file).getroot()
	for group in main.findall('group'):
		for module in group.findall('module'):
			module_path = group.attrib['id'] + '/' + module.attrib['id']
			print('load ' + module_path)
			module_file = main_dir + '/' + module_path + '.xml'
			module.content = ET.parse(module_file).getroot()
	print('parse modules')
	for group in main.findall('group'):
		for module in group.findall('module'):
			module.outputs = {}
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
					output = {}
					output['group'] = to_group
					output['module'] = to_module
					output['interface'] = to_interface
					module.outputs[interface_to] = output
	return main
	
if __name__ == '__main__':
	if len(sys.argv) != 2:
		print('Usage: build.py path/to/modules/main.xml')
		sys.exit(-1)
	# load all modules
	main = load_and_parse(sys.argv[1])
	# build markdown	
	print('building main')
	build_main(main)
	for group in main.findall('group'):
		for module in group.findall('module'):
			module_path = group.attrib['id'] + '/' + module.attrib['id']
			print('building ' + module_path)
			build_module(main, group, module)
	