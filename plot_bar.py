#!/usr/bin/env python
__author__ = "Jose M. Beltran <gemtoolbox@gmail.com>"
__version__ = "0.1.0"


import sys
import PyQt4.Qt as Qt
import PyQt4.Qwt5 as Qwt
from gem_color import *


class BarCurve(Qwt.QwtPlotCurve):
    def __init__(self, barAttributes=[Qt.Qt.black, 1, Qt.Qt.white]): #attributes [lineColor, width, fillColor]
        super(BarCurve, self).__init__()
        self.barAttributes = barAttributes
      
    def drawFromTo(self, painter, xMap, yMap, start, stop):
        """Draws rectangles with the corners taken from the x- and y-arrays.
        """
        painter.setPen(Qt.QPen(self.barAttributes[0], self.barAttributes[1]))
        painter.setBrush(self.barAttributes[2])
            
        if stop == -1:
            stop = self.dataSize()
        # force 'start' and 'stop' to be even and positive
        if start & 1:
            start -= 1
        if stop & 1:
            stop -= 1
        start = max(start, 0)
        stop = max(stop, 0)
        for i in range(start, stop, 2):
            px1 = xMap.transform(self.x(i))
            py1 = yMap.transform(self.y(i))
            px2 = xMap.transform(self.x(i+1))
            py2 = yMap.transform(self.y(i+1))
            painter.drawRect(px1, py1, (px2 - px1), (py2 - py1))

class BarPlot(Qwt.QwtPlot):
    def __init__(self, parent = None, attributes=[Qt.Qt.black, 1, Qt.Qt.white], *args):
        super(BarPlot, self).__init__(parent, *args)
        self.curves = {}
        self.attributes = attributes
            
        # set plot default layout
        self.plotLayout().setMargin(0)
        self.plotLayout().setCanvasMargin(0)
        self.plotLayout().setAlignCanvasToScales(True)
        
        # set X Axis
        bottomAxis = self.setAxisTitle(Qwt.QwtPlot.xBottom, 'Standard deviation')
        #self.setAxisScaleDraw(Qwt.QwtPlot.xBottom, TextScaleDraw(month))
        self.setAxisScale(Qwt.QwtPlot.xBottom, 0, 30)
        #self.setAxisMaxMajor(Qwt.QwtPlot.xBottom, 36) # set a maximum of 10 Major ticks
        #self.setAxisMaxMinor(Qwt.QwtPlot.xBottom, 0) # force zero minor ticks
        self.enableAxis(Qwt.QwtPlot.xBottom)
        # set Y Axis
        self.setAxisTitle(Qwt.QwtPlot.yLeft, 'Counts')
        self.setAxisScale(Qwt.QwtPlot.yLeft, 0, 100)
       

        grid = Qwt.QwtPlotGrid()
        pen = Qt.QPen(Qt.Qt.DotLine)
        pen.setColor(Qt.Qt.black)
        pen.setWidth(0)
        grid.setPen(pen)
        grid.attach(self)
        
    def go(self, nbars, x, y, Dx):
        """Create and plot a sequence of bars
        """
        n = int(nbars)
        

        for bar in self.itemList():
            if isinstance(bar, BarCurve):
                bar.detach()

        for i in range(n):
            bar = BarCurve(self.attributes)
            bar.attach(self)
            bar.setData([x[i]-Dx/2, Dx/2+x[i]], [0, y[i]])
