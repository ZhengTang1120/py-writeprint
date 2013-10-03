#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import htmlentitydefs 
import string

def get_html_encoding(source_html) :
  p = re.compile(u'charset=([^"]+)', re.I)
  match = re.search(p, source_html)
  if match :  
    return match.group(1).lower().strip()
  else :
    return u'iso-8859-1'

def clean_html(source_html) :
  source_html = re.sub(u'[ \t\n\r]+', u' ', source_html)
  source_html = re.sub(u'&nbsp;', ' ', source_html)

  list_clean1 = [u'<script.+?</script>',u'<!\-\-.+?\-\->',
                 u'<select.+?</select>',u'<style.+?</style>',
                 u'<input.+?</input>',u'<form.+?</form>',
                 u'<iframe.+?</iframe>']

  list_clean2 = [u'[ \t\n\r]+',u'&nbsp;',u'(?:&gt;|&lt;)']

  for e in list_clean1 : 
    p = re.compile(e, re.I|re.M)
    source_html = p.sub(u'',source_html)

  for e in list_clean2 : 
    source_html = re.sub(e,u' ', source_html)

  return source_html

def decode_entities(source_html) :
  source_html = re.sub(u'&#([0-9]+);', replace_num_entity, source_html)
  pattcomp = re.compile(u'&([a-z]+);', re.I)
  source_html = pattcomp.sub(replace_alpha_entity, source_html)
  return source_html

def replace_num_entity(m) :
  if int(m.group(1)) in range(65535) :
    return unichr(int(m.group(1)))
  else :
    return u'&#%s;'%m.group(1)

def replace_alpha_entity(m) :
  cle = m.group(1)
  if not htmlentitydefs.entitydefs.has_key(cle) :
    if cle.isupper() :
      cle = string.lower(m.group(1))
      if not htmlentitydefs.entitydefs.has_key(cle) :
        return ''
    else :
      return ''
  if len(htmlentitydefs.entitydefs[cle]) == 1 :
    car = htmlentitydefs.entitydefs[cle]
    return unicode(car, 'iso-8859-1')
  else :
    str_code_point = htmlentitydefs.entitydefs[cle].strip(u'&#;')
    return unichr(int(str_code_point))

##########

def clean_script(s_unicode) :
  return re.sub(u'<script.+?</script>','',s_unicode, re.DOTALL|re.UNICODE)

def clean_spaces(s_unicode) :
  return re.sub(u'\s+',u'',s_unicode,re.DOTALL|re.UNICODE)

def clean_spaces_text(s_unicode) :
  return re.sub(u'\s+',u' ',s_unicode, re.DOTALL|re.UNICODE)

def clean_special_char(s_unicode) :
  dic_equiv = {"’" : "'"}
  for k,v in dic_equiv.iteritems() :
    s_unicode = re.sub(u'%s'%(unicode(k,'utf-8')),u'%s'%(v), s_unicode, re.DOTALL|re.UNICODE)
  return s_unicode 

def clean_text(s_unicode) :
  s_unicode = clean_spaces_text(s_unicode)
  s_unicode = clean_special_char(s_unicode)
  return s_unicode
