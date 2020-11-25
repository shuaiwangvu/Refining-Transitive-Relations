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
from tarjan import tarjan
from collections import Counter

PATH_LOD = "/scratch/wbeek/data/LOD-a-lot/data.hdt"
hdt = HDTDocument(PATH_LOD)
t = "http://www.w3.org/2002/07/owl#TransitiveProperty"
s = "http://www.w3.org/2002/07/owl#SymmetricProperty"
antiS = "http://www.w3.org/2002/07/owl#AntisymmetricProperty" # not sure about this one
aS = "http://www.w3.org/2002/07/owl#AsymmetricProperty"
r = "http://www.w3.org/2002/07/owl#ReflexiveProperty"
iR = "http://www.w3.org/2002/07/owl#IrreflexiveProperty"

type = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'

subClassOf = 'http://www.w3.org/2000/01/rdf-schema#subClassOf'
subPropertyOf = 'http://www.w3.org/2000/01/rdf-schema#subPropertyOf'

broader = 'http://www.w3.org/2004/02/skos/core#broader'
narrower = 'http://www.w3.org/2004/02/skos/core#narrower'

inv = 'http://www.w3.org/2002/07/owl#inverseOf'
 # http://www.w3.org/2002/07/owl#equivalentClass  :  1051979
# is_eq_to = "http://www.w3.org/2002/07/owl#:equivalentProperty"
	# subject:  http://agrowiki.org/agrowiki/?title=Special:URIResolver/Category-3AOwl_TransitiveProperty(TransitiveProperty)
	# predicate:   http://www.w3.org/2002/07/owl#equivalentClass
	#
	#
	# subject:  http://www.cyc.com/2003/04/01/cyc#TransitiveBinaryPredicate
	# predicate:   http://www.w3.org/2002/07/owl#equivalentClass
	# subject:  http://sw.opencyc.org/concept/Mx4rnhSeOBSXQdiB19IvbH2fDg
	# predicate:   http://www.w3.org/2002/07/owl#sameAs

# print('as subject:')
# triples, cardinality = hdt.search_triples(t, "", "")
# print ('There are ', cardinality)
# for (s, p, o) in triples:
#     print ('\tpredicate: ', p)
#     print ('\tobject:    ', o)
#     print ('\n')
#
#
# print ('\n\n')
# print ('as predicate:')
# triples, cardinality = hdt.search_triples("", t, "")
# print ('There are ', cardinality)
# for (s, p, o) in triples:
#     print ('\tsubject: ', s)
#     print ('\tobject:  ', o)
#     print ('\n')


# the predicates are:
# http://data-gov.tw.rpi.edu/vocab/p/Tag
# http://rdfs.org/ns/void#class
# http://www.w3.org/1999/02/22-rdf-syntax-ns#type
# http://www.w3.org/2002/03owlt/testOntology#feature

	# subject:  http://agrowiki.org/agrowiki/?title=Special:URIResolver/Category-3AOwl_TransitiveProperty(TransitiveProperty)
	# predicate:   http://www.w3.org/2002/07/owl#equivalentClass
	#
	#
	# subject:  http://www.cyc.com/2003/04/01/cyc#TransitiveBinaryPredicate
	# predicate:   http://www.w3.org/2002/07/owl#equivalentClass
	#
	#
	# subject:  http://sw.opencyc.org/concept/Mx4rnhSeOBSXQdiB19IvbH2fDg
	# predicate:   http://www.w3.org/2002/07/owl#sameAs
	#


#


#
# triples, cardinality = hdt.search_triples(t, "", "")
# print ('There are ', cardinality, ' owl:transitive properties')
# for (s,p ,o) in triples:
#     print ('owl:transitive property: ', p, o)
#
#
# triples, cardinality = hdt.search_triples("", subPropertyOf, t)
# print ('There are ', cardinality, 'subPropertyOf of owl:transitive properties')
# for (s,p ,o) in triples:
#     print ('subPropertyOf: ', s)
#
#
# triples, cardinality = hdt.search_triples("", subClassOf, t)
# print ('There are ', cardinality, 'subclass of owl:transitive properties')
# for (s,p ,o) in triples:
#     print ('subClassOf: ', s)

trans_collect = set()
inv_collect = set()

triples, direct_trans_relations = hdt.search_triples("", type, t)
print ('There are ', direct_trans_relations, 'as typed by owl:transitive properties')
for (s,p ,o) in triples:
	trans_collect.add(str(s))
#
# # and another http://www.cyc.com/2003/04/01/cyc#EquivalenceRelation
# cyc_eq = 'http://www.cyc.com/2003/04/01/cyc#EquivalenceRelation'
# triples, cardinality = hdt.search_triples("", type, cyc_eq)
# print ('There are ', cardinality, 'type of cyc#eq properties')
# for (s,p ,o) in triples:
# 	trans_collect.add(str(s))
#
# print ('So in total that is ', len(trans_collect))
count_trans_rel_triples = 0
for trans_rel in trans_collect:
	triples, cardinality = hdt.search_triples("", trans_rel, "")
	count_trans_rel_triples += cardinality

