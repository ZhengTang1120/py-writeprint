# -*- coding: utf-8 -*-

import json
import sys
import os
import glob
import shutil

def get_dict_json(path) :
  f = open(path, 'r')
  j = json.load(f)
  f.close()
  return j


dir_src  = sys.argv[1]
dir_from = sys.argv[2]
dir_tgt  = sys.argv[3]

glob_src = glob.glob(os.path.join(dir_src, '*'))

for path_src in glob_src :
  dirname_src,filename_src = os.path.split(path_src)
  path_from = os.path.join(dir_from, filename_src)

  if not os.path.exists(path_from) :
    path_tgt = os.path.join(dir_tgt, filename_src)
    shutil.copyfile(path_src, path_tgt)
    continue
  
  j_src  = get_dict_json(path_src)
  j_from = get_dict_json(path_from)
  j_tgt  = {}
  for url in j_src.keys() :
    if url in j_from :
      j_tgt[url] = j_from[url]
    else :
      j_tgt[url] = j_src[url]

  path_tgt = os.path.join(dir_tgt, filename_src)
  f = open(path_tgt, 'w')
  json.dump(j_tgt, f)
  f.close()

