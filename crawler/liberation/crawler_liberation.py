# -*- coding: utf-8 -*-

import re
import urllib
import random
import time
import json
import os
import tool_liberation as tl

p = {'http': 'http://proxy.unicaen.fr:3128'}
json_author_path = './author.json'
f_author = open(json_author_path)
json_loaded = json.load(f_author)
f_author.close()

url_base = 'http://www.liberation.fr/recherche/?page=%s&q=%s'
for author in json_loaded.iterkeys() :
  start = 1
  json_path = os.path.join('corpus','%s.json'%re.sub("\s+",'_',author))
  print json_path

  if(os.path.exists(json_path)) :
    f = open(json_path)
#    continue
  else :
    f = open(json_path, 'w')
    json.dump({}, f)
    f.close()
    f = open(json_path)
  json_author = json.load(f)
  f.close()
  while True :  
    url = url_base%(start, author.encode('utf-8'))
    print url
    source = urllib.urlopen(url, proxies=p)
    s = source.read()
    items = tl.get_items(s)

    if len(items) == 0 :
      break

    cpt_i = 0

    for i in items :
      cpt_i += 1
      authors = tl.get_author(i)

      if len(authors) != 1 :
        continue

      if unicode(authors[0], 'utf-8') != author :
        continue

      url_article = tl.get_url(i)
#      if json_author.has_key(url_article) :
      if url_article in json_author :
        continue

      print url_article

      published = tl.get_time(i)
      source_article = urllib.urlopen(url_article, proxies=p).read()

      try :
        main = tl.get_main_article(source_article) 
      except Exception :
        print '[exception] %s'%url_article
        continue

      core = tl.get_core_article(main)

      if core['core'] == '' :
        print '[no_core] %s'%url_article
        continue

      content = '%s %s'%(core['head'], core['core'])
#      content = '%s'%(core['core'])
      d = {
        'author' : author,
        'published' : published,
        'title' : core['title'],
        'content' : content,
        'url' : url_article
      }
      json_author[url_article] = d

      f = open(json_path, 'w')
      json.dump(json_author, f)
      f.close()

      r = random.uniform(0,2)
      time.sleep(r)
      
    start += 1
    if start > 100 :
      break
    r = random.uniform(0,5)
    time.sleep(r)
    
