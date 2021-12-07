# -*- coding: utf-8 -*-
"""
Created on Thu Apr  3 12:15:13 2014

@author: Administrator
"""
import sys
from PyQt5.QtWidgets import QDialog, QApplication, QLabel, QLineEdit , QCheckBox
from PyQt5.QtWidgets import QGridLayout, QDialogButtonBox

from PyQt5.QtGui import QRegExpValidator, QIcon

from PyQt5.QtCore import Qt, QRegExp

class fitDialog(QDialog):
    
    def __init__(self, parameters, parent = None):
        
        super(fitDialog,self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        #"[-+]?[0-9]{0,3}(\\.[0-9]{0,2})"
        testRe = QRegExp(r"[0-9]{0,3}\.[0-9]")
        self.p0=parameters
        
        label_sigma = QLabel("Sigma: ")        
        self.le_sigma=QLineEdit(str(self.p0[2]))
        self.le_sigma.setValidator(QRegExpValidator(testRe,self))

        label_Integral = QLabel("Area: ")        
        self.le_Integral=QLineEdit(str(self.p0[0]))
        self.le_sigma.setValidator(QRegExpValidator(testRe,self))        
        
        label_peakPos = QLabel("Peak position: ")        
        self.le_peakPo=QLineEdit(str(self.p0[1]))
        self.le_sigma.setValidator(QRegExpValidator(testRe,self))
        
        self.showCurveCheckBox = QCheckBox("&Show Fitted Curve")
        
        buttonBox = QDialogButtonBox(QDialogButtonBox.Apply|
                                     QDialogButtonBox.Close)        
        
        grid = QGridLayout()
        grid.addWidget(label_sigma, 0, 0)
        grid.addWidget(self.le_sigma, 0, 1)
        grid.addWidget(label_Integral, 1, 0)
        grid.addWidget(self.le_Integral, 1, 1)
        grid.addWidget(label_peakPos, 2, 0)
        grid.addWidget(self.le_peakPo, 2, 1)
        grid.addWidget(self.showCurveCheckBox, 3, 0, 1, 2)
        grid.addWidget(buttonBox,4,0,1,2)
        self.setLayout(grid)
        
        buttonBox.button(QDialogButtonBox.Apply).clicked.connect(self.apply)
        buttonBox.rejected.connect(self.reject)  
                     
        self.setWindowTitle("fitDialog")
        self.setWindowIcon(QIcon("./images/fitIcon.png"))
        
        
    def apply(self):
        """ posredujem zacetne parametre glavnemu oknu in narisem fit"""
        mean = float(self.le_peakPo.text())
        sigma = float(self.le_sigma.text())
        area = float(self.le_Integral.text())
        self.p0[0] = area
        self.p0[1] = mean
        self.p0[2] = sigma
        self.emit("changed")

        
def main():
    
    
    app = QApplication(sys.argv)
    form = fitDialog()
    form.show()
    status = app.exec_()


if __name__=='__main__':
    
    main()