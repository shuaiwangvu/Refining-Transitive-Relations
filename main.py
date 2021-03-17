# Refine pseudo-Transitive Relations
# author: Shuai Wang @ VU Amsterdam

# example runs:
# python main.py -u ../your_path/rdfs_subClassOf_edgelist.gz P1 S1
# python main.py -u ../your_path/rdfs_subClassOf_edgelist.gz P2 S2

# -u means unweighted and -w means weighted
# P1: without preprocessing of relations in size-two cycles in SCCs.
# P2: make decisions on relations in size-two cycles in SCCs first.
import gzip

import numpy as np
import datetime
import pickle
import time
import networkx as nx
from networkx.algorithms import community
import pymetis
import sys
import csv
from z3 import *
import matplotlib.pyplot as plt
import tldextract
import json
import random
from collections import Counter
from bidict import bidict

mode = '' # either weighted or unweighted
input_file_path = ''
strategy_partitioning = ''
strategy_cycle_sampling = ''


parameter_setting = 1 # static setting 1 or 2, or dynamic (0)
# please ignore this dynamic setting for now. It's still to be explored.

collect_nodes = set()
can_remove = set()

scc_size_limit = 15000
num_clause_limit = 3000
path_size_limit = 200
timeout = 1000 * 10 # ten seconds

if parameter_setting == 2: # second static parameter setting
	scc_size_limit = 1000
	num_clause_limit = 200
	path_size_limit = 200
	timeout = 1000 * 1 # one second

o = Optimize()
o.set("timeout", timeout)
print('timeout = ',timeout/1000, 'seconds')

weight_map = {}


def compute_alpha_beta (scc_graphs):
	num_all_scc_edges = 0
	num_of_size_two_cycle_edges = 0
	num_edges_left_in_new_SCC = 0

	resulting_graph  = nx.DiGraph() # the resuling graph after computing SCC

	for s in scc_graphs:
		resulting_graph.add_edges_from(list(s.edges()))
		num_all_scc_edges += s.number_of_edges()
		edges_to_remove = set()
		for (l,r) in s.edges():
			if (r,l) in s.edges():
				edges_to_remove.add((l,r))
				edges_to_remove.add((r,l))

		num_of_size_two_cycle_edges += len (edges_to_remove)
		resulting_graph.remove_edges_from(list(edges_to_remove))

	sccs = nx.strongly_connected_components(resulting_graph)
	filter_scc = [x for x in sccs if len(x)>1]

	for f in filter_scc:
		num_edges_left_in_new_SCC += resulting_graph.subgraph(f).number_of_edges()

	alpha = num_of_size_two_cycle_edges / num_all_scc_edges
	beta = num_edges_left_in_new_SCC / num_all_scc_edges

	return (alpha, beta)


def compute_scc_gamma_delta (scc):
	alpha, beta = compute_alpha_beta([scc])
	gamma = (1- alpha + beta)/ 2 * (alpha +beta)
	delta = gamma * scc.number_of_edges()
	return gamma, delta

def compute_delta(sccs):
	# for each s in sccs, compute gamma
	delta_acc = 0
	for s in sccs:
		g, d = compute_scc_gamma_delta(s)
		delta_acc += d
	return delta_acc

