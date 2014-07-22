__author__ = "Jose M. Beltran <gemtoolbox@gmail.com>"
__version__ = "0.1.0"


import numpy as np
from PyQt4 import QtCore, QtGui, Qt
import PyQt4.Qwt5 as Qwt
from gem_color import *

class TextScaleDraw(Qwt.QwtScaleDraw):
    '''
    Class to implement the placement of text on axis scales (instead of just #'s)
    '''    
    def __init__(self, labelStrings, *args):
        """
        Initialize text scale draw with label strings and any other arguments that
        """
        Qwt.QwtScaleDraw.__init__(self, *args)
        self.labelStrings=labelStrings
        
        # __init__()
    
    def label(self, value):
        """
        Apply the label at location 'value' . Since this class is to be used for BarPlots
        or LinePlots, every item in 'value' should be an integer.
        """
        label=Qt.QString(self.labelStrings[int(value)])
        return Qwt.QwtText(label)

class NDVI_Curve(Qwt.QwtPlotCurve):

    def __init__(self, *args):
        super(NDVI_Curve, self).__init__(*args)
        self.setRenderHint(Qwt.QwtPlotItem.RenderAntialiased)
    
    def setAttributes(self, color, weight, isFilled=False):
        c = Qt.QColor(color)
        if isFilled:
            self.setPen(Qt.QPen(c, weight))
            self.setBrush(c)
        else:
            self.setPen(Qt.QPen(c, weight))

