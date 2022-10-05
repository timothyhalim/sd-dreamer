# ------------------------------------- #
#                                       #
# Modern Color Picker by Tom F.         #
# Version 1.3                           #
# made with Qt Creator & PyQt5          #
#                                       #
# ------------------------------------- #

import os, sys
import colorsys

from Qt.QtCore import (QPoint, Qt, Signal, QEvent)
from Qt.QtGui import QColor
from Qt.QtWidgets import (QDialog, QHBoxLayout)
from Qt import _QtUiTools


class ColorPicker(QDialog):

    colorChanged = Signal(QColor)

    def __init__(self, parent=None, rgb=None, hsv=None, hex=None, *args, **kwargs):

        # Extract Initial Color out of kwargs

        super(ColorPicker, self).__init__(parent=parent)

        ui_file = os.path.join(__file__, "..", "colorpicker.ui")
        loader = _QtUiTools.QUiLoader()
        self._layout = QHBoxLayout(self)
        self.ui = loader.load(ui_file, self)
        self._layout.addWidget(self.ui)
        self.resize(256,256)

        # Connect update functions
        self.ui.red.textEdited.connect(self.rgbChanged)
        self.ui.green.textEdited.connect(self.rgbChanged)
        self.ui.blue.textEdited.connect(self.rgbChanged)
        self.ui.hue.textEdited.connect(self.hsvChanged)
        self.ui.sat.textEdited.connect(self.hsvChanged)
        self.ui.val.textEdited.connect(self.hsvChanged)
        self.ui.hex.textEdited.connect(self.hexChanged)

        # Connect selector moving function
        self.ui.hue_picker.installEventFilter(self)
        self.ui.black_overlay.installEventFilter(self)

        if rgb:
            self.setRGB(rgb)
        elif hsv:
            self.setHSV(hsv)
        elif hex:
            self.setHex(hex)
        else:
            self.setRGB((255,0,0))

    def eventFilter(self, obj, event):
        if obj == self.ui.hue_picker:
            if event.type() in [QEvent.MouseMove, QEvent.MouseButtonPress]:
                self.moveHueSelector(event)
        elif obj == self.ui.black_overlay:
            if event.type() in [QEvent.MouseMove, QEvent.MouseButtonPress]:
                self.moveSVSelector(event)
        return super(ColorPicker, self).eventFilter(obj, event)

    ## Main Functions ##
    def getHSV(self, hrange=100, svrange=100):
        h,s,v = self.color
        return (h*(hrange/100.0), s*(svrange/100.0), v*(svrange/100.0))

    def getRGB(self, range=255):
        r,g,b = self.i(self.ui.red.text()), self.i(self.ui.green.text()), self.i(self.ui.blue.text())
        return (r*(range/255.0),g*(range/255.0),b*(range/255.0))

    def getHex(self,ht=False):
        rgb = (self.i(self.ui.red.text()), self.i(self.ui.green.text()), self.i(self.ui.blue.text()))
        if ht: return "#" + self.rgb2hex(rgb)
        else: return self.rgb2hex(rgb)


    ## Update Functions ##
    def colorPicked(self):
        scale = self.ui.hue_picker.height()/100.0
        h,s,v = (
            100 - ((self.ui.hue_selector.y()+1) / scale), 
            (self.ui.selector.x() + 6) / scale, 
            (self.ui.hue_picker.height() - self.ui.selector.y() - 6) / scale
        )
        r,g,b = self.hsv2rgb(h,s,v)
        self.color = (h,s,v)
        self._setRGB((r,g,b))
        self._setHSV((h,s,v))
        self._setHex(self.rgb2hex((r,g,b)))
        self.ui.color_vis.setStyleSheet("background-color: rgb({},{},{})".format(r,g,b,))
        
        if sys.version_info < (3, 0):
            h = h * 1.4 # Pyside issue
        self.ui.color_view.setStyleSheet("background-color: qlineargradient(x1:1, x2:0, stop:0 hsl({}%,100%,{}%), stop:1 #fff);".format(h, 100 if sys.version_info < (3, 0) else 50))
        self.colorChanged.emit(QColor(r,g,b))

    def rgbChanged(self):
        r,g,b = self.i(self.ui.red.text()), self.i(self.ui.green.text()), self.i(self.ui.blue.text())
        self.color = self.rgb2hsv(r,g,b)
        self._setPickerPos(self.color)
        self._setHSV(self.rgb2hsv((r,g,b)))
        self._setHex(self.rgb2hex((r,g,b)))
        self.ui.color_vis.setStyleSheet("background-color: rgb({},{},{})".format(r,g,b,))
        self.colorChanged.emit(QColor(r,g,b))
        
    def hsvChanged(self):
        h,s,v = self.f(self.ui.hue.text()), self.f(self.ui.sat.text()), self.f(self.ui.val.text())
        self._setPickerPos((h,s,v))
        self._setHex(self.hsv2hex((h,s,v)))
        r,g,b = self.hsv2rgb((h,s,v))
        self._setRGB((r,g,b))
        self.ui.color_vis.setStyleSheet("background-color: rgb({},{},{})".format(r,g,b,))
        self.colorChanged.emit(QColor(r,g,b))
        
    def hexChanged(self):
        hex = self.ui.hex.text()
        r,g,b = self.hex2rgb(hex)
        self.color = self.hex2hsv(hex)
        self._setPickerPos(self.rgb2hsv((r,g,b)))
        self._setRGB((r,g,b))
        self._setHSV(self.rgb2hsv((r,g,b)))
        self._setHSV(self.color)
        self.ui.color_vis.setStyleSheet("background-color: rgb({},{},{})".format(r,g,b,))
        self.colorChanged.emit(QColor(r,g,b))

    ## internal setting functions ##
    def _setRGB(self, c):
        r,g,b = c
        self.ui.red.setText(str(self.i(r)))
        self.ui.green.setText(str(self.i(g)))
        self.ui.blue.setText(str(self.i(b)))

    def _setHSV(self, c):
        h,s,v = c
        self.ui.hue.setText("%.02f" %h)
        self.ui.sat.setText("%.02f" %s)
        self.ui.val.setText("%.02f" %v)

    def _setHex(self, c):
        self.ui.hex.setText(c)
        
    def _setPickerPos(self, c):
        scale = self.ui.color_view.height()/100.0
        self.ui.hue_selector.move(0, ((100 - c[0]) * scale)-1)
        self.ui.color_view.setStyleSheet("background-color: qlineargradient(x1:1, x2:0, stop:0 hsl({}%,100%,{}%), stop:1 #fff);".format(c[0], 100 if sys.version_info < (3, 0) else 50))
        self.ui.selector.move(
            (c[1] * scale) - 6, 
            (self.ui.color_view.height() - (c[2] * scale)) - 6
        )

    ## external setting functions ##
    def setRGB(self, c):
        self._setRGB(c)
        self.rgbChanged()

    def setHSV(self, c):
        self._setHSV(c)
        self.colorPicked()

    def setHex(self, c):
        self._setHex(c)
        self.hexChanged()


    ## Color Utility ##
    def hsv2rgb(self, h_or_color, s = 0, v = 0):
        if type(h_or_color).__name__ == "tuple": h,s,v = h_or_color
        else: h = h_or_color
        r,g,b = colorsys.hsv_to_rgb(h / 100.0, s / 100.0, v / 100.0)
        return self.clampRGB((r * 255, g * 255, b * 255))

    def rgb2hsv(self, r_or_color, g = 0, b = 0):
        r = r_or_color
        if isinstance(r_or_color, tuple): 
            r,g,b = r_or_color
        h,s,v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
        return (h * 100, s * 100, v * 100)

    def hex2rgb(self, hex):
        if len(hex) < 6: hex += "0"*(6-len(hex))
        elif len(hex) > 6: hex = hex[0:6]
        rgb = tuple(int(hex[i:i+2], 16) for i in (0,2,4))
        return rgb

    def rgb2hex(self, r_or_color, g = 0, b = 0):
        if type(r_or_color).__name__ == "tuple": r,g,b = r_or_color
        else: r = r_or_color
        hex = '%02x%02x%02x' % (int(r),int(g),int(b))
        return hex

    def hex2hsv(self, hex):
        return self.rgb2hsv(self.hex2rgb(hex))

    def hsv2hex(self, h_or_color, s = 0, v = 0):
        if type(h_or_color).__name__ == "tuple": h,s,v = h_or_color
        else: h = h_or_color
        return self.rgb2hex(self.hsv2rgb(h,s,v))


    # selector move function
    def moveSVSelector(self, event):
        if event.buttons() == Qt.LeftButton:
            pos = event.pos()
            if pos.x() < 0: pos.setX(0)
            if pos.y() < 0: pos.setY(0)
            if pos.x() >= self.ui.color_view.width(): 
                pos.setX(self.ui.color_view.width())
            if pos.y() >= self.ui.color_view.height(): 
                pos.setY(self.ui.color_view.height())
            self.ui.selector.move(pos - QPoint(6,6))
            self.colorPicked()

    def moveHueSelector(self, event):
        if event.buttons() == Qt.LeftButton:
            pos = event.pos().y()
            if pos < 0: pos = 0
            if pos >= self.ui.hue_picker.height(): 
                pos = self.ui.hue_picker.height()
            self.ui.hue_selector.move(QPoint(0,pos-1))
            self.colorPicked()

    def i(self, text):
        try: return int(text)
        except: return 0
        
    def f(self, text):
        try: return float(text)
        except: return 0

    def clampRGB(self, rgb):
        r,g,b = rgb
        if r<0.0001: r=0
        if g<0.0001: g=0
        if b<0.0001: b=0
        if r>255: r=255
        if g>255: g=255
        if b>255: b=255
        return (r,g,b)