def obtain_scc_graph ():
	global input_file_path
	global weight_map

	print ('init the graph in mode ', mode)
	print ('now read file ', input_file_path)
	graph = nx.DiGraph()
	if mode == '-u':
		with gzip.open(input_file_path, "rt") as f:

			line = f.readline()
			while line:
				row = line.split('\t')
				s = int(row[0]) # source
				t = int(row[1])
				# print (s,t)
				if s != t:
					graph.add_edge(s, t)
					# d.setdefault(s,[]).append(t)
				line = f.readline()
	elif mode == '-w':
		with gzip.open(input_file_path, "rt") as f:

			line = f.readline()
			while line:
				row = line.split('\t')
				w = int(row[0]) # source
				s = int(row[1]) # source
				t = int(row[2])
				# print (s,t)
				if s != t:
					graph.add_edge(s, t)
					weight_map[(s,t)] = w
					# d.setdefault(s,[]).append(t)
				line = f.readline()

	# sccs = tarjan(d)
	sccs = nx.strongly_connected_components(graph)

	filter_sccs = [x for x in sccs if len(x)>1]

	collect_scc_graph = []

	new_map = {}

	for f in filter_sccs:
		graph_f = graph.subgraph(f).copy()
		if mode == '-w':
			d = { your_key: weight_map[your_key] for your_key in graph_f.edges()}
			new_map.update(d)
		# remove all reflexive relations.
		for v in graph_f.nodes():
			try:
				graph_f.remove_edge(v,v)
			except Exception as e:
				pass
		collect_scc_graph.append(graph_f)

	weight_map = new_map

	return collect_scc_graph

# this function is to verify that all edges that participate in nested cycles are removed
# note: In this study, singleton graphs are allowed since they often don't hurt and can be easily removed.
def verify_removed_edges (my_removed_edges):
	global input_file_path
	global weight_map

	print ('init the graph in mode ', mode)
	print ('now read file ', input_file_path)
	graph = nx.DiGraph()
	if mode == '-u':
		with gzip.open(input_file_path, "rt") as f:

			line = f.readline()
			while line:
				row = line.split('\t')
				s = int(row[0]) # source
				t = int(row[1])
				# print (s,t)
				if s != t:
					graph.add_edge(s, t)
					# d.setdefault(s,[]).append(t)
				line = f.readline()
	elif mode == '-w':
		with gzip.open(input_file_path, "rt") as f:

			line = f.readline()
			while line:
				row = line.split('\t')
				w = int(row[0]) # source
				s = int(row[1]) # source
				t = int(row[2])
				# print (s,t)
				if s != t:
					graph.add_edge(s, t)
					weight_map[(s,t)] = w
					# d.setdefault(s,[]).append(t)
				line = f.readline()

	graph.remove_edges_from(my_removed_edges)


	sccs = nx.strongly_connected_components(graph)

	filter_sccs = [x for x in sccs if len(x)>1]

	collect_scc_graph = []

	new_map = {}

	for f in filter_sccs:
		graph_f = graph.subgraph(f).copy()
		if mode == '-w':
			d = { your_key: weight_map[your_key] for your_key in graph_f.edges()}
			new_map.update(d)
		# remove all reflexive relations.
		for v in graph_f.nodes():
			try:
				graph_f.remove_edge(v,v)
			except Exception as e:
				pass
		collect_scc_graph.append(graph_f)

	weight_map = new_map

	return collect_scc_graph # this should be [] if there is no cycle (expect reflexive ones)

# define a new partitioning function to tidy things up.
def partition_pymetis(graph, num_partitions = 2) :
	print ('partition starts')
	# obtain an index from 0 onwards.
	adjacency = {}

	ele_to_index = {}
	index_to_ele = {}

	index = 0

	for n in graph.nodes():
		if n not in ele_to_index.keys():
			ele_to_index[n] = index
			index_to_ele[index] = n
			index += 1
	print ('index = ', index)
	print ('which should be the same as num of nodes = ', graph.number_of_nodes())

	for n in graph.nodes():
		adjacency.setdefault(ele_to_index[n], [])

	for (m,n) in graph.edges():
		adjacency[ele_to_index[m]].append(ele_to_index[n])

	cuts, part_vert  = pymetis.part_graph(num_partitions, adjacency=adjacency)

	print ('cuts = ', cuts)

	all_edges_to_remove = []
	for (n,m) in graph.edges():
		index_n = ele_to_index[n]
		index_m = ele_to_index[m]
		if part_vert[index_n] != part_vert[index_m]:
			# remove
			all_edges_to_remove.append( (n,m) )
	print ('# edges removed: ', len (all_edges_to_remove))
	return all_edges_to_remove

