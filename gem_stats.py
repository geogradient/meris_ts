#!/usr/bin/env python
__author__ = "Jose M. Beltran <gemtoolbox@gmail.com>"
__version__ = "0.1.1"

'''
Version 1.0 (Jan09,2009) [Moved similarity class from module gemv3.1]:
    Assess similarity between two numpy vectors(v and w) includes:
    >>> spectral_angle()
    >>> bray_curtis_distance()
    >>> euclidian_distance()
    >>> intensity_difference()
    >>> jaccards_coeficient()
    >>> mann_whitney()
    >>> kolmogorov_smirnov()
    
Version 1.1 (Jan 09,2009)

Updated: JAN 09, 2009
'''

__author__ = "Jose M. Beltran <gemtoolbox@gmail.com>"
__version__ = "0.1.0.0"

import numpy as np
import scipy.stats as stats#itemfreq
'''GEM statistics'''
import math
    
class Frequency(object):
    '''Requires an 2D-array with shape (nyears,pointValuesInYear)'''
    def __init__(self, array, stop=36):
        self.array = array
        self.stop = stop   
    def _freq(self):
        freqList = []
        stdList = []
        for element in xrange(self.array.shape[0]):
            std = self.array[element, 0:self.stop].std()
            stdList.append(int(round(std, 0)))
        
        return stats.itemfreq(np.array(stdList))
    
    freq = property(fget = _freq)


class Similarity(object):
    ''' Vectors v and w should be numpy arrays.'''
    def __init__(self,v=None,w=None):
        '''
        if v==None and w==None:
            print '-----------------------------------------------------------'
            print 'WARNING: Do not forget to set first the attribute values of'
            print '         vectors "v" and "w" for the instance.'
            print 'e.g.: my_instance.v = numpy array ([1,2,3])'
            print '      my_instance.w = numpy array ([2,3,4])'
            print '-----------------------------------------------------------'
            pass
        '''
        
        self.v = v
        self.w = w
        pass
    def spectral_angle(self):
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
            return math.acos(np.dot(self.v, self.w) / np.sqrt(np.dot(self.v, self.v)) / np.sqrt(np.dot(self.w, self.w)))
        except:
            return 0.0

    def bray_curtis_distance(self):
        ''' 
        Output ranges between [0:1] if all values are positive.
        Zero represent exact similar coordinates.
        A value close to zero means "very similar", large values mean "very distinct" 
        Coded by: Wim H. Bakker -ITC
        '''
        try:
            return sum(abs(self.v-self.w)) / (sum(self.v) + sum(self.w))
        except:
            return False # 0.0
    
    def euclidian_distance(self):
        '''
        A value close to zero means "very similar", large values mean "very distinct"
        Source: Bakker and Schmidt (2002)
        '''
        try:
            return np.sqrt(sum((self.v-self.w)**2))
        except:
            return False

    def intensity_difference(self):
        '''
        A value close to zero means "very similar", large values mean "very distinct"
        Source: Bakker and Schmidt (2002)
        '''
        try:
            return abs(sum(abs(self.v))-sum(abs(self.w)))
        except:
            return False
    
    def jaccards_coeficient(self):
        '''
        Measures similarity. Ranges from [0:1]
        A value close to one means "very similar", low values mean "very distinct"
        Source: Teknomo (2006)
        '''
        try:
            # Gives the number of elements without repetition
            n_elements_in_union = len(set(self.v)|set(self.w)) # Union
            n_elements_in_intersection = len (set(self.v) & set(self.w)) # Intersect
            return n_elements_in_intersection / float(n_elements_in_union)  
        except:
            return False
        
    def mann_whitney(self):
        '''
        Returns the mann_whitney u statistic for two tails
        if two_tailed_pvale (or one tail pvalue) < significance_level_p
        then REJECT Ho-THERE ARE DIFFERENCES
        '''
        #from scipy.stats import kruskal
        from scipy.stats import mannwhitneyu
        U_statistic, one_tailed_pvalue = mannwhitneyu(self.v,self.w)
        return U_statistic,one_tailed_pvalue*2
    
    def kolmogorov_smirnov(self):
        '''
        The test uses the two-sided asymptotic Kolmogorov-Smirnov distribution.
        The distribution is assumed to be continuous.
        If the K-S statistic is small or the p-value is high, then we cannot
        reject the null hypothesis. 
        '''
        from scipy.stats import ks_2samp
        D_statistic, two_tailed_pvalue = ks_2samp(self.v,self.w)
        return D_statistic,two_tailed_pvalue
 
