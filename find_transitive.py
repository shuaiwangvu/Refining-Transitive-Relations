# http://www.w3.org/2002/07/owl#TransitiveProperty


from hdt import HDTDocument, IdentifierPosition
import pandas as pd
import numpy as np
import datetime
import pickle
import time
import networkx as nx
import sys
import csv
from z3 import *
from bidict import bidict
import matplotlib.pyplot as plt
import tldextract
import json
import random
from tarjan import tarjan
from collections import Counter

PATH_LOD = "/scratch/wbeek/data/LOD-a-lot/data.hdt"
hdt = HDTDocument(PATH_LOD)
t = "http://www.w3.org/2002/07/owl#TransitiveProperty"
s = "http://www.w3.org/2002/07/owl#SymmetricProperty"
aS = "http://www.w3.org/2002/07/owl#AsymmetricProperty"
r = "http://www.w3.org/2002/07/owl#ReflexiveProperty"
iR = "http://www.w3.org/2002/07/owl#IrreflexiveProperty"

type = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'

subClassOf = 'http://www.w3.org/2000/01/rdf-schema#subClassOf'
subPropertyOf = 'http://www.w3.org/2000/01/rdf-schema#subPropertyOf'

broader = 'http://www.w3.org/2004/02/skos/core#broader'
narrower = 'http://www.w3.org/2004/02/skos/core#narrower'

inv = 'http://www.w3.org/2002/07/owl#inverseOf'

# is_eq_to = "http://www.w3.org/2002/07/owl#:equivalentProperty"
	# subject:  http://agrowiki.org/agrowiki/?title=Special:URIResolver/Category-3AOwl_TransitiveProperty(TransitiveProperty)
	# predicate:   http://www.w3.org/2002/07/owl#equivalentClass
	#
	#
	# subject:  http://www.cyc.com/2003/04/01/cyc#TransitiveBinaryPredicate
	# predicate:   http://www.w3.org/2002/07/owl#equivalentClass
	# subject:  http://sw.opencyc.org/concept/Mx4rnhSeOBSXQdiB19IvbH2fDg
	# predicate:   http://www.w3.org/2002/07/owl#sameAs

# print('as subject:')
# triples, cardinality = hdt.search_triples(t, "", "")
# print ('There are ', cardinality)
# for (s, p, o) in triples:
#     print ('\tpredicate: ', p)
#     print ('\tobject:    ', o)
#     print ('\n')
#
#
# print ('\n\n')
# print ('as predicate:')
# triples, cardinality = hdt.search_triples("", t, "")
# print ('There are ', cardinality)
# for (s, p, o) in triples:
#     print ('\tsubject: ', s)
#     print ('\tobject:  ', o)
#     print ('\n')


# the predicates are:
# http://data-gov.tw.rpi.edu/vocab/p/Tag
# http://rdfs.org/ns/void#class
# http://www.w3.org/1999/02/22-rdf-syntax-ns#type
# http://www.w3.org/2002/03owlt/testOntology#feature

	# subject:  http://agrowiki.org/agrowiki/?title=Special:URIResolver/Category-3AOwl_TransitiveProperty(TransitiveProperty)
	# predicate:   http://www.w3.org/2002/07/owl#equivalentClass
	#
	#
	# subject:  http://www.cyc.com/2003/04/01/cyc#TransitiveBinaryPredicate
	# predicate:   http://www.w3.org/2002/07/owl#equivalentClass
	#
	#
	# subject:  http://sw.opencyc.org/concept/Mx4rnhSeOBSXQdiB19IvbH2fDg
	# predicate:   http://www.w3.org/2002/07/owl#sameAs
	#


#


#
# triples, cardinality = hdt.search_triples(t, "", "")
# print ('There are ', cardinality, ' owl:transitive properties')
# for (s,p ,o) in triples:
#     print ('owl:transitive property: ', p, o)
#
#
# triples, cardinality = hdt.search_triples("", subPropertyOf, t)
# print ('There are ', cardinality, 'subPropertyOf of owl:transitive properties')
# for (s,p ,o) in triples:
#     print ('subPropertyOf: ', s)
#
#
# triples, cardinality = hdt.search_triples("", subClassOf, t)
# print ('There are ', cardinality, 'subclass of owl:transitive properties')
# for (s,p ,o) in triples:
#     print ('subClassOf: ', s)

trans_collect = set()
inv_collect = set()