print ('there are in total ', count_trans_rel_triples, ' triples among these  2,486 relations')


triples, total_triples = hdt.search_triples("", "", "")
print ('that gives ', count_trans_rel_triples/ total_triples , ' overall')




record = 0
closure_coll = trans_collect.copy()
while len(closure_coll) != record : # untill the size does not expand anymore.
	record = len(closure_coll)
	newly_found = set()
	for t in closure_coll:
		triples, cardinality = hdt.search_triples("", subPropertyOf, t)
		for (s,p,o) in triples:
			# print('new:',s,p,o)
			newly_found.add(str(s))

		triples1, cardinality1 = hdt.search_triples("" ,inv, t)
		for (s,p,o) in triples1:
			# print('new:',s,p,o)
			newly_found.add(str(s))
	closure_coll = closure_coll.union (newly_found)

print ('After computing the closure, there are in total', len (closure_coll), ' relations in the set')

# print('======')
# inv_collect = inv_collect.difference(trans_collect)
#
# print ('transitive relations', len(trans_collect))
# print ('total inverse', len (inv_collect))
#
# count how many triples are there in total
count_triples_trans = 0
for p in closure_coll:
	triples, cardinality = hdt.search_triples("", p, "")
	count_triples_trans += cardinality
print ('under closure = ', count_triples_trans)
print ('that gives ', count_triples_trans/ total_triples , ' overall')

print ('=========================================================================')


#
trans_collect_large = []

ct = {}

count = 0
for p in trans_collect:
	t_triples, t_cardinality = hdt.search_triples("", p, "")
	if t_cardinality > 100000: # over 100,000
		trans_collect_large.append(p)
		print ('trans: ', p, ' : ', t_cardinality)
		ct[p] = t_cardinality
		count += 1

print ('Among the original # trans: count over million: ', count)
# trans:  http://www.w3.org/2004/02/skos/core#broader  :  11866699
# trans:  http://www.w3.org/2004/02/skos/core#narrower  :  817194
# trans:  http://purl.org/dc/terms/hasPart  :  3461053
# trans:  http://www.w3.org/2002/07/owl#sameAs  :  558943116
# trans:  http://purl.org/dc/terms/isPartOf  :  59839730
# trans:  http://xmlns.com/foaf/0.1/knows  :  122046428
# trans:  http://www.w3.org/2004/02/skos/core#narrowerTransitive  :  101842
# trans:  http://www.w3.org/2004/02/skos/core#broaderTransitive  :  133634
# trans:  http://www.w3.org/2004/02/skos/core#exactMatch  :  566137
# trans:  http://data-gov.tw.rpi.edu/2009/data-gov-twc.rdf#isPartOf  :  151020
# trans:  http://www.geonames.org/ontology#parentFeature  :  10699159
# trans:  http://www.w3.org/2006/03/wn/wn20/schema/hyponymOf  :  203412
# trans:  http://data.ordnancesurvey.co.uk/ontology/spatialrelations/contains  :  167052
# trans:  http://www.w3.org/2006/time#intervalContains  :  1636798
# trans:  http://www.w3.org/2000/01/rdf-schema#subClassOf  :  4461717
# trans:  http://www.w3.org/2002/07/owl#equivalentClass  :  1051979
# # trans: count over million:  16

print ('Now the extended part: ')
trans_collect_large = []

ct = {}

count = 0
for p in closure_coll:
	t_triples, t_cardinality = hdt.search_triples("", p, "")
	if t_cardinality > 100000: # over 100,000
		trans_collect_large.append(p)
		print ('trans: ', p, ' : ', t_cardinality)
		ct[p] = t_cardinality
		count += 1

print ('# trans: count over million: ', count)

