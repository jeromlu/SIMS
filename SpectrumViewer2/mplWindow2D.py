# -*- coding: utf-8 -*-
"""
Created on Wed Apr 16 19:53:16 2014

@author: Luka

matplotlib canvas for 2Dmap windows 
dodatek k Spectrum Viewer
"""

from PyQt4.QtGui import QMainWindow, QApplication, QWidget, QPushButton, QVBoxLayout, QAction
from PyQt4.QtGui import QHBoxLayout, QSlider, QFont, QComboBox, QMessageBox, QDesktopWidget, QDialog
from PyQt4.QtGui import QMenu, QIcon, QLabel, QLineEdit, QRegExpValidator, QDialogButtonBox
from PyQt4.QtGui import QFileDialog

from PyQt4.QtCore import SIGNAL, Qt, QRect, QRegExp, SLOT, QFileInfo


import sys
import numpy as np

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas 
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from mpl_toolkits.axes_grid1 import make_axes_locatable
from scipy import ndimage






class mplWindow2D(QMainWindow):
    
    def __init__(self, H = None, interval = None, extent = [0,2.5,0,1.4], fname=r"C:\\", calibrated = False, parent = None):
        
        super(mplWindow2D, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        self.path=QFileInfo(fname).path()
        self.extent = extent
        self.calibrated=calibrated
        self.H = H
        self.filter=False
        #self.H = np.random.randn(30,30) #za testiranje
        self.drawn = False
        self.interval = interval #lahko poklicem direkt ce ga rabim vedet, ni skrit
        desktop = QDesktopWidget()
        self.screenSize = desktop.screenGeometry() #velikostEkrana
        #print("Veliksot zaslona je: "+str(self.screenSize))

        
        self.mainWindow = QWidget()
        self.mainWindow.setMinimumSize(650,300)
        
        dpi=100
        self.fig = Figure((5,3.5),dpi=dpi)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.mainWindow)
        self.mpl_toolbar = NavigationToolbar(self.canvas,self.mainWindow)
        self.mpl_toolbar.setFixedSize(400,30)
        
        self.pushButtonResetSize = QPushButton("Reset size")
        
        self.horizontalSlider = QSlider()
        self.horizontalSlider.setGeometry(QRect(120, 510, 531, 31))
        font = QFont()
        font.setPointSize(12)
        self.horizontalSlider.setFont(font)
        #self.horizontalSlider.setCursor(QCursor(Qt.SizeHorCursor))
        self.horizontalSlider.setAutoFillBackground(False)
        self.horizontalSlider.setMaximum(130)
        self.horizontalSlider.setMinimum(1)
        self.horizontalSlider.setPageStep(10)
        self.horizontalSlider.setProperty("value", 100)
        self.horizontalSlider.setOrientation(Qt.Horizontal)
        self.horizontalSlider.setTickPosition(QSlider.TicksBelow)
        self.horizontalSlider.setTickInterval(5)

                     
        self.comboBox = QComboBox()
        self.comboBox.setGeometry(QRect(570, 351, 111, 21))
        self.comboBox.setObjectName("ComboBox")
        items= [m for m in mpl.cm.datad if not m.endswith("_r")]
        #items = ["jet",'rainbow', 'Blues',"brg","spectral","Paired","seismic","binary",
        #         "hot","spring","summer","winter","bwr","prism","flag"]
        self.comboBox.addItems(items)
        self.comboBox.setCurrentIndex(items.index('spectral')) #nastavim zacetno vrednost barv
        
        self.canvas.setContextMenuPolicy(Qt.CustomContextMenu)
        self.connect(self.canvas, SIGNAL('customContextMenuRequested(const QPoint&)'), self.onContextMenu)
        
        self.createContextMenu()

        
        hBox1 = QHBoxLayout()
        hBox1.addWidget(self.mpl_toolbar)
        hBox1.addStretch()
        hBox1.addWidget(self.comboBox)
        hBox1.addWidget(self.pushButtonResetSize)
        
        vBox1 = QVBoxLayout()
        vBox1.addWidget(self.canvas)
        vBox1.addLayout(hBox1)
        vBox1.addWidget(self.horizontalSlider)


        self.mainWindow.setLayout(vBox1)
        
        
        if self.interval != None:
            naslov=str(self.interval[0]+(self.interval[1]-self.interval[0])/2)
            self.setWindowTitle("Mass: "+naslov)
        


                
        
        #self.mainWindow.setGeometry(100,200,500,500)
        self.setCentralWidget(self.mainWindow)
        
        self.connect(self.pushButtonResetSize, SIGNAL("clicked()"),
                     self.resetSize)
        self.drawIntensityGraph(self.H)
                     
        self.connect(self.horizontalSlider, SIGNAL("valueChanged(int)"),
                     self.clim)
                     
        self.connect(self.comboBox, SIGNAL("currentIndexChanged(int)"),
                     self.colorfunction)
        print(self.calculateWindowGeometry())
        
    def createContextMenu(self):
        
        #create contesxt menu
        self.popMenu = QMenu(self)
        self.applyFilter = QMenu('Apply filter',self)
        
        gaussianFilter1 = self.createAction("Gaussian smooth1", self.gaussianFilter1)
        gaussianFilter2 = self.createAction("Gaussian smooth2", self.gaussianFilter2)
        gaussianFilter3 = self.createAction("Gaussian smooth3", self.gaussianFilter3)
        gaussianFilter5 = self.createAction("Gaussian smooth5", self.gaussianFilter5)
        gaussianFilter10 = self.createAction("Gaussian smooth10", self.gaussianFilter10)
        medianFilter3 = self.createAction("Median filter3", self.medianFilter3)
        edgeDetectionX = self.createAction("Edge detection X", self.edgeDetectionX)
        edgeDetectionY = self.createAction("Edge detection Y", self.edgeDetectionY)
        edgeDetectionFilter = self.createAction("Edge detection Filter", self.edgeDetectionFilter)
                
        self.addActions(self.applyFilter, (gaussianFilter1, gaussianFilter2, gaussianFilter3, gaussianFilter5, gaussianFilter10,
                                           medianFilter3, None, edgeDetectionX, edgeDetectionY, edgeDetectionFilter))

        mySaveFig = self.createAction("Save As (Luka)", self.mySave)
        plainSave = self.createAction("Plain Save 100dpi",self.plainSave)
        savePyMCA = self.createAction("Save PyMCA", self.savePyMCAfileName)
        undoAllFiltering = self.createAction("Undo all filtering", self.undoAllImageFiltering)
        
        self.popMenu.addMenu(self.applyFilter)
 
        self.addActions(self.popMenu, (mySaveFig, plainSave, savePyMCA, None, undoAllFiltering))

    def gaussianFilter1(self):
        im=ndimage.gaussian_filter(self.H, sigma=1)
        self.drawIntensityGraph(im)
        self.filter=True
        
    def gaussianFilter2(self):
        im=ndimage.gaussian_filter(self.H, sigma=2)
        self.drawIntensityGraph(im)
        self.filter=True
        
    def gaussianFilter3(self):
        im=ndimage.gaussian_filter(self.H, sigma=3)
        self.drawIntensityGraph(im)
        self.filter=True
        
    def gaussianFilter5(self):
        im=ndimage.gaussian_filter(self.H, sigma=5)
        self.drawIntensityGraph(im)
        self.filter=True

    def gaussianFilter10(self):
        im=ndimage.gaussian_filter(self.H, sigma=10)
        self.drawIntensityGraph(im)
        self.filter=True
        
    def medianFilter3(self):
        im=ndimage.median_filter(self.H, 3)
        self.drawIntensityGraph(im)
        self.filter=True

    def edgeDetectionX(self):
        
        im= ndimage.sobel(self.H, axis=0, mode='constant')
        self.drawIntensityGraph(im)
        self.filter=True
        
    def edgeDetectionY(self):
        
        im= ndimage.sobel(self.H, axis=1, mode='constant')
        self.drawIntensityGraph(im)
        self.filter=True        
        
    def edgeDetectionFilter(self):
        
        sx = ndimage.sobel(self.H, axis=0, mode='constant')
        sy = ndimage.sobel(self.H, axis=1, mode='constant')
        im = np.hypot(sx, sy)      
        self.drawIntensityGraph(im)   
        self.filter=True
        
    def undoAllImageFiltering(self):
        
        self.drawIntensityGraph(self.H)
        self.filter = False
        
    def onContextMenu(self, point):
        
        self.popMenu.exec_(self.canvas.mapToGlobal(point))       
        
    def calculateWindowGeometry(self):
        
        point = self.rect().topLeft()
        #print(point)
        globalPoint = self.mapToGlobal(point)
        #print("Zgornji levi rob: " + str(globalPoint))
        
        return self.width(), self.height()
        
        
    def drawIntensityGraph(self, data = None):
        """ draws 2D matrix data """
        #self.figure.clear()
        masa = "Ni intervala"
        if self.interval != None:# and len(self.interval)==2:
            masa="m/z = {0:0.0f}".format(self.interval[0]+(self.interval[1]-self.interval[0])/2)
            #masa = "m/z = {0:0.1f} - {1:0.1f}".format(self.interval[0],self.interval[1])
        
        #data = self.H
        #self.extent=None
        self.maxC=max(max(x) for x in data)
        if data != None:
            self.fig.clear()
            self.axes = self.fig.add_subplot(1,1,1)
            self.im = self.axes.imshow(data, cmap=self.comboBox.currentText(), extent = self.extent)          
            divider = make_axes_locatable(self.axes)
            cax = divider.append_axes("right", size="5%", pad=0.1)
            ax=self.fig.colorbar(self.im,cax=cax)
            #ax.set_label('Number of counts')
            ax.set_label('Število ionov') #slo
            tick_locator = mpl.ticker.MaxNLocator(nbins=5)
            ax.locator = tick_locator
            ax.update_ticks()
            self.axes.set_xlabel("X (mm)")
            self.axes.set_ylabel("Y (mm)")
            self.axes.set_title(masa)
            self.fig.tight_layout(pad=0)
            self.canvas.draw()
            self.drawn = True
        
    def clim(self):
        
        if self.drawn:
            ma= self.horizontalSlider.value()
            
            maC=self.maxC*ma/100
    
            self.im.set_clim([0,maC])
            self.canvas.draw()
    
    def colorfunction(self):
        
        if self.drawn:
            
            self.im.set_cmap(self.comboBox.currentText())
            self.canvas.draw()
        
    def mySave(self):
        
        sirinaOkna, visinaOkna = self.calculateWindowGeometry()
        self.fig.savefig("2DmapTest.png",dpi=300,bbox_inches='tight')
        QMessageBox.information(self,"Informacija","Not implemented yet\n"+"Sirina okna je:\t"+str(sirinaOkna) \
                                +"\nVisina okna je:\t"+str(visinaOkna))
              
    def savePyMCAfileName(self):
        """kam bom shranu, posebej kerbom isto funkcijo uporabu iz glavnega oka"""
        self.fname=self.path+"\\untitled.csv"
        self.fname = QFileDialog.getSaveFileName(self, "Select file to save to", self.fname, "ASCII (*.csv);;All(*.*)")
        if self.fname:
            self.savePyMCA()
        
        
    def savePyMCA(self):
        fname = self.fname
        if self.filter:
            a=ndimage.gaussian_filter(self.H,2).flatten()
        else:
            a=self.H.flatten()
        np.savetxt(fname,a,delimiter=',',fmt='%1.8f')
        
    def plainSave(self):
        
        #To morm se pogledat zakaj je vse to ce je kaj koristno        
        #fig_size = fig.get_size_inches()
        #w,h = fig_size[0], fig_size[1]
        #fig.patch.set_alpha(0)
        #if kwargs.has_key('orig_size'): # Aspect ratio scaling if required
        #    w,h = kwargs['orig_size']
        #    w2,h2 = fig_size[0],fig_size[1]
        #    fig.set_size_inches([(w2/w)*w,(w2/w)*h])
        #    fig.set_dpi((w2/w)*fig.get_dpi())
        #a=fig.gca()
        #a.set_frame_on(False)
        #a.set_xticks([]); a.set_yticks([])
        #plt.axis('off')
        #plt.xlim(0,h); plt.ylim(w,0) 
        dialog = plainSaveDialog(self.path, self)
        if self.drawn and dialog.exec_():
            dpi=int(dialog.leDPI.text())
            pad=float(dialog.lePad.text())
            fname= dialog.fname
            self.axes.xaxis.set_ticks([])
            self.axes.yaxis.set_ticks([])
            self.axes.set_xlabel("")
            self.axes.set_ylabel("")
            self.axes.set_title("")
            self.fig.delaxes(self.fig.axes[1])
            #self.fig.tight_layout(pad=0)
            self.fig.subplots_adjust(left=None, bottom=None, right=None, top=None,wspace=None, hspace=None)
            self.fig.savefig(fname,dpi=dpi,bbox_inches='tight',pad_inches=pad)
            self.drawIntensityGraph(self.H)
            
        else:
            QMessageBox.warning(self,"No figure to save","there is no figure to save, reconsider your intention!")
        
    def resetSize(self):
        
        self.setGeometry(QRect(500, 347, 650, 450))  #ugotovil s poskusi, tako ko bom kaj spremenil ne bo vec prav!!!!
        self.fig.set_figwidth(500)
        self.fig.set_figheight(350)
        self.canvas.draw()

        

