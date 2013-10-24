#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import argparse
import os

import sys
sys.path.append('../')
from sklearn import svm

def build_vector_features(base_vector, features) :
  v = []
  for feature in base_vector :
    nb_feat = 0 if feature not in features else features[feature]
    v.append(nb_feat)
  return v


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
  for path in args.list_path :
    f = open(path, 'r')
    d = json.load(f)
    f.close()
    for url in d['url'].keys() :
      if (path, url) in set_test :
        authors_test[path] = d['url'][url]['global']
        continue

      for feat,cpt in d['url'][url]['global'].iteritems() :
        if feat not in global_features :
          global_features[feat] = 0
        global_features[feat] += cpt

      if path not in authors_features :
        authors_features[path] = {}
      authors_features[path][url] = d['url'][url]['global']

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
    for _, features in message.iteritems() :
      v = build_vector_features(base_vector, features)
#      v = []
#      for feature in base_vector :
#        nb_feat = 0 if feature not in features else features[feature]
#        v.append(nb_feat)
      list_vector_message.append(v)
      list_class.append(cpt_author)
    cpt_author += 1

#print list_vector_message[0]

  C = 1.
  svc = svm.SVC(kernel='linear', C=C).fit(list_vector_message, list_class)

  dict_test = {}
  results[id_test] = []

  for id_author, message in authors_test.iteritems() :
#    v = []
#    for feature in base_vector :
#      nb_feat = 0 if feature not in message else message[feature]
#      v.append(nb_feat)
#    dict_test[id_author] = v
    v = build_vector_features(base_vector, message)
    p = svc.predict(v)
    results[id_test].append((id_author, dict_author[p[0]]))

#  for id_author, v in dict_test.iteritems() :
#    p = svc.predict(v)
#    results[id_test].append((id_author, dict_author[p[0]]))

##
# args.diroutput, args.fileoutput
##

output_json = os.path.join(args.diroutput, args.fileoutput)
f = open(output_json, 'w')
json.dump(results, f)
f.close()

