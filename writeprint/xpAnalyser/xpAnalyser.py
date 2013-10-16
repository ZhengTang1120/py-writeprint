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
  pattern = '([0-9]+)-([0-9]+)\.json'
  pattern_compile = re.compile(pattern)
  s = pattern_compile.search(filename)
  id_xp = s.group(1)
  min_req = s.group(2)
  return {
    'id_xp'    : id_xp,
    'min_freq' : min_req
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

glob_expression = os.path.join(args.dirresults, '*')

for path in glob.glob(glob_expression) :
  root_dir, filename = os.path.split(path)
  i = get_info(filename)
  min_freq = i['min_freq']
  if min_freq not in dict_freq :
    dict_freq[min_freq] = {
      'total' : 0,
      'cpt_ok' : 0
    }

  f = open(path, 'r')
  d = json.load(f)
  f.close()
  for k,couples in d.iteritems() :
    for real_author, found_author in couples :
      dict_freq[min_freq]['total'] +=1
#      if re.search( 'Musseau', real_author) or re.search('Musseau', found_author) :
#        print real_author.encode('utf-8'), found_author.encode('utf-8')
      if real_author == found_author :
        dict_freq[min_freq]['cpt_ok'] +=1

k = sorted(dict_freq.keys())

list_x = []
list_y = []
for min_freq in k :
  list_x.append(min_freq)
  info = dict_freq[min_freq]
  percent = float(info['cpt_ok']) / info['total'] * 100
  list_y.append(str(percent))

j = {
  'data1' : {
    'x' : list_x,
    'y' : list_y
  }
}


#print args.output
f = open(args.output, 'w')
json.dump(j,f)
f.close()

