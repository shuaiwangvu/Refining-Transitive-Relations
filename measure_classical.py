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
"http://www.w3.org/2004/02/skos/core#narrower",
"http://purl.org/dc/terms/hasPart",
"http://purl.org/dc/terms/isPartOf",
"http://dbpedia.org/ontology/isPartOf"
]

predicate_to_study = c1 +c2 +c3


def get_domain_and_label(t):
	# domain = tldextract.extract(t).domain
	domain =  None
	if 'dbpedia' in t:
		domain = 'dbo'
	elif 'skos' in t:
		domain = 'skos'
	elif 'dc' in t:
		domain = 'dc'
	elif 'rdf-schema' in t:
		domain = 'rdfs'
	elif 'sioc' in t:
		domain = 'sioc'
	else:
		domain = tldextract.extract(t).domain

	name1 = t.rsplit('/', 1)[-1]
	name2 = t.rsplit('#', 1)[-1]
	if len(name2) < len(name1):
		return (domain, name2)
	else:
		return (domain, name1)



def compute_and_measure_graphs(p):
	graph = nx.DiGraph()
	t_triples, t_cardinality = hdt.search_triples("", p, "")
	print ("amount of triples: ", t_cardinality)
	for (l, p, r) in t_triples:
		graph.add_edge(l,r)

	avc = nx.average_clustering(graph) # average clustering coefficient
	trans = nx.transitivity(graph)
	pearson = nx.degree_pearson_correlation_coefficient(graph)
	reaching = nx.global_reaching_centrality(graph)

	return avc, trans, pearson, reaching

	# compute SCC
	# mydict = {}
	# for n in graph.nodes:
	# 	collect_succssor = []
	# 	for s in graph.successors(n):
	# 		collect_succssor.append(s)
	# 	mydict[n] = collect_succssor
	# sccs = tarjan(mydict)
	# filter_scc = [x for x in sccs if len(x)>1]
	# # compute the counter for ths filtered SCC
	# ct = Counter()
	# for f in filter_scc:
	# 	ct[len(f)] += 1
	# print ('SCC info: ', ct)
	# # obtain the corresponding scc graphs
	# scc_graphs = []
	# for s in filter_scc:
	# 	g = graph.subgraph(s).copy()
	# 	scc_graphs.append(g)
	return filter_scc, scc_graphs


file_name_reduced = 'measure_output'
outputfile_reduced =  open(file_name_reduced, 'w', newline='')
writer_reduced = csv.writer(outputfile_reduced, delimiter='\t')


file =  open('measures_classical.csv', 'w', newline='')
writer = csv.writer(file)
writer.writerow([ "Pelation", "AvC", "Trans", "Pearson", "Reaching"])

# now we deal with each predicate
measures = {}
for p in predicate_to_study:
	print ('now dealing with p = ', p)
	avc, trans, pearson, reaching = compute_and_measure_graphs(p)

	print ('avc:     ', avc)
	print ('trans:   ', trans)
	print ('pearson: ', pearson)
	print ('reaching:', reaching)
	writer.writerow([ p, avc, trans, pearson, reaching])
