#!/usr/bin/env python
__author__ = "Jose M. Beltran <gemtoolbox@gmail.com>"

import os, sys, mmap
import numpy as np
from decimal import Decimal as decimal
from string import strip,  split

from itertools import islice, imap, chain, ifilter

class Labels_Generator:
    ''' Requires an ofile'''
    def __init__(self, ofile):
        if ofile is not None:
            try:
                self._datammap = mmap.mmap(ofile.fileno(),0, access=mmap.ACCESS_READ)
            except ValueError:
                print 'ERROR: accesing self._datammap'
    def next(self):
        try:
            nline = self.toArray(self._datammap.readline())#[lowerIndexPointer:upperIndexPointer])
        except:
            self._datammap.seek(0, 0)
            raise StopIteration        
        return nline

    def __iter__(self):        
        return self

    def toArray(self, nline):
        '''Convert a string of comma-separated values
        to a numpy array as Decimal values'''
        
        dirtyData = list(nline.split('\t'))
        cleanme = map(strip, dirtyData)
        text = cleanme[1].split()
        label = 'uc_'+text[1].zfill(2)
        nlabel = label.replace('+', '_')
        return  nlabel

class Generator_Profiles:
    ''' Requires an ofile'''
    def __init__(self, ofile):
        if ofile is not None:
            try:
                self._datammap = mmap.mmap(ofile.fileno(),0, access=mmap.ACCESS_READ)
            except ValueError:
                print 'ERROR: accesing self._datammap'
    def next(self):
        try:
            nline = self.toArray(self._datammap.readline())#[lowerIndexPointer:upperIndexPointer])
        except:
            self._datammap.seek(0, 0)
            raise StopIteration        
        return nline

    def __iter__(self):        
        return self

    def toArray(self, nline):
        '''Convert a string of comma-separated values
        to a numpy array as Decimal values'''
        
        dirtyData = list(nline.split('\t'))
        cleanme = map(strip, dirtyData)
        # No counts NOTE no counts in sigfile
        dataDecimal = map(decimal, cleanme[2:])
        '''Data Transposed'''
        data = np.array(dataDecimal).T
        return  data

# ---------------------------------------------------------------------------- #
''' Data creators '''
def get_labels():
    
    fullpath_filename= unicode('D:\My Docs\working\dat\exported_wroli_49c_clean.dat') 
    ofile = open(fullpath_filename, 'r')
    g = Labels_Generator(ofile)
    nmap = g._datammap
    g_data = list(g)
    ofile.close()
    nmap.close()
    return g_data
    
def uclass(iclass):
    '''
    Returns an iterator with the unsupervised data derived from 
    the exported ERDAS signature file for the selected uclass
    '''
    fullpath_filename= unicode('D:\My Docs\working\dat\exported_wroli_49c_clean.dat') 
    ofile = open(fullpath_filename, 'r')
       
    newStart = iclass
    newEnd = newStart+1
    g = Generator_Profiles(ofile)
    '''The nmap is used to close the call to datammap'''
    nmap = g._datammap
    g_data = islice(g, newStart, newEnd, 1)
    data = np.array(list(g_data))
    ofile.close()
    nmap.close()
    return data
# ---------------------------------------------------------------------------- #
nattributes = 6
nyears = 10
npoints =36
nclasses= 66

def data_by_year(_data, iyear):
    newStart = iyear*npoints
    newEnd = newStart+npoints
    return np.array( _data[slice(newStart, newEnd)])
    
def uc_stats(iclass):
    
    uc ={}
    
    data = uclass(iclass)
    print data
    yearData = data
    
        
    #array_min =  np.array([int(yearData[ipoint])  for ipoint in xrange(0, npoints*nattributes*nyears, nattributes)])
    #array_max = np.array([int(yearData[ipoint])  for ipoint in xrange(1, 1+npoints*nattributes*nyears, nattributes)])
    array_mean = np.array([float(yearData[ipoint]) for ipoint in xrange(2, 2+npoints*nattributes*nyears, nattributes)])
    #array_SD = np.array([float(yearData[ipoint]) for ipoint in xrange(3, 3+npoints*nattributes*nyears, nattributes)])
    #array_LL = np.array([int(yearData[ipoint]) for ipoint in xrange(4, 4+npoints*nattributes*nyears, nattributes)])
    #array_HL = np.array([int(yearData[ipoint]) for ipoint in xrange(5, 5+npoints*nattributes*nyears, nattributes)])
    idx_mean =np.array([ipoint for ipoint in xrange(2, 2+npoints*nattributes*nyears, nattributes)])
    
    
    '''Transposing the array facilitates the calculation of mean values for each points in time'''
    '''min curve'''
   # _min =np.array([data_by_year(array_min, iyear) for iyear in xrange(nyears)]).T
  # __min = np.array(map(np.mean, _min))
    '''max curve'''
  #  _max =np.array([data_by_year(array_max, iyear) for iyear in xrange(nyears)]).T
   # __max = np.array(map(np.mean, _max))
    '''average curve'''
    _mean =np.array([data_by_year(array_mean, iyear) for iyear in xrange(nyears)]).T
    __mean = np.array(map(np.mean, _mean))
    '''SD curve'''
    #_SD =np.array([data_by_year(array_SD, iyear) for iyear in xrange(nyears)]).T
    #__SD = np.array(map(np.mean, _SD))   
    '''LL curve'''
    #_LL =np.array([data_by_year(array_LL, iyear) for iyear in xrange(nyears)]).T
    #__LL = np.array(map(np.mean, _LL))   
    '''HL curve'''
    #_HL =np.array([data_by_year(array_HL,  iyear) for iyear in xrange(nyears)]).T
    #__HL = np.array(map(np.mean, _HL))
    
    #uc['count']= pixel_count
    #uc['min'] = __min
    #uc['max'] = __max
    uc['mean']= __mean
   # uc['SD']= __SD
   # uc['LL']= __LL
  #  uc['HL']= __HL
    
    '''Reference data which match the table structure of the exported ERDAS signature file'''
    '''NOTE. After trying I discovered that we cannot modify and fake an ERDAS signature file
    so I move to ENVI and use the Spectral Library Builder
    ref_data = np.array(zip(uc['min'], uc['max'], uc['mean'], uc['SD'], uc['LL'],uc['HL'] )).ravel()
    library = 'class %d, %d'%(iclass,int(uc['count']))
    for idata in ref_data:
        library = library+', %.4f'%idata
    '''
    
    return uc['mean']#library

def spectral_library():
    labels = get_labels()
    '''Year-based spectral ibrary'''
    #ref = np.array([uc_stats(iclass)  for iclass in xrange(nclasses)])
    for iclass in xrange(nclasses):
        ref =uc_stats(iclass)
        filename = r'D:\My Docs\working\spectral_library\wroli' + '\\'+labels[iclass]+'.dpt'
        ofile = open(filename,  'w')
        for ipoint in xrange(36):
            ofile.writelines('%d %.4f'%(ipoint+1, ref[ipoint]))
            ofile.writelines(' \n')
        ofile.close()
    '''
    for iclass in ref:
        ofile.writelines(iclass)        
        ofile.writelines(' \n')
    '''
    
    print 'done'
    return ref
    
