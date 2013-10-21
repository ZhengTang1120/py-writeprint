# -*- coding: utf-8 -*-

import re

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
  if(suffix[0:3] == 'http') :
    return suffix
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

  re_head = '<h2 itemprop="description"[^>]*?>.*?</h2>'
  re_head_compile = re.compile(re_head, re.U|re.DOTALL)
  head = re_head_compile.search(main_article)
  res['head'] = head.group(0) if head != None else ''

  re_core = '</aside>(<div[^>]*?.*?</(div|p)>)<span class="author"[^>]*?>'
  re_core_compile = re.compile(re_core, re.U|re.DOTALL)
  core = re_core_compile.search(main_article)
  res['core'] = core.group(1) if core != None else ''
  return res


