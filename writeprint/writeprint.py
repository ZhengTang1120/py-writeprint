#!/usr/bin/env python
# -*- coding: utf-8 -*-

#import matplotlib.pyplot as plt
import json
import glob
import argparse
import os

import sys
sys.path.append('../')
#import numpy as np
#import pylab as pl
from sklearn import svm


parser = argparse.ArgumentParser(description='run a classifier on a corpus minus a test corpus')

parser.add_argument("-d", "--diroutput", default='./', type=str,
                    help="print result in the dir DIROUTPUT")
parser.add_argument("-o", "--fileoutput", default='res.json', type=str,
                    help="print result in the file DIROUTPUT/FILEOUTPUT")
parser.add_argument("-t", "--testcorpus", default='', type=str,
                    help="use the TESTCORPUS json file")
parser.add_argument("-i", "--idtest", default='', type=str,
                    help="use the IDTEST in TESTCORPUS")

parser.add_argument("--ngramMinFreq", default=0, type=int,
                    help="consider only occuring > NGRAMMINFREQ")



parser.add_argument('list_path', metavar='L', type=str, nargs='+',
                    help='List of path L of files containing features, a file per author')

args = parser.parse_args()

##
# args.diroutput
##

if not os.path.isdir(args.diroutput) :
  print 'OUTPUTDIR %s does not exist, create it or choose an other directory'%s(args.diroutput)
  exit(0)

##
# args.testcorpus
##

if not os.path.isfile(args.testcorpus) or args.testcorpus == '' :
  print 'TESTCORPUS %s does not exists, create it using build_jeson_corpus_test.py'%(args.testcorpus)
  exit(0)

ftest     = open(args.testcorpus,'r')
json_test = json.load(ftest)
ftest.close()

##
# args.idtest
##

json_test = {args.idtest : json_test[args.idtest]} if args.idtest in json_test else json_test

results = {}

for id_test, list_couple in json_test.iteritems() :
  set_test = set()# set(list_couple)
  for couple in list_couple :
    t = (couple[0], couple[1])
    set_test.add(t)

  global_features = {}
  authors_features = {}
  authors_test = {}
#  pattern_glob = '../data/features_liberation/*'
#  pattern_glob = './features_liberation/*'
  for path in args.list_path: #glob.glob(pattern_glob) :
    f = open(path, 'r')
    d = json.load(f)
    f.close()
    author_features = {}
    for url in d['url'].keys() :
#    if path == author_test and url == message_test:
      if (path, url) in set_test :
        authors_test[path] = d['url'][url]
        continue
      features = d['url'][url]
      author_features = {}
      for feat,cpt in features.iteritems() :
        if feat not in global_features :
          global_features[feat] = 0
        global_features[feat] += cpt

      if path not in authors_features :
        authors_features[path] = {}
      authors_features[path][url] = features

##
# args.ngramMinFreq
##

  base_vector = []
  for feat in sorted(global_features, key=global_features.get, reverse=False):
    if(global_features[feat] > args.ngramMinFreq) :
      base_vector.append(feat)

  list_vector_message = []
  list_class = []
  dict_author = {}

  cpt_author = 0
  for id_author, message in authors_features.iteritems() :
    dict_author[cpt_author] = id_author
    for id_message, features in message.iteritems() :
      v = []
      for feature in base_vector :
        nb_feat = 0 if feature not in features else features[feature]
        v.append(nb_feat)
      list_vector_message.append(v)
      list_class.append(cpt_author)
    cpt_author += 1

#print list_vector_message[0]

  C = 1.
  svc = svm.SVC(kernel='linear', C=C).fit(list_vector_message, list_class)

  dict_test = {}

  for id_author, message in authors_test.iteritems() :
    v = []
    for feature in base_vector :
      nb_feat = 0 if feature not in message else message[feature]
      v.append(nb_feat)
    dict_test[id_author] = v

  results[id_test] = []
#  cpt_total = 0
#  cpt_ok = 0
  for id_author, v in dict_test.iteritems() :
    p = svc.predict(v)
    results[id_test].append((id_author, dict_author[p[0]]))
#    cpt_total += 1
#    if id_author == dict_author[p[0]] :
#      cpt_ok += 1

#  print '%s :: %s / %s'%(id_test, cpt_ok, cpt_total)

##
# args.diroutput, args.fileoutput
##


output_json = os.path.join(args.diroutput, args.fileoutput)
f = open(output_json, 'w')
json.dump(results, f)
f.close()

