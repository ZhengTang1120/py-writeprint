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

r = Rstr_max()
idBlock_idDoc = {}

cpt_doc        = 0
cpt_block      = 0
dict_block_doc = {}
dict_doc_url   = {}

#d = {
#  'url1' : {
#    'title' : '<h1>aaa</h1>',
#    'content' : '<div><p>bb</p><p>cc</p></div>'
#   },
#  'url2' : {
#    'title' : '<h1>aaa</h1>',
#    'content' : '<div><p>bb</p><p>cc</p></div>'
#   }
#}

for url, info in d.iteritems() :
  dict_ngram_url = {}
  bs_content = BeautifulSoup(info['title'] + info['content'])
  cut = tbs.cut_bloc(bs_content.body)  
  for i, c in enumerate(cut) :
    cut2bs  = tbs.cut_bloc2bs_elt(c)
    content = ' '.join([s.strip() for s in cut2bs.strings])
    r.add_str(content)
    dict_block_doc[cpt_block] = (cpt_doc, i)
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
    id_doc, id_relative_block = dict_block_doc[id_str]
    url = dict_doc_url[id_doc] 
    if url not in dict_url :
      dict_url[url] = {'global' : {}, 'block' : {}}
    if feat not in dict_url[url]['global'] :
      dict_url[url]['global'][feat] = 0
    dict_url[url]['global'][feat] += 1
    if id_relative_block not in dict_url[url]['block'] :
      dict_url[url]['block'][id_relative_block] = {}
    if feat not in dict_url[url]['block'][id_relative_block] :
      dict_url[url]['block'][id_relative_block][feat] = 0
    dict_url[url]['block'][id_relative_block][feat] += 1

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

