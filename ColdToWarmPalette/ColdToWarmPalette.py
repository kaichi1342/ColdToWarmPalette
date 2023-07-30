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
# ColdToWarmPalette is a docker that  generates cold and warm tone palette    #
# based of a selected color as well as mix those color with another color     #
# from the mixer slots.                                                       #
# -----------------------------------------------------------------------------
    
  
 
from krita import *
import  math, os, random, json
from datetime import datetime
from functools import partial

 
from PyQt5.QtCore import ( Qt, QSize,  QTimer, QPoint )
  

from PyQt5.QtWidgets import ( 
    QApplication,
    QVBoxLayout,  QGridLayout,  QHBoxLayout, 
    QPushButton, QWidget, QLabel, QComboBox,
    QToolButton, QDesktopWidget  
)

from .CWP_ColorManager import *  
from .CWP_SettingsDialog import *

DOCKER_NAME = 'ColdToWarmPalette'
DOCKER_ID = 'pykrita_ColdWarmPalette'


class ColdToWarmPalette(DockWidget): 
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cold To Warm Palette")  
      
        self.loadSettings() 
       
        self.mixer_color = []
        self.sat_color = []
        self.gen_color = []
        self.hue_color = []
     
        self.with_canvas = False
        self.useFG = True
        self.theme_signal  = False 
    
        self.target_color = False

        self.color_manager = ColorGenerator(self)   
        
        self.setting_dialog = None

        self.setUI()
        self.connectButtons()
        self.connectColorGrid()
        self.loadMixer()
    
    def loadSettings(self):
        self.json_setting = open(os.path.dirname(os.path.realpath(__file__)) + '/settings.json')
        self.settings = json.load(self.json_setting)
        self.json_setting.close() 
 
    def reloadSettings(self):
        self.json_setting = open(os.path.dirname(os.path.realpath(__file__)) + '/settings.json')
        self.settings = json.load(self.json_setting)
        self.json_setting.close() 

    def setUI(self):
        self.base_widget = QWidget()
    
        self.main_container = QGridLayout()
        self.main_container.setContentsMargins(0, 0, 0, 0)

        self.base_widget.setLayout(self.main_container)
        self.setWidget(self.base_widget)
        
        self.base_widget.setMinimumSize(QSize(120,80))
        #self.base_widget.setMaximumSize(QSize(400,500))
  
        # ----------- #
        # MIXER COLOR #
        # ----------- #
        

        #UPPER COLOR BOX  
        self.upper_colorbox             = QWidget()
        self.upper_colorbox_container   = QHBoxLayout()
        self.upper_colorbox.setLayout(self.upper_colorbox_container)
        self.upper_colorbox.setContentsMargins(0, 0, 0, 0) 
        self.upper_colorbox_container.setContentsMargins(2, 2, 2, 2) 

        for c in range(0, 12):
            self.mixer_color.append(ColorBox()) 
            self.upper_colorbox_container.addWidget(self.mixer_color[c])

        # ---------- #
        # MAIN COLOR #
        # ---------- #
        
        #COLOR BOX 
        self.colorbox            = QWidget()
        self.colorbox_container  = QGridLayout()
        self.colorbox.setLayout(self.colorbox_container)
        self.colorbox_container.setContentsMargins(2, 2, 2, 2)
       
        #LEFT COLOR BOX  
        self.left_colorbox          = QWidget()
        self.left_color_container   = QGridLayout()
        self.left_colorbox.setLayout(self.left_color_container)
        self.left_color_container.setContentsMargins(0, 0, 2, 2)

        for r in range(0, 5):
            self.sat_color.append(ColorBox()) 
            self.left_color_container.addWidget(self.sat_color[r], r, 0, 1, 1)
         
     
        #MID  COLOR BOX 
        self.mid_colorbox         = QWidget()
        self.mid_color_container  = QGridLayout()
        self.mid_colorbox.setLayout(self.mid_color_container)
        self.mid_color_container.setContentsMargins(2, 0, 2, 2)

        #COLOR GRID
        for r in range(0, 5):
            self.gen_color.append([]) 
            for c in range(0, 5):
                self.gen_color[r].append(ColorBox()) 
                self.mid_color_container.addWidget(self.gen_color[r][c], r, c, 1, 1)

        #RIGHT COLOR BOX
        self.right_colorbox          = QWidget()
        self.right_color_container   = QGridLayout()
        self.right_colorbox.setLayout(self.right_color_container)
        self.right_color_container.setContentsMargins(2, 0, 0, 2)

        for r in range(0, 5):
            self.hue_color.append(ColorBox()) 
            self.right_color_container.addWidget(self.hue_color[r], r, 0, 1, 1)

        #ADD TO COLOR BOX  
        self.colorbox_container.addWidget(self.left_colorbox, 0, 0, 1, 1)
        self.colorbox_container.addWidget(self.mid_colorbox, 0, 1, 1, 6) 
        self.colorbox_container.addWidget(self.right_colorbox, 0, 7, 1, 1) 

        # ------------ #
        # TOOL BUTTON  #
        # ------------ #

        self.toolbox             = QWidget()
        self.toolbox_container   = QGridLayout()
        self.toolbox.setLayout(self.toolbox_container)
        self.toolbox_container.setContentsMargins(2, 2, 2, 2)

        self.btn_generate_mixer =  QToolButton() 
        self.btn_generate_mixer.setIcon( Krita.instance().icon("config-color-manage") ) 

        self.btn_reset_mixer =  QToolButton() 
        self.btn_reset_mixer.setIcon( Krita.instance().icon("reload-preset") ) 

        self.btn_generate_palette=  QToolButton() 
        self.btn_generate_palette.setIcon( Krita.instance().icon("animation_play") )  

        self.btn_fgbg_toggle =  QToolButton() 
        self.btn_fgbg_toggle.setIcon( Krita.instance().icon("object-order-lower-calligra") )   #object-order-raise-calligra

        self.btn_configure =  QToolButton() 
        self.btn_configure.setIcon( Krita.instance().icon("configure-shortcuts") )     

        self.toolbox_container.addWidget(self.btn_reset_mixer, 0, 0 , 1, 1)  
        self.toolbox_container.addWidget(self.btn_generate_mixer, 0, 1 , 1, 1)  
        self.toolbox_container.addWidget(self.btn_generate_palette, 0, 2 , 1, 1)  
        self.toolbox_container.addWidget(self.btn_fgbg_toggle, 0, 3 , 1, 1)  
        self.toolbox_container.addWidget(self.btn_configure, 0, 4 , 1, 1)  

        # -------------- #
        # MAIN CONTAINER #
        # -------------- #

        #self.timer     = QTimer()
        #self.msg      = QLabel("test") 

        #ADD TO MAIN CONTAINER
        self.main_container.addWidget(self.upper_colorbox, 0, 0, 1, 1) 
        self.main_container.addWidget(self.colorbox, 1, 0, 5, 1)  
        self.main_container.addWidget(self.toolbox, 6, 0, 1, 1)  

        #self.main_container.addWidget(self.msg, 7, 0, 1, 1)  
    

    def canvasChanged(self, canvas):
        if canvas:       
            if canvas.view():
                self.with_canvas = True
            else: 
                self.with_canvas = False 

        self.with_canvas = False

          

    #CONNECT BUTTONS
    def connectButtons(self): 
        self.btn_generate_palette.clicked.connect(self.generateColorPalette)
        self.btn_fgbg_toggle.clicked.connect(self.toggleFGBG) 
        
        self.btn_generate_mixer.clicked.connect(self.generateMixerColor) 
        self.btn_reset_mixer.clicked.connect(self.loadMixer) 
        self.btn_configure.clicked.connect(self.openSetting) 
        
        pass

    #COLOR GRID CONNECT
    def connectColorGrid(self):  
        for row in self.gen_color: 
            for color in row:
                color.clicked.connect(partial(self.setFGColor, color ))
                color.rightclicked.connect(partial(self.setBGColor, color ))

        for color in self.sat_color:
            color.clicked.connect(partial(self.setFGColor, color ))
            color.rightclicked.connect(partial(self.setMainToThisColor, color ))
         
        for color in self.hue_color:
            color.clicked.connect(partial(self.setFGColor, color ))
            color.rightclicked.connect(partial(self.setMainToThisColor, color ))
 
        for color in self.mixer_color:
            color.clicked.connect(partial(self.mixColor, color ))
            color.rightclicked.connect(partial(self.setMixerSlot, color )) 


    def disconnectColorGrid(self):
        for row in self.gen_color: 
            for color in row:
                color.disconnect()
        for color in self.sat_color:
            color.disconnect()
        for color in self.hue_color:
            color.disconnect()
        for color in self.mixer_color:
            color.disconnect()

        self.timer.timeout.disconnect 


    def toggleFGBG(self):
        if self.useFG == True:
            self.btn_fgbg_toggle.setIcon(Krita.instance().icon("object-order-raise-calligra")) 
            self.useFG = False
        else:
            self.btn_fgbg_toggle.setIcon(Krita.instance().icon("object-order-lower-calligra"))
            self.useFG = True 
        
        self.generateColorPalette()
        pass

    def setFGColor(self, color_box):   
        color_to_set = color_box.getColorForSet(Krita.instance().activeDocument())
        Krita.instance().activeWindow().activeView().setForeGroundColor(color_to_set)
             
    def setBGColor(self, color_box):   
        color_to_set = color_box.getColorForSet(Krita.instance().activeDocument())
        Krita.instance().activeWindow().activeView().setBackGroundColor(color_to_set)     
        

    def getHSV(self, colmgr):
        if(self.useFG == True):
            FG = colmgr.getFGColor(Krita.instance().activeWindow().activeView(), Krita.instance().activeDocument())
            return { "hue" : FG.hsvHue(), "sat" : FG.hsvSaturation(), "val" : FG.value() }
        else: 
            BG = colmgr.getBGColor(Krita.instance().activeWindow().activeView(), Krita.instance().activeDocument())
            return { "hue" : BG.hsvHue(), "sat" : BG.hsvSaturation(), "val" : BG.value() }

    def getFG(self, colmgr):
        FG = colmgr.getFGColor(Krita.instance().activeWindow().activeView(), Krita.instance().activeDocument())
        return { "hue" : FG.hsvHue(), "sat" : FG.hsvSaturation(), "val" : FG.value() }

    def distanceFrom(self, end, start, div = 1, max = 20, min = 2, is_val = False):
        distance = abs(end - start)
        
        if(div <= 1): return distance 

        distance = math.floor(distance / div)
        distance = distance if is_val == True and start > 50 else min
        
        if( abs(distance) >= max): return max

        if( abs(distance) <= min): return min

        return distance
 

    def accessOffset(self, hue, is_cold):
        min = self.settings["hue_min"]
        max = self.settings["hue_max"]
  
        if(hue <= 5 or hue > 240):
            return -1 * self.distanceFrom(240, hue, 2, max, min) if is_cold else self.distanceFrom(240, hue, 2, max, min)
            #return -6  if is_cold else 6;  
        else:
            return self.distanceFrom(240, hue, 2, max, min) if is_cold else -1 * self.distanceFrom(240, hue, 2, max, min) 
            #return 6  if is_cold else -6;   

    def generateColorPalette(self, color = False):
        cm = self.color_manager
        hsv = color if(color) else self.getHSV(self.color_manager)  

        #[2,2] is center grid / MAIN COLOR
        self.gen_color[2][2].setBorder(1)
        self.hue_color[2].setBorder(1)
        self.sat_color[2].setBorder(1)

        self.gen_color[2][2].setColorHSV( hsv["hue"], hsv["sat"], hsv["val"])  
        
        #center column

        frLight = abs(self.distanceFrom(255, hsv["val"],2, 30, 2, True))
        frDark  = abs(self.distanceFrom(0, hsv["val"],2, 20, 2, True))

        self.gen_color[0][2].setColorHSV( hsv["hue"], hsv["sat"], cm.setCappedVal(hsv["val"], frLight * 2) ) 
        self.gen_color[1][2].setColorHSV( hsv["hue"], hsv["sat"], cm.setCappedVal(hsv["val"], frLight  ) )
        self.gen_color[3][2].setColorHSV( hsv["hue"], hsv["sat"], cm.setCappedVal(hsv["val"], -1 * frDark) ) 
        self.gen_color[4][2].setColorHSV( hsv["hue"], hsv["sat"], cm.setCappedVal(hsv["val"], -1 * frDark * 2) ) 

        self.generateCold(hsv, frLight, frDark)
        self.generateWarm(hsv, frLight, frDark)

        self.generateSatStrip()
        self.generateHueStrip()
             
 

    def generateCold(self, hsv, frLight, frDark):
        cm = self.color_manager 

        offset = self.accessOffset(hsv["hue"], True)

        mul  = 2 
        for r in range (0,2):
            h_offset = offset * mul
            self.gen_color[0][r].setColorHSV( cm.setHue(hsv["hue"], h_offset) , hsv["sat"], cm.setCappedVal(hsv["val"], frLight * 2) ) 
            self.gen_color[1][r].setColorHSV( cm.setHue(hsv["hue"], h_offset) , hsv["sat"], cm.setCappedVal(hsv["val"], frLight  ) )
            self.gen_color[2][r].setColorHSV( cm.setHue(hsv["hue"], h_offset) , hsv["sat"], hsv["val"])  
            self.gen_color[3][r].setColorHSV( cm.setHue(hsv["hue"], h_offset) , hsv["sat"], cm.setCappedVal(hsv["val"], -1 * frDark) ) 
            self.gen_color[4][r].setColorHSV( cm.setHue(hsv["hue"], h_offset) , hsv["sat"], cm.setCappedVal(hsv["val"], -1 * frDark * 2) ) 
            mul = mul - 1

        


    def generateWarm(self, hsv, frLight, frDark): 
        cm = self.color_manager

        offset = self.accessOffset(hsv["hue"], False)

        mul  = 1
        for r in range (3,5): 
            h_offset = offset * mul
            self.gen_color[0][r].setColorHSV( cm.setHue(hsv["hue"], h_offset) , hsv["sat"], cm.setCappedVal(hsv["val"], frLight * 2) ) 
            self.gen_color[1][r].setColorHSV( cm.setHue(hsv["hue"], h_offset) , hsv["sat"], cm.setCappedVal(hsv["val"], frLight  ) ) 
            self.gen_color[2][r].setColorHSV( cm.setHue(hsv["hue"], h_offset) , hsv["sat"], hsv["val"])  
            self.gen_color[3][r].setColorHSV( cm.setHue(hsv["hue"], h_offset) , hsv["sat"], cm.setCappedVal(hsv["val"], -1 * frDark) ) 
            self.gen_color[4][r].setColorHSV( cm.setHue(hsv["hue"], h_offset) , hsv["sat"], cm.setCappedVal(hsv["val"], -1 * frDark * 2) )  
            mul = mul + 1
  
 
    
    def generateSatStrip(self):
        cm = self.color_manager

        random.seed(datetime.now())
        col =  self.gen_color[2][2].toHSV()
        self.sat_color[2].setColorHSV( col["H"], col["S"], col["V"]) 

        rng = {"min" : 1, "max" : 1 + self.settings["sat_strip"]}

        col =  self.gen_color[1][2].toHSV()
        self.sat_color[1].setColorHSV( col["H"], cm.setCappedSat(col["S"], random.randint(rng["min"], rng["max"])),  col["V"])
      
        col =  self.gen_color[3][2].toHSV()
        self.sat_color[3].setColorHSV( col["H"], cm.setCappedSat(col["S"], -1 * random.randint(rng["min"], rng["max"])),  col["V"])

        rng["min"] = rng["max"] + self.settings["sat_strip"]
        rng["max"] = rng["min"] + self.settings["sat_strip"]

        col =  self.gen_color[0][2].toHSV()
        self.sat_color[0].setColorHSV( col["H"], cm.setCappedSat(col["S"], random.randint(rng["min"], rng["max"])),  col["V"])
        
        col =  self.gen_color[4][2].toHSV()
        self.sat_color[4].setColorHSV( col["H"], cm.setCappedSat(col["S"], -1 * random.randint(rng["min"], rng["max"])),  col["V"])

    def generateHueStrip(self):
        cm = self.color_manager

        random.seed(datetime.now())
        col =  self.gen_color[2][2].toHSV()
        self.hue_color[2].setColorHSV( col["H"], col["S"], col["V"]) 

        rng = {"min" : 1, "max" : 1 + self.settings["hue_strip"]}

        col =  self.gen_color[1][2].toHSV()
        self.hue_color[1].setColorHSV( cm.setHue(col["H"], random.randint(rng["min"], rng["max"])) , col["S"],  col["V"])
        
        col =  self.gen_color[3][2].toHSV()
        self.hue_color[3].setColorHSV( cm.setHue(col["H"], -1 * random.randint(rng["min"], rng["max"])) , col["S"],  col["V"])
 

        rng["min"] = rng["max"] + self.settings["hue_strip"]
        rng["max"] = rng["min"] + self.settings["hue_strip"]

        col =  self.gen_color[0][2].toHSV()
        self.hue_color[0].setColorHSV( cm.setHue(col["H"], -1 * random.randint(rng["min"], rng["max"])) , col["S"],  col["V"])

        col =  self.gen_color[4][2].toHSV()
        self.hue_color[4].setColorHSV( cm.setHue(col["H"], random.randint(rng["min"], rng["max"])) , col["S"],  col["V"])

    def setMainToThisColor(self, color): 
        col =  color.toHSV() 
        self.generateColorPalette({"hue" : col["H"], "sat" : col["S"], "val" : col["V"]})

    #----------------#
    # COLOR MIXING   #
    #----------------#
    
    def loadMixer(self):
        hue = 0
        for mixer in self.mixer_color:
            mixer.setColorHSV(hue,255,255)
            hue += 30

    def generateMixerColor(self): 
        cm = self.color_manager
        random.seed(datetime.now())

        gap_limit = 30
        gap_interval = self.settings["mix_interval"]

        col =  { "H" : cm.setHue(), "S" : cm.setSat(), "V" : cm.setVal() } 
        col["S"] = col["S"] if col["S"] > gap_limit else gap_limit
        col["V"] = col["V"] if col["V"] > gap_limit else gap_limit

        #LEFT
        random.seed() 
        l_sat =  cm.setHue(col["S"], -1 * random.randint(8,gap_limit))
        for i in range(0, 3):  
            random.seed() 
            s = gap_limit + ( gap_interval * i ) + 1
            e = gap_limit + ( gap_interval * (i + 1))
            self.mixer_color[i].setColorHSV( cm.setHue(l_sat, -1 * random.randint(s,e) ) , col["S"], col["V"]) 

        #RIGHT
        random.seed() 
        r_sat =  cm.setHue(col["S"], random.randint(11,gap_limit))
        for i in range(3, 6):   
            random.seed() 
            s = gap_limit + ( gap_interval * i ) + 1
            e = gap_limit + ( gap_interval * (i + 1))
            self.mixer_color[i].setColorHSV( cm.setHue(l_sat, random.randint(s,e) ) , col["S"], col["V"]) 

        #OP_LEFT 
        l_sat += 180  
        for i in range(6, 9):  
            random.seed() 
            s = gap_limit + ( gap_interval * i ) + 1
            e = gap_limit + ( gap_interval * (i + 1))
            self.mixer_color[i].setColorHSV( cm.setHue(l_sat, -1 * random.randint(s,e) ) , col["S"], col["V"]) 

        #OP_RIGHT 
        r_sat += 180  
        for i in range(9, 12):  
            random.seed() 
            s = gap_limit + ( 10 * i ) + 1
            e = gap_limit + ( 10 * (i + 1))
            self.mixer_color[i].setColorHSV( cm.setHue(l_sat, random.randint(s,e) ) , col["S"], col["V"]) 

        pass
      
    #---------------------------------#
    # MIXER                           #
    #---------------------------------#
    def mixColor(self, target_color):
        cm = self.color_manager
        current  = self.gen_color[2][2].toHSV() #self.getFG( cm ) 
        target   = target_color.toHSV()

        next_hue = self.calcNextHue(target["H"], current["H"])

        next_sat =  self.calcNextSatVal(target["S"], current["S"])
        next_val =  self.calcNextSatVal(target["V"], current["V"], False)

        #new_color = ColorBox()
        #new_color.setColorHSV( next_hue, next_sat, next_val)  
        #self.setFGColor( new_color )
        
        self.generateColorPalette({"hue" : next_hue, "sat" : next_sat, "val" : next_val})


    def calcNextHue(self, target, current): 
        
        current = current if current > 0 else 360 + current
        target  = target  if target  > 0 else 360 + target

        if(current == 240): current = current - 1
        if(current == target): return target

        to_left  =  (360 - target) + current if ( current < target ) else  abs(target - current)
        to_right =  abs(target - current) if ( current < target ) else  (360 - current) + target


        offset = self.distanceFrom(to_left, 0, self.settings["mix_min"],  self.settings["mix_max"]) if (to_left < to_right) else self.distanceFrom(to_right, 0, self.settings["mix_min"],  self.settings["mix_max"])
         
 
        if(to_left >= to_right):    
            return target if (to_right - offset < 0) else current + offset  #to_right
        else: 
            return target if (to_left - offset < 0) else current - offset   #to_left
            
    
        

    def calcNextSatVal(self, target, current, is_sat = True):
        current = current if current >= 0 else 0
        target  = target if target >= 0 else 0

        gap = abs(target - current)
        dir = 1 if(current < target) else -1

        offset = math.ceil(gap * 0.05) if math.ceil(gap * 0.05) < 2 else 2
        offset = dir * offset if( abs(offset) < 12) else dir * 12 
   
        if(gap == 0): 
            return target
         

        return self.color_manager.setCappedSat(current, offset) if is_sat else self.color_manager.setCappedVal(current, offset) 

    
    def setMixerSlot(self, color): 
        hsv   = self.getFG(self.color_manager ) 
        c_hsv = color.toHSV()

        if(hsv["hue"] != c_hsv["H"] or hsv["sat"] != c_hsv["S"] or hsv["val"] != c_hsv["V"]):
            color.setColorHSV( hsv["hue"], hsv["sat"], hsv["val"]) 

    #---------------------------------#
    # Settings Dialog                 #
    #---------------------------------#
           
    
    def openSetting(self):
        if self.setting_dialog == None:
            self.setting_dialog = SettingsDialog(self, "Settings")
            self.setting_dialog.show() 
        elif self.setting_dialog.isVisible() == False : 
            self.setting_dialog.show() 
            #self.setting_dialog.loadDefault()
        else:
            pass
        
        self.moveDialog(self.setting_dialog) 
        
    def moveDialog(self, dialog):
        gp = self.mapToGlobal(QPoint(0, 0))     
         
        if self.x() < ( QDesktopWidget().screenGeometry().width() // 2) : 
            dialog.move(gp.x() + self.frameGeometry().width() + 10, gp.y() + 30) 
        else:  
            dialog.move(gp.x() - (dialog.frameGeometry().width() + 5 )  , gp.y() + 30) 



instance = Krita.instance()
dock_widget_factory = DockWidgetFactory(DOCKER_ID,
                                        DockWidgetFactoryBase.DockRight,
                                        ColdToWarmPalette)

instance.addDockWidgetFactory(dock_widget_factory) 