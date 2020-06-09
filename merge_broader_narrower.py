# this is about the analysis after the merge of files

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

narrower = "http://www.w3.org/2004/02/skos/core#narrower"
narrowerTransitive = "http://www.w3.org/2004/02/skos/core#narrowerTransitive"
broader = "http://www.w3.org/2004/02/skos/core#broader"
broaderTransitive = "http://www.w3.org/2004/02/skos/core#broaderTransitive"




graph = nx.DiGraph()
collect_nodes = set()
can_remove = set()


# load the 2/4 knowledge graphs from hdt
def load_KG (path_file, predicate_string, orientation = True):
    # load the file according to the given predicate
    hdt_file =  HDTDocument(path_file)
    (triples, cardinality) = hdt_file.search_triples('', predicate_string, '')
    for (s, _, o) in triples:
        if orientation :
            graph.add_edge(s, o)
        else:
            graph.add_edge(o, s)

def remove_leaf_nodes():
    global can_remove
    can_remove_now = set()
    for n in graph.nodes:
        if graph.out_degree(n) == 0:
            can_remove_now.add(n)
    graph.remove_nodes_from(can_remove_now)
    can_remove = can_remove.union(can_remove_now)


def compute_strongly_connected_component():
    dict = {}
    for n in graph.nodes:
        collect_succssor = []
        for s in graph.successors(n):
            collect_succssor.append(s)
        dict[n] = collect_succssor
    scc = tarjan(dict)
    print ('# Connected Component        : ', len(scc))
    filter_scc = [x for x in scc if len(x)>1]
    print('# Connected Component Filtered: ', len(filter_scc))
    ct = Counter()
    for c in filter_scc:
        ct[len(c)] += 1
        if len(c) in [2799, 3926, 3568]:
            print (c)


def main ():

    start = time.time()
    # ==============
    # file path specification
    file_spec = []
    BROADER  = False
    NARROWER = True
    direction = NARROWER
    file_spec.append(('./broader.hdt', broader, not direction))
    file_spec.append(('./narrower.hdt', narrower, direction))
    file_spec.append(('./broaderTransitive.hdt', broaderTransitive, not direction))
    file_spec.append(('./narrowerTransitive.hdt', narrowerTransitive, direction))
    for (f_path, p, orientation) in file_spec:
        load_KG(f_path, p, orientation)
    print ('before removed, there are ',len(graph.nodes), ' nodes')
    print ('before removed, there are ',len(graph.edges), ' edges')
    remove_leaf_nodes()
    print ('after removed, there are ',len(graph.nodes), ' nodes')
    print ('after removed, there are ',len(graph.edges), ' edges')
    compute_strongly_connected_component()
    # ===============
    end = time.time()
    hours, rem = divmod(end-start, 3600)
    minutes, seconds = divmod(rem, 60)
    print("Time taken: {:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds))


if __name__ == "__main__":
    main()
