# Here we print the subclassof  rdfs:subClassOf owl:ObjectProperty in the LOD-a-lot file
#

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

# http://rhm.cdepot.net/xml/properSubClassOf

propertyGraph = Graph()
PATH_LOD = "/scratch/wbeek/data/LOD-a-lot/data.hdt"
hdt = HDTDocument(PATH_LOD)
property = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#Property'
objectProperty = "http://www.w3.org/2002/07/owl#ObjectProperty"
subClassOf = "http://www.w3.org/2000/01/rdf-schema#subClassOf"


transPropertyCollect = set()
print('=====Property ======')
triples, cardinality = hdt.search_triples("", subClassOf, property)
print ('TOTAL subClassOf PROPERTY ', cardinality)
for (s, p, o) in triples:
    if 'transitive' in s or 'Transitive' in s:
        _, scardinality = hdt.search_triples("", "", s)
        print ('property: ', s, ' : ',scardinality)
        transPropertyCollect.add(s)


transObjectPropertyCollect = set()
print('=====Object property =====')
triples, cardinality = hdt.search_triples("", subClassOf, objectProperty)
print ('TOTAL subClassOf OBEJCTPROPERTY ', cardinality)
for (s, p, o) in triples:
    if 'transitive' in s or 'Transitive' in s:
        _, scardinality = hdt.search_triples("", "", s)
        print ('ObjectProperty: ', s, ' : ',scardinality)
        transObjectPropertyCollect.add(s)

print('==== and their intersection ====')
inter = transObjectPropertyCollect.intersection(transPropertyCollect)
for it in inter:
    print ('intersection: ', it)


ptriples, pcardinality = hdt.search_triples(property, "", property)
if pcardinality > 0:
    print('property: it is subclass of itself')


ptriples, pcardinality = hdt.search_triples(objectProperty, "", objectProperty)
if pcardinality > 0:
    print('objectProperty: it is subclass of itself')


print ('-------<as subject>--------')

triples, cardinality = hdt.search_triples(objectProperty, "", "")
for (s, p, o) in triples:
    print ('p, o', p, o)
