# -*- coding: utf-8 -*-
"""
Created on Sun Nov 30 12:14:01 2014

@author: Luka
"""

import sys

from PyQt5.QtWidgets import QDialog, QApplication, QLabel, QLineEdit, QVBoxLayout,QDialogButtonBox
from PyQt5.QtWidgets import QMessageBox

from PyQt5.QtCore import Qt

from math import sqrt


class TOFcalculatorDialog(QDialog):
    
    def __init__(self, parent = None):
        
       
        
        super(TOFcalculatorDialog, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        
        labelFlightLength = QLabel('Flight length [m]:')
        self.leFlightLength = QLineEdit("1")
        
        labelMass = QLabel('Mass [u]:')
        self.leMass = QLineEdit("400")
        
        labelInitialEnergy = QLabel('Initial energy [keV]')
        self.leInitialEnergy = QLineEdit("3")
        
        buttonBox = QDialogButtonBox(QDialogButtonBox.Apply|
                                     QDialogButtonBox.Close)
        
        vBox1 = QVBoxLayout()
        vBox1.addWidget(labelFlightLength)
        vBox1.addWidget(self.leFlightLength)
        vBox1.addWidget(labelMass)
        vBox1.addWidget(self.leMass)
        vBox1.addWidget(labelInitialEnergy)
        vBox1.addWidget(self.leInitialEnergy)
        vBox1.addWidget(buttonBox)
        
        self.setLayout(vBox1)
        self.setWindowTitle("TOF Calculator")
        
        
        buttonBox.button(QDialogButtonBox.Apply).clicked.connect(self.apply)
        buttonBox.rejected.connect(self.reject)
                     
                     
    def apply(self):
        
        u=931.5
        c = 299792458
        E = float(self.leInitialEnergy.text())
        m = float(self.leMass.text())
        L = float(self.leFlightLength.text())
        tofClassic = L * sqrt(m*1000*u/2/E)/c*1000000
        QMessageBox.information(self,"Cas preleta",str(tofClassic))  
        self.chaneged.emit()




def main():
    
    app=QApplication(sys.argv)
    window = TOFcalculatorDialog()
    window.show()
    app.exec_()
    

if __name__ =="__main__":
    
    main()
    