# P1: the first graph partitioning strategy as described in the paper
def cut_to_limit(graph):

	if graph.number_of_nodes() < scc_size_limit:
		return [], [graph]

	graph = nx.DiGraph(graph) # otherwise, it would remain frozen, can't be modified

	all_edges_to_remove = []
	collect_subgraphs = []

	# we adopt the pymetis package for graph partitioning
	removed_edges = partition_pymetis(graph)
	all_edges_to_remove += removed_edges

	graph.remove_edges_from(removed_edges)
	sccs = nx.strongly_connected_components(graph)
	filter_sccs = [x for x in sccs if len(x)>1]
	for s in filter_sccs:
		scc_g = graph.subgraph(s).copy()
		if scc_g.number_of_nodes() > scc_size_limit:
			sg_edges_between_subgraphs, sg_subgraphs = cut_to_limit(scc_g)
			collect_subgraphs += sg_subgraphs
			all_edges_to_remove += sg_edges_between_subgraphs
		else:
			collect_subgraphs.append(scc_g)

	return all_edges_to_remove, collect_subgraphs # also need to return the removed edges


# P2: the second graph partitioning strategy as described in the paper

def cut_to_limit2(graph):
	encode = {}
	print ('tocut: at first, there are in total ', graph.number_of_nodes(), ' nodes with ', graph.number_of_edges())
	# now make decision for weighted cases:
	collect_relations_size_two_cycles = []
	for (l, r) in graph.edges():
		if (r, l) in graph.edges():
			collect_relations_size_two_cycles.append((l,r))

	print ('There are in total ', len (collect_relations_size_two_cycles), ' relations of size two')
	count_unequally_weighted = 0
	relations_to_remove = []
	for (l,r) in collect_relations_size_two_cycles:
		if (l, r) in weight_map.keys() and (r, l) in weight_map.keys():
			if weight_map[(l, r)] != weight_map[(r, l)]:
				count_unequally_weighted += 1
				if weight_map[(l, r)] < weight_map[(r, l)]:
					relations_to_remove.append((l, r))


	print ('There are ', count_unequally_weighted/2, ' such cases')
	print ('so a total of ', len (relations_to_remove), ' relations to remove')

	all_edges_to_remove = relations_to_remove
	graph.remove_edges_from(relations_to_remove)
	sg_edges_between_subgraphs, collect_subgraphs = cut_to_limit(graph)
	all_edges_to_remove += sg_edges_between_subgraphs

	return all_edges_to_remove, collect_subgraphs


def obtain_initial_sccs():
	scc_graphs = obtain_scc_graph()

	coll_to_remove = []
	coll_to_add = []
	coll_edges_removed = []
	for g in scc_graphs:

		if g.number_of_nodes() > scc_size_limit:
			removed_edges = []
			gs = []
			if strategy_partitioning == 'P1':
				removed_edges, gs = cut_to_limit (g)
			elif strategy_partitioning == 'P2':
				removed_edges, gs = cut_to_limit2 (g)
			else:
				print ('error !!')

			coll_edges_removed += removed_edges
			coll_to_add += gs
			coll_to_remove.append(g)
	try:
		for g in coll_to_remove:
			scc_graphs.remove(g)
		for g in coll_to_add:
			scc_graphs.append(g)

	except Exception as e:
		print ('remove & append')

	print ('total edges removed after cutting: ', len (coll_edges_removed))
	return scc_graphs, coll_edges_removed



