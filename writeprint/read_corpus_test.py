#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

f = open('test.json', 'r')
d = json.load(f)
f.close()

cpt = {}

for k,corpus_test in d.iteritems() :
  for author,document in corpus_test :
    if author not in cpt :
      cpt[author] = 0
    cpt[author] += 1

print cpt

