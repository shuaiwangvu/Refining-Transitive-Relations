
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
# from bidict import bidict
import matplotlib.pyplot as plt
import tldextract
import json
# import random
# from equiClass import equiClassManager
import random
from tarjan import tarjan
from collections import Counter
from bidict import bidict

path = "../data-gold-standard-subclass-broader/"
broader_file = "broader_edgelist.gz"
subclass_file = "subclass_edgelist.gz"

subclass_weight = "subclass_edgelist_weight_reduced.gz"
broader_weight = "broader_edgelist_weight_reduced.gz"

graph = nx.DiGraph()
collect_nodes = set()
can_remove = set()
weight = {}

scc_size_limit = 2000

timeout = 1000 * 60 * 1
o = Optimize()
o.set("timeout", timeout)
print('timeout = ',timeout/1000/60, 'mins')

num_clause_limit = 4000
encode = {}

path_size_limit = 20

edges_to_remove = []

d = {}

#

def compute_scc_from_graph(g):
	dict = {}
	for n in g.nodes:
		collect_succssor = []
		for s in g.successors(n):
			collect_succssor.append(s)
		dict[n] = collect_succssor
	return tarjan(dict)


def obtain_scc_graph ():
	global collect_nodes
	global can_remove
	global d

	print ('init the graph') 

	with gzip.open(path + subclass_file, "rt") as f:

		line = f.readline()
		while line:
			row = line.split('\t')
			s = int(row[0]) # source
			t = int(row[1])
			# print (s,t)
			if s != t:
				d.setdefault(s,[]).append(t)
			line = f.readline()
	sccs = tarjan(d)
	filter_sccs = [x for x in sccs if len(x)>1]
	filter_sccs =  sorted (filter_sccs, key=(lambda x: len(x)), reverse=False)
	G = nx.DiGraph(d)
	collect_scc_graph = []
	for f in filter_sccs:
		graph_f = G.subgraph(f).copy()
		collect_scc_graph.append(graph_f)

	return collect_scc_graph



def cut_to_limit(graph):
	if graph.number_of_nodes() < scc_size_limit:
		return [], [graph]

	graph = nx.DiGraph(graph) # otherwise, it would remain frozen, can't be modified
	# print ('cut this scc size = ', graph.number_of_nodes())
	adjacency = {}

	ele_to_index = {}
	index_to_ele = {}
	# num_partitions = int((graph.number_of_nodes() / scc_size_limit)) + 1
	num_partitions = 2
	# print ('cut into ', num_partitions, ' partitions')

	index = 0

	# for n in graph.nodes():
	# 	if n not in ele_to_index.keys():
	# 		ele_to_index[n] = index
			# index_to_ele[index] = n

	for (m,n) in graph.edges():
		if m not in ele_to_index.keys():
			ele_to_index[m] = index
			index_to_ele[index] = m
			index += 1
		if n not in ele_to_index.keys():
			ele_to_index[n] = index
			index_to_ele[index] = n
			index += 1

	for n in graph.nodes():
		if n not in ele_to_index.keys():
			ele_to_index[n] = index
			index_to_ele[index] = n
			index += 1



	for m in graph.nodes():
		adjacency.setdefault(ele_to_index[m], [])

	for (m,n) in graph.edges():
		adjacency[ele_to_index[m]].append(ele_to_index[n])

	# print ('adj size = ', len(adjacency.keys()), flush=True)

	# except  Exception as e:
	# 	print ('bidict-> ', e, flush=True)

	# try:
	# print ('adj= ', adjacency)
	# print ('index_to_ele: ', index_to_ele)
	cuts, part_vert  = pymetis.part_graph(num_partitions, adjacency=adjacency)

	# print ('cuts: ', cuts, flush=True)
	# print ('part_vert', part_vert, flush=True)
	#
	# except Exception as e:
	# 	print ('pymetis: ',e, flush=True)
	subgraphs = []


	for c in range(num_partitions):
		col_nodes = []
		for p in range(len(part_vert)):
			if part_vert[p] == c:
				if p not in index_to_ele.keys():
					print ('****cannot find p=', p, flush=True)
				else:
					col_nodes.append(index_to_ele[p])
					if index_to_ele[p] not in graph.nodes():
						print ('found error: ', index_to_ele[p])

		# print (c, ' has size ', len(col_nodes))
		# print ('set node intersection: ', list(set(graph.nodes).intersection(set(col_nodes))))
		tmp_g = graph.subgraph(col_nodes).copy()
		# print ('this subgraph has edges: ', len(tmp_g.edges))
		subgraphs.append(tmp_g)

	try:
		# print ('total subgraphs:', len(subgraphs))
		col_edges = []
		for sg in subgraphs:
			col_edges += list(sg.edges())
		# print ('should remove (subgraphs)', len(col_edges))
		graph.remove_edges_from(col_edges)
		edges_between_subgraphs = list(graph.edges()) # those edges left
		# print ('confused : ', len(edges_between_subgraphs))
	except Exception as e:
		print ('******* exception : ', e)



	collect_subgraphs = []
	collect_subgraphs_removed_edges = []
	for sg in subgraphs:
		if sg.number_of_nodes() > scc_size_limit:
			# sg_edges_between_subgraphs, sg_subgraphs = cut_to_limit(sg)
			# collect_subgraphs += sg_subgraphs
			# collect_subgraphs_removed_edges += sg_edges_between_subgraphs
			#TODO: use the SCC instead!
			sccs = compute_scc_from_graph(sg)
			filter_sccs = [x for x in sccs if len(x)>1]
			for s in filter_sccs:
				scc_g = sg.subgraph(s).copy()
				if scc_g.number_of_nodes() > scc_size_limit:
					sg_edges_between_subgraphs, sg_subgraphs = cut_to_limit(scc_g)
					collect_subgraphs += sg_subgraphs
					collect_subgraphs_removed_edges += sg_edges_between_subgraphs
				else:
					collect_subgraphs.append(scc_g)
		else:
			sccs = compute_scc_from_graph(sg)
			filter_sccs = [x for x in sccs if len(x)>1]
			for s in filter_sccs:
				scc_g = sg.subgraph(s).copy()
				collect_subgraphs.append(scc_g)
	all_edges_to_remove = edges_between_subgraphs + collect_subgraphs_removed_edges
	# print ('there are in total ', len (all_edges_to_remove), ' removed during graph partitioning')
	return all_edges_to_remove, collect_subgraphs # also need to return the removed edges