triples, cardinality = hdt.search_triples("", type, t)
print ('There are ', cardinality, 'type of owl:transitive properties')
for (s,p ,o) in triples:
	trans_collect.add(str(s))

# and another http://www.cyc.com/2003/04/01/cyc#EquivalenceRelation
cyc_eq = 'http://www.cyc.com/2003/04/01/cyc#EquivalenceRelation'
triples, cardinality = hdt.search_triples("", type, cyc_eq)
print ('There are ', cardinality, 'type of cyc#eq properties')
for (s,p ,o) in triples:
	trans_collect.add(str(s))

print ('So in total that is ', len(trans_collect))


record = 0
while len(trans_collect) != record :
	record = len(trans_collect)
	found_subp = set()
	for t in trans_collect:
		triples, cardinality = hdt.search_triples("", subPropertyOf, t)
		for (s,p,o) in triples:
			# print('new:',s,p,o)
			found_subp.add(str(s))
	trans_collect = trans_collect.union(found_subp)

print ('now there are ', len(trans_collect), 'type of owl:transitive properties')

for s in trans_collect:
	#print ('property: ', s)
	triples1, cardinality1 = hdt.search_triples(s ,inv, '')

	for (s1,p1,o1) in triples1:
		#print ('\t it has inverse: ', o1)
		inv_collect.add(str(o1))


	triples2, cardinality2 = hdt.search_triples('',inv, s)

	for (s2,p2,o2) in triples2:
		#print ('\t it has inverse: ', s2)
		inv_collect.add(str(s2))

	#print('count inverse: ', len(inv_collect))
	# total_inverse += len(inv_collect)


print('======')
inv_collect = inv_collect.difference(trans_collect)

print ('transitive relations', len(trans_collect))
print ('total inverse', len (inv_collect))

# count how many triples are there in total
count_triples_trans = 0
for p in trans_collect:
	triples, cardinality = hdt.search_triples("", p, "")
	count_triples_trans += cardinality

count_triples_inv = 0
for p in inv_collect:
	triples, cardinality = hdt.search_triples("", p, "")
	count_triples_inv += cardinality

print('count_triples_trans: ', count_triples_trans)
print('count_triples_inv: ', count_triples_inv)



#print("nb triples: %i" % hdt.total_triples)
#print("nb predicates: %i" % hdt.nb_predicates)

triples, cardinality = hdt.search_triples("", "", "")
print ('There are ', cardinality, '  triples')
print ('percentage : ', (count_triples_trans + count_triples_inv) / cardinality)

print ('***** end *****')
# find the inverse of a transitive property

# subproperty
#
# triples, cardinality = hdt.search_triples(narrower, "", broader)
# print ('There are ', cardinality, 'narrower -> broader')
# for (s,p ,o) in triples:
#     print ('predicate: ', p)
#
#
# triples, cardinality = hdt.search_triples(broader, "", narrower)
# print ('There are ', cardinality, 'broader -> narrower')
# for (s,p ,o) in triples:
#     print ('predicate: ', p)



# print ('==========================\n\n')
# print ('as object:')


trans_collect_large = []

ct = {}

count = 0
for p in trans_collect:
	t_triples, t_cardinality = hdt.search_triples("", p, "")
	if t_cardinality > 1000000:
		trans_collect_large.append(p)
		print ('trans: ', p, ' : ', t_cardinality)
		ct[p] = t_cardinality
		count += 1

print ('trans: count over million: ', count)



print ('now print their SCC info')

trans_collect_large = ["http://rdfs.org/ns/void#classPartition",
"http://rdfs.org/ns/void#inDataset",
"http://www.geonames.org/ontology#parentCountry",
"http://purl.org/dc/terms/extent",
"http://www.w3.org/ns/prov#wasDerivedFrom",
"http://dbpedia.org/ontology/genus",
"http://purl.org/ontology/mo/release",
"http://www.w3.org/2006/time#intervalContains",
"http://dbpedia.org/ontology/isPartOf",
"http://www.openarchives.org/ore/terms/aggregates",
"http://www.w3.org/2004/02/skos/core#inScheme"]

def print_SCC_info(p):
	print (p)
	graph = nx.DiGraph()
	t_triples, t_cardinality = hdt.search_triples("", p, "")
	for (l, p, r) in t_triples:
		graph.add_edge(l,r)

	mydict = {}
	for n in graph.nodes:
		collect_succssor = []
		for s in graph.successors(n):
			collect_succssor.append(s)
		mydict[n] = collect_succssor
	scc = tarjan(mydict)

	print ('# Connected Component        : ', len(scc))
	filter_scc = [x for x in scc if len(x)>1]
	print('# Connected Component Filtered: ', len(filter_scc))
	ct = Counter()
	for f in filter_scc:
		ct[len(f)] += 1
	print ('SCC info', ct)


