#!/usr/bin/env python
__author__ = "Jose M. Beltran <gemtoolbox@gmail.com>"
__version__ = "0.1.0"

import numpy as np
from PyQt4 import QtCore, QtGui, Qt
import PyQt4.Qwt5 as Qwt

class Freq_Curve(Qwt.QwtPlotCurve):
    def __init__(self, *args):
        super(Freq_Curve, self).__init__(*args)
        self.setRenderHint(Qwt.QwtPlotItem.RenderAntialiased)
    
    def setAttributes(self, color, weight, isFilled=False):
        c = Qt.QColor(color)
        if isFilled:
            self.setPen(Qt.QPen(c, weight))
            self.setBrush(c)
        else:
            self.setPen(Qt.QPen(c, weight))

class Freq_Plot(Qwt.QwtPlot):
    def __init__(self, parent = None, *args):
        super(Freq_Plot, self).__init__(parent, *args)
        self.curves = {}
        self.data ={}
          
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setMinimumSize(QtCore.QSize(350, 0))
        #
        #self.setCanvasBackground(GemColor(217, 217, 217, 255))
        # set plot default layout
        self.plotLayout().setMargin(0)
        self.plotLayout().setCanvasMargin(0)
        self.plotLayout().setAlignCanvasToScales(True)
        # set Legend
        '''
        legend = Qwt.QwtLegend()
        legend.setItemMode(Qwt.QwtLegend.CheckableItem)
        self.insertLegend(legend, Qwt.QwtPlot.RightLegend)
        '''
        # set X Axis
        bottomAxis = self.setAxisTitle(Qwt.QwtPlot.xBottom, 'Standard deviation')
        #self.setAxisScale(Qwt.QwtPlot.xBottom, 0, 80)
        #self.setAxisMaxMajor(Qwt.QwtPlot.xBottom, 36) # set a maximum of 10 Major ticks
        #self.setAxisMaxMinor(Qwt.QwtPlot.xBottom, 0) # force zero minor ticks
        self.enableAxis(Qwt.QwtPlot.xBottom)
        # set Y Axis
        self.setAxisTitle(Qwt.QwtPlot.yLeft, 'Count')
        #self.setAxisScale(Qwt.QwtPlot.yLeft, 0, 45)
        # set Grid
        grid = Qwt.QwtPlotGrid()
        grid.attach(self)
        grid.setPen(Qt.QPen(Qt.Qt.black, 0, Qt.Qt.DotLine))   
        #
        self.replot()

   
        
    def showCurve(self, item, on):
        item.setVisible(on)
        self.replot()
 
