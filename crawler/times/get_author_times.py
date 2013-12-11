# -*- coding:utf-8  -*-
import re
import urllib
import random
import time
import json
import os
import tool_times as tt

q = 'economy'

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

current_url = 'http://search.time.com/results.html?Ntt=%s&N=0&Nty=1&p=2&cmd=tags&x=0&y=0'%q

while True :
  source = urllib.urlopen(current_url, proxies=p)
  s = source.read()
  current_url = tt.get_next_url(s)
  items = tt.get_items(s)
  if len(items) == 0 :
    break
  for author in items :
    json_loaded[author] = ''
  print len(json_loaded.keys())

  f = open(json_author_path, 'w')
  json.dump(json_loaded, f)
  f.close()

  r = random.uniform(1,7)
  time.sleep(r)
  cpt -= 1
  if cpt == 0 :
    break
