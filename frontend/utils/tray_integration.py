# frontend/tray_integration.py
import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from path_helper import resource_path

class FanMonitorTrayApp(QWidget):
    """Ứng dụng system tray đơn giản - chỉ quản lý tray icon"""
    def __init__(self, font_family=None, startup_window=None):
        super().__init__()
        self.font_family = font_family or "Arial"
        self.startup_window = startup_window
        
        QApplication.setApplicationName("ROSA System Monitor")
        QApplication.setApplicationDisplayName("ROSA System Monitor")
        QApplication.setWindowIcon(QIcon(resource_path(r"assets\icon\rosa-monitor.ico")))

        # Tạo system tray
        self.setup_tray_icon()
        
        # Ẩn cửa sổ chính
        self.setWindowTitle("Fan Monitor")
        self.resize(1, 1)
        self.move(-1000, -1000)
        
    def create_tray_icon(self):
        tray_icon_path = resource_path(r"assets\icon\rosa-monitor.ico")
        
        if os.path.exists(tray_icon_path):
            # Sử dụng icon từ file
            pixmap = QPixmap(tray_icon_path)
            # Scale icon về kích thước phù hợp cho system tray
            scaled_pixmap = pixmap.scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            return QIcon(scaled_pixmap)
        else:
            return self.create_default_icon()
    
    def create_default_icon(self):
        """Tạo icon mặc định nếu file icon không tồn tại"""
        pixmap = QPixmap(16, 16)
        pixmap.fill(QColor('transparent'))
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor('#27AE60'))  # Màu xanh cố định
        painter.setPen(QColor('darkGray'))
        painter.drawEllipse(0, 0, 15, 15)
        
        # Fan blades
        painter.setPen(QColor('white'))
        painter.drawLine(8, 3, 8, 13)  # Vertical
        painter.drawLine(3, 8, 13, 8)  # Horizontal
        painter.drawLine(5, 5, 11, 11)  # Diagonal
        painter.drawLine(5, 11, 11, 5)  # Diagonal
        
        painter.end()
        return QIcon(pixmap)
    
    def setup_tray_icon(self):
        """Thiết lập system tray icon"""
        # Tạo tray icon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.create_tray_icon())
        
        # THÊM DÒNG NÀY: Thiết lập tooltip
        self.tray_icon.setToolTip("ROSA System Monitor - Ứng dụng giám sát phần cứng")
        
        # Tạo context menu
        tray_menu = QMenu()
        
        # Show Main Window action
        show_window_action = QAction("Hiển thị cửa sổ chính", self)
        show_window_action.triggered.connect(self.show_main_window)
        tray_menu.addAction(show_window_action)
        
        tray_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("Thoát", self)
        exit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()
        
        # Hiển thị thông báo khởi động
        self.tray_icon.showMessage(
            "ROSA System Monitor", 
            "Ứng dụng đang chạy ngầm",
            QSystemTrayIcon.Information, 
            2000
        )

    def tray_icon_activated(self, reason):
        """Xử lý click vào tray icon"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_main_window()
    
    def show_main_window(self):
        """Hiển thị cửa sổ chính"""
        if self.startup_window:
            self.startup_window.show()
            self.startup_window.raise_()
            self.startup_window.activateWindow()
    
    def center_message_box(self, msg_box):
        """Căn giữa message box"""
        def center():
            # Lấy kích thước màn hình
            screen = QDesktopWidget().screenGeometry()
            # Lấy kích thước message box
            msg_size = msg_box.size()
            # Tính toán vị trí để căn giữa
            x = (screen.width() - msg_size.width()) // 2
            y = (screen.height() - msg_size.height()) // 2
            # Đặt vị trí message box
            msg_box.move(x, y)
        
        # Sử dụng QTimer để đảm bảo message box đã được hiển thị
        QTimer.singleShot(100, center)
    
    def set_message_box_icon(self, msg_box):
        """Thiết lập icon cho message box"""
        popup_icon_path = resource_path(r"assets\icon\rosa-monitor.ico") 
        
        if os.path.exists(popup_icon_path):
            msg_box.setWindowIcon(QIcon(popup_icon_path))
        else:
            print(f"Popup icon not found at: {popup_icon_path}")
    
    def quit_application(self):
        """Thoát ứng dụng - SỬ DỤNG QMessageBox TRỰC TIẾP"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Question)
        msg.setText("Bạn có chắc muốn thoát ROSA System Monitor?")
        msg.setWindowTitle("Xác nhận thoát")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        
        # THIẾT LẬP ICON CHO MESSAGE BOX
        self.set_message_box_icon(msg)
        
        # Áp dụng style
        msg.setStyleSheet(f"""
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
        """)
        
        # Căn giữa message box
        self.center_message_box(msg)
        
        result = msg.exec_()
        
        if result == QMessageBox.Yes:
            # Dừng monitoring từ startup_window nếu có
            if self.startup_window and hasattr(self.startup_window, 'stop_fan_monitoring'):
                self.startup_window.stop_fan_monitoring()
            QApplication.quit()