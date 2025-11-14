import time
import json
import yaml
import requests
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from datetime import datetime
import os
import sys
import base64
import random

# PyQt5 imports
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class ConfigWindow(QMainWindow):
    def __init__(self, monitor):
        super().__init__()
        self.monitor = monitor
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Fan Monitor Configuration")
        self.setFixedSize(500, 400)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("CẤU HÌNH FAN MONITOR")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
            }
        """)
        layout.addWidget(title)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        # Email input
        self.email_input = QLineEdit()
        self.email_input.setText(self.monitor.config.get('email', 'tranninh903@gmail.com'))
        self.email_input.setPlaceholderText("Nhập email nhận cảnh báo")
        form_layout.addRow("📧 Email:", self.email_input)
        
        # Company name input
        self.company_input = QLineEdit()
        self.company_input.setText(self.monitor.config.get('company_name', 'Viet Son JSC'))
        self.company_input.setPlaceholderText("Nhập tên công ty")
        form_layout.addRow("🏢 Company Name:", self.company_input)
        
        # Machine name input
        self.machine_input = QLineEdit()
        self.machine_input.setText(self.monitor.config.get('machine_name', 'PC-01'))
        self.machine_input.setPlaceholderText("Nhập tên máy")
        form_layout.addRow("💻 Machine Name:", self.machine_input)
        
        # Selected fan dropdown
        self.fan_combo = QComboBox()
        fan_names = list(self.monitor.simulated_fans.keys())
        self.fan_combo.addItems(fan_names)
        current_fan = self.monitor.config.get('selected_fan', 'CPU Fan #1')
        if current_fan in fan_names:
            self.fan_combo.setCurrentText(current_fan)
        form_layout.addRow("🎯 Fan Monitor:", self.fan_combo)
        
        # Polling interval
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 60)
        self.interval_spin.setValue(self.monitor.config.get('polling_interval', 5))
        self.interval_spin.setSuffix(" seconds")
        form_layout.addRow("⏰ Polling Interval:", self.interval_spin)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("💾 Save & Start Monitor")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #219a52;
            }
        """)
        self.save_btn.clicked.connect(self.save_config)
        
        self.cancel_btn = QPushButton("❌ Cancel")
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px 20px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.cancel_btn.clicked.connect(self.close)
        
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
    def save_config(self):
        # Validate email
        email = self.email_input.text().strip()
        if not email or '@' not in email:
            self.show_status("❌ Please enter a valid email address", "red")
            return
            
        # Update monitor configuration
        self.monitor.config.update({
            'email': email,
            'company_name': self.company_input.text().strip(),
            'machine_name': self.machine_input.text().strip(),
            'selected_fan': self.fan_combo.currentText(),
            'polling_interval': self.interval_spin.value()
        })
        
        # Save to file
        try:
            with open(self.monitor.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.monitor.config, f, default_flow_style=False, allow_unicode=True)
            
            self.monitor.polling_interval = self.interval_spin.value()
            self.show_status("✅ Configuration saved successfully!", "green")
            
            # Close window after short delay
            QTimer.singleShot(1000, self.accept_and_close)
            
        except Exception as e:
            self.show_status(f"❌ Error saving config: {e}", "red")
    
    def show_status(self, message, color):
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"color: {color}; font-weight: bold;")
    
    def accept_and_close(self):
        self.close()
        self.monitor.start_monitoring()

