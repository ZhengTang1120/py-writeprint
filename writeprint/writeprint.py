#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import argparse
import os
import math

import sys
sys.path.append('../')
from sklearn import svm

def filter_base_vector_absolute(global_features, min_freq, max_freq) :
  sorted_feat = sorted(global_features, key=global_features.get, reverse=False)
  start = 0
  len_sorted_feat = len(sorted_feat)
  end = len_sorted_feat
  for i in xrange(len_sorted_feat) :
    feat = sorted_feat[i]
    if(global_features[feat] > min_freq) :
      start = i
      break

  for j in xrange(len_sorted_feat) :
    i = len_sorted_feat-j-1
    feat = sorted_feat[i]
    if(global_features[feat] < max_freq) :
      end = i+1
      break

  if start > end :
    start,end = end,start

  return sorted_feat[start:end]


def filter_base_vector_rank(global_features, min_rank, max_rank) :
  sorted_feat = sorted(global_features, key=global_features.get, reverse=False)
  start = 0
  len_sorted_feat = len(sorted_feat)
  end = len_sorted_feat

  previous = -1
  cpt = 1
  for i in xrange(len_sorted_feat) :
    if cpt == min_rank :
      start = i
      break
    feat = sorted_feat[i]
    if global_features[feat] != previous :
      cpt += 1
    previous = global_features[feat]

  previous = -1
  cpt = 1
  for j in xrange(len_sorted_feat) :
    i = len_sorted_feat-j-1
    if cpt == max_rank :
      end = i + 1
      break
    feat = sorted_feat[i]
    if global_features[feat] != previous :
      cpt += 1
    previous = global_features[feat]

  if start > end :
    start,end = end,start

  return sorted_feat[start:end]


def filter_base_vector_percent_rank(global_features, min_percent, max_percent) :
  sorted_feat = sorted(global_features, key=global_features.get, reverse=False)

  previous = global_features[sorted_feat[0]]
  rank = [[0]]

  for i,feat in enumerate(sorted_feat[1:]) :
    if previous != global_features[feat] :
      rank.append([i+1])
    else :
      rank[-1].append(i+1)
    previous = global_features[feat]

  nb_rank  = len(rank)
  min_rank = int(math.ceil(nb_rank * float(min_percent) / 100))
  max_rank = int(math.floor(nb_rank * float(max_percent) / 100))

  start = min(min_rank, nb_rank-max_rank)
  end   = max(min_rank, nb_rank-max_rank)

  rank_slice  = rank[start:end]
  start_slice = rank_slice[0][0]
  end_slice   = rank_slice[-1][-1]
  return sorted_feat[start_slice:end_slice+1] 

def build_vector_features(base_vector, features) :
  v = []
  for feature in base_vector :
    nb_feat = 0 if feature not in features else features[feature]
    v.append(nb_feat)
  return v

def init_features(list_path, set_test, args) :
  global_features = {}
  authors_features = {}
  authors_test = {}
  for path in list_path :
    f = open(path, 'r')
    d = json.load(f)
    f.close()
    for url in d['url'].keys() :
      if (unicode(path,'utf-8'), url) in set_test :
        if(args.testType == 'block') :
          authors_test[path] = []
          for block in d['url'][url]['block'].keys() :
            authors_test[path].append(d['url'][url]['block'][block])
        else :
          authors_test[path] = [d['url'][url]['global']]
        continue

      for feat,cpt in d['url'][url]['global'].iteritems() :
        if feat not in global_features :
          global_features[feat] = 0
        global_features[feat] += cpt

      if path not in authors_features :
        authors_features[path] = {}

      if(args.learnType == 'block') :
        for block in d['url'][url]['block'].keys() :
          new_key = '%s_%s'%(url, block)
          authors_features[path][new_key] = d['url'][url]['block'][block]

      else :
        if path not in authors_features :
          authors_features[path] = {}
        authors_features[path][url] = d['url'][url]['global']
  return global_features, authors_features, authors_test

parser = argparse.ArgumentParser(description='run a classifier on a corpus minus a test corpus')
parser.add_argument("-d", "--diroutput", default='./', type=str,
                    help="print result in the dir DIROUTPUT")
parser.add_argument("-o", "--fileoutput", default='res.json', type=str,
                    help="print result in the file DIROUTPUT/FILEOUTPUT")
parser.add_argument("-t", "--testcorpus", default='', type=str,
                    help="use the TESTCORPUS json file")
parser.add_argument("-i", "--idtest", default='', type=str,
                    help="use the IDTEST in TESTCORPUS")
parser.add_argument("--learnType", default='doc', type=str,
                    help="doc|block")
parser.add_argument("--testType", default='doc', type=str,
                    help="doc|block")
parser.add_argument("--ngramMinFreq", default=str(0), type=str,
                    help="consider only occuring > NGRAMMINFREQ")
parser.add_argument("--ngramMaxFreq", default=str(100*100*100), type=str,
                    help="consider only occuring < NGRAMMAXFREQ")
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
# args.ngramMaxFreq, args.ngramMinFreq
##

if args.ngramMaxFreq[-2:] == '%r' or args.ngramMinFreq[-2:] == '%r' :
  filter_freq = filter_base_vector_percent_rank
  args.ngramMaxFreq = int(args.ngramMaxFreq[:-2])
  args.ngramMinFreq = int(args.ngramMinFreq[:-2])
elif args.ngramMaxFreq[-1] == 'r' or args.ngramMinFreq[-1] == 'r' :
  filter_freq = filter_base_vector_rank
  args.ngramMaxFreq = int(args.ngramMaxFreq[:-1])
  args.ngramMinFreq = int(args.ngramMinFreq[:-1])
else :
  filter_freq = filter_base_vector_absolute
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

  global_features, authors_features, authors_test = init_features(args.list_path, set_test, args)

##
# args.ngramMinFreq, args.ngramMaxFreq
##
  base_vector = filter_freq(global_features, args.ngramMinFreq, args.ngramMaxFreq)

#  base_vector = []
#  sorted_feat = sorted(global_features, key=global_features.get, reverse=False)
#  start = 0
#  len_sorted_feat = len(sorted_feat)
#  end = len_sorted_feat
#  for i in xrange(len_sorted_feat) :
#    feat = sorted_feat[i]
#    if(global_features[feat] > args.ngramMinFreq) :
#      start = i
#      break
#
#  for j in xrange(len_sorted_feat) :
#    i = len_sorted_feat-j-1
#    feat = sorted_feat[i]
#    if(global_features[feat] < args.ngramMaxFreq) :
#      end = i+1
#      break
#
#  base_vector = sorted_feat[start:end]

  list_vector_message = []
  list_class = []
  dict_author = {}

  cpt_author = 0
  for id_author, message in authors_features.iteritems() :
    dict_author[cpt_author] = id_author
    for _, features in message.iteritems() :
      v = build_vector_features(base_vector, features)
      list_vector_message.append(v)
      list_class.append(cpt_author)
    cpt_author += 1

  C = 1.
  svc = svm.SVC(kernel='linear', C=C).fit(list_vector_message, list_class)

  dict_test = {}
  results[id_test] = []

  for id_author, list_message in authors_test.iteritems() :
    res = {}
    for id_message, message in enumerate(list_message) :
      v = build_vector_features(base_vector, message)
      p = svc.predict(v)
      if p[0] not in res :
        res[p[0]] = 0
      res[p[0]] += 1
    sorted_res = sorted(res, key=res.get, reverse=True)
    results[id_test].append((id_author, dict_author[sorted_res[0]]))
#    print dict_author[sorted_res[0]], id_author


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
