# -*- coding: utf-8 -*-
"""
Created on Tue May  6 08:03:18 2014

@author: Administrator
"""

import numpy as np
import uuid
import xml.etree.ElementTree  as ET
from xml.etree.ElementTree import Element
import xml.dom.minidom
import time
#import lxml.etree as ET
#from lxml.etree import Element

from PyQt4.QtCore import QThread, pyqtSignal


srednjiFajl = r'C:\Dropbox\Sola\DoktoratFMF\MeV-SIMS\MERITVE\cetrteMeritve\20140126_101752'
maliFajl = r'C:\Dropbox\Sola\DoktoratFMF\MeV-SIMS\MERITVE\cetrteMeritve\20140116_170319' 
velikFajl= r'C:\Dropbox\Sola\DoktoratFMF\MeV-SIMS\MERITVE\cetrteMeritve\20140124_180055'
velikFajl2= r'C:\Dropbox\Sola\DoktoratFMF\MeV-SIMS\MERITVE\cetrteMeritve\20140123_201719'
ogromnFajl = r'C:\Dropbox\Sola\DoktoratFMF\MeV-SIMS\MERITVE\cetrteMeritve\20140124_200902'
ogromnFajlLepaSlika =r'C:\Dropbox\Sola\DoktoratFMF\MeV-SIMS\MERITVE\sedmeMeritve\20140515_133858'


#basePath=r"C:\Documents and Settings\Administrator\My Documents\Delo\imzML\example3x3"
basePath =r"C:\Users\Luka\Desktop\zacasno"



def readXML(pixels, binning, UUID = uuid.uuid1()):
    
    print(UUID)
    tree = ET.parse(basePath+'\\Example_Processed.imzML')
    root = tree.getroot()
    print("\n"+root.tag)
    for child in root:
        print(child.tag)
        print(child.attrib)
    for i in range(pixels**2):
        pass
    
def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = xml.dom.minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="\t") 


#**************************** CONTROLED VOCABULARY    
def cvList(root):
    cvList = ET.SubElement(root,"cvList",{"count":"3"})
    at ={"id" : "MS", "fullName" : "Proteomics Standards Initiative Mass Spectrometry Ontology", "version" : "2.26.0",
         "URI" : "http://psidev.cvs.sourceforge.net/*checkout*/psidev/psi/psi-ms/mzML/controlledVocabulary/psi-ms.obo"}
    ET.SubElement(cvList, "cv", at)
    
    at ={"id" : "IMS", "fullName" : "Imaging MS Ontology", "version" : "0.9.1",
         "URI" : "http://www.maldi-msi.org/download/imzml/imagingMS.obo"}
    ET.SubElement(cvList, "cv", at)
    
    at ={"id" : "UO", "fullName" : "Unit Ontology", "version" : "1.15",
         "URI" : "http://obo.cvs.sourceforge.net/obo/obo/ontology/phenotype/unit.obo"}
    ET.SubElement(cvList, "cv", at)
    
#***************************** OWN THREAD
    
class TaskThread(QThread):
    #notifyProgress = pyqtSignal(int)
    
    def __del__(self):
    
        self.wait()    
    
    def run(self):
        for i in range(101):
            #self.notifyProgress.emit(i)
            time.sleep(0.1)

#**************************** FILE DESCRIPTION    
def fileDescription(root,UUID):
    fd = ET.SubElement(root, "fileDescription")
    fc = ET.SubElement(fd, "fileContent")
    
    at={"cvRef" : "IMS", "accession" : "IMS:1000080", "name" : "universally unique identifier", "value" : str(UUID)}
    ET.SubElement(fc, "cvParam", at)
    
    at={"cvRef" : "IMS", "accession" : "IMS:1000031", "name" : "continous", "value" : ""}
    ET.SubElement(fc, "cvParam", at)
    

