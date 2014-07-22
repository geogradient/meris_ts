#!/usr/bin/env python
__author__ = "Jose M. Beltran <gemtoolbox@gmail.com>"

import os, sys, mmap
import numpy as np
from string import strip,  split

# ---------------------------------------------------------------------------- #
nyears = 10
nclasses= 54
npoints = 36
# ---------------------------------------------------------------------------- #

def data_by_year(_data, iyear):
    newStart = iyear*npoints
    newEnd = newStart+npoints
    return np.array( _data[slice(newStart, newEnd)])

def read_uc_data_means(fullpath_filename= r'D:\My Docs\working\dat\multispec\uc54_means.dat') :
    ofile = open(fullpath_filename, 'r')
    data =np.fromfile(ofile, dtype=float, count=-1, sep='\t').reshape(54, 364)
    ofile.close()
    uc_labels = data[:, 0]
    uc_pixels = data[:, 1]
    uc_percentage = data[:, 2]
    uc_hectares = data[:, 3]
    uc_means = data[:, 4:364]
    return uc_means

def read_uc_data_sd(fullpath_filename= r'D:\My Docs\working\dat\multispec\uc54_sd.dat') :
    ofile = open(fullpath_filename, 'r')
    data =np.fromfile(ofile, dtype=float, count=-1, sep='\t').reshape(54, 361)
    ofile.close()
    uc_labels = data[:, 0]
    uc_sd= data[:, 1:361]
    return uc_sd

def uc_by_year():
    data = read_uc_data_means()
    ndata =[]
    for iclass in xrange(nclasses):
        cdata = data[iclass, :]
        ndata.append([data_by_year(cdata, iyear) for iyear in xrange(nyears)])
    ndata=np.array(ndata)
    return ndata

def read_uc20(filename=r'D:\My Docs\working\dat\multispec\uc_20c_means.dat'):
    ofile = open(fullpath_filename, 'r')
    data =np.fromfile(ofile, dtype=float, count=-1, sep='\t').reshape(54, 361)
    infile.close()
    '''
    for iclass in xrange(nclasses):
        ref =data[iclass, 1:]
        outfilename = r'D:\My Docs\working\spectral_library\multispec' + '\\' +str(iclass).zfill(2)+'.dpt'
        ofile = open(outfilename,  'w')
        for ipoint in xrange(len(ref)):
            ofile.writelines('%d %.4f'%(ipoint+1, ref[ipoint]))
            ofile.writelines(' \n')
        ofile.close()
    
    print 'done'
    '''
    return data



def save_uc_means_by_year(filename=r'D:\My Docs\working\dat\multispec\uc_yearly_means.dat'):
    data = uc_by_year()
    ofile = open(filename,  'w')
    for iclass in xrange(nclasses):
        for iyear in xrange(nyears):
            ofile.writelines('class_'+str(iclass).zfill(2)+'_y'+str(iyear).zfill(2))
            for ipoint in xrange(npoints):
                ofile.writelines(' %.4f'%data[iclass, iyear, ipoint])
            ofile.writelines('\n')
    
    ofile.close()
    print 'done'

def save_uc_ymeans_by_class(filename=r'D:\My Docs\working\dat\multispec\uc_ymeans.dat'):
    data = uc_by_year()
    ofile = open(filename,  'w')
    for iyear in xrange(nyears):
        for iclass in xrange(nclasses):
            ofile.writelines('class_'+str(iclass).zfill(2)+'_y'+str(iyear).zfill(2))
            for ipoint in xrange(npoints):
                ofile.writelines(' %.4f'%data[iclass, iyear, ipoint])
            ofile.writelines('\n')
    
    ofile.close()
    print 'done'

   

def means_of_years():
    data=uc_by_year()
    means=[]
    for iclass in xrange(nclasses):
        ndata=data[iclass, :, :].T
        means.append(map(np.mean, ndata))
    return np.array(means)

def sd_of_years():
    data=uc_by_year()
    sd=[]
    for iclass in xrange(nclasses):
        ndata=data[iclass, :, :].T
        sd.append(map(np.std, ndata))
    return np.array(sd)

def save_uc_means_of_years(filename=r'D:\My Docs\working\dat\multispec\uc_means.dat'):
    data = means_of_years()
    ofile = open(filename,  'w')
    for iclass in xrange(nclasses):
        ofile.writelines('class_'+str(iclass).zfill(2))
        for ipoint in xrange(npoints):
            ofile.writelines(' %.4f'%data[iclass, ipoint])
        ofile.writelines('\n')
    
    ofile.close()
    print 'done'

