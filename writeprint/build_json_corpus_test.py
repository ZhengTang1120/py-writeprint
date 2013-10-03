#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
import random
import os

parser = argparse.ArgumentParser(description='build samples from a corpus of fetures')

parser.add_argument("-d", "--diroutput", default='./', type=str,
                    help="extract sample in the dir DIROUTPUT")
parser.add_argument("-o", "--fileoutput", default='sample.json', type=str,
                    help="extract sample in the file DIROUTPUT/FILEOUTPUT")
parser.add_argument('list_path', metavar='L', type=str, nargs='+',
                    help='List of path L of files containing features, a file per author')

args = parser.parse_args()

##
# args.diroutput
##

if not os.path.isdir(args.diroutput) :
  print 'OUTPUTDIR %s does not exist, create it or choose an other directory'%s(args.diroutput)
  exit(0)

a = {}

for path in args.list_path :
  f = open(path, 'r')
  d = json.load(f)
  f.close()
  a[path] = []
  for url in d['url'].keys() :
    a[path].append(url)

all_test_corpora = {}
nb_iter = 100

for i in xrange(nb_iter) :
  test = [] 
  for path, list_url in a.iteritems() :
    pick = random.randint(0, len(list_url)-1)  
    test.append((path,list_url[pick]))
  all_test_corpora[str(i)] = test

##
# args.diroutput, args.fileoutput
##

output_json = os.path.join(args.diroutput, args.fileoutput)#'test.json'

f = open(output_json, 'w')
json.dump(all_test_corpora, f)
f.close()
