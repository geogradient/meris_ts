#! /usr/bin/env python
# execfile('crop_vgt.py')
__author__ = "Jose M. Beltran <gemtoolbox@gmail.com>"
import os
import numpy as np
import gem

fullPath = r'D:\cropvgt\PL\NDVI_PL_360.img'
outPath = r'D:\cropvgt\PL'

image = gem.GEM_Image()
image.open(fullPath)
image.out_path =  r'D:\cropvgt\PL//'

image.writeBandsAsImages(rasterFormat='ENVI')
'''
years = [98,99,0,1,2,3,4,5,6,7,8]
months = [4,5,6,7,8,9,10,11,12,1,2,3]
day = [1,2,3]

names = ['NDV'+str(iyear).zfill(2)+str(imonth).zfill(2)+str(iday)+'PL.bin' for iyear in years for imonth in months for iday in day]

'''
