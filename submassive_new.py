

import gzip

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

path = "../data-gold-standard-subclass-broader/"
broader_file = "broader_edgelist.gz"
subclass_file = "subclass_edgelist.gz"

subclass_weight = "subclass_edgelist_weight_reduced.gz"
broader_weight = "broader_edgelist_weight_reduced.gz"

graph = nx.DiGraph()
collect_nodes = set()
can_remove = set()
weight = {}
filter_scc = []

MAX_cycle_ratio = 2

def init_graph():
	global collect_nodes
	global can_remove
	print ('init the graph')
	with gzip.open(path+subclass_file, "rt") as f:
		line = f.readline()
		while line:
			row = line.split('\t')
			s = int(row[0]) # source
			t = int(row[1])
			# print (s,t)
			if s != t:
				graph.add_edge(s, t)
			line = f.readline()
		print ('graph has size: ', len(graph.nodes))


def load_weight():
	global weight
	with gzip.open(path+subclass_weight, "rt") as f:
		line = f.readline()
		while line:
			row = line.split('\t')
			s = int(row[1]) # source
			t = int(row[2])
			w = int(row[0])
			# print (w, ' : ',s,t)
			if w != 1:
				weight[(s,t)] = w
			line = f.readline()
		print ('weight has size: ', len(weight.keys()))


def detected_nodes_to_remove():
	# while the nodes are being
	detected_to_remove = set()
	for n in collect_nodes:
		flag_all_succ_removed = True
		for x in graph.successors(n):
			if x not in can_remove:
				flag_all_succ_removed = False
		if flag_all_succ_removed :
			detected_to_remove.add(n)

		flag_all_pred_removed = True
		for x in graph.predecessors(n):
			if x not in can_remove:
				flag_all_pred_removed = False
		if flag_all_pred_removed :
			detected_to_remove.add(n)
	return detected_to_remove


def simplify_graph():
	global collect_nodes
	global can_remove
	for n in graph.nodes:
		if graph.out_degree(n) == 0 or graph.in_degree(n) == 0:
			can_remove.add(n)
		else:
			collect_nodes.add(n)

	graph.remove_nodes_from(can_remove)
	print ('graph has size: ', len(graph.nodes))
			# can_remove.add(n)
		# else:
		# 	collect_nodes.add(n)

	record_size = len(collect_nodes)
	print ('before the while-loop, the size of nodes is ', record_size)

	 # filter_nodes ()

	detected_to_remove = detected_nodes_to_remove()

	collect_nodes = collect_nodes.difference(detected_to_remove)
	can_remove = can_remove.union(detected_to_remove)
	while (record_size != len(collect_nodes)):
		record_size = len(collect_nodes)
		print ('before: ',record_size)

		detected_to_remove = detected_nodes_to_remove()

		collect_nodes = collect_nodes.difference(detected_to_remove)
		can_remove = can_remove.union(detected_to_remove)
		print ('after:  ',len(collect_nodes))

def compute_strongly_connected_component():
	global filter_scc

	dict = {}
	for n in graph.nodes:
		collect_succssor = []
		for s in graph.successors(n):
			collect_succssor.append(s)
		dict[n] = collect_succssor
	scc = tarjan(dict)
	filter_scc = [x for x in scc if len(x)>1]
	acc_size = 0
	for f in filter_scc:
		acc_size += len(f)

	print ('scc size nodes = ', acc_size)

def find_cycles():
	global filter_scc
	# compute a good amount of cycles for each SCC
	# MAX_cycle_ratio
	dic_cycles = []
	count = 0
	for f in filter_scc:
		# compute a subgraph
		sg = graph.subgraph(f)
		# find at most
		collect_cycles = []

		# cycle_limit = MAX_cycle_ratio * len (f)
		for (l,r) in sg.edges():
			c = nx.shortest_path(G = sg, source = r, target=l)
			print (c)
			collect_cycles.append(c)
		count += len(collect_cycles)
		dic_cycles += collect_cycles
	print ('found cycles ', count)
	return dic_cycles


def encode_to_SMT():
	print ("todo tomorrow")

def encode_and_decode():
	cycles  = find_cycles ()
	# encode cycles
	encode_to_SMT ()

def main ():

	start = time.time()
	# ==============
	# some small tests
	init_graph()
	simplify_graph()
	load_weight()

	# construct_graph()
	# c = nx.find_cycle(graph)
	# print ('cycle = ', c)
	compute_strongly_connected_component()
	encode_and_decode()

	# obtain_top_concepts()
	# draw_graph()
	# ===============
	end = time.time()
	hours, rem = divmod(end-start, 3600)
	minutes, seconds = divmod(rem, 60)
	print("Time taken: {:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds))

if __name__ == "__main__":
    main()
