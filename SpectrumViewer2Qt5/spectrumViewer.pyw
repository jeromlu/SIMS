# -*- coding: utf-8 -*-
"""
Created on Fri Mar 28 09:30:00 2014

@author: Administrator
"""

import sys, platform
import uuid



from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt5.QtWidgets import QFileDialog, QAction, QTextBrowser, QHBoxLayout
from PyQt5.QtWidgets import QDoubleSpinBox, QPushButton, QLineEdit
from PyQt5.QtWidgets import QGridLayout, QFrame, QMessageBox, QTextEdit
from PyQt5.QtWidgets import QDesktopWidget, QCheckBox, QApplication

from PyQt5.QtGui import QIcon, QIntValidator, QDoubleValidator, QFont, QCursor


from PyQt5.QtCore import QT_VERSION_STR, PYQT_VERSION_STR, QFileInfo
from PyQt5.QtCore import  Qt, QByteArray, QSettings, QFile, QPoint


from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from mpl_toolkits.axes_grid1 import ImageGrid #@UnresolvedImport
#from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes
#from mpl_toolkits.axes_grid1.inset_locator import mark_inset


import numpy as np
from scipy import optimize

import dataContainer #moj razred za vse potrebne podatke
import fitDialog #moj dialog 
import mplWindow2D #razred za prikazovanje posamezne 2D mape
import batchCalibrateDlg #razred za fitanje spektrov, ki se nahajojo v eni mapi
import imzMLdialog #dialog za nastavljanje parametrov za imzML fajle
import imzML
import propertiesDialog
import calibrateDialog
import timeOfFlightCalculator #izracun casa preleta iz podatkov
#import qrc_resources #ikone za razne menije

#from helpFunctionsSIMS import func  #moj fajl more bit sys.path
                                    #ali isti mapi kot MojGUI...py
                                    #rabim za fit pri kalibraciji



def func(x, a, b):
    return a*x*x+b
def func1(x, a, b):
    return a*x+b
def gauss(x, *p):
    A, mu, sigma = p
    return A*np.exp(-(x-mu)**2/(2.*sigma**2))
def isAlive(qobj):
    import sip
    try:
        sip.unwrapinstance(qobj)
    except RuntimeError:
        return False
    return True

def Newton(t,param = [205.318,170.904,-0.0107204,0.000115152]): #parametri za Arginin ena meritev (vedno prepisi)
    """newtonowa metoda za polinom tretje stopnje s koeficienti v seznamu param (dolg more bit vsaj 4)"""
    A=param[0]
    B=param[1]
    C=param[2]
    D=param[3]
    a=(3*B/D-(C/D)**2)/3
    b=(2*(C/D)**3-9*B*C/D**2+27*(A-t)/D)/27
    Di =(a/3)**3+(b/2)**2
    #temp1=-b/2+np.sqrt(Di) 
    #temp2=-b/2-np.sqrt(Di)
    #if temp1<0:
    #    ai=-(-temp1)**(1.0/3)
    #else:
    #    ai=temp1**(1.0/3)
    #if temp2<0:
    #    bi=-(-temp1)**(1.0/3)
    #else:
    #    bi=temp2**(1.0/3)
        
    #bi=(-b/2-np.sqrt(Di))**(1/3)
    stevec=0
    x0=(t-A)/B#(B+(t-A)*C/B+C*D*(t-A)**2/B**2)
    #x1 = (t-A)/(B+(t-A)*C/B+C*D*(t-A)**2/B**2)
    if Di<0:
        for i in range(10000):
            rezultat = x0 - (A+B*x0+C*x0**2+D*x0**3-t)/(B+2*C*x0+3*D*x0**2)
            stevec=stevec+1
            
            if abs(rezultat - x0) <1000*np.spacing(1):
                break
            x0=rezultat
    else:
        sol=np.roots(np.array([D,C,B,A-t]))
        x0=np.absolute(sol)[-1]
    return x0

Newton = np.vectorize(Newton)    
Newton.excluded.add(1)    


__version__ = "1.0.0"


