import os
import json
import sys
import glob
import argparse

sys.path.append('../tools/')
sys.path.append('../')
import tool_bs as tbs
from bs4 import BeautifulSoup

def build_dirname(path_input) :
  root_dir, filename = os.path.split(path_input)
  f = filename.split('.')
  return f[0]

def build_filename(path_input) :
  f = path_input.split('/')
  return '%s.html'%(f[-1])

parser = argparse.ArgumentParser(description='export corpus in jsons to xhtml')
parser.add_argument("-d", "--diroutput", type=str, default='./features/',
                    help="extract the corpus in the dir DIROUTPUT")
parser.add_argument('list_path', metavar='L', type=str, nargs='+',
                    help='List of path L of files to be analysed')

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

  dirname = os.path.join(args.diroutput, build_dirname(path))
  print dirname
  if not os.path.isdir(dirname) :
    os.makedirs(dirname)

  for url in d.keys() :
    filename = build_filename(url)
    path = os.path.join(dirname, filename.encode('utf-8'))
    info = d[url]
    a = '<a href="%s">%s</a>'%(url, url)
    bs_content = BeautifulSoup(a + '<hr/>' + info['title'] + info['content'])
    f = open(path, 'w')
    f.write(bs_content.prettify().encode('utf-8'))
    f.close()

