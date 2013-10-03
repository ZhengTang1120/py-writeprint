#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import glob
import pprint
import random

import sys
sys.path.append('../')
from sklearn import svm

pattern_glob = '../data/features_liberation/*'
a = {}

for path in glob.glob(pattern_glob) :
  f = open(path, 'r')
  d = json.load(f)
  f.close()
  a[path] = []
  for url in d['url'].keys() :
    a[path].append(url)

all_test_corpora = {}
nb_iter = 50

for i in xrange(nb_iter) :
  test = [] 
  for path, list_url in a.iteritems() :
    pick = random.randint(0, len(list_url)-1)  
    test.append((path,list_url[pick]))
  all_test_corpora[str(i)] = test

output_json = 'test.json'

f = open(output_json, 'w')
json.dump(all_test_corpora, f)
f.close()
