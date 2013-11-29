#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
#import argparse
import os
import math

import sys
try :
  sys.path.append(os.path.abspath('../'))
  from sklearn import svm
except Exception, e:
  print e
  print 0.0
  exit(0)

import itertools
import random
#import tool_writeprint as tw

import argparse

##
# argument parser tools
##

def get_argument_parser() :
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
  return parser

##
# filtering features according frequency/rank
##

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

def init_global_features(list_path, set_test, args) :
  global_features = {}
  authors_features = {}
  authors_test = {}
  for path in list_path :
    f = open(path, 'r')
    d = json.load(f)
    f.close()
    unicode_path = unicode(path, 'utf-8')
#    unicode_path = unicode(os.path.abspath(path), 'utf-8')
    for url in d['url'].keys() :
      for feat,cpt in d['url'][url]['global'].iteritems() :
        if feat not in global_features :
          global_features[feat] = 0
        global_features[feat] += cpt

      if (unicode_path, url) in set_test :
        if(args.testType == 'block') :
          authors_test[path] = []
          for block in d['url'][url]['block'].keys() :
            authors_test[path].append(d['url'][url]['block'][block])
        else :
          authors_test[path] = [d['url'][url]['global']]
        continue

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

def init_test_features(list_path_features, set_test, args) :
#  global_features = {}
  authors_test = {}
  cpt = 0
  for path in list_path_features :
    f = open(path, 'r')
    d = json.load(f)
    f.close()
    unicode_path = unicode(path, 'utf-8')
    for url in d['url'].keys() :
      if (unicode_path, url) in set_test :
        if(args.testType == 'block') :
          authors_test[path] = []
          for block in d['url'][url]['block'].keys() :
            authors_test[path].append(d['url'][url]['block'][block])
        else :
          authors_test[path] = [d['url'][url]['global']]
        continue

#      for feat,cpt in d['url'][url]['global'].iteritems() :
#        if feat not in global_features :
#          global_features[feat] = 0
#        global_features[feat] += cpt
#
#      if path not in authors_features :
#        authors_features[path] = {}
#
#      if(args.learnType == 'block') :
#        for block in d['url'][url]['block'].keys() :
#          new_key = '%s_%s'%(url, block)
#          authors_features[path][new_key] = d['url'][url]['block'][block]
#
#      else :
#        authors_features[path][url] = d['url'][url]['global']
  return authors_test

def extract_features(test_features) :
  specific_test_features = {}
  for path, list_block_features in test_features.iteritems() :
    for features in list_block_features :
      for feat, cpt in features.iteritems() :
        if feat not in specific_test_features :
          specific_test_features[feat] = 0
        specific_test_features[feat] += cpt
  return specific_test_features 

def diff_features(features1, features2) :
  diff = {}
  for feat, cpt_feat in features1.iteritems() :
    new_cpt = cpt_feat - features2[feat] if feat in features2 else cpt_feat
    diff[feat] = new_cpt
  return diff

def diff_chromosome(chromosome1, chromosome2) :
  chromosome = []
  for i,g in enumerate(chromosome) :
    if chromosome2[i] == '0' :
      chromosome.append('0')
    else :
      chromosome.append(g)
  return chromosome

def mask_chromosome(base_vector, diff) :
  base_chromosome = []
  for feat in base_vector :
    if diff[feat] == 0 :
      base_chromosome.append('0')
    else :
      base_chromosome.append('1')
  return ''.join(base_chromosome)

def apply_mask(chromosome, mask) :
  new_chromosome = []
  for i,gene in enumerate(mask) :
    if gene == '0' :
      new_chromosome.append('0')
    else :
      new_chromosome.append(chromosome[i])
  chromosome = ''.join(new_chromosome)

def init_features(list_path, set_test, args) :
  global_features = {}
  authors_features = {}
  authors_test = {}
  for path in list_path :
    f = open(path, 'r')
    d = json.load(f)
    f.close()
    unicode_path = unicode(path, 'utf-8')
    for url in d['url'].keys() :
      if (unicode_path, url) in set_test :
#        print (unicode_path, url)
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


def svm_get_svc(list_vector_message, list_class) :
  C = 1.
  return svm.SVC(kernel='linear', C=C, cache_size=1000).fit(list_vector_message, list_class)

def svm_test_svc(svc, base_vector, authors_test, dict_author) :
  predict = []
  for id_author, list_block in authors_test.iteritems() :
    res = {}
    for block in list_block :
      v = build_vector_features(base_vector, block)
      p = svc.predict(v)
      if p[0] not in res :
        res[p[0]] = 0
      res[p[0]] += 1
    sorted_res = sorted(res, key=res.get, reverse=True)
    predict.append((id_author, dict_author[sorted_res[0]]))
  return predict

def chromosome2base_vector(chromosome, base_vector) :
  new_base_vector = [base_vector[i] for i,val in enumerate(chromosome) if val == '1']
  return new_base_vector

def build_vector_features(base_vector, features) :
  v = []
  for feature in base_vector :
    nb_feat = 0 if feature not in features else features[feature]
    v.append(nb_feat)
  return v

def build_input_svm_fitness(chromosome, base_vector, authors_features) :
  new_base_vector     = chromosome2base_vector(chromosome, base_vector)
  cpt_author          = 0
  dict_author         = {}
  list_vector_message = []
  list_class          = []
  for id_author, message in authors_features.iteritems() :
    dict_author[cpt_author] = id_author
    for features in message.itervalues() :
      v = build_vector_features(new_base_vector, features)
      list_vector_message.append(v)
      list_class.append(cpt_author)
    cpt_author += 1
  return new_base_vector, list_vector_message, list_class, dict_author

def fitness(chromosome, base_vector, authors_features, authors_test) :
  new_base_vector, list_vector_message, list_class, dict_author = build_input_svm_fitness(chromosome, base_vector, authors_features)
  svc = svm_get_svc(list_vector_message, list_class)
  res = svm_test_svc(svc, new_base_vector, authors_test, dict_author)
  return res2score(res)

def res2score(res) :
  ok = 0
  for to_be_found, found in res :
    if to_be_found == found :
      ok += 1
  return float(ok) / len(res)

def build_vector_features(base_vector, features) :
  v = []
  for feature in base_vector :
    nb_feat = 0 if feature not in features else features[feature]
    v.append(nb_feat)
  return v

parser = get_argument_parser()
parser.add_argument("-c", "--chromosome", default='', type=str,
                    help="path where a chromosome is storaged")

args = parser.parse_args()

path_chromosome = args.chromosome
f = open(path_chromosome, 'r')
args.chromosome = f.read().strip(' \n\t')
f.close()

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

#chromosome = [int(i) for i in args.chromosome]
fitnesses = []

for id_test, list_couple in json_test.iteritems() :
  set_test = set()
  for couple in list_couple :
    t = (os.path.abspath(couple[0]), couple[1])
    set_test.add(t)

  global_features, authors_features, authors_test = init_global_features(args.list_path, set_test, args)
#  authors_test = init_test_features(args.list_path, set_test, args)
  test_features_extracted = extract_features(authors_test)
  diff = diff_features(global_features, test_features_extracted)

  base_vector = filter_freq(global_features, args.ngramMinFreq, args.ngramMaxFreq)
  mask = mask_chromosome(base_vector, diff)
  apply_mask(args.chromosome, mask)

  fitness_chromosome = fitness(args.chromosome, base_vector, authors_features, authors_test)
  fitnesses.append(fitness_chromosome)

print float(sum(fitnesses)) / len(fitnesses)