# Now the extended part:
# trans:  http://d-nb.info/standards/elementset/gnd#acquaintanceshipOrFriendship  :  101116
# trans:  http://www.europeana.eu/schemas/edm/hasView  :  2040572
# trans:  http://purl.org/ontology/mo/label  :  909022
# trans:  http://www.w3.org/2004/02/skos/core#narrower  :  817194
# trans:  http://dbpedia.org/ontology/division  :  274266
# trans:  http://purl.oclc.org/NET/ssnx/ssn#featureOfInterest  :  393856
# trans:  http://purl.org/ontology/mo/produced_work  :  517817
# trans:  http://dbpedia.org/ontology/party  :  256302
# trans:  http://dbpedia.org/ontology/deathPlace  :  1080556
# trans:  http://dbpedia.org/ontology/parent  :  105868
# trans:  http://www.geonames.org/ontology#parentCountry  :  7474352
# trans:  http://www.w3.org/2002/07/owl#sameAs  :  558943116
# trans:  http://dbpedia.org/ontology/format  :  336894
# trans:  http://dbpedia.org/ontology/district  :  335358
# trans:  http://dbpedia.org/ontology/thumbnail  :  9124175
# trans:  http://dbpedia.org/ontology/binomialAuthority  :  265429
# trans:  http://www.w3.org/2004/02/skos/core#inScheme  :  5188952
# trans:  http://www.openarchives.org/ore/terms/isAggregatedBy  :  130238
# trans:  http://dbpedia.org/ontology/currentMember  :  447068
# trans:  http://dbpedia.org/ontology/knownFor  :  107277
# trans:  http://dbpedia.org/ontology/kingdom  :  792205
# trans:  http://reference.data.gov.uk/def/intervals/intervalContainsSecond  :  863472
# trans:  http://dbpedia.org/ontology/owner  :  146108
# trans:  http://www.w3.org/2004/02/skos/core#topConceptOf  :  340119
# trans:  http://rdfs.org/ns/void#propertyPartition  :  241094
# trans:  http://dbpedia.org/ontology/almaMater  :  151201
# trans:  http://www.w3.org/2004/02/skos/core#exactMatch  :  566137
# trans:  http://www.geonames.org/ontology#parentADM3  :  228607
# trans:  http://www.geonames.org/ontology#parentADM2  :  2508526
# trans:  http://dbpedia.org/ontology/family  :  1844706
# trans:  http://purl.org/ontology/mo/media_type  :  1152707
# trans:  http://purl.org/dc/terms/references  :  655907
# trans:  http://dbpedia.org/ontology/stateOfOrigin  :  196300
# trans:  http://dbpedia.org/ontology/class  :  1085302
# trans:  http://dbpedia.org/ontology/capital  :  108442
# trans:  http://dbpedia.org/ontology/musicalArtist  :  131855
# trans:  http://vivoweb.org/ontology/core#authorInAuthorship  :  124420
# trans:  http://www.loc.gov/mads/rdf/v1#hasReciprocalAuthority  :  156583
# trans:  http://xmlns.com/foaf/0.1/homepage  :  42418326
# trans:  http://dbpedia.org/ontology/locationCity  :  152889
# trans:  http://www.geonames.org/ontology#parentADM4  :  121368
# trans:  http://rdfs.org/ns/void#subset  :  395227
# trans:  http://www.openarchives.org/ore/terms/aggregates  :  3175425
# trans:  http://vivoweb.org/ontology/core#linkedAuthor  :  124404
# trans:  http://purl.org/dc/terms/license  :  557333
# trans:  http://purl.org/dc/terms/contributor  :  36623164
# trans:  http://dbpedia.org/ontology/musicComposer  :  230167
# trans:  http://dbpedia.org/ontology/hometown  :  264864
# trans:  http://www.w3.org/ns/prov#alternateOf  :  206371
# trans:  http://www.europeana.eu/schemas/edm/isShownBy  :  751495
# trans:  http://dbpedia.org/ontology/state  :  250568
# trans:  http://dbpedia.org/ontology/type  :  941702
# trans:  http://dbpedia.org/ontology/nationality  :  423874
# trans:  http://www.w3.org/ns/prov#specializationOf  :  733472
# trans:  http://dbpedia.org/ontology/subsequentWork  :  511026
# trans:  http://dbpedia.org/ontology/federalState  :  105000
# trans:  http://dbpedia.org/ontology/phylum  :  751596
# trans:  http://purl.org/dc/terms/isPartOf  :  59839730
# trans:  http://www.w3.org/2004/02/skos/core#related  :  698032
# trans:  http://dbpedia.org/ontology/cinematography  :  152134
# trans:  http://dbpedia.org/ontology/category  :  131273
# trans:  http://www.w3.org/1999/02/22-rdf-syntax-ns#type  :  3321354308
# trans:  http://dbpedia.org/ontology/recordLabel  :  845329
# trans:  http://dbpedia.org/ontology/careerStation  :  698004
# trans:  http://purl.oclc.org/NET/ssnx/ssn#observedProperty  :  393856
# trans:  http://www.w3.org/2003/01/geo/wgs84_pos#location  :  14688561
# trans:  http://xmlns.com/foaf/0.1/knows  :  122046428
# trans:  http://dbpedia.org/ontology/occupation  :  886464
# trans:  http://dbpedia.org/ontology/isPartOf  :  1003184
# trans:  http://rdfs.org/sioc/ns#links_to  :  19031184
# trans:  http://dbpedia.org/ontology/managerClub  :  121879
# trans:  http://dbpedia.org/ontology/author  :  195471
# trans:  http://dbpedia.org/ontology/editing  :  117096
# trans:  http://data-gov.tw.rpi.edu/2009/data-gov-twc.rdf#isPartOf  :  151020
# trans:  http://dbpedia.org/ontology/instrument  :  246932
# trans:  http://dbpedia.org/ontology/musicalBand  :  109868
# trans:  http://data.ordnancesurvey.co.uk/ontology/spatialrelations/contains  :  167052
# trans:  http://purl.org/dc/terms/format  :  16306496
# trans:  http://www.w3.org/2006/time#intervalContains  :  1636798
# trans:  http://dbpedia.org/ontology/department  :  300506
# trans:  http://purl.org/ontology/mo/release  :  1102387
# trans:  http://dbpedia.org/ontology/leaderName  :  124883
# trans:  http://dbpedia.org/ontology/order  :  1633215
# trans:  http://dbpedia.org/ontology/location  :  952877
# trans:  http://www.w3.org/2000/01/rdf-schema#subClassOf  :  4461717
# trans:  http://vivoweb.org/ontology/core#dateTimeInterval  :  176247
# trans:  http://www.europeana.eu/schemas/edm/isShownAt  :  2344986
# trans:  http://dbpedia.org/ontology/genre  :  2009853
# trans:  http://dbpedia.org/ontology/league  :  131856
# trans:  http://dbpedia.org/ontology/previousWork  :  551284
# trans:  http://purl.org/ontology/bibo/editor  :  2699958
# trans:  http://www.w3.org/2004/02/skos/core#broader  :  11866699
# trans:  http://purl.org/dc/terms/hasVersion  :  312884
# trans:  http://rdfs.org/sioc/ns#previous_version  :  111038
# trans:  http://purl.org/dc/terms/extent  :  6427515
# trans:  http://www.europeana.eu/schemas/edm/object  :  2047562
# trans:  http://dbpedia.org/ontology/city  :  469144
# trans:  http://dbpedia.org/ontology/industry  :  139703
# trans:  http://purl.org/dc/terms/isFormatOf  :  2947607
# trans:  http://dbpedia.org/ontology/domain  :  320576
# trans:  http://purl.org/dc/terms/hasPart  :  3461053
# trans:  http://dbpedia.org/ontology/bandMember  :  104268
# trans:  http://dbpedia.org/ontology/commander  :  156192
# trans:  http://www.w3.org/ns/prov#wasDerivedFrom  :  113625586
# trans:  http://dbpedia.org/ontology/director  :  385773
# trans:  http://rdfs.org/sioc/ns#parent_of  :  101219
# trans:  http://dbpedia.org/ontology/starring  :  1819647
# trans:  http://purl.org/dc/terms/creator  :  10580237
# trans:  http://dbpedia.org/ontology/province  :  400757
# trans:  http://reference.data.gov.uk/def/intervals/intervalContainsMinute  :  682074
# trans:  http://purl.org/dc/terms/publisher  :  32564723
# trans:  http://dbpedia.org/ontology/riverMouth  :  109804
# trans:  http://purl.org/dc/terms/medium  :  15587471
# trans:  http://dbpedia.org/ontology/neighboringMunicipality  :  187256
# trans:  http://dbpedia.org/ontology/locationCountry  :  132800
# trans:  http://dbpedia.org/ontology/municipality  :  234629
# trans:  http://umbel.org/umbel#isLike  :  461054
# trans:  http://rdfs.org/sioc/ns#has_container  :  940843
# trans:  http://purl.org/dc/terms/source  :  1914955
# trans:  http://www.geonames.org/ontology#parentADM1  :  6814740
# trans:  http://dbpedia.org/ontology/wikiPageWikiLink  :  906449419
# trans:  http://purl.org/ontology/last-fm/user  :  630099
# trans:  http://dbpedia.org/ontology/formerTeam  :  377734
# trans:  http://xmlns.com/foaf/0.1/based_near  :  1130399
# trans:  http://www.w3.org/2004/02/skos/core#narrowerTransitive  :  101842
# trans:  http://purl.org/dc/terms/hasFormat  :  3360771
# trans:  http://dbpedia.org/ontology/distributor  :  196458
# trans:  http://dbpedia.org/ontology/country  :  2686392
# trans:  http://rdfs.org/sioc/ns#member_of  :  177681
# trans:  http://purl.org/ontology/bibo/status  :  218138
# trans:  http://dbpedia.org/ontology/award  :  242632
# trans:  http://dbpedia.org/ontology/associatedBand  :  243124
# trans:  http://dbpedia.org/ontology/region  :  733479
# trans:  http://www.europeana.eu/schemas/edm/landingPage  :  2388739
# trans:  http://dbpedia.org/ontology/club  :  409608
# trans:  http://www.europeana.eu/schemas/edm/aggregatedCHO  :  4771779
# trans:  http://dbpedia.org/ontology/producer  :  821305
# trans:  http://purl.org/ontology/mo/composer  :  477618
# trans:  http://dbpedia.org/ontology/birthPlace  :  3257921
# trans:  http://dbpedia.org/ontology/album  :  144151
# trans:  http://dbpedia.org/ontology/authority  :  104820
# trans:  http://dbpedia.org/ontology/computingPlatform  :  174810
# trans:  http://purl.org/dc/terms/isReferencedBy  :  12925902
# trans:  http://purl.org/dc/terms/rights  :  130488
# trans:  http://purl.org/dc/terms/language  :  20220368
# trans:  http://www.w3.org/2000/01/rdf-schema#isDefinedBy  :  9254565
# trans:  http://dbpedia.org/ontology/residence  :  112369
# trans:  http://dbpedia.org/ontology/associatedMusicalArtist  :  283705
# trans:  http://www.w3.org/2004/02/skos/core#hasTopConcept  :  345150
# trans:  http://data.ordnancesurvey.co.uk/ontology/spatialrelations/touches  :  102299
# trans:  http://dbpedia.org/ontology/product  :  125351
# trans:  http://dbpedia.org/ontology/locatedInArea  :  264481
# trans:  http://dbpedia.org/ontology/battle  :  228848
# trans:  http://rdfs.org/ns/void#inDataset  :  26725718
# trans:  http://dbpedia.org/ontology/successor  :  440746
# trans:  http://www.loc.gov/mads/rdf/v1#isMemberOfMADSScheme  :  8915253
# trans:  http://dbpedia.org/ontology/genus  :  1152472
# trans:  http://vivoweb.org/ontology/core#informationResourceInAuthorship  :  126543
# trans:  http://rdfs.org/ns/void#classPartition  :  4385636
# trans:  http://www.loc.gov/loc.terms/relators/AUT  :  415903
# trans:  http://dbpedia.org/ontology/canton  :  239080
# trans:  http://dbpedia.org/ontology/field  :  115543
# trans:  http://creativecommons.org/ns#license  :  175826
# trans:  http://dbpedia.org/ontology/gender  :  115033
# trans:  http://dbpedia.org/ontology/recordedIn  :  162317
# trans:  http://purl.org/dc/terms/relation  :  635978
# trans:  http://www.daml.org/2003/02/fips55/location-ont#directlyLocatedIn  :  213836
# trans:  http://dbpedia.org/ontology/team  :  2852279
# trans:  http://www.w3.org/2004/02/skos/core#broaderTransitive  :  133634
# trans:  http://www.w3.org/ns/prov#wasAttributedTo  :  214124
# trans:  http://dbpedia.org/ontology/writer  :  604597
# trans:  http://dbpedia.org/ontology/artist  :  492910
# trans:  http://dbpedia.org/ontology/language  :  464106
# trans:  http://www.geonames.org/ontology#parentFeature  :  10699159
# trans:  http://www.w3.org/2006/03/wn/wn20/schema/hyponymOf  :  203412
# trans:  http://dbpedia.org/ontology/ground  :  102978
# trans:  http://dbpedia.org/ontology/arrondissement  :  221618
# trans:  http://rdfs.org/sioc/ns#has_parent  :  112259
# trans:  http://dbpedia.org/ontology/predecessor  :  358244
# trans:  http://dbpedia.org/ontology/publisher  :  222853
# trans:  http://dbpedia.org/ontology/religion  :  136139
# trans:  http://dbpedia.org/ontology/timeZone  :  784340
# trans:  http://vivoweb.org/ontology/core#linkedInformationResource  :  126181
# trans:  http://purl.oclc.org/NET/ssnx/ssn#observedBy  :  393856
# trans:  http://www.w3.org/2002/07/owl#equivalentClass  :  1051979
# trans:  http://dbpedia.org/ontology/county  :  317518
# # trans: count over million:  186