#**************************** FILE DESCRIPTION (req)
def refGroups(root):
    refList=ET.SubElement(root, "referenceableParamGroupList",{"count" : "4"})
    
    group = ET.SubElement(refList, "referenceableParamGroup",{"id" : "mzArray"})
    at={"cvRef" : "MS", "accession" : "MS:1000576", "name" : "no compression", "value" : ""}
    ET.SubElement(group, "cvParam", at)
    at={"cvRef" : "MS", "accession" : "MS:1000514", "name" : "m/z array", "value" : "",
        "unitCvRef" : "MS", "unitAccession" : "MS:1000040", "unitName" : "m/z"}
    ET.SubElement(group, "cvParam", at)    
    at={"cvRef" : "IMS", "accession" : "IMS:1000101", "name" : "external data", "value" : "true"}
    ET.SubElement(group, "cvParam", at)
    at={"cvRef" : "MS", "accession" : "MS:1000521", "name" : "32-bit float", "value" : ""}
    ET.SubElement(group, "cvParam", at)

    group = ET.SubElement(refList, "referenceableParamGroup",{"id" : "intensityArray"})
    at={"cvRef" : "MS", "accession" : "MS:1000576", "name" : "no compression", "value" : ""}
    ET.SubElement(group, "cvParam", at)
    at={"cvRef" : "MS", "accession" : "MS:1000515", "name" : "intensity array", "value" : "",
        "unitCvRef" : "MS", "unitAccession" : "MS:1000131", "unitName" : "number of counts"}
    ET.SubElement(group, "cvParam", at)    
    at={"cvRef" : "IMS", "accession" : "IMS:1000101", "name" : "external data", "value" : "true"}
    ET.SubElement(group, "cvParam", at)
    at={"cvRef" : "MS", "accession" : "MS:1000521", "name" : "32-bit float", "value" : ""}
    ET.SubElement(group, "cvParam", at)     
    
    
    group = ET.SubElement(refList, "referenceableParamGroup",{"id" : "scan1"})
    at={"cvRef" : "MS", "accession" : "MS:1000093", "name" : "increasing m/z scan", "value" : ""}
    ET.SubElement(group, "cvParam", at)
    at={"cvRef" : "MS", "accession" : "MS:1000095", "name" : "linear", "value" : ""}
    ET.SubElement(group, "cvParam", at)    
    at={"cvRef" : "MS", "accession" : "MS:1000512", "name" : "filter string",
        "value" : "ITMS - p NSI Full ms [100,00-800,00]"}
    ET.SubElement(group, "cvParam", at)

    
    group = ET.SubElement(refList, "referenceableParamGroup",{"id" : "spectrum1"})
    at={"cvRef" : "MS", "accession" : "MS:1000579", "name" : "MS1 spectrum", "value" : ""}
    ET.SubElement(group, "cvParam", at)
    at={"cvRef" : "MS", "accession" : "MS:1000511", "name" : "ms level", "value" : "0"}
    ET.SubElement(group, "cvParam", at)    
    at={"cvRef" : "MS", "accession" : "MS:1000128", "name" : "profile spectrum", "value" : ""}
    ET.SubElement(group, "cvParam", at)
    at={"cvRef" : "MS", "accession" : "MS:1000129", "name" : "negative scan", "value" : ""}
    ET.SubElement(group, "cvParam", at)    

#***************************** SAMPLE LIST (opt)

#***************************** SOFTWARE LIST (opt)

def softList(root):
    sList = ET.SubElement(root, "softwareList", {"count" : "1"})
    at = {"id" : "SpecView", "version" : "1.0"}
    ET.SubElement(sList, "software", at)
    
#***************************** SCAN SETTINGS (opt)
def scanSettingsList(root, pixels):
    
    ssL = ET.SubElement(root, "scanSettingsList", {"count" : "1"})
    ss = ET.SubElement(ssL, "scanSettings", {"id":"scansettings1"})
    
    at = {"cvRef" : "IMS", "accession" : "IMS:1000042", "name" : "max count of pixel x", "value" : str(pixels)}
    ET.SubElement(ss, "cvParam", at)
    at = {"cvRef" : "IMS", "accession" : "IMS:1000043", "name" : "max count of pixel y", "value" : str(pixels)}
    ET.SubElement(ss, "cvParam", at)

    at = {"cvRef" : "IMS", "accession" : "IMS:1000044", "name" : "max dimension x",
          "value" : str(pixels*100), "unitCvRef" : "UO", "unitAccession" : "UO:0000017", "unitName" : "micrometer"}
    ET.SubElement(ss, "cvParam", at)
    at = {"cvRef" : "IMS", "accession" : "IMS:1000045", "name" : "max dimension y",
          "value" : str(pixels*100), "unitCvRef" : "UO", "unitAccession" : "UO:0000017", "unitName" : "micrometer"}
    ET.SubElement(ss, "cvParam", at)
    
    at = {"cvRef" : "IMS", "accession" : "IMS:1000046", "name" : "pixel size x",
          "value" : str(100), "unitCvRef" : "UO", "unitAccession" : "UO:0000017", "unitName" : "micrometer"}
    ET.SubElement(ss, "cvParam", at)
    at = {"cvRef" : "IMS", "accession" : "IMS:1000047", "name" : "pixel size y",
          "value" : str(100), "unitCvRef" : "UO", "unitAccession" : "UO:0000017", "unitName" : "micrometer"}
    ET.SubElement(ss, "cvParam", at)

    


