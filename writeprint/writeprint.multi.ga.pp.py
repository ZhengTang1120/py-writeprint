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

#def get_open_fds():
#    '''
#    return the number of open file descriptors for current process
#    .. warning: will only work on UNIX-like os-es.
#    '''
#    import subprocess
#    import os
#    pid = os.getpid()
#    procs = subprocess.check_output( 
#        [ "lsof", '-w', '-Ff', "-p", str( pid ) ] )
#    nprocs = len( 
#        filter( 
#            lambda s: s and s[ 0 ] == 'f' and s[1: ].isdigit(),
#            procs.split( '\n' ) )
#        )
#    return nprocs

def build_vector_features(base_vector, features) :
  v = []
  for feature in base_vector :
    nb_feat = 0 if feature not in features else features[feature]
    v.append(nb_feat)
  return v

parser = tw.get_argument_parser()
parser = tw.add_argument_parser(parser)
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

def make_history(population, fitnesses, history = {}) :
  for i,f in enumerate(fitnesses) :
    str_chromosome = chromosome2str(population[i])
    if str_chromosome not in history :
      history[str_chromosome] = f
  return history

def chromosome2str(chromosome) :
  return ''.join([str(i) for i in chromosome])

def run_chromosomes(chromosomes, cmd, history, args) :
  nb_cpu = args.nbcore
  tmpdir = args.tmpdir
  servers_ok = ('*',)
  run_pp = ppython.RunningMethod_pp('', nb_cpu, servers_ok)
  res_history = []
  for chromosome in chromosomes :
    str_chromosome = ''.join([str(i) for i in chromosome])

    if str_chromosome in history :
      res_history.append(history[str_chromosome])
      continue
    else :
      res_history.append('-1')

    fd, tmp_path = tempfile.mkstemp(dir=tmpdir)
    f = open(tmp_path, 'w')
    f.write(str_chromosome)
    f.close()
    os.close(fd)
    cmd[3] = tmp_path
    str_cmd = ' '.join(cmd)
    run_pp.addCommand(str_cmd)

  res_run = run_pp.run()
  res = []
  cpt = 0
  for r in res_history :
    if r == '-1' :
      res.append(res_run.pop(0))
    else :
      res.append(r)
      cpt += 1
  print 'use_history :: ', cpt, '/', len(res)
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
  list_min = []
  sum_min = len(population[0])
  sum_max = 0
  for i, chromosome in enumerate(population) :
    s = sum(chromosome)
    if s < sum_min :
      sum_min = s
      list_min = [i]
    elif s == sum_min :
      list_min.append(i)
    list_nb_genes.append(sum(chromosome))
  d = {
    'min_nb_gene'     : sum_min,
    'ids_min_nb_gene' : list_min,
    'max_nb_gene'     : max(list_nb_genes),
    'avg_nb_gene'     : float(sum(list_nb_genes)) / len(list_nb_genes)
  }
  return d

def run_chromosome(chromosome, cmd) :
  cmd[3] = ''.join([str(i) for i in chromosome])
  a = subprocess.check_output(cmd)
  return float(a)

def write_population_json(list_population, name_population, fitnesses, path_json) :
  cpt = 0
  d = {}
  for id_subpopulation, subpopulation in enumerate(list_population) :
    name = name_subpopulation[id_subpopulation]
    if name not in d :
      d[name] = {}
    for chromosome in subpopulation :
      str_chromosome = chromosome2str(chromosome)
      d[name][str_chromosome] = fitnesses[cpt]
      cpt += 1

  f = open(path_json, 'w')
  json.dump(d, f)
  f.close()


list_path = [os.path.abspath(p) for p in args.list_path]
cmd = ['python', '/home/personnels/brixtel/SVN/py-writeprint/writeprint/writeprint_chromosome.multi.ga.py',
  '-c', '',
  '--testType', str(args.testType),
  '--learnType', str(args.learnType),
  '-t', str(args.testcorpus),
#  '-i', str(args.idtest), 
  '--ngramMinFreq', str(args.ngramMinFreq),
  '--ngramMaxFreq', str(args.ngramMaxFreq),
  '-d', str(args.diroutput),
  '-o', str(args.fileoutput)] + list_path

set_test = set()

#for couple in list_couple :
#  t = (couple[0], couple[1])
#  set_test.add(t)