def obtained_edges_to_remove_using_SMT (sg):
	global num_clause_limit
	global timeout

	count = 0
	collect_cycles = []
	encode = {}
	# please ignore this dynamic setting for now. It's still to be explored.
	if parameter_setting == 0: # dynamic setting
		# compute the gamma and delta
		gamma, delta = compute_scc_gamma_delta(sg)
		timeout = int(1000* 20 * gamma + 1000)
		num_clause_limit = int (10 + delta)

	if len(sg.nodes) == 2:
		[l ,r] = list(sg.nodes())
		collect_cycles.append([l,r])
		count+=1
	else:
		if strategy_cycle_sampling == 'S1':
			# strategy 1: focus on edges: each edge and their counter corresponding cycle !
			edges_to_visit = set(sg.edges())
			while (len(edges_to_visit) != 0 and count < num_clause_limit):
				(l,r) =  edges_to_visit.pop()
				c = nx.shortest_path(G = sg, source = r, target=l)
				cycle_edge_set = set()
				for i in range(len(c) -1):
					j = i+1
					if (c[i], c[j]) in edges_to_visit:
						cycle_edge_set.add((c[i], c[j]))
				collect_cycles.append(c)

				count += 1
				edges_to_visit = edges_to_visit.difference(cycle_edge_set)

		elif strategy_cycle_sampling == 'S2':
		# strategy 2: focus on nodes: obtain a random pair and each l2r , r2l
			collect_nodes_visited_set = set()
			pct_covered = 0
			while count < num_clause_limit and pct_covered < 0.80: # replace the 20% constraint
				l = random.choice(list(sg.nodes()))
				r = random.choice(list(sg.nodes()))

				if l != r:
					l2r = nx.shortest_path(G = sg, source = l, target = r)
					r2l = nx.shortest_path(G = sg, source = r, target = l)
					c = l2r[:-1] + r2l[:-1]
					collect_cycles.append(c)
					collect_nodes_visited_set = collect_nodes_visited_set.union(set(c))
					pct_covered = len (collect_nodes_visited_set) / sg.number_of_nodes()
					count += 1

	o = Optimize()

	o.set("timeout", timeout)

	for cycle in collect_cycles:
		clause = False #
		for i in range(len(cycle)):
			j = i +1
			if j == len(cycle):
				j =0
			left = cycle[i]
			right = cycle[j]
			encode_string = '<'+str(left) + '\t' + str(right) +'>'

			if (left, right) not in encode:
				encode[(left, right)] = Bool(str(encode_string))

			#propositional variable
			p = encode[(left, right)]
			# append the negotiation of this propositional variable
			clause = Or(clause, Not(p))
		o.add (clause)

	# when there is no weight specified.
	for e in encode.keys():
		ecd = encode[e]
		if mode =='-u':
			o.add_soft(ecd, 1)
		elif mode == '-w':
			w = weight_map[e]
			o.add_soft(ecd, w)
	identified_edges = []
	if o.check() == 'unknown':
		print ('WhAT!!!')
		num_clause_limit -= 20
		print ('reduce clause limit to ', num_clause_limit)
		return []
	else:
		m = o.model()
		for arc in encode.keys():
			(left, right) = arc
			if m.evaluate(encode[arc]) == False:
				identified_edges.append(arc)

	return identified_edges




