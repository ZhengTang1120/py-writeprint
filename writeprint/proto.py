#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append('../')

import math

import numpy as np
import pylab as pl
from sklearn import svm, datasets

#import matplotlib.pyplot as plt
#import json
#import sys
#import glob

def insert_chunk_cpt(d, chunk) :
  if not d.has_key(chunk) :
    d[chunk] = 0
  d[chunk] += 1

def ngram_extractor(su, n, d) :
  for i in xrange(len(su) - (n-1)) :
    chunk = su[i:i+n]
    insert_chunk_cpt(d, chunk)

def sort_ngram(a, b) :
  return dict_ngram[a] - dict_ngram[b]

def filtering_ngram(dict_ngram_global, dict_ngram_author, MFT) :
  d = {}
  for chunk, cpt in dict_ngram_global.iteritems() :
    if not chunk in dict_ngram_author :
      continue
    if dict_ngram_author[chunk] < MFT :
      continue
    d[chunk] = cpt
  return d

def IG(gt, ak, inv) :
  ig = overall_H(ak) - conditional_H(gt, ak, inv)
  return ig

def overall_H(ak) :
  res = 0.
  nb_messages_total = 0.
  for k, messages in enumerate(ak) :
    nb_messages_total += len(messages)
  for k, messages in enumerate(ak) :
    p = len(messages) / nb_messages_total
    res += p * math.log(p, 2)
  return -res

def conditional_H(gt, ak, inv) :
  nb_occ_gt = 0.
  for k, messages in inv[gt].iteritems() :
    nb_occ_gt += sum(messages.values())
  res = 0.
  for k,_ in enumerate(ak) :
    if k not in inv[gt] :
      res += 0
    else :
      m = sum(inv[gt][k].values())
      p = m / nb_occ_gt
      res += p * math.log(p, 2)  
  return -res

#def W_t_k() :
#  pass

a1 = ['abc', 'abd', 'abz']
a2 = ['efg', 'afg']


list_author = [a1, a2]

dict_g = {}
G = {}

for k, messages in enumerate(list_author) :
  dict_g[k] = {}
  for i, m in enumerate(messages) :
    dict_g[k][i] = {}
    ngram_extractor(m, 1, dict_g[k][i])
    ngram_extractor(m, 1, G)

inv_dict_g = {}

print G

for k, messages in dict_g.iteritems() :
  for i, mi in messages.iteritems() :
    for ngram, cpt in mi.iteritems() :
      if ngram not in inv_dict_g :
        inv_dict_g[ngram] = {}
      if k not in inv_dict_g[ngram] :
        inv_dict_g[ngram][k] = {}
      if i not in inv_dict_g[ngram][k] :
        inv_dict_g[ngram][k][i] = 0
      inv_dict_g[ngram][k][i] += cpt
  

W = {}      
for ngram, cpt in G.iteritems() :
#  c = conditional_H(ngram, list_author, inv_dict_g)
#  o = overall_H(list_author)
  r = IG(ngram, list_author, inv_dict_g)
  W[ngram] = r
#  c = conditional_H(k, ngram, inv_dict_g)

base_vector = []

for w in sorted(G, key=G.get, reverse=False):
  base_vector.append(w)

print base_vector

list_vector_message = []
list_class = []

for id_author, message in dict_g.iteritems() :
  for id_message, ngrams in message.iteritems() :
    v = []
    for feature in base_vector :
      if feature not in ngrams :
        v.append(0)
      else :
        v.append(ngrams[feature])
    list_vector_message.append(v)
    list_class.append(id_author)

print list_vector_message
print list_class

C = 1.
svc = svm.SVC(kernel='linear', C=C).fit(list_vector_message, list_class)

a = svc.predict([0,0,0,0,1,1,0,0])

print a

exit(0)


print inv_dict_g

#print dict_g
print G

exit(0)

chunk_author = {}

#print G
#print dict_g

for k, G_t_k in dict_g.iteritems() :
  for ngram, cpt in G_t_k.iteritems() :
    if ngram not in chunk_author :
      chunk_author[ngram] = {}
    chunk_author[ngram][k] = cpt

print chunk_author

#print IG(list_author, G, chunk_author)

exit(0)

