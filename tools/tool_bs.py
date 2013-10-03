import sys
sys.path.append('../')

from bs4 import BeautifulSoup, Tag, NavigableString, Comment, Doctype, CData, Declaration, ProcessingInstruction
import tool_extracteur as te

list_bloc = ['p', 'div', 'h1', 'h2', 'h3', 'h4', 'hr', 'td', 'iframe', 'banner', 'ul']
list_inline = ['a', 'br', 'span']

def contain_visible_text(bs_elt) :
  if is_text(bs_elt) :
    return len(te.clean_spaces(bs_elt.string))
  elif is_cdata(bs_elt) :
    return 0
  elif is_declaration(bs_elt) :
    return 0
  elif is_processing_instruction(bs_elt) :
    return 0
  l = 0
  for e in bs_elt.descendants :
    if e.string == None :
      continue
    su  = te.clean_spaces(e.string)
    if len(su) == 0 :
      continue
    l += len(su)
  return l

def contain_direct_text(bs_elt) :
  if is_text(bs_elt) :
    return is_visible_text(bs_elt)
  else :
    for e in bs_elt :
      if is_visible_text(e) :
        return True
    return False

def is_visible_text(bs_elt) :
  if is_text(bs_elt) :
    s = te.clean_spaces(bs_elt.string)
    if len(s) == 0 :
      return False
    return True
  return False

def is_text(bs_elt) :
  return type(bs_elt) == NavigableString

def is_processing_instruction(bs_elt) :
  return type(bs_elt) == ProcessingInstruction

def is_declaration(bs_elt) :
  return type(bs_elt) == Declaration

def is_cdata(bs_elt) :
  return type(bs_elt) == CData

def is_bloc(bs_elt, list_bloc) :
  if type(bs_elt) != Tag :
    return False
  return bs_elt.name in list_bloc

def is_comment(bs_elt) :
  return type(bs_elt) == Comment

def is_tag(bs_elt) :
  return type(bs_elt) == 'tag'

#def is_script(bs_elt) :
#  return type(bs_elt) == Script

def is_doctype(bs_elt) :
  return type(bs_elt) == Doctype

def get_tag_info(bs_elt) :
  info = {'name' : bs_elt.name}
  for k,v in bs_elt.attrs.iteritems() :
    info[k] = v
  return info

def get_bloc_text(bs_elt) :
  l = []
  get_bloc_text_aux(bs_elt,l)
  return '\n'.join(l)

def get_bloc_text_aux(bs_elt,l) :
  for i,elt in enumerate(bs_elt) :
    if type(elt) == Tag :
      if elt.name == 'script' or elt.name == 'comment' or elt.name == 'style':
        continue
      get_bloc_text_aux(elt, l)
    elif is_visible_text(elt) :
      l.append(te.clean_text(elt.string))

##
# parse html with position in the tree
##

def parse_bs(bs_elt) :
  l = []
  parse_bs_aux(bs_elt, [0], l)
#  return l
  for bs_elt, path in l :
    if is_visible_text(bs_elt) :
      print "--"*len(path), 'str', path, len(bs_elt.string)
    else :
      print "--"*len(path), bs_elt.name, path
#  exit(2)

def parse_bs_aux(bs_elt, path, l) :
  l.append((bs_elt, path))
  for i,elt in enumerate(bs_elt) :
    if type(elt) == Tag :
      if elt.name == 'script' or elt.name == 'style' :
        continue
      parse_bs_aux(elt, path+[i], l)
    elif is_visible_text(elt) :
      l.append((elt, path+[i]))

def path2bs_elt(bs_elt, path) :
  pass

##
# Bloc modification
##

def add_bloc(tree, res_cut_bloc) :
  for son in res_cut_bloc :
    if son[0] == 'str' :
      if len(te.clean_spaces(son[1])) > 0 :
        tree[1].append(son)
    elif son[0] == 'comment' :
      continue
    elif son[0]['name'] == 'script' :
      continue
    else :
      tree[1].append(son)
  return tree

def cut_bloc(bs_elt) :
  if is_text(bs_elt)  :
    return [['str',bs_elt]]
  if is_comment(bs_elt) :
    return [['comment', str(bs_elt)]]

  res = []
  info = get_tag_info(bs_elt)
  head = [info, []]
  for e in bs_elt.children :
    if is_bloc(e, list_bloc) :
      if len(head[1]) > 0 :
        res.append(head)
      for tree in cut_bloc(e) :
        res.append([info,[tree]])
      head = [info,[]]
    else :
      head = add_bloc(head, cut_bloc(e))
  if len(head[1]) > 0 :
    res.append(head)
  return res

