#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import json
import random
import sys

sys.path.append('../')
from sklearn import svm

##
# GA functions
##

def create_random_chromosome(len_chromosome) :
  chromosome = [random.randint(0,1) for _ in xrange(len_chromosome)]
  return chromosome 

def init_population(size_population, len_chromosome) :
  pop = [create_random_chromosome(len_chromosome) for _ in xrange(size_population)]
  return pop

def mutate(chromosome) :
  l = len(chromosome)
  mutate_chromosome = chromosome[:]
  for i in xrange(l) :
    if random.randint(0,l) <= l/10 :
      mutate_chromosome[i] = 0 if chromosome[i] == 1 else 1    
  return mutate_chromosome

def crossover(chromosome1, chromosome2) :
  split = random.randint(0,len(chromosome1)-1)
  offspring = chromosome1[:split] + chromosome2[split:]
  return offspring

def selection_alpha(population, fitnesses, nb=25) :
  s = [(fitness, i) for i,fitness in enumerate(fitnesses)]
  s.sort(reverse=True)
  selected = []
  for i in xrange(nb) :
    _, id_pop = s[i]
    selected.append(population[id_pop])
  return selected

def selection(population, fitnesses, nb=25) :
  res = []
  s = [(i,p) for i,p in enumerate(population)]
  size_sample = len(population) / nb
  while 1 :
    if(len(s) == 0) :
      break
    random.shuffle(s)
    sample = []
    for _ in xrange(size_sample) :
      try :
        sample.append(s.pop())
      except Exception :
        break
    if len(sample) > 0 :
      res.append(sample)

  selected = []
  for sample in res :
    local_alphas = [(fitnesses[id_chromosome], id_chromosome) for id_chromosome,chromosome in sample]
    local_alphas.sort(reverse=True)
    selected.append(population[local_alphas[0][1]])
  return selected 


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

def chromosome2base_vector(chromosome, base_vector) :
  new_base_vector = [base_vector[i] for i,val in enumerate(chromosome) if val == 1]
  return new_base_vector

def res2score(res) :
  ok = 0
  for to_be_found, found in res :
    if to_be_found == found :
      ok += 1
  return float(ok) / len(res)

##
# SVM specific functions
##

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
# utilities to read features storaged in .json
##

def init_features_authors(list_path, set_test, args) :
  authors_features = {}
  authors_test = {}
  authors_global_features = {}
  for path in list_path :
    authors_global_features[path] = {}
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
        if feat not in authors_global_features[path] :
          authors_global_features[path][feat] = 0
        authors_global_features[path][feat] += cpt

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
  return authors_global_features, authors_features, authors_test


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

def build_vector_features(base_vector, features) :
  v = []
  for feature in base_vector :
    nb_feat = 0 if feature not in features else features[feature]
    v.append(nb_feat)
  return v

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


