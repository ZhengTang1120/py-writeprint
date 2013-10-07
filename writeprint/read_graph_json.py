#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json

import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description='plot a figure according xp results')
parser.add_argument('-i', '--input', type=str,
                    help='draw plot from the file INPUT')
parser.add_argument('-o', '--output', type=str, default='out_xp.png',
                    help='write plot in OUTPUT')

args = parser.parse_args()


f = open(args.input,'r')
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
plt.savefig(args.output)

