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

#print j.keys()
#exit(0)

#import numpy as np

selected = j['selected']

list_fitness = ['min_fitness', 'max_fitness']
list_len = ['max_fitness_len_min', 'min_fitness_len_min', 'min_fitness_len_max', 'max_fitness_len_max']

fig, ax1 = plt.subplots()

t = selected['x']
max_fitness = selected['max_fitness']
#min_fitness = selected['min_fitness']

#t = np.arange(0.01, 10.0, 0.01)
#s1 = np.exp(t)

#ax1.plot(t, min_fitness, 'b.')
ax1.plot(t, max_fitness, 'b-')
ax1.set_xlabel('generation')
# Make the y-axis label and tick labels match the line color.
ax1.set_ylabel('fitness', color='b')
for tl in ax1.get_yticklabels():
  tl.set_color('b')


ax2 = ax1.twinx()
len_min = selected['max_fitness_len_min']
len_max = selected['max_fitness_len_max']
ax2.plot(t, len_min, 'r-')
ax2.plot(t, len_max, 'r.')
ax2.set_ylabel('len', color='r')
for tl in ax2.get_yticklabels():
  tl.set_color('r')

plt.savefig(args.output)

#for dataName, data in j.iteritems() :
#  x = data['x']
#  y = data['y']
#  plt.plot(x, y, 'r-')

#name_legend = []
#for k,info in js_plot.iteritems() :
#  name_legend.append(info['name_legend'])
#  plt.plot(info['list_x'], info['list_y'], info['style_plot'])

#plt.xlabel(info['xlabel'])
#plt.ylabel(info['ylabel'])
#plt.legend(list(name_legend), 'upper left', shadow = True)
#plt.savefig(args.output)

