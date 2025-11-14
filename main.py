# main.py
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
from frontend.utils.popup_notification import PopupMessage
from path_helper import resource_path

class MainApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)  # QUAN TRỌNG: Không thoát khi đóng cửa sổ
        
        # THÊM: Thiết lập icon cho toàn bộ ứng dụng
        self.set_application_icon()
        
        self.load_fonts()
        
    def set_application_icon(self):
        """Thiết lập icon cho toàn bộ ứng dụng"""
        icon_path = resource_path(r"assets\icon\rosa-monitor.ico")
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            scaled_pixmap = pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            app_icon = QIcon(scaled_pixmap)
            self.app.setWindowIcon(app_icon)
        else:
            print(f"Application icon not found at: {icon_path}")
        
    def load_fonts(self):
        """Load cả font Regular và Bold"""
        font_id_regular = QFontDatabase.addApplicationFont(
            resource_path(r"assets\font\Montserrat-Regular.ttf")
        )
        
        font_id_bold = QFontDatabase.addApplicationFont(
            resource_path(r"assets\font\Montserrat-Bold.ttf")
        )
        
        if font_id_regular != -1:
            self.font_family = QFontDatabase.applicationFontFamilies(font_id_regular)[0]
        else:
            self.font_family = "Arial"
            
        font = self.app.font()
        font.setFamily(self.font_family)
        self.app.setFont(font)
        
    def show_popup(self, message_type="normal"):
        """Hiển thị popup với font family"""
        popup = PopupMessage(
            message_type=message_type,
            font_family=self.font_family
        )
        return popup
        
    def show_register_window(self):
        """Hiển thị màn hình đăng ký"""
        from frontend.register.register_window import StartupWindow
        
        self.register_window = StartupWindow(font_family=self.font_family)
        
        image_path = resource_path(r"assets\image\cpu-background.png") 
        self.register_window.set_image(image_path)
        
        # Kết nối signal khi đăng ký thành công
        self.register_window.registration_completed.connect(self.on_registration_completed)
        
        self.register_window.show()
    
    def on_registration_completed(self):
        """Xử lý khi đăng ký thành công - hiện màn hình update"""
        # Đóng màn hình đăng ký
        if hasattr(self, 'register_window'):
            self.register_window.close()
        
        # Hiện màn hình update
        self.show_update_window()
    
    def show_update_window(self):
        """Hiển thị màn hình update"""
        from frontend.update.update_window import StartupWindow
        
        self.update_window = StartupWindow(font_family=self.font_family)
        
        image_path = resource_path(r"assets\image\cpu-background.png") 
        self.update_window.set_image(image_path)
        
        self.update_window.show()

    def run_tray_only(self):
        """Chạy chỉ ở chế độ system tray (không hiển thị cửa sổ)"""
        from frontend.utils.tray_integration import FanMonitorTrayApp
        self.tray_app = FanMonitorTrayApp(self.font_family)
        
    def run(self, tray_only=False):
        """Chạy ứng dụng với lựa chọn chế độ"""
        from backend.register import RegistrationManager
        
        registration_manager = RegistrationManager()
        
        if tray_only:
            # Chạy system tray
            self.run_tray_only()
        else:
            # Kiểm tra trạng thái đăng ký
            if registration_manager.is_registered():
                # ĐÃ ĐĂNG KÝ: Chạy ngầm luôn (không hiện cửa sổ)
                self.run_tray_only()
            else:
                # CHƯA ĐĂNG KÝ: Hiện màn hình đăng ký
                self.show_register_window()
        
        return self.app.exec_()

if __name__ == "__main__":
    import argparse
    import os 
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--tray', action='store_true', help='Chạy ứng dụng dưới dạng system tray (không hiển thị cửa sổ)')
    args = parser.parse_args()
    
    main_app = MainApp()
    
    sys.exit(main_app.run(tray_only=args.tray))