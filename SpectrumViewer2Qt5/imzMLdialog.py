# -*- coding: utf-8 -*-
"""
Created on Fri Jun  6 12:21:10 2014

@author: Administrator
"""

import sys

from PyQt5.QtWidgets import QLineEdit, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QDialog
from PyQt5.QtWidgets import QApplication, QGridLayout, QFileDialog, QComboBox, QDialogButtonBox 
from PyQt5.QtWidgets import QCheckBox

from PyQt5.QtCore import Qt





class imzMLConverterDialog(QDialog):
    
    def __init__(self, fname = None, parent=None):
        super(QDialog,self).__init__(parent)
        
        self.UUID = 0
        self.path= fname
        formats = ("float32","integer16")
        
        labelPixels = QLabel("Pixels:")
        self.lePixels = QLineEdit("9")
        labelPixels.setMaximumWidth(50)
        self.lePixels.setMaximumWidth(50)
        
        labelBinning = QLabel("Binning:")
        self.leBinning = QLineEdit("1000")
        labelBinning.setMaximumWidth(50)
        self.leBinning.setMaximumWidth(50)
        
        self.cbSpecialFormat = QCheckBox('Use my reduced format')
        self.cbSpecialFormat.setCheckState(False)       
        
        pbPath = QPushButton("Path:")
        pbPath.setMaximumWidth(60)
        self.labelPath = QLabel(str(self.path))
        self.labelPath.setStyleSheet("border: 3px grey;\
                                        border-style: inset")
        self.labelPath.setMinimumWidth(300)
                                        
        labelMassRange=QLabel("Mass range:")
        self.leMassRangeLow = QLineEdit("1")
        self.leMassRangeLow.setMaximumWidth(50)
        labelCrtica = QLabel("--")
        labelCrtica.setFixedWidth(8)
        labelCrtica.setAlignment(Qt.AlignHCenter)
        self.leMassRangeHigh = QLineEdit("150")
        self.leMassRangeHigh.setMaximumWidth(50)
        
        labelNumberFormat = QLabel("Number format")
        self.cbNumberFormat = QComboBox()
        self.cbNumberFormat.addItems(formats)
        
        labelFileSize = QLabel("File size:")
        self.labelFSize = QLabel("")
        self.labelFSize.setStyleSheet("border: 3px grey;\
                                        border-style: inset")
        self.labelFSize.setMinimumWidth(50)
    
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|
                                     QDialogButtonBox.Cancel)
        
        
        vBox1 = QVBoxLayout()
        vBox1.addStretch(1)
        vBox1.addWidget(labelPixels)
        vBox1.addWidget(self.lePixels)
        
        vBox2 = QVBoxLayout()
        vBox2.addStretch(1)
        vBox2.addWidget(labelBinning)
        vBox2.addWidget(self.leBinning)
        
        

        
        hBox = QHBoxLayout()
        hBox.addWidget(pbPath)
        hBox.addWidget(self.labelPath)
        
        hBox1 = QHBoxLayout()
        hBox1.addWidget(labelNumberFormat)
        hBox1.addWidget(self.cbNumberFormat)
        
        hBox2 = QHBoxLayout()
        hBox2.addWidget(labelMassRange)
        hBox2.addWidget(self.leMassRangeLow)
        hBox2.addWidget(labelCrtica)
        hBox2.addWidget(self.leMassRangeHigh)
        hBox2.addStretch(1)
        
        hBox3 = QHBoxLayout()
        hBox3.addWidget(labelFileSize)
        hBox3.addWidget(self.labelFSize)
        hBox3.addStretch(1)
        
        hBox4 = QHBoxLayout()
        hBox4.addWidget(pbPath)
        hBox4.addWidget(self.labelPath)
        hBox4.addStretch(1)
        
        

        
        grid1 = QGridLayout()
        grid1.addLayout(vBox1,0,0)
        grid1.addLayout(vBox2,0,1)
        grid1.addWidget(self.cbSpecialFormat,0,3)
        grid1.addLayout(hBox1,1,0,1,2)
        grid1.addLayout(hBox2,2,0,1,4)
        grid1.addLayout(hBox4,3,0,1,4)
        grid1.addLayout(hBox3,4,0,1,2)
        grid1.addWidget(buttonBox,4,2)
        
        self.setLayout(grid1)
        self.setWindowTitle("imzML")
        
        pbPath.clicked.connect(self.getPath)
        buttonBox.accepted.connect(self.accept)
        self.leBinning.editingFinished.connect(self.calculateFileSize)
        self.lePixels.editingFinished.connect(self.calculateFileSize)
        self.cbSpecialFormat.stateChanged.connect(self.calculateFileSize)
        self.cbNumberFormat.currentIndexChanged.connect(self.calculateFileSize)
        buttonBox.rejected.connect(self.reject)
        self.calculateFileSize()            
                     
    def getPath(self):
        
        self.path = QFileDialog.getExistingDirectory(self, "narek", self.path )
        if self.path:
            self.labelPath.setText(self.path)
        
        
    def calculateFileSize(self):
        
        oneNumber = self.cbNumberFormat.currentText()
        if not self.cbSpecialFormat.isChecked():
            if oneNumber == 'float32':
                result = (16+(float(self.leBinning.text()))*float(self.lePixels.text())**2*32/8*2)/1024/1024
            else:
                result = (16+(float(self.leBinning.text()))*float(self.lePixels.text())**2*16/8*2)/1024/1024
        else:
            result = ((float(self.leBinning.text()))*float(self.lePixels.text())**2*16/8)/1024/1024
            
        self.labelFSize.setText("{:,.3f} MB".format(result))

        
def main():
    
    app = QApplication(sys.argv)
    form = imzMLConverterDialog()
    form.show()
    app.exec_()
    
if __name__ == "__main__":
    main()
    

   

