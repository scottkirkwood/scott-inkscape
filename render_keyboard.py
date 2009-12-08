#!/usr/bin/env python

# These two lines are only needed if you don't put the script directly into
# the installation directory
import sys
sys.path.append('/usr/share/inkscape/extensions')

from simplestyle import *
import inkex
import os
import simplepath
import logging
import copy
import svg_regex

addNS = inkex.addNS

class Key:
  def __init__(self, fname):
    self.keyfile = fname
    self.key, self.key_defs, self.key_w, self.key_h = LoadPath(self.keyfile)

  def AddDefs(self, defs):
    MergeById(defs, self.key_defs, addNS('linearGradient', 'svg'))

def LoadPath(svg_path):
  """Load an svg file and return it.
  Args:
    svg_path: Svg filename
  Returns:
    first layers, width, height
  """
  extensionDir = os.path.normpath(
                     os.path.join( os.getcwd(), os.path.dirname(__file__) )
                 )
  # __file__ is better then sys.argv[0] because this file may be a module
  # for another one.
  fname = os.path.join(extensionDir, svg_path)
  logging.info('fname: %r' % fname)
  tree = inkex.etree.parse(fname)
  root = tree.getroot()
  g = root.find(addNS('g', 'svg'))
  is_layer = g.get(addNS('groupmode', 'inkscape'))
  if is_layer == 'layer':
    # If our object has a layer, remove it.
    g = g.find(addNS('g', 'svg'))
  if g == None:
    return None, None, 0, 0
  width  = inkex.unittouu(root.get('width'))
  height = inkex.unittouu(root.get('height'))
  defs = root.find(addNS('defs', 'svg'))
  return g, defs, width, height

def MergeById(cur_defs, to_merge_defs, tagname):
  """Merge defs into cur_defs, filtering on tagname.
  Uses the ids in to_merge_defs to check for uniqueness.
  Args:
    cur_defs: tree we need to iterator over and will add to.
    to_merge_defs: tree we want to add.
    tagname: tag name we will filter on
  """
  curIds = {}
  for cur_def in cur_defs.iterchildren(tagname):
    if cur_def.get('id'):
      curIds[cur_def.get('id')] = True

  for new_def in to_merge_defs.iterchildren(tagname):
    if new_def.get('id') not in curIds:
      cur_defs.append(new_def)

class XY:
  def __init__(self, x=0, y=0):
    self.x = x
    self.y = y

  def set(self, xy):
    self.x = xy.x
    self.y = xy.y
    return self

  def setx(self, xy):
    if isinstance(xy, XY):
      self.x = xy.x
    else:
      self.x = xy
    return self

  def sety(self, xy):
    if isinstance(xy, XY):
      self.y = xy.y
    else:
      self.y = xy
    return self

  def trans(self, xy):
    self.x += xy.x
    self.y += xy.y

  def trans(self, dx, dy):
    """Translate."""
    self.x += dx
    self.y += dy
    return self

  def transx(self, dx):
    """Translate in x direction."""
    if isinstance(dx, XY):
      self.x += dx.x
    else:
      self.x += dx
    return self

  def transy(self, dy):
    """Translate in y direction."""
    if isinstance(dy, XY):
      self.y += dy.y
    else:
      self.y += dy
    return self

