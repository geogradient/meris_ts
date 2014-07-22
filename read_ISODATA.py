#!/usr/bin/env python
__author__ = "Jose M. Beltran <gemtoolbox@gmail.com>"

import os, sys, mmap
import numpy as np
from string import strip,  split
from scipy.stats import mannwhitneyu
from scipy.stats import ks_2samp

# ---------------------------------------------------------------------------- #
nyears = 10
nclasses= 56
nref = 56
#npoints = 20
npoints = 20

mean_attr=4 # xtra attributes before data begins in means data file
std_attr = 1 # xtra attributes before data begins in standard deviations data file
nattr1 = npoints*nyears+mean_attr
nattr2 =  npoints*nyears+std_attr
# ---------------------------------------------------------------------------- #
#in_means_filename=r'D:\My Docs\working\in_images\ISODATA\ISODATA_56c_means.txt'# <-- only 20p
in_means_filename=r'D:\My Docs\working\dat\multispec\uc_yearly_means.dat' # <-- 36 p
in_std_filename=r'D:\My Docs\working\in_images\ISODATA\ISODATA_56c_std.txt'
out_means_filename = r'D:\My Docs\working\in_images\ISODATA\ISODATA_56c_class_means.txt'
out_std_filename=r'D:\My Docs\working\in_images\ISODATA\ISODATA_56c_class_sd.txt'

# ---------------------------------------------------------------------------- #
anomalous_years =[]
spectra={}
# ---------------------------------------------------------------------------- #
def data_by_year(_data, iyear):
    newStart = iyear*npoints
    newEnd = newStart+npoints
    return np.array( _data[slice(newStart, newEnd)])


def data_means(filename=in_means_filename):
    ofile = open(filename, 'r')
    data =np.fromfile(ofile, dtype=float, count=-1, sep='\t').reshape(nclasses, nattr1)
    ofile.close()
    uc_labels = data[:, 0]
    uc_pixels = data[:, 1]
    uc_percentage = data[:, 2]
    uc_hectares = data[:, 3]
    uc_means = data[:, 4:nattr1]
    return uc_means

def data_sd(filename= in_std_filename) :
    ofile = open(filename, 'r')
    data =np.fromfile(ofile, dtype=float, count=-1, sep='\t').reshape(nclasses,  nattr2)
    ofile.close()
    uc_labels = data[:, 0]
    uc_sd= data[:, 1:nattr2]
    return uc_sd

def arrange_means_by_year():
    data = data_means()
    ndata =[]
    for iclass in xrange(nclasses):
        cdata = data[iclass, :]
        ndata.append([data_by_year(cdata, iyear) for iyear in xrange(nyears)])
    ndata=np.array(ndata)
    return ndata

def arrange_sd_by_year():
    data = data_sd()
    ndata =[]
    for iclass in xrange(nclasses):
        cdata = data[iclass, :]
        ndata.append([data_by_year(cdata, iyear) for iyear in xrange(nyears)])
    ndata=np.array(ndata)
    return ndata


def save_data_by_year(data=arrange_means_by_year(), filename=r'D:\My Docs\working\dat\isodata_56c_by_full_year.txt'):
    
    ofile = open(filename,  'w')
    for iclass in xrange(nclasses):
        for iyear in xrange(nyears):
            ofile.writelines('class_'+str(iclass).zfill(2)+'_y'+str(iyear).zfill(2))
            for ipoint in xrange(npoints):
                ofile.writelines(' %.2f'%data[iclass, iyear, ipoint])
            ofile.writelines('\n')
    
    ofile.close()
    print 'done'

def save_data_by_class(data=arrange_means_by_year(), filename=r'D:\My Docs\working\dat\isodata\isodata_56c_by_class.dat'):
    ofile = open(filename,  'w')
    for iyear in xrange(nyears):
        for iclass in xrange(nclasses):
            ofile.writelines('class_'+str(iclass).zfill(2)+'_y'+str(iyear).zfill(2))
            for ipoint in xrange(npoints):
                ofile.writelines(' %.2f'%data[iclass, iyear, ipoint])
            ofile.writelines('\n')
    
    ofile.close()
    print 'done'