print ('#######################')

# s = "http://www.w3.org/2002/07/owl#SymmetricProperty"
# antiS = "http://www.w3.org/2002/07/owl#AntisymmetricProperty" # not sure about this one
# aS = "http://www.w3.org/2002/07/owl#AsymmetricProperty"
# r = "http://www.w3.org/2002/07/owl#ReflexiveProperty"
# iR = "http://www.w3.org/2002/07/owl#IrreflexiveProperty"
print ('among the directly typed : ', len(trans_collect))
count_s = 0
count_antiS = 0
count_aS = 0
count_r = 0
count_iR = 0

count_s_triple = 0
count_antiS_triple = 0
count_aS_triple = 0
count_r_triple = 0
count_iR_triple = 0

for p in trans_collect:

	_, s_cardinality = hdt.search_triples(p, type, s)
	if s_cardinality >= 1:
		count_s += 1
		_, s_cardinality = hdt.search_triples("", p, "")
		count_s_triple += s_cardinality


	_, antiS_cardinality = hdt.search_triples(p, type, antiS)
	if antiS_cardinality >= 1:
		count_antiS += 1
		_, antiS_cardinality = hdt.search_triples("", p, "")
		count_antiS_triple += antiS_cardinality
		print ('this antiS is ', p)

	_, aS_cardinality = hdt.search_triples(p, type, aS)
	if aS_cardinality >= 1:
		count_aS += 1
		_, aS_cardinality = hdt.search_triples("", p, "")
		count_aS_triple += aS_cardinality

	_, r_cardinality = hdt.search_triples(p, type, r)
	if r_cardinality >= 1:
		count_r += 1
		_, r_cardinality = hdt.search_triples("", p, "")
		count_r_triple += r_cardinality
		print ('this reflexive is ', p)

	_, iR_cardinality = hdt.search_triples(p, type, iR)
	if iR_cardinality >= 1:
		count_iR += 1
		_, iR_cardinality = hdt.search_triples("", p, "")
		count_iR_triple += iR_cardinality


