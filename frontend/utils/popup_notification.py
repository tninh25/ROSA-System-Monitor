# frontend/popup/popup_notification.py 
from path_helper import resource_path

import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class PopupMessage(QWidget):
    # Thêm class variable để theo dõi popup hiện tại
    _current_popup = None
    
    def __init__(self, message_type="normal", font_family=None, parent=None):
        super().__init__(parent, Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        
        # ĐỢI popup hiện tại đóng hoàn toàn trước khi tạo popup mới
        if PopupMessage._current_popup and PopupMessage._current_popup.isVisible():
            PopupMessage._current_popup.force_close()
        
        PopupMessage._current_popup = self
        
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlag(Qt.WindowDoesNotAcceptFocus)
        
        self.font_family = font_family or "Arial"

        # Xác định thông báo theo loại
        messages = {
            "normal": {
                "title": "THIẾT BỊ ĐÃ ỔN ĐỊNH",
                "subtitle": "Sự cố đã được khắc phục",
                "gradient": """
                    background: qlineargradient(
                        x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #126B2A,
                        stop: 1 #061700
                    );
                """,
                "icon_path": resource_path(r"assets\image\normal.png")
            },
            "fan_error": {
                "title": "QUẠT CPU KHÔNG QUAY",
                "subtitle": "Không phát hiện tốc độ quạt. Có thể\nquạt bị kẹt hoặc hỏng.",
                "gradient": """
                    background: qlineargradient(
                        x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #8B0808,
                        stop: 1 #2A0000
                    );
                """,
                "icon_path": resource_path(r"assets\image\fan.png")
            },
            "fan_slow": {
                "title": "QUẠT LÀM MÁT YẾU",
                "subtitle": "Quạt quay chậm hơn trong thời\ngian dài. Vệ sinh hoặc thay quạt.",
                "gradient": """
                    background: qlineargradient(
                        x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #4A126B,
                        stop: 1 #170617
                    );
                """,
                "icon_path": resource_path(r"assets\image\fan_slow.png")
            },
            "fan_fast": {
                "title": "QUẠT CPU QUÁ TẢI",
                "subtitle": "Quạt quay tối đa trong thời gian dài. Kiểm tra\nkeo tản nhiệt hoặc giảm tải CPU.",
                "gradient": """
                    background: qlineargradient(
                        x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #6B1212,
                        stop: 1 #170606
                    );
                """,
                "icon_path": resource_path(r"assets\image\fan_fast.png")
            }
        }

        style_data = messages.get(message_type, messages["normal"])
        self.setup_ui(style_data)

    def setup_ui(self, style_data):
        """Thiết lập UI với font đã được truyền vào"""
        
        # Container chính
        container = QWidget()
        container.setFixedSize(440, 150)
        container.setStyleSheet(f"""
            QWidget {{
                {style_data['gradient']}
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
        """)

        # Shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 10)
        container.setGraphicsEffect(shadow)

        # Layout chính ngang
        main_layout = QHBoxLayout(container)
        main_layout.setContentsMargins(25, 10, 25, 15)
        main_layout.setSpacing(20)

        # === Phần nội dung bên trái ===
        left_layout = QVBoxLayout()
        left_layout.setSpacing(8)
        left_layout.setAlignment(Qt.AlignVCenter)

        # Main message - SỬ DỤNG QFont ĐỂ ĐẢM BẢO BOLD HOẠT ĐỘNG
        main_label = QLabel(style_data["title"])
        main_label.setAlignment(Qt.AlignLeft)
        
        # Tạo font object cho title
        title_font = QFont(self.font_family, 14)
        title_font.setWeight(QFont.Bold) 
        main_label.setFont(title_font)
        main_label.setStyleSheet(f"""
            QLabel {{
                color: white;  
                background: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
                line-height: 1.2;
            }}
        """)

        # Sub message - SỬ DỤNG QFont
        sub_label = QLabel(style_data["subtitle"])
        sub_label.setAlignment(Qt.AlignLeft)
        
        # Tạo font object cho subtitle
        subtitle_font = QFont(self.font_family, 10, QFont.Normal)
        subtitle_font.setWeight(500)  # Medium weight
        sub_label.setFont(subtitle_font)
        sub_label.setStyleSheet(f"""
            QLabel {{
                color: #FFDCB99E;
                background: none;
                border: none;
                padding: 0px;
                margin: 0px;
            }}
        """)
        sub_label.setMinimumHeight(45)

        # Thêm các widget vào layout trái
        left_layout.addWidget(main_label)
        left_layout.addWidget(sub_label)

        # === Phần icon bên phải ===
        # === Phần icon bên phải ===
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(100, 100)  # TĂNG từ 80,80 lên 100,100 hoặc lớn hơn
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
            }
        """)

        # Load icon từ file
        icon_path = style_data["icon_path"]
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            scaled_pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)  # TĂNG từ 120,120 lên 150,150
            self.icon_label.setPixmap(scaled_pixmap)
        else:
            # Fallback icon - có thể giữ nguyên hoặc tăng kích thước
            self.icon_label.setText("!")
            icon_font = QFont(self.font_family, 24, QFont.Bold)
            self.icon_label.setFont(icon_font)
            self.icon_label.setStyleSheet("""
                QLabel {
                    background: #E74C3C;
                    border-radius: 50px;  # TĂNG border-radius cho phù hợp
                    color: white;
                }
            """)

        # === Thêm vào layout chính ===
        main_layout.addLayout(left_layout, stretch=3)
        main_layout.addWidget(self.icon_label, stretch=1)
        main_layout.setAlignment(Qt.AlignVCenter)

        # Layout chính cho widget
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(container)

        self.resize(container.size())

        # Animation và timer
        self.set_position_with_animation()
        
        self.close_timer = QTimer()
        self.close_timer.setSingleShot(True)
        self.close_timer.timeout.connect(self.close_with_animation)
        self.close_timer.start(10000)
        
        self.show_with_animation()

    def set_position_with_animation(self):
        """Đặt vị trí popup với hiệu ứng"""
        screen = QApplication.primaryScreen().availableGeometry()
        x = screen.right() - self.width() - 20
        y = screen.bottom() - self.height() - 20
        self.setGeometry(x, y, self.width(), self.height())

    def show_with_animation(self):
        """Hiệu ứng xuất hiện mượt mà"""
        self.setWindowOpacity(0.0)
        self.show()
        
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.start()

    def force_close(self):
        """Đóng popup ngay lập tức không animation"""
        try:
            if self.close_timer and self.close_timer.isActive():
                self.close_timer.stop()
            if hasattr(self, 'animation') and self.animation.state() == QPropertyAnimation.Running:
                self.animation.stop()
            self.close()
        except:
            self.close()

    def close_with_animation(self):
        """Hiệu ứng đóng mượt mà"""
        try:
            self.animation = QPropertyAnimation(self, b"windowOpacity")
            self.animation.setDuration(300)
            self.animation.setStartValue(1.0)
            self.animation.setEndValue(0.0)
            self.animation.setEasingCurve(QEasingCurve.InCubic)
            self.animation.finished.connect(self.cleanup_close)  # Sửa thành cleanup_close
            self.animation.start()
        except Exception as e:
            print(f"Animation error: {e}")
            self.cleanup_close()

    def cleanup_close(self):
        """Dọn dẹp khi đóng popup"""
        try:
            if self == PopupMessage._current_popup:
                PopupMessage._current_popup = None
            self.close()
        except:
            self.close()