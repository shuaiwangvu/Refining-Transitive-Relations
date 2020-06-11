#http://purl.org/pav/hasEarlierVersion


from hdt import HDTDocument, IdentifierPosition

import numpy as np
import datetime
import pickle
import time
import networkx as nx
import sys
import csv
from z3 import *
# from bidict import bidict
import matplotlib.pyplot as plt
import tldextract
import json
import random
# from equiClass import equiClassManager
import random
from tarjan import tarjan
from collections import Counter

# PATH_LOD = "/scratch/wbeek/data/LOD-a-lot/data.hdt"
# PATH_LOD = './broader.hdt'

type = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
subClassOf = "http://www.w3.org/2000/01/rdf-schema#subClassOf"
equivalent = "http://www.w3.org/2002/07/owl#equivalentClass"
dbpediaPerson = 'http://dbpedia.org/ontology/Person'
foafperson = 'http://xmlns.com/foaf/0.1/Person'
purlHasEarlierVersion = 'http://purl.org/pav/hasEarlierVersion'

PATH_LOD = "/scratch/wbeek/data/LOD-a-lot/data.hdt"
hdt = HDTDocument(PATH_LOD)


def get_domain_and_label(t):
    domain = tldextract.extract(t).domain
    name1 = t.rsplit('/', 1)[-1]
    name2 = t.rsplit('#', 1)[-1]
    if len(name1) == 0:
        return (domain, name2)
    if len(name2) == 0:
        return (domain, name1)

    if len(name2) < len(name1):
        return (domain, name2)
    else:
        return (domain, name1)


triples, cardinality = hdt.search_triples("", purlHasEarlierVersion, "")
print ('There are ', cardinality, 'purlHasEarlierVersion properties')