# count_trans_rel_triples
print ('there are ', count_s, ' symmetric relations')
print ('gives ', count_s_triple, 'triples')
print ('-------')
print ('there are ', count_antiS, 'antisymmetric relations')
print ('gives ', count_antiS_triple, 'triples')

print ('-------')
print ('there are ', count_aS, ' asymmetric relations')
print ('gives ', count_aS_triple, 'triples')

print ('-------')
print ('there are ', count_r, ' reflexive relations')
print ('gives ', count_r_triple, 'triples')

print ('-------')
print ('there are ', count_iR, ' irreflexive relations')
print ('gives ', count_iR_triple, 'triples')




print ('\n\n === Now those in closure ====: ', len (closure_coll))
count_s = 0
count_antiS = 0
count_aS = 0
count_r = 0
count_iR = 0

count_s_triple = 0
count_antiS_triple = 0
count_aS_triple = 0
count_r_triple = 0
count_iR_triple = 0

for p in closure_coll:

	_, s_cardinality = hdt.search_triples(p, type, s)
	if s_cardinality >= 1:
		count_s += 1
		_, s_cardinality = hdt.search_triples("", p, "")
		count_s_triple += s_cardinality


	_, antiS_cardinality = hdt.search_triples(p, type, antiS)
	if antiS_cardinality >= 1:
		count_antiS += 1
		_, antiS_cardinality = hdt.search_triples("", p, "")
		count_antiS_triple += antiS_cardinality
		print ('this antiS is ', p)

	_, aS_cardinality = hdt.search_triples(p, type, aS)
	if aS_cardinality >= 1:
		count_aS += 1
		_, aS_cardinality = hdt.search_triples("", p, "")
		count_aS_triple += aS_cardinality


	_, r_cardinality = hdt.search_triples(p, type, r)
	if r_cardinality >= 1:
		count_r += 1
		_, r_cardinality = hdt.search_triples("", p, "")
		count_r_triple += r_cardinality

	_, iR_cardinality = hdt.search_triples(p, type, iR)
	if iR_cardinality >= 1:
		count_iR += 1
		_, iR_cardinality = hdt.search_triples("", p, "")
		count_iR_triple += iR_cardinality
		print ('this iR relation is ', p)