class Form(QMainWindow):
    
    FONT = QFont("Courier", 10)#, QFont.Bold, True)
    NextId = 1
    Instances = set()
    currentWindowPosition = QPoint(0,0)

    
    def __init__(self, parent = None):
        super(Form, self).__init__( parent)
        
        self.data = dataContainer.listModeContainer() #instance of my data container
        self.vlineL = None #lines to get interval for calibration and fitting and integration
        self.vlineH = None
        self.calibrationPeaks = None
        self.p0 = [10000., 1020., 5.] #zacetni parametri za Gaussov fit
        self.gaussFitPlot = None
        
        
        desktop = QDesktopWidget()
        self.screenSize = desktop.screenGeometry()
        #print(self.screenSize)

        #self.setAttribute(Qt.WA_DeleteOnClose)
        self.create_menu()        
        self.create_main_window()
        self.create_status_bar()
        if not self.properties:
            print("Ni propertiesov !!!!  :D Zato jih nastavim. :P")
            self.properties = {"extent" : [0,2.543,0,1.4587],                   # x,y velikost map, default 10*1 klorov zark 5,8 MeV
                               "binning" : 11250,                               # binning za spekter(se zmeraj uporabljam range(binninga))
                               "density" : False,                               # ali so spektri normirani
                               "normed" : False,                                # ali so mape normirane ali ne
                               "thresholdFileSize" : 800,                       # kdaj javim, da ne gre vec loadat po hitrem postopku
                               "thresholdForMaps" : 300,                        #velikost fajla, da se risem 2D histogram
                               "massRangeOfInterest" : [0,500],                 #zacetna prikazana najvecja mapa po kalibraciji
                               "SimpleCalibrationModel" : True,                 #kater kalibracijski model bom uporabil (True) samo dva parametra  
                               "baseFolder" : r'C:\Dropbox\Sola\DoktoratFMF\MeV-SIMS\MERITVE',
                               "units" : "mm",
                               "part" : -1,
                               "lightMaps": False,
                               "numberOfHighestPeaks" : 5,
                               "2Dbinning" : 256,
                               "2Drange" : np.array([[-10, 32691], [-10, 32691]])}                    
            
        self.initializeCalibrationPeaks()
        
        self.setWindowTitle("SpectraViewer")

        self.peaks_cb.stateChanged.connect(self.addPeakLabels)
        self.spinBox_tresh.valueChanged.connect(self.addPeakLabels)
        self.pushButton_calibrate.clicked.connect(self.quickCalibrateHistogram)
        self.pbCalibrateMorePeaks.clicked.connect(self.acquirePeakList)        
        self.le_ch1.textChanged.connect(self.plotVerticalLines)
        self.le_ch2.textChanged.connect(self.plotVerticalLines)
        self.pushButton_maps.clicked.connect(self.mappingFewHighestPeaks)
        self.pushButton_mapsZ.clicked.connect(self.mappingFromFile)
        self.pushButton_mapOnClick.clicked.connect(self.mappingDataBetweenGreenRed)

        self.pushButton_commands.clicked.connect(self.executeCommands)
        self.pbNewton.clicked.connect(self.deletePlottedFit)
                            
        
        self.canvas.mpl_connect('key_press_event', self.onclickButton)
        self.canvas.mpl_connect('key_release_event', self.onclickButtonR)
        



   
    
    def create_menu(self):
        
        self.fileMenu = self.menuBar().addMenu("&File")
        self.menuBar().setFont(Form.FONT)
        
        fileLoadAction = self.createAction("&Load file",
            shortcut="Ctrl+L", slot=self.openFile, tip="Load a file", icon="fileOpen")
        fileSaveimzML = self.createAction("&Save as imzML", self.exportAsimzML, "Ctrl+S",
                "fileSaveimzML", "Create imzML file format and saves it to disk (DAngerous)")
        fileQuitAction = self.createAction("&Quit", self.close,
                "Ctrl+Q", "fileQuit", "Close the application")
        fileExportAction = self.createAction("&Export spectrum", self.exportSpectrumToText,
                "Ctrl+E", "fileExport", "Export spectrum to text file")
        fileSaveSorts = self.createAction("Sa&ve current sorts", self.saveSorts,
            "Ctrl+Q", "fileExport", "Save sorts intervals to text file. Only masses.")
            
        self.fileMenuActions = (fileLoadAction, fileSaveimzML, fileExportAction, fileSaveSorts, None, 
                                          fileQuitAction)
                
        self.fileMenu.aboutToShow.connect(self.updateFileMenu)


                
        self.toolsMenu = self.menuBar().addMenu("&Tools")        
        
        toolsIntegrateAction = self.createAction("&Integrate", self.integrate, 
                "Ctr+Alt+I", "toolsIntegrate", "Add all counts between black lines")
        toolsFitAction = self.createAction("&Fit", self.fitDlg, 
                "Ctr+Alt+F", "toolsFit", "Fits gaussian to the data betweene two lines")
                
        toolsBatchCalibrateAction = self.createAction("Batch calibrate", self.batchCalibrate,
                "Ctrl+Alt+B", "toolsBatchCalibrate", "Calibrate and export selected specta in a folder.")
                
        toolsUndoCalibration = self.createAction("Undo Calibration", self.undoCalibration,
                "Ctrl+Alt+U", "toolsUndoCalibration", "Resets mass axis back to the channels.")

        toolsTOFcalculator = self.createAction("Calculate time-of-flight", self.timeOfFlightCalculationDlg,
                "Ctrl+Alt+T", "toolsTOFcalculator", "Calculates TOF from physical data.")
                
        toolsPropertiesAction = self.createAction("Properties", self.setProperties,
                "Ctrl+Alt+P", "toolsProperties", "Set some properties about measurement and application")
        toolsCloseAllMaps = self.createAction("Close all Maps", self.closeAllMaps,
                "Ctrl+Alt+C", "toolsCloseAll", "Close all active windows (created 2D maps)")
                


        self.addActions(self.toolsMenu, (toolsIntegrateAction, toolsFitAction,
                                          toolsBatchCalibrateAction, toolsUndoCalibration, toolsTOFcalculator, toolsCloseAllMaps,
                                          None, toolsPropertiesAction))
        
        
        self.help_menu = self.menuBar().addMenu("&Help")
        
        helpAboutAction = self.createAction("About", self.helpAbout, icon="helpAbout")
        helpHelpAction = self.createAction("Help", self.helpAbout, icon = "helpHelp")
            
            
        self.addActions(self.help_menu, (helpHelpAction,None,helpAboutAction))
        

    def updateFileMenu(self):
        self.fileMenu.clear()
        self.addActions(self.fileMenu, self.fileMenuActions[:-1])
        current = self.data.filename()
        recentFiles = []
        for fname in self.recentFiles:
            if fname != current and QFile.exists(fname):
                recentFiles.append(fname)
        if recentFiles:
            self.fileMenu.addSeparator()
            for i, fname in enumerate(recentFiles):
                action = QAction(QIcon("./images/icon.png"),
                        "&{} {}".format(i + 1, \
                                    fname.split('/')[-2]), self)
                action.setData(fname)
                action.triggered.connect(self.loadFile)
                self.fileMenu.addAction(action)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.fileMenuActions[-1])
        
        
    def create_main_window(self):
        
        self.mainFrame = QWidget()
        self.mainFrame.setFont(Form.FONT)
        self.mainFrame.setMinimumSize(1100,500)
        
        
        self.dpi=100
        self.fig = Figure((9,3.0),dpi=self.dpi)   #naredim sliko in dolocim velikost aspect ratio in dpi
        self.canvas = FigureCanvas(self.fig)        # naredim canvas na sliki, kjer risem in osvezujem
        self.canvas.setParent(self.mainFrame)       #dolocim kaj je foter od kanvasa in torej tudi slike
        self.canvas.setFocusPolicy(Qt.ClickFocus ) #da mi dela press_key_event
        self.canvas.setFocus()                     # v mpl_connect drugac ne dela
        self.axes = self.fig.add_subplot(111)       # nardim os na kateri pol tudi vse spreminjam in dodajam, risem ...
        self.mpl_toolbar = NavigationToolbar(self.canvas, self.mainFrame)   #dodam toolbar povezan s canvasom na main-frame
        
        #cursor=Cursor(self.axes, self.canvas)
        #self.canvas.mpl_connect('motion_notify_event', cursor.mouse_move)        NE DELA
        
        self.axes.format_coord = self.format_coord


        
        
        self.textInfo = QTextBrowser()
        self.textInfo.setFrameStyle(QFrame.StyledPanel|QFrame.Sunken)
        self.textInfo.setMinimumWidth(200)
        self.textInfo.setMaximumWidth(300)
        self.textInfo.setMinimumHeight(300)
        
        
        self.peaks_cb = QCheckBox('Show peaks above:')
        self.peaks_cb.setChecked(False)
        
        self.compare_cb = QCheckBox('Hold previous histogram')
        self.compare_cb.setChecked(False)        
        
        self.spinBox_tresh = QDoubleSpinBox()
        self.spinBox_tresh.setValue(0.25*100)
        self.spinBox_tresh.setRange(0,100)
        self.spinBox_tresh.setSuffix(' %')
        self.spinBox_tresh.setDecimals(1)
        self.spinBox_tresh.setSingleStep(0.25)
        
        self.pushButton_calibrate = QPushButton("Q Ca&lib")
        self.pushButton_calibrate.setToolTip("Calibrates spectra to the red and green line")
        self.pbCalibrateMorePeaks = QPushButton("Cali&brate")
        self.pbCalibrateMorePeaks.setToolTip("Calibrates to  the peak list with least square method")
        self.pbNewton = QPushButton("Newton")
        
        self.le_ch1 = QLineEdit("3070")#('385')
        self.le_ch1.setValidator(QDoubleValidator(0., 10000.,2))
        self.le_ch1.setMaximumWidth(100)
        self.le_ch2 = QLineEdit("3100")#('2482')
        self.le_ch2.setValidator(QDoubleValidator(0., 10000.,2))
        self.le_ch2.setMaximumWidth(100)

        self.le_mass1 = QLineEdit('1')
        self.le_mass1.setValidator(QDoubleValidator(0, 10000.,1))
        self.le_mass1.setMaximumWidth(100)
        self.le_mass2 = QLineEdit('175.2')
        self.le_mass2.setValidator(QDoubleValidator(0, 10000.,1))
        self.le_mass2.setMaximumWidth(100)

        self.label_ch1 = QLabel("Ch1:")
        self.label_ch1.setMaximumWidth(100)
        self.label_ch2 = QLabel("Ch2:")
        self.label_ch2.setMaximumWidth(100)
        self.label_mass1 = QLabel('Mass1')
        self.label_mass1.setMaximumWidth(100)
        self.label_mass2 = QLabel('Mass2')
        self.label_mass2.setMaximumWidth(100) 

        self.pushButton_maps = QPushButton('Maps - many')
        self.pushButton_mapsZ = QPushButton('Maps - from file')
        self.pushButton_mapOnClick = QPushButton('Map - on click Green line')

        self.label_stDogodkov = QLabel('num Data')
        
        moreButton = QPushButton("Only tech person")
        moreButton.setFixedWidth(100)
        moreButton.setCheckable(True)
        
        moreFrame = QFrame()
        moreFrame.setMaximumHeight(300)
        
        label_special = QLabel('special User: ')
        text='self.axes.text(2000,9000,"tadada",fontsize=30)\n\
        self.axes.set_xlim(0,300)\n\
        self.axes.set_ylim(0,10000)\n\
        self.axes.annotate("[M+H]$^+$",xy=(175.2, 3000), size=16,xycoords="data",xytext=(155, 20000), textcoords="data",arrowprops=dict(arrowstyle="->",connectionstyle="arc3"),)\n\
        self.axes.lines[0].set_color("black")\n\
        self.canvas.draw()'

        self.le_commands = QTextEdit()#QLineEdit('Samo za posvecene')
        self.le_commands.insertPlainText(text)
        #self.le_commands.setLineWrapMode(0)
        self.pushButton_commands = QPushButton("Execute")
        
        
        hBox1=QHBoxLayout()      
        hBox1.addWidget(self.peaks_cb)
        hBox1.addWidget(self.spinBox_tresh)
        hBox1.addWidget(self.pushButton_calibrate)
        hBox1.addWidget(self.mpl_toolbar)
            
        
        vBox1 = QVBoxLayout()
        vBox1.addWidget(self.canvas)
        vBox1.addLayout(hBox1)
        
        
        hBox2= QHBoxLayout()
        hBox2.addLayout(vBox1)
        hBox2.addWidget(self.textInfo)
        
        hBox3= QHBoxLayout()
        hBox3.addWidget(self.label_ch1)
        hBox3.addWidget(self.le_ch1)
        hBox3.addWidget(self.label_mass1)
        hBox3.addWidget(self.le_mass1)        
        hBox3.addWidget(self.label_ch2)
        hBox3.addWidget(self.le_ch2)
        hBox3.addWidget(self.label_mass2)
        hBox3.addWidget(self.le_mass2)
        hBox3.addWidget(self.compare_cb)
        hBox3.addWidget(self.pbCalibrateMorePeaks)
        hBox3.addWidget(self.pbNewton)
        hBox3.addStretch()        
        
        hBox4 = QHBoxLayout()
        hBox4.addWidget(self.pushButton_maps)
        hBox4.addWidget(self.pushButton_mapsZ)
        hBox4.addWidget(self.pushButton_mapOnClick)
        hBox4.addWidget(moreButton)
        
        hBox5 = QHBoxLayout()
        hBox5.addWidget(label_special)
        hBox5.addWidget(self.le_commands)
        hBox5.addWidget(self.pushButton_commands)
        moreFrame.setLayout(hBox5)
        
        grid = QGridLayout()
        grid.addLayout(hBox2, 0, 0)
        grid.addLayout(hBox3, 1, 0)
        grid.addLayout(hBox4, 2,0)
        grid.addWidget(moreFrame, 3, 0)
     

        #grid.setSizeConstraint(QLayout.SetFixedSize)
        self.mainFrame.setLayout(grid)
        
        self.setCentralWidget(self.mainFrame)
  
        moreFrame.hide()
        moreButton.toggled.connect(moreFrame.setVisible)
        self.restorePreviousState()
        #print(self.recentFiles)
        

    def restorePreviousState(self):
        """nalozim zacetni fajl in odperm okno z nastavitvami 
        od prejsnjega sessiona"""
        
        
        settings = QSettings()
        self.recentFiles = settings.value("RecentFiles") or []
        self.restoreGeometry(settings.value("MainWindow/Geometry",
                QByteArray()))
        self.restoreState(settings.value("MainWindow/State",
                QByteArray()))
        self.properties = settings.value("Properties")
        self.data.setExportFilename(settings.value("exportFilename"))
        self.loadInitialFile()

        
            
            
    def create_status_bar(self):
        """nardi staus bar kjer pokazem stevilo dogodkov v prebranem fajlu"""
        
        status = self.statusBar()
        status.setSizeGripEnabled(False)
        status.addPermanentWidget(self.label_stDogodkov)
        status.showMessage("Ready", 10000)
        
        
        


