#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import argparse
import os

def build_vector_features(base_vector, features) :
  v = []
  for feature in base_vector :
    nb_feat = 0 if feature not in features else features[feature]
    v.append(nb_feat)
  return v

parser = argparse.ArgumentParser(description='filter a corpus of feature')
parser.add_argument("-d", "--diroutput", default='./', type=str,
                    help="print result in the dir DIROUTPUT")
parser.add_argument("--ngramMinFreq", default=0, type=int,
                    help="consider only occuring > NGRAMMINFREQ")
parser.add_argument("--mostFreqNgram", default=0, type=str,
                    help="consider only the MOSTFREQNGRAM most frequent ngram")
parser.add_argument('list_path', metavar='L', type=str, nargs='+',
                    help='List of path L of files containing features, a file per author')
args = parser.parse_args()

##
# args.diroutput
##

if not os.path.isdir(args.diroutput) :
  print 'OUTPUTDIR %s does not exist, create it or choose an other directory'%(args.diroutput)
  exit(0)

global_features = {}
for path in args.list_path :
  f = open(path, 'r')
  d = json.load(f)
  f.close()
  for url in d['url'].keys() :
    for feat,cpt in d['url'][url].iteritems() :
      if feat not in global_features :
        global_features[feat] = 0
      global_features[feat] += cpt

base_vector = []
sorted_feat = sorted(global_features, key=global_features.get, reverse=False) 

if args.mostFreqNgram[-1] == '%' :
  percent = int(args.mostFreqNgram[:-1])
  start = int(round(float(len(sorted_feat)) / 100 * percent))
else :
  start = -int(args.mostFreqNgram)

dict_feat = {}
for feat in sorted_feat[start:] :
  if(global_features[feat] > args.ngramMinFreq) :
    dict_feat[feat] = True

for path in args.list_path :
  f = open(path, 'r')
  d = json.load(f)
  f.close()
  for feat_global in d['global'].keys() :
    if feat_global not in dict_feat :
      del d['global'][feat_global]
  for url, message in d['url'].iteritems() :
    for feat_local in message.keys() :
      if feat_local not in dict_feat :
        del d['url'][url][feat_local]
  _,filename = os.path.split(path)
  output_path = os.path.join(args.diroutput, filename)

  f = open(output_path, 'w')
  json.dump(d, f)
  f.close()
