# -*- coding: utf-8 -*-
"""
Created on Mon Jun 30 14:48:49 2014

@author: Luka


Properties dialog, nastavitve določenih stvari( velikost mape, binning, density ...)
"""

import sys

from PyQt5.QtWidgets import QApplication, QDialog, QTabWidget, QWidget
from PyQt5.QtWidgets import QLabel, QLineEdit,QVBoxLayout, QHBoxLayout, QBoxLayout, QCheckBox
from PyQt5.QtWidgets import QDialogButtonBox, QPushButton, QFileDialog


import numpy as np


class Form(QDialog):
    
    def __init__(self, properties, parent= None):
        
        
        super(QDialog, self).__init__(parent)
        
        self.properties = properties
                
        
        
        labelScanSize=QLabel("Scan size:")
        self.leScanSize = QLineEdit()
        hBoxScanSize = QHBoxLayout()
        hBoxScanSize.addWidget(labelScanSize)
        hBoxScanSize.addWidget(self.leScanSize)
        hBoxScanSize.addStretch(0.5)
        
        label2Dbinning = QLabel("Binning of 2D histogram:")
        self.le2Dbinning = QLineEdit()
        hBox2Dbinning = QHBoxLayout()
        hBox2Dbinning.addWidget(label2Dbinning)
        hBox2Dbinning.addWidget(self.le2Dbinning)
        hBox2Dbinning.addStretch(0.5)
        
        label2Drange = QLabel("Range of histogram values:")
        self.le2Drange = QLineEdit()
        hBox2Drange = QHBoxLayout()
        hBox2Drange.addWidget(label2Drange)
        hBox2Drange.addWidget(self.le2Drange)
        #hBox2Drange.addStretch(0.01)
        

        
        labelBinning = QLabel("Binning:")
        self.leBinning = QLineEdit()
        hBoxBinning = QHBoxLayout()
        hBoxBinning.addWidget(labelBinning)
        hBoxBinning.addWidget(self.leBinning)
        hBoxBinning.addStretch(1)
        
        pbBaseFolder = QPushButton("Base folder:")
        pbBaseFolder.setMaximumWidth(80)
        self.labelBaseFolder = QLabel()
        self.labelBaseFolder.setStyleSheet("border: 2px grey;\
                                        border-style: inset")
        self.labelBaseFolder.setMinimumWidth(300)
        hBoxBaseFolder = QHBoxLayout()
        hBoxBaseFolder.addWidget(pbBaseFolder)
        hBoxBaseFolder.addWidget(self.labelBaseFolder)
        
        
        labelDataThresholdSize = QLabel("Histogram threshold(MB)")
        self.leDataThresholdSize = QLineEdit()
        hBoxDataThresholdSize = QHBoxLayout()
        hBoxDataThresholdSize.addWidget(labelDataThresholdSize)
        hBoxDataThresholdSize.addWidget(self.leDataThresholdSize)
        hBoxDataThresholdSize.addStretch(1)
        
        
        
        labelDataThresholdSizeMaps = QLabel(" 2D Histogram threshold(MB)")
        self.leDataThresholdSizeMaps = QLineEdit()
        hBoxDataThresholdSizeMaps = QHBoxLayout()
        hBoxDataThresholdSizeMaps.addWidget(labelDataThresholdSizeMaps)
        hBoxDataThresholdSizeMaps.addWidget(self.leDataThresholdSizeMaps)
        hBoxDataThresholdSizeMaps.addStretch(1)

        labelPartOfFile = QLabel("Read Only first n*128 bites of data. n: ")
        self.lePartOfFile = QLineEdit()
        hBoxPartOfFile = QHBoxLayout()
        hBoxPartOfFile.addWidget(labelPartOfFile)
        hBoxPartOfFile.addWidget(self.lePartOfFile)
        hBoxPartOfFile.addStretch(1)
        
        labelNumberOfHighestPeaks = QLabel("Number of highest peaks drawn")
        self.leNumberOfHighestPeaks = QLineEdit()
        hBoxNumberOfHighestPeaks = QHBoxLayout()
        hBoxNumberOfHighestPeaks.addWidget(labelNumberOfHighestPeaks)
        hBoxNumberOfHighestPeaks.addWidget(self.leNumberOfHighestPeaks)
        hBoxNumberOfHighestPeaks.addStretch(1)
        
        self.cbDensityHistogram = QCheckBox('Density histogram:')
        self.cbDensityHistogram.setChecked(False)
        
        self.cbNormedMaps = QCheckBox('Normed Maps')
        self.cbNormedMaps.setChecked(False)

        self.cbCalibrationModel = QCheckBox('Use Simple calibration model (2 parameters)\n no initial velocity contribution')
        self.cbCalibrationModel.setChecked(False)
        
        self.cbLightMaps = QCheckBox('Draw lighter version of 2D maps:')
        self.cbLightMaps.setChecked(False)
        
        labelMassRange = QLabel("Mass Range")
        self.leMassRange1 = QLineEdit()
        labelCrtice = QLabel("--")
        self.leMassRange2 =QLineEdit()
        hBoxMassRange = QHBoxLayout()
        hBoxMassRange.addWidget(labelMassRange)
        hBoxMassRange.addWidget(self.leMassRange1)
        hBoxMassRange.addWidget(labelCrtice)
        hBoxMassRange.addWidget(self.leMassRange2)
        hBoxMassRange.addStretch(1)
        
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|
                                     QDialogButtonBox.Cancel)
        
        self.initializeAllProperties()
        
        qTabWidget = QTabWidget()
        
        generalWidget = QWidget()
        generalLayout = QVBoxLayout()
        generalLayout.addLayout(hBoxBinning)
        generalLayout.addLayout(hBoxMassRange)
        generalLayout.addWidget(self.cbDensityHistogram)
        generalLayout.addWidget(self.cbNormedMaps)
        generalWidget.setLayout(generalLayout)
        qTabWidget.addTab(generalWidget, "&General")
        
        settingsWidget = QWidget()
        settingsLayout = QVBoxLayout()
        settingsLayout.addLayout(hBoxBaseFolder)
        settingsLayout.addLayout(hBoxDataThresholdSize)
        settingsLayout.addLayout(hBoxDataThresholdSizeMaps)
        settingsLayout.addLayout(hBoxPartOfFile)
        settingsLayout.addWidget(self.cbCalibrationModel)
        settingsLayout.addWidget(self.cbLightMaps)
        settingsLayout.addLayout(hBoxNumberOfHighestPeaks)
        settingsWidget.setLayout(settingsLayout)
        qTabWidget.addTab(settingsWidget, "&Settings")
        
        scanWidget = QWidget()
        scanLayout = QVBoxLayout()
        scanLayout.addLayout(hBoxScanSize)
        scanLayout.addLayout(hBox2Dbinning)
        scanLayout.addLayout(hBox2Drange)
        scanWidget.setLayout(scanLayout)
        qTabWidget.addTab(scanWidget, "&Scanning data")
        
        
        layout = QVBoxLayout()
        layout.addWidget(qTabWidget)
        layout.addWidget(buttonBox)
        self.setLayout(layout)
        self.setWindowTitle("Properties")
        
        
        pbBaseFolder.clicked.connect(self.getBaseFolder)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        
    def initializeAllProperties(self):
        
        self.leBinning.setText(str(self.properties["binning"]))
        self.leScanSize.setText(self.extentToString(self.properties["extent"]))
        self.le2Drange.setText(self.rangeToString(self.properties["2Drange"]))
        self.le2Dbinning.setText(str(self.properties["2Dbinning"]))
        self.labelBaseFolder.setText(self.properties["baseFolder"])
        self.leDataThresholdSize.setText(str(self.properties["thresholdFileSize"]))
        self.leDataThresholdSizeMaps.setText(str(self.properties["thresholdForMaps"]))
        self.leNumberOfHighestPeaks.setText(str(self.properties["numberOfHighestPeaks"]))
        self.lePartOfFile.setText(str(self.properties["part"]))
        self.leMassRange1.setText(str(self.properties["massRangeOfInterest"][0]))
        self.leMassRange2.setText(str(self.properties["massRangeOfInterest"][1]))
        if self.properties["density"]:
            self.cbDensityHistogram.setChecked(True)
        if self.properties["normed"]:
            self.cbNormedMaps.setChecked(True)
        if self.properties["SimpleCalibrationModel"]:
            self.cbCalibrationModel.setChecked(True)
        if self.properties["lightMaps"]:
            self.cbLightMaps.setChecked(True)
    
    def extentToString(self, extent):
        
        t=str(extent[0])
        for i in extent[1:]:
            t=t+","+str(i)
        return t
        
        
    def getExtent(self,text):
        
        a=[]
        for i in text.split(","):
            t=float(i)
            a.append(t)
        
        return np.array(a)
        
    def rangeToString(self, table):
        
        
        extent=table.ravel()        
        t=str(extent[0])        
        for i in extent[1:]:
            t=t+","+str(i)
        return t
        
        
    def getRange(self,text):
        
        a=[]
        for i in text.split(","):
            t=float(i)
            a.append(t)
        
        return np.array(a).reshape((2,2))
        
    def getBaseFolder(self):
        path = self.labelBaseFolder.text()
        path = QFileDialog.getExistingDirectory(self, "Choose base folder", path )
        if path:
            self.labelBaseFolder.setText(path)
        
    def accept(self):
        density = self.cbDensityHistogram.isChecked()
        normed = self.cbNormedMaps.isChecked()
        calibrationModel = self.cbCalibrationModel.isChecked()
        lightMaps = self.cbLightMaps.isChecked()
        self.properties["density"] = density
        self.properties["normed"] = normed
        self.properties["SimpleCalibrationModel"] = calibrationModel
        self.properties["lightMaps"] = lightMaps
        massRange=[round(float(self.leMassRange1.text())),round(float(self.leMassRange2.text()))]
        self.properties["massRangeOfInterest"] = massRange
        self.properties["thresholdForMaps"]= int(self.leDataThresholdSizeMaps.text())
        self.properties["thresholdFileSize"] =int(self.leDataThresholdSize.text())
        self.properties["extent"] = self.getExtent(self.leScanSize.text())
        self.properties["part"] = int(self.lePartOfFile.text())
        self.properties["2Drange"] = self.getRange(self.le2Drange.text())
        self.properties["numberOfHighestPeaks"]=int(self.leNumberOfHighestPeaks.text())
        self.properties["binning"]=int(self.leBinning.text())
        self.properties["baseFolder"] = self.labelBaseFolder.text()
        self.properties["2Dbinning"] = int(self.le2Dbinning.text())

        
        QDialog.accept(self)
        
        
        
        

LEFT, ABOVE = range(2)

class LabelledLineEdit(QWidget):

    def __init__(self, labelText="", position=LEFT,
                 parent=None):
        super(LabelledLineEdit, self).__init__(parent)
        self.label = QLabel(labelText)
        self.lineEdit = QLineEdit()
        self.label.setBuddy(self.lineEdit)
        layout = QBoxLayout(QBoxLayout.LeftToRight
                if position == LEFT else QBoxLayout.TopToBottom)
        layout.addWidget(self.label)
        layout.addWidget(self.lineEdit)
        self.setLayout(layout)





def main():
    
    app = QApplication(sys.argv)
    form = Form({})
    form.show()
    app.exec_()


if __name__ == "__main__":
    
    main()

