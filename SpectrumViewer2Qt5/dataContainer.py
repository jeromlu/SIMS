# -*- coding: utf-8 -*-
"""
Created on Tue Mar 25 18:16:31 2014

@author: Luka

data container za histograme, listmode podatke, kalibracijo mass itd.
"""

from PyQt5.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QDialogButtonBox, QProgressBar
from PyQt5.QtCore import QFileInfo

import png
import numpy as np
import os#, uuid
import imzML


class listModeContainer(object):
    
    def __init__(self):
        
        self.__fname = ""
        self.__exportFname = ""
        
        self.__rawData = np.array([])
        
        self.__bins = np.array([])
        self.__mass = np.array([])
        self.__maximaBins = np.array([])
        self.__maximaN = np.array([])
        self.__n = np.array([])
        
        self.__infoText = None
        self.__userLabel = None
        self.__param = None #calibration parameters

        self.__recordDtype = np.dtype( [('x' , '<i2'), ('y' , '<i2'), 
                                       ('time', '<u4'), ('pNumb', '<u8')] )
        self.__part = -1 #kolikšen del preberem 10 pomeni 10*128bitov
                                       
        self.__maxN = None                               
        self.__size = None                               
        self.__calibrated = False
        self.__hasHistogram = False
        self.__dirty = False


                               
        
    def __len__(self):
        
        return len(self.__rawData)
        
#**************************************Get DATA
        
    def maxN(self):
        
        return self.__maxN
        
        
    def bins(self):
        
        return self.__bins
        
    def n(self):
        
        return self.__n
        
    def hasHistogram(self):
        return self.__hasHistogram
        
    def rawData(self):
        
        return self.__rawData
        
    def filename(self):
        
        return self.__fname
        
    def exportFilename(self):
        
        return self.__exportFname
        
    def infoText(self):
        
        return self.__infoText
        
    def maximaBins(self):
        
        return self.__maximaBins

    def maximaN(self):
        
        return self.__maximaN
        
    def size(self):
        return self.__size
        
    def calibrated(self):
        return self.__calibrated
        
    def massAxis(self):
        return self.__mass
        
    def calParam(self):
        return self.__param

#*************************************Set DATA

    def addMassAxis(self, mass, param):
        
        self.__mass = mass
        self.__param = param
        self.__calibrated = True
        self.maxima()
        self.__dirty = True
        
    def undoCalibration(self):
               
        
        self.__calibrated = False
        self.maxima()
        self.__dirty = False
        
    def setExportFilename(self, fname =None):
        self.__exportFname = fname
        
    def setPart(self, part = -1):
        self.__part = part
        
#************************************* Save-Export methods        
        




        
    def exportToTxt(self, fname = ""):
        
        error = None
        fh = None        
        
        if fname:
        
            self.__exportFname = fname
            try:
                fh = open(self.__exportFname,'w')
                if self.__calibrated:
                    for i, n in zip(self.__mass, self.__n):
                        fh.write(str(i)+'\t'+str(n)+'\n')
                else:
                    for i, n in zip(self.__bins, self.__n):
                        fh.write(str(i)+'\t'+str(n)+'\n')
            except EnvironmentError as e:
                error = "Failed to save: {}".format(e)
            finally:
                if fh is not None:
                    fh.close()
                if error is not None:
                    return False, error
                self.__dirty = False
                return True, "Saved {} calibrated spectra to {}".format(
                        len(self.__bins),
                        QFileInfo(self.__fname).fileName())
                    

    def exportToimzMLFormat(self, pixels, binning, fname = "", massRange=None, UUID = None):
          
        
        error = None
        
        if fname:
            self.__exportFname = fname
                
        try:
            imzML.createXML(pixels, binning, UUID, fname)          
            #myLongTask.start()
            #imzML.createIBD(self.__rawData, pixels, binning, UUID, self.__param, fname, massRange = massRange)
        except Exception as e:
            error = "Failed to save: {}".format(e)
        finally:
            if error is not None:
                return False, error
            else:
                return True, "Created and saved imzML file"
        
    


