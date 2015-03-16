# Introduction #

The `seven_segment.py` and `make_digits.py` programs can create a set of 10 LED style 'font' using SVG.

# Details #

You pass in an 8 template (ex. `plain-black.svg`) and it creates the 10 digits from that template.


Here's a combined image for [plain-black.svg](http://scott-inkscape.googlecode.com/hg/seven-segment/plain-black.svg):

![http://scott-inkscape.googlecode.com/hg/seven-segment/plain-black/combine.png](http://scott-inkscape.googlecode.com/hg/seven-segment/plain-black/combine.png)

Here's a combined image for [italic-black.svg](http://scott-inkscape.googlecode.com/hg/seven-segment/italic-black.svg):

![http://scott-inkscape.googlecode.com/hg/seven-segment/italic-black/combine.png](http://scott-inkscape.googlecode.com/hg/seven-segment/italic-black/combine.png)

Here's a combined image for [glow-green.svg](http://scott-inkscape.googlecode.com/hg/seven-segment/plain-black.svg):

![http://scott-inkscape.googlecode.com/hg/seven-segment/glow-green/combine.png](http://scott-inkscape.googlecode.com/hg/seven-segment/glow-green/combine.png)

# Template #

In order to make the template you need to name your seven segments with an id:
```
    tc
tl      tr
    cc
bl      br
    bc
```

If you have more than one segment that needs to 'disappear' you can add a number to them (up to 3), ex. tc1, tc2, or tc3.

Segment must be a path, however.