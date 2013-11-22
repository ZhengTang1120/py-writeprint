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

sys.path.append('../../parpyn/pp')
import pp
sys.path.append('../../parpyn')
import ppython

import tempfile

def get_open_fds():
    '''
    return the number of open file descriptors for current process

    .. warning: will only work on UNIX-like os-es.
    '''
    import subprocess
    import os

    pid = os.getpid()
    procs = subprocess.check_output( 
        [ "lsof", '-w', '-Ff', "-p", str( pid ) ] )

    nprocs = len( 
        filter( 
            lambda s: s and s[ 0 ] == 'f' and s[1: ].isdigit(),
            procs.split( '\n' ) )
        )
    return nprocs



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

def run_chromosomes(chromosomes, cmd) :
  nb_cpu = -1
  servers_ok = ('*',)
  run_pp = ppython.RunningMethod_pp('', nb_cpu, servers_ok)
  for chromosome in chromosomes :
    str_chromosome = ''.join([str(i) for i in chromosome])
    fd, tmp_path = tempfile.mkstemp(dir='/data/chercheurs/brixtel/writeprint/tmp/')
    f = open(tmp_path, 'w')
    f.write(str_chromosome)
    f.close()
    os.close(fd)
    cmd[3] = tmp_path
    str_cmd = ' '.join(cmd)
    print str_cmd
    exit(0)
    run_pp.addCommand(str_cmd)
  res = run_pp.run()
  run_pp.destroy()
  return res

def fitness_analyser(fitnesses) :
  val_max = -1
  list_max = []
  for i,f in enumerate(fitnesses) :
    if f > val_max :
      val_max = f
      list_max = [i]
    elif f == val_max :
      list_max.append(i)
    else :
      pass
  return val_max, list_max

def population_chromosome_analyser(population) :
  list_nb_genes = []
  for chromosome in population :
    list_nb_genes.append(sum(chromosome))
  return min(list_nb_genes), max(list_nb_genes), float(sum(list_nb_genes)) / len(list_nb_genes)

def run_chromosome(chromosome, cmd) :
  cmd[3] = ''.join([str(i) for i in chromosome])
  a = subprocess.check_output(cmd)
  return float(a)

list_path = [os.path.abspath(p) for p in args.list_path]
cmd = ['python', '/home/personnels/brixtel/SVN/py-writeprint/writeprint/writeprint_chromosome.ga.py',
  '-c', '',
  '--testType', str(args.testType),
  '--learnType', str(args.learnType),
  '-t', str(args.testcorpus),
  '-i', str(args.idtest), 
  '--ngramMinFreq', str(args.ngramMinFreq),
  '--ngramMaxFreq', str(args.ngramMaxFreq),
  '-d', str(args.diroutput),
  '-o', str(args.fileoutput)] + list_path

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

  nb_generations = 125
  size_population = 10
  population = tw.init_population(size_population, len(base_vector))

  fitness_population = [float(f) for f in run_chromosomes(population,cmd)]

#  for chromosome in population :
#    fitness_population.append(run_chromosome(chromosome, cmd))#   tw.fitness(chromosome, base_vector, authors_features, authors_test))

  print fitness_population
  for i in xrange(nb_generations) :
    selected = tw.selection(population, fitness_population)
    #mutate
    mutants = []
    for chromosome in selected :
      if random.randint(0,1) == 1 :
        mutants.append(tw.mutate(chromosome))
    #lobotomize
    lobos = []
    for chromosome in selected :
      if random.randint(0,1) == 1 :
        lobos.append(tw.lobotomize(chromosome))

    #crossover 
    crossed = []
    for chromosome1, chromosome2 in itertools.combinations(selected, 2) :
      if random.randint(0,10) == 1 :
        crossed.append(tw.crossover(chromosome1, chromosome2))
    
    population = mutants + crossed + selected + lobos
#    fitness_population = []
    fitness_population = [float(f) for f in run_chromosomes(population,cmd)]
#    for chromosome in population :
#      fitness_population.append(tw.fitness(chromosome, base_vector, authors_features, authors_test))
#      fitness_population.append(run_chromosome(chromosome, cmd))

    print fitness_population
    print max(fitness_population), '::', sum(fitness_population) / float(len(fitness_population))

    fitness_max, list_id = fitness_analyser(fitness_population)
    population_max = [population[i] for i in list_id]
    min_size, max_size, avg_size = population_chromosome_analyser(population_max)
    print 'chromosomes ::', min_size, max_size, avg_size    
    print 

    print get_open_fds()

  selected = tw.selection(population, fitness_population)
  fitness_population = [float(f) for f in run_chromosomes(population,cmd)]
  print max(fitness_population), '::', sum(fitness_population) / float(len(fitness_population))

  print fitness_population
  fitness_max, list_id = fitness_analyser(fitness_population)
  population_max = [population[i] for i in list_id]
  min_size, max_size, avg_size = population_chromosome_analyser(population_max)
  print 'chromosomes ::', min_size, max_size, avg_size    


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
