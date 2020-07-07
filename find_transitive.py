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
# from equiClass import equiClassManager
# import random


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



triples, cardinality = hdt.search_triples("", subPropertyOf, t)
print ('There are ', cardinality, 'subPropertyOf of owl:transitive properties')
for (s,p ,o) in triples:
    print ('subClass: ', s)




triples, cardinality = hdt.search_triples("", subClassOf, t)
print ('There are ', cardinality, 'subclass of owl:transitive properties')
for (s,p ,o) in triples:
    print ('subClass: ', s)

print ('==========================\n\n')
print ('as object:')
triples, cardinality = hdt.search_triples("", type, t)
print ('There are ', cardinality, 'transitive properties')
collect_transitive_properties = set()
count = 0
for (s, p, o) in triples:
    collect_transitive_properties.add(s)
    t_triples, t_cardinality = hdt.search_triples("", s, "")
    if t_cardinality > 1000000:
        print ('\tsubject: ', s)
        print ('\tpredicate:  ', p)
        print (t_cardinality, ' :', s)
        print ('\n')
        count += 1

print ('count over million', count)


triples, cardinality = hdt.search_triples("", "", s)
print ('There are ', cardinality, ' symmetric properties')
collect_symmetric_properties = set()
for (s, p, o) in triples:
    # print ('\tsubject: ', s)
    # print ('\tpredicate:  ', p)
    # print ('\n')
    collect_symmetric_properties.add(s)

triples, cardinality = hdt.search_triples("", "", aS)
print ('There are ', cardinality, ' assymmetric properties')
collect_assymmetric_properties = set()
for (s, p, o) in triples:
    # print ('\tsubject: ', s)
    # print ('\tpredicate:  ', p)
    # print ('\n')
    collect_assymmetric_properties.add(s)



triples, cardinality = hdt.search_triples("", "", r)
print ('There are ', cardinality, ' reflexive properties')
collect_reflexive_properties = set()
for (s, p, o) in triples:
    # print ('\tsubject: ', s)
    # print ('\tpredicate:  ', p)
    # print ('\n')
    collect_reflexive_properties.add(s)


triples, cardinality = hdt.search_triples("", "", iR)
print ('There are ', cardinality, ' irreflexive properties')
collect_irreflexive_properties = set()
for (s, p, o) in triples:
    # print ('\tsubject: ', s)
    # print ('\tpredicate:  ', p)
    # print ('\n')
    collect_irreflexive_properties.add(s)



collect_equivalent_properties = collect_reflexive_properties.intersection(collect_symmetric_properties.intersection(collect_transitive_properties))
print ('There are ', len(collect_equivalent_properties), ' equivalent properties')


# ====
print ('not symmetric but reflexive:')
tmp = collect_transitive_properties.intersection(collect_reflexive_properties).difference(collect_assymmetric_properties).difference(collect_symmetric_properties)
print ('size: ', len(tmp))
if len(tmp) > 0:
    print ('example:', list(tmp)[0])


print ('not symmetric and not reflexive:')
tmp = collect_transitive_properties.difference(collect_reflexive_properties).difference(collect_irreflexive_properties).difference(collect_assymmetric_properties).difference(collect_symmetric_properties)
print ('size: ', len(tmp))
if len(tmp) > 0:
    print ('example:', list(tmp)[0])

print ('not symmetric and irreflexive:')
tmp = collect_transitive_properties.intersection(collect_irreflexive_properties).difference(collect_assymmetric_properties).difference(collect_symmetric_properties)
print ('size: ', len(tmp))
if len(tmp) > 0:
    print ('example:', list(tmp)[0])


# =====
print ('#######')

print ('symmetric and not reflexive:')
tmp = collect_transitive_properties.intersection(collect_symmetric_properties).difference(collect_irreflexive_properties).difference(collect_reflexive_properties)
print ('size: ', len(tmp))
if len(tmp) > 0:
    print ('example:', list(tmp)[0])

print ('symmetric and irreflexive:')
tmp = collect_transitive_properties.intersection(collect_symmetric_properties).intersection(collect_irreflexive_properties)
print ('size: ', len(tmp))
if len(tmp) > 0:
    print ('example:', list(tmp)[0])

# =====
print ('#######')

print ('assymmetric and reflexive:')
tmp = collect_transitive_properties.intersection(collect_assymmetric_properties).intersection(collect_reflexive_properties)
print ('size: ', len(tmp))
if len(tmp) > 0:
    print ('example:', list(tmp)[0])

print ('assymmetric and not reflexive:')
tmp = collect_transitive_properties.intersection(collect_assymmetric_properties).difference(collect_irreflexive_properties).difference(collect_reflexive_properties)
print ('size: ', len(tmp))
if len(tmp) > 0:
    print ('example:', list(tmp)[0])

print ('assymmetric and irreflexive:')
tmp = collect_transitive_properties.intersection(collect_assymmetric_properties).intersection(collect_irreflexive_properties)
print ('size: ', len(tmp))
if len(tmp) > 0:
    print ('example:', list(tmp)[0])

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
