#!/usr/bin/env python
# -*- coding: utf-8 -*-

#import matplotlib.pyplot as plt
import json
import glob
import argparse
import os

import sys
sys.path.append('../')
#import numpy as np
#import pylab as pl
from sklearn import svm

parser = argparse.ArgumentParser(description='evolution of the size of the base vector according frequency of features')

parser.add_argument("-d", "--diroutput", default='./', type=str,
                    help="print result in the dir DIROUTPUT")
parser.add_argument("-o", "--fileoutput", default='res.json', type=str,
                    help="print result in the file DIROUTPUT/FILEOUTPUT")
parser.add_argument("--maxFreq", default=2500, type=int,
                    help="consider only occuring < MAXFREQ")
parser.add_argument('list_path', metavar='L', type=str, nargs='+',
                    help='List of path L of files containing features, a file per author')

args = parser.parse_args()

##
# args.diroutput
##

if not os.path.isdir(args.diroutput) :
  print 'OUTPUTDIR %s does not exist, create it or choose an other directory'%s(args.diroutput)
  exit(0)

global_features = {}
for path in args.list_path :
  f = open(path, 'r')
  d = json.load(f)
  f.close()
  for url in d['url'].keys() :
    features = d['url'][url]['global']
    for feat,cpt in features.iteritems() :
      if feat not in global_features :
        global_features[feat] = 0
      global_features[feat] += cpt

list_x = []
list_y = []
cpt = 0
sorted_global_features = sorted(global_features, key=global_features.get)
len_global_features = len(global_features)
cursor = 0

while cpt < args.maxFreq :
  base_vector = []
  for i,feat in enumerate(sorted_global_features[cursor:]) :
    if(global_features[feat] > cpt) :
      cursor += i
      break
  list_x.append(cpt)
  list_y.append(len_global_features-cursor)
  cpt += 1

res = {
  'data0' : {
    'x' : list_x, 
    'y' : list_y 
  }
}

output_json = os.path.join(args.diroutput, args.fileoutput)
f = open(output_json, 'w')
json.dump(res, f)
f.close()