def reduce_years_to_mean_class(data=arrange_means_by_year()):
    means=[]
    for iclass in xrange(nclasses):
        ndata=data[iclass, :, :].T
        means.append(map(np.mean, ndata))
    return np.array(means)

def draw_year(iclass, yeartodraw, data=arrange_means_by_year()):
    ''' returns an array of nyears minus the array of yeartodraw '''
    reduced =[]
    index = set(xrange(nyears))
    index.remove(yeartodraw)
    for idx in index:
        reduced.append(data[iclass, idx, :])
    reduced = np.array(reduced).T
    rmean= map(np.mean, reduced)
    rmean=np.array(rmean)
    
    return rmean
 
    
'''<<<------ CHECK ME ------>>>
def reduce_years_to_sd_class(data=arrange_sd_by_year()):
    sd=[]
    for iclass in xrange(nclasses):
        ndata=data[iclass, :, :].T
        sd.append(map(np.std, ndata))
    return np.array(sd)'''

def save_means_of_class(data =reduce_years_to_mean_class(), filename=out_means_filename):
    
    ofile = open(filename,  'w')
    for iclass in xrange(nclasses):
        ofile.writelines('class_'+str(iclass).zfill(2))
        for ipoint in xrange(npoints):
            ofile.writelines(' %.2f'%data[iclass, ipoint])
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

def spectral_library01(data = reduce_years_to_mean_class()):
       
    '''Year-based spectral ibrary'''
    
    for iclass in xrange(nclasses):
        ref =data[iclass, :]
        filename = r'D:\My Docs\working\spectral_library\isodata' + '\\' +'ref'+str(iclass+1).zfill(2)+'.dpt'
        ofile = open(filename,  'w')
        for ipoint in xrange(len(ref)):
            ofile.writelines('%d %.2f'%(ipoint+1, ref[ipoint]))
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
def mann_whitney(v, w):
        '''
        Calculates a Mann-Whitney U statistic on the provided scores and
        returns the result.  
        Use only when the n in each condition is < 20 and 
        you have 2 independent samples of ranks.  
        REMEMBER: Mann-Whitney U is significant 
        One tail: if the u-obtained is LESS THAN or equal to the critical value of U.
        Two tail: One tail or Ucalc greater than m*n - u [Prob of u with alpha/2]
        
        Ho: There is no difference. Any observed differences are due to chance.
        The two populations follow the same distribution.
        H1: There are significant differences between the two populations thus
        not due to chance.
    
        Returns: u-statistic, one-tailed p-value (i.e., p(z(U)))
    
        Returns the mann_whitney u statistic for two tails
        if two_tailed_pvale (or one tail pvalue) < significance_level_p
        then REJECT Ho-THERE ARE DIFFERENCES
        '''
        U_statistic, one_tailed_pvalue = mannwhitneyu(v,w)
        return U_statistic,one_tailed_pvalue



def MWU_year_to_year_test(year1=0, year2=0):
    '''
    Test whether a particular year in an unsupervised class  set is similar 
    to elements of the set using the Mann-Whitnet U-test.
    '''
    # From Milton (1964) An Extended table of critical values for the MW two sample
    u_tables20m20n ={'0.0005':81, '0.005':105, '0.0025':97, '0.001':88, '0.01':114,  '0.025':127,  '0.05':138, '0.1': 151}
    
    m=20
    n= 20
    mn=m*n
    alpha_one_tail = '0.1'
    alpha_two_tails = '0.05'
    # Using two tails
    
    u_two_tails = u_tables20m20n[alpha_two_tails]
    u_one_tail =  u_tables20m20n[alpha_one_tail]
        
    #U_calc, p_mann_one_tail = mann_whitney(avg, y)
    if (year1==year1[0]).all() or (year2==year2[0]).all():
        hypothesis=0 #All numbers are equal-chasing zeros
    else:
        
        U_calc, p_mann_one_tail = mann_whitney(year1, year2)
        
        if (U_calc >= mn-u_two_tails) or (U_calc < u_one_tail):
            hypothesis= 0#'Accept Ho'
        else:
            hypothesis = 1#'Reject Ho'
         
        #u_tuple =(U_calc, u_one_tail, u_two_tails)
        #two_tailed_pvalue = p_mann_one_tail*2
    
        
    return hypothesis
    
