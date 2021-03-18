# Refining-Transitive-and-Pseudo-Transitive-Relations

This repository provides code and scripts for the refinement of edges of knowledge graphs of transitive and pseudo-transitive relations. 

The main file to examine is main.py

It takes knowledge graphs in three forms: the naive unweighted version, a version with weighted inferred, and a version with weighted counted. More details can be found about the setting can be found in the paper. 

To run the file, please specify if your input is weighetd (-w) or unweighted (-u) and the corresponding strategies (P1/P2 for partitioning, and S1/S2 for cycle sampling). An example run is:

```
python main.py -w ../data-gold-standard/rdfs_subClassOf_edgelist_inferred.gz P1 S1
```

There are two static settings of the parameter given:
static 1: b1 = 15,000 and b2 = 3,000
static 2: b1 = 1,000 and b2 = 200

An experimental setting in a dynamic fashion is also provided. However, we are not entiredly sure about it and some more fine-tuning is required. 

The corresponding data files can be found on zenodo:
https://zenodo.org/record/4610000#.YFHrHGRKgUE


The scripts depends on the SMT solver Z3, the well-used package networkx as well as a graph partitioning package called PyMetis. 

If any mistake, please report to Shuai: shuai.wang@vu.nl
