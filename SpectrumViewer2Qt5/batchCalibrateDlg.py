# -*- coding: utf-8 -*-
"""
Created on Mon Jun  2 13:20:08 2014

@author: Administrator
"""
import sys, os
from PyQt5.QtWidgets import QDialog, QApplication, QGridLayout
from PyQt5.QtWidgets import QLabel, QListView, QFileDialog, QPushButton
from PyQt5.QtWidgets import QDialogButtonBox, QTableWidget, QTableWidgetItem

from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon

from PyQt5.QtCore import Qt

import numpy as np

testnaTabela = {"xData" :np.array([1,150]), "yData" : np.array([300,2000])}
homeF = r"C:/Dropbox/Sola/DoktoratFMF/MeV-SIMS/MERITVE/kurac/kji"

class batchCalibrateDlg(QDialog):
    
    X_MAX = 2
    
    def __init__(self, peaks = testnaTabela , home = homeF, parent=None):
        
        super(QDialog, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        self.seriesListModel = QStandardItemModel()
        self.info = None
        self.choosen=[]
        print(home)
        self.home = home.rstrip(home.split('/')[-1]).rstrip(home.split('/')[-2]+'/')
        self.calibrationPeaks = peaks
        print(peaks)
        
        
        logLabel = QLabel("Data series:")
        self.seriesListView = QListView()
        self.seriesListView.setModel(self.seriesListModel)
        
        self.table = QTableWidget()
        self.table.setColumnCount(self.X_MAX)
        self.table.setHorizontalHeaderLabels(['Mass',"Time", "Error"])
        
        self.pbSelectFolder = QPushButton("Select folder")
        
        self.pbSelectAll = QPushButton("Select All")
        
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|
                                     QDialogButtonBox.Cancel) 
        
        
        grid=QGridLayout()
        grid.addWidget(logLabel, 0, 0)
        grid.addWidget(self.seriesListView,1,0,1,3)
        grid.addWidget(self.table,1,3,1,3)
        grid.addWidget(self.pbSelectFolder, 2,0)
        grid.addWidget(self.pbSelectAll,2,1)
        grid.addWidget(buttonBox, 3,0)
        
        self.connect(self.pbSelectFolder,SIGNAL("clicked()"),self.getFolderName)
        self.connect(self.pbSelectAll,SIGNAL("clicked()"),self.selectAll)
        
        self.connect(buttonBox, SIGNAL("accepted()"),
                     self, SLOT("accept()"))
        self.connect(buttonBox, SIGNAL("rejected()"),
                     self, SLOT("reject()"))
        
        self.setLayout(grid)

        self.setWindowTitle("batchCalibrate")
        self.setWindowIcon(QIcon("./images/toolsBatchCalibrate.png"))
        
        self.refreshTable()
        
        
    def getFolderName(self):
        info=[]
        
        file = str(QFileDialog.getExistingDirectory(self, "Select Directory",self.home))
        self.home = file
        if os.path.isfile(file+"\\meritve.txt"):            
            f = open(file+"\\meritve.txt","r")
            for line in f:
                text = line.split("\t")
                info.append(text)
                
            f.close()
            self.info=np.array(info)
            print(self.info)
            

            
        names=[]
        if file:
            for x in os.listdir(file):
                if os.path.isfile(file+"\\"+x):
                    pass
                else:
                    names.append(x)
                   
        if names:
            self.fillSeriesList(names)
    
    def fillSeriesList(self, names):
        self.seriesListModel.clear()
        test=[]
        for name in names:
            if os.path.isfile(self.home+"\\meritve.txt"):
                test = self.info[:,0]
            if name in test:
                index = int(np.where(self.info[:,0] == name)[0])
                itemContent = name +"\t"+ str(self.info[index,-1].strip())
            else:               
                itemContent = name
            item = QStandardItem(itemContent)
            item.setCheckState(Qt.Unchecked)
            item.setCheckable(True)
            self.seriesListModel.appendRow(item)
            
            
    def selectAll(self):
        
        for row in range(self.seriesListModel.rowCount()):
            item=self.seriesListModel.itemFromIndex(self.seriesListModel.index(row, 0))
            item.setCheckState(Qt.Checked)
            
    def selectByRegExpression():
        pass

                
    def apply(self):
        pass
    
    def accept(self):
        
        for row in range(self.seriesListModel.rowCount()):
            item=self.seriesListModel.itemFromIndex(self.seriesListModel.index(row, 0))
            if item.checkState() == Qt.Checked:
                
                self.choosen.append(item.text().split("\t")[0])
                
        QDialog.accept(self) 
        
    def refreshTable(self):
        """ nafila tabelo z znanimi kalibracijskimi vrhovi"""
        
        self.table.clear()        
        rowCounter = 0
        for i,j in zip(self.calibrationPeaks["xData"],self.calibrationPeaks["yData"]):
            self.table.insertRow(rowCounter)
            
            item = QTableWidgetItem(str(i))
            self.table.setItem(rowCounter,0,item)
            item = QTableWidgetItem(str(j))
            self.table.setItem(rowCounter,1,item)
            rowCounter=rowCounter+1
        
        
def main():
    
    app = QApplication(sys.argv)
    dialog = batchCalibrateDlg()
    dialog.show()
    app.exec_()
    
if __name__=="__main__":
    
    main()