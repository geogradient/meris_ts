import os, sys, mmap
import numpy as np
from string import strip
import scipy.stats as stats
import math
from itertools import islice, imap, chain, ifilter
from shapely.geometry import LineString
from scipy.stats import mannwhitneyu
from scipy.stats import ks_2samp
from decimal import Decimal as decimal
'''
abbrevations:
uc --> unsupervised class
'''
lockData = False
lockAtIndex = 20
nPoints = 36
nclasses=87
nyears = 10
anomalous_years = []


def timePoint(ipoint):
    month = ['APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP',\
                       'OCT', 'NOV', 'DEC',  'JAN', 'FEB', 'MAR']
    synthesisDay = frozenset([1, 11, 21])
    dayInTime =[('%s '%iday)+imonth for imonth in month for iday in synthesisDay]
    
    return dayInTime[ipoint]

class Generator_Profiles:
    def __init__(self, ofile):
        self._datammap = mmap.mmap(ofile.fileno(),0, access=mmap.ACCESS_READ)
        
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
# ---------------------------------------------------------------------------- #
''' Useful functions '''
def combination(nc, data=None):
    ''' Generates a list of unique pair combinations on the given list.
   and returns an unique tuple of (row,col) '''
    idx =[]
    i=0
    index = range(0, nc )
    for each in xrange(len(index)):
        #current = index.pop(0)
        dat = []
        for left in index:
            idx.append((each,left))
            #value= data[i]
            #dat.append('%.2f, '%data[i])
            i+=1
        current = index.pop(0)
        #dat.append('\n')
 
    return idx
# ---------------------------------------------------------------------------- #
''' Data creators '''
def uclass(iclass, nyears=10):
        '''
        Returns an iterator of the year-profiles of the selected class
        '''
        newStart = iclass*nyears
        newEnd = newStart+nyears
        g = Generator_Profiles(ofile)
        nmap = g._datammap
        # The nmap is used to close the call to datammap
        return islice(g, newStart, newEnd, 1), nmap


def year(iclass, iyear):
    '''
    Returns the array of a year in a unsupervised class
    '''
    gen_data, nmap=uclass(iclass)
    if lockData:
        y = list(islice(gen_data, iyear, iyear+1, 1))
        y = np.array(y)
        y= y[0, 0:lockAtIndex]
    else:
        y = list(islice(gen_data, iyear, iyear+1, 1))
        y = np.array(y)
        y= y[0, 0:nPoints]
    return y
    
def dataT(iclass, yeartodraw=None,  reuse=True):
        '''
        Returns the data as an transpose sliced array which
        faciliates computation of descriptive stats and optionally 
        pop out the yeartodraw to meet indepent samples
        '''
        gen_data, nmap=uclass(iclass)
        data_list= list(gen_data)
        if yeartodraw is not None:
            data_list.pop(yeartodraw)
        s = data_list[0: nPoints]
        s = np.array(s).T
        nmap.close()
        return s
# ---------------------------------------------------------------------------- #
''' Descriptive statitics '''
def average( iclass,  yeartodraw=None):
    '''calculates the mean of a point in all years'''
    
    aT = dataT(iclass, yeartodraw)
    avg = np.array(map(np.mean, aT))
    if lockData:
        return avg[0:lockAtIndex]
    else:
        return avg
   
def SD( iclass, yeartodraw=None):
    '''calculates the SD of a point in all years'''
    aT = dataT(iclass, yeartodraw)
    sd = np.array(map(np.std, aT))
    if lockData:
        return sd[0:lockAtIndex]
    else:
        return sd
    
    
def upperSD( iclass):
    '''calculates the upper- SD limit of a point in all years'''
    point_avg = average(iclass)
    point_sd = SD(iclass)
    return  point_avg + point_sd

def lowerSD( iclass):
    '''calculates the lower- SD limit of a point in all years'''
    point_avg = average(iclass)
    point_sd = SD(iclass)
    return  point_avg - point_sd




