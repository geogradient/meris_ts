#!/usr/bin/env python
__author__ = "Jose M. Beltran <beltran.data@gmail.com>"
__version__ = "0.2.3"

import os, sys, mmap
import numpy as np
import scipy.stats as stats
from string import strip
from itertools import islice, imap, chain, ifilter
from gem import GEM_Image
from shapely.geometry import LineString

from PyQt4 import QtCore, QtGui, Qt
import PyQt4.Qwt5 as Qwt 
import ui_gem_viewer

from gem_stats import *

from plot_image import *
from plot_NDVI import *
from plot_freq import *
from plot_bar import *
from xing_table import *
from simtest_table import *


class GenerateClassProfiles:
    def __init__(self, ofile):
        if ofile is not None:
            try:
                self._datammap = mmap.mmap(ofile.fileno(),0,tagname='signaturefile', access=mmap.ACCESS_READ)
            except ValueError:
                print 'ERROR: accesing self._datammap'
    def next(self):
        '''The lower-index slice will decrease its value in 12 bytes to 
        get rid off the header [CLASS000_00,] and upper-index in 2 bytes 
        to get rid off the EOL characters \r\n'''
        try:
            self._datammap.read(12)
            profile = self.toArray(self._datammap.readline())#[lowerIndexPointer:upperIndexPointer])
        except:
            self._datammap.seek(0, 0)
            raise StopIteration        
        return profile

    def __iter__(self):        
        return self

    def toArray(self, _string):
        '''Convert a string of comma-separated values
        to a numpy array with float values'''
        dirty = list(_string.split(','))
        cleanme = map(strip, dirty)
        clean = map(float, cleanme)    
        return  np.array(clean)