#********************************************* SLOTS

    def format_coord(self, x, y):
        """spremenim izpis koordinat v navigation toolbaru,
        da napise kok je v kanalih in lahko takoj vpisem vrh v kalibracijo"""
        if self.data.calibrated():
            ch = self.data.calParam()[0]+np.sqrt(x)*self.data.calParam()[1]+\
            self.data.calParam()[2]*x+np.sqrt(x)**3*self.data.calParam()[3]
            string = "x = {0:1.4f} y = {1:1.4f} ch = {2:1.0f}".format(x,y,ch)
        else:      
            string = "x = {0:1.4f} y = {1:1.4f}".format(x,y)
        return string
        
        
    def executeCommands(self):
        """executes commands that are inserted in text box"""
        try:
            commands = self.le_commands.toPlainText().split("\n")
            for com in commands:           
                exec(com)
        except Exception as e:
                excType, excObj, excTb =sys.exc_info()
                error = "There were errors to:\n {0}, {1}".format(excType,e)
                QMessageBox.critical(self,"Ni slo",error)
            
        
    def okToContinue(self):
        """checks if changes are saved or not (tega se ne uporablam sam se mi zdi fajn)"""
        if True:
            reply = QMessageBox.question(self,
                    "Spectrum Viewer - Unsaved Calibration",
                    "Save unsaved changes?",
                    QMessageBox.Yes|QMessageBox.No|QMessageBox.Cancel)
            if reply == QMessageBox.Cancel:
                return False
            elif reply == QMessageBox.Yes:
                return True#self.fileSave()
        return True   
        
        
    def fitDlg(self):
        
        self.fitDialog = fitDialog.fitDialog(self.p0, self)
        self.fitDialog.changed.connect(self.fit)
        self.fitDialog.show()
        self.p0 = self.fitDialog.p0
                
        
    def fit(self):
        """fita gaussovo krivuljo na podatke izbrane z rdeco in modro crto"""
        
        #pass
        QMessageBox.information(self,"Initial fit parameters",str(self.p0))
        if self.data.hasHistogram():
            
            
            
            interval = np.array(\
                [float(self.le_ch1.text()),float(self.le_ch2.text())])

            
            if self.data.calibrated():
                interval = self.data.calParam()[0]+np.sqrt(interval)*self.data.calParam()[1]+\
                    self.data.calParam()[2]*interval+np.sqrt(interval)**3*self.data.calParam()[3]
                xData = self.data.massAxis()[round(interval[0]):round(interval[1])]

            else:
                
                xData = self.data.bins()[round(interval[0]):round(interval[1])]
                
            
            coeff, var_matrix = \
                optimize.curve_fit(gauss, xData, 
                                   self.data.n()[round(interval[0]):round(interval[1])], p0=self.p0)
            if self.fitDialog.showCurveCheckBox.isChecked():
                xFine = np.arange(xData[0],xData[-1],(xData[-1]-xData[1])/500)
                hist_fit = gauss(xFine, *coeff)
                self.gaussFitPlot = self.axes.plot(xFine,hist_fit)
                self.canvas.draw()
            resolucija = coeff[1]/coeff[2]/(2*np.sqrt(2*np.log(2))) #resolucija
            QMessageBox.information(self,"Fitted parameters",str(coeff)+"\nresolucija: "+str(resolucija))
            
    def timeOfFlightCalculationDlg(self):
        """morm se malo popravit"""
        
        dlg = timeOfFlightCalculator.TOFcalculatorDialog()
        dlg.changed.connect(self.timeOfFlightCalculation)
        dlg.show()
    
    def timeOfFlightCalculation(self):
        pass
        
    def closeAllMaps(self):
        
        for window in Form.Instances:
            if isAlive(window):
                window.close()
        Form.currentWindowPosition=QPoint(0,0)
                
    def deletePlottedFit(self):
        

        if len(self.gaussFitPlot)>0:
            self.axes.lines.remove(self.gaussFitPlot[0])
            self.canvas.draw()


    def integrate(self):
        """ funkcija za sestevanje vseh kanalov med rdeco in zeleno crto
        """
        
        if self.data.hasHistogram():
            #dolocim interval integracije v kanalih (isto kot za mape)
            if self.data.calibrated():
                edge1 = self.data.calParam()[0]+np.sqrt(float(self.le_ch1.text()))*self.data.calParam()[1]+\
                    self.data.calParam()[2]*float(self.le_ch1.text())+np.sqrt(float(self.le_ch1.text()))**3*self.data.calParam()[3]
                edge2 = self.data.calParam()[0]+np.sqrt(float(self.le_ch2.text()))*self.data.calParam()[1]+\
                    self.data.calParam()[2]*float(self.le_ch2.text())+np.sqrt(float(self.le_ch2.text()))**3*self.data.calParam()[3]
            else:
                edge1 = float(self.le_ch1.text())
                edge2 = float(self.le_ch2.text())
        
            sumInt = self.data.n()\
            [round(edge1):round(edge2)].sum()
            QMessageBox.information(self,
            "Integrated between "+self.le_ch1.text()+" - "+self.le_ch2.text(),
            '<p align=center><font size = 9 color = red > Total area:{0:0,.2f}</font></p>'.format(sumInt),
            QMessageBox.Ok)         
        
        
    def onclickButton(self, event):
        """nastavljanje crte zelena"""
        
        
        if event.key == 'g':
            self.connection=self.canvas.mpl_connect('button_press_event', self.onclick)
            
    def onclickButtonR(self, event):
        """nastavljanje crte rdeca"""
 
        if event.key == 'g' and self.connection:
            self.canvas.mpl_disconnect(self.connection)
            
    def onclick(self, event):
        if event.inaxes!=self.axes: return
        #print('button=%d, x=%d, y=%d, xdata=%f, ydata=%f'%(
        #    event.button, event.x, event.y, event.xdata, event.ydata))
    
        if event.button == None:
            return    
    
        if event.button == 1 and event.xdata<float(self.le_ch2.text()):
            self.le_ch1.setText('{0:0.1f}'.format(event.xdata))
        if event.button == 3 and event.xdata>float(self.le_ch1.text()):
            self.le_ch2.setText('{0:0.1f}'.format(event.xdata))             



            
            
    def openFile(self):
        
        home = self.properties["baseFolder"]
        #home = r"C:\Documents and Settings\Administrator\My Documents\SIMS meritve\MERITVE"
        path = (QFileInfo(self.data.filename()).path()
                if self.data.filename() else home)

        dlg = QFileDialog()
        dlg.setViewMode(QFileDialog.Detail)        
        fname = dlg.getOpenFileName(self, 'Open file', 
                                                 path, "Binary file (*.bin)")
        self.loadFile(fname)
        
        
        
    def loadFile(self, fname = None):
        """metoda, ki nalozi podatke in narise histogram, ce je fname None
           potem pogleda ce je akcija in nardi akcijo"""
           
        if fname is None:
            action = self.sender()
            if isinstance(action, QAction):
                fname = action.data()
                if not self.okToContinue():
                    return
            else:
                return
        binning = self.properties["binning"]
        density = self.properties["density"]
        size = self.properties["thresholdFileSize"]
        self.data.setPart(self.properties["part"])
        if fname:
            ok, msg = self.data.load(fname, binning, density, size)
            #nastavim range za 2D mapo glede na t od kje do kje so podatki
            if self.data.rawData() != np.array([]):
                self.properties['2Drange']=np.array( \
                    [[self.data.rawData()['x'].min(),self.data.rawData()['x'].max()], \
                    [self.data.rawData()['y'].min(),self.data.rawData()['y'].max()]])

            #dodam v recent files, da lahko kasnej odpiram pred kratkim odprte dadoteke
            self.addRecentFile(fname)

            self.textInfo.clear()
            self.textInfo.append(self.data.infoText())
            self.statusBar().showMessage(msg, 500000)
            self.label_stDogodkov.setText('{0:,.0f} dogodkov' \
                                                .format(self.data.size()))
            self.plot_Histogram()
            self.le_ch1.setText('395.5') #naredi da ti nastavi na prvi vrh
            self.le_ch2.setText('2482.5')
            self.le_mass1.setText('1')
            self.le_mass2.setText('175.2')
            self.plotVerticalLines()
            
    def loadInitialFile(self):
        """ ce imam fname od prej nalozim ta histogram avtomatsko"""

        settings = QSettings()
        fname = settings.value("LastFile")
        if fname and QFile.exists(fname):
            self.loadFile(fname)
                
    
    def addRecentFile(self, fname = None):
        """dodam trenutni fajl med recent files"""
        if fname not in self.recentFiles:
            self.recentFiles = [fname] + self.recentFiles[:8]
            
    def exportAsimzML(self):
        
        UUID = uuid.uuid1()
        fname = self.data.exportFilename()
        if not self.data.calibrated():
            QMessageBox.warning(self,"Warning, no mass axis", "You have to calibrate mass spectra first")
            return
        dialog = imzMLdialog.imzMLConverterDialog(fname)
        message="Pederu !!!"
        if dialog.exec_():
            pixels = int(dialog.lePixels.text())
            binning = int(dialog.leBinning.text())
            massRange = np.array([float(dialog.leMassRangeLow.text()),float(dialog.leMassRangeHigh.text())])
            fname = dialog.path
            formatN = dialog.cbNumberFormat.currentText()
            reducedFormat = dialog.cbSpecialFormat.isChecked()
            
            progressDialog = dataContainer.MyCustomProgressBar(self.data.rawData(), pixels, binning, UUID,
                                                               self.data.calParam(), fname, massRange, formatN, reducedFormat)
            progressDialog.exec_()
            
            if not reducedFormat:
                ok,message = self.data.exportToimzMLFormat(pixels, binning, fname,massRange, UUID)
                self.statusBar().showMessage(message, 50000)
            

        
        
        
    def exportSpectrumToText(self):

        fname = self.data.exportFilename() if self.data.exportFilename() else QFileInfo(self.data.filename()).path()
        
        fname = QFileDialog.getSaveFileName(self, "Export Spectrum", 
                                            fname, "Text files (*.txt)")
        if fname:
            ok, msg = self.data.exportToTxt(fname)
            self.statusBar().showMessage(msg, 5000)
            return ok
        return False
        
    def savePyMCAmaps(self):
        """da lahko pol nardim edf file format in uporabljam pyMCA za risanje profilov"""
        pass        
    def saveSorts(self):
        
        fname = self.data.filename()


        error = None
        fh = None        

        try:
            
            if self.data.calibrated():
                fh = open(QFileInfo(fname).path()+"/SortsL.srt",'w')
                for window in Form.Instances:
                    
                    if isAlive(window) and window.calibrated:
                        interval = window.interval
                        fh.write("Luka\t{}\t{}\n".format(interval[0],interval[1]))
            else:
                QMessageBox.information(self, 'Message',
                                        "Spectrum needs to be calibrated first!", QMessageBox.Ok)
        except EnvironmentError as e:
            error = "Failed to save sorts: {}".format(e)
        finally:
            if fh is not None:
                fh.close()
            if error is not None:
                msg = error
            if error is None:
                msg = "Saved calibrated spectra to {}".format(
                        QFileInfo(fname).fileName())
            self.statusBar().showMessage(msg, 500000)

    def plot_Histogram(self):
        
        
        if self.data.hasHistogram():
              
            massRange = self.properties["massRangeOfInterest"]
            n = self.data.n()        
            
            if self.data.calibrated():
                bins = self.data.massAxis()
            else:
                bins = self.data.bins()
                
            if self.peaks_cb.isChecked():
                if not(self.compare_cb.isChecked()):
                    self.fig.clear()
                    self.axes = self.fig.add_subplot(111)
                self.axes.step(bins ,n,where='mid')
                self.axes.set_title('Histogram '+self.data.filename().split('/')[-2])
                self.axes.set_ylabel(r"Intensity")
                if self.data.calibrated():
                    self.axes.set_xlim(massRange[0],massRange[1])
                    self.axes.set_xlabel(r"m/z [u]")
                else:
                    self.axes.set_xlabel(r"Channel")
                self.axes.set_ylim(0, 1.06* max(n))

                
            else:
                if not(self.compare_cb.isChecked()):
                    self.fig.clear()
                    self.axes = self.fig.add_subplot(111)
                self.axes.step(bins ,n,where='mid')
                self.axes.set_title('Histogram '+self.data.filename().split('/')[-2])
                self.axes.set_ylabel(r"Intensity")
                #self.axes.set_xlim(0, max(bins))
                if self.data.calibrated():
                    self.axes.set_xlim(massRange[0],massRange[1])
                    self.axes.set_xlabel(r"m/z [u]")
                else:
                    self.axes.set_xlabel(r"Channel")
                self.axes.set_ylim(0, 1.06* max(n))
                
            self.axes.format_coord = self.format_coord
            self.canvas.draw()




    def plotVerticalLines(self):
        """narisem rdeco in zeleno crto, istocasno pa odstranim prejsnji"""        
        
        if self.le_ch1.text() and len(self.axes.lines) > 0:
            
            
            maxN = self.data.maxN()
            if self.vlineL and self.vlineH and len(self.axes.collections) > 0:
                self.axes.collections.remove(self.vlineL)
                self.axes.collections.remove(self.vlineH)
            self.vlineL = self.axes.vlines(float(self.le_ch1.text()), 
                          0,1.2 * maxN, color = 'g',linewidth=1)
            self.vlineH = self.axes.vlines(float(self.le_ch2.text()), 
                          0,1.2 * maxN, color ='r',linewidth=1)
            self.canvas.draw()
            

    def addPeakLabels(self):
        """dodam vrednosti vrhov (se velik za izboljsat)"""
        
        #print("getXlim:",self.axes.get_xlim())
        if self.peaks_cb.isChecked() and self.data.hasHistogram():
            self.axes.texts = []
            self.data.maxima()
            s=self.data.maximaBins()
            maxima = self.data.maximaN()
            maskPart = maxima > self.spinBox_tresh.value()/100 * self.data.maxN()
            maskx= np.logical_and((min(self.axes.get_xlim())<s),( s < max(self.axes.get_xlim())))
            masky = np.logical_and((min(self.axes.get_ylim())<maxima),( maxima < max(self.axes.get_ylim())))
            mask = np.logical_and(np.logical_and(maskx, maskPart),masky)
            #print(self.axes.collections)
            #print(self.axes.patches)
            #print(self.axes.lines)
            #print(self.axes.texts)
            #print('\n')
            for x,y in zip(s[mask],maxima[mask]):
                self.axes.text(x,y,'{0:1.1f}'.format(x),fontsize=10,rotation="horizontal")
            
            #print(self.axes.collections)
            #print(self.axes.patches)
            #print(self.axes.lines)
            #print(self.axes.texts)
        else:
            self.axes.texts = []
            
        self.canvas.draw()
        