#***************************** INSTRUMENT CONFIGURATION (req)

def instrumentConfigList(root):
    
    icList = ET.SubElement(root, "instrumentConfigurationList", {"count" : "1"})
    ET.SubElement(icList, "instrumentConfiguration", {"id" : "MeVSIMS-IJS"})
    
#***************************** DATA PROCESSING (req)

def dataProcessinglist(root):
    
    dpList = ET.SubElement(root, "dataProcessingList", {"count" : "1"})
    dp = ET.SubElement(dpList, "dataProcessing", {"id" : "LZprocessing"})
    pm = ET.SubElement(dp, "processingMethod", {"order":"1", "softwareRef":"SpecView"})
    
    at={"cvRef" : "MS", "accession" : "MS:1000544", "name" : "Conversion to mzML", "value" : ""}
    ET.SubElement(pm, "cvParam", at)
    

    

 
def createXML(pixels, binning, UUID, fname):
    
    """creates XML file about metaData of measurement"""
      

#**************************** ROOT
    at={"xmlns" : "http://psi.hupo.org/ms/mzml", "xmlns:xsi" : "http://www.w3.org/2001/XMLSchema-instance",
        "xsi:schemaLocation" : "http://psi.hupo.org/ms/mzml http://psidev.info/files/ms/mzML/xsd/mzML1.1.0_idx.xsd",
        "version" : "1.1"}
    root = Element("mzML",at)
    
#**************************** CONTOLED VOCABULARY (req)
    cvList(root)
    
#**************************** FILE DESCRIPTION (req)
    fileDescription(root, UUID)
    
#**************************** REFERENCABLE PARAM GROUPS (opt)
    refGroups(root)

#***************************** SAMPLE LIST (opt)

#***************************** SOFTWARE LIST (req)
    softList(root)
    
#***************************** SCAN SETTINGS (opt)
    scanSettingsList(root, pixels)
    
#***************************** INSTRUMENT CONFIGURATION (req)
    instrumentConfigList(root)
    
#***************************** DATA PROCESSING (req)
    dataProcessinglist(root)
    
#***************************** RUN (req)    
    at = {"defaultInstrumentConfigurationRef" :"MeVSIMS-IJS", "id":"experiment1"}
    run = ET.SubElement(root,"run",at)
    spectrumList = ET.SubElement(run, "spectrumList")
    spectrumList.attrib = {"count" : str(pixels**2), "defaultDataProcessingRef" : "LZprocessing"}

    offset = 16
    encLength = 4 * (binning)
    x = 1
    y = 1
    
    for i in range(1,pixels**2+1):
        
        atributi = {"defaultArrayLength" : "0", "id" : "scan="+str(i), "index" : str(i)}
        spectrum = ET.SubElement(spectrumList, "spectrum", atributi)
        
        
        
        refGroup = ET.SubElement(spectrum, "referenceableParamGroupRef")
        atributi = {"ref" : "spectrum1"}
        refGroup.attrib = atributi
        
        scanList = ET.SubElement(spectrum, "scanList", {"count" : "1"})
        at = {"cvRef" : "MS", "accession" : "MS:1000795", "name" : "no combination", "value" : ""}
        ET.SubElement(scanList, "cvParam", at)
        scan = ET.SubElement(scanList, "scan", {"instrumentConfigurationRef" : "MeVSIMS-IJS"})
        at = {"cvRef" : "IMS", "accession" : "IMS:1000050", "name" : "position x", "value" : str(x)} # pozicija X
        ET.SubElement(scan, "cvParam", at)
        at = {"cvRef" : "IMS", "accession" : "IMS:1000051", "name" : "position y", "value" : str(y)} # pozicija Y
        ET.SubElement(scan, "cvParam", at)
        
        #print(x,"\t",y)
        if x< np.sqrt(pixels**2):
            x = x+1
        else:
            x=1
            y=y+1
        

        
        binArrayL = ET.SubElement(spectrum, "binaryDataArrayList", {"count" :"2"})
        binArray = ET.SubElement(binArrayL, "binaryDataArray", {"encodedLength" : "0"})
        ET.SubElement(binArray, "referenceableParamGroupRef", {"ref":"mzArray"})                    #mzArray
        at = {"cvRef" : "IMS", "accession" : "IMS:1000103", "name" : "external array length", "value" : str(binning)} # velikosti podatkov
        ET.SubElement(binArray, "cvParam", at)
        at = {"cvRef" : "IMS", "accession" : "IMS:1000102", "name" : "external offset", "value" : str(offset)} # offset
        ET.SubElement(binArray, "cvParam", at)
        at = {"cvRef" : "IMS", "accession" : "IMS:1000104", "name" : "external encoded length", "value" : str(encLength)} # dolzina 4 * velikost
        ET.SubElement(binArray, "cvParam", at)
        ET.SubElement(binArray, "binary")
        
        offset = offset + encLength
        
        binArray = ET.SubElement(binArrayL, "binaryDataArray", {"encodedLength" : "0"})
        ET.SubElement(binArray, "referenceableParamGroupRef", {"ref":"intensityArray"})                    #mzArray
        at = {"cvRef" : "IMS", "accession" : "IMS:1000103", "name" : "external array length", "value" : str(binning-1)} # velikosti podatkov
        ET.SubElement(binArray, "cvParam", at)
        at = {"cvRef" : "IMS", "accession" : "IMS:1000102", "name" : "external offset", "value" : str(offset)} # offset
        ET.SubElement(binArray, "cvParam", at)
        at = {"cvRef" : "IMS", "accession" : "IMS:1000104", "name" : "external encoded length", "value" : str(encLength)} # dolzina 4 * velikost
        ET.SubElement(binArray, "cvParam", at)
        
        ET.SubElement(binArray, "binary")
        
        offset = offset + encLength
        

    
    
    tree = ET.ElementTree(root)
    #xmlText=prettify(root)
    #print(xmlText)
    f = open(fname+"\\generiranXML"+str(pixels)+".imzML","w")
    tree.write(fname+"\\generiranXML"+str(pixels)+".imzML")
    f.close()
    #f=open(basePath + "\\generiranXML256.imzML","w")
    #f.write(xmlText)
    #f.close()
    
    
