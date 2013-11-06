#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import math

import sys
sys.path.append('../')
from sklearn import svm
import numpy

import tool_writeprint as tw

def build_vector_features(base_vector, features, list_vector_message, i) :
  for id_feat, feature in enumerate(base_vector) :
    if feature in features :
      list_vector_message[i][id_feat] = features[feature]

def get_vector_features(base_vector, features) :
  v = numpy.zeros(shape=len(base_vector), dtype=int)
  for id_feat, feature in enumerate(base_vector) :
    if feature in features :
      v[id_feat] = features[feature]
  return v

parser = tw.get_argument_parser()
args   = parser.parse_args()

##
# args.diroutput
##

if not os.path.isdir(args.diroutput) :
  print 'OUTPUTDIR %s does not exist, create it or choose an other directory'%(args.diroutput)
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
# args.ngramMaxFreq, args.ngramMinFreq
##

if args.ngramMaxFreq[-2:] == '%r' or args.ngramMinFreq[-2:] == '%r' :
  filter_freq = tw.filter_base_vector_percent_rank
  args.ngramMaxFreq = int(args.ngramMaxFreq[:-2])
  args.ngramMinFreq = int(args.ngramMinFreq[:-2])
elif args.ngramMaxFreq[-1] == 'r' or args.ngramMinFreq[-1] == 'r' :
  filter_freq = tw.filter_base_vector_rank
  args.ngramMaxFreq = int(args.ngramMaxFreq[:-1])
  args.ngramMinFreq = int(args.ngramMinFreq[:-1])
else :
  filter_freq = tw.filter_base_vector_absolute
  args.ngramMaxFreq = int(args.ngramMaxFreq)
  args.ngramMinFreq = int(args.ngramMinFreq)

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

  global_features, authors_features, authors_test = tw.init_features(args.list_path, set_test, args)

##
# args.ngramMinFreq, args.ngramMaxFreq
##

  base_vector = filter_freq(global_features, args.ngramMinFreq, args.ngramMaxFreq)
  len_base_vector = len(base_vector)
  len_authors = sum([len(messages) for messages in authors_features.itervalues()])
  list_vector_message = numpy.zeros(shape=(len_authors, len_base_vector), dtype=int)
  list_class = numpy.zeros(shape=(len_authors), dtype=int)

  dict_author = {}

  cpt_author  = 0
  cpt_message = 0
  for id_author, message in authors_features.iteritems() :
    dict_author[cpt_author] = id_author
    for features in message.itervalues() :
      build_vector_features(base_vector, features, list_vector_message, cpt_author)
      list_class[cpt_message] = cpt_author
      cpt_message += 1
    cpt_author += 1

  C = 1.
  svc = svm.SVC(kernel='linear', C=C, cache_size=1000).fit(list_vector_message, list_class)
#  svc = svm.LinearSVC(C=C).fit(list_vector_message, list_class)

  dict_test = {}
  results[id_test] = []

  for id_author, list_message in authors_test.iteritems() :
    res = {}
    for id_message, message in enumerate(list_message) :
      v = get_vector_features(base_vector, message)
      p = svc.predict(v)
      if p[0] not in res :
        res[p[0]] = 0
      res[p[0]] += 1
    sorted_res = sorted(res, key=res.get, reverse=True)
    results[id_test].append((id_author, dict_author[sorted_res[0]]))

##
# args.diroutput, args.fileoutput
##

output_json = os.path.join(args.diroutput, args.fileoutput)
f = open(output_json, 'w')
json.dump(results, f)
f.close()