global_features, authors_features, test_features = tw.init_global_features(args.list_path, set_test, args)
#test_features = tw.init_test_features(args.list_path, set_test, args)
#test_features_extracted = tw.extract_features(test_features)
#diff = tw.diff_features(global_features, test_features_extracted)

base_vector = filter_freq(global_features, args.ngramMinFreq, args.ngramMaxFreq)
#mask_chromosome = tw.mask_chromosome(base_vector, diff)
#print chromosome2str(mask_chromosome)

nb_generations = args.nbgeneration
size_population = len(authors_features.keys())*10
#population = tw.init_population_mask(size_population, len(base_vector), mask_chromosome)
population = tw.init_population(size_population, len(base_vector))

fitness_population = [float(f) for f in run_chromosomes(population, cmd, {}, args)]
history = make_history(population, fitness_population)

for i in xrange(nb_generations) :
#   print 'select'
  selected = tw.selection(population, fitness_population)

  #crossover 
  crossed = []
  for chromosome1, chromosome2 in itertools.combinations(selected, 2) :
    if random.randint(0,10) == 1 :
      offspring1, offspring2 = tw.crossover2(chromosome1, chromosome2)
      crossed.append(offspring1)
      crossed.append(offspring2)
#      crossed.append(tw.crossover(chromosome1, chromosome2))


  current = selected + crossed

  #mutate
  mutants = []
  for chromosome in current :
    if random.randint(0,1) == 1 :
      mutants.append(tw.mutate(chromosome))

  #lobotomize
#  lobos = []
#  for chromosome in current :
#    if random.randint(0,1) == 1 :
#      lobos.append(tw.lobotomize(chromosome))

  #trisofy
#  trisos = []
#  for chromosome in current :
#    if random.randint(0,1) == 1 :
#      trisos.append(tw.trisofy(chromosome))

  
  population = selected + crossed + mutants# + lobos + trisos
#  population = selected + mutants + crossed
  fitness_population = [float(f) for f in run_chromosomes(population, cmd, history, args)]

  ##
  # print json
  ##

#  list_subpopulation = [selected, mutants, crossed, lobos, trisos]
#  name_subpopulation = ['selected', 'mutants', 'crossed', 'lobos', 'trisos']
#  list_subpopulation = [selected, mutants, crossed]
#  name_subpopulation = ['selected', 'mutants', 'crossed']
  list_subpopulation = [selected, crossed, mutants]
  name_subpopulation = ['selected', 'crossed', 'mutants']
  path_json = os.path.join(args.diroutput, '%04d.json'%i)
  write_population_json(list_subpopulation, name_subpopulation, fitness_population, path_json)

  history = make_history(population, fitness_population)

  print max(fitness_population), '::', sum(fitness_population) / float(len(fitness_population))

  fitness_max, list_id = fitness_analyser(fitness_population)
  population_max = [population[i] for i in list_id]
  dict_analyser = population_chromosome_analyser(population_max)
  print 'chromosomes (%s)::'%len(population[0]), dict_analyser['min_nb_gene'], dict_analyser['max_nb_gene'], dict_analyser['avg_nb_gene']    

#    print get_open_fds()

selected = tw.selection(population, fitness_population)
#tw.apply_mask_population(selected, mask_chromosome)
fitness_population = [float(f) for f in run_chromosomes(population, cmd, history, args)]
print max(fitness_population), '::', sum(fitness_population) / float(len(fitness_population))

print fitness_population
fitness_max, list_id = fitness_analyser(fitness_population)
population_max = [population[i] for i in list_id]
dict_analyser = population_chromosome_analyser(population_max)
print 'chromosomes (%s)::'%len(population[0]), dict_analyser['min_nb_gene'], dict_analyser['max_nb_gene'], dict_analyser['avg_nb_gene']    

for id_chromosome in dict_analyser['ids_min_nb_gene'] :
  print '****chromosome %s'%(id_chromosome)
  for i,gene in enumerate(population_max[id_chromosome]) :
    if gene == 1 :
      print base_vector[i]
  exit(0)

##
# args.diroutput, args.fileoutput
##

#output_json = os.path.join(args.diroutput, args.fileoutput)
#f = open(output_json, 'w')
#json.dump(results, f)
#f.close()