# ---------------------------------------------------------------------------- #
'''Similarity measures'''
def spectral_angle(v, w):
        '''
        The spectral angle is expressed in radians.
        The value should be between [0:pi/4], but typically much lower if the bands are highly correlated.
        A value close to zero means "very similar", large values mean "very distinct" 
        From Bakker and Schimdt (2002): 
        "The cosine of the spectral angle is equivalent to the correlation coefficient (Hadley, 1961), this means
        that the spectral angle (SA) is a statistical method for expressing similarity or dissimilarity between
        two pixel vectors".

        Coded by: Wim H. Bakker -ITC
        '''
        try:
            return math.acos(np.dot(v, w) / np.sqrt(np.dot(v, v)) / np.sqrt(np.dot(w, w)))
        except:
            return 0.0


def euclidian_distance(v, w):
    '''
    A value close to zero means "very similar", large values mean "very distinct"
    Source: Bakker and Schmidt (2002)
    '''
    try:
        return np.sqrt(sum((v - w)**2))
    except:
        return False

def intensity_difference(v, w):
    '''
    A value close to zero means "very similar", large values mean "very distinct"
    Source: Bakker and Schmidt (2002)
    '''
    try:
        return abs(sum(abs(v))-sum(abs(w)))
    except:
        return False
        
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
        return U_statistic,one_tailed_pvalue*2
def jaccards_coeficient(v, w):
        '''
        Measures similarity. Ranges from [0:1]
        A value close to one means "very similar", low values mean "very distinct"
        Source: Teknomo (2006)
        '''
        try:
            # Gives the number of elements without repetition
            n_elements_in_union = len(set(v)|set(w)) # Union
            n_elements_in_intersection = len (set(v) & set(w)) # Intersect
            return n_elements_in_intersection / float(n_elements_in_union)  
        except:
            return -9999
# ---------------------------------------------------------------------------- #
def MWU_test_yearBelongToClass(iclass, iyear):
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
    
    avg = average(iclass, yeartodraw=iyear)
    
    y = year(iclass,iyear)
    
    U_calc, p_mann_one_tail = mann_whitney(avg, y)
        
    if (U_calc >= mn-u_two_tails) or (U_calc < u_one_tail):
        hypothesis= 0#'Accept Ho'
    else:
        hypothesis = 1#'Reject Ho'
     
    u_tuple =(U_calc, u_one_tail, u_two_tails)
    two_tailed_pvalue = p_mann_one_tail*2
    
    if hypothesis==1:
        anomalous_years.append((iclass, iyear))
    return '%d '%hypothesis
    
def MWU_test_similarYearsInClass(iclass):
    '''
    Test among all years in particular class for similarity using the
    Mann-Whitnet U-test.
    '''
    similatities = [MWU_test_yearBelongToClass(iclass, iyear) for iyear in xrange(nyears)]
    return similatities
def MWU_test_allUClasses():
    if lockData:
        ofile = open(r'D:\My Docs\working\dat\MWU_20p_yearly.dat', 'w')
    else:
        ofile = open(r'D:\My Docs\working\dat\MWU_36p_yearly.dat', 'w')
    for iclass in xrange(nclasses):
        simUCs = MWU_test_similarYearsInClass(iclass)
        ofile.writelines(simUCs)
        ofile.writelines(' \n')
    ofile.close()
    print 'done'
    
def MWC_similarUC():
    if lockData:
        ofile = open(r'D:\My Docs\working\dat\simUC_20p_MWU.dat', 'w')
    else:
        ofile = open(r'D:\My Docs\working\dat\simUC_36p_MWU.dat', 'w')
    
    idx = set(combination(nclasses))
      
    for row in xrange(nclasses):
        for col in xrange(nclasses):
            index = (row, col)
            cond = index in idx
            if cond:
                MWC = '%.2f, '%kees_Index(row, col)                
            else:
                MWC = '-9999, '
            ofile.writelines(MWC)        
        ofile.writelines(' \n')
    ofile.close()
    print 'done'
    
def ED_test_yearBelongToClass(iclass, iyear):
    '''
    Test whether a particular year in an unsupervised class  set is similar 
    to elements of the set using the Bray-Curtis-Distance.
    '''
    avg = average(iclass, yeartodraw=iyear)
    y = year(iclass,iyear)
    _SA = spectral_angle(avg,y)
    _CC= math.cos(_SA)
    _ED = euclidian_distance(avg, y)
    _ID = intensity_difference(avg, y)
    
    SA = '%.2f'%_SA
    CC= '%.2f'%_CC
    ED = '%.2f'%_ED
    ID = '%.2f'%_ID
        
    if (CC >=0.95):
        hypothesis= 0#'Accept Ho'
    else:
        hypothesis = 1#'Reject Ho
    
    if hypothesis==1:
        anomalous_years.append((iclass, iyear))
    return CC
    #return SA,CC,  ED, ID, hypothesis
    
