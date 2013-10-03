#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
import random
import os

parser = argparse.ArgumentParser(description='Analyse results of xps')

parser.add_argument('list_path', metavar='L', type=str, nargs='+',
                    help='List of path L of files containing xp results, a file per xp')

args = parser.parse_args()

a = {}

total  = 0
cpt_ok = 0

for path in args.list_path :
  f = open(path, 'r')
  d = json.load(f)
  f.close()
  for k,couples in d.iteritems() :
    for real_author, found_author in couples :
      total += 1
      if real_author == found_author :
        cpt_ok += 1

print "%s / %s"%(cpt_ok, total)
print "%s %%"%(cpt_ok / total * 100)
