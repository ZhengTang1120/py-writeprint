import json
import sys
import glob

#import subprocess
import argparse

sys.path.append('../../tools/')
sys.path.append('../../')
import tool_bs as tbs
from bs4 import BeautifulSoup

sys.path.append('../../rstr_max/')
from rstr_max import *




def info_json(json) :
  nb_messages = len(json.keys())
  return {
    'nb_messages' : nb_messages
  }

def build_json_filename_output(path_input) :
  root_dir, filename = os.path.split(path_input)
  f = filename.split('.')
  root_filename = '.'.join(f[:-1])
  json_output_filename = '.'.join([root_filename, 'features', f[-1]])
  return json_output_filename

parser = argparse.ArgumentParser(description='build features according a corpus')
parser.add_argument("-d", "--diroutput", default='./features', type=str,
                    help="extract features for each author in the dir DIROUTPUT")
parser.add_argument("--messagesMin", help="only chosse author with MESSAGESMIN < nb. messages", type=int, default=0)
parser.add_argument("--messagesMax", help="only chosse author with nb. messages < MESSAGEMAX", type=int, default=10000000000)
parser.add_argument("--sizeMinRstr", type=int, default=0,
                    help="extract rstr with SIZEMINRSTR < len(rstr)  (default : --sizeMinRstr 0)")
parser.add_argument('list_path', metavar='L', type=str, nargs='+',
                    help='List of path L of files to be analysed')

args = parser.parse_args()

r = Rstr_max()

cpt_doc         = 0
cpt_block       = 0
dict_block_doc  = {}
dict_doc_url    = {}
dict_url_author = {}

history = []

dict_author = {}

for path in args.list_path :
  f = open(path, 'r')
  j = json.load(f)
  f.close()
  i = info_json(j)
  if not (args.messagesMin <= i['nb_messages'] <= args.messagesMax) :
    continue

  if path not in dict_author :
    dict_author[path] = {'global' : {}, 'url' : {}}

  for url, info in j.iteritems() :
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
    dict_url_author[url] = path
    cpt_doc += 1

print 'run rstr'
res = r.go()

for (offset_end, nb), (l, start_plage) in res.iteritems():
  id_chaine = r.idxString[offset_end-1]
  feat = r.get_repeat(id_chaine, r.idxPos[offset_end-l], l)
#  global_features[feat] = nb
  for o in xrange(start_plage, start_plage + nb) :
    offset_global = r.res[o]
    offset = r.idxPos[offset_global]
    id_str = r.idxString[offset_global]
    id_doc = dict_block_doc[id_str]
    url = dict_doc_url[id_doc]
    author = dict_url_author[url]

    if feat not in dict_author[author]['global'] :
      dict_author[author]['global'][feat] = 0
    dict_author[author]['global'][feat] += 1

    if url not in dict_author[author]['url'] :
      dict_author[author]['url'][url] = {}
    if feat not in dict_author[author]['url'][url] :
      dict_author[author]['url'][url][feat] = 0
    dict_author[author]['url'][url][feat] += 1

for author, json in dict_author.iteritems() :
  filename = build_json_filename_output(author)
  output_json = os.path.join(args.diroutput,filename)
  f = open(output_json, 'w')
  json.dump(json, f)
  f.close()

print '[done] #authors considered :: %s'%(len(dict_author))

#  cmd = 'python build_rstr_author.py --sizeMinRstr %s -d %s %s'%(args.sizeMinRstr, args.diroutput, path)
#  history.append(cmd)
#  print cmd
#  list_cmd = cmd.split(' ')
#  subprocess.call(list_cmd)

