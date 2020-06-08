# http://www.w3.org/2002/07/owl#TransitiveProperty


from hdt import HDTDocument, IdentifierPosition
import pandas as pd
import numpy as np
import datetime
import pickle
import time
# import networkx as nx
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
from rdflib import Graph, Literal, RDF, URIRef
# rdflib knows about some namespaces, like FOAF
from rdflib.namespace import FOAF , XSD
import validators


# create a Graph
narrowerGraph = Graph()
broaderGraph = Graph()
integratedGraph = Graph()
# Create an RDF URI node to use as the subject for multiple triples

#
# # Add triples using store's add() method.
# g.add((donna, RDF.type, FOAF.Person))
# g.add((donna, FOAF.nick, Literal("donna", lang="ed")))
# g.add((donna, FOAF.name, Literal("Donna Fales")))
# g.add((donna, FOAF.mbox, URIRef("mailto:donna@example.org")))
#
# # Add another person
# ed = URIRef("http://example.org/edward")
#
# # Add triples using store's add() method.
# g.add((ed, RDF.type, FOAF.Person))
# g.add((ed, FOAF.nick, Literal("ed", datatype=XSD.string)))
# g.add((ed, FOAF.name, Literal("Edward Scissorhands")))
# g.add((ed, FOAF.mbox, URIRef("mailto:e.scissorhands@example.org")))



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

file_integrated =  open('integrated.nt', 'w', newline='')
file_narrower = open('narrower.nt', 'w', newline='')
file_broader = open('broader.nt', 'w', newline='')


triples, cardinality = hdt.search_triples("", narrower, "")
print ('There are ', cardinality, 'narrower properties')

for (s, p, o) in triples:
    file_narrower.write('<' + s + '> <' + p + '> <' + o + '> .' )
    file_integrated.write('<' + s + '> <' + p + '> <' + o + '> .' )

# file.close()
# narrowerGraph.serialize(destination='narrower.nt', format='nt')
#
triples, cardinality = hdt.search_triples("", broader, "")
print ('There are ', cardinality, 'broader properties')
for (s, p, o) in triples:
    file_broader.write('<' + s + '> <' + p + '> <' + o + '> .' )
    file_integrated.write('<' + o + '> <' + p + '> <' + s + '> .' )


file_broader.close()
file_narrower.close()
file_integrated.close()


#     # writer.writerow([s, o])
#     # writer_integrated.writerow([o, s])
#     # broaderGraph.add((URIRef(s), broaderRef, URIRef(o)))
#     # integratedGraph.add((URIRef(o), narrowerRef, URIRef(s)))
#     if validators.url(o):
#         o = URIRef(o)
#     else:
#         o = Literal(o)
#
#     if validators.url(s):
#         s = URIRef(s)
#     else:
#         s = Literal(s)
#
#     broaderGraph.add((s, broaderRef, o))
#     integratedGraph.add((o, broaderRef, s))
#
# # file.close()
# broaderGraph.serialize(destination='broader.nt', format='nt')
# integratedGraph.serialize(destination='integrated.nt', format='nt')

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