class Visual_Main(QtGui.QMainWindow, ui_gem_viewer.Ui_GemVisualGUI):
    '''It is important to inherit from the QtGui.QMainWindow, 
    otherwise it will fail'''

    def __init__(self, parent=None):
        super(Visual_Main, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.__month = ['APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP',\
                                   'OCT', 'NOV', 'DEC',  'JAN', 'FEB', 'MAR']
        self.__synthesisDay = frozenset([1, 11, 21])
        self.__dayInTime =[('%s '%iday)+imonth for imonth in self.__month for iday in self.__synthesisDay]
        '''Available dates on the SPOT-VEGETATION NDVI 10-day synthesys product.'''
        self.__yearsAvailable=[iyear for iyear in xrange(1998, 2009)]
        self._nyears = len(self.__yearsAvailable)
        self._nclasses = 87
        self._nPointsInTime =36
        
        self.setupUi(self)
        self.initializeMainApp()
        # Adding the plots to widget Holders
        self.layoutPlot = Qt.QVBoxLayout(self.plotWidgetHolder)
        self.plot = NDVI_Plot(self.plotWidgetHolder)
        self.layoutPlot.addWidget(self.plot)

        self.imagePlot = ImagePlot(self.imageWidgetHolder)
        layoutImage = Qt.QVBoxLayout(self.imageWidgetHolder)
        layoutImage.addWidget(self.imagePlot)

        self.histo = BarPlot(self.freqWidgetHolder, attributes=[GemColor(217, 217, 217, 255), 1, GemColor(0, 0, 255, 200)])
        #self.histo.setCanvasBackground(Qt.Qt.white)
        layoutHisto = Qt.QVBoxLayout(self.freqWidgetHolder)
        layoutHisto.addWidget(self.histo)
        
        self.xingTable = XingTable(self.crossTableWidgetHolder)
        layoutXingTable = Qt.QVBoxLayout(self.crossTableWidgetHolder)
        layoutXingTable.addWidget(self.xingTable)
        
        self.simTestTable= SimTestTable(self.simTestWidgetHolder)
        layoutSimTestTable = Qt.QVBoxLayout(self.simTestWidgetHolder)
        layoutSimTestTable.addWidget(self.simTestTable)
           
        # ---------------------------------------------------------------------#
        self.initializePlotZoomers(self.plot)
       # ---------------------------------------------------------------------#
        self.pickerImage = Qwt.QwtPlotPicker(
            Qwt.QwtPlot.xBottom,
            Qwt.QwtPlot.yLeft,
            Qwt.QwtPicker.PointSelection | Qwt.QwtPicker.DragSelection,
            Qwt.QwtPlotPicker.CrossRubberBand,
            Qwt.QwtPicker. ActiveOnly,
            self.imagePlot.canvas())

        self.pickerImage.setRubberBandPen(QtGui.QPen(Qt.Qt.yellow))
        self.pickerImage.setTrackerPen(QtGui.QPen(Qt.Qt.yellow))

        # -------------------------------------------------------------------- #

        self.connect(self.btnZoomPlot, Qt.SIGNAL('toggled(bool)'), self.zoom)
        self.connect(self.lockButton, Qt.SIGNAL('toggled(bool)'), self.limit_data)
        self.connect(self.loadMaskButton, Qt.SIGNAL('pressed()'), self.openMaskDataset)
        self.connect(self.applyMask, Qt.SIGNAL('toggled(bool)'), self.updateImageData)
        self.connect(self.picker,
                     Qt.SIGNAL('moved(const Qt.QPoint &)'),
                     self.moved)
        self.connect(self.picker,
                     Qt.SIGNAL('selected(const Qt.QaPolygon &)'),
                     self.selected)

        self.connect(self.pickerImage,
                     Qt.SIGNAL('moved(const Qt.QPoint &)'),
                     self.moved)                     
        self.connect(self.pickerImage,
                     Qt.SIGNAL('appended(const QPoint &)'),
                     self.appended)

    def initializeMainApp(self):
        self.__currentClass = 0
        self.gemClassSpinBox.setValue(self.__currentClass)
        self.__currentTimeSeries = 0
        self.timeSeriesComboBox.setCurrentIndex(self.__currentTimeSeries)
        self.__pointInTime = 0
        self.timeSlider.setValue(self.__pointInTime)
        self.__ofile = None
        self.__mask = None
        self.__dataLoaded = None
        self.__maskLoaded = None
        self.__oimage = None
        self._exit = None
        self.gdal_image=None
        self.gdal_mask=None
        self.freqPlot = None
        self.freqData = None
             
        self.controlSimTestDockWidget.setEnabled(False)
        self.lockButton.setEnabled(False)
        self.loadMaskButton.setEnabled(False)
        self.applyMask.setEnabled(False)
        
        self._testID = 0
        self._selectedSet = 0
        self._data = None
        self._dataAVG = None
        self._dataSD = None
        self._class0 = 0
        self._class1 = 0
        
        
        self.testDescriptions = {0:'Spectral angle: \n The spectral angle is expressed in radians. The value should be between [0:pi/4], but typically much lower if the bands are highly correlated.  A value close to zero means "very similar", large values mean "very distinct" Coded by: Wim H. Bakker -ITC. "The cosine of the spectral angle is equivalent to the correlation coefficient (Hadley, 1961), this means  that the spectral angle (SA) is a statistical method for expressing similarity or dissimilarity between two pixel vectors..." Source: Bakker and Schimdt (2002).', 1:'Bray-Curtis distance:\n Output ranges between [0:1] if all values are positive. Zero represent exact similar coordinates. A value close to zero means "very similar", large values mean "very distinct" Coded by: Wim H. Bakker -ITC', 2:'Euclidian distance:\n A value close to zero means "very similar", large values mean "very distinct". Source: Bakker and Schmidt (2002)', 3:'Intensity difference: \n A value close to zero means "very similar", large values mean "very distinct". Source: Bakker and Schmidt (2002)', 4:'Jaccards coefficient:\n Measures similarity. Ranges from [0:1]  A value close to one means "very similar", low values mean "very distinct". Source: Teknomo (2006)', 5:'Mann-Whitney u statistic: \n Returns the mann_whitney u statistic for two tails if two_tailed_pvale (or one tail pvalue) < significance_level_p then REJECT Ho-THERE ARE DIFFERENCES. Source: SCIPY-stats module', 6:'Kolmogorov-Smirnov: \n The test uses the two-sided asymptotic Kolmogorov-Smirnov distribution. The distribution is assumed to be continuous. If the K-S statistic is small or the p-value is high, then we cannot reject the null hypothesis. Source: SCIPY-stats module'}
        
        

    def initializePlotZoomers(self, obj):
        
        self.zoomers = []

        zoomer = Qwt.QwtPlotZoomer(
            Qwt.QwtPlot.xBottom,
            Qwt.QwtPlot.yLeft,
            Qwt.QwtPicker.DragSelection,
            Qwt.QwtPicker.AlwaysOff,
            obj.canvas())
        zoomer.setRubberBandPen(QtGui.QPen(Qt.Qt.green))
        self.zoomers.append(zoomer)

        zoomer = Qwt.QwtPlotZoomer(
            Qwt.QwtPlot.xTop,
            Qwt.QwtPlot.yRight,
            Qwt.QwtPicker.PointSelection | Qwt.QwtPicker.DragSelection,
            Qwt.QwtPicker.AlwaysOff,
            obj.canvas())
        zoomer.setRubberBand(Qwt.QwtPicker.NoRubberBand)
        self.zoomers.append(zoomer)

        self.picker = Qwt.QwtPlotPicker(
            Qwt.QwtPlot.xBottom,
            Qwt.QwtPlot.yLeft,
            Qwt.QwtPicker.PointSelection | Qwt.QwtPicker.DragSelection,
            Qwt.QwtPlotPicker.CrossRubberBand,
            Qwt.QwtPicker.ActiveOnly,
            obj.canvas())

        self.picker.setRubberBandPen(QtGui.QPen(Qt.Qt.yellow))
        self.picker.setTrackerPen(QtGui.QPen(Qt.Qt.black))
       
    
    def updateImageData(self):
        # attach a plot image
        newBand = (self.__pointInTime+1)+(self.__currentTimeSeries*self._nPointsInTime)
          
        if self.gdal_image is not None and self.applyMask.isChecked() !=True:
            self.imagePlot.image.setData(self.getBand(newBand))
            self.imagePlot.replot()
            
           
        elif self.gdal_image is not None and self.applyMask.isChecked():
            NDVI_Data=self.getBand(newBand)
            mask=self.gdal_mask.getBand(1)
            
            masked = np.where(mask==self.__currentClass+1, mask/self.__currentClass+1, 0)
            maskedData = NDVI_Data*masked
               
            self.imagePlot.image.setData(maskedData, isMask=True)
            self.imagePlot.replot()
       

    def showCoordinates(self, position):
        self.statusBar().showMessage(
            'x = %+.6g, y = %.6g'
            % (self.histo.invTransform(Qwt.QwtPlot.xBottom, position.x()),
               self.histo.invTransform(Qwt.QwtPlot.yLeft, position.y())))

    def showInfo(self, text=None):
        #From Qwt demos
        if not text:
            if self.picker.rubberBand():
                text = 'Cursor Pos: Press left mouse button in plot region'
            else:
                text = 'Zoom: Press mouse button and drag'

        self.statusBar().showMessage(text)

    def moved(self, point):
        '''From Qwt demos'''
        info = "Point=%g, NDVI Scaled=%g"%(
           self.plot.invTransform(Qwt.QwtPlot.xBottom, point.x()),
            self.plot.invTransform(Qwt.QwtPlot.yLeft, point.y()))
        self.showInfo(info)
        
    def movedFreq(self, point):
        '''From Qwt demos'''
        info = "SD=%g, Count=%g"%(
           self.histo.invTransform(Qwt.QwtPlot.xBottom, point.x()),
            self.histo.invTransform(Qwt.QwtPlot.yLeft, point.y()))
        self.showInfo(info)
    
    def appended(self, point):
       pass


    def selected(self, _):
        self.showInfo(_)

    def zoom(self, on):
        self.zoomers[0].setEnabled(on)
        self.zoomers[0].zoom(0)

        self.zoomers[1].setEnabled(on)
        self.zoomers[1].zoom(0)

        if on:
            self.picker.setRubberBand(Qwt.QwtPicker.NoRubberBand)
        else:
            self.picker.setRubberBand(Qwt.QwtPicker.CrossRubberBand)

        self.showInfo()
    def zoomFreq(self, on):
        self.zoomersFreq[0].setEnabled(on)
        self.zoomersFreq[0].zoom(0)

        self.zoomersFreq[1].setEnabled(on)
        self.zoomersFreq[1].zoom(0)

        if on:
            self.pickerFreq.setRubberBand(Qwt.QwtPicker.NoRubberBand)
        else:
            self.pickerFreq.setRubberBand(Qwt.QwtPicker.CrossRubberBand)

        self.showInfo()
    def showDialog(self):
        #TODO: Create a dialog box to prevent user interation until the process is finished.
        pass
          
    def retriveDataFromMMAP(self, iclass, nyears=10):
        #FIXME: It raises an error if you try to open a file and then you decide not to.
        '''Returns an iterator of the year-profiles of the selected class'''
        newStart = iclass*nyears
        newEnd = newStart+nyears
        g = GenerateClassProfiles(self.__ofile)
        nmap = g._datammap
        # The nmap is used to close the call to datammap
        return islice(g, newStart, newEnd, 1), nmap 

    def getBand(self, iclass):
        return self.gdal_image.getBand(iclass)
    @QtCore.pyqtSignature("int")
    def on_binSpinBox_valueChanged(self):
        self.new_histogram()
        
    @QtCore.pyqtSignature("int")
    def on_gemClassSpinBox_valueChanged(self):
        self.__currentClass = self.getCurrentClass()
        if self.__dataLoaded:
            self.updatePlot(self.__currentClass)
            self.generator_stats(self.__currentClass)

        if self.gdal_image is not None:
            self.updateImageData()

    def getCurrentClass(self):
        return self.gemClassSpinBox.value()

    @QtCore.pyqtSignature("int")
    def on_timeSlider_valueChanged(self):
        self.__pointInTime = self.getpointInTime()
        self.updatePointInTime()
        if self.__ofile is not None:
            self.updatePlotMarker()
            if  self.lockButton.isChecked():
                self.updatePlot(self.__currentClass)

        if self.gdal_image is not None:
            self.updateImageData() 

    def getpointInTime(self):
        return self.timeSlider.value()

    def updatePointInTime(self):
        nextYear = set(['JAN', 'FEB', 'MAR'])
        if self.__dayInTime[self.__pointInTime][-3:] in nextYear:
            self.pointInTime.setText(self.__dayInTime[self.__pointInTime]+( ' %2d'%(self.__yearsAvailable[self.__currentTimeSeries+1])))
        else:
            self.pointInTime.setText(self.__dayInTime[self.__pointInTime]+( ' %2d'%(self.__yearsAvailable[self.__currentTimeSeries])))


    
    def updateTestID(self):
        self._testID = self.getCurrentTest()
    def getCurrentTest(self):
        return self.testComboBox.currentIndex()
    
    @QtCore.pyqtSignature("int")
    def on_timeSeriesComboBox_currentIndexChanged(self):
        self.updateCurrentTimeseries()
        self.updatePointInTime()
        if self.gdal_image is not None:
            self.updateImageData()

    def getCurrentTimeSeries(self):
        return self.timeSeriesComboBox.currentIndex()

    def updateCurrentTimeseries(self):
        self.__currentTimeSeries = self.getCurrentTimeSeries()

    @QtCore.pyqtSignature("bool")
    def on_actionOpenImageDataset_triggered(self):
        #self.statusBar().showMessage("Loading Image Dataset")
        self.updateDisplay("Loading Image Dataset") 
        self.fileOpenImageDataset()
        self.createDataset()
        self.updateDisplay("Image Loaded")
        self.loadMaskButton.setEnabled(True)
        self.rightTabWidget.setCurrentIndex(0)

    def fileOpenImageDataset(self):
        supportedFileFormats=['img', 'tif']
        dir = os.path.dirname(self.__oimage) if self.__oimage is not None else "."
        formats = ["*.%s" % unicode(format).lower() for format in supportedFileFormats]
        fullpathfilename = unicode(QtGui.QFileDialog.getOpenFileName(self,
            "GEM Visual - Choose Image", dir,
            "Image files (%s)" % " ".join(formats)))
        try:
            self.__oimage = str(fullpathfilename)
            self.statusBar().showMessage("Loading image file reference: SUCCEED")
        except:
            self.statusBar().showMessage("Loading image file reference: FAILED")
        self.updateDisplay(self.__oimage)
    
    
    def openMaskDataset(self):
        supportedFileFormats=['img', 'tif']
        dir = os.path.dirname(self.__oimage) if self.__oimage is not None else "."
        formats = ["*.%s" % unicode(format).lower() for format in supportedFileFormats]
        fullpathfilename = unicode(QtGui.QFileDialog.getOpenFileName(self,
            "GEM Visual - Choose Image", dir,
            "Image files (%s)" % " ".join(formats)))
        try:
            self.__mask = str(fullpathfilename)
            self.statusBar().showMessage("Mask image loaded")
        except:
            self.statusBar().showMessage("Masked image file reference: FAILED")

        self.updateDisplay(self.__mask)
        self.createMaskDataset()
        self.updateImageData()
        self.applyMask.setEnabled(True)
        self.updateDisplay("Mask Loaded")
        
    def createDataset(self):
        self.gdal_image = GEM_Image()
        try:
            if self.__oimage is not None or len(self.__oimage >2):
                self.gdal_image.open(self.__oimage)
                self.dims = self.gdal_image.dims
                self.updateDisplay('Dataset dimensions %d rows, %d cols, %d bands'%(self.dims[0], self.dims[1], self.dims[2]))
                self.statusBar().showMessage("Dataset loaded: SUCCEED")
                self.__imageLoaded = True
                self.updateImageData()
            else:
                self.updateDisplay('Image is none, please load an image dataset')
        except:
            self.statusBar().showMessage("Dataset loaded: FAILED")
    
    def createMaskDataset(self):
        self.gdal_mask = GEM_Image()
        try:
            if self.__mask is not None or len(self.__mask >2):
                self.gdal_mask.open(self.__mask)
                self.dims = self.gdal_mask.dims
                self.updateDisplay('Mask dataset dimensions %d rows, %d cols, %d bands'%(self.dims[0], self.dims[1], self.dims[2]))
                self.statusBar().showMessage("Mask dataset loaded: SUCCEED")
                self.__maskLoaded = True
                
            else:
                self.updateDisplay('Mask is none, please load a mask dataset')
        except:
            self.statusBar().showMessage("Mask dataset loaded: FAILED")

    @QtCore.pyqtSignature("bool")
    def on_actionOpenSignatureFile_triggered(self):
        #self.statusBar().showMessage('blablabla')
        self.updateDisplay("Loading signature File") 
        self.fileOpenSignatureFile()
        if self.__ofile is not None:
            self.plot.initialize()
            self.updatePlot(self.__currentClass)
            self.updateDisplay("Signature File Loaded")
            self.updateDisplay("Please waiting... Calculating initial stats")
            self.calculateClassStats()
            self.new_histogram()
            #self.wroli()
            self.statsTabWidget.setCurrentIndex(2)
            self.rightTabWidget.setCurrentIndex(1)
            self.lockButton.setEnabled(True)
            self.controlSimTestDockWidget.setEnabled(True)
            
    def openExcelFile(self, filename='hola'):
        import xlrd 
        book = xlrd.open_workbook(filename)
        sh = book.sheet_by_index(0) 
        for r in range(sh.nrows)[1:]:  print sh.row(r)[:4]
        
    def fileOpenSignatureFile(self):
        #FIXME: Find the way to close the datafilename
        if self.__dataLoaded:
            self.fileClose()

        supportedFileFormats=['dat', 'txt']
        dir = os.path.dirname(self.__ofile) if self.__ofile is not None else "."
        formats = ["*.%s" % unicode(format).lower() for format in supportedFileFormats]
        fullpathfilename = unicode(QtGui.QFileDialog.getOpenFileName(self,
            "GEM Visual - Choose Signature File", dir,
            "GEM Signature files (%s)" % " ".join(formats)))

        try:
            self.__ofile = open(fullpathfilename, 'r')
            self.__dataLoaded = True
            self.statusBar().showMessage("Signature file open and ready")

        except:
            self.updateDisplay('Error opening the signature file')

    def updatePlotMarker(self):
        # Creating markers
        self.plot.pointMarker.setValue(self.__pointInTime, 0.0)
        self.plot.pointMarker.setLineStyle(Qwt.QwtPlotMarker.VLine)
        self.plot.pointMarker.setLineStyle(Qwt.QwtPlotMarker.VLine)
        self.plot.pointMarker.setLabelAlignment(Qt.Qt.AlignRight | Qt.Qt.AlignBottom)
        self.plot.pointMarker.setLabel(Qwt.QwtText(self.__dayInTime[self.__pointInTime]))
        self.plot.replot()
        #
    def freq_XY(self, freq_array):
        '''Calculates Y values for missing X'''
        x = range(freq_array[0, 0], freq_array[freq_array.shape[0]-1, 0])
        y=[]
        i=0
        for value in x:
            if value == freq_array[i, 0]:
                y.append(freq_array[i, 1])
                i+=1
            else:
                y.append(0)
        return x, y

            
    
    def activateFreqZoomers(self):

        '''self.zoomersFreq =[]

        zoomer = Qwt.QwtPlotZoomer(
            Qwt.QwtPlot.xBottom,
            Qwt.QwtPlot.yLeft,
            Qwt.QwtPicker.DragSelection,
            Qwt.QwtPicker.AlwaysOff,
            self.histo.canvas())
        zoomer.setRubberBandPen(QtGui.QPen(Qt.Qt.green))
        self.zoomersFreq.append(zoomer)

        zoomer = Qwt.QwtPlotZoomer(
            Qwt.QwtPlot.xTop,
            Qwt.QwtPlot.yRight,
            Qwt.QwtPicker.PointSelection | Qwt.QwtPicker.DragSelection,
            Qwt.QwtPicker.AlwaysOff,
            self.histo.canvas())
        zoomer.setRubberBand(Qwt.QwtPicker.NoRubberBand)
        self.zoomersFreq.append(zoomer)'''

        self.pickerFreq = Qwt.QwtPlotPicker(
            Qwt.QwtPlot.xBottom,
            Qwt.QwtPlot.yLeft,
            Qwt.QwtPicker.PointSelection | Qwt.QwtPicker.DragSelection,
            Qwt.QwtPlotPicker.CrossRubberBand,
            Qwt.QwtPicker.ActiveOnly,
            self.histo.canvas())
            
        self.pickerFreq.setRubberBandPen(QtGui.QPen(Qt.Qt.yellow))
        self.pickerFreq.setTrackerPen(QtGui.QPen(Qt.Qt.black))

        #self.connect(self.btnZoomFreq, Qt.SIGNAL('toggled(bool)'), self.zoomFreq)
        self.connect(self.pickerFreq,
                     Qt.SIGNAL('moved(const Qt.QPoint &)'),
                     self.movedFreq)
        self.connect(self.pickerFreq,
                     Qt.SIGNAL('selected(const Qt.QaPolygon &)'),
                     self.selected)
    
    @QtCore.pyqtSignature("int")
    def on_byYearCheckBox_stateChanged (self):
        if self.byYearCheckBox.isChecked():
            self._selectedSet = 0
            self.updateTestTable()
              
    @QtCore.pyqtSignature("int")
    def on_byPairedClassesCheckBox_stateChanged (self):
        if self.byPairedClassesCheckBox.isChecked():
            self._selectedSet = 1
            self.updateTestTable()
    
    @QtCore.pyqtSignature("int")
    def on_class0SpinBox_valueChanged(self):
        self._class0 = self.class0SpinBox.value()
        self.updateTestTable()
        self.byPairedClassesCheckBox.setChecked(True)
    
    @QtCore.pyqtSignature("int")
    def on_class1SpinBox_valueChanged(self):
        self._class1 = self.class1SpinBox.value()
        self.updateTestTable()
        self.byPairedClassesCheckBox.setChecked(True)
    

    @QtCore.pyqtSignature("int")
    def on_testComboBox_currentIndexChanged(self):
        self.updateTestID()
        self.updateTestTable()
        self.testLog.clear()
        self.testLog.setText(self.testDescriptions[self._testID])
                
    def updateTestID(self):
        self._testID = self.getCurrentTest()
    def getCurrentTest(self):
        return self.testComboBox.currentIndex()
    
    
    def updateTestTable(self):
        if self._selectedSet ==1:
            v=self.fpoint_upperSD(self._class0)
            w=self.fpoint_upperSD(self._class1)
            gen_data = None
            self.simTestTable.populateTable(self._testID, self._selectedSet,v, w, gen_data, self._class0, self._class1)
            self.statusBar().showMessage('Test: %d, Dataset: %d --->\
            Average+standard deviation-paired classes (%d,%d)'%\
            (self._testID, self._selectedSet, self._class0, self._class1))
        else:
            v=self.fpoint_avg(self.__currentClass)
            w = None
            gen_data =self.generator_dataInClass(self.__currentClass)
           
            self.simTestTable.populateTable(self._testID, self._selectedSet, v, w, gen_data)
            self.statusBar().showMessage('Test: %d, Dataset: %d ---> \
            Yearly basis-current class'%(self._testID, self._selectedSet))
    
    def generator_stats(self, iclass):
        generator = self.generator_dataInClass(iclass)
        gen_contents= generator.next()
        self.updateDisplay(gen_contents)
        return gen_contents
        
    def generator_dataInClass(self, iclass):
        '''Returns a year data generator to build a list'''
        yearDataGenerator, nmap = self.retriveDataFromMMAP(iclass)
        #nmap.close()
        return yearDataGenerator
    
    def newPlotData(self, iclass):
        '''using iterators for creating the data'''
        gen_data = self.generator_dataInClass(iclass)
        return gen_data
       
    def updatePlot(self, iclass):
        self.dockPlotWidget.setWindowTitle('Plot viewer --> Class %d'%iclass)
        gen_data = self.newPlotData(iclass)
       
        stats_data = self.calculatePlotStats(iclass) 
        '''
        if self._selectedSet == None:
            self._xSelection = 0
        if self._testID == None:
            self._testID = 0
        '''
        self.updateTestTable()
        self.plot.update(gen_data, stats_data)
        self.updatePlotMarker()
   
    def sliceme(self, values_list):
        '''Slice the data used in the generators'''
        if self.lockButton.isChecked():
            s = values_list[0:self.__pointInTime+1]           
        else:
            s = values_list[0: 36]
        return s
        
    def data_transposed(self, iclass):
       '''facilitates points statistics calculation for all years'''
       gen_stats = self.generator_dataInClass(iclass)
       a = imap(self.sliceme, gen_stats)
       aT= np.array(list(a)).T
       return aT
   
    def calculatePlotStats(self, iclass):
        '''Calculates average, standard deviation, upper & lower-SD limits'''
        point_avg = self.fpoint_avg(iclass)
        point_sd = self.fpoint_sd(iclass)
        upper_SD = point_avg + point_sd
        lower_SD = point_avg - point_sd
        return point_avg, point_sd, upper_SD, lower_SD
    
    def fpoint_avg(self, iclass):
        '''calculates the mean of a point in all years'''
        aT = self.data_transposed(iclass)
        return np.array(map(np.mean, aT))
    
    def fpoint_sd(self, iclass):
        '''calculates the SD of a point in all years'''
        aT = self.data_transposed(iclass)
        return np.array(map(np.std, aT))
        
    def fpoint_upperSD(self, iclass):
        '''calculates the upper- SD limit of a point in all years'''
        point_avg = self.fpoint_avg(iclass)
        point_sd = self.fpoint_sd(iclass)
        return  point_avg + point_sd
    
    def fpoint_lowerSD(self, iclass):
        '''calculates the lower- SD limit of a point in all years'''
        point_avg = self.fpoint_avg(iclass)
        point_sd = self.fpoint_sd(iclass)
        return  point_avg - point_sd
    
    def combination(self, nclasses, dummy=0, data=None):
        ''' Generates a list of unique pair combinations on the given list.
       and returns an unique tuple of (row,col) '''
        idx =[]
        i=0
        index = range(0, self._nclasses )
        f = open(r'D:\My Docs\working\dat\dist_wroli.txt', 'w')
       
        for each in xrange(len(index)):
            #current = index.pop(0)
            dat = []
            
            for left in index:
                idx.append((each,left))
                if dummy == 1:
                    value= data[i]
                    dat.append('%.2f, '%data[i])
                    #dat.append(str(data[i]))
                    #dat.append(',  ')
                i+=1
            current = index.pop(0)
            dat.append('\n')
            f.writelines(dat)
            
        f.close()
        return idx
    
    
    def lines2(self):
        #For debugging
        L1 = [((1, 1), (1, 3)), ((2, 2), (2, 3)), ((3, 3), (3, 4)), ((4, 2), (4, 4)), ((5, 2), (5, 3)), ((6, 0),(6, 2)), ((7, 1), (7, 3)), ((8, 1), (8, 4)), ((9, 0), (9, 3)), ((10, 0), (10, 4))]
        
        L2 = [((1, 2), (1, 4)), ((2, 2), (2, 4)), ((3, 3), (3, 4)), ((4, 4), (4, 5)), ((5, 2), (5, 3)), ((6, 0), (6, 2)), ((7, 2), (7, 4)), ((8, 2), (8, 4)), ((9, 0), (9, 2)), ((10, 2), (10, 3))]
        lines0 = [LineString(line) for line in L1]
        lines1 = [LineString(line) for line in L2]
        lengths0 = np.array([line.length for line in lines0])
        lengths1 = np.array([line.length for line in lines1])
        return lines0, lengths0, lines1, lengths1
    
    def Kees_Distance(self, iclass):
        upper1 = self.fpoint_upperSD(iclass)
        lower1 = self.fpoint_lowerSD(iclass)
        difference= (upper1-lower1)/2.0
        lines = [LineString(((point, lower1[point], 2), (point, upper1[point], 2))) for point in xrange(len(upper1))]
        lengths = np.array([line.length for line in lines])
        return lines, lengths, difference
    
    def lines(self, iclass):
        upper1 = self.fpoint_upperSD(iclass)
        lower1 = self.fpoint_lowerSD(iclass)
        lines = [LineString(((point, lower1[point], 2), (point, upper1[point], 2))) for point in xrange(len(upper1))]
        lengths = np.array([line.length for line in lines])
        return lines, lengths
    
    def wroli(self):
        indices  = self.combination(self._nclasses)
        #wroli_index_list = [self.wroli_index(pair) for pair in indices]
        wroli_index_list = [self.wroli_kees(pair) for pair in indices]
        self.combination(self._nclasses, dummy=1, data=wroli_index_list)
        print 'done'
        
        # DEBUGGING print self.wroli_index((0, 1))
        #try:
       #     self.xingTable.populateTable(indices, wroli_index_list)
       # except:
        #    print 'Error pupalting the table'
        self.statsTabWidget.setCurrentIndex(2)
        
    def wroli_kees(self, pairedClasses):
        #Weighted Ratio of Length of Intersections-#Beltran - de Bie index
        
        ##lines0, lengths0 = self.lines(pairedClasses[0])
        ##lines1, lengths1 = self.lines(pairedClasses[1])
        
        lines0, lengths0, difference0 = self.Kees_Distance(pairedClasses[0])
        lines1, lengths1, difference1 = self.Kees_Distance(pairedClasses[1])
        
        
        # DEBUGGING   lines0, lengths0, lines1, lengths1 = self.lines2()
        
        LO = lengths0
        LI = lengths1
        nvalues = len(LO)
        '''Intersections lengths for each point in time'''
        LINT=np.array([lines0[point].intersection(lines1[point]).length for point in xrange(nvalues)])
        ''''
        try:
            return sqrt(sum((self.v-self.w)**2))
        except:
            return False
        '''
        weigths = np.array([1.0/((difference0[point]**2)+(difference1[point]**2))**(1/2.0) for point in xrange(len(difference0))])
        
        WLINT = LINT*weigths
        SWLINT=WLINT.sum()
        
        
        return WLINT
    
    
    def wroli_index(self, pairedClasses):
        #Weighted Ratio of Length of Intersections-#Beltran - de Bie index
        
        lines0, lengths0 = self.lines(pairedClasses[0])
        lines1, lengths1 = self.lines(pairedClasses[1])
                
        # DEBUGGING   lines0, lengths0, lines1, lengths1 = self.lines2()
        
        LO = lengths0
        LI = lengths1
        nvalues = len(LO)
        '''Intersections lengths for each point in time'''
        LINT=np.array([lines0[point].intersection(lines1[point]).length for point in xrange(nvalues)])
        
        if (LO==LI).all() and (LO==LINT).all():
            WROLI = 1
        else:
            '''Sum of lengths in each point of time''' 
            LOLI = LO+LI
            '''maximum LOLI'''
            MAXLOLI = LOLI.max()
            '''minimum LOLI'''
            MINLOLI =  LOLI.min()
            '''forcing equality if max and min are equals'''
            '''
            if (MAXLOLI-MINLOLI)==0:
                NLOLI = np.zeros(nvalues)
            else:
            '''
            '''Normalized LOLI'''
            NLOLI= (LOLI - MINLOLI)/ (MAXLOLI-MINLOLI) 
                
            '''Ratio of LINT with LO'''
            RLINTO = LINT/LO
            '''Ratio of LINT with LI'''
            RLINTI = LINT/LI
            '''Difference on LINT ratios'''
            DRLINT = abs(RLINTO-RLINTI)
            '''Weigth due to DRLINT'''
            WDRLINT = 1 - DRLINT
            '''Weigth due to NLOLI'''
            WNLOLI = 1- NLOLI
            '''Weighted LINT'''
            WLINT = LINT*WDRLINT*WNLOLI
            '''Zero Intersections'''
            ZLINT = LINT[LINT==0]
            '''Count number of zero intersections'''
            SZLINT = len(ZLINT)
            '''Weight due to zero intersections'''
            WSZLINT = (nvalues-SZLINT) / float(nvalues)
            
            '''Sum of LINT'''
            SLINT = LINT.sum()
            '''Sum of WLINT'''
            SWLINT = WLINT.sum()
            
            if SLINT !=0:
                WROLI = (SWLINT / SLINT)*WSZLINT
            else:
                WROLI = -9999
        
        '''  #For DEBUGGING
        print LO
        print LI
        print LINT
        print LOLI
        print MAXLOLI,  MINLOLI
        print NLOLI
        print RLINTO
        print RLINTI
        print DRLINT
        print WDRLINT
        print WNLOLI
        print WLINT
        print ZLINT
        print SZLINT
        print WSZLINT
        print SLINT
        print SWLINT
        print WROLI
        '''
        
        print pairedClasses,WROLI
        return WROLI
       
    def calculateClassStats(self):
        '''Calculates de mean standard deviation for all the classes'''
        sd_points = (self.fpoint_sd(iclass) for iclass in xrange(self._nclasses))
        gen_overall_mean_sd = imap(np.mean, sd_points)
        # Creates a global variable to avoid calling calculateClasssStats when is not necessary
        self._overall_mean_sd = list(gen_overall_mean_sd)
        
    
    def createPolygons(self, point_avg, point_sd):
        '''using iterators for creating the data'''
        up = point_avg + point_sd
        low = point_avg - point_sd
        up_coords =[(x, up[x]) for x in xrange(len(up))]
        low_coords =[(x, low[x]) for x in xrange(len(low))][::-1]# invert the series in order to create a closed polygon
        closeSD =[up_coords[0]]
        sd_polygon= Polygon((up_coords+low_coords+closeSD))
        return sd_polygon
            
    def new_histogram(self):
        #Max_bin prevents to write more bins than necessary
        self.histo.clear()
        max_bins = len(stats.itemfreq(map(int, self._overall_mean_sd)))
        self.binSpinBox.setMaximum(max_bins)
        histoData = stats.histogram(self._overall_mean_sd, self.binSpinBox.value())
        
        width = histoData[2]
        y = histoData[0]
        x =[histoData[1]+k*width for k in xrange(len(y))]
        
        self.histo.clear()
        self.histo.attributes = [GemColor(0, 0, 255, 200), 0, GemColor(0, 0, 255, 200)]
        nbins= len(x)
        self.histo.setAxisScale(Qwt.QwtPlot.yLeft, 0, max(y)+1)
        self.histo.setAxisScale(Qwt.QwtPlot.xBottom, min(x)-1, max(x)+1)
        self.histo.go(nbins, x, y, width)

        self.activateFreqZoomers()
        self.histo.replot()
           
       
    def limit_data(self):
        self.updateDisplay(self.lockButton.isChecked())
        if self.lockButton.isChecked():
            self.timeSlider.setEnabled(False)
            self.pointInTime.setEnabled(False)
            self.calculateClassStats()
            self.new_histogram()
        else:
            self.timeSlider.setEnabled(True)
            self.pointInTime.setEnabled(True)
            self.calculateClassStats()
            self.new_histogram()
            
        self.updatePlot(self.__currentClass)
        
    @QtCore.pyqtSignature("bool")
    def on_actionClose_triggered(self):
        #TODO: Create a close dataset.
        self.fileClose()

    def fileClose(self):
        if self.__dataLoaded:
            self.plot.clear()
            self.plot.replot()
            #self.plot.setTitle('File>Open>Signature file to plot')
            self.__ofile.close()
            self.initializeMainApp()
            self.imagePlot.clear()


    def updateDisplay(self, message):
        self.textDisplay.append(str(message))#append(str(message))

#------------------------------------------------------------------------------#
#------------------------------------------------------------------------------#
def make():
    form = Visual_Main()

    form.show()
    return form

def main(args):
    app = QtGui.QApplication(sys.argv)
    #QCleanlooksStyle
    app.setStyle('cleanlooks')
    form = make()

    if form._exit == True:
        form.dataset =None
        form.gdal_image = None

    sys.exit(app.exec_())





#Run the application
if __name__ == "__main__":  
    main(sys.argv)
