# -*- coding: utf-8 -*-
"""
Created on Wed Aug  6 13:51:26 2014

@author: Administrator
"""

import sys

from PyQt4.QtGui import QApplication, QDialog, QTableWidget, QVBoxLayout, QPushButton, QIntValidator
from PyQt4.QtGui import QHBoxLayout, QMessageBox, QTableWidgetItem, QDialogButtonBox, QLineEdit, QFileDialog

from PyQt4.QtCore import SIGNAL, SLOT, Qt

import numpy as np
from numpy import random


testnaTabela = {"xData" :np.array([1,150.45]), "yData" : np.array([300.2,2000])}
home=r"C:\Dropbox\Sola\DoktoratFMF\MeV-SIMS\MERITVE"


class calibrationDialog(QDialog):
    
    X_MAX = 2
    
    
    def __init__(self, peaks = testnaTabela, fname=home, parent = None):
        
        super(calibrationDialog, self).__init__(parent)
        
        self.calibrationPeaks = peaks
        self.fname = fname
        
        
        self.table = QTableWidget()
        self.table.setColumnCount(self.X_MAX)
        self.table.setHorizontalHeaderLabels(['Mass',"Channel (Time)"])
        
        pbAddRow = QPushButton("Add row")
        
        pbDeleteRow = QPushButton("Delete row")
        
        self.pbFillFromRedLine = QPushButton("Fill")
        
        pbSave = QPushButton("Save to file")
        pbLoad = QPushButton("Load from file")
        
        
        hBox1 = QHBoxLayout()
        hBox1.addWidget(pbAddRow)
        hBox1.addWidget(pbDeleteRow)
        hBox1.addWidget(self.pbFillFromRedLine)
        
        hBox2 =QHBoxLayout()
        hBox2.addWidget(pbSave)
        hBox2.addWidget(pbLoad)
        hBox2.addStretch()
        
        hBox3 =QHBoxLayout()
        hBox3.addWidget(self.table)
        hBox3.addStretch(1)
    
        
                
        
        buttonBox = QDialogButtonBox(QDialogButtonBox.Apply|
                                     QDialogButtonBox.Close)
        
        layout = QVBoxLayout()
        layout.addLayout(hBox3)
        layout.addLayout(hBox1)
        layout.addLayout(hBox2)
        layout.addWidget(buttonBox)
        
        
        self.setLayout(layout)
        self.setMinimumSize(300, 300)
        self.setWindowTitle("Calibration dialog")
        
        self.connect(pbAddRow, SIGNAL("clicked()"),self.addRow)
        self.connect(pbDeleteRow, SIGNAL("clicked()"),self.remove)
        self.connect(self.pbFillFromRedLine, SIGNAL("clicked()"),self.fill)
        self.connect(buttonBox.button(QDialogButtonBox.Apply),
                     SIGNAL("clicked()"), self.apply)
        self.connect(buttonBox, SIGNAL("rejected()"),
                     self, SLOT("reject()"))
        self.connect(pbSave, SIGNAL("clicked()"),self.saveToFile)
        self.connect(pbLoad, SIGNAL("clicked()"),self.loadFromFile)
                     
        self.refreshTable()
                    
    def refreshTable(self):
        """ nafila tabelo z znanimi kalibracijskimi vrhovi"""
        
        self.table.clearContents()
        self.removeAll()
        rowCounter = 0
        try:
            for i,j in zip(self.calibrationPeaks["xData"],self.calibrationPeaks["yData"]):
                self.table.insertRow(rowCounter)
                
                item = QTableWidgetItem()
                item.setData(Qt.EditRole, float(i))
                self.table.setItem(rowCounter,0,item)
                #item = QTableWidgetItem("{0} ({1} ".format(j,8*j/1000)+u"\u00B5"+"s)")   Ce bom kdaj hotu skupaj z casovno informacijo
                item = QTableWidgetItem()
                item.setData(Qt.EditRole, float(j))
                item.setData(Qt.DisplayRole, "{0:.2f}".format(j))
                print(item.type())
                #item.setData(Qt.DisplayRole, 0)
                self.table.setItem(rowCounter,1,item)
                rowCounter=rowCounter+1
            self.table.setSortingEnabled(True)
        except Exception as e:
                excType, excObj, excTb =sys.exc_info()
                error = "Cannot refresh table,\n  {0}: {1}".format(excType,e)
                QMessageBox.critical(self,"Error",error)
            
    
    def addRow(self):
        
        i=self.table.rowCount()
        self.table.insertRow(i)
        
        item = QTableWidgetItem()
        item.setData(Qt.EditRole, 1.0)
        self.table.setItem(i,0,item)
        item = QTableWidgetItem()
        item.setData(Qt.EditRole, 385.5)
        self.table.setItem(i,1,item)
        #QMessageBox.critical(self, "Teslo",str(self.table.rowCount()))
        
    def showData(self):
        xData = np.array([])
        yData = np.array([])
        for j in range(self.table.rowCount()):

            if self.table.item(0,j) and self.table.item(1,j):           
                xData = np.append(xData,float(self.table.item(j,0).text()))
                yData = np.append(yData,float(self.table.item(j,1).text()))
                

        QMessageBox.information(self, "V kvadratku 2,3", "se ne vem")

    def fill(self, xItem = None):
        """ iz rdece crte prebere kanal, nato uporabnik v okence vpise pripadajoco maso"""
        
        self.table.setSortingEnabled(False)
        rowNum=self.table.rowCount()
        if xItem:
            
            self.table.insertRow(rowNum)
            item = QTableWidgetItem()
            item.setData(Qt.EditRole, float(xItem))
            self.table.setItem(rowNum,1,item)
            
            dialog = massDialog()
            if dialog.exec_():
                item = QTableWidgetItem()
                item.setData(Qt.EditRole,float(dialog.leMass.text()))
                #item.setData(Qt.DisplayRole, 0)
                self.table.setItem(rowNum,0,item)
                              
            else:
                self.table.removeRow(rowNum)
                return
        self.table.setSortingEnabled(True)
        
        

    def updateCalibrationPeakList(self):
        """uskladi self.calibrationpeakList z podatki v tabeli"""
        
        xData = np.array([])
        yData = np.array([])
        for j in range(self.table.rowCount()):
            if self.table.item(0,j) and self.table.item(1,j):           
                xData = np.append(xData,float(self.table.item(j,0).text()))
                yData = np.append(yData,float(self.table.item(j,1).text()))

        self.calibrationPeaks={"xData" : xData, "yData" : yData}        
        
    def apply(self):

        self.updateCalibrationPeakList()
        self.emit(SIGNAL("changed"))
        
    def validateValues(self):
        pass


    def remove(self):
        """odstrani izbrano vrstico"""
        
        self.table.removeRow(self.table.currentRow())
        
    def removeAll(self):
        """odstrani vse vrstice"""
        
        for i in range(self.table.rowCount()):
            self.table.removeRow(0)
        
    def saveToFile(self):
        """shranim trenutne podatke v tabeli v text file s koncnico .cali"""

        self.updateCalibrationPeakList() #uskladi podatke s podatki v tabeli, da shranim to kar vidim      
        

        error = None
        fh = None
        home = self.fname
        fname = QFileDialog.getSaveFileName(self, "Export Spectrum", 
                                    home, "Text files (*.cali)")
        if fname:
        
            
            try:
                fh = open(fname,'w')
                for x,y in zip(self.calibrationPeaks["xData"],self.calibrationPeaks["yData"]):
                    fh.write(str(x)+"\t"+str(y)+"\n")


            except EnvironmentError as e:
                excType, excObj, excTb =sys.exc_info()
                error = "Failed to save, due to:\n {0}, {1}".format(excType,e)
            finally:
                if fh is not None:
                    fh.close()
                if error is not None:
                    return False, error
                return True, "Saved peak List"
    
    def loadFromFile(self):
        
        error = None
        fh = None
        home = self.fname
        
        dataN=[] #zacsen seznam za prebrane podatke iz .cali fajla, nakanco spremenim v numpay array
        
        dlg = QFileDialog()
        dlg.setViewMode(QFileDialog.Detail)        
        fname = dlg.getOpenFileName(self, 'Open file', 
                                                 home, "Binary file (*.cali)")
        if fname:
            try:
                fh = open(fname,'r')
                for line in fh:
                    data=line.split("\t")
                    for element in data:
                        t=float(element.strip())
                        dataN.append(t)
                dataN=np.asarray(dataN)
                if len(dataN)%2!=0:
                    raise Exception("Ni deljivo z dva!!!")
                else:
                    dataN.shape=(len(dataN)/2,2)


            except Exception as e:
                error = "Failed to save: {}".format(e)
                QMessageBox.critical(self,"Error",error)
            finally:
                if fh is not None:
                    fh.close()
                if error is not None:
                    return False, error
                self.calibrationPeaks={"xData" : dataN[:,0], "yData" : dataN[:,1]}
                self.refreshTable()
                return True, "Saved peak List"
        
        
        
class massDialog(QDialog):
    
    def __init__(self, parent = None):
        
        super(massDialog, self).__init__(parent)
        
        self.setWindowTitle('Insert mass for selected channel')
        self.leMass = QLineEdit()
        self.leMass.setValidator(QIntValidator(1,10000,self))
        
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|
                                     QDialogButtonBox.Cancel)     
        
        layout = QVBoxLayout()
        layout.addWidget(self.leMass)
        layout.addWidget(buttonBox)
        self.setLayout(layout)
        


        
        self.connect(buttonBox, SIGNAL("accepted()"),
                     self, SLOT("accept()"))
        self.connect(buttonBox, SIGNAL("rejected()"),
                     self, SLOT("reject()"))
        
class MyTableWidgetItem(QTableWidgetItem):
    def __init__(self, text, sortKey):
            QTableWidgetItem.__init__(self, text, QTableWidgetItem.UserType)
            self.sortKey = sortKey

    #Qt uses a simple < check for sorting items, override this to use the sortKey
    def __lt__(self, other):
            return self.sortKey < other.sortKey 
        
        
        
        
def main():
    
    app = QApplication(sys.argv)
    form = calibrationDialog()
    form.show()
    app.exec_()
        
        
if __name__ == "__main__":
    
    main()