def cut_to_limit2(graph):
	print ('tocut: there are in total ', graph.number_of_nodes(), ' nodes with ', graph.number_of_edges())

	if graph.number_of_nodes() < scc_size_limit:
		return [], [graph]

	graph = nx.DiGraph(graph)

	best_source_node = None
	max_outdegree = 0
	best_target_node = None
	max_indegree = 0

	for n in graph.nodes():
		out_degree = graph.out_degree(n)
		in_degree = graph.in_degree(n)
		if out_degree > max_outdegree:
			best_source_node = n
			max_outdegree = out_degree
		if in_degree > max_indegree and n != best_source_node:
			best_target_node = n
			max_indegree = in_degree

	o = Optimize()
	count_clause = 0
	# print ('found best_source_node = ', best_source_node, ' best_target_node = ', best_target_node )
	for path in nx.all_simple_paths(G=graph, source = best_source_node, target = best_target_node, cutoff= path_size_limit):

		# print ('\t path = ', path)
		clause = False #
		for i in range(len(path) - 1):
			j = i +1

			left = path[i]
			right = path[j]
			encode_string = '<'+str(left) + '\t' + str(right) +'>'

			if (left, right) not in encode:
				encode[(left, right)] = Bool(str(encode_string))
			clause = Or (clause, Not(encode[(left, right)]))

		o.add (clause)
		count_clause += 1
		if count_clause >= num_clause_limit :
			break


	# print ('there are in total: ', count_clause, 'clauses / path between the source & target')

	# when there is no weight specified.
	for e in encode.values():
		o.add_soft(e, 1)
	# print ('ending encode length ', len(encode.keys()))
	# print ('all clauses encoded', flush = True)
	identified_edges = []
	if o.check() == 'unknown':
		print ('WhAT!!!')
		return [],[]
	else:
		# print ('start decoding')
		# print ('>encode length ', len(encode.keys()))
		m = o.model()
		for arc in encode.keys():
			(left, right) = arc
			if m.evaluate(encode[arc]) == False:
				identified_edges.append(arc)

	graph.remove_edges_from(identified_edges)

	collect_subgraphs = []
	collect_subgraphs_removed_edges = []
	sccs = compute_scc_from_graph(graph)
	filter_sccs = [x for x in sccs if len(x)>1]
	for s in filter_sccs:
		scc_g = graph.subgraph(s).copy()
		if scc_g.number_of_nodes() > scc_size_limit:
			sg_edges_between_subgraphs, sg_subgraphs = cut_to_limit(scc_g)
			collect_subgraphs += sg_subgraphs
			collect_subgraphs_removed_edges += sg_edges_between_subgraphs
		else:
			collect_subgraphs.append(scc_g)

	all_edges_to_remove = collect_subgraphs_removed_edges + identified_edges
	# print ('there are in total ', len (all_edges_to_remove), ' removed during graph partitioning')
	return all_edges_to_remove, collect_subgraphs # also need to return the removed edges