def cut_bloc2bs_elt(cut_bloc_res) :
  bs = BeautifulSoup('')
  if cut_bloc_res[0] == 'str' :
    return bs.new_string(cut_bloc_res[1])
  name = cut_bloc_res[0]['name']
  new_bs_elt = bs.new_tag(name)
  new_bs_elt.attrs = {}
  for k,v in cut_bloc_res[0].iteritems() :
    if k == 'name' :
      continue
    new_bs_elt.attrs[k] = v
  for bloc in cut_bloc_res[1] :
    new_bs_elt.append(cut_bloc2bs_elt(bloc))
  return new_bs_elt

def contains_bloc(bs_elt, list_bloc) :
  for e in bs_elt.descendants:
    if is_bloc(e, list_bloc) :
      return True
  return False

def contain_bloc(bs_elt, list_bloc) :
  cpt = 0
  for e in bs_elt.descendants:
    if is_bloc(e, list_bloc) :
      cpt += 1
  return cpt

def contain_direct_bloc(bs_elt, list_bloc) :
  cpt = 0
  for elt in bs_elt :
    if is_bloc(elt, list_bloc) :
      cpt += 1
  return cpt

def contain_direct_bloc_text(bs_elt, list_bloc) :
  cpt = 0
  for elt in bs_elt :
    if is_bloc(elt, list_bloc) and not contain_bloc(elt, list_bloc) :
      cpt += 1
  return cpt

#def is_informative_bloc(bs_elt, list_bloc) :
#  test1 = (contain_direct_text(bs_elt) and not contain_direct_bloc(bs_elt, list_bloc))
#  test2 = (not contain_direct_text(bs_elt) and contain_direct_bloc(bs_elt, list_bloc))
#  return test1 or test2

def is_tower_singleton_bloc(bs_elt, list_bloc) :
  if is_text(bs_elt) :
    return 1
  cpt = 0
  for elt in bs_elt :
    if is_text(elt) or is_comment(elt) :
      continue
    if is_bloc(elt, list_bloc) :
      last_elt = elt
      cpt += 1
  if cpt == 0 :
    return 1
  elif cpt == 1 :
    t = is_tower_singleton_bloc(last_elt, list_bloc)
    if t == 0 :
      return 0
    else :
      return 1 + t
  else :
    return 0

def contain_consecutive_direct_bloc_text(bs_elt, list_bloc) :
  flag = False
  max_count = 0
  current_count = 0
  for elt in bs_elt :
    if is_text(elt) and not is_visible_text(elt) :
      continue
    if is_bloc(elt, list_bloc) and not contain_direct_bloc(elt, list_bloc) and contain_direct_text(elt) :
      if not flag :
        flag = True
      current_count += 1
    elif flag :
      max_count = max(current_count, max_count)
      current_count = 0
      flag = False
  max_count = max(current_count, max_count)
  return max_count

##
# Styles
##

def get_bloc_global_style(bs_elt) :
  info = get_tag_info(bs_elt)
  tag_name = info['name']
  tag_class = None
  tag_id = None
  if info.has_key('class') :
    tag_class = '_'.join(info['class'])
  if info.has_key('id') :
    tag_id = info['id']
  return (tag_name, tag_class, tag_id)

def get_bloc_start(bs_elt) :
  return get_bloc_extremum(bs_elt, 'start')

def get_bloc_end(bs_elt) :
  return get_bloc_extremum(bs_elt, 'end')

def get_bloc_extremum(bs_elt,locality='start') :
  if locality == 'start' :
    l = bs_elt
  elif locality == 'end' :
    l = list(bs_elt)[::-1]
  else :
    l = []
  for elt in l :
    if is_comment(elt) :
      continue
    elif is_text(elt) :
      if is_visible_text(elt) :
        return elt
      else :
        continue
    else :
      if contain_visible_text(elt) == 0 :
        continue
      return elt

def get_bloc_style_extremum_aux(bs_elt, list_style, get_extremum) :
  e = get_extremum(bs_elt)
  if is_visible_text(e) :
    return list_style
  else :
    list_style.append(get_bloc_global_style(e))
    return get_bloc_style_extremum_aux(e, list_style, get_extremum)

def get_bloc_style_extremum(bs_elt, get_extremum) :
  list_style = [get_bloc_global_style(bs_elt)]
  return get_bloc_style_extremum_aux(bs_elt, list_style, get_extremum)

def get_bloc_style(bs_elt) :
  s = set(get_bloc_style_extremum(bs_elt, get_bloc_start))
  e = set(get_bloc_style_extremum(bs_elt, get_bloc_end))
  return s.intersection(e)


