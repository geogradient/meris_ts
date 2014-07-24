#! /usr/bin/env python
# execfile('gem_v3.1.py')
__author__ = "Jose M. Beltran <gemtoolbox@gmail.com>"

''' 
GEM ToolBox V3.3
Author: Jose M. Beltran (gemtoolbox@gmail.com)
Purpose: Set of functions to work with a stack of hyper-temporal images using GDAL
        It will accept as input any of the GDAL-recognised image formats,
        and will output as an ERDAS imaging file.
USAGE: 
    GEM image class:
    >>> image = gem.GEM_Image()
    >>> image.open(fullPath)
    >>> image.writeBandsAsImages(rasterFormat='GEOTIFF')
    Signature class:
    >>> my_signatures = Signature()
    >>> (optional) my_signatures.transpose_SIG_file(inPath,inSIGfile)
    >>> my_signatures.read_transposed_SIG_file(inPath = 'D://My Docs//working//dat//',currentSIGfile='means_16classes4Excel.dat')
    Similarity class
    >>> tests = Similarity(v,w) # v and w are numpy arrays and could be set after
    >>> tests.v = np.array([0,3,4,5])
    >>> tests.w = np.array([7,6,3,-1])
    >>> tests.euclidian_distance() # will calculate over v and w
    >>> tests.spectral_angle() # will calculate over v and w
    >>> tests.mann_whitney() # Calculates the Mann Whitney U statistics

Version 1.0 (Nov 03, 2008): 
    Module bindings with: osgeo.gdal, osgeo.gdal_array, osgeo.gdalconst, numpy, scipy.r_, scipy.c_
    >>> yearsInProfile(temporal_profile)
    >>> getImageDim(in_dataset) # return nrows,ncolumns,nbands of the in_dataset
    >>> createImageHolder(in_dataset,out_file) # Creates a new file to hold the new image of type HFA
    >>> getPixelProfile(in_dataset, idx_row = 0 ,idx_col = 0) # Reads the nband-values at the given pixel
        and returns a 1D-array
    >>> getRowProfile(in_dataset,idx_row) # Reads all the column-values at the given row
        and returns a 2D-array
    >>> get3DFullProfiles(in_dataset) # Reads all the values of the source dataset and returns
        a 3D-array.
    >>> pixelProfileToImage(t1Dprofile, idx_row = 0,idx_col=0) # writes the profile for selected pixel.
        Do not forget to close the image holder when it is not need it anymore by setting: imageHolderName = None
    >>> rowProfileToImage(t2Dprofile, idx_row = 0) # # writes the profile for all the columns in the selected row.
        Do not forget to close the image holder when it is not need it anymore by setting: imageHolderName = None
    >>> array3DToImage(array3D,outfilenamePlusPath,in_dataset) # Saves a 3D array to an image file of type HFA    
    >>> DEPRECIATED FROM VERSION 3.0-- initGraphics() # Returns an instance of Gnuplot ready for ploting

Version 1.1 (Nov 26, 2008):

    >>> writeBandsAsImages(in_dataset,outPath,outfilename,outFormat = 'HFA')
        Reads a GDAL dataset from GDAL supported images and save each individual band as a new file 
        in a different or current GDAL image supported formats. It keep when possible
        the metadata from the source image.
        - outPath should be in the format: D:\\working\\path\\
        - outfilename should not have extension.
        
Version 2.0 (Nov 30, 2008):
    >>> The GEMtoolBox.py was converted into a module which manage functions
        inside a class.
    >>> The GEM_Image class is created to handle more efficiently the GDAL 
        image formats.
        
Version 3.0 (Dec 10, 2008):
    New functions:
    >>> combination(justalist) # Generates a list of unique pair combinations on the given list
    >>> 
    
    The signature class was incorporated with the following methods:
    
    >>> transpose_SIG_file(inPath,inSIGfile)
            # Transpose the signature file (.sig) produced by Signature Editor in ERDAS 9.1
    >>> read_transposed_SIG_file(inPath,currentSIGfile) 
            # Returns: (class,classValues) ---> Numpy array holding the full profile values for each class
    >>> get_annual_profiles_xclass() # Returns a numpy array with shape (nclasses, nyears, nptperyear)        
    >>> save_annual_profile_xclass(out_path='D://My Docs//working//dat//',filename = 'apxc.txt')
            # Saves the current array of annual profiles x class (nyears,nptperyear,nclasses)

Version 3.1 (Dec 11,2008):
    Added Similarity class to assess similarity between two numpy vectors(v and w) includes:
    >>> spectral_angle()
    >>> bray_curtis_distance()
    >>> euclidian_distance()
    >>> intensity_difference()
    >>> jaccards_coeficient()
    >>> mann_whitney()
    >>> kolmogorov_smirnov()
    
Version 3.2 (Jan 04,2009)
    Added getBand to the GEM_Image class
    similarity class moved to gem_stats module
    
Version 3.3 (March 27,2009)
    Added the pyTIMESAT_v11.
    
Updated: JAN 09, 2009
'''
import os
import osgeo.gdal as og
import numpy as np
import osgeo.gdalconst as ogc
import osgeo.gdal_array as oga

