# -*- coding:utf-8  -*-
import re
import urllib
import random
import time
import json
import os
import tool_liberation as tl

q = 'éducation'
start = 1

p = {'http': 'http://proxy.unicaen.fr:3128'}
json_author_path = './author.json'

if(os.path.exists(json_author_path)) :
  f = open(json_author_path)
else :
  f = open(json_author_path, 'w')
  json.dump({}, f)
  f.close()
  f = open(json_author_path)

json_loaded = json.load(f)
f.close()

cpt = 10000

while True :
  url = 'http://www.liberation.fr/recherche/?page=%s&q=%s'%(start, q)
  source = urllib.urlopen(url, proxies=p)
  s = source.read()
  re_item = '<li>\s*?<time[^>]*?>.*?</li>'
  re_item_compile = re.compile(re_item, re.DOTALL|re.U)
  f = re_item_compile.findall(s)
  if len(f) == 0 :
    break
  for i in f :
    for a in tl.get_author(i) :
      json_loaded[a] = ''
  print len(json_loaded.keys())
  start += 1

  f = open(json_author_path, 'w')
  json.dump(json_loaded, f)
  f.close()
  r = random.uniform(1,7)
  time.sleep(r)
  cpt -= 1
  if cpt == 0 :
    break