#***********************************************Metode povezane s kalibracijo
        
    def initializeCalibrationPeaks(self):
        """nastavi kalibracijske vrhove na zacetne vrednosti"""
        
        xdata = np.array([float(self.le_mass1.text()),float(self.le_mass2.text())])
        ydata = np.array([float(self.le_ch1.text()),float(self.le_ch2.text())])
        self.calibrationPeaks = {"xData" : xdata, "yData" : ydata}
        
        
    def quickCalibrateHistogram(self):
        """hitra kalibracija, samo dva vrhova(tista na main interfacu)"""
        
        xdata = np.array([float(self.le_mass1.text()),float(self.le_mass2.text())])
        ydata = np.array([float(self.le_ch1.text()),float(self.le_ch2.text())])
        self.calibrationPeaks = {"xData" : xdata, "yData" : ydata}
        
        if not self.data.hasHistogram():
            QMessageBox.warning(self,"Warning","First you have to load some data...")
            return
        
        self.calibrateHistogram()
        self.plot_Histogram()
        self.le_ch1.setText(self.le_mass1.text())
        self.le_ch2.setText(self.le_mass2.text())
        
        
    def acquirePeakList(self):
        """preberem seznam vrhov za kalibracijo iz calibrateDialoga"""
        
        self.dialog = calibrateDialog.calibrationDialog(self.calibrationPeaks, QFileInfo(self.data.filename()).path(), self)
        self.dialog.changed.connect(self.calibrateHistogramPeakList)
        self.dialog.pbFillFromRedLine.clicked.connect(self.fill)
        self.dialog.show()
        
        
    def fill(self):
        self.dialog.fill(self.le_ch2.text())
        
        
    def calibrateHistogramPeakList(self):
        """kalibracija z uporabo vec vrhov, uporabim model izbran v oknu properties(4 ali 2 kalibracijska parametra)"""
        
        if not self.data.hasHistogram():
            QMessageBox.warning(self,"Warning","First you have to load some data...")
            return        
        
        self.calibrationPeaks = self.dialog.calibrationPeaks
        self.data.undoCalibration()
        self.calibrateHistogram()
        self.plot_Histogram()
        self.le_ch1.setText(str(self.calibrationPeaks["xData"][0]))
        self.le_ch2.setText(str(self.calibrationPeaks["xData"][-1]))


        
    def leastSquareLinearFit(self, Xdata, Ydata, sigma=None):
        """fit najmanjših kvadratov za linearno funkcijo (za razlago Luis Lyons)
           vrne se parametra C in D, ampak kot nulo"""
        if not sigma:
            sigma = np.ones(len(Xdata))
        one = (1/sigma**2).sum()
        x = (Xdata/(sigma**2)).sum()
        y = (Ydata/(sigma**2)).sum()
        xy = ((Xdata*Ydata)/(sigma**2)).sum()
        x2 =((Xdata**2)/(sigma**2)).sum()
        
        b=(one*xy-x*y)/(one*x2-x**2)
        a=(x2*y-x*xy)/(x2*one-x**2)
        return np.array([a,b, 0, 0, 1])  #Peti pove ali sem uporabil model z stirimi parametri(0) ali samo dvema(1)
        
        
    def leastSquarePolinomialFit(self, Xdata, Ydata, sigma=None):
        """fit najmanjših kvadratov za linearno funkcijo (za razlago glej Bevington)
           vrne 5 parametre"""
        if not sigma:
            sigma = np.ones(len(Xdata))
        b=np.array([Xdata**0,Xdata,Xdata**2,Xdata**3]).transpose()
        beta=np.dot(Ydata,b)
        
        alfa=[]
        for i in range(4):
            c=np.sum(np.array([Xdata**i,Xdata**(i+1),Xdata**(i+2),Xdata**(i+3)]).transpose(),axis=0)
            alfa.append(c)
        alfa=np.asarray(alfa)

        return np.append(np.dot(np.linalg.inv(alfa),beta),0)  #Peti pove ali sem uporabil model z stirimi parametri(0) ali samo dvema(1)
        
    def undoCalibration(self):
        """iznici kalibracijo, vrne se nazaj na raw kanale (kam postavi crte je slabo narejeno)"""
        if self.data.calibrated():
            self.data.undoCalibration()
            self.plot_Histogram()
            self.le_ch1.setText(str(395.5))
            self.le_ch2.setText(str(2482.50))
        else:
            QMessageBox.warning(self, "Cannot undo calibration" , "Not calibrated or no data loaded")

        
    def calibrateHistogram(self):
        
        #temp = np.array([float(self.le_ch1.text()),float(self.le_ch2.text())])
        #self.ydata = np.array([float(self.le_mass1.text()),float(self.le_mass2.text())])
        
        xdata = self.calibrationPeaks["xData"]
        tempY =  self.calibrationPeaks["yData"]

        
        if self.data.calibrated():    #vse kalibriram iz kanalov zato morm podatke pretvorit v kanale
                ydata = self.data.calParam()[0]+np.sqrt(tempY)*self.data.calParam()[1]+\
                self.data.calParam()[2]*tempY+np.sqrt(tempY)**3*self.data.calParam()[3]
        else:
            ydata = tempY
            
        
        #izracun parametrov glede na izbran model in stevilo vrhov (lahko so problemi z Newtonovo metodo, treba je pametno izbrat vrhove)
        if len(ydata) == 2:
            poptB = (ydata[1]-ydata[0])/(np.sqrt(xdata[1])-np.sqrt(xdata[0]))
            poptA = (np.sqrt(xdata[0])*ydata[1]-np.sqrt(xdata[1])*ydata[0])/(np.sqrt(xdata[0])-np.sqrt(xdata[1]))
            popt1 = (poptA, poptB, 0, 0, 1)                                 #Peti pove ali sem uporabil model z stirimi parametri(0) ali samo dvema(1)
            mass = (self.data.bins()-popt1[0])/popt1[1]
        elif len(ydata) > 2 and self.properties["SimpleCalibrationModel"]:
            popt1 = self.leastSquareLinearFit(np.sqrt(xdata) ,ydata)
            mass = (self.data.bins()-popt1[0])/popt1[1]
        elif len(ydata) > 3 and not self.properties["SimpleCalibrationModel"]:
            popt1 = self.leastSquarePolinomialFit(np.sqrt(xdata) ,ydata)
            print("parametri:",popt1)
            mass = Newton(self.data.bins(),popt1)
        else:
            QMessageBox.warning(self, "Wrong calibration" , "Something is wrong with the number of choosen peaks")
            return

            
        #infoString ="Values of fitted parameters are:\n" +"<font size = 10 color = red > Param: {} </font>".format(popt1[0:4]) + model
        infoString="<p>Values of fitted parameters are:</p> <p><ul><font size = 5 color = black > \
                    <li>A: {0:.2f}</li> \
                    <li>B: {1:.2f}</li> \
                    <li>C: {2:.5f}</li> \
                    <li>D: {3:.5f}</li> \
                    </font><ul></p>".format(popt1[0],popt1[1],popt1[2],popt1[3])#+model
        
        
                
        QMessageBox.information(self, "Fitted parameters" ,  infoString)               
        mass = mass**2
        self.data.addMassAxis(mass, popt1)

        
    def batchCalibrate(self):
        
