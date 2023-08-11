
######################################
# 
# Title: Logic Simulator
# Developer: Kalind Karia
# GitHub: kalindkaria
# Email: kalind1610@gmail.com
# 
######################################

# Import modules
import json, sys
from functools import reduce

"""
# =========================
# Data structure for a Node
# =========================

- Node number
- Type of gate
- Controlling value (optional)
- Inversion parity (optional)
- No. of inputs
- No. of outputs
- Input list of nodes
- Output list of nodes
- Output value of Node
- Level of Node

# =========================
"""

# complete list of nodes and their properties in given circuit
circuit_nodes = {}


class Node:
	"""Defining properties for a Node in the netlist of given circuit.
	"""

	def __init__(self) -> None:
		self.node_num = 0
		self.gate_type = None
		self.num_inputs = 0
		self.num_outputs = 0
		self.input_list = []
		self.output_list = []
		self.level = None
		self.value = None


def get_node_level(node_info):
	"""Compute the level of a node from its given netlist information.

	Args:
		node_info (dict): Information related to a given node or gate.

	Returns:
		int: Level of a given node = 1 + max( level of all its inputs )
	"""
	inp_node_levels = []
	for inp_node in node_info['input_list']:
		if vars(circuit_nodes[str(inp_node)])['level'] is not None:
			inp_node_levels.append(vars(circuit_nodes[str(inp_node)])['level'])
		else:
			get_node_level(vars(circuit_nodes[str(inp_node)]))
		if len(inp_node_levels) == len(node_info['input_list']):
			return 1 + max(inp_node_levels)


def compute_output_value(gate_type, inp_node_values):
	"""Compute the output value of given node from the values
	of the input nodes to this particular gate or node.

	Args:
		gate_type (str): Type of gate present at given node.
		inp_node_values (list): List of values for input nodes for given gate or node.

	Returns:
		int: Output value for a given gate or node.
	"""
	inp_node_values = sorted(inp_node_values)
	if gate_type == 'not' and len(inp_node_values) == 1:
		if inp_node_values[0] == 2:
			return 2
		else:
			return int(not(inp_node_values[0]))
	elif gate_type == 'and':
		return reduce((lambda a, b: a and b), inp_node_values)
	elif gate_type == 'or':
		return reduce((lambda a, b: a or b), inp_node_values)
	elif gate_type == 'nand':
		return int(compute_output_value('not', [reduce((lambda a, b: a and b), inp_node_values)]))
	elif gate_type == 'nor':
		return int(compute_output_value('not', [reduce((lambda a, b: a or b), inp_node_values)]))
	elif gate_type == 'xor':
		return int(reduce((lambda a, b: (a and compute_output_value('not', [b])) or (compute_output_value('not', [a]) and b)), inp_node_values))
	elif gate_type == 'out' and len(inp_node_values) == 1:
		return inp_node_values[0]


def find_output_value(node_info):
	"""Iterate over each node or gate in the given circuit and
	find output value for the inputs at that node or gate.

	Args:
		node_info (dict): Information related to a given node or gate.

	Returns:
		int: Output value for a given gate or node.
	"""
	inp_node_values = []
	for inp_node in node_info['input_list']:
		if vars(circuit_nodes[str(inp_node)])['value'] is not None:
			inp_node_values.append(vars(circuit_nodes[str(inp_node)])['value'])
		else:
			find_output_value(vars(circuit_nodes[str(inp_node)]))
		if len(inp_node_values) == len(node_info['input_list']):
			return compute_output_value(node_info['gate_type'], inp_node_values)


def simulate(circuit_file_path, input_vect_file_path):
	"""Simulate the circuit for a given netlist description
    and the input test vectors for applying stimuli to the circuit.

	Args:
		circuit_file_path (str): File path describing the circuit netlist.
		input_vect_file_path (str): File path describing the set of input stimuli vectors.
	"""

	# read data from the 'circuit_file_path'
	circuit_file_obj = open(circuit_file_path, 'r')
	netlist_data = json.load(circuit_file_obj)
	circuit_file_obj.close()

	# extract information about each node from the given netlist
	for node_type in netlist_data:
		for node in netlist_data[node_type]:
			circuit_nodes[str(node['node_num'])] = Node()
			circuit_nodes[str(node['node_num'])].node_num = node['node_num']

			if node_type == "inputs":
				circuit_nodes[str(node['node_num'])].gate_type = "in"
				circuit_nodes[str(node['node_num'])].level = 0
				circuit_nodes[str(node['node_num'])].output_list = node['out_nodes']
				circuit_nodes[str(node['node_num'])].num_outputs = len(circuit_nodes[str(node['node_num'])].output_list)
			elif node_type == "gates":
				circuit_nodes[str(node['node_num'])].gate_type = node['type']
				circuit_nodes[str(node['node_num'])].input_list = node['inp_nodes']
				circuit_nodes[str(node['node_num'])].num_inputs = len(circuit_nodes[str(node['node_num'])].input_list)
				circuit_nodes[str(node['node_num'])].output_list = node['out_nodes']
				circuit_nodes[str(node['node_num'])].num_outputs = len(circuit_nodes[str(node['node_num'])].output_list)
			elif node_type == "outputs":
				circuit_nodes[str(node['node_num'])].gate_type = "out"
				circuit_nodes[str(node['node_num'])].input_list = node['inp_nodes']
				circuit_nodes[str(node['node_num'])].num_inputs = len(circuit_nodes[str(node['node_num'])].input_list)
	
	# levelize the circuit nodes apart from primary inputs
	max_level = -1
	for node in circuit_nodes:
		if vars(circuit_nodes[node])['gate_type'] not in ["in", "out"]:
			level = get_node_level(vars(circuit_nodes[node]))
			circuit_nodes[node].level = level
			max_level = max(max_level, level)

	for node in circuit_nodes:
		if vars(circuit_nodes[node])['gate_type'] in ["out"]:
			circuit_nodes[node].level = max_level + 1
	
	# provide stimuli to the 'input' nodes
	input_vect_obj = open(input_vect_file_path, 'r')
	input_vect = json.load(input_vect_obj)
	input_vect_obj.close()

	for test_vect in input_vect:
		print(test_vect + " => " + str(input_vect[test_vect]) + '\n')
		for node_num, inp_val in input_vect[test_vect].items():
			circuit_nodes[node_num].value = inp_val
		for node_level in range(1, max_level + 1):
			for node in circuit_nodes:
				if vars(circuit_nodes[node])['level'] == node_level:
					val = find_output_value(vars(circuit_nodes[node]))
					circuit_nodes[node].value = val
		for node in circuit_nodes:
			if vars(circuit_nodes[node])['gate_type'] in ["out"]:
				val = find_output_value(vars(circuit_nodes[node]))
				circuit_nodes[node].value = val
				print(vars(circuit_nodes[node]))
		print('=========================================\n')


if __name__ == '__main__':
	"""Main function of entry point
	"""
	# get path of the netlist file for circuit description
	circuit_file_path = sys.argv[1]
	# get path of the input test vector file
	input_vect_file_path = sys.argv[2]
	# start with logical simulation
	simulate(circuit_file_path, input_vect_file_path)