# count_trans_rel_triples
print ('there are ', count_s, ' symmetric relations')
print ('gives ', count_s_triple, 'triples')
print ('-------')
print ('there are ', count_antiS, 'antisymmetric relations')
print ('gives ', count_antiS_triple, 'triples')

print ('-------')
print ('there are ', count_aS, ' asymmetric relations')
print ('gives ', count_aS_triple, 'triples')

print ('-------')
print ('there are ', count_r, ' reflexive relations')
print ('gives ', count_r_triple, 'triples')

print ('-------')
print ('there are ', count_iR, ' irreflexive relations')
print ('gives ', count_iR_triple, 'triples')

print ('#######################')



def print_relation_info(p):

	_, cardinality = hdt.search_triples("", p, "")
	print ("cardinality: ", cardinality)

	_, s_cardinality = hdt.search_triples(p, type, t)
	if s_cardinality >= 1:
		print ('transitive')

	_, s_cardinality = hdt.search_triples(p, type, s)
	if s_cardinality >= 1:
		print ('symmetric')

	_, antiS_cardinality = hdt.search_triples(p, type, antiS)
	if antiS_cardinality >= 1:
		print ('antisymmetric')

	_, aS_cardinality = hdt.search_triples(p, type, aS)
	if aS_cardinality >= 1:
		print ('asymmetric')


	_, r_cardinality = hdt.search_triples(p, type, r)
	if r_cardinality >= 1:
		print ('reflexive')

	_, iR_cardinality = hdt.search_triples(p, type, iR)
	if iR_cardinality >= 1:
		print ('irreflexive')

has_part = "http://www.obofoundry.org/ro/ro.owl#has_part"
print ('as for ', has_part)
print_relation_info (has_part)


is_part_of = "http://dbpedia.org/ontology/isPartOf"
print ('as for ', is_part_of)
print_relation_info (is_part_of)

triples, cardinality = hdt.search_triples("", is_part_of, "")
cot = 0
for (l, p , r) in triples:
	r_triples, r_cardinality = hdt.search_triples(r, is_part_of, l)
	if r_cardinality >0:
		print (l, r)
		cot+= 1
	if cot > 100:
		break


# print some examples of is_part_of

# has_part = "http://dbpedia.org/ontology/hasPart"
# print ('as for ', has_part)
# print_relation_info (has_part)

# print ('now print their SCC info')

# trans_collect_large = [
# # "http://dbpedia.org/ontology/order",
# # "http://dbpedia.org/ontology/family",
# "http://www.geonames.org/ontology#parentADM1"]
#
#
#
#
# def print_SCC_info(p):
# 	print (p)
# 	graph = nx.DiGraph()
# 	t_triples, t_cardinality = hdt.search_triples("", p, "")
# 	print ("amount of triples: ", t_cardinality)
# 	for (l, p, r) in t_triples:
# 		graph.add_edge(l,r)
#
# 	try:
# 		collect_nodes_remove= []
# 		for n in graph.nodes():
# 			if graph.in_degree(n) == 0 or graph.out_degree(n) == 0:
# 				collect_nodes_remove.append(n)
#
# 		graph.remove_nodes_from(collect_nodes_remove)
#
# 		print ('now the amount of triples : ', graph.number_of_edges())
# 		print ('now the amount of nodes : ', graph.number_of_nodes())
#
#
# 		mydict = {}
# 		for n in graph.nodes:
# 			collect_succssor = []
# 			for s in graph.successors(n):
# 				collect_succssor.append(s)
# 			mydict[n] = collect_succssor
# 		scc = tarjan(mydict)
#
#
#
# 		filter_scc = [x for x in scc if len(x)>1]
# 		# if len(filter_scc) > 5:
# 		print('# Connected Component Filtered: ', len(filter_scc))
# 		ct = Counter()
# 		for f in filter_scc:
# 			ct[len(f)] += 1
# 		print ('SCC info', ct)
#
#
# 	except Exception as e:
# 		print ('oh there is an error: ', e)


