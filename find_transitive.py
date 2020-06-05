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
import random


PATH_LOD = "/scratch/wbeek/data/LOD-a-lot/data.hdt"
hdt = HDTDocument(PATH_LOD)
t = "http://www.w3.org/2002/07/owl#TransitiveProperty"
a = "http://www.w3.org/2002/07/owl#AsymmetricProperty"
	# subject:  http://agrowiki.org/agrowiki/?title=Special:URIResolver/Category-3AOwl_TransitiveProperty(TransitiveProperty)
	# predicate:   http://www.w3.org/2002/07/owl#equivalentClass
    #
    #
	# subject:  http://www.cyc.com/2003/04/01/cyc#TransitiveBinaryPredicate
	# predicate:   http://www.w3.org/2002/07/owl#equivalentClass
    # subject:  http://sw.opencyc.org/concept/Mx4rnhSeOBSXQdiB19IvbH2fDg
	# predicate:   http://www.w3.org/2002/07/owl#sameAs

print('as subject:')
triples, cardinality = hdt.search_triples(t, "", "")
print ('There are ', cardinality)
for (s, p, o) in triples:
    print ('\tpredicate: ', p)
    print ('\tobject:    ', o)
    print ('\n')


print ('\n\n')
print ('as predicate:')
triples, cardinality = hdt.search_triples("", t, "")
print ('There are ', cardinality)
for (s, p, o) in triples:
    print ('\tsubject: ', s)
    print ('\tobject:  ', o)
    print ('\n')


print ('\n\n')
print ('as object:')
triples, cardinality = hdt.search_triples("", "", t)
print ('There are ', cardinality)
collect_t_subject = set()
for (s, p, o) in triples:
    print ('\tsubject: ', s)
    print ('\tpredicate:  ', p)
    print ('\n')
    collect_t_subject.add(s)

triples, cardinality = hdt.search_triples("", "", a)
print ('There are ', cardinality, ' asymmetric property')
collect_a_subject = set()
for (s, p, o) in triples:
    print ('\tsubject: ', s)
    print ('\tpredicate:  ', p)
    print ('\n')
    collect_a_subject.add(s)
both = collect_t_subject.intersection(collect_a_subject)
print ('transitive and asymmetric: ', len (both))
for b in both:
    print (b)




for b in both:
    # prepare a graph:
    graph = nx.DiGraph()
    triples, cardinality = hdt.search_triples("", b, "")
    print ('graph (edge) size = ',cardinality)
    collect_pairs = []
    for (s, _, o) in triples:
        collect_pairs.append((s, o))
    graph.add_edges_from(collect_pairs)
    c = []
    try:
        c = nx.find_cycle(graph)
    except :
        print ('no cycle found for ', b)

    print('found ', len(c), ' cycles')
