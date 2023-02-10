#!/usr/bin/python
# File created by adm on host labo32 (id="007f0101")
# Sun  5 Feb 17:53:02 CET 2023

import argparse
import csv
import matplotlib.pyplot as plt
import math
import re


def import_text(filename, separator):
    for line in csv.reader(open(filename), delimiter=separator, 
                           skipinitialspace=True):
        if line:
            yield line

parser = argparse.ArgumentParser(description='mesure grapher')


parser.add_argument('filename', type=str, help='Name of file to graph')
parser.add_argument('-x', dest='x', type=int, help='X column index')
parser.add_argument('-y', dest='y', type=int, help='Y column index')
parser.add_argument('-db', dest='gain',  action='store_true')
parser.add_argument('-s', dest='sec', type=int, help='Secondary Y column index')
parser.add_argument('-xlog', dest='xlogscale',  action='store_true')
parser.add_argument('-v', '--verbose', dest='verbose', action='store_true')  # on/off flag

args = parser.parse_args()

# default values

if (args.x is None):
	args.x=0
	print ("Default x=0")

if (args.y is None):
	args.y=1
	print ("Default y=1")

if (args.xlogscale is None):
	args.xlogscale=0
	
	
xValues=[]
yValues=[]
sValues=[]
gValues=[]

for data in import_text(args.filename, ','):
	if (args.verbose):
		print (data[args.x]+","+data[args.y])
	xValues.append(float(data[args.x]))
	yValues.append(float(data[args.y]))
	if (args.sec):
		sValues.append(float(data[args.sec]))
		if (args.gain):
			if ((float(data[args.y])>0) and (float(data[args.sec])>0)):
				print (float(data[args.y]))
				print (float(data[args.sec]))
				gValues.append(math.log10(float(data[args.y])/float(data[args.sec])))
			else:
				xValues.pop()

title=re.sub('\.csv$', '', args.filename)
plt.figure(num=title)

if (args.gain):
	plt.plot(xValues,gValues)
else:
	plt.plot(xValues,yValues)
	if (args.sec):
		plt.plot(xValues,sValues)

if (args.xlogscale):
	plt.xscale('log',base=10) 

plt.grid(linestyle='--')

plt.show()




