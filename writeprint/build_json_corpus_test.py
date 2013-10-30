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
parser.add_argument("-n", "--nbIter", default=100, type=int,
                    help="nb. of iterations NBITER")
parser.add_argument("-t", "--typeTest", default='doc', type=str,
                    help="doc|block")
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
u = {}

for path in args.list_path :
  f = open(path, 'r')
  d = json.load(f)
  f.close()
  a[path] = []
  for url in d['url'].keys() :
    a[path].append(url)
    u[url] = len(d['url'][url]['block'].keys())

all_test_corpora = {}

if args.typeTest == 'block':
  for i in xrange(args.nbIter) :
    test = [] 
    for path, list_url in a.iteritems() :
      pickUrl = random.randint(0, len(list_url)-1)  
      url = list_url[pickUrl]
      nbBlock = u[url]
      pickBlock = random.randint(0, nbBlock-1)
      test.append((path,url,pickBlock))
    all_test_corpora[str(i)] = test

else :
  for i in xrange(args.nbIter) :
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
