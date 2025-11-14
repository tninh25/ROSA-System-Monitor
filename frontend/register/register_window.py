# frontend/register/register_window.py
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from backend.register import RegistrationManager
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from path_helper import resource_path
from .styles.register_styles import *
from ..utils.popup_manager import PopupManager
from ..utils.left_panel import RoundedImageLabel

class StartupWindow(QWidget):
    registration_completed = pyqtSignal()
    def __init__(self, font_family=None, parent=None):
        super().__init__(parent)
        self.font_family = font_family or "Arial"
        self.registration_manager = RegistrationManager()
        self.popup_manager = PopupManager(self, font_family=self.font_family)
        self.dragging = False
        self.drag_position = QPoint()
        self.setup_ui()
    
    def keyPressEvent(self, event):
        """Xử lý sự kiện phím"""
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.on_activate_clicked()
            event.accept()
        else:
            super().keyPressEvent(event)

    def setup_ui(self):
        """Thiết lập giao diện startup"""
        self.setWindowTitle("Khởi động hệ thống")
        self.setFixedSize(1000, 700)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet(get_main_styles())
        
        # Layout chính
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setSpacing(20)
        
        # === PHẦN BÊN TRÁI - ẢNH ===
        left_widget = self.create_left_panel()
        
        # === PHẦN BÊN PHẢI - FORM NHẬP ===
        right_widget = self.create_right_panel()
        
        main_layout.addWidget(left_widget)
        main_layout.addWidget(right_widget)
    
    def create_left_panel(self):
        """Tạo panel bên trái chứa ảnh"""
        left_widget = QWidget()
        left_widget.setFixedWidth(450)
        left_widget.setStyleSheet(get_left_panel_styles())
        
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)
        
        image_container = QWidget()
        image_container.setFixedSize(450, 600)
        image_container.setStyleSheet("background: transparent; border: none;")
        image_layout = QVBoxLayout(image_container)
        image_layout.setContentsMargins(0, 0, 0, 0)
        
        self.image_label = RoundedImageLabel(radius=15, size=(450, 600))
        self.image_label.set_placeholder()
        image_layout.addWidget(self.image_label)
        
        left_layout.addWidget(image_container)
        return left_widget
    
    def create_right_panel(self):
        """Tạo panel bên phải chứa form nhập"""
        right_widget = QWidget()
        right_widget.setFixedWidth(450)
        right_widget.setStyleSheet(get_right_panel_styles())
        
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(40, 10, 20, 50)  # GIẢM: top margin từ 15 xuống 10
        right_layout.setSpacing(0)
        right_layout.setAlignment(Qt.AlignTop)
        
        # Header với control buttons
        header_widget = self.create_header_with_controls()
        right_layout.addWidget(header_widget)
        right_layout.addSpacing(0)  # GIẢM: từ 2 xuống 0 (loại bỏ hoàn toàn)
        
        # Logo
        logo_label = self.create_logo()
        right_layout.addWidget(logo_label, alignment=Qt.AlignLeft)
        right_layout.addSpacing(0)  # GIẢM: từ 5 xuống 0 (loại bỏ hoàn toàn)
        
        # Tiêu đề chính
        title_label = self.create_title_form()
        right_layout.addWidget(title_label)
        right_layout.addSpacing(30)  # TĂNG: khoảng cách giữa desc và form lên 30px
        
        # Form nhập liệu
        form_widget = self.create_input_form()
        right_layout.addWidget(form_widget)
        right_layout.addStretch()
        
        return right_widget

    def create_header_with_controls(self):
        """Tạo header với các nút điều khiển"""
        header_widget = QWidget()
        header_widget.setStyleSheet("background: transparent; border: none;")
        header_widget.setFixedHeight(30)
        
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)
        
        header_layout.addStretch()
        
        # Nút thu nhỏ
        self.minimize_btn = QPushButton("−")  # Dấu trừ
        self.minimize_btn.setFixedSize(20, 20)
        self.minimize_btn.setStyleSheet(get_minimize_button_styles())
        self.minimize_btn.clicked.connect(self.minimize_window)
        
        # Nút đóng
        self.close_btn = QPushButton("×")  # Dấu nhân
        self.close_btn.setFixedSize(20, 20)
        self.close_btn.setStyleSheet(get_close_button_styles())
        self.close_btn.clicked.connect(self.close_window)
        
        header_layout.addWidget(self.minimize_btn)
        header_layout.addWidget(self.close_btn)
        
        return header_widget

    def minimize_window(self):
        """Thu nhỏ cửa sổ"""
        self.showMinimized()

    def close_window(self):
        """Đóng cửa sổ"""
        self.close()

    def create_logo(self):
        """Tạo logo"""
        logo_label = QLabel()
        logo_label.setFixedSize(90, 90)
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("background: transparent; border: none;")

        logo_path = resource_path(r"assets\image\logo.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            scaled_pixmap = pixmap.scaled(90, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
        else:
            logo_label.setText("ROSA")
            logo_label.setStyleSheet(get_logo_styles(self.font_family))
        
        return logo_label
    
    def create_title_form(self):
        """Tạo phần tiêu đề và mô tả"""
        title_widget = QWidget()
        title_widget.setStyleSheet("background: transparent; border: none;")
        
        title_layout = QVBoxLayout(title_widget)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(8)  # GIẢM: từ 15 xuống 8 (khoảng cách giữa title và desc)
        
        title_label = QLabel("NHẬP THÔNG TIN")
        title_label.setStyleSheet(get_title_styles(self.font_family))
        title_label.setFixedHeight(30)  # GIẢM: từ 40 xuống 30
        
        desc_label = QLabel("Nhập đủ thông tin để bật giám sát hệ thống tự động \nvà nhận cảnh báo sớm về các sự cố")
        desc_label.setStyleSheet(get_desc_styles(self.font_family))
        desc_label.setFixedHeight(40)  # GIẢM: từ 50 xuống 40
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(desc_label)
        
        return title_widget

    def create_input_form(self):
        """Tạo form nhập liệu đơn giản"""
        form_widget = QWidget()
        form_widget.setStyleSheet("background: transparent; border: none;")
        form_layout = QVBoxLayout(form_widget)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(15)
        
        # Ô nhập tên công ty
        self.company_input = QLineEdit()
        self.company_input.setPlaceholderText("Tên công ty")
        self.company_input.setFixedHeight(45)
        self.company_input.setStyleSheet(get_input_styles(self.font_family))
        
        # Ô nhập tên máy
        self.machine_input = QLineEdit()
        self.machine_input.setPlaceholderText("Tên máy/thiết bị")
        self.machine_input.setFixedHeight(45)
        self.machine_input.setStyleSheet(get_input_styles(self.font_family))
        
        # Ô nhập email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email nhận thông báo")
        self.email_input.setFixedHeight(45)
        self.email_input.setStyleSheet(get_input_styles(self.font_family))
        
        # THÊM DÒNG MÔ TẢ Ở ĐÂY
        desc_label = QLabel("Khi phát hiện sự cố hệ thống, email sẽ được gửi tự động đến địa chỉ trên.")
        desc_label.setStyleSheet(f"""
            color: #004386;
            font-family: "{self.font_family}";
            font-size: 12px;
            font-weight: 300; 
            background: transparent;
            border: none;
            padding: 8px 0px;
            line-height: 1.4;
        """)
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setMinimumHeight(40)
        
        # Thêm stretch để đẩy nút xuống dưới
        form_layout.addWidget(self.company_input)
        form_layout.addWidget(self.machine_input)
        form_layout.addWidget(self.email_input)
        form_layout.addWidget(desc_label)  # THÊM DÒNG MÔ TẢ
        form_layout.addStretch()  # THÊM STRETCH ĐỂ ĐẨY NÚT XUỐNG
        
        # Nút kích hoạt
        self.activate_button = QPushButton("Kích hoạt tính năng")
        self.activate_button.setFixedHeight(40)
        self.activate_button.setStyleSheet(get_button_styles(self.font_family))
        self.activate_button.clicked.connect(self.on_activate_clicked)
        
        form_layout.addWidget(self.activate_button)
        
        return form_widget
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.dragging:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            event.accept()
    
    def set_image(self, image_path):
        """Thiết lập ảnh từ đường dẫn"""
        self.image_label.set_rounded_pixmap(image_path)
    
    def on_activate_clicked(self):
        """Xử lý khi nhấn nút kích hoạt"""
        company = self.company_input.text().strip()
        machine = self.machine_input.text().strip()
        email = self.email_input.text().strip()
        
        # Validation cơ bản
        if not company or not machine or not email:
            self.popup_manager.show_error("Vui lòng điền đầy đủ thông tin")
            return
        
        if "@" not in email:
            self.popup_manager.show_error("Email không hợp lệ")
            return
        
        # Sử dụng backend để đăng ký
        success, messages = self.registration_manager.register_system(
            company=company,
            machine=machine,
            email=email,
            os_info=os.name,
            timestamp=datetime.now().isoformat()
        )
        
        if success:
            self.popup_manager.show_success(messages[0])
            print("Registration successful!")
            
            # QUAN TRỌNG: Đóng cửa sổ đăng ký và mở cửa sổ update
            QTimer.singleShot(1500, self.open_update_window)  # Đợi 1.5 giây rồi chuyển
        
        else:
            self.popup_manager.show_error("\n".join(messages))

    def open_update_window(self):
        """Mở cửa sổ update và đóng cửa sổ hiện tại"""
        from frontend.update.update_window import StartupWindow
        from path_helper import resource_path
        
        # Tạo cửa sổ update mới
        self.update_window = StartupWindow(font_family=self.font_family)
        image_path = resource_path(r"assets\image\cpu-background.png")
        self.update_window.set_image(image_path)
        
        # Hiển thị cửa sổ update và đóng cửa sổ đăng ký
        self.update_window.show()
        self.close()