#        if not self.data.hasHistogram():
#            QMessageBox.warning(self,"Warning","First you have to load some data...")
#            return
        
        if self.data.filename():
            fname = self.data.filename()
            
        else:
            fname = r"C:/Dropbox/Sola/DoktoratFMF/MeV-SIMS/MERITVE/kurac/kji" #expanduser("~")
        if not self.calibrationPeaks:
            QMessageBox.critical(self,"Warning", "No calibration peaks")
            return   
        dialog = batchCalibrateDlg.batchCalibrateDlg(self.calibrationPeaks, fname,  self)
        if dialog.exec_():
            for measurement in dialog.choosen:
                self.data.load(dialog.home+"/"+measurement+"/"+"ListMode.bin")
                self.calibrateHistogram()
                self.data.exportToTxt(dialog.home+"/"+measurement+".txt")
                
                
                self.printInfo("Done!!")
            self.plot_Histogram()

        
        
#***************************************Nastavim Lastnosti Aplikacije
        
    def setProperties(self):
        

        dialog = propertiesDialog.Form(self.properties, self)
        if dialog.exec_():
            self.properties["density"] = dialog.properties["density"]
            self.properties["normed"] = dialog.properties["normed"]
            self.properties["SimpleCalibrationModel"] = dialog.properties["SimpleCalibrationModel"]
            self.properties["massRangeOfInterest"] = dialog.properties["massRangeOfInterest"]
            self.properties["thresholdForMaps"] = dialog.properties["thresholdForMaps"]
            self.properties["thresholdFileSize"] = dialog.properties["thresholdFileSize"]
            self.properties["extent"] = dialog.properties["extent"]
            self.properties["units"] = None
            self.properties["part"] = dialog.properties["part"]
            self.properties["lightMaps"] = dialog.properties["lightMaps"]
            self.properties["numberOfHighestPeaks"] = dialog.properties["numberOfHighestPeaks"]
            self.properties["2Drange"] = dialog.properties["2Drange"]
            self.properties["2Dbinning"] = dialog.properties["2Dbinning"]

            
        
