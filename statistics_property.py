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

print('=====Property ======')
triples, cardinality = hdt.search_triples("", subClassOf, property)
for (s, p, o) in triples:
    _, scardinality = hdt.search_triples("", "", s)
    print ('property: ', s, ' : ',scardinality)



print('=====Object property =====')
triples, cardinality = hdt.search_triples("", subClassOf, objectProperty)
for (s, p, o) in triples:
    _, scardinality = hdt.search_triples("", "", s)
    print ('property: ', s, ' : ',scardinality)


ptriples, pcardinality = hdt.search_triples(objectProperty, "", objectProperty)
if pcardinality == 1:
    print('it is subclass of itself')


print ('-------<as subject>--------')

triples, cardinality = hdt.search_triples(objectProperty, "", "")
for (s, p, o) in triples:
    print ('p, o', p, o)
