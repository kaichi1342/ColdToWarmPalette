
#-----------------------------------------------------------------------------#
# Palette Generator - Copyright (c) 2023 - kaichi1342                         #
# ----------------------------------------------------------------------------#
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
# ----------------------------------------------------------------------------#
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.                        #
# See the GNU General Public License for more details.                        #
#-----------------------------------------------------------------------------#
# You should have received a copy of the GNU General Public License           #
# along with this program.                                                    #
# If not, see https://www.gnu.org/licenses/                                   # 
# -----------------------------------------------------------------------------
# ColdToWarmPalette is a docker that  generates cold and warm tone palette    #
# based of a selected color as well as mix those color with another color     #
# from the mixer slots.                                                       #
# -----------------------------------------------------------------------------
    
  
from krita import *  
import os, json  

from PyQt5.QtCore import ( Qt, pyqtSignal, QEvent)

from PyQt5.QtGui import (QStandardItemModel)


from PyQt5.QtWidgets import ( 
        QWidget, QFrame, QDialog, QDoubleSpinBox,
        QVBoxLayout, QHBoxLayout, QGridLayout, QSpacerItem, QSizePolicy,
        QLabel, QPushButton, QToolButton, QComboBox , QCheckBox,
        QListWidget, QLineEdit, QListWidgetItem, QMenu,
        QMessageBox, QSlider, QCheckBox 
)


class DoubleSpinBox(QDoubleSpinBox):
    stepChanged = pyqtSignal() 
    
    def __init__(self):
         super(QDoubleSpinBox, self).__init__() 
    
    def __init__(self, low = 0, high = 0, step = 0):
        super(QDoubleSpinBox, self).__init__() 
        self.setRange(low, high)
        self.setSingleStep(step)

    def stepBy(self, step):
        value = self.value()
        super(DoubleSpinBox, self).stepBy(step)
        if self.value() != value:
            self.stepChanged.emit()

    def focusOutEvent(self, e):
        value = self.value() 
        super(DoubleSpinBox, self).focusOutEvent(e)
        self.stepChanged.emit()

