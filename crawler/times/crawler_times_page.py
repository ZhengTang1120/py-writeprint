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

#current_url = 'http://search.time.com/results.html?Ntt=%s&N=0&Nty=1&p=2&cmd=tags&x=0&y=0'

#item_url = 'http://entertainment.time.com/2012/10/17/the-muggles-take-manhattan-j-k-rowling-live-at-lincoln-center/'
#item_url = 'http://content.time.com/time/magazine/article/0,9171,1900238,00.html'
#item_url = """http://poy.time.com/2012/12/19/runner-up-tim-cook-the-technologist/"""
#item_url = """http://techland.time.com/2009/07/17/fridays-nerd-news-top-five/"""

#item_url = '''http://content.time.com/time/specials/packages/article/0,28804,2016836_2016859_2017095,00.html'''
#item_url = '''http://techland.time.com/2010/05/24/the-lost-finale-reviewed-by-someone-whos-never-seen-lost-before/'''
#item_url = '''http://techland.time.com/2010/01/15/app-club-n-o-v-a-halo-goodbye/'''
#item_url = '''http://techland.time.com/2009/12/14/james-cameron-almost-died-making-the-abyss/'''

#item_url = '''http://content.time.com/time/specials/packages/article/0,28804,1945379_1943868_1943885,00.html'''

#item_url = '''http://business.time.com/2013/12/05/why-obscure-fed-policy-might-mean-higher-bank-fees/'''
item_url = '''http://content.time.com/time/quotes/0,26174,2006289,00.html'''

item_url = '''http://content.time.com/time/magazine/article/0,9171,984867,00.html'''


info_article = tt.get_article(item_url, p)

try :
  pass
except Exception, e :
  print e
  print '[exception] %s'%item_url

print info_article
print info_article['head']
print info_article['title']

exit(0)


for author in json_loaded.iterkeys() :
  author = author.strip(' ')
  json_path = os.path.join('corpus','%s.json'%re.sub("\s+",'_',author))
  print json_path
  if(os.path.exists(json_path)) :
    f = open(json_path)
    continue
  else :
    f = open(json_path, 'w')
    json.dump({}, f)
    f.close()
    f = open(json_path)

  json_author = json.load(f)
  f.close()

  current_url = current_url%author
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
      print item_url

      item_date  = tt.get_date(item)
#      item_title = tt.get_title_article(item)

      try :
        info_article = tt.get_article(item_url, p)
      except Exception :
        print '[exception] %s'%item_url
        continue

      if info_article['core'] == None :
        print '[no_core] %s'%item_url
        continue

      if info_article['head'] == None :
        print '[no_head] %s'%item_url
        continue

      content = info_article['head'] + info_article['core']

      d = {
        'author'    : item_author,
        'published' : item_date,
        'title'     : info_article['title'],
        'content'   : content,
        'url'       : item_url
      }
      json_author[item_url] = d

      f = open(json_path, 'w')
      json.dump(json_author, f)
      f.close()

      r = random.uniform(0,2)
      time.sleep(r)      
    if flag_stop :
      exit(0)
