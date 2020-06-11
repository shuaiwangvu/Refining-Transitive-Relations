# this file gets the two broader & narrower subgraph from LOD-a-lot

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
# from rdflib.namespace import FOAF , XSD
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

narrowerRef = URIRef(narrower)
broaderRef = URIRef(broader)

file_integrated =  open('integrated.nt', 'w', newline='')
file_narrower = open('narrower.nt', 'w', newline='')
file_narrower = open('narrower.nt', 'w', newline='')
file_broader = open('broader.nt', 'w', newline='')
file_broader = open('broader.nt', 'w', newline='')


# file_narrower = open('narrower.nt', 'w', newline='')
# file_broader = open('broader.nt', 'w', newline='')
file_narrower = open('narrowerTransitive.nt', 'w', newline='')
file_broader = open('broaderTransitive.nt', 'w', newline='')

# file_integrated =  open('integrated.nt', 'w', newline='')
#
# triples, cardinality = hdt.search_triples("", narrower, "")
# print ('There are ', cardinality, 'narrower properties')
#
# for (s, p, o) in triples:
#     if s[0] == '"':
#         s = s
#     else:
#         s = '<' + s + '>'
#     if o[0] == '"':
#         o = o
#     else:
#         o = '<' + o + '>'
#     p = '<' + p + '>'
#     file_narrower.write(s +' '+  p+  ' ' + o + '.\n' )
#     # file_integrated.write(s +' '+  p+  ' ' + o + '.\n' )
#
# # file.close()
# # narrowerGraph.serialize(destination='narrower.nt', format='nt')
# #
# triples, cardinality = hdt.search_triples("", broader, "")
# print ('There are ', cardinality, 'broader properties')
# for (s, p, o) in triples:
#     if s[0] == '"':
#         s = s
#     else:
#         s = '<' + s + '>'
#     if o[0] == '"':
#         o = o
#     else:
#         o = '<' + o + '>'
#     p = '<' + p + '>'
#     file_broader.write(s +' '+  p+  ' ' + o + '.\n' )
#     # narrower_ =  '<' + narrower + '>'
#     # file_integrated.write(o +' '+  narrower +  ' ' + s + '.\n' )
#


triples, cardinality = hdt.search_triples("", narrowerTransitive, "")
print ('There are ', cardinality, 'narrowerTransitive properties')

for (s, p, o) in triples:
    if s[0] == '"':
        s = s
    else:
        s = '<' + s + '>'
    if o[0] == '"':
        o = o
    else:
        o = '<' + o + '>'
    p = '<' + p + '>'
    file_narrower.write(s +' '+  p+  ' ' + o + '.\n' )
    # file_integrated.write(s +' '+  p+  ' ' + o + '.\n' )

# file.close()
# narrowerGraph.serialize(destination='narrower.nt', format='nt')
#
triples, cardinality = hdt.search_triples("", broaderTransitive, "")
print ('There are ', cardinality, 'broaderTransitive properties')
for (s, p, o) in triples:
    if s[0] == '"':
        s = s
    else:
        s = '<' + s + '>'
    if o[0] == '"':
        o = o
    else:
        o = '<' + o + '>'
    p = '<' + p + '>'
    file_broader.write(s +' '+  p+  ' ' + o + '.\n' )
    # narrower_ =  '<' + narrower + '>'
    # file_integrated.write(o +' '+  narrower +  ' ' + s + '.\n' )


file_broader.close()
file_narrower.close()
# file_integrated.close()