class HelloWorldEffect(inkex.Effect):
  """
  Example Inkscape effect extension.
  Creates a new layer with a "Hello World!" text centered in the middle of the document.
  """
  def __init__(self):
    """
    Constructor.
    """
    # Call the base class constructor.
    inkex.Effect.__init__(self)

    # Define string option "--what" with "-w" shortcut and default value "World".
    self.OptionParser.add_option('-k', '--keyfile', action = 'store',
      type = 'string', dest = 'keyfile', default = 'key.svg',
      help = 'The template svg file')

  def effect(self):
    """
    Effect behaviour.
    Create multiple keys.
    """
    # Get access to main SVG document element and get its dimensions.
    svg = self.document.getroot()

    width  = inkex.unittouu(svg.get('width'))
    height = inkex.unittouu(svg.get('height'))

    cur_defs = svg.find(addNS('defs', 'svg'))
    self.key = Key('key.svg')
    self.key.AddDefs(cur_defs)

    # Create a new layer.
    self.layer = inkex.etree.SubElement(svg, 'g')
    self.layer.set(addNS('label', 'inkscape'), 'Button layer')
    self.layer.set(addNS('groupmode', 'inkscape'), 'layer')

    self.CreateKeyboard()

  def CreateKeyboard(self):
    xy = XY(10, 10)
    no_resize = XY(1, 1) 
    key_w, key_h = self.key.key_w, self.key.key_h
    homepadx = XY(xy.x + key_w * 15.2, 0)
    numpadx = XY(xy.x + key_w * 18.4, 0)

    keys = ['Esc', '.', 'F1', 'F2', 'F3', 'F4', '', 'F5', 'F6', 'F7', 'F8', '', 'F9', 'F10', 'F11', 'F12']
    curxy = XY()
    curxy.set(xy)
    for key_let in keys:
      if key_let == '.':
        curxy.transx(key_w)
        continue
      if not key_let:
        curxy.transx(key_w / 2)
        continue
      curxy = self.PositionKey(self.key, curxy, no_resize, key_let)

    curxy.setx(homepadx)
    for key_let in ['PrtScr', 'Scroll', 'Pause']:
      curxy = self.PositionKey(self.key, curxy, no_resize, key_let)

    curxy.setx(xy)
    curxy.transy(key_h * 1.2)
    keys = '`1234567890-='
    for key_let in keys:
      curxy = self.PositionKey(self.key, curxy, no_resize, key_let)

    curxy = self.PositionKey(self.key, curxy, XY(2.0, 1), 'Back')

    curxy.setx(homepadx)
    for key_let in ['Ins', 'Home', 'PgUp']:
      curxy = self.PositionKey(self.key, curxy, no_resize, key_let)

    curxy.setx(numpadx)
    for key_let in ['Num', '/', '*', '-']:
      curxy = self.PositionKey(self.key, curxy, no_resize, key_let)

    curxy.setx(xy)
    curxy.transy(key_h)
    tab_w = 1.5
    curxy = self.PositionKey(self.key, curxy, XY(tab_w, 1), 'Tab')
    
    keys = 'QWERTYUIOP[]'
    for key_let in keys:
      curxy = self.PositionKey(self.key, curxy, no_resize, key_let)
    curxy = self.PositionKey(self.key, curxy, XY(1.5, 1), '\\')

    curxy.setx(homepadx)
    for key_let in ['Del', 'End', 'PgDn']:
      curxy = self.PositionKey(self.key, curxy, no_resize, key_let)

    curxy.setx(numpadx)
    for key_let in ['7', '8', '9']:
      curxy = self.PositionKey(self.key, curxy, no_resize, key_let)
    
    curxy = self.PositionKey(self.key, curxy, XY(1, 2.06), '+')
    curxy.setx(xy)  # new line
    curxy.transy(key_h)

    curxy = self.PositionKey(self.key, curxy, XY(2.1, 1), 'Caps')

    keys = 'ASDFGHJKL;\''
    for i, key_let in enumerate(keys):
      curxy = self.PositionKey(self.key, curxy, no_resize, key_let)
    curxy = self.PositionKey(self.key, curxy, XY(1.99, 1), 'Enter')
    
    curxy.setx(numpadx)
    for key_let in ['4', '5', '6']:
      curxy = self.PositionKey(self.key, curxy, no_resize, key_let)

    curxy.setx(xy)  # new line
    curxy.transy(key_h)

    shift_w = 2.48
    curxy = self.PositionKey(self.key, curxy, XY(shift_w, 1), 'Shift')

    keys = 'ZXCVBNM,./'
    for i, key_let in enumerate(keys):
      curxy = self.PositionKey(self.key, curxy, no_resize, key_let)

    curxy = self.PositionKey(self.key, curxy, XY(2.65, 1), 'Shift')
    
    curxy.setx(homepadx)
    curxy.transx(key_w)
    for key_let in ['^']:
      curxy = self.PositionKey(self.key, curxy, no_resize, key_let)

    curxy.setx(numpadx)
    for key_let in ['1', '2', '3']:
      curxy = self.PositionKey(self.key, curxy, no_resize, key_let)
    
    curxy = self.PositionKey(self.key, curxy, XY(1, 2.06), 'E')
    curxy.setx(xy)
    curxy.transy(key_h)
    for key_let in ['Ctrl', 'Win', 'Alt']:
      wider = 1.4
      curxy = self.PositionKey(self.key, curxy, XY(wider, 1), key_let)

    space_w = 6
    curxy = self.PositionKey(self.key, curxy, XY(space_w, 1), '')

    for key_let in ['Alt', 'Win', 'Menu', 'Ctrl']:
      wider = 1.282
      curxy = self.PositionKey(self.key, curxy, XY(wider, 1), key_let)

    curxy.setx(homepadx)
    for key_let in ['<', 'd', '>']:
      curxy = self.PositionKey(self.key, curxy, no_resize, key_let)

    curxy.setx(numpadx)
    curxy = self.PositionKey(self.key, curxy, XY(2.05, 1), '0')
    curxy = self.PositionKey(self.key, curxy, no_resize, '.')


  def PositionKey(self, element, xy, dwh, letter):
    """Position, stretch and change the letter after duplicating.
    Args:
      element: the element to duplicate
      xy: Position to move to.
      dwh: How much to make wider or higher 1 means don't change.
      letter: New letter to use in tspan
    """
    cur_key = copy.deepcopy(element.key)
    tspan = cur_key.find('.//' + addNS('tspan', 'svg'))
    tspan.text = letter
    # Set text position to center of document.
    cur_key.set('transform', 'translate(%d,%d)' % (xy.x, xy.y))
    if dwh.x == 1 and dwh.y == 1:
      # No resizing required.
      self.layer.append(cur_key)
      return xy.transx(element.key_w)
    rect = cur_key.find(addNS('rect', 'svg'))
    old_w = inkex.unittouu(rect.get('width'))
    old_h = inkex.unittouu(rect.get('height'))
    w = old_w * dwh.x
    h = old_h * dwh.y
    dx = w - old_w
    dy = h - old_h

    rect.set('width', str(w))
    rect.set('height', str(h))
    for path in cur_key.iterchildren(addNS('text', 'svg')):
      TranslateXY(path, (dx / 2.0, 0))
      for tspan in path.iterchildren(addNS('tspan', 'svg')):
        TranslateXY(tspan, (dx / 2.0, 0))
    for path in cur_key.iterchildren(addNS('path', 'svg')):
      d = svg_regex.svg_parser.parse(path.get('d'))
      id = path.get('id')
      d2 = TranslatePath(d, (dx, dy), (10, 20))
      path.set('d', d2)
    self.layer.append(cur_key)
    return xy.transx(element.key_w + dx + 0.1 * dwh.x)

def TranslateXY(elem, (dx, dy)):
  """Translate an element by (x, y)."""
  if dx:
    x = inkex.unittouu(elem.get('x'))
    elem.set('x', str(x + dx))
  if dy:
    y = inkex.unittouu(elem.get('y'))
    elem.set('y', str(y + dy))

def TranslatePath(d, (dx, dy), (ifgtx, ifgty)):
  """convert [('M', [(1, 2),(3,4)])] to 'M 2,4 4,6' with (dx=1,dy=1).
  Args:
    d: path ex. [('T', [ (x, y), ]), ('Z', None)]
    dx, dy: delta for x and y direction.
    ifgtx, ifgty: use delta if x or y > this value.
  """
  ret = []
  for op, values in d:
    ret.append(op)
    if values:
      for x, y in values:
        if ifgtx and x > ifgtx:
          x += dx
        if ifgty and y > ifgty:
          y += dy
        ret.append('%f,%f' % (x, y))
  return ' '.join(ret)

# Create effect instance and apply it.
effect = HelloWorldEffect()
effect.affect()
