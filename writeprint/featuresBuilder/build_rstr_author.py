import os
import json
import sys
import glob
import argparse

sys.path.append('../../tools/')
sys.path.append('../../')
import tool_bs as tbs
from bs4 import BeautifulSoup

sys.path.append('../../rstr_max/')
from rstr_max import *

parser = argparse.ArgumentParser(description='build features according a corpus linked to an author')

parser.add_argument("-d", "--diroutput", type=str, default='./features/',
                    help="extract the features in the dir DIROUTPUT")

parser.add_argument("-o", "--fileoutput", type=str, default='',
                    help="extract the features in the file DIROUTPUT/FILEOUTPUT")
parser.add_argument("--sizeMinRstr", type=int, default=0,
                    help="extract rstr with SIZEMINRSTR < len(rstr)  (default : --sizeMinRstr 0)")

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
d= json.load(f)
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


dict_ngram_author = {}

r = Rstr_max()
idBlock_idDoc = {}

cpt_doc   = 0
cpt_block = 0
dict_block_doc = {}
dict_doc_url = {}
for url, info in d.iteritems() :
  dict_ngram_url = {}
  bs_content = BeautifulSoup(info['content'])
  cut = tbs.cut_bloc(bs_content.body)
  
  for c in cut :
    cut2bs  = tbs.cut_bloc2bs_elt(c)
    content = ''
    for s in cut2bs.strings :
      content += s
    r.add_str(content)
    dict_block_doc[cpt_block] = cpt_doc
    cpt_block += 1
  dict_doc_url[cpt_doc] = url
  cpt_doc += 1

global_features = {}
dict_url = {}
res = r.go()

for (offset_end, nb), (l, start_plage) in res.iteritems():
  id_chaine = r.idxString[offset_end-1]
  feat = r.get_repeat(id_chaine, r.idxPos[offset_end-l], l)
  global_features[feat] = nb
  for o in range(start_plage, start_plage + nb) :
    offset_global = r.res[o]
    offset = r.idxPos[offset_global]
    id_str = r.idxString[offset_global]
    id_doc = dict_block_doc[id_str]
    url = dict_doc_url[id_doc] 
    if url not in dict_url :
      dict_url[url] = {}
    if feat not in dict_url[url] :
      dict_url[url][feat] = 0
    dict_url[url][feat] += 0

res = {
  'global' : global_features,
  'url' : dict_url
}

##
# args.fileoutput
##

fileoutput  = build_json_filename_output(args.path) if args.fileoutput == '' else args.fileoutput
output_json = os.path.join(args.diroutput, fileoutput)

f = open(output_json, 'w')
json.dump(res, f)
f.close()

