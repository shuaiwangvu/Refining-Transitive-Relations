# python submassive_final.py -u ../data-gold-standard/subclass_edgelist.gz P1 S1
# python submassive_final.py -w ../data-gold-standard/rdfs_subClassOf_edgelist_inferred.gz P1 S1
# python submassive_final.py -w ../data-gold-standard/skos_broader_edgelist_counted.gz P2 S1
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
# from bidict import bidict
import matplotlib.pyplot as plt
import tldextract
import json
# import random
# from equiClass import equiClassManager
import random
# from tarjan import tarjan
from collections import Counter
from bidict import bidict

# path = "../data-gold-standard-subclass-broader/"
# broader_file = "broader_edgelist.gz"
# subclass_file = "subclass_edgelist.gz"
#
# subclass_weight = "subclass_edgelist_weight_reduced.gz"
# broader_weight = "broader_edgelist_weight_reduced.gz"

mode = '' # either weighted or unweighted
input_file_path = ''
strategy_partitioning = ''
strategy_cycle_sampling = ''



# graph = nx.DiGraph()
collect_nodes = set()
can_remove = set()


scc_size_limit = 15000
num_clause_limit = 3000
path_size_limit = 200
timeout = 1000 * 10
o = Optimize()
o.set("timeout", timeout)
print('timeout = ',timeout/1000/60, 'mins')

weight_map = {}

# edges_to_remove = []

# d = {}

#
#
# def compute_scc_from_graph(g):
# 	dict = {}
# 	for n in g.nodes:
# 		collect_succssor = []
# 		for s in g.successors(n):
# 			collect_succssor.append(s)
# 		dict[n] = collect_succssor
# 	return tarjan(dict)


def obtain_scc_graph ():
	# global collect_nodes
	# global can_remove
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
	# filter_sccs =  sorted (filter_sccs, key=(lambda x: len(x)), reverse=True)
	# G = nx.DiGraph(d)

	# let's reduce the size of this map.
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
					print ('****cannot find p =', p, flush=True)
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
			sccs = nx.strongly_connected_components(sg)
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
			sccs = nx.strongly_connected_components(sg)
			filter_sccs = [x for x in sccs if len(x)>1]
			for s in filter_sccs:
				scc_g = sg.subgraph(s).copy()
				collect_subgraphs.append(scc_g)

	all_edges_to_remove = edges_between_subgraphs + collect_subgraphs_removed_edges
	# print ('there are in total ', len (all_edges_to_remove), ' removed during graph partitioning')
	return all_edges_to_remove, collect_subgraphs # also need to return the removed edges

