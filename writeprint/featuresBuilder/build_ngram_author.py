import os
import json
import sys
import glob
import argparse

sys.path.append('../../tools/')
sys.path.append('../../')
import tool_bs as tbs
from bs4 import BeautifulSoup

import tool_features as tf

parser = argparse.ArgumentParser(description='build features according a corpus linked to an author')
parser.add_argument("-d", "--diroutput", type=str, default='./features/',
                    help="extract the features in the dir DIROUTPUT")
parser.add_argument("-o", "--fileoutput", type=str, default='',
                    help="extract the features in the file DIROUTPUT/FILEOUTPUT")
parser.add_argument("-s", "--sizengram", type=int, default=3,
                    help="extract SIZENGRAM-gram (default : -s 3)")
parser.add_argument('path', metavar='P', type=str,
                    help='path P of the json files to be analysed')

args = parser.parse_args()

f = open(args.path, 'r')
d = json.load(f)
f.close()

res = {
  'global' : True,
  'url' : {}
}

##
# args.diroutput
##

if not os.path.isdir(args.diroutput) :
  print 'OUTPUTDIR %s does not exist, create it or choose an other directory'%(args.diroutput)
  exit(0)

##
# args.fileoutput
##

fileoutput = build_json_filename_output(args.path) if args.fileoutput == '' else args.fileoutput

output_json = os.path.join(args.diroutput, fileoutput)

dict_ngram_author = {}

for url, info in d.iteritems() :
  dict_ngram_url = {}
  bs_content = BeautifulSoup(info['title'] + info['content'])
  cut = tbs.cut_bloc(bs_content.body)
  res['url'][url] = {'global' : True, 'block':[]}
  for c in cut :
    cut2bs  = tbs.cut_bloc2bs_elt(c)
    dict_ngram_block = {}
    content = ' '.join([s.strip() for s in cut2bs.strings])
    tf.ngram_extractor(content, args.sizengram, dict_ngram_author, dict_ngram_url, dict_ngram_block)
    res['url'][url]['block'].append(dict_ngram_block)
  res['url'][url]['global'] = dict_ngram_url
res['global'] = dict_ngram_author

f = open(output_json, 'w')
json.dump(res, f)
f.close()
