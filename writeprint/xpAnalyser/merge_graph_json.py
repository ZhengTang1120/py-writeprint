#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json

import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description='plot a figure according xp results')
parser.add_argument('-o', '--output', type=str, default='out_xp.png',
                    help='write plot in OUTPUT')
parser.add_argument('list_path', metavar='L', type=str, nargs='+',
                    help='List of path L of files containing results, a file per curve')

args = parser.parse_args()

for path in args.list_path :
  f = open(path,'r')
  j = json.load(f)
  f.close()

  for dataName, data in j.iteritems() :
    x = data['x']
    y = data['y']
    plt.plot(x, y, 'r-')

#name_legend = []
#for k,info in js_plot.iteritems() :
#  name_legend.append(info['name_legend'])
#  plt.plot(info['list_x'], info['list_y'], info['style_plot'])

#plt.xlabel(info['xlabel'])
#plt.ylabel(info['ylabel'])
#plt.legend(list(name_legend), 'upper left', shadow = True)
#plt.yscale('log')
#plt.xscale('log')
plt.savefig(args.output)

