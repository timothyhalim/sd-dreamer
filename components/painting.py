import os
from Qt.QtWidgets import (
    QMdiSubWindow, QLayout, QLabel, QApplication
)
from Qt.QtCore import Qt, QPoint, QSize, Signal
from Qt.QtGui import QPixmap, QColor, QPainter, QPen, QCursor

class Canvas(QMdiSubWindow):
    def __init__(self, parent=None, flags=Qt.FramelessWindowHint):
        super(Canvas, self).__init__(parent, flags)
        self.__drag = False
        self.__last_button = None
        self.is_full_size = False
        self._is_painting = False
        self.__last_position = QPoint(0, 0)
        self._brush_size = 4

        pixmap = QPixmap(os.path.join(__file__, "..", "icons", "brush_cursor.png").replace("\\", "/"))
        pixmap = pixmap.scaled(
            QSize(32, 32), 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        self._brush_cursor = QCursor(pixmap, -1, -1)

        self.setStyleSheet(
            """
            border: 0px;
            background: white url(%s);
            background-repeat: repeat-xy;
            background-position: top left;
            """
            % os.path.join(__file__, "..", "icons", "checker.jpg").replace("\\", "/")
        )
        self.layout().setSizeConstraint(QLayout.SetFixedSize)

        self.painting = Painting(self)
        # self.painting.setMinimumSize(64, 64)
        self.layout().addWidget(self.painting)

        self.setBrushColor(QColor.fromRgb(255, 0, 0))
        self.setBrushSize(10)
        
    def mousePressEvent(self, mouseEvent):
        self.__last_button = mouseEvent.button()
        if mouseEvent.button() == Qt.MouseButton.MiddleButton:
            self.__drag = True
            self.__start = mouseEvent.pos()
            self.setCursor(QCursor(Qt.OpenHandCursor))
            return True
            
        self.setCursor(
            self._brush_cursor if self._is_painting
            else QCursor(Qt.ArrowCursor)
        )
        if self._is_painting:
            return True

        return super(Canvas, self).mousePressEvent(mouseEvent)
    
    def mouseMoveEvent(self, mouseEvent):
        if self.__last_button == Qt.MouseButton.MiddleButton:
            if self.__drag:
                self.setCursor(QCursor(Qt.ClosedHandCursor))
                delta = mouseEvent.pos()-self.__start
                self.move(self.pos()+delta)
            return True
            
        self.setCursor(
            self._brush_cursor if self._is_painting
            else QCursor(Qt.ArrowCursor)
        )
        if self._is_painting:
            return True

        return super(Canvas, self).mouseMoveEvent(mouseEvent)
    
    def mouseReleaseEvent(self, mouseEvent):
        if mouseEvent.button() == Qt.MouseButton.MiddleButton:
            self.__drag = False
            
        self.setCursor(
            self._brush_cursor if self._is_painting
            else QCursor(Qt.ArrowCursor)
        )
        if self._is_painting:
            return True

        return super(Canvas, self).mouseReleaseEvent(mouseEvent)
    
    def toggleFit(self):
        self.is_full_size = not self.is_full_size
        if self.is_full_size:
            self.__last_position = self.pos()
        else:
            self.move(self.__last_position)

    def enableDrawing(self, state):
        self._is_painting = state
        self.painting._drawing_enabled = self._is_painting
        self.setCursor(
            self._brush_cursor if self._is_painting
            else QCursor(Qt.ArrowCursor)
        )

    def brushColor(self):
        return self._brush_color

    def brushSize(self):
        return self._brush_size

    def setBrushColor(self, color):
        self._brush_color = color
        self.painting.setBrushColor(self._brush_color)

    def setBrushSize(self, size):
        self._brush_size = size
        self.painting.setBrushSize(self._brush_size)

    def setPainting(self, pixmap):
        self.painting.setPainting(pixmap)

    def getPainting(self):
        return self.painting.getPainting()


class Painting(QLabel):
    paintingChanged = Signal(QPixmap)
    exported = Signal(str)
    def __init__(self, parent=None):
        super(Painting, self).__init__("", parent)
        
        self.setMouseTracking(True)
        self._is_drawing = False
        self._drawing_enabled = False
        self._draw_mode = 'paint'
        self._brush_color = QColor.fromRgb(255, 0, 0)
        self._brush_size = 4
        self._last_pos = QPoint(0,0)
        
        self.blank = QColor.fromRgb(255, 255, 255)
        self.blank.setAlpha(0)
        
        pixmap = QPixmap(512, 512)
        pixmap.fill(QColor.fromRgbF(0, 0, 0, 0))
        self.setPainting(pixmap)
    
    def setPainting(self, pixmap):
        self._pixmap = pixmap
        self.paintingChanged.emit(self._pixmap)
        self._size = pixmap.size()
        
        self._paint_layer = QPixmap(self._size)
        self._paint_layer.fill(self.blank)
        
        self._brush_display_layer = QPixmap(self._size)
        self._brush_display_layer.fill(self.blank)
        
        self.setFixedSize(self._size)
        return super(Painting, self).setPixmap(pixmap)
    
    def getPainting(self):
        size = self._pixmap.size()
        painting = QPixmap(size)
        painter = QPainter(painting)
        painter.drawPixmap(
            0,0,size.width(), size.height(), 
            self._pixmap,
            0,0,size.width(), size.height(), 
        )
        painter.drawPixmap(
            0,0,size.width(), size.height(), 
            self._paint_layer,
            0,0,size.width(), size.height(), 
        )
        painter.end()
        return painting.toImage()
        # export_pixmap.save(output)
        # self.exported.emit(output)
        
    # def setDrawMode(self, state="paint"):
    #     """Set drawmode, should be either "paint" or "erase"

    #     Args:
    #         state (str, optional): "paint" or "erase". Defaults to "paint".
    #     """
    #     self._draw_mode = state
    
    def setBrushColor(self, color):
        self._brush_color = color
        
    def setBrushSize(self, radius):
        self._brush_size = radius
        
    def setupPainter(self):
        modifiers = QApplication.keyboardModifiers()
        
        painter = QPainter(self._paint_layer)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(
            QPen(
                self._brush_color, self._brush_size, 
                Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin
            )
        )
        
        painter.setCompositionMode(
            QPainter.CompositionMode_SourceOver if self._draw_mode == 'paint'
            else QPainter.CompositionMode_Clear
        )
        if modifiers == Qt.AltModifier:
            painter.setCompositionMode(
                QPainter.CompositionMode_Clear if self._draw_mode == 'paint'
                else QPainter.CompositionMode_SourceOver
            )
        return painter
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.geometry(), self._pixmap)
        painter.drawPixmap(self.geometry(), self._paint_layer)
        
        if self._drawing_enabled:
            if self._is_drawing: return

            # Draw brush display
            bp = QPainter(self._brush_display_layer)
            color = QColor.fromRgb(0, 0, 0)
            color.setAlpha(128)
            bp.setRenderHint(QPainter.Antialiasing)
            bp.setPen(
                QPen(
                    color, 1, 
                    Qt.DotLine, Qt.RoundCap, Qt.RoundJoin
                )
            )
            bp.setCompositionMode(QPainter.CompositionMode_SourceOver)
            bp.drawEllipse(
                self._last_pos, 
                self._brush_size/2, self._brush_size/2
            )
        
        painter.drawPixmap(self.geometry(), self._brush_display_layer)
        self._brush_display_layer.fill(self.blank)
    
    def mousePressEvent(self, event):
        if self._drawing_enabled:
            if event.button() == Qt.LeftButton:
                self._is_drawing = True
                self._last_pos = QPoint(
                    float(event.pos().x())/self.size().width()*self._pixmap.size().width(), 
                    float(event.pos().y())/self.size().height()*self._pixmap.size().height()
                )

                painter = self.setupPainter()
                painter.drawPoint(self._last_pos)

            self.update()
            
        return super(Painting, self).mousePressEvent(event)
            
    def mouseMoveEvent(self, event):
        if self._drawing_enabled:
            modifiers = QApplication.keyboardModifiers()
            self._draw_line = modifiers == Qt.ShiftModifier
            
            pos = QPoint(
                float(event.pos().x())/self.size().width()*self._pixmap.size().width(), 
                float(event.pos().y())/self.size().height()*self._pixmap.size().height()
            )
            
            if event.buttons() == Qt.LeftButton and self._is_drawing:
                painter = self.setupPainter()
                    
                if not self._draw_line:
                    painter.drawLine(self._last_pos, pos)
                    
            self._last_pos = pos
            self.update()
            
        return super(Painting, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._drawing_enabled:
            modifiers = QApplication.keyboardModifiers()
            self._draw_line = modifiers == Qt.ShiftModifier
            if event.button() == Qt.LeftButton:
                pos = QPoint(
                    float(event.pos().x())/self.size().width()*self._pixmap.size().width(), 
                    float(event.pos().y())/self.size().height()*self._pixmap.size().height()
                )
                if self._draw_line:
                    painter = self.setupPainter()
                    painter.drawLine(self._last_pos, pos)
                self._last_pos = pos
                self._is_drawing = False
            self.update()
            
        if self.parent():
            return self.parent().mouseReleaseEvent(event)
        return super(Painting, self).mouseReleaseEvent(event)
        
    # def mouseDoubleClickEvent(self, event):
    #     if event.button() == Qt.MouseButton.LeftButton:
    #         self.toggle_fit()
    
    # def toggle_fit(self):
    #     if self.parent():
    #         self.parent().toggle_fit()
    #         if self.parent().is_full_size:
    #             self._size = self.size()
    #             self.fit(self.parent().parent().size())
    #         else:
    #             self.setPixmap(
    #                 self._pixmap.scaled(
    #                     self._size, 
    #                     Qt.KeepAspectRatio, 
    #                     Qt.SmoothTransformation
    #                 )
    #             )
    #             self.setFixedSize(self._size)
    
    # def fit(self, size):
    #     new_width = float(self._size.width())/self._size.height()*size.height()
    #     new_height = float(self._size.height())/self._size.width()*size.width()
    #     use_width = new_width > size.width() and new_height < size.height()
    #     new_size = QSize(
    #                     size.width() if use_width else new_width,
    #                     new_height if use_width else size.height(),
    #                 )
    #     self.setPixmap(
    #         self._pixmap.scaled(
    #             new_size, 
    #             Qt.KeepAspectRatio, 
    #             Qt.SmoothTransformation
    #         )
    #     )
    #     new_size = self.pixmap().size()
    #     self.setFixedSize(new_size)
    #     delta = size - new_size
    #     new_pos = QPoint(delta.width()/2.0, delta.height()/2.0)
    #     self.parent().move(new_pos)
    
    # def zoom(self, pos, in_or_out):
    #     increment = self._size/10
    #     min_size_x = float(self._size.width())/self._size.height()*10
    #     min_size_y = float(self._size.height())/self._size.width()*10
    #     use_width = self._size.width() > self._size.height()
    #     new_size = self.size()
    #     new_pos = self.parent().pos()
        
    #     if self.parent():
    #         self.parent().is_full_size = False
    #         x = float(increment.width())*pos.x()/self.width()
    #         y = float(increment.height())*pos.y()/self.height()
    #     if in_or_out > 0:
    #         new_size += increment
    #         if self.parent():
    #             new_pos -= QPoint(x,y)
    #     elif in_or_out < 0:
    #         if self.width() > 10:
    #             new_size -= increment
    #             if self.parent():
    #                 new_pos += QPoint(x,y)
                
    #     new_size = QSize(
    #                 max(new_size.width(), min_size_x if use_width else 10 ), 
    #                 max(new_size.height(), 10 if use_width else min_size_y)
    #             )
    #     self.parent().move(new_pos)
    #     self.setPixmap(
    #         self._pixmap.scaled(
    #             new_size, 
    #             Qt.KeepAspectRatio, 
    #             Qt.SmoothTransformation
    #         )
    #     )
    #     self.setFixedSize(new_size)
    
    # def reset_zoom(self):
    #     if self.parent():
    #         self.parent().move(0,0)
    #     self.setPixmap(self._pixmap)
    #     self.setFixedSize(self._pixmap.size())