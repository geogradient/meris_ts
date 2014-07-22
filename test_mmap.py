import mmap
import os
from string import strip
import numpy as np
from itertools import islice
os.chdir(r'D:\My Docs\working\dat')
filename = 'D://My Docs//working//dat//apxc087.txt'
f = open(filename, 'r')

class GenerateClassProfiles:
    def __init__(self, ofile):
        self.ofile = ofile
        self._datammap = mmap.mmap(self.ofile.fileno(),0,tagname='signaturefile', access=mmap.ACCESS_READ)
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
    
def dataInClass(ofile, iclass, nyears=10):
    '''Returns an iterator of the year-profiles of the selected class'''
    newStart = iclass*nyears
    newEnd = newStart+nyears
    g = GenerateClassProfiles(ofile)
    nmap = g._datammap
    return islice(g, newStart, newEnd, 1), nmap

def getDataInClass(ofile, iclass):
    '''Returns a numpy array with the year-profiles of the selected class'''
    generator, nmap = dataInClass(ofile, iclass)
    data = list(generator)
    nmap.close()
    return np.array(data)