def main ():
	global input_file_path
	global mode
	global strategy_cycle_sampling
	global strategy_partitioning
	global parameter_setting
	global mode

	mode = sys.argv[1]
	input_file_path = sys.argv[2]
	strategy_partitioning = sys.argv[3]
	strategy_cycle_sampling = sys.argv[4]
	print ('mode = ', mode)
	print ('input_file_path = ' , input_file_path)

	start = time.time()
	# ==============
	all_removed_edges = []
	graphs_obtained, edges_removed_in_cutting = obtain_initial_sccs()
	all_removed_edges += edges_removed_in_cutting

	# now resolve each graph (instead of SCC)
	round = 1
	while len(graphs_obtained) != 0:
		print ('this is round ', round)
		round += 1
		new_graphs_to_work_on = []
		for g in graphs_obtained:
			if g.number_of_nodes() > 200:
				print ('working on ', len (g))
			edges_removed_by_SMT = obtained_edges_to_remove_using_SMT (g)
			g.remove_edges_from(edges_removed_by_SMT)
			sccs = nx.strongly_connected_components(g)
			filter_sccs = [x for x in sccs if len(x)>1]
			for s in filter_sccs:
				if g.number_of_nodes() > 200 and len (s) > 30:
					print ('\tit was decomposed to: ', len (s))
				new_graphs_to_work_on.append(g.subgraph(s).copy())
			all_removed_edges += edges_removed_by_SMT
		graphs_obtained = new_graphs_to_work_on

	print ('there are in total ', len (all_removed_edges), 'edges removed')
	# ===============
	end = time.time()
	hours, rem = divmod(end-start, 3600)
	minutes, seconds = divmod(rem, 60)
	print("Time taken: {:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds))
	print ('partitioning strategy = ', strategy_partitioning)
	print ('sampling strategy = ', strategy_cycle_sampling)
	print ('scc_size_limit = ', scc_size_limit)
	print ('num_clause_limit = ', num_clause_limit)
	print ('now export all these edges:')

	# ***** output for table 2
	output_filename = ''
	# if parameter_setting == 1:
	# 	output_filename += './setting_XL/'
	# elif parameter_setting == 2:
	# 	output_filename += './setting_L/'
	# elif parameter_setting == 0:
	# 	output_filename += './setting_dynamic/'


	# ***** output for table 3
	output_filename += './table3/'

	if mode == '-u':
		output_filename += 'unweighted2/'
	elif mode == '-w':
		if 'ounted' in input_file_path:
			output_filename += 'counted2/'
		elif 'nferred' in input_file_path:
			output_filename += 'inferred2/'



	extra = ''
	if 'nferred' in input_file_path: # inferred or Inferred
		extra = '_weightsInferred'
	elif 'ounted' in input_file_path: # counted or Counted
		extra ='_weightsCounted'

	if 'lass' in input_file_path:
		output_filename += 'rdfs_subClassOf_removed_edges_'+strategy_partitioning + strategy_cycle_sampling + extra
	elif 'broader' in input_file_path:
 		output_filename += 'skos_broader_removed_edges_'+strategy_partitioning + strategy_cycle_sampling + extra
	elif 'dbo_isPartOf' in input_file_path:
		output_filename += 'dbo_isPartOf_removed_edges_'+strategy_partitioning + strategy_cycle_sampling + extra
	elif 'narrower' in input_file_path:
		output_filename += 'skos_narrower_removed_edges_'+strategy_partitioning + strategy_cycle_sampling + extra
	elif 'dbo_isPartOf' in input_file_path:
		output_filename += 'dbo_isPartOf_removed_edges_'+strategy_partitioning + strategy_cycle_sampling + extra
	elif 'dbo_previousWork' in input_file_path:
		output_filename += 'dbo_previousWork_removed_edges_'+strategy_partitioning + strategy_cycle_sampling + extra
	elif 'dbo_subsequentWork' in input_file_path:
		output_filename += 'dbo_subsequentWork_removed_edges_'+strategy_partitioning + strategy_cycle_sampling + extra
	elif 'dbo_successor' in input_file_path:
		output_filename += 'dbo_successor_removed_edges_'+strategy_partitioning + strategy_cycle_sampling + extra
	elif 'dbo_predecessor' in input_file_path:
		output_filename += 'dbo_predecessor_removed_edges_'+strategy_partitioning + strategy_cycle_sampling + extra
	elif 'dbo_parent' in input_file_path:
		output_filename += 'dbo_parent_removed_edges_'+strategy_partitioning + strategy_cycle_sampling + extra
	elif 'sioc_parent_of' in input_file_path:
		output_filename += 'sioc_parent_of_removed_edges_'+strategy_partitioning + strategy_cycle_sampling + extra

	print ('output file name: ', output_filename)
	outputfile = open(output_filename, 'w+', newline='')
	writer = csv.writer(outputfile, delimiter='\t')
	for (left,right) in all_removed_edges:
		# print ('l and r: ', l, r)
		writer.writerow([left, right])

	# Please uncomment these two following lines to validate your results.
	# hint: it takes less than one minute for skos:broader

	# scc_graphs = verify_removed_edges (all_removed_edges)
	# print ('Validating....there should be zero SCC: ', len (scc_graphs))

if __name__ == "__main__":
	main()
