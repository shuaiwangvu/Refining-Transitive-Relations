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
for (s, p, o) in triples:
    print ('\tsubject: ', s)
    print ('\tpredicate:  ', p)
    print ('\n')
