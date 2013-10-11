import os
import json
import sys
import glob

sys.path.append('../tools/')
sys.path.append('../')
import tool_bs as tbs
from bs4 import BeautifulSoup

import argparse

parser = argparse.ArgumentParser(description='read corpus and features')
parser.add_argument("-d", "--diroutput", type=str, default='./',
                    help="extract the info in the dir DIROUTPUT")

parser.add_argument("-o", "--fileoutput", type=str, default='',
                    help="extract the infos in the file DIROUTPUT/FILEOUTPUT")

parser.add_argument("-i", "--index", type=str, default='',
                    help="dir INDEX, dir containing json with features")
args = parser.parse_args()
  
##
# args.diroutput
##

if not os.path.isdir(args.diroutput) :
  print 'OUTPUTDIR %s does not exist, create it or choose an other directory'%(args.diroutput)
  exit(0)

glob_expression = os.path.join(args.index, '*')

global_features = {}
core_features = {}

##
# init
##

list_path = glob.glob(glob_expression)
first_path = list_path[0]
f = open(first_path, 'r')
d = json.load(f)
f.close()
core_features_author = {}
for feat in d['global'].keys() :
  core_features_author[feat] = True

core_features_message = {}
list_messages_features = d['url'].values()
for feat in list_messages_features[0].keys() :
  core_features_message[feat] = True

for features in list_messages_features[1:] :
  for feat in core_features_message.keys() :
    if feat not in features :
      del core_features_message[feat]
      
for p in list_path[1:] :
  f = open(p, 'r')
  d = json.load(f)
  f.close()
  for feat, cpt in d['global'].iteritems() :
    if feat not in global_features :
      global_features[feat] = 0
    global_features[feat] += cpt

  for feat in core_features_author.keys() :
    if feat not in d['global'] :
      del core_features_author[feat]

  for url, message in d['url'].iteritems() :
    for feat in core_features_message.keys() :
      if feat not in message :
        del core_features_message[feat]

print 'nb. unique features in features corpus'
print 'unique features corpus : %s'%(len(global_features))
print 'intersection authors   : %s'%(len(core_features_author))
print 'intersection messages  : %s'%(len(core_features_message))
