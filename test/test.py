import sys
import wmi
import json
import pythoncom
import requests
import time
import os
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime

# PyQt5 imports
from PyQt5.QtWidgets import (QApplication, QSystemTrayIcon, QMenu, QAction, 
                           QMessageBox, QWidget, QVBoxLayout, QLabel, 
                           QDialog, QTextEdit, QPushButton, QHBoxLayout)
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt

class MonitorThread(QThread):
    """Thread để chạy monitoring độc lập"""
    status_update = pyqtSignal(str, str, float)  # old_status, new_status, fan_rpm
    error_signal = pyqtSignal(str)
    
    def __init__(self, monitor):
        super().__init__()
        self.monitor = monitor
        self.running = True
        
    def run(self):
        """Chạy vòng lặp monitoring"""
        try:
            self.monitor.initialize_sensor_min_max()
            time.sleep(1)
            
            while self.running:
                try:
                    fan_rpm = self.monitor.get_current_fan_reading()
                    
                    if self.monitor.sensor_min_max_initialized:
                        self.monitor.current_status = self.monitor.check_fan_status(fan_rpm)
                    else:
                        self.monitor.current_status = "000"
                    
                    # Phát tín hiệu khi có thay đổi trạng thái
                    if self.monitor.current_status != self.monitor.previous_status:
                        self.status_update.emit(
                            self.monitor.previous_status, 
                            self.monitor.current_status, 
                            fan_rpm or 0
                        )
                        self.monitor.log_status_change(
                            self.monitor.previous_status, 
                            self.monitor.current_status, 
                            fan_rpm or 0
                        )
                    
                    self.monitor.previous_status = self.monitor.current_status
                    time.sleep(self.monitor.polling_interval)
                    
                except Exception as e:
                    self.error_signal.emit(f"Monitoring error: {e}")
                    time.sleep(5)
                    
        except Exception as e:
            self.error_signal.emit(f"Thread error: {e}")
    
    def stop(self):
        """Dừng thread"""
        self.running = False
        self.wait()