for p in trans_collect_large:
	print_SCC_info(p)

#
# count = 0
# for p in inv_collect:
#     t_triples, t_cardinality = hdt.search_triples("", p, "")
#     if t_cardinality > 1000000:
#         ct[p] = t_cardinality
#         print('inv: ', p, ' : ', t_cardinality)
#         count += 1
#
# print ('inv: count over million', count)
#
# sort_ct = sorted(ct.items(), key=lambda x: x[1], reverse=True)
# for p in sort_ct:
#     print (p)
#
#
#
# print (' ....... type ........')
# triples, cardinality = hdt.search_triples(type, '', '')
# print ('There are ', cardinality, ' properties for TYPE')
# for (s, p, o) in triples:
#     print ('\tpredicate:  ', p)
#     print ('\tobject: ', o)
#     print ('\n')


# triples, cardinality = hdt.search_triples("", "", s)
# print ('There are ', cardinality, ' symmetric properties')
# collect_symmetric_properties = set()
# for (s, p, o) in triples:
#     # print ('\tsubject: ', s)
#     # print ('\tpredicate:  ', p)
#     # print ('\n')
#     collect_symmetric_properties.add(s)
#
# triples, cardinality = hdt.search_triples("", "", aS)
# print ('There are ', cardinality, ' assymmetric properties')
# collect_assymmetric_properties = set()
# for (s, p, o) in triples:
#     # print ('\tsubject: ', s)
#     # print ('\tpredicate:  ', p)
#     # print ('\n')
#     collect_assymmetric_properties.add(s)
#
#
#
# triples, cardinality = hdt.search_triples("", "", r)
# print ('There are ', cardinality, ' reflexive properties')
# collect_reflexive_properties = set()
# for (s, p, o) in triples:
#     # print ('\tsubject: ', s)
#     # print ('\tpredicate:  ', p)
#     # print ('\n')
#     collect_reflexive_properties.add(s)
#
#
# triples, cardinality = hdt.search_triples("", "", iR)
# print ('There are ', cardinality, ' irreflexive properties')
# collect_irreflexive_properties = set()
# for (s, p, o) in triples:
#     # print ('\tsubject: ', s)
#     # print ('\tpredicate:  ', p)
#     # print ('\n')
#     collect_irreflexive_properties.add(s)
#
#
#
# collect_equivalent_properties = collect_reflexive_properties.intersection(collect_symmetric_properties.intersection(collect_transitive_properties))
# print ('There are ', len(collect_equivalent_properties), ' equivalent properties')
#
#
# # ====
# print ('not symmetric but reflexive:')
# tmp = collect_transitive_properties.intersection(collect_reflexive_properties).difference(collect_assymmetric_properties).difference(collect_symmetric_properties)
# print ('size: ', len(tmp))
# if len(tmp) > 0:
#     print ('example:', list(tmp)[0])
#
#
# print ('not symmetric and not reflexive:')
# tmp = collect_transitive_properties.difference(collect_reflexive_properties).difference(collect_irreflexive_properties).difference(collect_assymmetric_properties).difference(collect_symmetric_properties)
# print ('size: ', len(tmp))
# if len(tmp) > 0:
#     print ('example:', list(tmp)[0])
#
# print ('not symmetric and irreflexive:')
# tmp = collect_transitive_properties.intersection(collect_irreflexive_properties).difference(collect_assymmetric_properties).difference(collect_symmetric_properties)
# print ('size: ', len(tmp))
# if len(tmp) > 0:
#     print ('example:', list(tmp)[0])
#
#
# # =====
# print ('#######')
#
# print ('symmetric and not reflexive:')
# tmp = collect_transitive_properties.intersection(collect_symmetric_properties).difference(collect_irreflexive_properties).difference(collect_reflexive_properties)
# print ('size: ', len(tmp))
# if len(tmp) > 0:
#     print ('example:', list(tmp)[0])
#
# print ('symmetric and irreflexive:')
# tmp = collect_transitive_properties.intersection(collect_symmetric_properties).intersection(collect_irreflexive_properties)
# print ('size: ', len(tmp))
# if len(tmp) > 0:
#     print ('example:', list(tmp)[0])
#
# # =====
# print ('#######')
#
# print ('assymmetric and reflexive:')
# tmp = collect_transitive_properties.intersection(collect_assymmetric_properties).intersection(collect_reflexive_properties)
# print ('size: ', len(tmp))
# if len(tmp) > 0:
#     print ('example:', list(tmp)[0])
#
# print ('assymmetric and not reflexive:')
# tmp = collect_transitive_properties.intersection(collect_assymmetric_properties).difference(collect_irreflexive_properties).difference(collect_reflexive_properties)
# print ('size: ', len(tmp))
# if len(tmp) > 0:
#     print ('example:', list(tmp)[0])
#
# print ('assymmetric and irreflexive:')
# tmp = collect_transitive_properties.intersection(collect_assymmetric_properties).intersection(collect_irreflexive_properties)
# print ('size: ', len(tmp))
# if len(tmp) > 0:
#     print ('example:', list(tmp)[0])