#*************************************Reimplemented Events
        
    def closeEvent(self, event):
        
        if True:
            #print(self.recentFiles)
            settings = QSettings()
            settings.setValue("LastFile", self.data.filename())
            settings.setValue("RecentFiles", self.recentFiles or [])
            settings.setValue("MainWindow/Geometry", self.saveGeometry())
            settings.setValue("MainWindow/State", self.saveState())
            settings.setValue("Properties", self.properties)
            #if self.data.exportFilename:
            settings.setValue("exportFilename", self.data.exportFilename())
            #else:
            #    settings.setValue("exportFilename", self.data.filename())
            QApplication.closeAllWindows()
        else:
            event.ignore()
        
        
        
        

#********************************************* SLOTS for help Menu

    def helpAbout(self):
        QMessageBox.about(self, "About Spectra Viewer",
                """<b>Spectra Viewer</b> v %s
                <p>Copyright &copy; 2013 IJS Ltd. 
                All rights reserved.
                <p>This application can be used to view spectra from
                Zravko's binary file.
                <p>Python %s - Qt %s - PyQt %s on %s""" % (
                __version__, platform.python_version(),
                QT_VERSION_STR, PYQT_VERSION_STR, platform.system()))            
        
        

#********************************************* za lazje kreiranje menija
        
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
            action.triggered.connect(slot)
        if checkable:
            action.setCheckable(True)
        return action
        
