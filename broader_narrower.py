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
# t = "http://www.w3.org/2002/07/owl#TransitiveProperty"
# s = "http://www.w3.org/2002/07/owl#SymmetricProperty"
# aS = "http://www.w3.org/2002/07/owl#AsymmetricProperty"
# r = "http://www.w3.org/2002/07/owl#ReflexiveProperty"
# iR = "http://www.w3.org/2002/07/owl#IrreflexiveProperty"

narrower = "http://www.w3.org/2004/02/skos/core#narrower"
narrowerTransitive = "http://www.w3.org/2004/02/skos/core#narrowerTransitive"
broader = "http://www.w3.org/2004/02/skos/core#broader"
broaderTransitive = "http://www.w3.org/2004/02/skos/core#broaderTransitive"


file_integrated =  open('integrated.csv', 'w', newline='')
writer_integrated = csv.writer(file_integrated)
writer_integrated.writerow([ "Narrower", "Broader"])



triples, cardinality = hdt.search_triples("", narrower, "")
print ('There are ', cardinality, 'narrower properties')
file =  open('narrower.csv', 'w', newline='')
writer = csv.writer(file)
writer.writerow([ "Subject", "Object"])

for (s, p, o) in triples:
    writer.writerow([s, o])
    writer_integrated.writerow([s, o])

file.close()


triples, cardinality = hdt.search_triples("", broader, "")
print ('There are ', cardinality, 'broader properties')
file =  open('broader.csv', 'w', newline='')
writer = csv.writer(file)
writer.writerow([ "Subject", "Object"])

for (s, p, o) in triples:
    writer.writerow([s, o])
    writer_integrated.writerow([o, s])
    
file.close()



#
#
# print ('\n\n')
# print ('as subject:')
# triples, cardinality = hdt.search_triples(narrower, "" ,"")
# # print ('There are ', cardinality, 'narrower properties')
# # collect_narrower_properties = set()
# for (s, p, o) in triples:
#     print ('\tpredicate:  ', p)
#     print ('\tobject: ', o)
#     print ('\n')
#     # collect_narrower_properties.add(s)
#
# print ('\n\n')
# print ('as object:')
# triples, cardinality = hdt.search_triples("" ,"", narrower)
# # print ('There are ', cardinality, 'narrower properties')
# # collect_narrower_properties = set()
# for (s, p, o) in triples:
#     print ('\tsubject: ', s)
#     print ('\tpredicate:  ', p)
#     print ('\n')
#     # collect_narrower_properties.add(s)
#
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
