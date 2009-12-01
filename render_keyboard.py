#!/usr/bin/env python

# These two lines are only needed if you don't put the script directly into
# the installation directory
import sys
sys.path.append('/usr/share/inkscape/extensions')

from simplestyle import *
import inkex
import os
import simplepath
import sys

def loadPath(svg_path):
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
  tree = inkex.etree.parse( extensionDir + "/" + svg_path )
  root = tree.getroot()
  pathElement = root.find('{http://www.w3.org/2000/svg}path')
  if pathElement == None:
    return None, 0, 0
  d = pathElement.get("g")
  width = float(root.get("width"))
  height = float(root.get("height"))
  return d, width, height


class HelloWorldEffect(inkex.Effect):
  """
  Example Inkscape effect extension.
  Creates a new layer with a "Hello World!" text centered in the middle of the document.
  """
  def __init__(self):
    """
    Constructor.
    Defines the "--what" option of a script.
    """
    # Call the base class constructor.
    inkex.Effect.__init__(self)

    # Define string option "--what" with "-w" shortcut and default value "World".
    self.OptionParser.add_option('-w', '--what', action = 'store',
      type = 'string', dest = 'what', default = 'World',
      help = 'What would you like to greet?')

  def effect(self):
    """
    Effect behaviour.
    Overrides base class' method and inserts "Hello World" text into SVG document.
    """
    # Get script's "--what" option value.
    what = self.options.what

    # Get access to main SVG document element and get its dimensions.
    svg = self.document.getroot()
    # or alternatively
    # svg = self.document.xpath('//svg:svg',namespaces=inkex.NSS)[0]

    width  = inkex.unittouu(svg.get('width'))
    height = inkex.unittouu(svg.get('height'))

    # Create a new layer.
    layer = inkex.etree.SubElement(svg, 'g')
    layer.set(inkex.addNS('label', 'inkscape'), 'Button layer')
    layer.set(inkex.addNS('groupmode', 'inkscape'), 'layer')

    # Create text element
    text = inkex.etree.Element(inkex.addNS('text', 'svg'))
    text.text = 'Hello %s!' % (what)

    # Set text position to center of document.
    text.set('x', str(width / 2))
    text.set('y', str(height / 2))

    # Center text horizontally with CSS style.
    style = {'text-align' : 'center', 'text-anchor': 'middle'}
    text.set('style', formatStyle(style))

    # Connect elements together.
    layer.append(text)

# Create effect instance and apply it.
effect = HelloWorldEffect()
effect.affect()
