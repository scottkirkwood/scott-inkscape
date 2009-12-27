#!/usr/bin/python
#
# Copyright 2009 Scott Kirkwood All Rights Reserved.

"""Make the digits from 0-9

Uses my inkscape extension seven_segments.py
"""

__author__ = 'scott@forusers.com (Scott Kirkwood)'

import optparse
import subprocess

def DoOne(number, template, prefix):
  args = ['seven_segment.py', '--number', str(number), template]
  print args
  new_svg = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0]

  fout = open(prefix + str(number) + '.svg', 'w')
  fout.write(new_svg)
  fout.close()

def Combine(number, template, prefix):
  args = ['gm', 'montage', '-mode', 'concatenate', '-tile', '10x1']
  args += ['combine.png']
  print args
  subprocess.Call(args)

def Main():
  parser = optparse.OptionParser()
  parser.add_option('-t', '--template', dest='template', default='seven-segment.svg',
                    help='The svg template to use')
  parser.add_option('--prefix', dest='prefix', default='seven-segment/seven-seg-',
                    help='The file prefix to use for all output files.')
  parser.add_option('--buildall', dest='buildall', action='store_true',
                    help='Build all styles')
  options, args = parser.parse_args()

  for number in range(10):
    DoOne(number, options.template, options.prefix)


if __name__ == '__main__':
  Main()