#********************************************* vse mozne vrste mapiranja
        
    def mappingFewHighestPeaks(self):
        """narise mapo petih vrhov z najvisjim signalom in jih razporedi - priblizn"""
            
        calibrated = self.data.calibrated()
        stVrhov=self.properties["numberOfHighestPeaks"]

        #izberem samo izbrano stevilo najvisjih, ki so desno od zelene crte
        zelenaCrta = float(self.le_ch1.text())    
        peakCandidatesMask = self.data.maximaBins() > zelenaCrta
        peakCandidatesBins = self.data.maximaBins()[peakCandidatesMask]
        peakCandidatesN = self.data.maximaN()[peakCandidatesMask]
        
        #pogledam, ce sploh je dovolj vrhov
        if len(peakCandidatesBins) >= stVrhov:
            peaks = peakCandidatesBins[np.argsort(peakCandidatesN)[-stVrhov:]]
        else:
            peaks = peakCandidatesBins
            
        #ce je histogram kalibriran je treba spremenit v kanale    
        if self.data.calibrated():
            peaks = self.data.calParam()[0]+np.sqrt(peaks)*self.data.calParam()[1]+\
                self.data.calParam()[2]*peaks+np.sqrt(peaks)**3*self.data.calParam()[3]

        dm = 10        
        for peak in peaks:
            
            interval = np.array([peak-dm,peak+dm])
            self.create2DhistogramWindow(interval, calibrated)

        
    def mappingDataBetweenGreenRed(self):
        """Narise mapo podatkov med rdeco in zeleno crto"""

        #nastavim zacetno vrednost intervala
        interval=np.array([float(self.le_ch1.text()),float(self.le_ch2.text())])
        
        #preracunam v kanale, ce je 1D histogram kalibriran
        calibrated = self.data.calibrated()    
        if calibrated:
            interval[0] = self.data.calParam()[0]+np.sqrt(float(self.le_ch1.text()))*self.data.calParam()[1]+\
                self.data.calParam()[2]*float(self.le_ch1.text())+np.sqrt(float(self.le_ch1.text()))**3*self.data.calParam()[3]
            interval[1] = self.data.calParam()[0]+np.sqrt(float(self.le_ch2.text()))*self.data.calParam()[1]+\
                self.data.calParam()[2]*float(self.le_ch2.text())+np.sqrt(float(self.le_ch2.text()))**3*self.data.calParam()[3]

        self.create2DhistogramWindow(interval, calibrated)
        
    def mappingFromFile(self):
        
        error = None
        home = self.properties["baseFolder"]
        path = (QFileInfo(self.data.filename()).path()
                if self.data.filename() else home)
        calibrated = self.data.calibrated()
        if not calibrated:
            QMessageBox.warning(self, "Warning", "You have to calibrate mass spectrum first")
            return
        
        sortFajl = QFileDialog.getOpenFileName(self, 'Open sort file', 
                                                 path, "Sort file (*.srt)")
        if sortFajl:                                         
            try:
                fh = open(sortFajl,'r')
                for line in fh:
                    line = line.split("\t")
                    interval = np.array([float(line[1]),float(line[2])])
                    interval = self.data.calParam()[0]+np.sqrt(interval)*self.data.calParam()[1]+\
                    self.data.calParam()[2]*interval+np.sqrt(interval)**3*self.data.calParam()[3]
                    self.create2DhistogramWindow(interval, calibrated)
            except Exception as e:
                error = "Error: "+e
            finally:
                if fh is not None:
                    fh.close()
                if error is not None:
                    msg = error
                if error is None:
                    msg = "Sort intervals loaded from file {}.".format(
                            QFileInfo(sortFajl).fileName())
                self.statusBar().showMessage(msg, 500000)
        
    def create2DhistogramWindow(self, interval = None, calibrated = False):
        """nardi histogram in odpre okno z 2D map, interval more bit oblike np.array, v kanalih
        interval mora biti znotraj te funkcije primerno izračunan glede na to ali je bil 1D histogram kalibriran """
        
        #pogledam kolk je velik fajl, ce je prevelik potem ne nardim, da se program ne sesnuje (v prihodnosti primerno da polovim napake)
        size = self.properties["thresholdForMaps"]
        
        if not(self.data.hasHistogram()):
            QMessageBox.warning(self,"Warning","No mass spectra loaded")
            return
        
        if (self.data.size() > 1024*1024*size/16):
            self.statusBar().showMessage(self.data.filename() +'\t Size of file is above threshold for maps.')
            
            QMessageBox.critical(self, "Warning", self.data.filename() + \
                                '\n\n Size of read data is above the set threshold for maps (look in properties dialog) !!!!!')
            return   
        
        #nardim histogram, ce smo prestali prvi test
        normed = self.properties["normed"]
        extent = self.properties["extent"]
        ran = self.properties["2Drange"]
        binning = self.properties["2Dbinning"]
        mask = np.logical_and((self.data.rawData()['time'] < interval[1]), 
                                   (self.data.rawData()['time'] > interval[0]))
                                   
        H, x, y = np.histogram2d(self.data.rawData()['y'][mask],self.data.rawData()['x'][mask],\
                                    bins=binning, normed = normed, range=ran)
        np.savetxt("H.txt",H)
        #primerno preracunam interval, seveda, le ce je potrebno                            
        if calibrated:            
            if self.data.calParam()[4] == 0:
                interval = (Newton(interval,self.data.calParam()))**2
            else:
                interval = ((interval-self.data.calParam()[0])/self.data.calParam()[1])**2        
        
        #dodam okno z 2D histogramom (morm nardit se preprosto okno)
        if self.properties["lightMaps"]:
            window=mplWindow2D.mplWindow2DLight(H, interval, extent, self.data.filename(), self.data.calibrated())
        else:
            window=mplWindow2D.mplWindow2D(H, interval, extent, self.data.filename(), self.data.calibrated())
        Form.Instances.add(window)
        #dodam noter zato, da ostane referenca, ce ne bi okno takoj tudi zginlo
        window.show()
        currentP = Form.currentWindowPosition
        window.move(currentP)
        if (currentP.x()+2*window.width()) > self.screenSize.width() and not (currentP.y()+2*window.height()) > self.screenSize.height():
            nextP = QPoint(0,currentP.y()+window.height()+7)
        elif (currentP.y()+2*window.height()) > self.screenSize.height() and (currentP.x()+2*window.width()) > self.screenSize.width():
            nextP = QPoint(0,0)
        else:
            nextP=currentP+QPoint(window.width(),0)
        Form.currentWindowPosition=nextP
        

        
        
    def mappingAdvanced1(self):
        """nardi vse mape na en list, zaenkrat ni prevec uporabno ker, se ni dokoncano"""
        
        size = self.properties["thresholdForMaps"]
        
        if self.data.size() != None:
            if (self.data.size() > 1024*1024*size/16):
                self.statusBar().showMessage( \
                self.data.filename() +'\tPREVELIK ZA MAPE !!!!!')
                QMessageBox.critical(self.data.filename() +'\tPREVELIK ZA MAPE !!!!!')
                return
       
        if len(self.data):
            fig2 = plt.figure(figsize = (15, 10))
            grid = ImageGrid(fig2, (1, 1, 1), nrows_ncols=(3, 3), axes_pad=0.4,
                             add_all=True, label_mode='L', cbar_mode='each',
                             cbar_location='right', cbar_pad=0.05)

            
            data = self.data.rawData()

            #cmaps = ['spring', 'summer', 'autumn', 'winter']
            for i in range(9):
                
                trijeNajvisji = self.data.maximaBins()[np.argsort(self.data.maximaN())[-11:-1]]

                mask = np.logical_and((data['time'] < trijeNajvisji[i]+10), 
                                      (data['time'] > trijeNajvisji[i]-10))                 
            
                H, x, y = np.histogram2d(
                    data['y'][mask],data['x'][mask],
                     bins=256)
                im = grid[i].imshow(H, extent=[0, 3, 0, 1.5])
                grid.cbar_axes[i].colorbar(im)
                grid[i].set_title('{}'.format(trijeNajvisji[i]))
            fig2.show()      
            
            
