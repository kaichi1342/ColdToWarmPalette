#-----------------------------------------------------------------------------#
# Palette Generator - Copyright (c) 2022 - kaichi1342                         #
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
# PaletteGenerator is a docker that  generates color scheme palette randomly  #
# or based of the selected scheme. There are 9 color scheme available to      #
# generate from.                                                              #
# -----------------------------------------------------------------------------
  
 
from krita import *  
import random, time
from datetime import datetime

from PyQt5.QtCore import ( Qt, pyqtSignal)

from PyQt5.QtGui import (QPainter, QColor, QPen, QMouseEvent)

from PyQt5.QtWidgets import (QWidget, QMessageBox, QLabel)
 
from .CWP_ColorManager import * 

class PaletteManager():  

    def __init__(self, parent, settings):  
        
        self.mixer_color = []
        self.sat_color = []
        self.gen_color = []
        self.hue_color = []

        self.settings = settings

        self.color_manager = ColorGenerator(self)   
        
        super().__init__() 
    
    def __init__(self, parent): 

        super().__init__() 
    
    def setMixerSlot(self, color):
        hsv   = self.getFG(self.color_manager ) 
        c_hsv = color.toHSV()

        if(hsv["hue"] != c_hsv["H"] or hsv["sat"] != c_hsv["S"] or hsv["val"] != c_hsv["V"]):
            color.setColorHSV( hsv["hue"], hsv["sat"], hsv["val"])  
           