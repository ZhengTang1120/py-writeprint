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

parser.add_argument("-d", "--diroutput", type=str, default='./',
                    help="extract the info in the dir DIROUTPUT")

parser.add_argument("-o", "--fileoutput", type=str, default='',
                    help="extract the infos in the file DIROUTPUT/FILEOUTPUT")

parser.add_argument("-i", "--index", type=str, default='',
                    help="")

parser.add_argument('path', metavar='P', type=str, nargs='+',
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
res = {
  'global' : {
     'nbMessages' : 0,
     'nbBlocks' : 0,
     'nbCars' : 0
   },
  'authors' : {}
}


##
# args.diroutput
##

if not os.path.isdir(args.diroutput) :
  print 'OUTPUTDIR %s does not exist, create it or choose an other directory'%(args.diroutput)
  exit(0)

for p in args.path :
  f = open(p, 'r')
  d = json.load(f)
  f.close()
  print d['global'].keys()

  cpt_doc = 0
  for url, info in d.iteritems() :
    dict_ngram_url = {}
    print info.keys()
    bs_content = BeautifulSoup(info['content'])
    cut = tbs.cut_bloc(bs_content.body)    
    cpt_cut = 0
    len_content = 0
    for c in cut :
      cut2bs  = tbs.cut_bloc2bs_elt(c)
      for s in cut2bs.strings :
        len_content += len(s)
      cpt_cut += 1
    cpt_doc += 1

  dict_ngram_author = {
    'nbMessages' : cpt_doc,
    'nbBlocks' : cpt_cut,
    'nbCars' : len_content
  }
  res['authors'][p] = dict_ngram_author

output_json = os.path.join(args.diroutput, args.fileoutput)
f = open(output_json, 'w')
json.dump(res, f)
f.close()
