#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tools_karkkainen_sanders import list2list_symbol, kark_sort, direct_kark_sort
from array import array

class Stack:
  def __init__(self) :
    self._top = 0
    self.lst_max = []

class Rstr_max :

  char_frontier = chr(2)

  def __init__(self) :
    self.array_str = []
    self.array_list_word = []

  def add_str(self, s) :
    self.array_str.append(s)

  def get_repeat(self, id_str, offset, length) :
    return self.array_str[id_str][offset:offset+length]

  def step0_init(self) :
    list_merge = []
    len_list_word = len(self.array_str)
    for i in xrange(len_list_word) :
      list_merge.extend(self.array_str[i])
      if i != len_list_word - 1 :
        list_merge.append(self.char_frontier) 

    self.global_suffix,self.len_alphabet = list2list_symbol(list_merge)

  def step0_init_str(self) :  
    self.global_suffix = self.char_frontier.join(self.array_str)

  def step1_sort_suffix(self) :
    n = len(self.global_suffix)
    init = [-1]*n
    self.idxString = array('i', init)
    self.idxPos = array('i', init)
    self.endAt = array('i', init)
    
    k = idx = 0
    for w in self.array_str :
      len_w = len(w)
      last = k + len_w
      for p in xrange(len_w) :
        self.idxString[k] = idx
        self.idxPos[k] = p
        self.endAt[k] = last
        k += 1
      idx += 1
      k += 1

    res = array('i',[0]*(n+3))
    kark_sort(array('i',self.global_suffix+[0,0,0]), res, n, self.len_alphabet)
    self.res = res[:n]
#    self.res = direct_kark_sort(self.global_suffix)

  def step2_lcp(self) :
    n = len(self.res)
    init = [0]*n
    rank = array('i', init)
    LCP = array('i', init)
    
    s = self.global_suffix
    suffix_array = self.res
    endAt = self.endAt

    for i in xrange(len(self.array_str),n):
      v = self.res[i]
      rank[v] = i

    l = 0
    for j in xrange(n):
      if(l > 0) :
        l -= 1
      i = rank[j]
      j2 = suffix_array[i-1]
      if i:
        while l + j < endAt[j] and l + j2 < endAt[j2] and s[j+l] == s[j2+l]:
          l += 1
        LCP[i-1] = l 
      else:
        l = 0
    self.lcp = LCP

  def step3_rstr(self) :
    prev_len = 0
    idx = 0
    results = {}
    len_lcp = len(self.lcp) - 1

    stack = Stack()

    if len(self.res) == 0 :
      return {}

    pos1 = self.res[0]
    #offset1 = self.idxPos[self.res[0]]
    #idStr1 = self.idxString[self.res[0]]
    for idx in xrange(len_lcp):
      current_len = self.lcp[idx]
      pos2 = self.res[idx+1]
      #offset2 = self.idxPos[pos2]
      #idStr2 = self.idxString[pos2]
      #offset2, idStr2  = self.array_suffix[idx+1]
      end_ = max(pos1, pos2) + current_len# max(pos1, pos2) + current_len 
#      e = max((idStr1, offset1), (idStr2, offset2))
#      end_ = (e[0],e[1]+current_len)
      n = prev_len - current_len
      if n < 0 :
        #pushMany
        stack.lst_max.append([-n, idx, end_])
        stack._top += -n
      elif n > 0:
        self.removeMany(stack, results, n, idx)
      elif stack._top > 0 and end_ > stack.lst_max[-1][-1] :
        #setMax
        stack.lst_max[-1][-1] = end_

      prev_len = current_len
      pos1 = pos2
      #offset1 = offset2
      #idStr1 = idStr2
      
    if(stack._top > 0) :
      self.removeMany(stack, results, stack._top, idx+1)

    return results

  def removeMany(self, stack, results, m, idxEnd):
      prevStart = -1
      while m > 0:
        n, idxStart, maxEnd = stack.lst_max.pop()
        if prevStart != idxStart:
          #idStr = self.idxString[maxEnd-1]
          #pos = self.idxPos[maxEnd-1]
          id_ = (maxEnd, idxEnd-idxStart+1)
          if id_ not in results or results[id_][0] < stack._top:
              results[id_] = (stack._top,idxStart)
          prevStart = idxStart
        m -= n
        stack._top -= n
      if m < 0:
        stack.lst_max.append([-m, idxStart, maxEnd-n-m])
        stack._top -= m    

  def go_word(self) :
    self.step0_init_word()
    return self.go_rstr()

  def go(self) :
    self.step0_init()
    self.step1_sort_suffix()
    self.step2_lcp()
    r = self.step3_rstr()
    return r
    
  def go_rstr(self) :
    self.step1_sort_suffix()
    self.step2_lcp()
    r = self.step3_rstr()
    return r

if (__name__ == '__main__') :
  str1 = 'toto'
  str1_unicode = unicode(str1,'utf-8','replace')
  rstr = Rstr_max()
  rstr.add_str(str1_unicode)
  rstr.add_str(str1_unicode)
  r = rstr.go()
  for (offset_end, nb), (l, start_plage) in r.iteritems():
    ss = rstr.global_suffix[offset_end-l:offset_end]
    id_chaine = rstr.idxString[offset_end-1]
    repeat = rstr.get_repeat(id_chaine, rstr.idxPos[offset_end-l], l)
    print repeat, nb
