#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import json
import random
import sys
import math
import os

sys.path.append('../')
from sklearn import svm

##
# GA functions
##

#def create_random_chromosome(len_chromosome) :
#  chromosome = [random.randint(0,1) for _ in xrange(len_chromosome)]
#  return chromosome 

def create_random_chromosome(len_chromosome, luck=1000) :
  chromosome = [random.randint(1,luck)/luck for _ in xrange(len_chromosome)]
  return chromosome 

def init_population(size_population, len_chromosome, luck=1000) :
  pop = [create_random_chromosome(len_chromosome, luck) for _ in xrange(size_population)]
  return pop

def lobotomize(chromosome, luck=5) :
  l = len(chromosome)
  mutate_chromosome = chromosome[:]
  for i in xrange(l) :
    if chromosome[i] == 1 and random.randint(1,luck) == 1 : 
      mutate_chromosome[i] = 0
  return mutate_chromosome

def trisofy(chromosome) :
  l = len(chromosome)
  mutate_chromosome = chromosome[:]
  s = sum(chromosome)
  for i in xrange(l) :
    if chromosome[i] == 0 and random.randint(1,l) < s : 
      mutate_chromosome[i] = 1
  return mutate_chromosome

def trisofy2(chromosome, luck=5) :
  l = len(chromosome)
  mutate_chromosome = chromosome[:]
  for i in xrange(l) :
    if chromosome[i] == 0 and random.randint(1,luck) == 1 : 
      mutate_chromosome[i] = 1
  return mutate_chromosome

def mutate(chromosome, luck=1000) :
  l = len(chromosome)
  mutate_chromosome = chromosome[:]
  for i in xrange(l) :
    if random.randint(1,luck) == 1 :
      mutate_chromosome[i] = 0 if chromosome[i] == 1 else 1
  return mutate_chromosome

def crossover(chromosome1, chromosome2) :
  split = random.randint(0,len(chromosome1)-1)
  offspring = chromosome1[:split] + chromosome2[split:]
  return offspring

def crossover2(chromosome1, chromosome2) :
  split = random.randint(0,len(chromosome1)-1)
  offspring1 = chromosome1[:split] + chromosome2[split:]
  offspring2 = chromosome2[:split] + chromosome1[split:]
  return offspring1, offspring2

def selection_alpha(population, fitnesses, nb=25) :
  s = [(fitness, i) for i,fitness in enumerate(fitnesses)]
  s.sort(reverse=True)
  selected = []
  for i in xrange(nb) :
    _, id_pop = s[i]
    selected.append(population[id_pop])
  return selected

def selection_tournament(population, fitnesses, nb=25) :
  res = []
  s = [(i,p) for i,p in enumerate(population)]
  if nb >= len(population) :
    return population
  size_sample = int(math.floor(float(len(population) / nb)))
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

def selection(population, fitnesses, nb=20) :
  res = []
  s = [(i,p) for i,p in enumerate(population)]
#  print 'nb ::, ', nb
  if nb >= len(population) :
    return population
  size_sample = int(math.floor(float(len(population)) / nb))
#  print 'size_sample ::, ', size_sample
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
#  print 'nb_sample ::', len(res)
  for sample in res :
    local_alphas = [(fitnesses[id_chromosome], sum(population[id_chromosome]), id_chromosome) for id_chromosome,chromosome in sample]
    local_alphas.sort(key=lambda x: (x[0], -x[1]), reverse=True)
    selected.append(population[local_alphas[0][2]])
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

def add_argument_parser(parser) :
  parser.add_argument("--tmpdir", default='/data/chercheurs/brixtel/writeprint/tmp/', type=str,
                      help="stock tempfile in TEMPFILE")
  parser.add_argument("--processchromosome", default='/data/personnels/brixtel/SVN/py-writeprint/writeprint/writeprint_chromosome.ga.py', type=str,
                      help="use program at path PROCESSCHROMOSOME to process a single chromosome")
  parser.add_argument("--nbcore", default=20, type=int,
                      help="use NBCORE cores")
  parser.add_argument("--nbgeneration", default=100, type=int,
                      help="loop NBGENERATION times")
  parser.add_argument("--nbselect", default=25, type=int,
                      help="select NBSELECT chromosome each generation")
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
    unicode_path = unicode(path, 'utf-8')
#    unicode_path = unicode(os.path.abspath(path), 'utf-8')
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
#    unicode_path = unicode(os.path.abspath(path), 'utf-8')
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

########

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

def mask_chromosome(base_vector, diff) :
  base_chromosome = []
  for feat in base_vector :
    if diff[feat] == 0 :
      base_chromosome.append('0')
    else :
      base_chromosome.append('1')
  return base_chromosome

def apply_mask(chromosome, mask) :
  for i,gene in enumerate(mask) :
    if gene == '0' :
      chromosome[i] = 0

def apply_mask_population(list_chromosome, mask) :
  for chromosome in list_chromosome :
    apply_mask(chromosome, mask)

def create_random_chromosome_mask(len_chromosome, mask, luck=1000) :
  chromosome = []
  for i in xrange(len_chromosome) :
    chromosome.append(random.randint(1,luck)/luck if mask[i] == '1' else 0)
  return chromosome

def init_population_mask(size_population, len_chromosome, mask, luck=1000) :
  pop = [create_random_chromosome_mask(len_chromosome, mask, luck) for _ in xrange(size_population)]
  return pop