class SettingsDialog(QDialog):
    def __init__(self, parent, title = "" ):
        super().__init__(parent)
        
        self.resize(210,180)
        self.setWindowTitle(title)  

        self.loadSettings()
        self.setUI()
        self.loadDefault()
        self.connectSignals()

    
    # UI LAYOUT
    def setUI(self):
        self.setting_container = QVBoxLayout() 
        self.setting_container.setContentsMargins(5, 5, 5, 5)
    
        self.setLayout(self.setting_container)  

        self.general_container =  QHBoxLayout()
        self.general_widget = QWidget()
        self.general_widget.setLayout(self.general_container)
        self.general_container.setContentsMargins(0, 0, 0, 0)

        self.setting_container.addWidget(self.general_widget)
         
        self.roll_container =  QGridLayout()  
        self.roll_container.setContentsMargins(0, 0, 0, 0)
        self.color_setting = QWidget()
        self.color_setting.setLayout(self.roll_container) 

        #self.label_hue_min = QLabel("Hue Min")
        #self.label_hue_max = QLabel("Hue Max")

        self.label_mix_min = QLabel("Mix Min")
        self.label_mix_max = QLabel("Mix Max")
        self.label_mix_interval = QLabel("Generated Mixer Interval")
        
        self.label_hue_strip = QLabel("Hue Strip Variance")
        self.label_sat_strip = QLabel("Saturation Strip Variance")
        
        #self.dsb_hue_min    = DoubleSpinBox(2,20,1)
        #self.dsb_hue_max    = DoubleSpinBox(2,20,1)
        
        self.dsb_mix_min    = DoubleSpinBox(2,20,1)
        self.dsb_mix_max  = DoubleSpinBox(2,50,1)

        self.dsb_mix_interval  = DoubleSpinBox(2,30,1)

        self.dsb_hue_strip  = DoubleSpinBox(2,30,1)
        self.dsb_sat_strip  = DoubleSpinBox(2,30,1)
        
        
        self.label_auto_change = QLabel("Auto Change Color") 
        self.chk_auto_change     = QCheckBox()

        self.button_ok      = QPushButton("&Save")
        self.button_cancel  = QPushButton("&Cancel") 

        #self.roll_container.addWidget(self.label_hue_min, 0, 0, 1, 2)
        #self.roll_container.addWidget(self.dsb_hue_min, 0, 2, 1, 2)

        #self.roll_container.addWidget(self.label_hue_max, 0, 4, 1, 2)
        #self.roll_container.addWidget(self.dsb_hue_max, 0, 6, 1, 2)


        self.roll_container.addWidget(self.label_mix_min, 1, 0, 1, 2)
        self.roll_container.addWidget(self.dsb_mix_min, 1, 2, 1, 2)

        self.roll_container.addWidget(self.label_mix_max, 1, 4, 1, 2)
        self.roll_container.addWidget(self.dsb_mix_max, 1, 6, 1, 2)

        self.roll_container.addWidget(self.label_mix_interval, 2, 0, 1, 4)
        self.roll_container.addWidget(self.dsb_mix_interval, 2, 4, 1, 4)


        self.roll_container.addWidget(self.label_hue_strip, 3, 0, 1, 4)
        self.roll_container.addWidget(self.dsb_hue_strip, 3, 4, 1, 4)
        
        self.roll_container.addWidget(self.label_sat_strip, 4, 0, 1, 4)
        self.roll_container.addWidget(self.dsb_sat_strip, 4, 4, 1, 4)


        self.roll_container.addWidget(self.label_auto_change, 5, 0, 1, 4)
        self.roll_container.addWidget(self.chk_auto_change, 5, 4, 1, 4)


        self.roll_container.addWidget(self.button_ok, 6, 0, 1, 4)
        self.roll_container.addWidget(self.button_cancel, 6, 4, 1, 4)

        self.general_container.addWidget(self.color_setting)   

        self.dsb_mix_min.setToolTip("Set the minimum gap in hues between generate mixer color.")
        self.dsb_mix_max.setToolTip("Set the maximum gap in hues between generate mixer color.")

        self.dsb_mix_interval.setToolTip("Set the maximum possible step from current color to target color in mix.")

        self.dsb_hue_strip.setToolTip("Set color variance of generated color in hue strip.")
        self.dsb_sat_strip.setToolTip("Set color variance of generated color in saturation strip.")
        
        self.chk_auto_change.setToolTip("Toggles On/Off: Auto Generate Palette when selected color change.")

    def loadDefault(self): 

        #self.dsb_hue_min.setValue(self.evalSettingValue(self.settings["hue_min"], 4, 20))
        #self.dsb_hue_max.setValue(self.evalSettingValue(self.settings["hue_max"], 4, 20))

        
        self.dsb_mix_min.setValue(self.evalSettingValue(self.settings["mix_min"], 11, 20))
        self.dsb_mix_max.setValue(self.evalSettingValue(self.settings["mix_max"], 30, 50))
        self.dsb_mix_interval.setValue(self.evalSettingValue(self.settings["mix_interval"], 9, 30))

        self.dsb_hue_strip.setValue(self.evalSettingValue(self.settings["hue_strip"], 5, 30))
        self.dsb_sat_strip.setValue(self.evalSettingValue(self.settings["sat_strip"], 5, 30))

        self.chk_auto_change.setChecked(self.settings["auto_change"])
        pass

    
    def loadSettings(self):
        json_setting = open(os.path.dirname(os.path.realpath(__file__)) + '/settings.json')
        self.settings = json.load(json_setting)
        json_setting.close() 
    
    
    def connectSignals(self): 
        self.button_ok.clicked.connect(self.saveSettings)  
        self.button_cancel.clicked.connect(self.cancelSave)   

    def evalSettingValue(self, value, low, high, off_low = 0, off_high = 0 ):
        if value < low: 
            value = low + off_low
        elif value > high:
            value = high + off_high
        else:
            pass
        return value 
    
    def cancelSave(self):  
        self.done(0)

    def saveSettings(self):    
            
        #if( self.dsb_hue_max.value() >=  self.dsb_hue_min.value()):
        #    self.settings["hue_max"]    = self.dsb_hue_max.value()
        #    self.settings["hue_min"]    = self.dsb_hue_min.value()
       
        if(self.dsb_mix_max.value() >= self.dsb_mix_min.value()):
            self.settings["mix_min"]  = self.dsb_mix_min.value()
            self.settings["mix_max"]   = self.dsb_mix_max.value()

        self.settings["mix_interval"]   = self.dsb_mix_interval.value()

        self.settings["hue_strip"]   = self.dsb_hue_strip.value()
        self.settings["sat_strip"]   = self.dsb_sat_strip.value()

        self.settings["auto_change"] = self.chk_auto_change.isChecked()

        json_setting = json.dumps(self.settings, indent = 4)
    
        with open(os.path.dirname(os.path.realpath(__file__)) + '/settings.json', "w") as outfile:
            outfile.write(json_setting)
        
        self.loadSettings() 
        self.parent().reloadSettings()
        self.done(0)