class NDVI_Plot(Qwt.QwtPlot):
    def __init__(self, parent = None, *args):
        super(NDVI_Plot, self).__init__(parent, *args)
        self.curves = {}
        #self.statCurves={}
        self.data ={}
        month = ['APR','','', 'MAY','','',  'JUN','','', 'JUL','','',  'AUG','','',  'SEP','','', \
                                   'OCT','','',  'NOV','','',  'DEC','','',   'JAN','','',  'FEB','','',  'MAR', '', '']
        
        #self.series = (series_name,weight,isFilled, visible, z)
        self.series = [\
                        ('1998 - 1999',2,  False, False, 0),('1999 - 2000',2,  False, False, 0),\
                        ('2000 - 2001',2,  False, False, 0),('2001 - 2002',2,  False, False, 0),\
                        ('2002 - 2003',2,  False, False, 0),('2003 - 2004',2,  False, False, 0),\
                        ('2004 - 2005',2,  False, False, 0),('2005 - 2006',2,  False, False, 0),\
                        ('2006 - 2007',2,  False, False, 0),('2007 - 2008',2,  False, False, 0),\
                        ('Average',3,  False, True, 0), 
                        ('SD Lower',0,  True, True, 100),('SD Upper',0, True, True, 101)]
           
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setMinimumSize(QtCore.QSize(350, 0))
        #
        self.setCanvasBackground(GemColor(217, 217, 217, 255))
        # set plot default layout
        self.plotLayout().setMargin(0)
        self.plotLayout().setCanvasMargin(0)
        self.plotLayout().setAlignCanvasToScales(True)
        
        # set X Axis
        bottomAxis = self.setAxisTitle(Qwt.QwtPlot.xBottom, 'Time (SPOT-VGT-S10 periods)')
        self.setAxisScaleDraw(Qwt.QwtPlot.xBottom, TextScaleDraw(month))
        self.setAxisScale(Qwt.QwtPlot.xBottom, 0, 35)
        self.setAxisMaxMajor(Qwt.QwtPlot.xBottom, 36) # set a maximum of 10 Major ticks
        self.setAxisMaxMinor(Qwt.QwtPlot.xBottom, 0) # force zero minor ticks
        self.enableAxis(Qwt.QwtPlot.xBottom)
        # set Y Axis
        self.setAxisTitle(Qwt.QwtPlot.yLeft, 'Scaled NDVI')
        self.setAxisScale(Qwt.QwtPlot.yLeft, 0, 255)
        #
        # attach a grid    
        grid = Qwt.QwtPlotGrid()
        grid.attach(self)
        grid.setPen(Qt.QPen(Qt.Qt.black, 0, Qt.Qt.DotLine))
        
        #
        self._colorList = self.createColorList()
                
        #self.replot()
    def linear_color_gradient(self, beginColor, endColor, steps=10, alpha=255):
        '''
        beginColor & endColor are tuples of (R,G,B)
        '''
        color1 = beginColor
        color2 = endColor
        stepColor = []
        for i in xrange(steps):
            ratio = i / float(steps)
            R_ = int(round(color2[0] * ratio + color1[0] * (1 - ratio)));
            G_ = int(round(color2[1] * ratio + color1[1] * (1 - ratio)));
            B_ = int(round(color2[2] * ratio + color1[2] * (1 - ratio)));
            Rx = hex(R_)[2:]
            Gx = hex(G_)[2:]
            Bx = hex(B_)[2:]
            #Ax = hex(alpha)[2:]
            stepColor.append((R_,G_,B_,alpha))#'0x'+Rx+Gx+Bx)#+Ax)
        return stepColor

    def createColorList(self):
        color_list1= self.linear_color_gradient((255, 237, 160), (252, 78, 42), 5) #creating 5 steps
        color_list2= self.linear_color_gradient((227, 26, 28), (8, 29, 88), 5) #creating 5 steps
        color_avg = [(0,0,255,255)] #Blue
        color_sd_lower = [(217, 217, 217, 255)] #Gray
        color_sd_upper = [(0, 255, 25, 75)] # Green
        color_list = color_list1 + color_list2 +color_avg+color_sd_lower+color_sd_upper# Updating with 10 steps
        return color_list
    
    def initialize(self):
        # attach a horizontal marker at y = 0
        self.clear()
        self.curves = {}
        # set Markers
        marker = Qwt.QwtPlotMarker()
        marker.attach(self)
        marker.setValue(0.0, 25.0)
        marker.setLineStyle(Qwt.QwtPlotMarker.HLine)
        marker.setLabelAlignment(Qt.Qt.AlignLeft | Qt.Qt.AlignTop)
        marker.setLabel(Qwt.QwtText('NDVI = 0'))
        #
        self.pointMarker = Qwt.QwtPlotMarker()
        self.pointMarker.attach(self)
           
        # set Legend
        legend = Qwt.QwtLegend()
        legend.setItemMode(Qwt.QwtLegend.CheckableItem)
        self.insertLegend(legend, Qwt.QwtPlot.RightLegend)
        self.connect(self,
                     Qt.SIGNAL('legendChecked(QwtPlotItem*, bool)'),
                     self.showCurve)
             
        
    def update(self, gen_data, stats_data):
        '''I am using iterators for creating the data'''
        '''stats_data ---> tuple (point_avg, point_sd, upper_SD, lower_SD)'''
        
        self.clearCurves()
        self.initialize()
        self.curves = {}
        point_avg, point_sd, upper_SD, lower_SD   = stats_data
        ydata = list(gen_data)
        ydata.append(point_avg)
        ydata.append(lower_SD)
        ydata.append(upper_SD)
           
        #self.series = (series_name,weight,isFilled, visible, z)
       
        gen_curve = (self.createCurve(self.series[id][0],ydata[id], 
                        GemColor(self._colorList[id][0], 
                                        self._colorList[id][1],
                                        self._colorList[id][2],
                                        self._colorList[id][3]), 
                        weight=self.series[id][1], 
                        isFilled=self.series[id][2], curveType='fitted', 
                        visible=self.series[id][3], 
                        z=self.series[id][4])  
                        for id in xrange(len(self.series)))
                        
        list(gen_curve)
               
        self.replot()
     
    def createCurve(self, name, ydata, color, weight, isFilled=False, curveType='fitted', visible=True, z=0):
        x = (x for x in xrange(36))
        curveAttribute = {'fitted':Qwt.QwtPlotCurve.Fitted}
        curve= NDVI_Curve(name)
        #setAttributes(self, color, weight, isFilled=False)
        curve.setAttributes(color, weight, isFilled)
        curve.setStyle(Qwt.QwtPlotCurve.Lines)
        curve.setCurveAttribute(curveAttribute[curveType])
        curve.attach(self)
        xdata = list(x)
        curve.setData(xdata, ydata)
        self.curves[name]=curve
        curve.setZ(curve.z()-z)
        self.showCurve(self.curves[name], visible)
    
    def deleteCurve(self, name) :
        try:
            item = self.curves[name]
            widget = self.legend().find(item)
            del widget
            del item
            
        except:
            print 'curve: ', name, 'not found'
    
    def clearCurves(self):
        for serie in self.series:
           name = serie[0]
           self.deleteCurve(name)
           
    
    def showCurve(self, item, on):
        item.setVisible(on)
        widget = self.legend().find(item)
        if isinstance(widget, Qwt.QwtLegendItem):
            widget.setChecked(on)
        self.replot()