from pylab import sqrt
from pylab import dot
from pylab import sum

from scipy import r_ as r_
from scipy import c_ as c_
import time




def combination(justalist):
    ''' Generates a list of unique pair combinations on the given list '''
    idx =[]
    for each in xrange(len(justalist)):
        current = justalist.pop(0)
        for left in justalist:
            idx.append((each,left))
    return idx

#    
class GEM_Image(object):
    #FIXME: Try to catch when the file is not in directory
    '''
    Creates an Image object.
    Attributes:
    dims --> image dimensions [nrows,ncolumns,nbands]
    '''
    def __init__(self):
        self.name = None
        self.dims = None
        self.dataset = None
        self.knownRasterFormats = {'ERDAS':('HFA','.img'),'GEOTIFF':('GTiff','.tif'),\
                                   'IDRISI':('RST','.rst'),'ILWIS':('ILWIS','.mp#'),\
                                   'ASCIIGRID':('AAIGrid','.txt'),'ENVI':('ENVI','.bin'),\
                                   'JPEG':('JPEG','.jpg')}
        self.outputRasterFormat = None
        self.out_path = None
        self.out_filename = None
        self.outfileExt = None
        self.status = None
        pass
    
    def open(self,fullPath):
        '''Open a GDAL supported image format''' 
        
        self.src_path, self.name= os.path.split(fullPath)
        
        print('working with image: ',self.name)
        self.dataset = og.Open(fullPath)
        # Getting image dimensions
        ncolumns = self.dataset.RasterXSize
        nrows = self.dataset.RasterYSize
        nbands = self.dataset.RasterCount
        self.dims = [nrows,ncolumns,nbands]
        self.driver = self.dataset.GetDriver().ShortName
        pass
    
    def getBand(self, band):
        b = self.dataset.GetRasterBand(band)
        
        return b.ReadAsArray(xoff=0,yoff=0,win_xsize=self.dims[1],win_ysize=self.dims[0])
        
    def getPixelProfile(self, idx_row = 0 ,idx_col = 0):
        ''' Reads the nband-values at the given pixel and returns a 1D-array (nband,1)'''
        # The array shape of (nband,1) is required to save it later as an image using GDAL.
        pixel_1D_profile = self.dataset.ReadAsArray(xoff=idx_col,yoff=idx_row,xsize=1,ysize=1)#(nbands,1,1)
        return pixel_1D_profile[:,0,:]
    def getRowProfile(self,idx_row=0):
        ''' Reads all the column-values at the given row and returns a numpy array (nbands,1 row, ncol)'''
        row_2D_profile = self.dataset.ReadAsArray(xoff=0,yoff=idx_row,xsize=self.dims[1],ysize=1)# (nbands,1,ncols)
        #row_2D_profile = row_2D_profile[:,0,:]
        #row_2D_profile = np.reshape(row_2D_profile,(self.dims[1],self.dims[2]))
        return row_2D_profile
    def asArray(self):
        ''' Read all the image at once and returns a numpy Array (nbands,nrows,ncols)'''
        array3D = self.dataset.ReadAsArray(xoff=0,yoff=0,xsize=self.dims[1],ysize=self.dims[0]) 
        #array3D = np.reshape(array3D, (self.dims[0],self.dims[1],self.dims[2]))     
        return array3D
    ###
    
    def create_emptyRaster(self,out_path='D://My Docs//working//out_test//',filenameWithoutExtension='test',outputRasterFormat='ERDAS'):
        '''
        Creates a new empty raster to hold the new image.
        Default raster,  format: 'ERDAS'; data type: uint8
        '''
        self.out_path = out_path
        self.out_filename = filenameWithoutExtension
        out_format,fileExtension = self.knownRasterFormats[outputRasterFormat]
        self.outfileExt = fileExtension
        self.outputRasterFormat = outputRasterFormat
        fullPathName = out_path+filenameWithoutExtension+fileExtension
        src_projection = self.dataset.GetProjection()
        src_geotransform = self.dataset.GetGeoTransform()
        out_datatype = ogc.GDT_Byte
        driver = og.GetDriverByName(out_format)
        outdataset = driver.Create(fullPathName, self.dims[1],self.dims[0],self.dims[2], out_datatype)
        outdataset.SetProjection(src_projection)
        outdataset.SetGeoTransform(src_geotransform)
        outdataset = None
        return True
    
    
    #
    def pixelProfileToRaster(self, idx_row = 0,idx_col=0, currentPixelArray = None):
        ''' Saves the current temporal profile for selected pixel @(idx_row,idx_col)
        to a previous created empty raster '''
        if self.out_filename == None: self.update() # It will updated itself if no out filename is given.
        self.status = None 
        print('updating pixel in',self.out_filename+self.outfileExt)
        fullpath = self.out_path+self.out_filename+self.outfileExt
        updatedataset = og.Open(fullpath,ogc.GA_Update)
        if currentPixelArray == None:
            currentPixelArray= self.getPixelProfile(idx_row,idx_col)
        nbands = currentPixelArray.shape[0]
        for iband in range(nbands):
            eprofile = np.array(currentPixelArray[iband])
            eprofile.shape = (1,-1) #shape (1,1)
            currentBand = updatedataset.GetRasterBand(iband+1)
            oga.BandWriteArray(currentBand, eprofile, xoff = idx_col, yoff=idx_row)
            pass
        updatedataset = None
        self.status = True
        pass
    
    def rowProfileToImage(self,idx_row = 0,currentRowArray = None,rasterFormat='ERDAS'): #currentRowArray.shape (nbands,1 row,ncols)
        ''' Saves the current temporal profile for selected pixel @(idx_row,idx_col)
        to a previous created empty raster '''
        def update():
            self.out_filename = self.name[:-4]+'_new'
            self.outfileExt = self.name[-4:]
            if self.out_path == None: self.out_path = 'D://My Docs//working//out_test//'
        
            self.create_emptyRaster(out_path=self.out_path,\
                                    filenameWithoutExtension=self.out_filename,\
                                    outputRasterFormat=rasterFormat)
            pass
        
        
        if self.out_filename == None: update() # It will updated itself if no out filename is given.
        if (self.name == (self.out_filename+self.outfileExt)):
            print('Creating an empty raster')
            update()
        self.status = None
        print('updating row in',self.out_filename+self.outfileExt)
        fullpath = self.out_path+self.out_filename+self.outfileExt
        updatedataset = og.Open(fullpath,ogc.GA_Update)
        if currentRowArray == None: # If array in not given, retrieve the one @ given row. This allows to write other arrays instead of the image. 
            currentRowArray = self.getRowProfile(idx_row)
            pass
            
        for iband in range(currentRowArray.shape[0]):
            currentBand = updatedataset.GetRasterBand(iband+1)
            rowprofile = currentRowArray[iband]# (1 row,ncols)
            oga.BandWriteArray(currentBand, rowprofile, xoff = 0, yoff=idx_row)
           
        updatedataset = None
        self.status = True
        pass
    def array3DToImage(self,imageArray = None,rasterFormat='ERDAS'):
        '''
        Saves a 3D array to an image file of type HFA.
        NOTE. THIS WILL NOT REQUIRE TO OPEN A HOLDER data set.
        It will use like_src_dataset
        '''
        #FIXME:error if the name and out_name are not the same...shijo's problem check in outFileExt...weird...
        #FIXME: try to solve the need of outfileExt
        def update():
            self.out_filename = self.name[:-4]+'_new'
            self.outfileExt = self.name[-4:] # required to test for name duplicates
            if self.out_path == None: self.out_path ='D://My Docs//working//out_images//'        
            pass
        
        if imageArray == None:
            imageArray = self.asArray()
            pass
        if self.out_filename == None: update() # It will make a copy of itself if no out filename is given.
        if (self.name == (self.out_filename+self.outfileExt)): update()
        self.status = None
        idriver,fileExt = self.knownRasterFormats[rasterFormat]
        self.outfileExt = fileExt
        outfilenamePlusPath = self.out_path+self.out_filename+self.outfileExt
        oga.SaveArray(imageArray,outfilenamePlusPath,format = idriver,prototype = self.dataset )
        self.status = True
        pass
    
    def writeBandsAsImages(self, imageArray = None,rasterFormat = 'ERDAS'):
        '''
        Reads a GDAL supported image and save each individual band as a new file 
        in a different or current GDAL image supported formats. It keep when possible
        the metadata from the source image.
        - outPath should be in the format: D:\\working\\path\\
        - outfilename should not have extension.
    
        outFormat:
        ERDAS imaging = 'HFA'
        Geotiff format = 'GTiff'
        Idrisi fomat = 'RST'
        Ilwis format = 'ILWIS'
        '''
        years = [98,99,0,1,2,3,4,5,6,7,8]
        months = [4,5,6,7,8,9,10,11,12,1,2,3]
        day = [1,2,3]
        names = ['NDV'+str(iyear).zfill(2)+str(imonth).zfill(2)+str(iday)+'PL' for iyear in years for imonth in months for iday in day]
        
        def update():
            self.out_filename = self.name[:-4]
            if self.out_path == None: self.out_path = 'D://My Docs//working//out_test//'        
            pass
        
        if imageArray == None:
            imageArray = self.asArray()
            pass
        if self.out_filename == None: update() # It will make a copy of itself if no out filename is given.
          
        self.status = None
        idriver,fileExt = self.knownRasterFormats[rasterFormat]
        self.outfileExt = fileExt
        for iband in range(imageArray.shape[0]):
            #output = self.out_path+self.out_filename+'_b'+str(iband+1).zfill(3)+self.outfileExt
            output = self.out_path + names[iband]+self.outfileExt
            # Without the prototype will not save properly. 
            oga.SaveArray(imageArray[iband,:,:], output, format = idriver, prototype = self.dataset , INTERLEAVE = 'BIL')
            pass
        return True
    pass
