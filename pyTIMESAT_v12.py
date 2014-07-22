#! /usr/bin/env python
# from os import chdir; chdir('D://working'); execfile('pyTIMESAT_v11.py')
'''
pyTIMESAT --> TIMESAT implentation for python 2.5 
AUTHOR: Jose M. Beltran(gemtoolbox@gmail.com)
PURPOSE: Applies a modification of the adaptive Savitzky-Golay filter 
        following the TIMESAT v2.3 implementation with optional upper envelope 
        forcing. To be used with SPOT VEG NDVI 10-day synthesis. 
NOTE:    TIMESAT v2.3. A package for processing time-series of satellite sensor 
        data. 
         Authors: 
         Per Jonsson, Malmo University, Sweden, 
            e-mail per.jonsson@ts.mah.se
         Lars Eklundh, Lund University, Sweden, 
            e-mail lars.eklundh@nateko.lu.se )

REQUIRES: numpy, GDAL, Gnuplot, scipy, and GEMtoolBox
WARNING: Only complete yearly stack of images should be used as an input.
        e.g. 10 years, 9 years; but no 9 years with 8 months.

pyTIMESAT version log.
-----------------------------------------------------------------------         
Version 3. Changed the dtype of w to float to be float instead of uint8
        - Corrected element by element basic operations like A + B
Version 4. Changed dtype for y to float
        - Original vector y will be kept as it is. Any changes will occur on 
        a copy of it python do not create copies of vectors or matrices, 
        it will create a view of it when you assign B=A, B is a view of A, 
        so any changes in B will be reflected on A.
        I needed to have A without change. So I create B=A.copy().
Version 5. Ready to run without the debugging variables.
Version 6. Version 5 BUT DID NOT WORKED so I return to Version 4 and tried again
        Comments were added and plotting has been disabled.
Version 7. There was a bug in the assignment of wmatrix and w. wmatrix has been
    removed  and w is initialised every time for each column.
Version 8. Tried to reduce processing time.
        yearsInProfile function NOT in USE so it has been removed...
        getPixelProfile function NOT in USE so it has been removed...
        get3DFullProfiles function NOT in USE so it has been removed...
        return spikes in function spike has been removed
        plot capabilities had been removed
        weighting factor removed
        modweight function capabilities has been removed- This one was having 
        the problem with performance 
Version 9. Incorporates the GEMToolBox
Version 10. Version to perform the upper envelope on all the pixels and then 
    write the array.
        Should be used with small 3D arrays.
Version 11. User input window size array and plotting capabilities by pixel. 
    return spikes enabled.
Version 12. GEMtoolBox was replaced by the gem module. 
    Plotting capabilities were removed.
    Only spike and savgol functions were kept

Updated: Mar 26,2009
''' 

import numpy as np

from scipy import r_ as r_
from scipy import c_ as c_

# ---
def spike(y,w,spikecutoff = 0.5):
    ''' 
    A spikecutoff will be used as: spikecutoff * y[y>0].std(). A value of 2 is 
    the normal value  for TIMESAT. But in TIMESAT they used
    spikecutoff * y.std(). I suggest to use only the values of y>0 to 
    calculate the distance. A value lower than 1 will pick up more spikes.
    '''
    w0 = np.ravel(w.copy()) 
    # Preserving the old weight values. This could be done directly over w.
    spikes = np.zeros(nb)
    ymean = y[y>0].mean()
    ystd = y[y>0].std()
    wmax = w0.max()
    dist = spikecutoff*ystd
    swinmax = int(np.floor(nptperyear/7)) # 
    leftSlice = slice(nb-swinmax,nb)
    rightSlice = slice(0,swinmax)
    
    wext = np.ravel(r_[w0[leftSlice],w0,w0[rightSlice]])
    yext = np.ravel(r_[y[leftSlice],y,y[rightSlice]])
    # find single spikes and set weights to zero
    for i in range(swinmax,nb+swinmax):
        m1 = i - swinmax
        m2 = i + swinmax + 1
       
        idx_wext_nonzero = wext[slice(m1,m2)].nonzero()
        index = m1 + idx_wext_nonzero[0]
        med = np.median(yext[index])
        if abs(y[m1] - med) >= dist and ((y[m1] < (float(yext[i-1])+\
        float(yext[i+1]))/2 - dist) or (y[m1] > max(yext[i-1],yext[i+1])+dist)):
            w0[m1] = 0
            spikes [m1] = 1
            pass
        pass
    return w0,spikes