# first make decisions on some relations in size-two cycles:
# 1) For the weighted cases with unequal weights on each relation.

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
	# to_be_randomly_decided = []
	for (l,r) in collect_relations_size_two_cycles:
		if (l, r) in weight_map.keys() and (r, l) in weight_map.keys():
			if weight_map[(l, r)] != weight_map[(r, l)]:
				count_unequally_weighted += 1
				if weight_map[(l, r)] < weight_map[(r, l)]:
					relations_to_remove.append((l, r))

		# else:
		# 	if l < r :
		# 		to_be_randomly_decided.append((l, r))
		# 	else:
		# 		to_be_randomly_decided.append((r, l))
	# for (l,r) in to_be_randomly_decided:
	# 	if random.random() > 0.5:
	# 		relations_to_remove.append((l,r))
	# 	else:
	# 		relations_to_remove.append((r,l))

	print ('There are ', count_unequally_weighted/2, ' such cases')
	print ('so a total of ', len (relations_to_remove), ' relations to remove')

	all_edges_to_remove = relations_to_remove
	graph.remove_edges_from(relations_to_remove)
	sg_edges_between_subgraphs, collect_subgraphs = cut_to_limit(graph)
	all_edges_to_remove += sg_edges_between_subgraphs

	return all_edges_to_remove, collect_subgraphs
	#
	#
	# if graph.number_of_nodes() < scc_size_limit:
	# 	return [], [graph]
	#
	# graph = nx.DiGraph(graph)
	#
	#
	# if best_source_node ==  None or best_source_node not in graph :
	# 	max_outdegree = 0
	# 	for n in graph.nodes():
	# 		out_degree = graph.out_degree(n)
	# 		if out_degree > max_outdegree:
	# 			best_source_node = n
	# 			max_outdegree = out_degree
	#
	# if best_target_node ==  None or best_target_node not in graph :
	# 	max_indegree = 0
	# 	for n in graph.nodes():
	# 		in_degree = graph.in_degree(n)
	# 		if in_degree > max_indegree and n != best_source_node:
	# 			best_target_node = n
	# 			max_indegree = in_degree
	#
	# o = Optimize()
	# o.set("timeout", timeout)
	# # print ('found best_source_node = ', best_source_node, ' best_target_node = ', best_target_node )
	#
	# # for path in nx.all_simple_paths(G=graph, source = best_source_node, target = best_target_node, cutoff= path_size_limit):
	# # 	# num_clauses_encoded+=1
	# # 	print ('\t path = ', path)
	# # 	clause = False #
	# # 	for i in range(len(path) - 1):
	# # 		j = i +1
	# #
	# # 		left = path[i]
	# # 		right = path[j]
	# # 		encode_string = '<'+str(left) + '\t' + str(right) +'>'
	# #
	# # 		if (left, right) not in encode:
	# # 			encode[(left, right)] = Bool(str(encode_string))
	# # 		clause = Or (clause, Not(encode[(left, right)]))
	# #
	# # 	o.add (clause)
	# # 	count_clause += 1
	# # 	if count_clause >= num_clause_limit :
	# # 		break
	# count_clause = 0
	# while count_clause <= num_clause_limit:
	# # for n in graph.nodes():
	# 	n = random.choice(list(graph.nodes()))
	# 	path1 = nx.shortest_path(G =graph, source=best_source_node, target=n)
	# 	# if len(path) > 10:
	# 	# 	clause = False
	# 	# 	for i in range(len(path) - 1):
	# 	# 		j = i +1
	# 	#
	# 	# 		left = path[i]
	# 	# 		right = path[j]
	# 	# 		encode_string = '<'+str(left) + '\t' + str(right) +'>'
	# 	#
	# 	# 		if (left, right) not in encode:
	# 	# 			encode[(left, right)] = Bool(str(encode_string))
	# 	# 		clause = Or (clause, Not(encode[(left, right)]))
	# 	#
	# 	# 	o.add (clause)
	# 	# 	count_clause += 1
	#
	# 	# print ('in the loop')
	# 	path2 = nx.shortest_path(G =graph, source=n, target=best_target_node)
	# 	# if len(path) > 10:
	#
	# 	# print ('path1 = ', path1)
	# 	# print ('path2 = ', path2)
	# 	path = path1 + path2[1:]
	#
	# 	if len (path) > 10 :
	# 		# print ('path = ',path)
	# 		clause = False
	# 		for i in range(len(path) - 1):
	# 			j = i +1
	#
	# 			left = path[i]
	# 			right = path[j]
	# 			encode_string = '<'+str(left) + '\t' + str(right) +'>'
	#
	# 			if (left, right) not in encode:
	# 				encode[(left, right)] = Bool(str(encode_string))
	# 			clause = Or (clause, Not(encode[(left, right)]))
	#
	# 			o.add (clause)
	# 		count_clause += 1
	# 	if  count_clause >= num_clause_limit :
	# 		break
	#
	# print ('there are in total: ',  count_clause, 'clauses from a random node to a target')
	#
	# # when there is no weight specified.
	# for e in encode.keys():
	# 	ecd = encode[e]
	# 	if mode =='-u':
	# 		o.add_soft(ecd, 1)
	# 	elif mode == '-w':
	# 		w = weight_map[e]
	# 		o.add_soft(ecd, w)
	# # print ('ending encode length ', len(encode.keys()))
	# # print ('all clauses encoded', flush = True)
	# identified_edges = []
	# if o.check() == 'unknown':
	# 	print ('WhAT!!!')
	# 	return [],[]
	# else:
	# 	# print ('start decoding')
	# 	# print ('>encode length ', len(encode.keys()))
	# 	m = o.model()
	# 	for arc in encode.keys():
	# 		(left, right) = arc
	# 		if m.evaluate(encode[arc]) == False:
	# 			identified_edges.append(arc)
	#
	# graph.remove_edges_from(identified_edges)
	# print ('this round removes some edges = ', len (identified_edges))
	# collect_subgraphs = []
	# collect_subgraphs_removed_edges = []
	# sccs = nx.strongly_connected_components(graph)
	# filter_sccs = [x for x in sccs if len(x)>1]
	# for s in filter_sccs:
	# 	scc_g = graph.subgraph(s).copy()
	# 	if scc_g.number_of_nodes() > scc_size_limit:
	# 		sg_edges_between_subgraphs, sg_subgraphs = cut_to_limit2(scc_g, best_source_node=best_source_node, best_target_node=best_target_node)
	# 		collect_subgraphs += sg_subgraphs
	# 		collect_subgraphs_removed_edges += sg_edges_between_subgraphs
	# 	else:
	# 		collect_subgraphs.append(scc_g)
	#
	# all_edges_to_remove = collect_subgraphs_removed_edges + identified_edges
	# print ('there are in total ', len (all_edges_to_remove), ' removed during graph partitioning')
	# return all_edges_to_remove, collect_subgraphs # also need to return the removed edges
	#
	#


