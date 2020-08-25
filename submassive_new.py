

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

scc_size_limit = 40

timeout = 1000 * 60 * 1
o = Optimize()
o.set("timeout", timeout)
print('timeout = ',timeout/1000/60, 'mins')

num_clause_limit = 200
encode = {}

edges_to_remove = []

# num_trial_to_find_pairs = 20


def init_graph():
	global collect_nodes
	global can_remove
	print ('init the graph')
	with gzip.open(path + subclass_file, "rt") as f:
		line = f.readline()
		while line:
			row = line.split('\t')
			s = int(row[0]) # source
			t = int(row[1])
			# print (s,t)
			if s != t:
				graph.add_edge(s, t)
			line = f.readline()
		print ('graph has size: ', len(graph.nodes))


def load_weight():
	global weight
	with gzip.open(path + broader_weight, "rt") as f:
		line = f.readline()
		while line:
			row = line.split('\t')
			s = int(row[1]) # source
			t = int(row[2])
			w = int(row[0])
			# print (w, ' : ',s,t)
			if w != 1:
				weight[(s,t)] = w
			line = f.readline()
		print ('weight has size: ', len(weight.keys()))


def detected_nodes_to_remove():
	# while the nodes are being
	can_remove = []
	for n in graph.nodes:
		if graph.out_degree(n) == 0 or graph.in_degree(n) == 0:
			can_remove.append(n)
	print ('this round removes: ', len(can_remove))
	return can_remove


def simplify_graph():
	global collect_nodes
	global can_remove

	record_size = graph.number_of_nodes()
	detected_to_remove = detected_nodes_to_remove()
	graph.remove_nodes_from(detected_to_remove)
	# print ('graph has size: ', len(graph.nodes))

	print ('before the while-loop, the size of nodes is ', record_size)
	while (record_size != graph.number_of_nodes()):
		record_size = graph.number_of_nodes()
		print ('now: ', record_size)
		detected_to_remove = detected_nodes_to_remove()
		# collect_nodes = collect_nodes.difference(detected_to_remove)
		# can_remove = can_remove.union(detected_to_remove)
		graph.remove_nodes_from(detected_to_remove)
		# record_size = graph.number_of_nodes()
		# print ('after:  ', record_size)

def compute_scc_from_graph(g):
	dict = {}
	for n in g.nodes:
		collect_succssor = []
		for s in g.successors(n):
			collect_succssor.append(s)
		dict[n] = collect_succssor
	return tarjan(dict)



def cut_until_limit(scc):
	global edges_to_remove
	global graph

	if len (scc) <= 1:
		return []
	elif len(scc) <= scc_size_limit:
		return [scc]
	else:
		try:
			sg = graph.subgraph(scc) # this graph is frozen. Cannot be modified!!!
			sg2 = graph.subgraph(scc) # this graph is frozen. Cannot be modified!!!
			sg = nx.DiGraph(sg)
			sg2 = nx.DiGraph(sg2)
			sg.remove_edges_from(edges_to_remove)
			print ('cutting this scc of size: #nodes', len(scc))
			print ('cutting this scc of size: #edges', sg.number_of_edges())

			# num_partitions =  int(len(scc) / ( scc_size_limit ))
			num_partitions = 2
			print ('to be divded into ', num_partitions, ' partitions')
			ele_to_index = bidict()
			index = 0
			for n in sg.nodes():
				if n not in ele_to_index.keys():
					ele_to_index[n] = index
					index += 1

			adjacency = {}
			for m in sg.nodes():
				adjacency.setdefault(ele_to_index[m], [])

			for (s, t) in sg.edges:
				adjacency.setdefault(ele_to_index[s], []).append(ele_to_index[t])

			# print ('adj-lst = ', len(adjacency))

			cuts, part_vert  = pymetis.part_graph(num_partitions, adjacency=adjacency)
			# print ('cuts = ', cuts)
			# print ('part ', part_vert)
			print ('finished!', flush=True)

			partition_sccs = []
			partitions = []
			for c in range(num_partitions):
				col_nodes = []
				for p in range(len(part_vert)):
					if part_vert[p] == c:
						col_nodes.append(ele_to_index.inverse[p])

				print (c, ' has size ', len(col_nodes))
				partitions.append(col_nodes)

			collect_edges_partition = []
			for p in partitions:
				sg_p = sg.subgraph(p)
				partition_sccs += compute_scc_from_graph(sg_p)
				collect_edges_partition += sg_p.edges()

			sg.remove_edges_from(collect_edges_partition)

			print ('edges removed during partitioning: ', len(sg.edges()))
			edges_to_remove += list(sg.edges()) # remove all those left
			graph.remove_edges_from(edges_to_remove)

			for s in partition_sccs:
				if len (s) >10:
					print ('partition scc size = ', len (s))

			collect_sccs = []
			for s in partition_sccs:
				collect_sccs += cut_until_limit(s)
			return collect_sccs
			# print ('=================', flush=True)

		except Exception as e:
			print ('error: ', e)




def cut_sccs_to_smaller(filter_sccs):
	new_sccs = []
	for f in filter_sccs:
		if len (f) > scc_size_limit:
			smaller_sccs = cut_until_limit(f)
			new_sccs +=  smaller_sccs
		else:
			new_sccs.append(f)
	return new_sccs


def compute_strongly_connected_component():

	scc = compute_scc_from_graph(graph)
	filter_scc = [x for x in scc if len(x)>1]
	print ('num of (filtered) sccs: ', len(filter_scc))
	filter_scc.sort(reverse =True, key=len)

	print ('largest size: ', len( filter_scc[0]))
	print ('second largest size: ', len( filter_scc[1]))

	acc_size = 0
	for f in filter_scc:
		acc_size += len(f)

	print ('scc filter size nodes = ', acc_size)
	return filter_scc



