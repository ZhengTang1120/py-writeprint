import os
import json
import sys
import glob
import argparse

sys.path.append('../../tools/')
sys.path.append('../../')
import tool_bs as tbs
from bs4 import BeautifulSoup


def build_json_filename_output(path_input) :
  root_dir, filename = os.path.split(path_input)
  f = filename.split('.')
  root_filename = '.'.join(f[:-1])
  json_output_filename = '.'.join([root_filename, 'features', f[-1]])
  return json_output_filename

parser = argparse.ArgumentParser(description='build a subcorpus according criteria')
parser.add_argument("-d", "--diroutput", type=str, default='./features/',
                    help="extract the corpus in the dir DIROUTPUT")
parser.add_argument('list_path', metavar='L', type=str, nargs='+',
                    help='List of path L of files to be analysed')

parser.add_argument("--alineasMin", help="only select messages with ALINEAMIN < nb. alineas (title not included)", type=int, default=0)
parser.add_argument("--alineasMax", help="only select messages with nb. alineas < ALINEASMAX(title not included)", type=int, default=10000000000)
parser.add_argument("--messagesMin", help="only select authors with MESSAGESMIN < nb. messages", type=int, default=0)
parser.add_argument("--messagesMax", help="only select authors with nb. messages < MESSAGEMAX", type=int, default=10000000000)

args = parser.parse_args()

##
# args.diroutput
##

if not os.path.isdir(args.diroutput) :
  print 'OUTPUTDIR %s does not exist, create it or choose an other directory'%(args.diroutput)
  exit(0)

cpt = 0

for path in args.list_path :
  f = open(path, 'r')
  d = json.load(f)
  f.close()

  for url in d.keys() :
    info = d[url]
    bs_content = BeautifulSoup(info['content'])
    cut = tbs.cut_bloc(bs_content.body)
    if len(cut) <= args.alineasMin or args.alineasMax <= len(cut) :
      del d[url]

  nb_doc = len(d.keys())

  if args.messagesMin <= nb_doc <= args.messagesMax :
    _, filename_src = os.path.split(path)
    filename_tgt = build_json_filename_output(filename_src)
    path_tgt = os.path.join(args.diroutput, filename_tgt)
    f_tgt = open(path_tgt, 'w')
    json.dump(d, f_tgt)
    cpt += 1

print '[done] author considered :: %s'%(cpt)

