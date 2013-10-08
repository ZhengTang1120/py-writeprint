import os
import json
import sys
import glob

sys.path.append('../tools/')
sys.path.append('../')
import tool_bs as tbs
from bs4 import BeautifulSoup

import argparse

import math

#ecart type
def standart_deviation(rep) :
  n = len(rep)
  if n == 0 :
    return 0
  moy = avg(rep)
  v = 0.
  for i in xrange(n) :
    v += math.pow(rep[i]-moy,2)
  v /= n
  return math.sqrt(math.fabs(v))

#esperance
def expected_value(rep) :
  n = len(rep)
  s = sum(rep)
  e = 0.
  for i in xrange(n) :
    e += i * (float(rep[i]) / s)
  return e

#moyenne
def avg(rep) :
  return float(sum(rep))/len(rep)

parser = argparse.ArgumentParser(description='build features according a corpus linked to an author')

parser.add_argument("-j", "--jsoninput", type=str, default='out.json',
                    help="read the analysis in JSONINPUT")

args = parser.parse_args()

f = open(args.jsoninput, 'r')
j = json.load(f)
f.close()

for k,v in j['global'].iteritems() :
  print k,v

print 'avg. #block per message :: %s'%(float(j['global']['nbBlocks']) / j['global']['nbMessages'])
print 'avg. #car per message :: %s'%(float(j['global']['nbCars']) / j['global']['nbMessages'])
print '*'*40

lb = []
lc = []
lm = []

for a,i in j['authors'].iteritems() :
  lb.append(i['nbBlocks'])
  lc.append(i['nbCars'])
  lm.append(i['nbMessages'])

print 'avg. #blocks per author ::', avg(lb), '+/-', standart_deviation(lb)
print 'avg. #cars per author ::', avg(lc), '+/-', standart_deviation(lc)
print 'avg. #messages per author ::', avg(lm), '+/-', standart_deviation(lm)
