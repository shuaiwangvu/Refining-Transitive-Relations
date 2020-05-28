# SUBMASSIVE
# Shuai Wang
# shuai.wang@vu.nl
# All rights reserved.
# =====
# this is the main script of the SUBMASSIVE system.
# it includes the functionality of HDT (interaction with a knowledge graph),
# and networkx (for the analysis of graphs) and Z3 (MAXSAT solver). As a result,
# it is heavy for the memory. Thus, the use of the output files of SUBMASSIVE will
# be implemented in the near future in another script.

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
PATH_LOD = '/Users/sw-works/Documents/backbone/submassive_data/subC-all.hdt'
subClassOf = "http://www.w3.org/2000/01/rdf-schema#subClassOf"
equivalent = "http://www.w3.org/2002/07/owl#equivalentClass"

hdt_file =  HDTDocument(PATH_LOD)


graph = nx.DiGraph()
collect_nodes = set()
can_remove = set()


def is_leaf_node (n):
    (_, s_cardinality) = hdt_file.search_triples('', subClassOf, n)
    if s_cardinality == 0:
        return True

def all_subclass_removed(n):
    (triples, cardinality) = hdt_file.search_triples('', subClassOf, n)
    flag  = True
    for (s, _, _) in triples:
        if s not in can_remove and s != n:
            flag = False
    if flag :
        return True
    else:
        return False

def filter_nodes():
    detected_to_remove = set()
    for n in collect_nodes:
        if all_subclass_removed(n):
            detected_to_remove.add(n)
    # TODO: to remove these nodes
    print ('filter : can remove ', len (detected_to_remove),' nodes')
    return detected_to_remove

def init_nodes():
    global collect_nodes
    global can_remove
    (subclass_triples, cardinality) = hdt_file.search_triples('', subClassOf, '')
    for (s, _, o) in subclass_triples:
        # if the s has only no subclass, then s can be removed.
        if is_leaf_node(s):
            can_remove.add(s)
        else:
            collect_nodes.add(s)

    print ('\tcan remove = ', len(can_remove))
    print ('\tcollect    = ', len(collect_nodes))

    for o in collect_nodes:
        if all_subclass_removed(o):
            can_remove.add(o)

    collect_nodes -= can_remove
    print ('\tcan remove = ', len(can_remove))
    print ('\tcollect    = ', len(collect_nodes))

    record_size = len(collect_nodes)
    print ('before the while-loop, the size of nodes is ', record_size)
    detected_to_remove = filter_nodes ()
    collect_nodes = collect_nodes.difference(detected_to_remove)
    can_remove = can_remove.union(detected_to_remove)
    while (record_size != len(collect_nodes)):
        record_size = len(collect_nodes)
        print ('before: ',record_size)
        detected_to_remove = filter_nodes()
        collect_nodes = collect_nodes.difference(detected_to_remove)
        can_remove = can_remove.union(detected_to_remove)
        print ('after:  ',len(collect_nodes))


def construct_graph():
    # graph
    print ('**** construct graph ****')
    print ('# collect nodes = ', len(collect_nodes))
    for n in collect_nodes:
        (subclass_triples, cardinality) = hdt_file.search_triples('', subClassOf, n)
        for (s, _, _) in subclass_triples:
            if s in collect_nodes:
                if s != n :
                    graph.add_edge(s, n)
        (subclass_triples, cardinality) = hdt_file.search_triples(n, subClassOf, '')
        for (_, _, o) in subclass_triples:
            if o in collect_nodes:
                if n != o:
                    graph.add_edge(n, o)
    print ('# nodes of graph = ', len(graph.nodes))
    print ('# edges of graph = ', len(graph.edges))

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
    print (ct)

    for c in filter_scc:
        if len(c) > 5:
            print (len(c))
            print (c)




def main ():

    start = time.time()
    # ==============
    # some small tests
    init_nodes()
    construct_graph()
    # c = nx.find_cycle(graph)
    # print ('cycle = ', c)
    compute_strongly_connected_component()
    # ===============
    end = time.time()
    hours, rem = divmod(end-start, 3600)
    minutes, seconds = divmod(rem, 60)
    print("Time taken: {:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds))


if __name__ == "__main__":
    main()