class PopupMessage(QWidget):
    def __init__(self, message_type="normal", parent=None):
        super().__init__(parent, Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlag(Qt.WindowDoesNotAcceptFocus)
        
        # Xác định thông báo theo loại
        messages = {
            "normal": {
                "title": "THIẾT BỊ ĐÃ\nBÌNH THƯỜNG",
                "subtitle": "Sự cố đã được khắc phục",
                "gradient": """
                    background: qlineargradient(
                        x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #126B2A,
                        stop: 1 #061700
                    );
                """,
                "icon_path": "assets/icon/normal.png"
            },
            "fan": {
                "title": "QUẠT ĐANG\nGẶP SỰ CỐ",
                "subtitle": "Vui lòng kiểm tra linh kiện",
                "gradient": """
                    background: qlineargradient(
                        x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #6B1212,
                        stop: 1 #170606
                    );
                """,
                "icon_path": "assets/icon/fan.png"
            }
        }
        
        style_data = messages.get(message_type, messages["normal"])
        
        # Container chính với gradient background - LỚN HƠN
        container = QWidget()
        container.setFixedSize(450, 150)  # Tăng kích thước
        container.setStyleSheet(f"""
            QWidget {{
                {style_data['gradient']}
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
        """)
        
        # Thêm shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 10)
        container.setGraphicsEffect(shadow)

        # Layout chính ngang
        main_layout = QHBoxLayout(container)
        main_layout.setContentsMargins(25, 20, 25, 20)  # Tăng padding
        main_layout.setSpacing(20)

        # === Phần nội dung bên trái ===
        left_layout = QVBoxLayout()
        left_layout.setSpacing(10)
        left_layout.setAlignment(Qt.AlignVCenter)

        # Main message - FONT LỚN HƠN
        main_label = QLabel(style_data["title"])
        main_label.setAlignment(Qt.AlignLeft)
        main_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 20px;  /* Tăng font size */
                font-weight: bold;
                background: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
                line-height: 1.2;
            }
        """)
        main_label.setFont(QFont("Segoe UI", 12, QFont.Bold))

        # Sub message - FONT LỚN HƠN
        sub_label = QLabel(style_data["subtitle"])
        sub_label.setAlignment(Qt.AlignLeft)
        sub_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.9);
                font-size: 14px;  /* Tăng font size */
                font-weight: 500;
                background: none;
                border: none;
                padding: 0px;
                margin: 0px;
            }
        """)
        sub_label.setMinimumHeight(25)

        # Thêm các widget vào layout trái
        left_layout.addWidget(main_label)
        left_layout.addWidget(sub_label)

        # === Phần icon bên phải - LỚN HƠN ===
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(80, 80)  # Tăng kích thước icon
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
            }
        """)
        
        # Load icon từ file - SỬ DỤNG ĐƯỜNG DẪN ẢNH
        icon_path = style_data["icon_path"]
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            # Scale pixmap để vừa với kích thước mới
            scaled_pixmap = pixmap.scaled(70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.icon_label.setPixmap(scaled_pixmap)
        else:
            # Fallback nếu file không tồn tại
            print(f"⚠️ Icon not found: {icon_path}")
            self.icon_label.setText("!")
            self.icon_label.setStyleSheet("""
                QLabel {
                    background: #E74C3C;
                    border-radius: 40px;
                    color: white;
                    font-size: 24px;
                    font-weight: bold;
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
        self.close_timer.start(3000)  # Hiển thị 3 giây
        
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

    def close_with_animation(self):
        """Hiệu ứng đóng mượt mà"""
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.setEasingCurve(QEasingCurve.InCubic)
        self.animation.finished.connect(self.close)
        self.animation.start()

class Client:
    def __init__(self):
        self.salt = os.urandom(16)
        self.password = 'ROSAComputer'

    def get_time_seconds(self):
        """Giả lập thời gian"""
        return "123456789"

    def generate_key(self, password, salt):
        """Giả lập key generation"""
        return b'simulated_key_32_bytes_long_1234'

    def encrypt_data(self, data):
        """Giả lập mã hóa - trả về dữ liệu giả"""
        simulated_nonce = b'simulated_nonce'
        simulated_encrypted = b'simulated_encrypted_data'
        combined = simulated_nonce + simulated_encrypted
        return base64.b64encode(combined).decode(), base64.b64encode(self.salt).decode()

    def get_key_and_sal(self):
        """Giả lập lấy key và salt"""
        guid = "045c0333-9682-4fa3-a464-b75927330f11"
        mbid = "230926374300040"
        seconds = self.get_time_seconds()

        combined = f"{guid}?{mbid}?{seconds}"
        encrypted_data, salt_b64 = self.encrypt_data(combined)
        return encrypted_data, salt_b64

class FanMonitor:
    def __init__(self, config_file: str = "fan_monitor_config.yaml", data_file: str = "fan_sensors.json"):
        self.config_file = config_file
        self.data_file = data_file
        self.previous_status = "000"
        self.current_status = "000"
        self.status_changes = []
        self.sensor_min_max_initialized = True
        self.last_sent_status = None
        self.qt_app = None
        self.iteration_count = 0
        self.monitoring_active = False

        self.server_url = "https://rosaai_server1.rosachatbot.com/error/send/email"
        self.polling_interval = 5
        
        # Dữ liệu giả lập
        self.simulated_fans = {
            "CPU Fan #1": {"min": 500, "max": 2500, "current": 1200},
            "GPU Fan #1": {"min": 800, "max": 3000, "current": 1500},
            "Case Fan #1": {"min": 400, "max": 2000, "current": 800}
        }
        
        # Load config
        self.config = self._load_config()
        self.sensor_min_max = {'fans': self.simulated_fans}
        
        # Tạo thư mục assets nếu chưa tồn tại
        self._create_assets_folder()
    
    def _create_assets_folder(self):
        """Tạo thư mục assets nếu chưa tồn tại"""
        assets_dir = Path("assets/icon")
        assets_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ Assets folder: {assets_dir}")
    
    def _load_config(self) -> Dict:
        """Load config từ file YAML"""
        config_path = Path(self.config_file)
        
        if not config_path.exists():
            sample_config = {
                'email': 'tranninh903@gmail.com',
                'company_name': 'Viet Son JSC',
                'machine_name': 'PC-01',
                'selected_fan': "CPU Fan #1",
                'polling_interval': 5
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(sample_config, f, default_flow_style=False, allow_unicode=True)
            
            print(f"✅ Created sample config file: {self.config_file}")
            return sample_config
        
        with open(self.config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        return config or {}
    
    def show_config_window(self):
        """Hiển thị cửa sổ cấu hình"""
        if self.qt_app is None:
            self.qt_app = QApplication([])
        
        self.config_window = ConfigWindow(self)
        self.config_window.show()
        
        return self.qt_app.exec_()
    
    def start_monitoring(self):
        """Bắt đầu giám sát sau khi cấu hình"""
        self.monitoring_active = True
        print("🚀 Starting SIMULATED Fan Monitor...")
        print("💡 This version uses simulated data for testing")
        print("🔄 Cycle: 3 normal → 2 error (repeating every 5 iterations)")
        print(f"⏰ Polling interval: {self.polling_interval} seconds")
        print("Press Ctrl+C to stop\n")
        
        # KHỞI TẠO MIN/MAX VỚI DỮ LIỆU GIẢ LẬP
        self.initialize_sensor_min_max()
        
        self.monitor_loop()
    
    def initialize_sensor_min_max(self):
        """Khởi tạo min/max với dữ liệu giả lập"""
        print("✅ Simulated fan sensors initialized:")
        for fan_name, fan_data in self.simulated_fans.items():
            print(f"   - {fan_name}: Min={fan_data['min']}, Max={fan_data['max']}, Current={fan_data['current']}")
    
    def get_fan_sensors(self) -> Dict:
        """Lấy tất cả sensor fan với dữ liệu giả lập"""
        fan_sensors = {
            'fans': [],
            'timestamp': datetime.now().isoformat()
        }
        
        for fan_name, fan_data in self.simulated_fans.items():
            sensor_data = {
                'name': fan_name,
                'type': "Fan",
                'value': fan_data['current'],
                'min': fan_data['min'],
                'max': fan_data['max'],
            }
            fan_sensors['fans'].append(sensor_data)
        
        return fan_sensors
    
    def export_sensors_to_json(self):
        """Xuất dữ liệu sensor ra file JSON"""
        sensors_data = self.get_fan_sensors()
        
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(sensors_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Fan sensor data exported to: {self.data_file}")
    
    def simulate_fan_behavior(self):
        """Giả lập hành vi của quạt - luân phiên giữa bình thường và lỗi"""
        self.iteration_count += 1
        selected_fan = self.config.get('selected_fan', 'CPU Fan #1')
        fan_data = self.simulated_fans[selected_fan]
        
        # Tạo chu kỳ: 3 lần bình thường, 2 lần lỗi (dựa trên iteration_count)
        cycle_position = self.iteration_count % 5
        
        if cycle_position < 3:
            # Trạng thái bình thường - RPM trong khoảng an toàn
            safe_min = fan_data['min'] + 100
            safe_max = fan_data['max'] - 100
            fan_data['current'] = random.randint(safe_min, safe_max)
            print(f"🔄 Cycle {self.iteration_count} (Position {cycle_position}): NORMAL - RPM between {safe_min}-{safe_max}")
        else:
            # Trạng thái lỗi
            error_type = random.choice(['high', 'low', 'zero'])
            if error_type == 'high':
                # RPM quá cao
                fan_data['current'] = random.randint(
                    int(fan_data['max'] + 100),
                    int(fan_data['max'] + 500)
                )
                print(f"🔄 Cycle {self.iteration_count} (Position {cycle_position}): ERROR HIGH - RPM above max")
            elif error_type == 'low':
                # RPM quá thấp
                fan_data['current'] = random.randint(
                    int(fan_data['min'] * 0.1),
                    int(fan_data['min'] - 50)
                )
                print(f"🔄 Cycle {self.iteration_count} (Position {cycle_position}): ERROR LOW - RPM below min")
            else:
                # RPM bằng 0
                fan_data['current'] = 0
                print(f"🔄 Cycle {self.iteration_count} (Position {cycle_position}): ERROR ZERO - RPM = 0")
        
        return fan_data['current']
    
    def get_current_fan_reading(self) -> Optional[float]:
        """Lấy tốc độ quạt hiện tại từ dữ liệu giả lập"""
        selected_fan_name = self.config.get('selected_fan', 'CPU Fan #1')
        
        if selected_fan_name in self.simulated_fans:
            # Cập nhật RPM giả lập
            current_rpm = self.simulate_fan_behavior()
            self.simulated_fans[selected_fan_name]['current'] = current_rpm
            return current_rpm
        
        return None
        
    def check_fan_status(self, fan_rpm: Optional[float]) -> str:
        """Kiểm tra và trả về mã trạng thái fan"""
        selected_fan_name = self.config.get('selected_fan', 'CPU Fan #1')
        
        # Kiểm tra nếu không lấy được giá trị fan
        if fan_rpm is None or fan_rpm == 0:
            print(f"❌ Fan error: No reading or RPM=0")
            return "001"
        
        # Lấy min/max cho quạt được chọn
        fan_ranges = self.simulated_fans.get(selected_fan_name, {})
        fan_min = fan_ranges.get('min', 500)
        fan_max = fan_ranges.get('max', 2500)
        
        # Kiểm tra quạt với min/max
        if fan_rpm <= fan_min:
            print(f"❌ Fan error: RPM {fan_rpm} <= min {fan_min}")
            return "001"
        
        if fan_rpm >= fan_max:
            print(f"❌ Fan error: RPM {fan_rpm} >= max {fan_max}")
            return "001"
        
        print(f"✅ Fan normal: RPM {fan_rpm} within range {fan_min}-{fan_max}")
        return "000"
    
    def show_popup(self, status):
        """Hiển thị popup thông báo"""
        if not self.monitoring_active:
            return
            
        # Khởi tạo QApplication nếu chưa có
        if self.qt_app is None:
            self.qt_app = QApplication.instance()
            if self.qt_app is None:
                self.qt_app = QApplication([])
        
        # Hiển thị popup dựa trên trạng thái
        if status == "000":
            print("🪟 Showing NORMAL popup")
            popup = PopupMessage("normal")
        elif status == "001":
            print("🪟 Showing ERROR popup")
            popup = PopupMessage("fan")
        
        # Xử lý sự kiện để popup hiển thị đúng
        QApplication.processEvents()
    
    def send_status_to_server(self, status_data: Dict):
        """Gửi trạng thái đến server khi có thay đổi QUAN TRỌNG"""
        try:
            # Chỉ gửi khi có sự thay đổi trạng thái
            old_status = status_data['old_status']
            new_status = status_data['new_status']
            
            # Nếu trạng thái mới giống lần gửi trước, không gửi lại
            if new_status == self.last_sent_status:
                print(f"🔄 Status unchanged, skipping send: {new_status}")
                return
            
            # Tạo client để lấy key và sal
            client = Client()
            key, sal = client.get_key_and_sal()
            
            # Chuẩn bị dữ liệu theo format API server
            error_list = []
            if new_status != "000":
                error_list.append(new_status)
            
            payload = {
                'key': key,  
                'sal': sal,  
                'email': self.config.get('email', 'tranninh903@gmail.com'),
                'company_name': self.config.get('company_name', 'Viet Son JSC'),
                'machine_name': self.config.get('machine_name', 'PC-01'),
                'error': error_list,
            }
            
            status_messages = {
                "000": "Normal",
                "001": "Fan Error"
            }
            
            print(f"📤 SENDING REQUEST TO SERVER:")
            print(f"   - Email: {payload['email']}")
            print(f"   - Company: {payload['company_name']}")
            print(f"   - Machine: {payload['machine_name']}")
            print(f"   - Status: {new_status} ({status_messages[new_status]})")
            print(f"   - Errors: {error_list}")
            print(f"   - Change: {status_messages[old_status]} → {status_messages[new_status]}")
            print(f"   - Fan Speed: {status_data['fan_speed']} RPM")
            
            # Gửi request thực tế đến server
            response = requests.post(
                self.server_url,
                data=payload,
                verify=False,
                timeout=20
            )
            
            if response.status_code == 200:
                print(f"✅ Request sent successfully! Status: {response.status_code}")
                self.last_sent_status = new_status
            else:
                print(f"❌ Server error: {response.status_code} - {response.text}")
                    
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to send to server: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    
    def log_status_change(self, old_status: str, new_status: str, fan_rpm: float):
        """Ghi lại sự thay đổi trạng thái và gửi đến server nếu cần"""
        if old_status != new_status:
            change_record = {
                'timestamp': datetime.now().isoformat(),
                'from_status': old_status,
                'to_status': new_status,
                'fan_speed': fan_rpm
            }
            self.status_changes.append(change_record)
            
            status_messages = {
                "000": "Normal",
                "001": "Fan Error"
            }
            
            print(f"🎯 STATUS CHANGED: {status_messages[old_status]} → {status_messages[new_status]}")
            print(f"   Fan Speed: {fan_rpm:.0f} RPM")
            print(f"   Total changes: {len(self.status_changes)}")
            
            # Hiển thị popup thông báo
            self.show_popup(new_status)
            
            # Gửi thông báo đến server cho mọi thay đổi
            server_data = {
                'timestamp': change_record['timestamp'],
                'old_status': old_status,
                'new_status': new_status,
                'old_status_text': status_messages[old_status],
                'new_status_text': status_messages[new_status],
                'fan_speed': fan_rpm,
                'selected_fan': self.config.get('selected_fan', 'CPU Fan #1')
            }
            self.send_status_to_server(server_data)
        else:
            # Vẫn hiển thị trạng thái hiện tại nhưng không gửi request
            status_messages = {
                "000": "Normal",
                "001": "Fan Error"
            }
            print(f"📊 Status maintained: {status_messages[new_status]} | Fan: {fan_rpm:.0f} RPM")
    
    def monitor_loop(self):
        """Vòng lặp giám sát chính"""
        try:
            while self.monitoring_active:
                fan_rpm = self.get_current_fan_reading()
                self.current_status = self.check_fan_status(fan_rpm)
                
                # Log thay đổi trạng thái
                self.log_status_change(self.previous_status, self.current_status, fan_rpm)
                
                self.previous_status = self.current_status
                time.sleep(self.polling_interval) 
                
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped.")
            print(f"📊 Total status changes: {len(self.status_changes)}")
            print(f"🔄 Total iterations: {self.iteration_count}")
    
    def get_status_history(self) -> List[Dict]:
        """Lấy lịch sử thay đổi trạng thái"""
        return self.status_changes


if __name__ == "__main__":
    monitor = FanMonitor()
    
    # Hiển thị cửa sổ cấu hình trước khi bắt đầu giám sát
    monitor.show_config_window()