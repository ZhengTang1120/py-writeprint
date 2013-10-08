import os
import json
import sys
import glob

sys.path.append('../tools/')
sys.path.append('../')
import tool_bs as tbs
from bs4 import BeautifulSoup

import argparse

parser = argparse.ArgumentParser(description='build features according a corpus linked to an author')

parser.add_argument("-d", "--diroutput", type=str, default='./features/',
                    help="extract the features in the dir DIROUTPUT")

parser.add_argument("-o", "--fileoutput", type=str, default='',
                    help="extract the features in the file DIROUTPUT/FILEOUTPUT")
parser.add_argument("-s", "--sizengram", type=int, default=3,
                    help="extract SIZENGRAM-gram")

parser.add_argument('path', metavar='P', type=str,
                    help='path P of the json files to be analysed')

args = parser.parse_args()

def insert_chunk_cpt(d, chunk) :
  if not d.has_key(chunk) :
    d[chunk] = 0
  d[chunk] += 1

def ngram_extractor(su, n, d1, d2) :
  for i in xrange(len(su) - n) :
    chunk = su[i:i+n]
    insert_chunk_cpt(d1, chunk)
    insert_chunk_cpt(d2, chunk)

def build_json_filename_output(path_input) :
  root_dir, filename = os.path.split(path_input)
  f = filename.split('.')
  root_filename = '.'.join(f[:-1])
  json_output_filename = '.'.join([root_filename, 'features', f[-1]])
  return json_output_filename

dict_ngram = {}
res = {}

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
  bs_content = BeautifulSoup(info['content'])
  cut = tbs.cut_bloc(bs_content.body)
  for c in cut :
    cut2bs  = tbs.cut_bloc2bs_elt(c)
    content = ''
    for s in cut2bs.strings :
      content += s
    ngram_extractor(content, args.sizengram, dict_ngram_author, dict_ngram_url)
  res['url'][url] = dict_ngram_url
res['global'] = dict_ngram_author

f = open(output_json, 'w')
json.dump(res, f)
f.close()

