# this script studies the measurements of the graphs with transitive relations
# in-  and out- degree distribution


import gzip

from hdt import HDTDocument, IdentifierPosition
import numpy as np
import datetime
import pickle
import time
import networkx as nx
from networkx.algorithms import community
# import pymetis
import sys
import csv
# from z3 import *
import matplotlib.pyplot as plt
import tldextract
import json
import random
from tarjan import tarjan
from collections import Counter
from bidict import bidict
import math
PATH_LOD = "/scratch/wbeek/data/LOD-a-lot/data.hdt"
hdt = HDTDocument(PATH_LOD)


c1=[
"http://dbpedia.org/ontology/predecessor",
"http://dbpedia.org/ontology/successor",
"http://dbpedia.org/ontology/previousWork",
"http://dbpedia.org/ontology/subsequentWork" ]


c2=[
"http://rdfs.org/sioc/ns#parent_of",
"http://dbpedia.org/ontology/parent"]

c3 =[
"http://www.w3.org/2000/01/rdf-schema#subClassOf",
"http://www.w3.org/2004/02/skos/core#broader",
# "http://www.w3.org/2004/02/skos/core#narrower",
"http://purl.org/dc/terms/hasPart",
"http://purl.org/dc/terms/isPartOf",
"http://dbpedia.org/ontology/isPartOf"]

c = c1 + c2 + c3




def compute_SCC_graphs(p):
	graph = nx.DiGraph()
	t_triples, t_cardinality = hdt.search_triples("", p, "")
	print ("amount of triples: ", t_cardinality)
	for (l, p, r) in t_triples:
		graph.add_edge(l,r)
	# compute SCC
	mydict = {}
	for n in graph.nodes:
		collect_succssor = []
		for s in graph.successors(n):
			collect_succssor.append(s)
		mydict[n] = collect_succssor
	sccs = tarjan(mydict)
	filter_scc = [x for x in sccs if len(x)>1]
	# compute the counter for ths filtered SCC
	ct = Counter()
	for f in filter_scc:
		ct[len(f)] += 1
	print ('SCC info: ', ct)
	# obtain the corresponding scc graphs
	scc_graphs = []
	for s in filter_scc:
		g = graph.subgraph(s).copy()
		scc_graphs.append(g)
	return sccs, scc_graphs

def compute_alpha_beta (scc_graphs):
	num_all_scc_edges = 0
	num_of_size_two_cycle_edges = 0
	num_edges_left_in_new_SCC = 0

	resulting_graph  = nx.DiGraph() # the resuling graph after computing SCC

	for s in scc_graphs:
		resulting_graph.add_edges_from(s.subgraph(s).edges())
		num_all_scc_edges += s.number_of_edges()
		edges_to_remove = set()
		for (l,r) in s.edges():
			if (r,l) in s.edges():
				edges_to_remove.add((l,r))
				edges_to_remove.add((r,l))

		num_of_size_two_cycle_edges += len (edges_to_remove)
		resulting_graph.remove_edges_from(list(edges_to_remove))

	# now compute the SCCs for this new graph
	mydict = {}
	for n in resulting_graph.nodes:
		collect_succssor = []
		for s in resulting_graph.successors(n):
			collect_succssor.append(s)
		mydict[n] = collect_succssor

	sccs = tarjan(mydict)
	filter_scc = [x for x in sccs if len(x)>1]

	for f in filter_scc:
		num_edges_left_in_new_SCC += resulting_graph.subgraph(f).number_of_edges()

	print ('num_all_edges               = ', num_all_scc_edges )
	print ('num_of_size_two_cycle_edges = ',  num_of_size_two_cycle_edges )
	print ('num_edges_left_in_new_SCC   = ', num_edges_left_in_new_SCC )

	alpha = num_of_size_two_cycle_edges / num_all_scc_edges
	beta = num_edges_left_in_new_SCC / num_all_scc_edges

	return (alpha, beta)

def compute_gamma_delta (sccs):
	ct = Counter()
	for f in sccs:
		ct[len(f)] += 1
	gamma = 0
	delta = 0
	for s in ct.keys():
		gamma += math.log(ct[s]) / math.log(s)
		delta += math.log(s) / math.log(ct[s])

	return (gamma, delta)


# now we deal with each predicate
for p in c:
	print ('now dealing with p = ', p)
	sccs, scc_graphs = compute_SCC_graphs(p)

	(alpha, beta) = compute_alpha_beta(scc_graphs)
	print ('alpha = ', alpha, ' beta =', beta)

	(gamma, delta) = compute_gamma_delta(sccs)
	print ('gamma = ', gamma, ' delta ', delta)
	print ('\n\n')