class StatusDialog(QDialog):
    """Dialog hiển thị trạng thái chi tiết"""
    def __init__(self, monitor, parent=None):
        super().__init__(parent)
        self.monitor = monitor
        self.setWindowTitle("Fan Monitor Status")
        self.setFixedSize(400, 300)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Fan Monitor Status")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Current status
        self.status_label = QLabel("Status: Checking...")
        layout.addWidget(self.status_label)
        
        # Fan RPM
        self.rpm_label = QLabel("Fan RPM: --")
        layout.addWidget(self.rpm_label)
        
        # Log area
        log_label = QLabel("Recent Changes:")
        layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_status)
        button_layout.addWidget(refresh_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # Timer để cập nhật real-time
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(2000)  # Update every 2 seconds
        
    def update_display(self):
        """Cập nhật hiển thị"""
        try:
            fan_rpm = self.monitor.get_current_fan_reading()
            status = self.monitor.check_fan_status(fan_rpm)
            
            status_messages = {"000": "Normal", "001": "Fan Error"}
            status_text = status_messages.get(status, "Unknown")
            
            # Update status với màu sắc
            if status == "000":
                self.status_label.setText(f"Status: <font color='green'>{status_text}</font>")
            else:
                self.status_label.setText(f"Status: <font color='red'>{status_text}</font>")
            
            self.rpm_label.setText(f"Fan RPM: {fan_rpm or 'N/A'}")
            
            # Update log
            self.update_log()
            
        except Exception as e:
            self.status_label.setText(f"Status: <font color='orange'>Error: {str(e)}</font>")
    
    def update_log(self):
        """Cập nhật log"""
        log_content = ""
        for change in self.monitor.status_changes[-10:]:  # Last 10 entries
            timestamp = change['timestamp'][11:19]  # Just time
            old_status = "Normal" if change['from_status'] == "000" else "Error"
            new_status = "Normal" if change['to_status'] == "000" else "Error"
            log_content += f"{timestamp}: {old_status} → {new_status} (RPM: {change['fan_speed']})\n"
        
        self.log_text.setText(log_content)
    
    def refresh_status(self):
        """Refresh status manually"""
        self.update_display()

class FanMonitorApp(QWidget):
    """Ứng dụng chính với system tray"""
    
    def __init__(self):
        super().__init__()
        self.monitor = FanMonitor()
        self.monitor_thread = None
        
        # Tạo system tray
        self.setup_tray_icon()
        
        # Ẩn cửa sổ chính
        self.setWindowTitle("Fan Monitor")
        self.resize(1, 1)
        self.move(-1000, -1000)  # Move off-screen
        
        # Status dialog
        self.status_dialog = None
        
        # Start monitoring
        self.start_monitoring()
        
    def create_icon(self, color):
        """Tạo icon động với màu sắc"""
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(color))
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
        self.tray_icon.setIcon(self.create_icon('green'))
        
        # Tạo context menu
        tray_menu = QMenu()
        
        # Show Status action
        status_action = QAction("Show Status", self)
        status_action.triggered.connect(self.show_status)
        tray_menu.addAction(status_action)
        
        tray_menu.addSeparator()
        
        # Start/Stop actions
        self.start_action = QAction("Start Monitoring", self)
        self.start_action.triggered.connect(self.start_monitoring)
        tray_menu.addAction(self.start_action)
        
        self.stop_action = QAction("Stop Monitoring", self)
        self.stop_action.triggered.connect(self.stop_monitoring)
        self.stop_action.setEnabled(False)
        tray_menu.addAction(self.stop_action)
        
        tray_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()
        
        # Hiển thị thông báo khởi động
        self.tray_icon.showMessage(
            "Fan Monitor", 
            "Application started and running in background",
            QSystemTrayIcon.Information, 
            2000
        )
    
    def tray_icon_activated(self, reason):
        """Xử lý click vào tray icon"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_status()
    
    def start_monitoring(self):
        """Bắt đầu monitoring"""
        if self.monitor_thread and self.monitor_thread.isRunning():
            return
            
        self.monitor_thread = MonitorThread(self.monitor)
        self.monitor_thread.status_update.connect(self.handle_status_update)
        self.monitor_thread.error_signal.connect(self.handle_error)
        self.monitor_thread.start()
        
        self.start_action.setEnabled(False)
        self.stop_action.setEnabled(True)
        
        self.tray_icon.setIcon(self.create_icon('blue'))
        self.tray_icon.setToolTip("Fan Monitor - Running")
    
    def stop_monitoring(self):
        """Dừng monitoring"""
        if self.monitor_thread:
            self.monitor_thread.stop()
            self.monitor_thread = None
        
        self.start_action.setEnabled(True)
        self.stop_action.setEnabled(False)
        
        self.tray_icon.setIcon(self.create_icon('gray'))
        self.tray_icon.setToolTip("Fan Monitor - Stopped")
    
    def handle_status_update(self, old_status, new_status, fan_rpm):
        """Xử lý cập nhật trạng thái"""
        status_messages = {"000": "Normal", "001": "Fan Error"}
        old_msg = status_messages.get(old_status, "Unknown")
        new_msg = status_messages.get(new_status, "Unknown")
        
        # Đổi màu icon dựa trên trạng thái
        if new_status == "001":
            self.tray_icon.setIcon(self.create_icon('red'))
            # Hiển thị cảnh báo
            self.tray_icon.showMessage(
                "Fan Alert!",
                f"Fan status changed: {old_msg} → {new_msg}\nRPM: {fan_rpm}",
                QSystemTrayIcon.Warning,
                5000
            )
        else:
            self.tray_icon.setIcon(self.create_icon('green'))
    
    def handle_error(self, error_msg):
        """Xử lý lỗi"""
        self.tray_icon.setIcon(self.create_icon('orange'))
        print(f"Error: {error_msg}")
    
    def show_status(self):
        """Hiển thị dialog trạng thái"""
        if not self.status_dialog:
            self.status_dialog = StatusDialog(self.monitor, self)
        
        self.status_dialog.show()
        self.status_dialog.raise_()
        self.status_dialog.activateWindow()
    
    def quit_application(self):
        """Thoát ứng dụng"""
        reply = QMessageBox.question(
            self, 
            "Confirm Exit",
            "Are you sure you want to exit Fan Monitor?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.stop_monitoring()
            QApplication.quit()

class FanMonitor:
    def __init__(self, config_file: str = "config/settings.json"):
        self.config_file = config_file
        self.selected_fan_name = "Fan #1"
        
        # Lưu trạng thái
        self.previous_status = "000"
        self.current_status = "000"
        self.last_sent_status = "000"
        self.status_changes = []
        
        # Sensor
        self.sensor_min_max_initialized = False
        
        self.server_url = "https://rosaai_server1.rosachatbot.com/error/send/email"
        self.polling_interval = 2
        
        # Khởi tạo WMI
        pythoncom.CoInitialize()
        self.wmi_connection = wmi.WMI(namespace="root\\LibreHardwareMonitor")
        
        # Load config
        self.config = self._load_config()
        self.sensor_min_max = {'fans': {}}

    def _load_config(self) -> Dict:
        """Load config từ file settings.json"""
        try:
            config_path = Path(self.config_file)
            if not config_path.exists():
                raise FileNotFoundError(f"Config file not found: {self.config_file}")
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Validate required fields
            required_fields = ['company_name', 'machine_name', 'email']
            registration = config.get('registration', {})
            
            for field in required_fields:
                if field not in registration:
                    raise ValueError(f"Missing required field in config: {field}")
            
            print("Config loaded successfully")
            return config
        except Exception as e:
            print(f"Error loading config: {e}")
            return {
                'registration': {
                    'company_name': 'Unknown',
                    'machine_name': 'Unknown', 
                    'email': 'unknown@example.com'
                }
            }

    def initialize_sensor_min_max(self):
        """Khởi tạo min/max chỉ MỘT LẦN"""
        if not self.sensor_min_max_initialized:
            try:
                sensors = self.wmi_connection.Sensor()
                fan_count = 0

                for sensor in sensors:
                    if not hasattr(sensor, 'Parent') or not hasattr(sensor, 'SensorType'):
                        continue

                    sensor_type = sensor.SensorType

                    if sensor_type == "Fan":
                        fan_count += 1
                        if sensor.Name not in self.sensor_min_max['fans']:
                            self.sensor_min_max['fans'][sensor.Name] = {
                                'min': float(sensor.Min) if sensor.Min is not None else 0,
                                'max': float(sensor.Max) if sensor.Max is not None else 5000
                            }
                            print(f"Initialized fan: {sensor.Name} (Min: {sensor.Min}, Max: {sensor.Max})")
                
                if fan_count == 0:
                    print("Warning: No fan sensors found!")
                else:
                    print(f"Found {fan_count} fan sensors")
                    
                self.sensor_min_max_initialized = True
            except Exception as e:
                print(f"Error initializing sensor min/max: {e}")

    def get_fan_sensors(self) -> Dict:
        """Lấy tất cả sensor fan"""
        try:
            sensors = self.wmi_connection.Sensor()
            fan_sensors = {
                'fans': [],
                'timestamp': datetime.now().isoformat()
            }

            for sensor in sensors:
                if not hasattr(sensor, 'SensorType'):
                    continue

                sensor_type = sensor.SensorType
                
                if sensor_type == "Fan":
                    sensor_data = {
                        'name': sensor.Name,
                        'type': sensor_type,
                        'value': float(sensor.Value) if sensor.Value is not None else 0,
                        'min': float(sensor.Min) if sensor.Min is not None else 0,
                        'max': float(sensor.Max) if sensor.Max is not None else 5000,
                    }
                    fan_sensors['fans'].append(sensor_data)
            
            return fan_sensors
        except Exception as e:
            print(f"Error getting fan sensors: {e}")
            return {'fans': [], 'timestamp': datetime.now().isoformat()}

    def get_current_fan_reading(self) -> Optional[float]:
        """Lấy tốc độ quạt hiện tại"""
        try:
            sensors = self.get_fan_sensors()

            for fan in sensors['fans']:
                if fan['name'] == self.selected_fan_name and fan['value'] is not None:
                    return fan['value']
            
            # Fallback: Lấy fan đầu tiên có RPM > 0
            for fan in sensors['fans']:
                if fan['value'] is not None and fan['value'] > 0:
                    print(f"Using fallback fan: {fan['name']} = {fan['value']} RPM")
                    return fan['value']
            
            return 0.0
        except Exception as e:
            print(f"Error getting fan reading: {e}")
            return 0.0

    def check_fan_status(self, fan_rpm: Optional[float]) -> str:
        """Kiểm tra và trả về mã trạng thái fan"""
        if fan_rpm is None:
            return "001"
        
        if not self.sensor_min_max_initialized:
            return "000"
        
        fan_ranges = self.sensor_min_max['fans'].get(self.selected_fan_name, {})
        fan_min = fan_ranges.get('min', 0)
        fan_max = fan_ranges.get('max', 5000)

        # SỬA LOGIC: Chỉ báo lỗi khi ngoài ngưỡng
        if fan_rpm < fan_min or fan_rpm > fan_max:
            return "001"

        return "000"

    def send_status_to_server(self, status_data: Dict):
        """Gửi trạng thái đến server khi có sự thay đổi"""
        try:
            new_status = status_data['new_status']

            if new_status == self.last_sent_status:
                return 
            
            from backend.authentication import Authentication
            authentication = Authentication()
            key, salt = authentication.get_key_and_salt()

            error_list = [new_status]
            
            registration = self.config.get('registration', {})
            
            payload = {
                'key': key,
                'sal': salt,
                'email': registration.get('email', ''),
                'company_name': registration.get('company_name', ''),
                'machine_name': registration.get('machine_name', ''),
                'error': error_list
            }

            print(f"Sending payload: {payload}") 

            response = requests.post(
                self.server_url,
                data=payload,
                verify=False,
                timeout=20
            )
            
            if response.status_code == 200:
                self.last_sent_status = new_status
                print(f"Status {new_status} sent successfully")
            else:
                print(f"Server error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Failed to send to server: {e}")
    
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
            
            print(f"STATUS CHANGED: {status_messages[old_status]} → {status_messages[new_status]}")
            
            server_data = {
                'timestamp': change_record['timestamp'],
                'old_status': old_status,
                'new_status': new_status,
                'fan_speed': fan_rpm,
            }
            self.send_status_to_server(server_data)

def main():
    # Ẩn console window trên Windows
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Không thoát khi đóng cửa sổ
    
    # Tạo và hiển thị ứng dụng
    fan_app = FanMonitorApp()
    
    print("Fan Monitor is running in background. Check system tray.")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()