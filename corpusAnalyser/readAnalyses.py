import os
import json
import sys
import glob

sys.path.append('../tools/')
sys.path.append('../')
import tool_bs as tbs
from bs4 import BeautifulSoup

import argparse

import math

#ecart type
def standart_deviation(rep) :
  n = len(rep)
  if n == 0 :
    return 0
  moy = avg(rep)
  v = 0.
  for i in xrange(n) :
    v += math.pow(rep[i]-moy,2)
  v /= n
  return math.sqrt(math.fabs(v))

#esperance
def expected_value(rep) :
  n = len(rep)
  s = sum(rep)
  e = 0.
  for i in xrange(n) :
    e += i * (float(rep[i]) / s)
  return e

#moyenne
def avg(rep) :
  return float(sum(rep))/len(rep)

parser = argparse.ArgumentParser(description='build features according a corpus linked to an author')

parser.add_argument("-j", "--jsoninput", type=str, default='out.json',
                    help="read the analysis in JSONINPUT")

args = parser.parse_args()

f = open(args.jsoninput, 'r')
j = json.load(f)
f.close()

for k,v in j['global'].iteritems() :
  print k,v

print 'avg. #block per message :: %s'%(float(j['global']['nbBlocks']) / j['global']['nbMessages'])
print 'avg. #car per message :: %s'%(float(j['global']['nbCars']) / j['global']['nbMessages'])

lb = []
lc = []
lm = []

for a,i in j['authors'].iteritems() :
  lb.append(i['nbBlocks'])
  lc.append(i['nbCars'])
  lm.append(i['nbMessages'])

print 'avg. #blocks per author ::', avg(lb), '+/-', standart_deviation(lb)
print 'avg. #cars per author ::', avg(lc), '+/-', standart_deviation(lc)
print 'avg. #messages per author ::', avg(lm), '+/-', standart_deviation(lm)

exit(0)



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

def build_original_filename(path) :
  root_dir, filename = os.path.split(path)
  f = filename.split('.')
  return "%s.json"%(f[0])
  
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

glob_expression = os.path.join(args.index, '*')

for p in glob.glob(glob_expression) :
  original_filename = build_original_filename(p)
  path_doc = os.path.join(args.corpus, original_filename)
  f = open(path_doc, 'r')
  d = json.load(f)
  f.close()
  print path_doc

  cpt_doc = 0
  cpt_cut = 0
  len_content = 0
  for url, info in d.iteritems() :
    dict_ngram_url = {}
    bs_content = BeautifulSoup(info['content'])
    cut = tbs.cut_bloc(bs_content.body)    
    for c in cut :
      cut2bs  = tbs.cut_bloc2bs_elt(c)
      for s in cut2bs.strings :
        len_content += len(s)
      cpt_cut += 1
    cpt_doc += 1

  res['global']['nbMessages'] += cpt_doc
  res['global']['nbBlocks'] += cpt_cut
  res['global']['nbCars'] += len_content

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
