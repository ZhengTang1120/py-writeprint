#!/usr/bin/env python
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import json
import sys
import glob

def sort_ngram(a, b) :
  return dict_ngram[b] - dict_ngram[a]

f = open('ngram.json', 'r')
d = json.load(f)
dict_ngram = d['global']
#dict_ngram_author = d['authors']['corpus/Alain_Auffray.json']
dict_ngram_author = d['authors']['../crawler_liberation/corpus/Bernadette_Sauvaget.json']

keys = dict_ngram.keys()
keys.sort(sort_ngram)

info_x = []
info_y = []
inverted_index = {}

cpt = 1
for chunk in keys :
  info_x.append(cpt)
  info_y.append(dict_ngram[chunk])
  inverted_index[chunk] = cpt
  cpt += 1

info_y_author = [0]*len(info_x)

for c, nb in dict_ngram_author.iteritems() :
  inv = inverted_index[c]-1
  info_y_author[inv] = nb


#name_legend.append(info['name_legend'])
plt.plot(info_x, info_y, 'r-')
plt.plot(info_x, info_y_author, 'g-')

#plt.xlabel('len(string)')
#plt.ylabel('seconds')
#plt.legend(list(name_legend), 'upper left', shadow = True)
#plt.yscale('log')
plt.xscale('log')
plt.savefig('out.png')