#
class Signature(object):
    ''' Instance of a Signature object '''
    def __init__(self):
        self.data = None # will hold a numpy array of shape (npt,nclasses)
        self.annual_profile_xclass = None
        self.nyears = None
        pass
    
    def transpose_SIG_file(self,inPath='D://My Docs//working//dat//',inSIGfile='means_16classes.dat'):
        '''
        # ---
        CODED BY: Jose M. Beltran (gemtoolbox@gmail.com)
        CURRENT VERSION 1.1
        UPDATED: Nov 26, 2008
        # ---
        PURPOSE: Transpose the Signature file produced by Signature Editor in ERDAS 9.1.
        NOTES: Reads the mean signature values per class from a derived text file
            of an ERDAS imaging 9.x signature file. SEE BELOW the instructions
            to create the input text file from the ERDAS 'sig' file format.
        INPUTS:
            inpath --> Directory path in the form of: D:\\working\\path\\
            inSIGfile --> Filename of the ERDAS signature (SIG) file
        USAGE:
        # with the signature editor open in ERDAS choose:
        # View>Columns>Statistics
        # Check Mean and verify that order by Layer is cheked, then close the column statistics
        # Shift-select only Columns 1 and 8 (Signature Name and Count, respectively) then apply
        # With the Signature Editor open right click on the Signature Name column and Select all,
        # then copy and paste into a plain ASCII file, using notepad or any available text editor.
        # use the produced text file as an input file 
        # 
        VERSION LOG:
        Version 1.0 Date: Sep 23,2008
            All the code was outside the function. The code was in the script named ERDAS_sig_TO_EXCEL.py.
            required user input
        Version 1.1 Update: Nov 26, 2008
            Code was included as function in GEM Toolbox.
        Version 1.2  Update: Dec 10, 2008
            Code was included as a method of the Signature Class
        '''
    
        outname = inSIGfile[:-4]+'4Excel'+inSIGfile[-4:]  
        outfilename = inPath+outname
        ifile = open(inPath+inSIGfile, 'r')
        ofile = open(outfilename, 'w')
    
        tempArray = [];
        lineIndex = 0;
        lines = ifile.readlines()
        # Remove trailing characters and string variables at the beginning of each line.
        for eachline in lines:
            lineIndex = lineIndex + 1;
            valuesInLine = eachline.split()
            if lineIndex == 1: tempArray.append(valuesInLine[2:]) # include everything except the first two string values-"True" and "Class"
            elif lineIndex >1: tempArray.append(valuesInLine[1:]) # include everything except the first string value- "Class"
            pass
        # convert the list into Array and Transpose the array
        sigdata = np.array(tempArray).T
        # write the new file
        for i in xrange(sigdata.shape[0]):
            for j in xrange(sigdata.shape[1]):
                ofile.write(sigdata[i,j]+' ',)
                pass
            ofile.write('\n')
            pass
        ifile.close()
        ofile.close()
        self.data = sigdata[2:,:]  # (npt,nclasses)
        return sigdata[2:,:]
    
    def read_transposed_SIG_file(self,inPath = 'D://My Docs//working//dat//',currentSIGfile='means_87classes4Excel.dat'):
        ''' 
        # Returns: (class,classValues) ---> Numpy array holding the full profile values for each class 
        '''
        fullPathfile = inPath+currentSIGfile
        data = np.loadtxt(fullPathfile)
        # uclasses = data[0]; cvalues = data[2:]; nvalues = cvalues.shape[0]; nclasses = cvalues.shape[1]
        self.data = data[2:,:]
        return data[2:,:] # (npt,nclasses)

    def get_annual_profiles_xclass(self):
        ''' 
        Returns a numpy array with shape (nyears,nptperyear,nclasses) 
        aClasses ---> Array holding the full profile values for each class
        TODO: catch error when self.data is None
        '''
        
        nptperyear = 36 # Number of points per year SPOT-VEG 10 day synthesis has 36 per year.
        nclasses = self.data.shape[1]
        npt = self.data.shape[0]
        nyears = npt/nptperyear
        apxc =  np.reshape(self.data,(nyears,nptperyear,self.data.shape[1])) #(nyears,nptperyear,nclasses)
        self.annual_profile_xclass = apxc
        self.nyears = self.annual_profile_xclass[0]
        return apxc
    
    def save_annual_profile_xclass(self,out_path='D://My Docs//working//dat//',filename = 'apxc.txt'):
        '''
        Saves the current array of annual profiles x class (nyears,nptperyear,nclasses) 
        '''
        apxc = self.annual_profile_xclass
        
        if (apxc == None) and (self.data != None):
            self.get_annual_profiles_xclass()
            pass
        
        nclasses = apxc.shape[2]
        outfilename = out_path+filename[:-4]+str(nclasses).zfill(3)+filename[-4:]  
        ofile = open(outfilename, 'w')
    
        classlabel = ['CLASS'+str(eachClass).zfill(3)+'_'+str(eachYear).zfill(2)\
                      for eachClass in xrange(apxc.shape[2])\
                      for eachYear in xrange(apxc.shape[0])]
        count = 0
        for eachClass in xrange(apxc.shape[2]):
            for eachYear in xrange(apxc.shape[0]):
                yearValues = str(apxc[eachYear,:,eachClass].tolist()).replace('[','').replace(']','')
                ofile.write(classlabel[count]+','+yearValues+'\n')
                count = count + 1
                pass
            pass
        ofile.close()
        return True
    
#Debugging or use as example:    
# execfile('classi.py');image=GEM_Image();image.open();image.create_emptyRaster();image.pixelProfileToRaster();
# pixel = GEM_Image(); pixel.open(path='D://My Docs//working//out_test//', filename='test.img');w = pixel.getRowProfile(); w[0,:,:]=1;w[1,:,:]=2;