def obtain_sccs():
	scc_graphs = obtain_scc_graph()

	# print ('start plt: ', scc_graphs[4].number_of_nodes())
	# plt.figure()
	# nx.draw_kamada_kawai(scc_graphs[4])
	# plt.show()

	# how many such nodes have only one in, one out degree?
	# count = 0
	# g = scc_graphs[0]
	# for n in g.nodes():
	# 	if g.out_degree(n) == 1 and g.in_degree(n) == 1:
	# 		count += 1
	# print ('count = ', count, ' that amounts to ', count/g.number_of_nodes())


	coll_to_remove = []
	coll_to_add = []
	coll_edges_removed = []
	print ('start cutting')
	for g in scc_graphs:
		# print ('clustering : ', nx.average_clustering(G= g))

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

	count = 0
	collect_cycles = []
	encode = {}
	if len(sg.nodes) == 2:
		# [left, right] =  random.choice(list(sg.edges()))
		# return [(left, right)]
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
			while count < num_clause_limit and pct_covered <= 0.2:
				l = random.choice(list(sg.nodes()))
				r = random.choice(list(sg.nodes()))

				if l != r:
					l2r = nx.shortest_path(G = sg, source = l, target = r)
					r2l = nx.shortest_path(G = sg, source = r, target = l)
					# print ('l2r: ', l2r)
					# print ('r2l: ', r2l)
					c = l2r[:-1] + r2l[:-1]
					# print ('l2r2l: ',c, flush=True)
					collect_cycles.append(c)
					collect_nodes_visited_set = collect_nodes_visited_set.union(set(c))
					pct_covered = len (collect_nodes_visited_set) / sg.number_of_nodes()
					# print ('count = ', count , ' covers ', pct_covered)
					count += 1


		# 		# TODO: But is this representative enough? YES: it covers over 99% when there are 4000 clauses for 2000 size limit on nodes
		# 		pct_covered = len(collect_nodes_visited_set)/sg.number_of_nodes()
		#
			# if sg.number_of_nodes() > 200:
			# 	print (' sg nodes: ', sg.number_of_nodes(), count, ' covers ', pct_covered)
		# evaluate how many nodes were covered.
			# st_nodes = set(sg.nodes())
			# remain_nodes = st_nodes.difference(collect_nodes_visited_set)
			# print ('total: ', len (st_nodes), ' remain:', len (remain_nodes))
			# print ('covered:', len (collect_nodes_visited_set), ' = ',
			# 		len(collect_nodes_visited_set)/len(st_nodes))
			#


	o = Optimize()
	o.set("timeout", timeout)

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
	for e in encode.keys():
		ecd = encode[e]
		if mode =='-u':
			o.add_soft(ecd, 1)
		elif mode == '-w':
			w = weight_map[e]
			o.add_soft(ecd, w)
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
	# global graph
	# global edges_to_remove
	global input_file_path
	global mode
	global strategy_cycle_sampling
	global strategy_partitioning

	mode = sys.argv[1]
	input_file_path = sys.argv[2]
	strategy_partitioning = sys.argv[3]
	strategy_cycle_sampling = sys.argv[4]
	print ('mode = ', mode)
	print ('input_file_path = ' , input_file_path)
	print ('partitioning strategy = ', strategy_partitioning)
	print ('sampling strategy = ', strategy_cycle_sampling)

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
		# graphs_obtained = sorted(graphs_obtained, key=(lambda g: g.number_of_nodes()), reverse=True)
		# print ('there are still ', len (graphs_obtained), ' graphs to be processed')



		# if len (graphs_obtained)> 20:
		# 	print ('the biggest one has       : ', graphs_obtained[0].number_of_nodes(), ' with ' ,
	 	# 											graphs_obtained[0].number_of_edges(), )
		# 	print ('the second biggest one has: ', graphs_obtained[1].number_of_nodes(), ' with ' ,
		# 											graphs_obtained[1].number_of_edges(), )
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
			# graphs_obtained.remove(g)
			# graphs_to_remove.append(g)
			all_removed_edges += edges_removed_by_SMT
		# for g in graphs_to_remove:
			# graphs_obtained.remove(g)

		graphs_obtained = new_graphs_to_work_on

	print ('there are in total ', len (all_removed_edges), 'edges removed')
	# ===============
	end = time.time()
	hours, rem = divmod(end-start, 3600)
	minutes, seconds = divmod(rem, 60)
	print("Time taken: {:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds))

	print ('now export all these edges:')
	# the name of exported edges:
	output_filename = ''

	extra = ''
	if 'nferred' in input_file_path: # inferred or Inferred
		extra = '_weightsInferred'
	elif 'ounted' in input_file_path: # counted or Counted
		extra ='_weightsCounted'

	if 'lass' in input_file_path:
		output_filename = 'rdfs_subClassOf_removed_edges_'+strategy_partitioning + strategy_cycle_sampling + extra
	elif 'broader' in input_file_path:
 		output_filename = 'skos_broader_removed_edges_'+strategy_partitioning + strategy_cycle_sampling + extra
	elif 'dbo_isPartOf' in input_file_path:
		output_filename = 'dbo_isPartOf_removed_edges_'+strategy_partitioning + strategy_cycle_sampling + extra
	elif 'narrower' in input_file_path:
		output_filename = 'skos_narrower_removed_edges_'+strategy_partitioning + strategy_cycle_sampling + extra
	elif 'dbo_isPartOf' in input_file_path:
		output_filename = 'dbo_isPartOf_removed_edges_'+strategy_partitioning + strategy_cycle_sampling + extra
	elif 'dbo_previousWork' in input_file_path:
		output_filename = 'dbo_previousWork_removed_edges_'+strategy_partitioning + strategy_cycle_sampling + extra
	elif 'dbo_subsequentWork' in input_file_path:
		output_filename = 'dbo_subsequentWork_removed_edges_'+strategy_partitioning + strategy_cycle_sampling + extra
	elif 'dbo_successor' in input_file_path:
		output_filename = 'dbo_successor_removed_edges_'+strategy_partitioning + strategy_cycle_sampling + extra
	elif 'dbo_predecessor' in input_file_path:
		output_filename = 'dbo_predecessor_removed_edges_'+strategy_partitioning + strategy_cycle_sampling + extra
	elif 'dbo_parent' in input_file_path:
		output_filename = 'dbo_parent_removed_edges_'+strategy_partitioning + strategy_cycle_sampling + extra
	elif 'sioc_parent_of' in input_file_path:
		output_filename = 'sioc_parent_of_removed_edges_'+strategy_partitioning + strategy_cycle_sampling + extra

	print ('output file name: ', output_filename)
	outputfile = open(output_filename, 'w+', newline='')
	writer = csv.writer(outputfile, delimiter='\t')
	for (left,right) in all_removed_edges:
		# print ('l and r: ', l, r)
		writer.writerow([left, right])



if __name__ == "__main__":
	main()
