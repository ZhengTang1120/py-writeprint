#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
import random
import os
import re
import glob


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

glob_expression = os.path.join(args.dirresults, '*')

res = {}
set_author = set()

for path in glob.glob(glob_expression) :
  f = open(path, 'r')
  d = json.load(f)
  f.close()

  for _,couples in d.iteritems() :
    for real_author, found_author in couples :
#      if re.search( 'Musseau', real_author) : #or re.search('Musseau', found_author) :
#        print real_author.encode('utf-8'), found_author.encode('utf-8')

      set_author.add(real_author)
      set_author.add(found_author)
      l = [real_author, found_author]
      k1 = "('%s','%s')"%(l[0], l[1])
      k2 = "('%s','%s')"%(l[1], l[0])
      if k1 not in res :
        res[k1] = 0
      if k2 not in res :
        res[k2] = 0
      res[k1] += 1
      if k1 != k2  :
        res[k2] += 1

filenames = list(set_author)
max_value = max(res.values())

matrix = []
for path1 in filenames :
  line = [] 
  for path2  in filenames :
    k = "('%s','%s')"%(path1, path2)
    v = 1 - float(res[k])/max_value if k in res else 1
    line.append(v)
  matrix.append(line)

j = {
  "signature" : "{'documentDistance': '', 'verbose': True, 'documentFilter': ['', ''], 'fileout': '', 'segmenter': ['a'], 'segmentDistance': '', 'documentDistanceFilter': ['']}",
  "filenames" :    filenames,
  "corpus_scores" : matrix
}

#print args.output
f = open(args.output, 'w')
json.dump(j,f)
f.close()

exit(0)
