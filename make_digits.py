#!/usr/bin/python
#
# Copyright 2009 Scott Kirkwood All Rights Reserved.

"""Make the digits from 0-9

Uses my inkscape extension seven_segments.py
"""

__author__ = 'scott@forusers.com (Scott Kirkwood)'

import optparse
import subprocess
import os

def DoOne(number, template, prefix):
  args = ['seven_segment.py', '--number', str(number), template]
  print ' '.join(args)
  new_svg = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0]

  outfname = prefix + str(number) + '.svg'
  fout = open(outfname, 'w')
  fout.write(new_svg)
  print 'Created %s' % outfname
  fout.close()

def ExportAllPng(subdir):
  ls = os.listdir(subdir)
  for fname in ls:
    if not fname.endswith('.svg'):
      continue
    filename = os.path.join(subdir, fname)
    pngname = filename.replace('.svg', '.png')
    args = ['inkscape', '-f', filename, '--export-png', pngname]
    print ' '.join(args)
    subprocess.call(args)

def Combine(subdir):
  args = ['gm', 'montage', '-mode', 'concatenate', '-tile', '20x1']
  ls = os.listdir(subdir)
  ls.sort()
  for fname in ls:
    fullname = os.path.join(subdir, fname)
    if fname == 'combine.png':
      os.unlink(fullname)
      continue
    if not fname.endswith('.png'):
      continue
    args.append(fullname)
    args.append('spacer.png')
  args += [os.path.join(subdir, 'combine.png')]
  print ' '.join(args)
  subprocess.call(args)

def BuildAll(subdir):
  ls = os.listdir(subdir)
  for filename in ls:
    fname = os.path.join(subdir, filename)
    if not os.path.isdir(fname) and fname.endswith('svg'):
      basename = os.path.splitext(filename)[0]
      newdir = os.path.join(subdir, basename)
      if not os.path.exists(newdir):
        os.mkdir(newdir)
      prefix = os.path.join(newdir, basename + '-')
      for num in range(10):
        DoOne(num, fname, prefix)
      ExportAllPng(newdir)
      Combine(newdir)

def Main():
  parser = optparse.OptionParser()
  parser.add_option('-t', '--template', dest='template', default='seven-segment.svg',
                    help='The svg template to use')
  parser.add_option('--prefix', dest='prefix', default='seven-segment/seven-seg-',
                    help='The file prefix to use for all output files.')
  parser.add_option('--buildall', dest='buildall', action='store_true',
                    help='Build all styles')
  options, args = parser.parse_args()

  if options.buildall:
    BuildAll('seven-segment')
  else:
    for number in range(10):
      DoOne(number, options.template, options.prefix)


if __name__ == '__main__':
  Main()
