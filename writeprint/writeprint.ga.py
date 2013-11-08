#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
#import argparse
import os
import math

import sys
sys.path.append('../')
from sklearn import svm

import tool_writeprint as tw

import itertools
import random

import subprocess

def build_vector_features(base_vector, features) :
  v = []
  for feature in base_vector :
    nb_feat = 0 if feature not in features else features[feature]
    v.append(nb_feat)
  return v

parser = tw.get_argument_parser()
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

cmd = ['python', 'writeprint_chromosome.ga.py', '-c', ''] + sys.argv[1:]
def run_chromosome(chromosome, cmd) :
  cmd[3] = ''.join([str(i) for i in chromosome])
  a = subprocess.check_output(cmd)
  return float(a)


for id_test, list_couple in json_test.iteritems() :
  set_test = set()
  for couple in list_couple :
    t = (couple[0], couple[1])
    set_test.add(t)

  global_features, authors_features, authors_test = tw.init_features(args.list_path, set_test, args)

##
# args.ngramMinFreq, args.ngramMaxFreq
##

  base_vector = filter_freq(global_features, args.ngramMinFreq, args.ngramMaxFreq)

  nb_generations = 20
  size_population = 60
  population = tw.init_population(size_population, len(base_vector))
  fitness_population = []
  for chromosome in population :
    fitness_population.append(run_chromosome(chromosome, cmd))#   tw.fitness(chromosome, base_vector, authors_features, authors_test))

  print fitness_population
  for i in xrange(nb_generations) :
    selected = tw.selection(population, fitness_population)
    #mutate
    mutants = []
    for chromosome in selected :
      if random.randint(0,1) == 1 :
        mutants.append(tw.mutate(chromosome))
    #crossover 
    crossed = []
    for chromosome1, chromosome2 in itertools.combinations(selected, 2) :
      if random.randint(0,10) == 1 :
        crossed.append(tw.crossover(chromosome1, chromosome2))
    
    population = mutants + crossed + selected
    fitness_population = []
    for chromosome in population :
#      fitness_population.append(tw.fitness(chromosome, base_vector, authors_features, authors_test))
      fitness_population.append(run_chromosome(chromosome, cmd))
    print fitness_population
    print max(fitness_population), '::', sum(fitness_population) / float(len(fitness_population))

  exit(0)





  list_vector_message = []
  list_class = []
  dict_author = {}

  cpt_author = 0
  for id_author, message in authors_features.iteritems() :
    dict_author[cpt_author] = id_author
    for features in message.itervalues() :
      v = build_vector_features(base_vector, features)
      list_vector_message.append(v)
      list_class.append(cpt_author)
    cpt_author += 1

#  svc = tw.svm_get_svc(list_vector_message, list_class)
  C = 1.
  svc = svm.SVC(kernel='linear', C=C, cache_size=1000).fit(list_vector_message, list_class)
#  svc = svm.LinearSVC(C=C).fit(list_vector_message, list_class)

#  results[id_test] = tw.svm_test_svc(svc, base_vector, authors_test, dict_author)
  results[id_test] = []
  for id_author, list_message in authors_test.iteritems() :
    res = {}
    for message in list_message :
      v = build_vector_features(base_vector, message)
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
