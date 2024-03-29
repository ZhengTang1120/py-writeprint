# -*- coding: utf-8 -*-

import re
import urllib
import random
import time
import json
import os
import sys
import tool_liberation as tl

#sys.path.append('../tools/')
sys.path.append('../../')
#import tool_bs as tbs
from bs4 import BeautifulSoup

def get_items_liberation(source) :
  re_item = '<li>\s*?<time[^>]*?>.*?</li>'
  re_item_compile = re.compile(re_item, re.DOTALL|re.U)
  f = re_item_compile.findall(s)
  return f

def get_time_liberation(item) :
  re_published = 'datetime="(.*?)"'
  re_published_compile = re.compile(re_published, re.DOTALL|re.U)
  published = re_published_compile.search(item)
  return published.group(1)

def get_url_liberation(item) :
  re_url = 'href="([^"]*?)"'
  re_url_compile = re.compile(re_url)
  s = re_url_compile.search(item)
  return rebuild_url_liberation(s.group(1))

def get_author_liberation(item) :
  re_author = '<span class="authorname">(.*?)</span>'
  re_author_compile = re.compile(re_author, re.DOTALL|re.U)
  fi = re_author_compile.finditer(item)

  res = []
  for m in fi :
    author = m.group(1).strip()
    re.sub("\s+", ' ', author, flags=re.DOTALL|re.U)
    res.append(author)
  return res

def rebuild_url_liberation(suffix) :
  return 'http://www.liberation.fr%s'%suffix

def get_main_article(source_article) :
  re_main = '<article.*?</article>'
  re_main_compile = re.compile(re_main, re.U|re.DOTALL)
  main = re_main_compile.search(source_article)
  return main.group(0)

def get_core_article(main_article) :
  res = {}
  re_title = '<h1 itemprop="headline"[^>]*?>.*?</h1>'
  re_title_compile = re.compile(re_title, re.U|re.DOTALL)
  title = re_title_compile.search(main_article)
  res['title'] = title.group(0) if title != None else ''

  re_core = '</aside>(<div[^>]*?.*?</(div|p)>)<span class="author"[^>]*?>'
  re_core_compile = re.compile(re_core, re.U|re.DOTALL)
  core = re_core_compile.search(main_article)
  if core != None :
    res['core'] = core.group(1)
  else :
    res['core'] = ''

  re_head = '<h2 itemprop="description"[^>]*?>.*?</h2>'
  re_head_compile = re.compile(re_head, re.U|re.DOTALL)
  head = re_head_compile.search(main_article)
  if head != None and core != None:
    if head.end(0) <= core.start(1) :
      res['head'] = head.group(0)
    else :
      res['head'] = ''
  else :
    res['head'] = ''


  return res


p = {'http': 'http://proxy.unicaen.fr:3128'}
url_article = sys.argv[1]
source_article = urllib.urlopen(url_article, proxies=p).read()

try :
  main = tl.get_main_article(source_article) 
except Exception :
  exit(0)


core = get_core_article(main)

if core['core'] == '' :
  exit(0)

content = '%s %s'%(core['head'], core['core'])

bs_main = BeautifulSoup(content)
print bs_main.prettify()

exit(0)

d = {
  'author' : author,
  'published' : published,
  'title' : core['title'],
  'content' : content,
  'url' : url_article
}



url_base = 'http://www.liberation.fr/recherche/?page=%s&q=%s'
for author in json_loaded.iterkeys() :
  start = 1
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
  while True :  
    url = url_base%(start, author.encode('utf-8'))
    source = urllib.urlopen(url, proxies=p)
    s = source.read()
    f = get_items_liberation(s)

    if len(f) == 0 :
      break

    cpt_i = 0

    for i in f :
      cpt_i += 1
      authors = get_author_liberation(i)

      if len(authors) != 1 :
        continue

      if unicode(authors[0], 'utf-8') != author :
        continue

      url_article = get_url_liberation(i)
#      if json_author.has_key(url_article) :
      if url_article in json_author :
        continue

      print url_article

      published = get_time_liberation(i)
      source_article = urllib.urlopen(url_article, proxies=p).read()

      try :
        main = get_main_article(source_article) 
      except Exception :
        continue

      core = get_core_article(main)

      if core['core'] == '' :
        continue

      content = '%s %s'%(core['head'], core['core'])
      d = {
        'author' : author,
        'published' : published,
        'title' : core['title'],
        'content' : content,
        'url' : url_article
      }
      json_author[url_article] = d
      r = random.uniform(0,2)
      time.sleep(r)

    f = open(json_path, 'w')
    json.dump(json_author, f)
    f.close()
      
    start += 1
    if start > 100 :
      break
    r = random.uniform(0,5)
    time.sleep(r)
    