#
# for b in both:
#     # print ('\n\n')
#     # prepare a graph:
#     graph = nx.DiGraph()
#     triples, cardinality = hdt.search_triples("", b, "")
#     if cardinality >= 100000:
#         print ('too large to find all cycles: ', cardinality,' for ', b)
#     else:
#         collect_pairs = []
#         for (s, _, o) in triples:
#             collect_pairs.append((s, o))
#         graph.add_edges_from(collect_pairs)
#         c = []
#         try:
#             c = nx.find_cycle(graph)
#         except :
#             # print ('no cycle found for ', b)
#             pass
#         if len(c) > 0:
#             print('found ', len(c), ' cycles for ', b)
#             print (c)
#             print ('graph (edge) size = ',cardinality)
#             print('\n')

#
# geo = 'http://www.geonames.org/ontology#parentFeature'
#
# # subClassOf
# intervalContains = 'http://www.w3.org/2006/time#intervalContains'
# intervalDuring = 'http://www.w3.org/2006/time#intervalDuring'
#
# hasPart = 'http://purl.org/dc/terms/hasPart'
# isPartOf = 'http://purl.org/dc/terms/isPartOf'
#
# broader = 'http://www.w3.org/2004/02/skos/core#broader'
# narrower = 'http://www.w3.org/2004/02/skos/core#narrower'
#
# broaderTransitive = 'http://www.w3.org/2004/02/skos/core#broaderTransitive'
# narrowerTransitive = 'http://www.w3.org/2004/02/skos/core#narrowerTransitive'
#
# list_relations = [geo, subClassOf, subPropertyOf, intervalContains, intervalDuring, hasPart, isPartOf, broader, narrower, broaderTransitive, narrowerTransitive]
#
#
# s = "http://www.w3.org/2002/07/owl#SymmetricProperty"
# aS = "http://www.w3.org/2002/07/owl#AsymmetricProperty"
# r = "http://www.w3.org/2002/07/owl#ReflexiveProperty"
# iR = "http://www.w3.org/2002/07/owl#IrreflexiveProperty"
# f = "http://www.w3.org/2002/07/owl#FunctionalProperty"
# ivf = ' http://www.w3.org/2002/07/owl#InverseFunctionalProperty'
#
# ub = 'http://www.daml.org/2000/12/daml+oil#UnambiguousProperty'
# uq = 'http://www.daml.org/2001/03/daml+oil#UniqueProperty'
#
#
# list_properties = [s, aS, r, iR, f, ivf, ub, uq]
#
# for r in list_relations:
#     # test SymmetricProperty, assymmetric, etc.
#     triples, cardinality = hdt.search_triples('', r, '')
#     print ('This relation ',r, ' has triples : ', cardinality)
#
#     # for test_p in list_properties:
#     #     triples, cardinality = hdt.search_triples(r, "", test_p)
#     #     for (s, p , o) in triples:
#     #         print ('subject  : ', s)
#     #         print ('predicate: ', p)
#     #         print ('object   : ', o, '\n\n')
#
#
# print('===== test other properties =====')
#
# for r in [intervalDuring]:
#     print('=======================:::::::: ', r)
#     # test SymmetricProperty, assymmetric, etc.
#     triples, cardinality = hdt.search_triples(r, "", "")
#     for (s, p , o) in triples:
#         print ('subject  : ', s)
#         print ('predicate: ', p)
#         print ('object   : ', o, '\n\n')