#************************************* LOAD DATA

    def load(self, fname = "", noBins = 11250, density = True, size = 800):
        """preveri končnico fajla in poklice pravi import(naceloma ne bi rabu, ker mam samo en format)"""
        
        if fname:
            self.__fname = fname
        
        if self.__fname.endswith(".bin"):
            return self.loadFromBinaryFile(noBins, density, size)
            
            
            
    def loadFromBinaryFile(self, noBins, density, size):
        
        self.__calibrated = False
        self.__hasHistogram = False
        self.__param = None
        error = None
        fh = None
        tooBig = ""
        
        try:
            #pogledam velikost fajla (v resnic stevilo zapisov, dogodkov)
            self.__size = os.path.getsize(self.__fname)/16
            
            
            #preberem info text
            paramsFajl = self.__fname.rstrip(self.__fname.split('/')[-1])+'Parameters.txt'
            fh = open(paramsFajl,'r')
            self.__infoText = fh.read()
            
            fh.close()
            
            path = QFileInfo(self.__fname).path()
            #preberem info text ce jev nadrejeni mapi fajl z imenom meritve.txt
            vzorecInfo = path.rstrip(path.split('/')[-1])+'/meritve.txt'
            
            if os.path.isfile(vzorecInfo):
                fh = open(vzorecInfo,'r')
                for line in fh:
                    text =line.split("\t")
                    if text[0] == self.__fname.split('/')[-2]:
                        self.__infoText=self.__infoText+"\n"+text[-1]
    
                fh.close()
            
            simulateMeasurement = False
            
            #preverim glavo in primerno nastavim offset 
            offset=self.checkHeader(self.__fname)

            #preberem podatke
            fh = open(self.__fname,'rb')
            fh.seek(offset)
            if (self.__size > 1024*1024*size/16):
                tooBig = "Size of file is too Big!!!!!"
                raise ValueError
            if simulateMeasurement:
                print(simulateMeasurement)
                dataChunk=2000
                maxN=60
                interval=np.array([3050,3120])
                print("Zacetek zanke")
                for i in range(maxN):
                    rawData = np.fromfile(fh , dtype = self.__recordDtype, count = dataChunk)
                    rawData = rawData[['x','y','time']]
                    if i==0:
                        self.__rawData = rawData
                        
                    else:
                        self.__rawData=np.append(self.__rawData,rawData)
                    mask = np.logical_and((self.__rawData['time'] < interval[1]), 
                                               (self.__rawData['time'] > interval[0]))

                    H, x, y = np.histogram2d(self.__rawData['y'][mask],self.__rawData['x'][mask],\
                                                bins=256, normed = False, range=[[-10, 32690], [-10, 32690]]) #popravit je treba ta range
                    maksimum = max(H.flatten())
                    minimum = min(H.flatten())
                    k = (255-1)/(maksimum-minimum)
                    n = (1* maksimum - minimum * 255)/(maksimum-minimum)
                    H=H*k+n
                    try:
                        fileA=open("C:\Dropbox\Python\SimulacijaMeritve\image"+str(i)+".png",'wb')                        
                        image_2d = np.vstack(map(np.uint16, H))
                        column_count,row_count=image_2d.shape
                        pngWriter = png.Writer(column_count, row_count,
                                               greyscale=True,
                                               alpha=False,
                                               bitdepth=8)
                        
                        pngWriter.write(fileA,image_2d)
                    except Exception as e:
                        QMessageBox.critical(self,"Error",e)
                    finally:
                        fileA.close()
                            
            else:
                self.__rawData = np.fromfile(fh , dtype = self.__recordDtype, count = self.__part)
                self.__rawData = self.__rawData[['x','y','time']]

            self.create_Histogram(noBins, density)
            fh.close()  
        
        #polovim napake          
        except (IOError, OSError, ValueError) as e:
            error = "Failed to load: {} ".format(e) + tooBig
            print(error)
        
        #na koncu pa naredim se tole
        finally:
            if fh is not None:
                fh.close()
            if error is not None:
                return False, error
            self.__dirty = False
            return True, "Loaded {0:,.3f} MB of data from {1}".format(
                    self.__size*16/1024/1024,
                    QFileInfo(self.__fname).filePath())              


    def create_Histogram(self, noBins, density):
        """nardim histogram iz casovnih podatkov, vrednost pripišem sredini intervala
        noBins pove stevilo intervalov, density ce zelim spekter normiran na stevilo vseh podatkov"""
        
        self.__n, bins = np.histogram(self.__rawData['time'], 
                                         bins = range(noBins), density = density)
        self.__bins = (bins[:-1] + bins[1:])/2
        self.__maxN = max(self.__n)
        self.maxima()
        self.__hasHistogram = True
        
    def maxima(self):
        """zracunam vse lokalne maksimume seveda tudi ves sum ipd. (kar je zelo slabo)"""
        
        n=15
        
        
        mask= np.r_[True, self.__n[1:] > self.__n[:-1]] & \
                                    np.r_[self.__n[:-1] > self.__n[1:], True]
        iteracijskiSeznam = range(n+1)
        for i in iteracijskiSeznam[2:]:
            a=np.ones(i,dtype=bool)
            newMask= np.r_[a, self.__n[i:] > self.__n[:-i]] & \
                                        np.r_[self.__n[:-i] > self.__n[i:], a]
            mask=mask & newMask
            

        
        if self.__calibrated:
            self.__maximaBins= self.__mass[mask]
        else:
            self.__maximaBins= self.__bins[mask]
                            
        self.__maximaN = self.__n[mask]
        
        
        
    def checkHeader(self, fname=""):
        """preveri glavo Zdravkovega binarnega fajla in nastavi dtype 
        ter vrne primeren offset"""
        
        error =  None        
        
        fh = open(fname,'rb')  
        t=np.fromfile(fh , dtype = "a1", count = 28)
  
        
        try:
            t="".join([i.decode("utf-8") for i in t])                           
        except UnicodeDecodeError as e:
            error = e
        finally:
            if fh is not None:
                fh.close()
            if error is not None:
                return 0
            if t == "*** Data Format Ver 1.0  ***":
                self.__recordDtype = np.dtype([('x' , '<i2'), ('y' , '<i2'), 
                                               ('time', '<u4'), ('pNumb', '<u8')])
                self.__infoText = self.__infoText + "\n"+t
                return 2048
            elif t == "*** Data Format Ver 2.0  ***":
                #self.__recordDtype = np.dtype([('time', '<u2'), ('pNumb', '<u2'), 
                #                               ('x' , '<i2'), ('y' , '<i2')])
                self.__recordDtype = np.dtype([('x', '<u2'), ('y', '<u2'), 
                                               ('pNumb' , '<u2'), ('time' , '<u2')])
                self.__infoText = self.__infoText + "\n"+t
                return 2048                              
            return 0
                                        

