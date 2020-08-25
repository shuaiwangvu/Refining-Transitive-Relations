
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

scc_size_limit = 800

timeout = 1000 * 60 * 1
o = Optimize()
o.set("timeout", timeout)
print('timeout = ',timeout/1000/60, 'mins')

num_clause_limit = 200
encode = {}

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

	with gzip.open(path + broader_file, "rt") as f:

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
	print ('cut this scc size = ', graph.number_of_nodes())
	adjacency = {}

	ele_to_index = {}
	index_to_ele = {}
	# num_partitions = int((graph.number_of_nodes() / scc_size_limit)) + 1
	num_partitions = 2
	print ('cut into ', num_partitions, ' partitions')

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
			for s in sccs:
				scc_g = sg.subgraph(s).copy()
				if scc_g.number_of_nodes() > scc_size_limit:
					sg_edges_between_subgraphs, sg_subgraphs = cut_to_limit(scc_g)
					collect_subgraphs += sg_subgraphs
					collect_subgraphs_removed_edges += sg_edges_between_subgraphs
				else:
					collect_subgraphs.append(scc_g)
		else:
			collect_subgraphs.append(sg)
	all_edges_to_remove = edges_between_subgraphs + collect_subgraphs_removed_edges
	# print ('there are in total ', len (all_edges_to_remove), ' removed during graph partitioning')
	return all_edges_to_remove, collect_subgraphs # also need to return the removed edges


def obtain_sccs():
	scc_graphs = obtain_scc_graph()

	coll_to_remove = []
	coll_to_add = []
	coll_edges_removed = []
	for g in scc_graphs:
		if g.number_of_nodes() > scc_size_limit:
			removed_edges, gs = cut_to_limit (g)
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

	print ('total edges removed: ', len (coll_edges_removed))
	return scc_graphs, coll_edges_removed


def main ():
	global graph
	global edges_to_remove

	start = time.time()
	# ==============

	graphs_obtained, edges_removed = obtain_sccs()

	# cuts, part_vert  = pymetis.part_graph(num_partitions, adjacency=adjacency)


	# ===============
	end = time.time()
	hours, rem = divmod(end-start, 3600)
	minutes, seconds = divmod(rem, 60)
	print("Time taken: {:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds))

if __name__ == "__main__":
	main()
