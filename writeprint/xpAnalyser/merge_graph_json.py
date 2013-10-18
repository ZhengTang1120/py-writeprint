#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
import os
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description='plot a figure according xp results')
parser.add_argument('-o', '--output', type=str, default='out_xp.png',
                    help='write plot in OUTPUT')
parser.add_argument('-s', '--styleplot', type=str, default='',
                    help='write plot in OUTPUT using style defined in STYLEPLOT')

parser.add_argument('--logscale', default=False, action='store_true',
                    help='use log scale to display the graph')

parser.add_argument('list_path', metavar='L', type=str, nargs='+',
                    help='List of path L of files containing results, a file per curve')

args = parser.parse_args()

plt.rc('text', usetex=True)
plt.rc('font', family='serif')

##
# args.styleplot
##

jstyle = {}
if os.path.isfile(args.styleplot) :
  f = open(args.styleplot, 'read')
  jstyle = json.load(f)
  f.close()
  plt.xlabel(jstyle['legend_x'])
  plt.ylabel(jstyle['legend_y'])

name_legend = []
for path in args.list_path :
  f = open(path,'r')
  j = json.load(f)
  f.close()
  if 'data1' in jstyle :
    style = jstyle['data1'][path]['line_style']
    name_legend.append(jstyle['data1'][path]['legend'])
  else :
    name_legend.append('default')
    style = '-'
  for dataName, data in j.iteritems() :
    x = data['x']
    y = data['y']
    plt.plot(x, y, style)

#plt.legend(list(name_legend), 'upper right', shadow = False)

##
# args.logscale
##

if(args.logscale) :
  plt.yscale('log')
  plt.xscale('log')

plt.savefig(args.output)

