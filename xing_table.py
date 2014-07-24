#!/usr/bin/env python
__author__ = "Jose M. Beltran <beltran.data@gmail.com>"
__version__ = "0.1.0"

from PyQt4 import QtCore, QtGui, Qt
import numpy as np
import string
from decimal import Decimal as decimal
from shapely.geometry import Polygon
from shapely.geometry import LineString

# setItem( row , column , new QTableWidgetItem( icon , caption ) )
class XingTable(QtGui.QTableWidget):
    def __init__(self, *args):
        super(XingTable, self).__init__(*args)
        self._nclasses =87
               
    def populateTable(self, indices, wroli_index_list):
        
        ofile = open('D://My Docs//working//dat//wroli_matrix.dat', 'r+')
        self.clear()
        self.setSortingEnabled(False)
        
        headers =['class %2d'%each for each in xrange(self._nclasses )]
        self.setRowCount(len(headers))
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        self.setVerticalHeaderLabels(headers)
        k=0
        for c_ in indices:
            self.setItem(c_[0],c_[1], QtGui.QTableWidgetItem('%.2f'%wroli_index_list[k]))
            ofile.write('(%d,%d):%.2f '%(c_[0],c_[1], wroli_index_list[k]))
            k+=1
        ofile.close()
        self.resizeColumnsToContents()

