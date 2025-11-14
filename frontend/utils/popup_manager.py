# frontend/utils/popup_manager.py
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from path_helper import resource_path
import os

class PopupManager:
    def __init__(self, parent=None, icon_path=None, font_family="Arial"):  # THÊM font_family
        self.parent = parent
        self.icon_path = icon_path or resource_path(r"assets\icon\rosa-monitor.ico")
        self.font_family = font_family  # THÊM DÒNG NÀY
        
    def set_window_icon(self, msg_box):
        """Thiết lập icon cho message box"""
        if os.path.exists(self.icon_path):
            msg_box.setWindowIcon(QIcon(self.icon_path))
    
    def get_popup_stylesheet(self):
        """Style sheet cho popup với font family"""
        return f"""
            QMessageBox {{
                background-color: #FFFFFF;
                color: #2C3E50;
                font-family: "{self.font_family}";
                border: 1px solid #E0E0E0;
                border-radius: 10px;
            }}
            QMessageBox QLabel {{
                color: #2C3E50;
                font-size: 14px;
                font-family: "{self.font_family}";
                background: transparent;
            }}
            QMessageBox QPushButton {{
                background-color: #004386;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-family: "{self.font_family}";
                font-weight: bold;
                min-width: 80px;
            }}
            QMessageBox QPushButton:hover {{
                background-color: #003366;
            }}
            QMessageBox QPushButton:pressed {{
                background-color: #00274D;
            }}
        """
        
    def show_success(self, message, title="Thành công"):
        """Hiển thị thông báo thành công"""
        msg = QMessageBox(self.parent)
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle(title)
        msg.setStyleSheet(self.get_popup_stylesheet())
        self.set_window_icon(msg)
        return msg.exec_()
            
    def show_error(self, message, title="Lỗi"):
        """Hiển thị thông báo lỗi"""
        msg = QMessageBox(self.parent)
        msg.setIcon(QMessageBox.Warning)
        msg.setText(message)
        msg.setWindowTitle(title)
        msg.setStyleSheet(self.get_popup_stylesheet())
        self.set_window_icon(msg)
        return msg.exec_()

    def show_info(self, message, title="Thông tin"):
        """Hiển thị thông báo thông tin"""
        msg = QMessageBox(self.parent)
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle(title)
        msg.setStyleSheet(self.get_popup_stylesheet())
        self.set_window_icon(msg)
        return msg.exec_()
    
    def show_question(self, message, title="Xác nhận"):
        """Hiển thị thông báo xác nhận"""
        msg = QMessageBox(self.parent)
        msg.setIcon(QMessageBox.Question)
        msg.setText(message)
        msg.setWindowTitle(title)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setStyleSheet(self.get_popup_stylesheet())
        self.set_window_icon(msg)
        return msg.exec_()
    
    def show_critical(self, message, title="Lỗi nghiêm trọng"):
        """Hiển thị thông báo lỗi nghiêm trọng"""
        msg = QMessageBox(self.parent)
        msg.setIcon(QMessageBox.Critical)
        msg.setText(message)
        msg.setWindowTitle(title)
        msg.setStyleSheet(self.get_popup_stylesheet())
        self.set_window_icon(msg)
        return msg.exec_()
    
    