def ED_test_similarYearsInClass(iclass):
    '''
    Test among all years in particular class for similarity Bray-Curtis-Distance
    '''
    similatities = [ED_test_yearBelongToClass(iclass, iyear) for iyear in xrange(nyears)]
    return similatities

def ED_test_similarityAllClasses():
    if lockData:
        ofile = open(r'D:\My Docs\working\dat\ED_20p_yearly.dat', 'w')
    else:
        ofile = open(r'D:\My Docs\working\dat\ED_36p_yearly.dat', 'w')
    for iclass in xrange(nclasses):
        sim_in_uc = ED_test_similarYearsInClass(iclass)
        ofile.writelines(str(sim_in_uc))
        ofile.writelines(' \n')
    ofile.close()
    print 'done'

def roundFixed(value):
    return '%.1f'%value
    
def JC_test_yearBelongToClass(iclass, iyear):
    '''
    Test whether a particular year in an unsupervised class  set is similar 
    to elements of the set using the Jackards Coefficient.
    Jackards coefficient returns [0:1] where 0 represent more similar. I used 
    1- jaccards_coeficient to get a porcentage of the similairity.
    '''
    _avg = average(iclass, yeartodraw=iyear)
    _y = year(iclass,iyear)
    
    avg = map(roundFixed, _avg)
    y = map(roundFixed, _y)
    
    JC = jaccards_coeficient(avg, y)
        
    return '%.2f'%(1-JC)
def JC_test_similarYearsInClass(iclass):
    '''
    Test among all years in particular class for similarity Bray-Curtis-Distance
    '''
    similatities = [JC_test_yearBelongToClass(iclass, iyear) for iyear in xrange(nyears)]
    return similatities
def JC_test_allUClasses():
    if lockData:
        ofile = open(r'D:\My Docs\working\dat\JC_20p_yearly.dat', 'w')
    else:
        ofile = open(r'D:\My Docs\working\dat\JC_36p_yearly.dat', 'w')
    for iclass in xrange(nclasses):
        sim_in_uc = JC_test_similarYearsInClass(iclass)
        ofile.writelines(str(sim_in_uc))
        ofile.writelines(' \n')
    ofile.close()
    print 'done'


def JC_half_SD(iclass):
    up = upperSD(iclass)
    low = lowerSD(iclass)
    lengths = up - low
    halfs= lengths/2.0
    return halfs

def JC_similarUC():
    if lockData:
        ofile = open(r'D:\My Docs\working\dat\simUC_20p_JC.dat', 'w')
    else:
        ofile = open(r'D:\My Docs\working\dat\simUC_36p_JC.dat', 'w')
    idx = set(combination(nclasses))
        
    for row in xrange(nclasses):
        for col in xrange(nclasses):
            index = (row, col)
            cond = index in idx
            if cond:
                JC_uc = '%.2f, '%jaccards_coeficient(JC_half_SD(row), JC_half_SD(col))                
            else:
                JC_uc = '-9999, '
            ofile.writelines(JC_uc)        
        ofile.writelines(' \n')
    ofile.close()
    print 'done'
# ---------------------------------------------------------------------------- #
def kees_Index(vclass, wclass):
    
    up1 = upperSD(vclass)
    up2 = upperSD(wclass)
    
    low1 = lowerSD(vclass)
    low2 = lowerSD(wclass)
        
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
    
    
    wloverlap = weight*(overlap)**2
    kIndex= wloverlap.sum()/(2*nPoints)
    kIndex = OVERsum/Dsum
   
    return kIndex

