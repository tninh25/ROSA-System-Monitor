import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from path_helper import resource_path

class RoundedImageLabel(QLabel):
    def __init__(self, radius=15, size=(450, 600), parent=None):
        super().__init__(parent)
        self.radius = radius
        self.size = size
        self.setFixedSize(*self.size)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("background: transparent; border: none;")
        
    def set_rounded_pixmap(self, image_path):
        """Thiết lập ảnh bo tròn từ đường dẫn"""
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path).scaled(
                self.size[0], self.size[1], Qt.IgnoreAspectRatio, Qt.SmoothTransformation
            )

            rounded = QPixmap(self.size[0], self.size[1])
            rounded.fill(Qt.transparent)

            painter = QPainter(rounded)
            painter.setRenderHint(QPainter.Antialiasing)
            path = QPainterPath()
            path.addRoundedRect(0, 0, self.size[0], self.size[1], self.radius, self.radius)
            painter.setClipPath(path)
            painter.drawPixmap(0, 0, pixmap)
            painter.end()

            self.setPixmap(rounded)
    
    def set_placeholder(self):
        """Tạo placeholder bo tròn"""
        pixmap = QPixmap(self.size[0], self.size[1])
        pixmap.fill(QColor(248, 249, 250))
        
        rounded = QPixmap(self.size[0], self.size[1])
        rounded.fill(Qt.transparent)

        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.size[0], self.size[1], self.radius, self.radius)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)
        
        painter.setFont(QFont("Arial", 16, QFont.Normal))
        painter.setPen(QColor(180, 180, 180))
        painter.drawText(rounded.rect(), Qt.AlignCenter, "Hình ảnh hệ thống\n(450x600)") 
        painter.end()

        self.setPixmap(rounded)