#********************************************* kreiranje in brisanje vec oken
        
    @staticmethod
    def updateInstances(qobj):
        Form.Instances = set([window for window \
        in Form.Instances if isAlive(window)])
    

        
    def calculateNextWindowPosition(self):
        
        nextX = Form.Instances[-1].size().width+Form.windowPosition[-1][0]
            
        
    def printInfo(self, text):
        QMessageBox.information(self,text,QMessageBox.Ok)
    

class Cursor:
    def __init__(self, ax, canvas):
        self.axes = ax
        self.canvas=canvas
        #self.lx = ax.axhline(color='k')  # the horiz line
        #self.ly = ax.axvline(color='k')  # the vert line

        # text location in axes coords
        self.txt = ax.text( 0.7, 0.9, 'sfsf', transform=ax.transAxes)

    def mouse_move(self, event):
        if event.inaxes!=self.axes: 

            return

        x, y = event.x, event.y
        # update the line positions
        #self.lx.set_ydata(y )
        #self.ly.set_xdata(x )
        self.txt.set_text( 'x={0:.2f}, y={1:.2f}'.format(x,y) )
        self.canvas.draw()

        
#***************************************** MAIN FUNCTION
     
def main():
    
    
    app = QApplication(sys.argv)
    form = Form()
    newFont = QFont("Courier", 11, QFont.Bold, True)
    app.setStyle("Plastique")
    #app.setFont(newFont)
    app.setApplicationName("SpectraViewer")
    app.setOrganizationName("Tič Ltd.")
    app.setOrganizationDomain("ijs.si")
    app.setWindowIcon(QIcon("./images/icon.png"))
    form.show()
    app.exec_()


if __name__=='__main__':
    
    main()
    
    