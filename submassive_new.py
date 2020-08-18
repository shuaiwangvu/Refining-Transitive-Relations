

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
	with gzip.open(path+ broader_file, "rt") as f:
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
	with gzip.open(path+broader_weight, "rt") as f:
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
	can_remove = []
	for n in graph.nodes:
		if graph.out_degree(n) == 0 or graph.in_degree(n) == 0:
			can_remove.append(n)
	print ('this round removes: ', len(can_remove))
	return can_remove


def simplify_graph():
	global collect_nodes
	global can_remove

	record_size = graph.number_of_nodes()
	detected_to_remove = detected_nodes_to_remove()
	graph.remove_nodes_from(detected_to_remove)
	# print ('graph has size: ', len(graph.nodes))

	print ('before the while-loop, the size of nodes is ', record_size)
	while (record_size != graph.number_of_nodes()):
		record_size = graph.number_of_nodes()
		print ('now: ', record_size)
		detected_to_remove = detected_nodes_to_remove()
		# collect_nodes = collect_nodes.difference(detected_to_remove)
		# can_remove = can_remove.union(detected_to_remove)
		graph.remove_nodes_from(detected_to_remove)
		# record_size = graph.number_of_nodes()
		# print ('after:  ', record_size)

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
		collect_cycles = []
		if len(f) == 2:
			collect_cycles.append(f)
			collect_cycles.append([f[1], f[0]])
			count+=2
		else:
			# compute a subgraph
			sg = graph.subgraph(f)
			if sg.number_of_nodes()>1000:
				print ('\nnodes = ', sg.number_of_nodes())
				print ('edges = ', sg.number_of_edges())
			# find at most
			collect_cycles = []

			# cycle_limit = MAX_cycle_ratio * len (f)
			for (l,r) in sg.edges():
				c = nx.shortest_path(G = sg, source = r, target=l)
				# print (c)
				collect_cycles.append(c)
			count += len(collect_cycles)
			print ('cycles = ', len(collect_cycles))
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