def MWU_years_to_mean_similarities_in_class(iclass):
    similarities =[]
    # Test among all years in particular class for similarity against the mean values of the class
    # while drawing one year at time for new mean calculation
    # Mann-Whitnet U-test.
    #ypairs = list(combination(nyears))
    meansdata =reduce_years_to_mean_class() 
    for iyear in xrange(nyears):
        #year1 = draw_year(iclass, iyear)
        year1 = meansdata[iclass]
        year2 = data[iclass, iyear, :]
        similarities.append(MWU_year_to_year_test(year1, year2))
    similarities=np.array(similarities)
    return similarities

def reference_spectrum(iclass, similars=None):
    if similars==None:
        similars = MWU_years_to_mean_similarities_in_class(iclass)
        
    select_similar = np.where(similars==0)
    
    spectrum= [data[iclass, iyear] for iyear in select_similar]
    spectrum = np.array(spectrum).T
    spectrum_mean = np.array(map(np.mean, spectrum))
    if similars==None:
        label = 'ref_'+str(iclass).zfill(3)
    else:
        nref+=1
        label = 'ref_'+str(nref).zfill(3)
        
    spectra[label]= spectrum_mean
    return select_similar#spectrum_mean

def reference_spectra():
    [reference_spectrum(iclass) for iclass in xrange(nclasses)]
    
def anomalies(iclass, similars=None):
    if similars==None:
        similars = MWU_years_to_mean_similarities_in_class(iclass)
    select_anomalies = np.where(similars==1)
    nano=select_anomalies[0].shape[0]
    pairs = list(combination(nano))
    
    nano_list= list(select_anomalies[0])
    
    idx =[]
    
    index = nano_list[:]
    for each in xrange(len(index)):
        current = index.pop(0)
        for left in index:
            y1=data[iclass, nano_list[each]]
            y2=data[iclass, left]
            #idx.append([(nano_list[each], left), MWU_year_to_year_test(y1, y2)])
            idx.append(MWU_year_to_year_test(y1, y2))
    idx=np.array(idx)
    select_similar = np.where(idx==0)
    
    spectrum= [data[iclass, iyear] for iyear in select_similar]
    
    return np.array(idx)
    

def MWU_year_to_year_similarities_in_class(iclass):
    similarities =[]
    # Test among all years in particular class for similarity using the
    # Mann-Whitnet U-test.
    ypairs = list(combination(nyears))
       
    for idx in xrange(len(ypairs)):
        
        year1 = data[iclass, ypairs[idx][0], :]
        year2= data[iclass, ypairs[idx][1], :]
        similarities.append(MWU_year_to_year_test(year1, year2))
    similarities=np.array(similarities)
    return similarities


def save_MWU_years_similarities_in_class(iclass):
    
    filename =r'D:\My Docs\working\dat\isodata\mwu_sim_class_'+str(iclass+1).zfill(2)+'.txt'
    
    ofile = open(filename,  'w')
    idx = set(combination(nyears))
    sims= MWU_years_similarities_in_class(iclass)
    i=0
    for row in xrange(nyears):
        for col in xrange(nyears):
            index = (row, col)
            cond = index in idx
            if cond:
                #sim_ = '(%d,%d):%d; '%(row, col, sims[i])
                sim_ = '%d; '%sims[i]
                i+=1
            else:
                sim_ = '-9; '
            
            ofile.writelines(sim_)        
        ofile.writelines(' \n')
    ofile.close()
    print 'done'

# ---------------------------------------------------------------------------- #
data=arrange_means_by_year()


#MWU_year_to_year_test(year1, year2)
