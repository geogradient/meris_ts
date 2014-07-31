__author__ = "Jose M. Beltran <gemtoolbox@gmail.com>"
__version__ = "0.1.0"

import numpy as np
from PyQt4 import Qt
from PySide import Qwt
# import PyQt4.Qwt5 as Qwt

class PlotImage(Qwt.QwtPlotItem):
    def __init__(self, title = Qwt.QwtText()):
        #Qwt.QwtPlotItem.__init__(self)
        super(PlotImage, self).__init__()
        if not isinstance(title, Qwt.QwtText):
            self.title = Qwt.QwtText(str(title))
        else:
            self.title = title
        self.setItemAttribute(Qwt.QwtPlotItem.Legend);
        self.xyz = None
        self.xRange = None
        self.yRange = None
        
        
    def setData(self, xyz, xRange = None, yRange = None, isMask=False):
        '''Fixing a false maximum in the four cornes'''
        xyz[0, 0]=256
        xyz[0, 1134]=256
        xyz[664, 0]=256
        xyz[664, 1134]=256
        
        self.xyz = np.swapaxes(xyz, 0, 1)
        
        shape = xyz.shape
        if not xRange:
            xRange = (0, shape[1])
        if not yRange:
            yRange = (0, shape[0])

        print(xyz.max(), xyz.min())
        
        
        self.xMap = Qwt.QwtScaleMap(0, xyz.shape[1], *xRange)
        self.plot().setAxisScale(Qwt.QwtPlot.xBottom, *xRange)
        self.yMap = Qwt.QwtScaleMap(0, xyz.shape[0], *yRange)
        self.plot().setAxisScale(Qwt.QwtPlot.yLeft, *yRange)
          
       
        self.raster = Qwt.toQImage((self.xyz).astype(np.uint8))#.mirrored(True, True)
       
        
        for i in range(0, 256):
            if i == 0:
                self.raster.setColor(i, Qt.qRgb(0, 0, 0))
            else:
                #self.raster.setColor(i, Qt.qRgb(i, 75, (i-256)*-1))
                if isMask:
                    self.raster.setColor(i, Qt.qRgb(255, 255,0))
                else:
                    self.raster.setColor(i, Qt.qRgb(i, 30, (i-256)*-1))
                '''
                
                if isMask==False:
                    
                else:
                    self.raster.setColor(i, Qt.qRgb(i, i, i))
                '''
    #Qt.qRgba
    # Blue4(0,0,139) 
    # Light yellow (255 255 224)
    # Khaki1 (255 246 143)
    # Drak red (103,0 13)
    # Middle red(251 106  74)
    # light red (255, 245, 240)
    
    def updateLegend(self, legend):
        Qwt.QwtPlotItem.updateLegend(self, legend)
        legend.find(self).setText(self.title)

    def draw(self, painter, xMap, yMap, rect):
        """Paint image zoomed to xMap, yMap

        Calculate (x1, y1, x2, y2) so that it contains at least 1 pixel,
        and copy the visible region to scale it to the canvas.
        """
        assert(isinstance(self.plot(), Qwt.QwtPlot))
        
        # calculate y1, y2
        # the scanline the pixel order (index y) is normal
        y1 = y2 = self.raster.height()
        y1 *= (yMap.s1() - yMap.s1())
        y1 /= (self.yMap.s2() - self.yMap.s1())
        y1 = max(0, int(y1-0.5))
        y2 *= (yMap.s2() - self.yMap.s1())
        y2 /= (self.yMap.s2() - self.yMap.s1())
        y2 = min(self.raster.height(), int(y2+0.5))
        # calculate x1, x2 -- the pixel order (index x) is normal
        x1 = x2 = self.raster.width()
        x1 *= (xMap.s1() - self.xMap.s1())
        x1 /= (self.xMap.s2() - self.xMap.s1())
        x1 = max(0, int(x1-0.5))
        x2 *= (xMap.s2() - self.xMap.s1())
        x2 /= (self.xMap.s2() - self.xMap.s1())
        x2 = min(self.raster.width(), int(x2+0.5))
        # copy
        raster = self.raster.copy(x1, y1, x2-x1, y2-y1)
        # zoom
        raster = raster.scaled(xMap.p2()-xMap.p1()+1, yMap.p1()-yMap.p2()+1)
        # draw
        painter.drawImage(xMap.p1(), yMap.p2(), raster)

class ImagePlot(Qwt.QwtPlot):
    def __init__(self, parent=None, *args):
        #TODO: Enable zoomer
        super(ImagePlot, self).__init__(parent, *args)
       # set plot layout
        self.plotLayout().setMargin(0)
        self.plotLayout().setCanvasMargin(0)
        
        self.plotLayout().setAlignCanvasToScales(True)
        # set legend
        ##legend = Qwt.QwtLegend()
        ##legend.setItemMode(Qwt.QwtLegend.ClickableItem)
        ##self.insertLegend(legend, Qwt.QwtPlot.RightLegend)
        # set axis titles
        self.setAxisTitle(Qwt.QwtPlot.xBottom, 'colums')
        self.setAxisTitle(Qwt.QwtPlot.yLeft, 'rows')
        
        '''
        x = np.arange(-2*np.pi, 2*np.pi, 0.01)
        y = np.pi*np.sin(x)
        z = 4*np.pi*np.cos(x)*np.cos(x)*np.sin(x)
        # attach a curve
        curve = Qwt.QwtPlotCurve('y = pi*sin(x)')
        curve.attach(self)
        curve.setPen(Qt.QPen(Qt.Qt.green, 2))
        curve.setData(x, y)
        '''
        # attach a grid
        grid = Qwt.QwtPlotGrid()
        grid.attach(self)
        grid.setPen(Qt.QPen(Qt.Qt.black, 0, Qt.Qt.DotLine))
        
        # attach a plot image
        self.image = PlotImage('Image')
        self.image.attach(self)
        self.image.setData(np.zeros((665, 1138)))
            #square(512, -2*pi, 2*pi), (-2*pi, 2*pi), (-2*pi, 2*pi))
               
        ##self.connect(self,
                     ##Qt.SIGNAL("legendClicked(QwtPlotItem*)"),
                     ##self.toggleVisibility)
        
        # replot
        self.replot()
        self.zoomer = Qwt.QwtPlotZoomer(Qwt.QwtPlot.xBottom,
                                        Qwt.QwtPlot.yLeft,
                                        Qwt.QwtPicker.DragSelection,
                                        Qwt.QwtPicker.AlwaysOff,
                                        self.canvas())
        self.zoomer.setRubberBandPen(Qt.QPen(Qt.Qt.green))
        self.zoomer.setEnabled(False)
        self.zoomer.zoom(0)

    def toggleVisibility(self, plotItem):
        """Toggle the visibility of a plot item
        """
        plotItem.setVisible(not plotItem.isVisible())
        self.replot()