# ---

# ---
def savgol(y,w):
    ''' Adapted code from TIMESAT ''' 
    # Preventing modifications on the source profile
    y_ = y.copy()
    w_ = w.copy()
    winmax = win.max()    
    # Extend data circularity to improve fitting near the boundary 
    # of original data
    t = np.arange(-winmax+1,nb + winmax+1)
    leftSlice = slice(nb-winmax,nb)
    rightSlice = slice(0,winmax)
    # ---
    y_ = r_[y_[leftSlice], y_,y_[rightSlice]]#[:,:,np.newaxis]
    # Need it to convert to 1D to be dimensions-compatible with the yfits
    yfit = np.ravel(y_) 
    wfit = r_[w_[leftSlice],w_,w_[rightSlice]]
    # general slice which points always to the profile data
    dataSlice = slice(winmax, nb + winmax)
    dataRange = range(winmax, nb + winmax)
    # number of elements in tuple of indices resulting 
    # during the following fitWindowAt
    idx_t = 2 
    nenvi = len(win) # number of fitting windows-nenvi)
    #
    yfits = np.zeros((nb,nenvi))
    #
    for ienvi in range(nenvi):
        # Compute standard deviation for fitted function
        yfitstd= np.std(yfit[:])
        for i in dataRange:
            # set fitting window        
            m1 = i-win[ienvi]
            m2 = i+win[ienvi]+1
            left = 0
            right = 0
            # Adapting fitting interval. Large variation use a smaller window.  
            adjustWindow = ((yfit[slice(m1,m2)].max() -\
                    yfit[slice(m1,m2)].min()) > 1.2 * 2 * yfitstd)
            if adjustWindow == True:
                # adjusting the left side with views of m1
                m1 = m1 + int(np.floor(win[ienvi])/3)
               # adjusting the right side with views of m2 
                m2 = m2 - int(np.floor(win[ienvi])/3) 
                pass
            # Check so that there are enough points, at least 3 at either side
            # with weights different from zero. If not, extend fitting window
            failleft = 0 
            while  (abs(wfit[slice(m1,i+1)]) > 1e-10).sum() \
                                                        < 3 and failleft ==0:
                m1 = m1 -1
                if m1 < 1:
                    failleft = 1
                    m1 = 1
                    left = left +1
                    #print 'extended on left '+str(left)
                    pass
                pass               
            failright = 0 
            
            while (abs(wfit[slice(i,m2)]) > 1e-10).sum() < 3 and failright == 0:
                m2 = m2+1
                if m2 > nb + 2*winmax:
                    failright = 1
                    m2 = nb + 2*winmax
                    right = right+1
                    #print 'extended on right '+str(right)
                    pass
                pass    
            # Fit the polynomial if enough data values with non-zero weight 
            if failleft ==0 and failright == 0:
                # preparing data slices as to construct the design matrix
                s_wfit = np.ravel(wfit[slice(m1,m2)])
                s_t = t[slice(0,m2-m1)]
                s_y = np.ravel(y_[slice(m1,m2)])
                # Construct the design matrix A and the column matrix b
                A = c_[np.matrix(s_wfit).T,np.matrix(s_wfit*s_t).T,\
                       np.matrix(s_wfit*s_t**2).T]
                b = np.matrix(s_wfit*s_y).T
                # Solving linear-squares problem A^TAc = A^Tb
                ATA = (A.T)*A
                ATb = (A.T)*b 
                #
                c = np.linalg.solve(ATA, ATb)
                # Evaluating the fitted function
                yfit[i] = c[0] + c[1]*t[i-m1] + c[2]*t[i-m1]**2
            else:
                s_y = np.ravel(y_[slice(m1,m2)])
                yfit[i] = np.median(s_y)
                pass
            #####################################
            # Kees' suggestion                ####
            if forceUpperEnvelope == True:
                # All iterations will be forced to the upper envelope
                if lastIterationLikeTIMESATfit == False: 
                    if (yfit[i] < y[i-winmax])and wfit[i]==1: 
                        yfit[i] = y[i-winmax]
                # All except the last iteration 
                # will be forced to the upper envelope  
                else: 
                    if (yfit[i] < y[i-winmax])and wfit[i]==1 and \
                        ienvi<win.shape[0]-1: yfit[i] = y[i-winmax]
                    pass                       
                pass                         ####
            #####################################
            yfits[:,ienvi] = yfit[dataSlice]
            pass
        pass
    return yfits
# ---