def save_uc_sd_of_years(filename=r'D:\My Docs\working\dat\multispec\uc_sd.dat'):
    data = sd_of_years()
    ofile = open(filename,  'w')
    for iclass in xrange(nclasses):
        ofile.writelines('class_'+str(iclass).zfill(2))
        for ipoint in xrange(npoints):
            ofile.writelines(' %.4f'%data[iclass, ipoint])
        ofile.writelines('\n')
    
    ofile.close()
    print 'done'

def combination(nc, data=None):
    ''' Generates a list of unique pair combinations on the given list.
   and returns an unique tuple of (row,col) '''
    idx =[]
    i=0
    index = range(0, nc )
    for each in xrange(len(index)):
        dat = []
        for left in index:
            idx.append((each,left))
            i+=1
        current = index.pop(0)
        
    return idx

def ki(vclass=0, wclass=0):
    
    mean_data = means_of_years() #[class,points]
    sd_data = sd_of_years()#[class,points]
    
    sd1 =sd_data[vclass, :]
    sd2 =sd_data[wclass, :]
    
    avg1=mean_data[vclass, :]
    avg2=mean_data[wclass, :]
       
    up1 = avg1+sd1
    up2 = avg2+sd2
        
    low1 = avg1-sd1
    low2 = avg2-sd2
        
    lengths1 = up1 - low1
    lengths2 = up2 - low2
    halfs1= lengths1/2.0
    halfs2 = lengths2/2.0
    
    ups = np.array([min(up1[ipoint], up2[ipoint]) for ipoint in xrange(len(up1))])
    lows = np.array([max(low1[ipoint], low2[ipoint]) for ipoint in xrange(len(up1))])
    
    overlap =[]
    
    for ipoint in xrange(len(up1)):
        if lows[ipoint] >= ups[ipoint]:
            overlap.append(0)
        else:
            overlap.append(ups[ipoint]-lows[ipoint])
    
    overlap = np.array(overlap)
    
    # Using the inverse of distance
    #weight = np.array([1/np.sqrt(((halfs1[ipoint])**2) + ((halfs2[ipoint])**2)) for ipoint in xrange(len(up1))])
    # Using the Inverse of the squared distance
    #KEES SUGGESTION--->SQR( [dev1^2 + dev2^2] /2 ) 
    
    weight = np.array([1/((halfs1[ipoint])**2 + ((halfs2[ipoint])**2)) for ipoint in xrange(len(up1))])
    
    
    wloverlap = (weight*(overlap)**2)/2
    kIndex= wloverlap.sum()/(npoints)
    
   
    return kIndex

def save_ki(filename=r'D:\My Docs\working\dat\ki_20090201.dat'):
    ofile = open(filename,  'w')
    idx = set(combination(nclasses))
    for row in xrange(nclasses):
        for col in xrange(nclasses):
            index = (row, col)
            cond = index in idx
            if cond:
                kees = '%.2f, '%ki(row, col)                
            else:
                kees = '-9999, '
            ofile.writelines(kees)        
        ofile.writelines(' \n')
    ofile.close()
    print 'done'

def spectral_library01():
       
    '''Year-based spectral ibrary'''
    data = means_of_years()
    for iclass in xrange(nclasses):
        ref =data[iclass, :]
        filename = r'D:\My Docs\working\spectral_library\multispec' + '\\' +str(iclass).zfill(2)+'.dpt'
        ofile = open(filename,  'w')
        for ipoint in xrange(len(ref)):
            ofile.writelines('%d %.4f'%(ipoint+1, ref[ipoint]))
            ofile.writelines(' \n')
        ofile.close()
    
    print 'done'

def spectral_library02():
       
    '''Class-based spectral ibrary'''
    data = data = uc_by_year() #[iclass,iyears,ipoint]
    for iyear in xrange(nyears):
        for iclass in xrange(nclasses):
                
            ref =data[iclass,iyear,  :]
            filename = r'D:\My Docs\working\spectral_library\multispec\byuc' + '\\'+'y'+str(iyear).zfill(2)+'_uc'+str(iclass).zfill(2)+'.dpt'
            ofile = open(filename,  'w')
            
            for ipoint in xrange(len(ref)):
                ofile.writelines('%d %.4f'%(ipoint+1, ref[ipoint]))
                ofile.writelines(' \n')
            ofile.close()
        
    print 'done'

# ---------------------------------------------------------------------------- #
