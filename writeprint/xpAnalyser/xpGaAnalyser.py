#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
import random
import os
import re
import glob

import matplotlib.pyplot as plt

def get_info(filename) :
  pattern = '([0-9]+)\.json'
  pattern_compile = re.compile(pattern)
  s = pattern_compile.search(filename)
  cpt_generation = s.group(1)
  return {
    'cpt_generation'    : cpt_generation,
  }


parser = argparse.ArgumentParser(description='Analyse results of xps')
parser.add_argument('-r', '--dirresults', type=str,
                    help='dir DIRRESULTS : dir where results of an xp are storaged')
parser.add_argument('-o', '--output', type=str, default='out_xp.json',
                    help='write data in OUTPUT')
args = parser.parse_args()

a = {}

total  = 0
cpt_ok = 0

dict_freq = {}

k = ['crossed', 'mutants', 'lobos', 'selected', 'trisos']
#subres = {
#  'x' : [],
#  'max_fitness' : [],
#  'max_fitness_len_max' : [],
#  'max_fitness_len_min' : [],
#  'min_fitness' : [],
#  'min_fitness_len_max' : [],
#  'min_fitness_len_min' : []
#}

res = {}
for names in k :
  res[names] = {
    'x' : [],
    'max_fitness' : [],
    'max_fitness_len_max' : [],
    'max_fitness_len_min' : [],
    'min_fitness' : [],
    'min_fitness_len_max' : [],
    'min_fitness_len_min' : []
  }

glob_expression = os.path.join(args.dirresults, '*')

def str2chromosome(chromosome_str) :
  return [int(i) for i in chromosome_str]

def get_info_population(population) :
  max_fitness     = -1
  max_chromosomes = []
  min_fitness = 100*100*100
  min_chromosomes = []

  for chromosome_str, fitness in population.iteritems() :
    if fitness > max_fitness :
      max_fitness = fitness
      max_chromosomes = [chromosome_str]
    elif fitness == max_fitness :
      max_chromosomes.append(chromosome_str)
    if fitness < min_fitness :
      min_fitness = fitness
      min_chromosomes = [chromosome_str]
    elif fitness == min_fitness :
      min_chromosomes.append(chromosome_str)
  
  max_chromosomes = [str2chromosome(chromosome_str) for chromosome_str in max_chromosomes]
  len_chromosomes = [sum(c) for c in max_chromosomes]
  max_min_len = min(len_chromosomes)
  max_max_len = max(len_chromosomes)

  min_chromosomes = [str2chromosome(chromosome_str) for chromosome_str in min_chromosomes]
  len_chromosomes = [sum(c) for c in min_chromosomes]
  min_min_len = min(len_chromosomes)
  min_max_len = max(len_chromosomes)

  res = {
    'max_fitness' : max_fitness,
    'max_fitness_len_max' : max_max_len,
    'max_fitness_len_min' : max_min_len,
    'min_fitness' : min_fitness,
    'min_fitness_len_max' : min_max_len,
    'min_fitness_len_min' : min_min_len
  }
  return res


for path in glob.glob(glob_expression) :
  root_dir, filename = os.path.split(path)
  i = get_info(filename)
  f = open(path, 'r')
  d = json.load(f)
  f.close()
  cpt = i['cpt_generation']
  print cpt
  for name in k :
    if name == 'selected' :
      print name, cpt
    res[name]['x'].append(int(cpt))
    info = get_info_population(d[name])
    for key, value in info.iteritems() :
      res[name][key].append(value)

f = open(args.output, 'w')
json.dump(res,f)
f.close()

