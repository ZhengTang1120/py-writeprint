#!/usr/bin/env python
# -*- coding: utf-8 -*-

#import matplotlib.pyplot as plt
import json
import glob

import sys
sys.path.append('../')
#import numpy as np
#import pylab as pl
from sklearn import svm

#author_test  = 'features_liberation/Matthieu_Ecoiffier.features.json'
#message_test = 'http://www.liberation.fr/politiques/2013/08/18/la-mere-patrie_925425'
#subcorpus_test = {
#  'couple' : [(author_test, message_test)]
#}

ftest     = open('test.json','r')
json_test = json.load(ftest)
ftest.close()

for id_test, list_couple in json_test.iteritems() :
  set_test = set()# set(list_couple)
  for couple in list_couple :
    t = (couple[0], couple[1])
    set_test.add(t)

  global_features = {}
  authors_features = {}
  authors_test = {}
  pattern_glob = '../data/features_liberation/*'
#  pattern_glob = './features_liberation/*'

  for path in glob.glob(pattern_glob) :
    f = open(path, 'r')
    d = json.load(f)
    f.close()
    author_features = {}
    for url in d['url'].keys() :
#    if path == author_test and url == message_test:
      if (path, url) in set_test :
        authors_test[path] = d['url'][url]
        continue
      features = d['url'][url]
      author_features = {}
      for feat,cpt in features.iteritems() :
        if feat not in global_features :
          global_features[feat] = 0
        global_features[feat] += cpt

      if path not in authors_features :
        authors_features[path] = {}
      authors_features[path][url] = features


  base_vector = []
  for feat in sorted(global_features, key=global_features.get, reverse=False):
    if(global_features[feat] > 10) :
      base_vector.append(feat)

  list_vector_message = []
  list_class = []
  dict_author = {}

  cpt_author = 0
  for id_author, message in authors_features.iteritems() :
    dict_author[cpt_author] = id_author
    for id_message, features in message.iteritems() :
      v = []
      for feature in base_vector :
        nb_feat = 0 if feature not in features else features[feature]
        v.append(nb_feat)
      list_vector_message.append(v)
      list_class.append(cpt_author)
    cpt_author += 1

#print list_vector_message[0]

  C = 1.
  svc = svm.SVC(kernel='linear', C=C).fit(list_vector_message, list_class)

  dict_test = {}

  for id_author, message in authors_test.iteritems() :
    v = []
    for feature in base_vector :
      nb_feat = 0 if feature not in message else message[feature]
      v.append(nb_feat)
    dict_test[id_author] = v

  cpt_total = 0
  cpt_ok = 0
  for id_author, v in dict_test.iteritems() :
    p = svc.predict(v)
    cpt_total += 1
    if id_author == dict_author[p[0]] :
      cpt_ok += 1

  print '%s :: %s / %s'%(id_test, cpt_ok, cpt_total)

