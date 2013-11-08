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

def build_vector_features(base_vector, features) :
  v = []
  for feature in base_vector :
    nb_feat = 0 if feature not in features else features[feature]
    v.append(nb_feat)
  return v

parser = tw.get_argument_parser()
parser.add_argument("-c", "--chromosome", default='', type=str,
                    help="chromosome (...1001010101101100...)")

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

chromosome = [int(i) for i in args.chromosome]

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
  fitness_chromosome = tw.fitness(chromosome, base_vector, authors_features, authors_test)
  print fitness_chromosome
