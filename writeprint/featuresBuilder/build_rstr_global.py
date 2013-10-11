import json
import sys
import glob

import subprocess
import argparse

def info_json(json) :
  nb_messages = len(json.keys())
  return {
    'nb_messages' : nb_messages
  }

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

history = []

for path in args.list_path :
  f = open(path, 'r')
  j = json.load(f)
  f.close()
  i = info_json(j)
  if not (args.messagesMin <= i['nb_messages'] <= args.messagesMax) :
    continue
  cmd = 'python build_rstr_author.py --sizeMinRstr %s -d %s %s'%(args.sizeMinRstr, args.diroutput, path)
  history.append(cmd)
  print cmd
  list_cmd = cmd.split(' ')
  subprocess.call(list_cmd)

print '[done] #authors considered :: %s'%(len(history))