# print ('there are in total : ', len(trans_collect_large ))
# for p in trans_collect_large:
# 	print ('p = ', p)
# 	# print('Do you want to study this predicate ? (y/n):')
# 	# x = input()
# 	# if x == 'y':
# 	print_SCC_info(p)
# 	# else:
# 		# print ('next\n')

#
# count = 0
# for p in inv_collect:
#     t_triples, t_cardinality = hdt.search_triples("", p, "")
#     if t_cardinality > 1000000:
#         ct[p] = t_cardinality
#         print('inv: ', p, ' : ', t_cardinality)
#         count += 1
#
# print ('inv: count over million', count)
#
# sort_ct = sorted(ct.items(), key=lambda x: x[1], reverse=True)
# for p in sort_ct:
#     print (p)
#
#
#
# print (' ....... type ........')
# triples, cardinality = hdt.search_triples(type, '', '')
# print ('There are ', cardinality, ' properties for TYPE')
# for (s, p, o) in triples:
#     print ('\tpredicate:  ', p)
#     print ('\tobject: ', o)
#     print ('\n')


# triples, cardinality = hdt.search_triples("", "", s)
# print ('There are ', cardinality, ' symmetric properties')
# collect_symmetric_properties = set()
# for (s, p, o) in triples:
#     # print ('\tsubject: ', s)
#     # print ('\tpredicate:  ', p)
#     # print ('\n')
#     collect_symmetric_properties.add(s)
#
# triples, cardinality = hdt.search_triples("", "", aS)
# print ('There are ', cardinality, ' assymmetric properties')
# collect_assymmetric_properties = set()
# for (s, p, o) in triples:
#     # print ('\tsubject: ', s)
#     # print ('\tpredicate:  ', p)
#     # print ('\n')
#     collect_assymmetric_properties.add(s)
#
#
#
# triples, cardinality = hdt.search_triples("", "", r)
# print ('There are ', cardinality, ' reflexive properties')
# collect_reflexive_properties = set()
# for (s, p, o) in triples:
#     # print ('\tsubject: ', s)
#     # print ('\tpredicate:  ', p)
#     # print ('\n')
#     collect_reflexive_properties.add(s)
#
#
# triples, cardinality = hdt.search_triples("", "", iR)
# print ('There are ', cardinality, ' irreflexive properties')
# collect_irreflexive_properties = set()
# for (s, p, o) in triples:
# 	# print ('\tsubject: ', s)
# 	# print ('\tpredicate:  ', p)
# 	# print ('\n')
# 	collect_irreflexive_properties.add(s)

# this prints some irreflexive transitve ones
# triples, cardinality = hdt.search_triples("", type, iR)
# print ('iR: ', cardinality)
# for (s, p, o) in triples:
# 	# triples, cardinality = hdt.search_triples(s, "", t)
# 	if s in trans_collect:
# 		print ('Transitive and irreflexive ===> ', s)
#
# triples, cardinality = hdt.search_triples("", type, r)
# print ('r: ', cardinality)
# for (s, p, o) in triples:
# 	# triples, cardinality = hdt.search_triples(s, type, t)
# 	if s in trans_collect:
# 		print ('Transitive and reflexive ===> ', s)
#
#
# #
#
#
# collect_equivalent_properties = collect_reflexive_properties.intersection(collect_symmetric_properties.intersection(collect_transitive_properties))
# print ('There are ', len(collect_equivalent_properties), ' equivalent properties')
#
#
# # ====
# print ('not symmetric but reflexive:')
# tmp = collect_transitive_properties.intersection(collect_reflexive_properties).difference(collect_assymmetric_properties).difference(collect_symmetric_properties)
# print ('size: ', len(tmp))
# if len(tmp) > 0:
#     print ('example:', list(tmp)[0])
#
#
# print ('not symmetric and not reflexive:')
# tmp = collect_transitive_properties.difference(collect_reflexive_properties).difference(collect_irreflexive_properties).difference(collect_assymmetric_properties).difference(collect_symmetric_properties)
# print ('size: ', len(tmp))
# if len(tmp) > 0:
#     print ('example:', list(tmp)[0])
#
# print ('not symmetric and irreflexive:')
# tmp = collect_transitive_properties.intersection(collect_irreflexive_properties).difference(collect_assymmetric_properties).difference(collect_symmetric_properties)
# print ('size: ', len(tmp))
# if len(tmp) > 0:
#     print ('example:', list(tmp)[0])
#
#
# # =====
# print ('#######')
#
# print ('symmetric and not reflexive:')
# tmp = collect_transitive_properties.intersection(collect_symmetric_properties).difference(collect_irreflexive_properties).difference(collect_reflexive_properties)
# print ('size: ', len(tmp))
# if len(tmp) > 0:
#     print ('example:', list(tmp)[0])
#
# print ('symmetric and irreflexive:')
# tmp = collect_transitive_properties.intersection(collect_symmetric_properties).intersection(collect_irreflexive_properties)
# print ('size: ', len(tmp))
# if len(tmp) > 0:
#     print ('example:', list(tmp)[0])
#
# # =====
# print ('#######')
#
# print ('assymmetric and reflexive:')
# tmp = collect_transitive_properties.intersection(collect_assymmetric_properties).intersection(collect_reflexive_properties)
# print ('size: ', len(tmp))
# if len(tmp) > 0:
#     print ('example:', list(tmp)[0])
#
# print ('assymmetric and not reflexive:')
# tmp = collect_transitive_properties.intersection(collect_assymmetric_properties).difference(collect_irreflexive_properties).difference(collect_reflexive_properties)
# print ('size: ', len(tmp))
# if len(tmp) > 0:
#     print ('example:', list(tmp)[0])
#
# print ('assymmetric and irreflexive:')
# tmp = collect_transitive_properties.intersection(collect_assymmetric_properties).intersection(collect_irreflexive_properties)
# print ('size: ', len(tmp))
# if len(tmp) > 0:
#     print ('example:', list(tmp)[0])

