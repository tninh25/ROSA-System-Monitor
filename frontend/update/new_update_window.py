#frontend/new_update_window.py
# frontend/update/update_window.py
import time
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtNetwork import *

from path_helper import resource_path

from .styles.update_styles import *
from ..utils.popup_manager import PopupManager
from ..utils.popup_notification import PopupMessage
from ..utils.left_panel import RoundedImageLabel

from backend.register import RegistrationManager
from backend.hc_fan import FanMonitor

# Thêm vào update_window.py
from PyQt5.QtCore import QRunnable, QThreadPool, pyqtSignal, QObject

class ServerSendWorker(QRunnable):
    def __init__(self, fan_monitor, payload, new_status):
        super().__init__()
        self.fan_monitor = fan_monitor
        self.payload = payload
        self.new_status = new_status

    def run(self):
        """Gửi request đến server trong thread riêng"""
        try:
            import requests
            
            # Gửi request thực tế đến server
            response = requests.post(
                self.fan_monitor.server_url,
                data=self.payload,
                verify=False,
                timeout=20
            )
            
            if response.status_code == 200:
                print(f"Request sent successfully! Status: {response.status_code}")
                self.fan_monitor.last_sent_status = self.new_status
            else:
                print(f"Server error: {response.status_code} - {response.text}")
                    
        except requests.exceptions.RequestException as e:
            print(f"Failed to send to server: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
            
class FanMonitorSignals(QObject):
    status_changed = pyqtSignal(str, float) 
    error_occurred = pyqtSignal(str)

class FanMonitorWorker(QRunnable):
    def __init__(self, fan_monitor):
        super().__init__()
        self.fan_monitor = fan_monitor
        self.signals = FanMonitorSignals()
        self.is_running = True
        self.local_previous_status = "000"

    def run(self):
        """Chạy trong thread riêng"""
        try:
            self.fan_monitor.initialize_wmi()
            self.fan_monitor.initialize_sensor_min_max()
            
        except Exception as e:
            self.signals.error_occurred.emit(f"Failed to initialize WMI: {e}")
            return
            
        while self.is_running:
            try:
                fan_rpm = self.fan_monitor.get_current_fan_reading()
                
                # CHỈ LẤY STATUS CODE (bỏ status_text)
                current_status, current_status_text = self.fan_monitor.check_fan_status(fan_rpm)
                
                # Chỉ kiểm tra thay đổi status code
                if self.local_previous_status != current_status:
                    print(f"🔍 WORKER: Status changed {self.local_previous_status} → {current_status}")
                    self.signals.status_changed.emit(current_status, fan_rpm)
                    self.local_previous_status = current_status
                
                time.sleep(self.fan_monitor.polling_interval)
                
            except Exception as e:
                self.signals.error_occurred.emit(str(e))
                break

class StartupWindow(QWidget):
    def __init__(self, font_family=None, parent=None):
        super().__init__(parent)
        self.font_family = font_family or "Arial"
        self.registration_manager = RegistrationManager() 
        self.popup_manager = PopupManager(self)

        # THÊM: Khởi tạo FanMonitor và ThreadPool
        self.fan_monitor = FanMonitor()
        self.thread_pool = QThreadPool()
        self.monitor_worker = None

        # Kéo giao diện theo chuột
        self.dragging = False
        self.drag_position = QPoint()
        self.edit_mode = False

        # Mặc định là có mạng, sẽ kiểm tra sau
        self.network_manager = QNetworkAccessManager()
        self.is_online = True  # GIẢ ĐỊNH CÓ MẠNG

        self.setup_ui()
        
        # KIỂM TRA MẠNG SAU KHI UI ĐÃ HIỂN THỊ
        QTimer.singleShot(1000, self.check_connection) 
        
        self.start_fan_monitoring()             
    
    def check_connection(self):
        """Kiểm tra kết nối mạng"""
        try:
            url = QUrl("https://www.google.com")
            request = QNetworkRequest(url)
            request.setTransferTimeout(2000)  # 3 giây timeout
            
            reply = self.network_manager.get(request)
            reply.finished.connect(lambda: self.handle_network_reply(reply))
            
        except Exception as e:
            print(f"Lỗi khi bắt đầu kiểm tra mạng: {e}")

    def handle_network_reply(self, reply):
        """Xử lý kết quả kiểm tra mạng"""
        try:
            if reply.error() == QNetworkReply.NoError:
                self.is_online = True
                print("Có kết nối internet")
            else:
                self.is_online = False
                print(f"Không có internet: {reply.errorString()}")
            
            # CẬP NHẬT UI VỚI TRẠNG THÁI MẠNG MỚI
            self.update_network_status_ui()
            
        except Exception as e:
            print(f"Lỗi xử lý kết quả mạng: {e}")
            self.is_online = False
            self.update_network_status_ui()
        finally:
            reply.deleteLater()

    def update_network_status_ui(self):
        """Cập nhật giao diện với trạng thái mạng hiện tại"""
        # Tìm và cập nhật status_label trong header
        status_label = self.findChild(QLabel, "status_label")  # Sẽ cần thêm objectName
        
        if status_label:
            # Cập nhật text và màu sắc
            if self.is_online:
                status_label.setText("Máy chủ đang hoạt động")
                status_label.setStyleSheet(get_status_styles(self.font_family, "active"))
                
                # Cập nhật cả dot_label nếu cần
                dot_label = self.findChild(QLabel, "dot_label")
                if dot_label:
                    dot_label.setStyleSheet("color: #27AE60; font-size: 8px; background: transparent; border: none;")
            else:
                status_label.setText("Không có kết nối internet")
                status_label.setStyleSheet(get_status_styles(self.font_family, "offline"))
                
                # Cập nhật cả dot_label nếu cần
                dot_label = self.findChild(QLabel, "dot_label")
                if dot_label:
                    dot_label.setStyleSheet("color: #E74C3C; font-size: 8px; background: transparent; border: none;")
        else:
            # Nếu không tìm thấy bằng objectName, tìm bằng cách khác
            self.refresh_header_display()

    def refresh_header_display(self):
        """Làm mới hiển thị header (cách đơn giản hơn)"""
        # Tìm header_content_widget hiện tại
        right_panel = self.findChild(QWidget)  # Tìm widget phải
        if right_panel:
            # Tìm header trong right_panel
            for i in range(right_panel.layout().count()):
                widget = right_panel.layout().itemAt(i).widget()
                if widget and "header_content_widget" in widget.objectName():
                    # Thay thế header cũ bằng header mới
                    new_header = self.create_header()
                    right_panel.layout().replaceWidget(widget, new_header)
                    widget.deleteLater()
                    break

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
        # TĂNG CHIỀU CAO ẢNH từ 500 lên 600
        image_container.setFixedSize(450, 600) 
        image_container.setStyleSheet("background: transparent; border: none;")
        image_layout = QVBoxLayout(image_container)
        image_layout.setContentsMargins(0, 0, 0, 0)
        
        # CẬP NHẬT: Tăng kích thước RoundedImageLabel
        self.image_label = RoundedImageLabel(radius=15, size=(450, 600)) 
        self.image_label.set_placeholder()
        image_layout.addWidget(self.image_label)
        
        left_layout.addWidget(image_container)
        return left_widget
        
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
    
    def create_right_panel(self):
        """Tạo panel bên phải chứa form cập nhật"""
        right_widget = QWidget()
        right_widget.setFixedWidth(450)
        right_widget.setStyleSheet(get_right_panel_styles())
        
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(40, 10, 20, 10)  
        right_layout.setSpacing(0)
        right_layout.setAlignment(Qt.AlignTop)
        
        # THÊM: Header với control buttons
        header_widget = self.create_header_with_controls()
        right_layout.addWidget(header_widget)
        right_layout.addSpacing(0)  
        
        # Header với logo và trạng thái
        header_content_widget = self.create_header()
        right_layout.addWidget(header_content_widget)
        right_layout.addSpacing(10)
        
        # Thông tin giám sát
        monitoring_widget = self.create_monitoring_section()
        right_layout.addWidget(monitoring_widget)
        right_layout.addSpacing(30)
        
        # Form thông tin hiện tại VÀ cập nhật tích hợp
        info_widget = self.create_current_info_section()
        right_layout.addWidget(info_widget)
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

    def create_header(self):
        """Tạo header với logo và trạng thái server"""
        header_content_widget = QWidget()
        header_content_widget.setObjectName("header_content_widget")  # THÊM objectName
        header_content_widget.setStyleSheet("background: transparent; border: none;")
        
        header_layout = QHBoxLayout(header_content_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(0)
        
        # Logo bên trái
        logo_label = self.create_logo()
        header_layout.addWidget(logo_label)
        
        # Spacer
        header_layout.addStretch()
        
        # Trạng thái server bên phải
        status_widget = QWidget()
        status_widget.setStyleSheet("background: transparent; border: none;")
        status_layout = QVBoxLayout(status_widget)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(2)
        status_layout.setAlignment(Qt.AlignRight)
        
        # Icon chấm tròn + text
        status_container = QWidget()
        status_container.setStyleSheet("background: transparent; border: none;")
        status_container_layout = QHBoxLayout(status_container)
        status_container_layout.setContentsMargins(0, 0, 0, 0)
        status_container_layout.setSpacing(5)
        
        # Xác định trạng thái và màu sắc
        if self.is_online:
            status_text = "Máy chủ đang hoạt động"
            dot_color = "#27AE60"  # Xanh
            status_type = "active"
        else:
            status_text = "Không có kết nối internet"
            dot_color = "#E74C3C"  # Đỏ
            status_type = "offline"
        
        # Tạo icon chấm tròn
        dot_label = QLabel("●")
        dot_label.setObjectName("dot_label")  # THÊM objectName
        dot_label.setStyleSheet(f"color: {dot_color}; font-size: 8px; background: transparent; border: none;")
        dot_label.setFixedSize(10, 10)
        
        status_label = QLabel(status_text)
        status_label.setObjectName("status_label")  # THÊM objectName
        status_label.setStyleSheet(get_status_styles(self.font_family, status_type))
        
        status_container_layout.addWidget(dot_label)
        status_container_layout.addWidget(status_label)
        status_container_layout.addStretch()
        
        status_layout.addWidget(status_container)
        header_layout.addWidget(status_widget)
        
        return header_content_widget

    def create_monitoring_section(self):
        """Tạo phần thông tin giám sát"""
        monitoring_widget = QWidget()
        monitoring_widget.setStyleSheet("background: transparent; border: none;")
        
        monitoring_layout = QHBoxLayout(monitoring_widget)
        monitoring_layout.setContentsMargins(0, 0, 0, 0)
        monitoring_layout.setSpacing(8)
        
        # THÊM: Stretch bên trái để đẩy nội dung vào giữa
        monitoring_layout.addStretch()
        
        # Icon monitoring
        icon_label = QLabel("📊")
        icon_label.setStyleSheet("font-size: 16px; background: transparent; border: none;")
        
        text_label = QLabel("Thiết bị đang được giám sát")
        text_label.setStyleSheet(get_monitoring_styles(self.font_family))
        
        monitoring_layout.addWidget(icon_label)
        monitoring_layout.addWidget(text_label)
        
        # THÊM: Stretch bên phải để cân bằng
        monitoring_layout.addStretch()
        
        return monitoring_widget

    def create_current_info_section(self):
        """Tạo phần hiển thị và cập nhật thông tin tích hợp"""
        info_widget = QWidget()
        info_widget.setStyleSheet("background: transparent; border: none;")
        
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(15)
        
        # Load thông tin từ JSON
        current_info = self.registration_manager.get_registration_info()
        
        if current_info:
            reg_info = current_info.get("registration", {})
            
            # Tên công ty - HIỂN THỊ HOẶC CHỈNH SỬA
            self.company_row = self.create_info_display_row("Tên công ty:", reg_info.get("company_name", ""))
            info_layout.addWidget(self.company_row)
            
            # Tên máy - HIỂN THỊ HOẶC CHỈNH SỬA
            self.machine_row = self.create_info_display_row("Tên máy:", reg_info.get("machine_name", ""))
            info_layout.addWidget(self.machine_row)
            
            # Email - HIỂN THỊ HOẶC CHỈNH SỬA
            self.email_row = self.create_info_display_row("Email:", reg_info.get("email", ""))
            info_layout.addWidget(self.email_row)
            
            # Ngày đăng ký - chỉ hiển thị (không thể chỉnh sửa)
            reg_date = reg_info.get("registration_date", "")
            if reg_date:
                try:
                    date_obj = datetime.fromisoformat(reg_date)
                    formatted_date = date_obj.strftime("%d/%m/%Y %H:%M")
                    date_widget = self.create_info_row("Ngày đăng ký:", formatted_date)
                    info_layout.addWidget(date_widget)
                except:
                    pass
        
        else:
            # Nếu chưa có thông tin đăng ký
            no_data_label = QLabel("Chưa có thông tin đăng ký")
            no_data_label.setStyleSheet(get_info_label_styles(self.font_family))
            no_data_label.setAlignment(Qt.AlignCenter)
            info_layout.addWidget(no_data_label)
        
        # THÊM spacing TRƯỚC desc label
        info_layout.addSpacing(10)
        
        # Desc label
        desc_label = QLabel("Khi phát hiện sự cố hệ thống, email sẽ được gửi tự động đến địa chỉ trên.")
        desc_label.setStyleSheet(f"""
            color: #666666;
            font-family: {self.font_family};
            font-size: 12px;
            background: transparent;
            border: none;
            padding: 8px 0px;
            line-height: 1.4;
        """)
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setMinimumHeight(40)
        info_layout.addWidget(desc_label)
        
        # THÊM spacing SAU desc label
        info_layout.addSpacing(15)
        
        # Nút chỉnh sửa/cập nhật - BAN ĐẦU LÀ "CHỈNH SỬA THÔNG TIN"
        self.edit_button = QPushButton("CHỈNH SỬA THÔNG TIN")
        self.edit_button.setFixedHeight(50)
        self.edit_button.setStyleSheet(get_edit_button_styles(self.font_family))  # ⬅️ Style riêng
        self.edit_button.clicked.connect(self.on_edit_clicked)  # ⬅️ Kết nối sự kiện mới
        info_layout.addWidget(self.edit_button)
        
        info_layout.addStretch()
        
        return info_widget

    def on_edit_clicked(self):
        """Xử lý khi nhấn nút chỉnh sửa/cập nhật"""
        if not self.edit_mode:
            # Chuyển sang chế độ chỉnh sửa
            self.enter_edit_mode()
        else:
            # Chuyển sang chế độ cập nhật
            self.on_update_clicked()

    def enter_edit_mode(self):
        """Vào chế độ chỉnh sửa"""
        self.edit_mode = True
        
        # Ẩn labels, hiện line edits
        self.company_label.setVisible(False)
        self.company_edit.setVisible(True)
        
        self.machine_label.setVisible(False)
        self.machine_edit.setVisible(True)
        
        self.email_label.setVisible(False)
        self.email_edit.setVisible(True)
        
        # Đổi text nút thành "CẬP NHẬT THÔNG TIN"
        self.edit_button.setText("CẬP NHẬT THÔNG TIN")
        self.edit_button.setStyleSheet(get_update_button_styles(self.font_family))  # Style khác

    def exit_edit_mode(self):
        """Thoát chế độ chỉnh sửa"""
        self.edit_mode = False
        
        # Hiện labels, ẩn line edits
        self.company_label.setVisible(True)
        self.company_edit.setVisible(False)
        
        self.machine_label.setVisible(True)
        self.machine_edit.setVisible(False)
        
        self.email_label.setVisible(True)
        self.email_edit.setVisible(False)
        
        # Đổi text nút thành "CHỈNH SỬA THÔNG TIN"
        self.edit_button.setText("CHỈNH SỬA THÔNG TIN")
        self.edit_button.setStyleSheet(get_edit_button_styles(self.font_family))

    def create_info_display_row(self, label, value):
        """Tạo dòng thông tin có thể chuyển đổi giữa hiển thị và chỉnh sửa"""
        row_widget = QWidget()
        row_widget.setStyleSheet("background: transparent; border: none;")
        
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(15)
        
        # Label bên trái
        label_widget = QLabel(label)
        label_widget.setStyleSheet(get_info_label_styles(self.font_family))
        label_widget.setFixedWidth(80)
        
        # QLabel để hiển thị (ban đầu)
        value_label = QLabel(value)
        value_label.setStyleSheet(get_info_value_styles(self.font_family))
        value_label.setFixedHeight(45)
        value_label.setMinimumWidth(250)
        
        # QLineEdit để chỉnh sửa (ban đầu ẩn)
        line_edit = QLineEdit()
        line_edit.setText(value)
        line_edit.setPlaceholderText(f"Nhập {label.lower()}")
        line_edit.setFixedHeight(45)
        line_edit.setMinimumWidth(250)
        line_edit.setStyleSheet(get_input_styles(self.font_family))
        line_edit.setVisible(False)  # ⬅️ Ban đầu ẩn đi
        
        row_layout.addWidget(label_widget)
        row_layout.addWidget(value_label)
        row_layout.addWidget(line_edit)  
        row_layout.addStretch()
        
        # Lưu reference để có thể chuyển đổi
        if label == "Tên công ty:":
            self.company_label = value_label
            self.company_edit = line_edit
        elif label == "Tên máy:":
            self.machine_label = value_label
            self.machine_edit = line_edit
        elif label == "Email:":
            self.email_label = value_label
            self.email_edit = line_edit
        
        return row_widget

    def create_editable_info_row(self, label, current_value):
        """Tạo một dòng thông tin có thể chỉnh sửa"""
        row_widget = QWidget()
        row_widget.setStyleSheet("background: transparent; border: none;")
        
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(15)
        
        # Label bên trái
        label_widget = QLabel(label)
        label_widget.setStyleSheet(get_info_label_styles(self.font_family))
        label_widget.setFixedWidth(80)
        
        # QLineEdit bên phải chứa dữ liệu hiện tại
        line_edit = QLineEdit()
        line_edit.setText(current_value)
        line_edit.setPlaceholderText(f"Nhập {label.lower()}")
        line_edit.setFixedHeight(45)
        line_edit.setMinimumWidth(250)
        line_edit.setStyleSheet(get_input_styles(self.font_family))
        
        row_layout.addWidget(label_widget)
        row_layout.addWidget(line_edit)
        row_layout.addStretch()
        
        # Lưu reference đến line_edit dựa trên label
        if label == "Tên công ty:":
            self.company_edit = line_edit
        elif label == "Tên máy:":
            self.machine_edit = line_edit
        elif label == "Email:":
            self.email_edit = line_edit
        
        return row_widget  # QUAN TRỌNG: trả về row_widget, không phải line_edit

    def create_info_row(self, label, value):
        """Tạo một dòng thông tin chỉ hiển thị (không chỉnh sửa)"""
        row_widget = QWidget()
        row_widget.setStyleSheet("background: transparent; border: none;")
        
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(15)
        
        label_widget = QLabel(label)
        label_widget.setStyleSheet(get_info_label_styles(self.font_family))
        label_widget.setFixedWidth(100)
        
        value_widget = QLabel(value)
        value_widget.setStyleSheet(get_info_value_styles(self.font_family))
        
        row_layout.addWidget(label_widget)
        row_layout.addWidget(value_widget)
        row_layout.addStretch()
        
        return row_widget

    def on_update_clicked(self):
        """Xử lý khi nhấn nút cập nhật"""
        updates = {}
        
        # Lấy dữ liệu từ các QLineEdit
        company = self.company_edit.text().strip()
        current_company = self.company_label.text()
        if company and company != current_company:
            updates["company_name"] = company
            
        machine = self.machine_edit.text().strip()
        current_machine = self.machine_label.text()
        if machine and machine != current_machine:
            updates["machine_name"] = machine
            
        email = self.email_edit.text().strip()
        current_email = self.email_label.text()
        if email and email != current_email:
            if "@" not in email:
                self.popup_manager.show_error("Email không hợp lệ")
                return
            updates["email"] = email
        
        if updates:
            success, message = self.registration_manager.update_registration(**updates)
            if success:
                self.popup_manager.show_success(message)
                # Cập nhật labels với giá trị mới
                if "company_name" in updates:
                    self.company_label.setText(updates["company_name"])
                if "machine_name" in updates:
                    self.machine_label.setText(updates["machine_name"])
                if "email" in updates:
                    self.email_label.setText(updates["email"])
                
                self.highlight_updated_fields(updates.keys())
                self.exit_edit_mode()  # Thoát chế độ chỉnh sửa sau khi cập nhật thành công
            else:
                self.popup_manager.show_error(message)
        else:
            self.popup_manager.show_info("Không có thông tin nào được thay đổi")
            self.exit_edit_mode()  # Thoát chế độ chỉnh sửa nếu không có thay đổi

    def highlight_updated_fields(self, updated_fields):
        """Highlight các trường vừa được cập nhật"""
        highlight_style = "border: 2px solid #27AE60; background-color: #F8FFF8;"
        
        if "company_name" in updated_fields:
            self.company_edit.setStyleSheet(get_input_styles(self.font_family) + highlight_style)
        
        if "machine_name" in updated_fields:
            self.machine_edit.setStyleSheet(get_input_styles(self.font_family) + highlight_style)
        
        if "email" in updated_fields:
            self.email_edit.setStyleSheet(get_input_styles(self.font_family) + highlight_style)
        
        # Reset style sau 2 giây
        QTimer.singleShot(2000, self.reset_field_styles)

    def reset_field_styles(self):
        """Reset style của các field về bình thường"""
        self.company_edit.setStyleSheet(get_input_styles(self.font_family))
        self.machine_edit.setStyleSheet(get_input_styles(self.font_family))
        self.email_edit.setStyleSheet(get_input_styles(self.font_family))
        
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
    
    # Sửa method on_activate_clicked:
    def on_activate_clicked(self):
        """Xử lý khi nhấn nút kích hoạt"""
        company = self.company_input.text().strip()
        machine = self.machine_input.text().strip()
        email = self.email_input.text().strip()
        
        # Sử dụng backend để đăng ký
        success, messages = self.registration_manager.register_system(
            company=company,
            machine=machine,
            email=email,
            os_info=os.name,
            timestamp=datetime.now().isoformat()
        )
        
        if success:
            self.popup_manager.show_success(messages[0])  # SỬ DỤNG POPUP MANAGER
            print("Registration successful!")
        else:
            self.popup_manager.show_error("\n".join(messages))  # SỬ DỤNG POPUP MANAGER

    #-----------------FAN MONITORING----------------------
    def start_fan_monitoring(self):
        """Bắt đầu giám sát quạt sử dụng QRunnable"""
        try:
            # Tạ worker
            self.monitor_worker = FanMonitorWorker(self.fan_monitor)
            self.monitor_worker.signals.status_changed.connect(self.on_fan_status_changed)
            self.monitor_worker.signals.error_occurred.connect(self.on_monitor_error)
            
            # Khởi chạy worker trong thread pool
            self.thread_pool.start(self.monitor_worker)
            
        except Exception as e:
            print(f"❌ Error starting fan monitoring: {e}")

    def on_fan_status_changed(self, new_status, fan_rpm):  # BỎ status_text
        """Xử lý khi trạng thái quạt thay đổi"""
        try:
            old_status = self.fan_monitor.current_status
            
            # Cập nhật trạng thái
            self.fan_monitor.current_status = new_status
            self.fan_monitor.previous_status = old_status
            
            # Ghi log thay đổi
            change_record = {
                'timestamp': datetime.now().isoformat(),
                'from_status': old_status,
                'to_status': new_status,
                'fan_speed': fan_rpm
            }
            self.fan_monitor.status_changes.append(change_record)
            
            # Hiển thị popup DỰA TRÊN STATUS CODE
            self.show_fan_popup(new_status, fan_rpm)  # BỎ status_text
            
            # GỬI REQUEST KHI CÓ THAY ĐỔI
            if new_status != old_status:
                print(f"UI: Status changed {old_status} → {new_status}")
                
                # Tạo dữ liệu đầy đủ
                server_data = {
                    'timestamp': change_record['timestamp'],
                    'old_status': old_status,
                    'new_status': new_status,
                    'fan_speed': fan_rpm,
                }
                
                # Gọi method từ hc_fan.py
                self.fan_monitor.send_status_to_server(server_data)
            
            # In thông báo console
            status_names = {
                "000": "Normal",
                "001": "Fan Stopped", 
                "002": "Fan Slow",
                "003": "Fan Fast"
            }
            print(f"STATUS CHANGED: {status_names.get(old_status, old_status)} → {status_names.get(new_status, new_status)} | RPM: {fan_rpm}")
            
        except Exception as e:
            print(f"Error handling status change: {e}")

    def send_status_to_server_async(self, old_status, new_status, fan_rpm):
        """Gửi trạng thái đến server trong thread riêng"""
        try:
            # Chuẩn bị dữ liệu
            status_data = {
                'old_status': old_status,
                'new_status': new_status, 
                'fan_speed': fan_rpm,
                'timestamp': datetime.now().isoformat()
            }
            
            # Tạo worker cho network request
            server_worker = ServerSendWorker(self.fan_monitor, status_data)
            self.thread_pool.start(server_worker)
            
        except Exception as e:
            print(f"Error sending to server: {e}")

    def on_monitor_error(self, error_message):
        """Xử lý lỗi từ monitor worker"""
        print(f"Monitor error: {error_message}")

    def show_fan_popup(self, status, fan_rpm):
        """Hiển thị popup thông báo trạng thái quạt - SỬ DỤNG STATUS CODE"""
        try:
            # Ánh xạ trực tiếp từ status code sang popup type
            status_mapping = {
                "000": "normal",     # Bình thường
                "001": "fan_error",  # Quạt không hoạt động
                "002": "fan_slow",   # Quạt quay chậm  
                "003": "fan_fast"    # Quạt quay quá nhanh
            }
            
            popup_type = status_mapping.get(status, "normal")
            popup = PopupMessage(popup_type, font_family=self.font_family)
            popup.show()
                
        except Exception as e:
            print(f"Error showing popup: {e}")

    def stop_fan_monitoring(self):
        """Dừng giám sát quạt"""
        if self.monitor_worker:
            self.monitor_worker.stop()
        
        # Đợi các worker hoàn thành (timeout 2 giây)
        self.thread_pool.waitForDone(2000)
        
    def setup_tray_integration(self):
        """Thiết lập tích hợp với system tray"""
        from frontend.utils.tray_integration import FanMonitorTrayApp
        self.tray_app = FanMonitorTrayApp(self.font_family, self)

    def close_window(self):
        """Đóng cửa sổ và chuyển sang chế độ system tray"""
        self.hide()  # Ẩn thay vì đóng
        
        # Khởi tạo system tray nếu chưa có
        if not hasattr(self, 'tray_app'):
            self.setup_tray_integration()

    def closeEvent(self, event):
        """Xử lý sự kiện đóng cửa sổ"""
        self.close_window()
        event.ignore()  # Không đóng hoàn toàn, chỉ ẩn