#**********************Za dodajanje akcij (kopirano iz spectrum viewer)
    def addActions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def createAction(  self, text, slot=None, shortcut=None, 
                        icon=None, tip=None, checkable=False, 
                        signal="triggered()"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon("./images/{}.png".format(icon)))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action
        

class plainSaveDialog(QDialog):
    
    def __init__(self, path=None, parent = None):
        
        super(plainSaveDialog,self).__init__(parent)
        testRe = QRegExp(r"[0-9]{0,3}")
        testRe1 = QRegExp(r"[0-9]{0,3}\.[0-9]")        
        
        
        self.path = path
        self.fname = self.path + "/plainImage.png"
        
        
        labelDPI = QLabel("Dots per Inch value: ")        
        self.leDPI=QLineEdit("100")
        self.leDPI.setValidator(QRegExpValidator(testRe,self))
        
        labelPad = QLabel("White margin around the image: ")        
        self.lePad=QLineEdit("0.1")
        self.lePad.setValidator(QRegExpValidator(testRe1,self))
        
        labelFname = QLabel("File path: ")        
        self.leFname=QLineEdit(self.fname)
        
        pbBrowse = QPushButton("Browse")

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|
                                     QDialogButtonBox.Cancel)
        
        hBox1 = QHBoxLayout()
        hBox1.addWidget(labelDPI)
        hBox1.addWidget(self.leDPI)
        hBox1.addStretch(1)
        
        hBox2 = QHBoxLayout()
        hBox2.addWidget(labelPad)
        hBox2.addWidget(self.lePad)
        hBox2.addStretch(1)
        
        hBox3 = QHBoxLayout()
        hBox3.addWidget(labelFname)
        hBox3.addWidget(self.leFname)
        hBox3.addWidget(pbBrowse)
        
        vBox1=QVBoxLayout()
        vBox1.addLayout(hBox1)
        vBox1.addLayout(hBox2)
        vBox1.addLayout(hBox3)
        vBox1.addWidget(buttonBox)
        
        self.setLayout(vBox1)
        self.setWindowTitle("Plain Save Dialog")

        self.connect(buttonBox, SIGNAL("accepted()"),
                     self, SLOT("accept()"))
        self.connect(buttonBox, SIGNAL("rejected()"),
                     self, SLOT("reject()"))
        self.connect(pbBrowse,SIGNAL("clicked()"),self.getPath)
        
        self.connect(self.leFname, SIGNAL("editingFinished()"), self.updateFname)
        
    def getPath(self):
        
        self.fname = QFileDialog.getSaveFileName(self, "Select file to save to", self.fname, "Images (*.png *.xpm *.jpg *.pdf);;All(*.*)")
        self.path = QFileInfo(self.fname).path()
        if self.fname:
            self.leFname.setText(self.fname)
            
    def updateFname(self):
        
        self.fname = self.leFname.text()
        
        
        
        