#
# for b in both:
#     # print ('\n\n')
#     # prepare a graph:
#     graph = nx.DiGraph()
#     triples, cardinality = hdt.search_triples("", b, "")
#     if cardinality >= 100000:
#         print ('too large to find all cycles: ', cardinality,' for ', b)
#     else:
#         collect_pairs = []
#         for (s, _, o) in triples:
#             collect_pairs.append((s, o))
#         graph.add_edges_from(collect_pairs)
#         c = []
#         try:
#             c = nx.find_cycle(graph)
#         except :
#             # print ('no cycle found for ', b)
#             pass
#         if len(c) > 0:
#             print('found ', len(c), ' cycles for ', b)
#             print (c)
#             print ('graph (edge) size = ',cardinality)
#             print('\n')

#
# geo = 'http://www.geonames.org/ontology#parentFeature'
#
# # subClassOf
# intervalContains = 'http://www.w3.org/2006/time#intervalContains'
# intervalDuring = 'http://www.w3.org/2006/time#intervalDuring'
#
# hasPart = 'http://purl.org/dc/terms/hasPart'
# isPartOf = 'http://purl.org/dc/terms/isPartOf'
#
# broader = 'http://www.w3.org/2004/02/skos/core#broader'
# narrower = 'http://www.w3.org/2004/02/skos/core#narrower'
#
# broaderTransitive = 'http://www.w3.org/2004/02/skos/core#broaderTransitive'
# narrowerTransitive = 'http://www.w3.org/2004/02/skos/core#narrowerTransitive'
#
# list_relations = [geo, subClassOf, subPropertyOf, intervalContains, intervalDuring, hasPart, isPartOf, broader, narrower, broaderTransitive, narrowerTransitive]
#
#
# s = "http://www.w3.org/2002/07/owl#SymmetricProperty"
# aS = "http://www.w3.org/2002/07/owl#AsymmetricProperty"
# r = "http://www.w3.org/2002/07/owl#ReflexiveProperty"
# iR = "http://www.w3.org/2002/07/owl#IrreflexiveProperty"
# f = "http://www.w3.org/2002/07/owl#FunctionalProperty"
# ivf = ' http://www.w3.org/2002/07/owl#InverseFunctionalProperty'
#
# ub = 'http://www.daml.org/2000/12/daml+oil#UnambiguousProperty'
# uq = 'http://www.daml.org/2001/03/daml+oil#UniqueProperty'
#
#
# list_properties = [s, aS, r, iR, f, ivf, ub, uq]
#
# for r in list_relations:
#     # test SymmetricProperty, assymmetric, etc.
#     triples, cardinality = hdt.search_triples('', r, '')
#     print ('This relation ',r, ' has triples : ', cardinality)
#
#     # for test_p in list_properties:
#     #     triples, cardinality = hdt.search_triples(r, "", test_p)
#     #     for (s, p , o) in triples:
#     #         print ('subject  : ', s)
#     #         print ('predicate: ', p)
#     #         print ('object   : ', o, '\n\n')
#
#
# print('===== test other properties =====')
#
# for r in [intervalDuring]:
#     print('=======================:::::::: ', r)
#     # test SymmetricProperty, assymmetric, etc.
#     triples, cardinality = hdt.search_triples(r, "", "")
#     for (s, p , o) in triples:
#         print ('subject  : ', s)
#         print ('predicate: ', p)
#         print ('object   : ', o, '\n\n')