def obtain_sccs():
	scc_graphs = obtain_scc_graph()

	coll_to_remove = []
	coll_to_add = []
	coll_edges_removed = []
	print ('start cutting')
	for g in scc_graphs:
		if g.number_of_nodes() > scc_size_limit:
			# removed_edges, gs = cut_to_limit (g)
			removed_edges, gs = cut_to_limit2 (g)
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

	count = 0
	collect_cycles = []
	encode = {}
	if len(sg.nodes) == 2:
		for (l,r) in sg.edges():
			collect_cycles.append([l,r])
		count+=2
	else:

# strategy 1:  each edge and their counter corresponding cycle !
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

# strategy 2: obtain a random pair and each l2r , r2l
		# while count < num_clause_limit:
		# 	l = random.choice(list(sg.nodes()))
		# 	r = random.choice(list(sg.nodes()))
		#
		# 	if l != r:
		# 		l2r = nx.shortest_path(G = sg, source = l, target = r)
		# 		r2l = nx.shortest_path(G = sg, source = r, target = l)
		# 		# print ('l2r: ', l2r)
		# 		# print ('r2l: ', r2l)
		# 		c = l2r[:-1] + r2l[:-1]
		# 		# print ('l2r2l: ',c, flush=True)
		# 		collect_cycles.append(c)
		# 		count += 1

# strategy 3: all path from big outgoing hubs to incoming hubs, and back.










	o = Optimize()

	for cycle in collect_cycles:
		# print ('now encode  cycle: ', cycle )
		clause = False #
		for i in range(len(cycle)):
			j = i +1
			if j == len(cycle):
				j =0
			# i and j
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
	for e in encode.values():
		o.add_soft(e, 1)
	# print ('ending encode length ', len(encode.keys()))
	# print ('all clauses encoded', flush = True)
	identified_edges = []
	if o.check() == 'unknown':
		print ('WhAT!!!')
		num_clause_limit -= 20
		print ('reduce clause limit to ', num_clause_limit)
		return []
	else:
		# print ('start decoding')
		# print ('>encode length ', len(encode.keys()))
		m = o.model()
		for arc in encode.keys():
			(left, right) = arc
			if m.evaluate(encode[arc]) == False:
				identified_edges.append(arc)

	return identified_edges




def main ():
	global graph
	global edges_to_remove

	start = time.time()
	# ==============
	all_removed_edges = []
	graphs_obtained, edges_removed_in_cutting = obtain_sccs()
	all_removed_edges += edges_removed_in_cutting

	# now resolve each graph (instead of SCC)
	round = 1
	while len(graphs_obtained) != 0:
		print ('this is round ', round)
		round += 1
		graphs_obtained = sorted(graphs_obtained, key=(lambda g: g.number_of_nodes()), reverse=True)
		print ('there are still ', len (graphs_obtained), ' graphs to be processed')
		if len (graphs_obtained)> 20:
			print ('the biggest one has       : ', graphs_obtained[0].number_of_nodes(), ' with ' ,
	 												graphs_obtained[0].number_of_edges(), )
			print ('the second biggest one has: ', graphs_obtained[1].number_of_nodes(), ' with ' ,
													graphs_obtained[1].number_of_edges(), )

		for g in graphs_obtained:
			edges_removed_by_SMT = obtained_edges_to_remove_using_SMT (g)
			g.remove_edges_from(edges_removed_by_SMT)
			sccs = compute_scc_from_graph(g)
			filter_sccs = [x for x in sccs if len(x)>1]
			for s in filter_sccs:
				graphs_obtained.append(g.subgraph(s).copy())
			graphs_obtained.remove(g)
			all_removed_edges += edges_removed_by_SMT

	print ('there are in total ', len (all_removed_edges), 'edges removed')
	# ===============
	end = time.time()
	hours, rem = divmod(end-start, 3600)
	minutes, seconds = divmod(rem, 60)
	print("Time taken: {:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds))

if __name__ == "__main__":
	main()