class mplWindow2DLight(QMainWindow):
    
    def __init__(self, H = None, interval = None, extent = [0,2.5,0,1.4], fname=r"C:\\", calibrated=False, parent = None):
        
        super(mplWindow2DLight, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        

        self.extent = extent
        self.calibrated=calibrated
        self.H = H
        #self.H = np.random.randn(30,30) #za testiranje
        self.drawn = False
        self.interval = interval #lahko poklicem direkt ce ga rabim vedet, ni skrit
        self.path = QFileInfo(fname).path()

        self.mainWindow = QWidget()
        self.mainWindow.setMinimumSize(100,100)
        
        dpi=100
        a=self.extent[1]-self.extent[0]
        b=self.extent[3]-self.extent[2]
        self.fig = Figure((a,b),dpi=100)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.mainWindow)

        
        self.createContextMenu()

        self.canvas.setContextMenuPolicy(Qt.CustomContextMenu)
        self.connect(self.canvas, SIGNAL('customContextMenuRequested(const QPoint&)'), self.onContextMenu)        

        
        vBox1 = QVBoxLayout()
        vBox1.addWidget(self.canvas)



        self.mainWindow.setLayout(vBox1)
        
        if self.interval != None:
            naslov=str(self.interval[0]+(self.interval[1]-self.interval[0])/2)
            self.setWindowTitle("Mass: "+naslov)
        

        self.setCentralWidget(self.mainWindow)
        self.setContentsMargins(0,0,0,0)
        self.drawIntensityGraph(self.H)
                     
        
    def createContextMenu(self):
        
        #create contesxt menu
        self.popMenu = QMenu(self)
        self.applyFilter = QMenu('Apply filter',self)
        
        gaussianFilter1 = self.createAction("Gaussian smooth1", self.gaussianFilter1)
        gaussianFilter2 = self.createAction("Gaussian smooth2", self.gaussianFilter2)
        gaussianFilter3 = self.createAction("Gaussian smooth3", self.gaussianFilter3)
        gaussianFilter5 = self.createAction("Gaussian smooth5", self.gaussianFilter5)
        gaussianFilter10 = self.createAction("Gaussian smooth10", self.gaussianFilter10)
        medianFilter3 = self.createAction("Median filter3", self.medianFilter3)
        edgeDetectionX = self.createAction("Edge detection X", self.edgeDetectionX)
        edgeDetectionY = self.createAction("Edge detection Y", self.edgeDetectionY)
        edgeDetectionFilter = self.createAction("Edge detection Filter", self.edgeDetectionFilter)
                
        self.addActions(self.applyFilter, (gaussianFilter1, gaussianFilter2, gaussianFilter3, gaussianFilter5, gaussianFilter10,
                                           medianFilter3, None, edgeDetectionX, edgeDetectionY, edgeDetectionFilter))

        
        plainSave = self.createAction("Plain Save 100dpi",self.plainSave)
        savePyMCA = self.createAction("Save PyMCA", self.savePyMCA)
        undoAllFiltering = self.createAction("Undo all filtering", self.undoAllImageFiltering)
        
        self.popMenu.addMenu(self.applyFilter)
 
        self.addActions(self.popMenu, ( plainSave, savePyMCA, None, undoAllFiltering))

    def gaussianFilter1(self):
        im=ndimage.gaussian_filter(self.H, sigma=1)
        self.drawIntensityGraph(im)
        
    def gaussianFilter2(self):
        im=ndimage.gaussian_filter(self.H, sigma=2)
        self.drawIntensityGraph(im)
        
    def gaussianFilter3(self):
        im=ndimage.gaussian_filter(self.H, sigma=3)
        self.drawIntensityGraph(im)
        
    def gaussianFilter5(self):
        im=ndimage.gaussian_filter(self.H, sigma=5)
        self.drawIntensityGraph(im)

    def gaussianFilter10(self):
        im=ndimage.gaussian_filter(self.H, sigma=10)
        self.drawIntensityGraph(im)
        
    def medianFilter3(self):
        im=ndimage.median_filter(self.H, 3)
        self.drawIntensityGraph(im)

    def edgeDetectionX(self):
        
        im= ndimage.sobel(self.H, axis=0, mode='constant')
        self.drawIntensityGraph(im)
        
    def edgeDetectionY(self):
        
        im= ndimage.sobel(self.H, axis=1, mode='constant')
        self.drawIntensityGraph(im)        
        
    def edgeDetectionFilter(self):
        
        sx = ndimage.sobel(self.H, axis=0, mode='constant')
        sy = ndimage.sobel(self.H, axis=1, mode='constant')
        im = np.hypot(sx, sy)      
        self.drawIntensityGraph(im)        
        
    def undoAllImageFiltering(self):
        
        self.drawIntensityGraph(self.H)
        
    def onContextMenu(self, point):
        
        self.popMenu.exec_(self.canvas.mapToGlobal(point))       
        
    def calculateWindowGeometry(self):
        
        point = self.rect().topLeft()
        #print(point)
        globalPoint = self.mapToGlobal(point)
        #print("Zgornji levi rob: " + str(globalPoint))
        
        return self.width(), self.height()
        
        
    def drawIntensityGraph(self, data = None):
        """ draws 2D matrix data """
        #self.figure.clear()
        masa = "Ni intervala"
        if self.interval != None:# and len(self.interval)==2:
            masa = "m/z = {0:0.1f} - {1:0.1f}".format(self.interval[0],self.interval[1])
        
        #data = self.H
        
        self.maxC=max(max(x) for x in data)
        if data != None:
            self.fig.clear()
            self.axes = self.fig.add_subplot(1,1,1)
            self.im = self.axes.imshow(data, cmap="spectral", extent = self.extent)
            self.axes.xaxis.set_ticks([])
            self.axes.yaxis.set_ticks([])
            #self.axes.set_title(masa)
            self.fig.tight_layout(pad=0)
            self.canvas.draw()
            self.drawn = True
        
    def savePyMCA(self):
        fname = "testSave.csv"
        a=self.H.flatten()
        
        np.savetxt(fname,a,delimiter=',')        
                                
    def plainSave(self):
        
        #To morm se pogledat zakaj je vse to ce je kaj koristno        
        #fig_size = fig.get_size_inches()
        #w,h = fig_size[0], fig_size[1]
        #fig.patch.set_alpha(0)
        #if kwargs.has_key('orig_size'): # Aspect ratio scaling if required
        #    w,h = kwargs['orig_size']
        #    w2,h2 = fig_size[0],fig_size[1]
        #    fig.set_size_inches([(w2/w)*w,(w2/w)*h])
        #    fig.set_dpi((w2/w)*fig.get_dpi())
        #a=fig.gca()
        #a.set_frame_on(False)
        #a.set_xticks([]); a.set_yticks([])
        #plt.axis('off')
        #plt.xlim(0,h); plt.ylim(w,0) 
        dialog = plainSaveDialog(self.path, self)
        if self.drawn and dialog.exec_():
            dpi=int(dialog.leDPI.text())
            pad=float(dialog.lePad.text())
            fname= dialog.fname
            self.axes.xaxis.set_ticks([])
            self.axes.yaxis.set_ticks([])
            self.axes.set_xlabel("")
            self.axes.set_ylabel("")
            self.axes.set_title("")
            #self.fig.delaxes(self.fig.axes[1])
            #self.fig.tight_layout(pad=0)
            self.fig.subplots_adjust(left=None, bottom=None, right=None, top=None,wspace=None, hspace=None)
            self.fig.savefig(fname,dpi=dpi,bbox_inches='tight',pad_inches=pad)
            self.drawIntensityGraph(self.H)
            
        else:
            QMessageBox.warning(self,"No figure to save","there is no figure to save, reconsider your intention!")
        
        

#**********************Za dodajanje akcij (kopirano iz spectrum viewer)
    def addActions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def createAction(  self, text, slot=None, shortcut=None, 
                        icon=None, tip=None, checkable=False, 
                        signal="triggered()"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon("./images/{}.png".format(icon)))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action        

            

        
def main():
    
    app = QApplication(sys.argv)
    form = mplWindow2DLight()
    print("Frame Geometry1: ", str(form.frameGeometry()))
    form.setWindowFlags(Qt.FramelessWindowHint)
    form.show()
    initialSize = form.frameGeometry()
    print("Frame Geometry: ", str(initialSize))
    app.exec_()

if __name__ == "__main__":
    
    main()