def find_cycles( f):
	# compute a good amount of cycles for each SCC
	# MAX_cycle_ratio

	count = 0


	collect_cycles = []
	sg = graph.subgraph(f)

	if len(f) == 2:

		collect_cycles.append(f)
		collect_cycles.append([f[1], f[0]])
		count+=2
		# all_cycles += collect_cycles
	else:

		# edges_visited = set()
		edges_to_visit = set(sg.edges())
		# if len(f)>10:
		# 	print ('total nodes', len (f))
		# 	print ('total edges:', len (edges_to_visit))
		# compute a subgraph
		# cycle_limit = MAX_cycle_ratio * len (f)
		# path = nx.all_pairs_shortest_path(sg)

		while (len(edges_to_visit) != 0 and count < num_clause_limit):
		# for (l,r) in edges_to_visit:
			(l,r) =  edges_to_visit.pop()
			c = nx.shortest_path(G = sg, source = r, target=l)
			# print ('for edge ', l,r, ' found path ', c, ' size ', len(c))
			# edges_to_visit.remove((l,r))
			# edges_visited.add((l,r))
			cycle_edge_set = set()
			for i in range(len(c) -1):
				j = i+1
				if (c[i], c[j]) in edges_to_visit:
					cycle_edge_set.add((c[i], c[j]))
				# else:
				# 	print('not in graph!!!!', (c[i], c[j]))
			# edges_to_visit = edges_to_visit.difference(set(c))
			# edges_visited = edges_visited.union(set(c))
			collect_cycles.append(c)

			count += 1
			edges_to_visit = edges_to_visit.difference(cycle_edge_set)



		# if len(f)>10:
		# 	print ('before count ', count)
		#
		while count < num_clause_limit:
			l = random.choice(sg.nodes())
			r = random.choice(sg.nodes())
			if l != r:
				l2r = nx.shortest_path(G = sg, source = l, target = r)
				r2l = nx.shortest_path(G = sg, source = r, target = l)
				print ('l2r: ', l2r)
				print ('r2l: ', r2l)
				c = l2r[:-1] + r2l[:-1]
				print ('l2r2l: ',c, flush=True)
				collect_cycles.append(c)
				count += 1
		# # print (c)

		if len(f)>10:
			print ('after count ', count)

	# print ('total found cycles ', len(collect_cycles))
	return collect_cycles


def encode_to_SMT(cycles):
	global o, encode
	# print ('begin encode length ', len(encode.keys()))

	for cycle in cycles:
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


def analysis_removed_edges():
	global edges_to_remove
	print ('there are ', len(edges_to_remove), 'removed')


def encode_and_decode(filter_scc):
	global num_clause_limit
	global o
	global encode

	print ('start solving')
	try:
		identified_edges = []
		for f in filter_scc:
			o = Optimize()
			# encode = {}
			o.set("timeout", timeout)
			cycles  = find_cycles (f)
			# for c in cycles:
			# 	print (c)
			encode_to_SMT (cycles)
	except Exception as e:
		print ('error during encoding ', e)
	try:
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
	except Exception as e:
		print ('error during decoding ', e)
	print ('there are ', len(identified_edges), ' edges identified to remove (out of ', graph.number_of_edges())
	return identified_edges


def main ():
	global graph
	global edges_to_remove

	# start = time.time()
	# ==============
	# some small tests
	init_graph()
	simplify_graph()
	load_weight()

	start = time.time()
	flag = True
	round = 1
	while flag:
		try:
			print ('\n\nthis is round ', round)
			nx.find_cycle(G=graph, orientation='original')
			# if not all cycles are resolved, then update the SCC and compute the filter_scc to encode again
			filter_scc = compute_strongly_connected_component()
			print('# edges_to_remove before cutting ', len(edges_to_remove))
			filter_scc = cut_sccs_to_smaller(filter_scc)
			for f in filter_scc:
				if len(f) > 100:
					print ('These small (after cut) SCCS are', len(f))
			print('# edges_to_remove after cutting ', len(edges_to_remove))
			graph.remove_edges_from(edges_to_remove)
			identified_edges = encode_and_decode(filter_scc)
			edges_to_remove += identified_edges
			print ('# identified edges to remove ', len (identified_edges))
			print ('# total edges to remove ', len (edges_to_remove))

			# i = len(set (graph.edges()).intersection(set(identified_edges)))
			# print ('there is ', i, ' intersection')
			graph.remove_edges_from(identified_edges)
			# for e in edges_to_remove:
			# 	encode.pop(e, None)

			# print ('edges are like: ', list(graph.edges())[:3])
			# print ('identified edges are like: ', identified_edges[:3])
			# print ('but removed edges are like', list(edges_to_remove)[:3])
			#
			# print ('before removing, there are ', graph.number_of_edges(), ' edges ')
			# print ('there are in total ', len(edges_to_remove), 'to removed')
			# graph.remove_edges_from(edges_to_remove)
			# print ('after removing, there are ', graph.number_of_edges(), ' edges left')
			round += 1
		except:
			flag = False
	analysis_removed_edges()

	# obtain_top_concepts()
	# draw_graph()
	# ===============
	end = time.time()
	hours, rem = divmod(end-start, 3600)
	minutes, seconds = divmod(rem, 60)
	print("Time taken: {:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds))

if __name__ == "__main__":
	main()
