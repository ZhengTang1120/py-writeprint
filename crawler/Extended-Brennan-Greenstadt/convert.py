# -*- coding: utf-8 -*-

import re
import urllib
import random
import time
import json

import os
import glob

stop_list = ['imitation', 'obfuscation', 'demographics', 'verification']

def check_filename(path) :
  d, f = os.path.split(path)
  root_filename,ext = f.split('.')
  l = root_filename.split('_')
  if l[1] not in stop_list :
    return True
  return False

def txt2html(path) :
  f = open(path, 'r')
  s = f.read()
  f.close()
  print path
  su = unicode(s, 'utf-8')
  l = re.split('\s*\n\s*', su, flags = re.DOTALL|re.U)
  l = [sub.strip('\t\n ') for sub in l]
  return '<html>\n<div>%s</div>\n</html>'%'</div>\n<div>'.join(l)

corpus_path_src = 'Drexel-AMT-Corpus'

corpus_path_tgt = 'corpus'

glob_corpus_path_src = os.path.join(corpus_path_src, '*')

for author_dir in glob.glob(glob_corpus_path_src) :
  author = os.path.split(author_dir)[-1]
  author_tgt = os.path.join(corpus_path_tgt, '%s.json'%(author))
#  if not os.path.isdir(author_dir_tgt) :
#    os.mkdir(author_dir_tgt)
  a = {}
  glob_author_subdir = os.path.join(author_dir, '*.txt')
  for subdir in glob.glob(glob_author_subdir) :
    if check_filename(subdir) :
      t = txt2html(subdir)
      d = {
        'author' : author,
        'published' : '',
        'title' : '',
        'content' : t,
        'url' : subdir
      }
      a[subdir] = d

  f = open(author_tgt, 'w')
  json.dump(a, f)
  f.close()


#      print subdir
#  exit(0)

