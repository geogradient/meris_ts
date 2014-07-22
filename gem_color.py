#!/usr/bin/env python
__author__ = "Jose M. Beltran <gemtoolbox@gmail.com>"
__version__ = "0.1.0.0"

from PyQt4 import QtGui

class GemColor(QtGui.QColor):
    '''Provides custom colors with RGB and alpha values'''
    def __init__(self, r, g, b, a = 255):
        super(GemColor, self).__init__()
        self.setRed(r)
        self.setGreen(g)
        self.setBlue(b)
        self.setAlpha(a)
