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
# from funcy import project

# PATH_SUBMASSIVE = "/Users/sw-works/Documents/backbone/submassive_data/subC-all.nt"
PATH_SUBMASSIVE = "/Users/sw-works/Documents/backbone/submassive_data/refined-subC-FA.nt"
PATH_SAMEAS = "/Users/sw-works/Documents/backbone/sameAs_data/term2id_0-99.csv"

dict_class_to_group = {}

def export_class_nodes():
    global dict_class_to_group
    file =  open('class_group_names.csv', 'w', newline='')
    writer = csv.writer(file)
    writer.writerow([ "Class_name", "Group_ID"])

    class_set = set()
    with open(PATH_SUBMASSIVE) as  class_file:
        csv_reader = csv.reader(class_file, delimiter=' ')
        for row in csv_reader:
            # print ( row[0][1:-1] , ' - and - ', row [2][1:-1])
            # print ( row[0] , ' - and - ', row [2])
            if len (row) > 3:
                class_set.add(row[0][1:-1])
                class_set.add(row[2][1:-1])
            else:
                print (row)
    print('collected ', len(class_set), ' classes')
    count_total_class = len(class_set)
    count_found = 0
    with open(PATH_SAMEAS) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=' ')
        line_count = 0
        count_processed = 0
        for row in csv_reader:
            count_processed += 1
            # print ('count_processed = ', count_processed)
            # print(row[0])
            if row[0] in class_set:
                # print ('Found: ',row[0], row[1])
                writer.writerow([row[0], 'https://krr.cs.vu.nl/SUBMASSIVE/'+row[1]])
                dict_class_to_group[row[0]] = 'https://krr.cs.vu.nl/SUBMASSIVE/'+row[1]
                count_found += 1
    print ('total found to be shrinked: ', count_found)
    print('NOT TO BE shrinked: ', count_total_class - count_found)


# PATH_LOD = "/scratch/wbeek/data/LOD-a-lot/data.hdt"
# PATH_LOD = '/Users/sw-works/Documents/backbone/submassive_data/subC-all.hdt'
PATH_LOD = '/Users/sw-works/Documents/backbone/submassive_data/refined-subC-FA.hdt'
subClassOf = "http://www.w3.org/2000/01/rdf-schema#subClassOf"
equivalent = "http://www.w3.org/2002/07/owl#equivalentClass"

hdt_file =  HDTDocument(PATH_LOD)


graph = nx.DiGraph()
collect_nodes = set()
can_remove = set()


def get_domain_and_label(t):
    domain = tldextract.extract(t).domain
    name1 = t.rsplit('/', 1)[-1]
    name2 = t.rsplit('#', 1)[-1]
    if len(name2) < len(name1):
        return (domain, name2)
    else:
        return (domain, name1)


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
        if all_subclass_removed(n) and n not in dict_class_to_group.keys():
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
        if is_leaf_node(s) and s not in dict_class_to_group.keys():
            can_remove.add(s)
        else:
            collect_nodes.add(s)

    print ('\tcan remove = ', len(can_remove))
    print ('\tcollect    = ', len(collect_nodes))

    for o in collect_nodes:
        if all_subclass_removed(o) and o not in dict_class_to_group.keys():
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
                    if s in dict_class_to_group.keys():
                        s = dict_class_to_group[s]
                    if n in dict_class_to_group.keys():
                        n = dict_class_to_group[n]
                    graph.add_edge(s, n)
        (subclass_triples, cardinality) = hdt_file.search_triples(n, subClassOf, '')
        for (_, _, o) in subclass_triples:
            if o in collect_nodes:
                if n != o:
                    if o in dict_class_to_group.keys():
                        o = dict_class_to_group[o]
                    if n in dict_class_to_group.keys():
                        n = dict_class_to_group[n]
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
        if len(c) > 3:
            print (len(c))
            print (c)
    # export to
    index = 1
    color = {}
    for c in filter_scc:
        if len(c) > 3:
            for n in c:
                color[n] = index
            index += 1
    # export the nodes and color
    file =  open('node_color.csv', 'w', newline='')
    writer = csv.writer(file)
    writer.writerow([ "Short_name", "Color"])
    for n in graph.nodes:
        (domain, name) = get_domain_and_label(n)
        short_name = domain + ':' + name
        if n in color:
            # write that line with color
            writer.writerow([short_name, color[n]])
        else:
            # write that line with ZERO as color
            writer.writerow([short_name,0])

    file.close()


    # export the edges
    file =  open('edges.csv', 'w', newline='')
    writer = csv.writer(file)
    writer.writerow([ "Subject", "Object"])
    for (l,r) in graph.edges:
        writer.writerow([l, r])

    file.close()

    # export the edges
    file =  open('edges_shortname.csv', 'w', newline='')
    writer = csv.writer(file)
    writer.writerow([ "Subject", "Object"])
    for (l,r) in graph.edges:
        (domain, name) = get_domain_and_label(l)
        short_name_l = domain + ':' + name
        (domain, name) = get_domain_and_label(r)
        short_name_r = domain + ':' + name
        writer.writerow([short_name_l, short_name_r])

    file.close()


def draw_graph():
    graph_pos = nx.spectral_layout(graph)
    #  # draw nodes, edges and labels
    nx.draw_networkx_nodes(graph, graph_pos, node_size=5, node_color='blue', alpha=0.3)
    nx.draw_networkx_edges(graph, graph_pos)
    # nx.draw_networkx_labels(G, graph_pos, font_size=12, font_family='sans-serif')
    #
    # # show graph
    # plt.show()

    # nx.draw(graph)
    plt.savefig("shrinked_graph.png")
    plt.show()


def main ():

    start = time.time()
    # ==============
    # some small tests

    export_class_nodes()

    init_nodes()
    construct_graph()
    # c = nx.find_cycle(graph)
    # print ('cycle = ', c)
    compute_strongly_connected_component()
    draw_graph()

    # ===============
    end = time.time()
    hours, rem = divmod(end-start, 3600)
    minutes, seconds = divmod(rem, 60)
    print("Time taken: {:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds))


if __name__ == "__main__":
    main()
