# -*- coding: utf-8 -*-
"""
Created on Wed May 28 12:44:19 2014

@author: Administrator
"""
import uuid
import numpy as np


srednjiFajl = r'C:\Dropbox\Sola\DoktoratFMF\MeV-SIMS\MERITVE\cetrteMeritve\20140126_101752'
maliFajl = r'C:\Dropbox\Sola\DoktoratFMF\MeV-SIMS\MERITVE\cetrteMeritve\20140116_170319' 
velikFajl= r'C:\Dropbox\Sola\DoktoratFMF\MeV-SIMS\MERITVE\cetrteMeritve\20140124_180055'
velikFajl2= r'C:\Dropbox\Sola\DoktoratFMF\MeV-SIMS\MERITVE\cetrteMeritve\20140123_201719'
ogromnFajl = r'C:\Dropbox\Sola\DoktoratFMF\MeV-SIMS\MERITVE\cetrteMeritve\20140124_200902'
ogromnFajlLepaSlika =r'C:\Dropbox\Sola\DoktoratFMF\MeV-SIMS\MERITVE\sedmeMeritve\20140515_133858'

baseFile=r"C:\Documents and Settings\Administrator\My Documents\Delo\imzML\example3x3"


record_dtype = np.dtype( [ ( 'x' , '<i2' ) , ( 'y' , '<i2' ) , ( 'time' , '<u4') , ( 'pNumb' , '<u8' ) ] ) 
f = open(ogromnFajlLepaSlika + '\ListMode.bin', 'rb')
data = np.fromfile(f,dtype=record_dtype,count=-1)
f.close()





#fig = plt.figure()


def createIBD(data, pixels, binning, fname = None, formatN="float32"):
    if fname:
        OUT = open(fname+"\\generiranXML150.ibd","bw")
    else:
        return
    UUID=uuid.uuid1()
    print(UUID)
    OUT.write(UUID.bytes)
    maxVal = 32768
    minVal = 0
    intSize = maxVal / pixels
    intervals = np.arange(minVal,maxVal,intSize)
    count=1
    for i in range(pixels):
                if i < pixels-1:
                    maskX = np.logical_and(intervals[i] < data['x'],
                                           data['x'] < intervals [i+1])
                else:
                    maskX = intervals[i] < data['x']
                
                for j in range(pixels):
                    
                    if j < pixels -1:
                        maskY = np.logical_and(intervals[j] < data['y'],
                                               data['y'] < intervals[j+1])
                    else:
                        maskY = intervals[j] < data['y']
                    mask = np.logical_and(maskX,maskY)
                    #print(len(mask))
                    #ax=fig.add_subplot(pixels,pixels,count)
                    count = count + 1
                    H, bins = np.histogram(data['time'][mask], bins=range(binning))
                    bins[1:].astype('float32',copy=False).tofile(OUT)
                    #print(len(bins[1:]))
                    H.astype('float32',copy=False).tofile(OUT)
                    if count % 1000 ==0:
                        print(count)
    if OUT:
        OUT.close()
        
        
createIBD(data, 15, 3000, r"C:\Dropbox\Python\SIMS\SpectrumViewer2\images")