import re
import urllib
import random
import time
from urlparse import urlparse

def get_next_url(source) :
  pattern = "<a title=['\"]Next['\"].*?href=['\"](.*?)['\"][^>]*?>"
  pattern_compile = re.compile(pattern, re.DOTALL|re.U)
  s = pattern_compile.search(source)
  return s.group(1)

def get_items(source) :
  pattern = '<div class="tout">.*?<span class="name">([^<]+)</span>'
  pattern_compile = re.compile(pattern, re.DOTALL|re.U)
  s = pattern_compile.findall(source)
  f = []
  for n in s :
    if n[:3] == 'By ' :
      f.append(n[3:])
    else :
      f.append(n)
  return f

def get_list_items(source) :
  pattern = '<div class="tout">.*?<div class="byline">.*?</div>.*?</div>'
  pattern_compile = re.compile(pattern, re.DOTALL|re.U)
  s = pattern_compile.findall(source)
  return s

def get_date(item) :
  pattern = '<span class="date">([^<]+)</span>'
  pattern_compile = re.compile(pattern, re.DOTALL|re.U)
  s = pattern_compile.search(item)
  return s.group(1)

def get_author(item) :
  pattern = '<span class="name">([^<]+)</span>'
  pattern_compile = re.compile(pattern, re.DOTALL|re.U)
  s = pattern_compile.search(item)
  return s.group(1) if s != None else None

def clean_author(author_from_item) :
  if author_from_item[:3] == 'By ' :
    return author_from_item[3:]
  return author_from_item


def get_title_article(item) :
  pattern = '<h3><a.*?>(.*?)</a></h3>'
  pattern_compile = re.compile(pattern, re.DOTALL|re.U)
  s = pattern_compile.search(item)
  return s.group(1) if s != None else None

def get_url_article(item) :
  pattern = '<h3><a href="([^"]+)".*?</h3>'
  pattern_compile = re.compile(pattern, re.DOTALL|re.U)
  s = pattern_compile.search(item)
  return s.group(1) if s != None else None

def get_article_info(source) :
  title = get_article_title(source)
  head  = get_article_header(source)
  core  = get_article_core(source)
  return {
    'title' : title,
    'head'  : head,
    'core'  : core
  }

def get_article(url_article, proxy) :
  source_article = urllib.urlopen(url_article, proxies=proxy).read()
  info     = get_article_info(source_article)
  title    = info['title']
  head     = info['head']
  core     = info['core']
  next_url = get_next_page_article(source_article)
  if next_url != None :
    print '  multipage'
    next_url  = rebuild_url(url_article, next_url)
    core     += get_article_aux(next_url, proxy)
  info['core'] = core
  return info

def get_article_aux(url_article, proxy) :
  core = ''
  while True :
    source_article = urllib.urlopen(url_article, proxies=proxy).read()
    info = get_article_info(source_article)
    print url_article
    core += info['core']
    next_url = get_next_page_article(source_article)
    if next_url == None :
      break
    url_article = rebuild_url(url_article, next_url)
    r = random.uniform(0,2)
    time.sleep(r)
  return core

def get_article_header(source_article) :
  pattern = '<header class="entry-header">.*?(<h2 class="entry-deck">.*?</h2>).*?</header>'
#  pattern = '<header class="entry-header">.*?(<h1 class="entry-title">.*?</h1>).*?(<h2 class="entry-deck">.*?</h2>).*?</header>'
  pattern_compile = re.compile(pattern, re.DOTALL|re.U)
  s = pattern_compile.search(source_article)
#  title = s.group(1) if s != None else None
  head  = s.group(1) if s != None else None
  return head

def get_article_title(source_article) :
  pattern = '<header class="entry-header">.*?(<h1 class="entry-title">.*?</h1>).*?</header>'
  pattern_compile = re.compile(pattern, re.DOTALL|re.U)
  s = pattern_compile.search(source_article)
  title = s.group(1) if s != None else None
  return title

def get_article_core(source_article) :
  pattern = '</div>.*?</aside>(.*?)</div>.*?<footer'
#  pattern = '<!--/.post-rail-->(.*?)</div><!--/.entry-contents-->'
  pattern_compile = re.compile(pattern, re.DOTALL|re.U)
  s = pattern_compile.search(source_article)
  return s.group(1) if s != None else None

def rebuild_url(url_article, next_url) :
  if next_url[0] != '/' and next_url[0] != '.' :
    return next_url
  a = urlparse(url_article)
  root_url = a.scheme + '://' + a.netloc
  new_url = root_url + next_url
  return new_url

def get_next_page_article(source_article) :
  pattern = '<ol class="wp-paginate">.*?<a href="([^"]+)" class="next">.*?</ol>'
  pattern_compile = re.compile(pattern, re.DOTALL|re.U)
  s = pattern_compile.search(source_article)
  res = s.group(1) if s != None else None
  return res