#***************************************** Another Thread
#za custom progress bar zaenkrat tega ne rabim drgac morm importat vse svetsko sranje
        
class MyCustomProgressBar(QDialog):

    def __init__(self,data, pixels, binning, UUID, calParam, fname, massRange, formatN, reducedFormat, parent=None):
        super(MyCustomProgressBar, self).__init__(parent)
        layout = QVBoxLayout(self)       

        self.progressBar = QProgressBar(self)
        self.progressBar.setRange(0,100)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|
                                     QDialogButtonBox.Cancel)
        layout.addWidget(self.progressBar)
        layout.addWidget(buttonBox)

        buttonBox.rejected.connect(self.reject)
        buttonBox.accepted.connect(self.accept)
                             
        self.myLongTask = imzML.imzMLThread()
        self.myLongTask.initialize(data, pixels, binning, UUID, calParam, fname, massRange, formatN, reducedFormat)
        self.myLongTask.notifyProgress.connect(self.onProgress)
        try:
            self.myLongTask.start()
        except Exception as e:
            error = e
            QMessageBox.critical(self,"Error in imzML thread",error)
        finally:
            QMessageBox.information(self, "Long task finished", "Finally the process is finished")

            
            
    def reject(self):
        self.myLongTask.terminate()
        self.myLongTask.wait()
        QDialog.reject(self)

    def onProgress(self, i):
        self.progressBar.setValue(i)        
