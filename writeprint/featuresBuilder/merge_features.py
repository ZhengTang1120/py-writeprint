import json
import sys
import glob
import os

import subprocess
import argparse

def info_json(json) :
  return {
    'nb_messages' : len(json.keys())
  }

parser = argparse.ArgumentParser(description='merge corpus of features')
parser.add_argument("-d", "--diroutput", default='./features', type=str,
                    help="merge features of each author into the dir DIROUTPUT")
parser.add_argument('list_path', metavar='D', type=str, nargs='+',
                    help='List of path D of directories to be analysed')

args = parser.parse_args()

##
# args.diroutput
##

if not os.path.isdir(args.diroutput) :
  print 'OUTPUTDIR %s does not exist, create it or choose an other directory'%(args.diroutput)
  exit(0)

history = {}

for path_dir in args.list_path :
  glob_current = os.path.join(path_dir, '*')
  for path_json in glob.glob(glob_current) :
    d,f = os.path.split(path_json)
    j = json.load(open(path_json))
    if f not in history :
      history[f] = {'global': j['global'], 'url': j['url']}
    else :
      for feat, nbFeat in j['global'].iteritems() :
        history[f]['global'][feat] = nbFeat
      for url, local in j['url'].iteritems() :
        for feat, nbFeat in local.iteritems() :
          history[f]['url'][url][feat] = nbFeat

for filename, j in history.iteritems() :
  path_json = os.path.join(args.diroutput, filename)
  f = open(path_json, 'w')
  json.dump(j, f)
  f.close()