def kees_similarUC():
    if lockData:
        ofile = open(r'D:\My Docs\working\dat\simUC_20p_IDW.dat', 'w')
    else:
        ofile = open(r'D:\My Docs\working\dat\simUC_36p_IDW.dat', 'w')
    idx = set(combination(nclasses))
      
    for row in xrange(nclasses):
        for col in xrange(nclasses):
            index = (row, col)
            cond = index in idx
            if cond:
                kees = '%.2f, '%kees_Index(row, col)                
            else:
                kees = '-9999, '
            ofile.writelines(kees)        
        ofile.writelines(' \n')
    ofile.close()
    print 'done'

# ---------------------------------------------------------------------------- #
def wroli_similarUC():
    if lockData:
        ofile = open(r'D:\My Docs\working\dat\simUC_20p_WROLI.dat', 'w')
    else:
        ofile = open(r'D:\My Docs\working\dat\simUC_36p_WROLI.dat', 'w')
    idx = set(combination(nclasses))
      
    for row in xrange(nclasses):
        for col in xrange(nclasses):
            index = (row, col)
            cond = index in idx
            if cond:
                wroli = '%.2f, '%wroli_index(row, col)                
            else:
                wroli = '-9999, '
            ofile.writelines(wroli)        
        ofile.writelines(' \n')
    ofile.close()
    print 'done'
    
def wroli_index(vclass, wclass):
    #Weighted Ratio of Length of Intersections-#Beltran - de Bie index
        
    up1 = upperSD(vclass)
    up2 = upperSD(wclass)
    
    low1 = lowerSD(vclass)
    low2 = lowerSD(wclass)
        
    lengths1 = up1 - low1
    lengths2 = up2 - low2
                
    # DEBUGGING   lines0, lengths0, lines1, lengths1 = self.lines2()
    
    LO = lengths1
    LI = lengths2
    
    nvalues = len(LO)
    '''Intersections lengths for each point in time'''
    ups = np.array([min(up1[ipoint], up2[ipoint]) for ipoint in xrange(len(up1))])
    lows = np.array([max(low1[ipoint], low2[ipoint]) for ipoint in xrange(len(up1))])
    
    overlap = ups - lows
    LOVER=overlap  #Lines OVERlap
    '''Catching for equality regardless the difference in lengths'''
    if (LO==LI).all() and (LO==LOVER).all():
        WROLI = 1
    else:
           
        ZLOVER =[] # Catching when LOVER goes negative
        for ilover in LOVER:
            if ilover <= 0: 
                ZLOVER.append(0)
            else:
                ZLOVER.append(ilover)
        
        LOVER = np.array(ZLOVER)
        
        '''Sum of lengths in each point of time''' 
        LOLI = LO+LI
        '''maximum LOLI'''
        MAXLOLI = LOLI.max()
        '''minimum LOLI'''
        MINLOLI =  LOLI.min()
        
        '''Normalized LOLI'''
        NLOLI= (LOLI - MINLOLI)/ (MAXLOLI-MINLOLI) 
            
        '''Ratio of LOVER with LO'''
        LOVERO = LOVER/LO
        '''Ratio of LOVER with LI'''
        LOVERI = LOVER/LI
        '''Difference on LOVER ratios'''
        DLOVER = abs(LOVERO-LOVERI)
        '''Weigth due to DLOVER'''
        WDLOVER = 1 - DLOVER
        '''Weigth due to NLOLI'''
        WNLOLI = 1- NLOLI
        '''Weighted LOVER'''
        WLOVER = LOVER*WDLOVER*WNLOLI
            
        '''Sum of LOVER'''
        SLOVER = LOVER.sum()
        
        '''Sum of WLOVER'''
        SWLOVER = WLOVER.sum()
        
        ZLOVER = LOVER[LOVER==0]
        '''Count number of zero intersections'''
        SZLOVER = len(ZLOVER)
        '''Weight due to zero intersections'''
        WSZLOVER = (nvalues-SZLOVER) / float(nvalues)
        
        if SLOVER !=0:
            WROLI = (SWLOVER / SLOVER)*WSZLOVER
        else:
            WROLI = 0
      
        
    return WROLI
    
# ---------------------------------------------------------------------------- #


''' Main app
'''
fullpathfilename=r'D:\My Docs\working\dat\apxc087.txt'
ofile = open(fullpathfilename, 'r')

ReferenceSet = {}
ReferenceAnomalies = {}
Library ={}