def createIBD(data, pixels, binning,  UUID, calParam = (1,0), fname = None, formatN="float32", massRange = [1,500]):
    """tole je se treba vkljucit QFileInfo(QFileInfo(path).path()).fileName()"""
    notifyProgress = pyqtSignal(int)
    if fname:
        OUT = open(fname+"\\generiranXML"+str(pixels)+".ibd","bw")
    else:
        return
    OUT.write(UUID.bytes)
    massRange=np.array(massRange)
    countRange = calParam[0]*np.sqrt(massRange)+calParam[1]
    maxVal = 32768
    minVal = 0
    intSize = maxVal / pixels
    intervals = np.arange(minVal,maxVal,intSize)
    count=1
    binsN = np.arange(countRange[0],countRange[1]+1,(countRange[1]-countRange[0])/binning)
    tmax = (pixels**2/100)
    print(tmax)
    #if not calParam:
    #    calParam = [1,0]
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
                    maskP = np.logical_and(maskX,maskY)
                    maskM = np.logical_and(countRange[0] < data['time'],
                                           data['time'] < countRange[1])
                    mask = np.logical_and(maskM, maskP)
                    #ax=fig.add_subplot(pixels,pixels,count)
                    count = count + 1
                    H, bins = np.histogram(data['time'][mask], bins=binsN)
                    if not calParam:
                        (bins[1:]).astype('float32',copy=False).tofile(OUT)
                    else:
                        mass = ((bins[1:]-calParam[1])/calParam[0])**2
                        (mass).astype('float32',copy=False).tofile(OUT)
                    #print(len(bins[1:]))
                    H.astype('float32',copy=False).tofile(OUT)
                    if count % round(tmax) ==0:
                        print(count/pixels**2*100)
    if OUT:
        OUT.close()
    
def main():
    pixels = 256
    binning = 11250
    record_dtype = np.dtype( [ ( 'x' , '<i2' ) , ( 'y' , '<i2' ) , ( 'time' , '<u4') , ( 'pNumb' , '<u8' ) ] ) 
    f = open(ogromnFajlLepaSlika + '\ListMode.bin', 'rb')
    data = np.fromfile(f,dtype=record_dtype,count=-1)
    f.close()
    UUID=uuid.uuid1()
    print(UUID)
    start_time = time.time()
    createXML(pixels, binning, basePath, UUID)
    mid_time = time.time()
    createIBD(data,pixels,binning,UUID, basePath)
    end_time = time.time()
    t1 = mid_time-start_time
    t2 = end_time-mid_time
    print(pixels,binning)
    print("ZA XML fajl sem potreboval{0:.1f} s, za ibd fajl sem potreboval {1:.1f} s, skupaj {2:.1f} min".format(t1,t2,(t1+t2)/60))
    
if __name__ == "__main__":
    main()