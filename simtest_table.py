#!/usr/bin/env python
__author__ = "Jose M. Beltran <gemtoolbox@gmail.com>"
__version__ = "0.1.0"

from PyQt4 import QtCore, QtGui, Qt
import numpy as np
from gem_stats import *

# setItem( row , column , new QTableWidgetItem( icon , caption ) )
class SimTestTable(QtGui.QTableWidget):
    def __init__(self, *args):
        super(SimTestTable, self).__init__(*args)
        self._nyears =10
        self.DATA = Similarity()
    
   
    def populateTable(self, testID=0, selectedSet=0, v=None, w=None, gen_data=None, class0=None, class1=None ):
        rowheaders_dic={0:'SA [Radians]', 1:'BC [distance]',2:'ED [distance]', 3:'ID [Intensity]', 4:'JC [ratio]', 5:'U statistic', 6:'D statistic', 99:'two tailed p value' }
        
               
        test_dic={0:'Spectral angle', 1:'Bray-Curtis distance', 2:'Euclidian distance', 3:'Intensity difference', 4:'Jaccards coefficient', 5:'Mann-Whitney u statistic', 6:'Kolmogorov-Smirnov'}
        self.clear()
        self.setSortingEnabled(False)
        rowheaders =[rowheaders_dic[testID], rowheaders_dic[99]]
        self.setRowCount(2)
        self.setVerticalHeaderLabels(rowheaders)
        self.DATA.v = v
        
        if selectedSet == 0:
            headers =['year %2d'%year for year in xrange(self._nyears)]
            self.setColumnCount(len(headers))
            self.setHorizontalHeaderLabels(headers)   
            
            yearListData = list(gen_data)
            print len(yearListData)
           
            for year in xrange(len(yearListData)):
                self.DATA.w = yearListData[year]
               
                if testID==0:
                    SA= self.DATA.spectral_angle()
                    self.setItem(0, year, QtGui.QTableWidgetItem('%.12f'%SA))
                elif testID==1:
                    BCD= self.DATA.bray_curtis_distance()
                    self.setItem(0, year, QtGui.QTableWidgetItem('%.8f'%BCD))
                elif testID==2:
                    ED = self.DATA.euclidian_distance()
                    self.setItem(0, year, QtGui.QTableWidgetItem('%.8f'%ED))
                elif testID==3:
                    ID = self.DATA.intensity_difference()
                    self.setItem(0, year, QtGui.QTableWidgetItem('%.8f'%ID))
                elif testID==4:
                    JC = self.DATA.jaccards_coeficient()
                    self.setItem(0, year, QtGui.QTableWidgetItem('%.8f'%JC))
                elif testID==5:
                    U_statistic, two_tailed_pvalue = self.DATA.mann_whitney()
                    self.setItem(0, year, QtGui.QTableWidgetItem('%.8f'%U_statistic))
                    self.setItem(1, year, QtGui.QTableWidgetItem('%.12f'%two_tailed_pvalue))
                elif testID==6:
                    D_statistic,two_tailed_pvalue = self.DATA.kolmogorov_smirnov()
                    self.setItem(0, year, QtGui.QTableWidgetItem('%.8f'%D_statistic))
                    self.setItem(1, year, QtGui.QTableWidgetItem('%.12f'%two_tailed_pvalue))
                      
        else:
            
            self.DATA.w = w
            headers =['(%d class,%d class)'%(class0, class1)]
            self.setColumnCount(len(headers))
            self.setHorizontalHeaderLabels(headers)
            
            if testID==0:
                SA= self.DATA.spectral_angle()
                self.setItem(0, 0, QtGui.QTableWidgetItem('%.12f'%SA))
            elif testID==1:
                BCD= self.DATA.bray_curtis_distance()
                self.setItem(0, 0, QtGui.QTableWidgetItem('%.8f'%BCD))
            elif testID==2:
                ED = self.DATA.euclidian_distance()
                self.setItem(0, 0, QtGui.QTableWidgetItem('%.8f'%ED))
            elif testID==3:
                ID = self.DATA.intensity_difference()
                self.setItem(0, 0, QtGui.QTableWidgetItem('%.8f'%ID))
            elif testID==4:
                JC = self.DATA.jaccards_coeficient()
                self.setItem(0, 0, QtGui.QTableWidgetItem('%.8f'%JC))
            elif testID==5:
                U_statistic, two_tailed_pvalue = self.DATA.mann_whitney()
                self.setItem(0, 0, QtGui.QTableWidgetItem('%.8f'%U_statistic))
                self.setItem(1, 0, QtGui.QTableWidgetItem('%.12f'%two_tailed_pvalue))
            elif testID==6:
                D_statistic,two_tailed_pvalue = self.DATA.kolmogorov_smirnov()
                self.setItem(0, 0, QtGui.QTableWidgetItem('%.8f'%D_statistic))
                self.setItem(1, 0, QtGui.QTableWidgetItem('%.12f'%two_tailed_pvalue))
              
        self.resizeColumnsToContents()
        self.resizeRowsToContents()
