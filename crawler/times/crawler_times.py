# -*- coding: utf-8 -*-

import re
import urllib
import random
import time
import json
import os
import tool_times as tt

p = {'http': 'http://proxy.unicaen.fr:3128'}
json_author_path = './author.json'
f_author = open(json_author_path)
json_loaded = json.load(f_author)
f_author.close()

base_url = 'http://search.time.com/results.html?Ntt=%s&N=0&Nty=1&p=2&cmd=tags&x=0&y=0'

for author in json_loaded.iterkeys() :
  author = author.strip(' ')
  json_path = os.path.join('corpus','%s.json'%re.sub("\s+",'_',author))
  if(os.path.exists(json_path)) :
#    f = open(json_path)
    continue
  else :
    f = open(json_path, 'w')
    json.dump({}, f)
    f.close()
    f = open(json_path)

  json_author = json.load(f)
  f.close()

  current_url = base_url%author.encode('utf-8')
  flag_stop = False
  page = 0
  while True :
    print 'page :: %s'%page
    page += 1
    source = urllib.urlopen(current_url, proxies=p)
    s = source.read()
    try :
      current_url = tt.get_next_url(s)
    except Exception :
      flag_stop = True

    list_items = tt.get_list_items(s)
    for item in list_items :
      item_author = tt.get_author(item)
      if item_author == None :
        continue
#      print item_author
      item_author = tt.clean_author(item_author).strip(' ')
      item_author = unicode(item_author, 'utf-8')
      if item_author != author :
        continue

#      print author, item_author 
#      print item_date
      item_url = tt.get_url_article(item)
      if item_url in json_author :
        continue
      print item_author, item_url

      item_date  = tt.get_date(item)
#      item_title = tt.get_title_article(item)

      try :
        info_article = tt.get_article(item_url, p)
      except Exception :
        print '  [exception]'
        continue

      if info_article['core'] == None :
        print '  [no_core]'
        continue

      if info_article['title'] == None :
        print '  [no_title]'
        continue

      if info_article['head'] == None :
        info_article['head'] = ''
        print '  [no_head]'

      content = info_article['head'] + info_article['core']

      try :
        unicode(content, 'utf-8')
      except :
        print '  [error_encoding]'
        continue

      d = {
        'author'    : item_author,
        'published' : item_date,
        'title'     : info_article['title'],
        'content'   : content,
        'url'       : item_url
      }

      json_author[item_url] = d
      f = open(json_path, 'w')
 
      try :
        json.dump(json_author, f, indent=4)
      except :
        print '  [no dump]'
        f.close()
        continue

      f.close()

      r = random.uniform(1,2)
      time.sleep(r)      
    if flag_stop or page >= 30:
      r = random.uniform(1,10)
      time.sleep(r)      
      break
