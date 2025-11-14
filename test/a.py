import pythoncom
import wmi
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
import subprocess
import pytz
import winreg as reg
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class Client:
    def __init__(self):
        self.salt = os.urandom(16)
        self.password = 'ROSAComputer'

    def get_time_seconds(self):
        HCM_tz = pytz.timezone('Asia/Ho_Chi_Minh')
        current_time = datetime.now(HCM_tz)
        specific_date = datetime(2024, 10, 10, tzinfo=HCM_tz)
        delta = current_time - specific_date
        return str(int(delta.total_seconds()))

    def generate_key(self, password, salt):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return kdf.derive(password.encode())

    def encrypt_data(self, data):
        key = self.generate_key(self.password, self.salt)
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)
        encrypted = aesgcm.encrypt(nonce, data.encode(), None)
        return base64.b64encode(nonce + encrypted).decode(), base64.b64encode(self.salt).decode()

    def get_key_and_sal(self):
        # Sử dụng GUID và MBID cố định như yêu cầu
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
        self.sensor_min_max_initialized = False
        self.last_sent_status = "000"  # ✅ FIX: Khởi tạo = "000" thay vì None để tránh gửi lần đầu

        self.server_url = "https://rosaai_server1.rosachatbot.com/error/send/email"
        self.polling_interval = 2
        
        # Khởi tạo WMI
        pythoncom.CoInitialize()
        self.wmi_connection = wmi.WMI(namespace="root\\LibreHardwareMonitor")
        
        # Load config
        self.config = self._load_config()
        self.sensor_min_max = {'fans': {}}
    
    def _load_config(self) -> Dict:
        """Load config từ file YAML"""
        config_path = Path(self.config_file)
        
        if not config_path.exists():
            sample_config = {
                'selected_fan': "CPU Fan #1",
                'polling_interval': 2
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(sample_config, f, default_flow_style=False, allow_unicode=True)
            
            print(f"Created sample config file: {self.config_file}")
            return sample_config
        
        with open(self.config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        if 'selected_fan' in config and isinstance(config['selected_fan'], str):
            config['selected_fan'] = config['selected_fan'].strip('"\'')
        
        return config
    
    def initialize_sensor_min_max(self):
        """Khởi tạo min/max chỉ MỘT LẦN duy nhất"""
        if not self.sensor_min_max_initialized:
            sensors = self.wmi_connection.Sensor()
            
            for sensor in sensors:
                if not hasattr(sensor, 'Parent') or not hasattr(sensor, 'SensorType'):
                    continue
                    
                sensor_type = sensor.SensorType
                
                # Chỉ lấy thông tin fan
                if sensor_type == "Fan":
                    if sensor.Name not in self.sensor_min_max['fans']:
                        self.sensor_min_max['fans'][sensor.Name] = {
                            'min': float(sensor.Min) if sensor.Min is not None else None,
                            'max': float(sensor.Max) if sensor.Max is not None else None
                        }
                        print(f"✓ Initialized fan: {sensor.Name} (Min: {sensor.Min}, Max: {sensor.Max})")
            
            self.sensor_min_max_initialized = True
            print("✓ Fan sensor min/max initialized")
    
    def get_fan_sensors(self) -> Dict:
        """Lấy tất cả sensor fan"""
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
                    'value': float(sensor.Value) if sensor.Value is not None else None,
                    'min': float(sensor.Min) if sensor.Min is not None else None,
                    'max': float(sensor.Max) if sensor.Max is not None else None,
                }
                fan_sensors['fans'].append(sensor_data)
        
        return fan_sensors
    
    def export_sensors_to_json(self):
        """Xuất dữ liệu sensor ra file JSON"""
        sensors_data = self.get_fan_sensors()
        
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(sensors_data, f, indent=2, ensure_ascii=False)
        
        print(f"Fan sensor data exported to: {self.data_file}")
        
        # Hiển thị thông tin fans
        print("\n=== FAN SENSORS ===")
        for fan in sensors_data['fans']:
            print(f"  - {fan['name']}: {fan['value']} RPM (Min: {fan['min']}, Max: {fan['max']})")
        
        print(f"Selected fan: {self.config.get('selected_fan', 'CPU Fan #1')}")
    
    def get_current_fan_reading(self) -> Optional[float]:
        """Lấy tốc độ quạt hiện tại"""
        sensors = self.get_fan_sensors()
        
        # Lấy tốc độ quạt theo config
        selected_fan_name = self.config.get('selected_fan', 'CPU Fan #1')
        
        for fan in sensors['fans']:
            if fan['name'] == selected_fan_name and fan['value'] is not None:
                return fan['value']
        
        # Fallback: lấy fan đầu tiên có RPM > 0
        for fan in sensors['fans']:
            if fan['value'] is not None and fan['value'] > 0:
                print(f"Using fallback fan: {fan['name']} = {fan['value']} RPM")
                return fan['value']
        
        return None
        
    def check_fan_status(self, fan_rpm: Optional[float]) -> str:
        """Kiểm tra và trả về mã trạng thái fan"""
        selected_fan_name = self.config.get('selected_fan', 'CPU Fan #1')
        
        # Kiểm tra nếu không lấy được giá trị fan
        if fan_rpm is None:
            return "001"
        
        # Kiểm tra nếu chưa khởi tạo min/max
        if not self.sensor_min_max_initialized:
            return "000"  # Chưa có dữ liệu để so sánh
        
        # Lấy min/max cho quạt được chọn
        fan_ranges = self.sensor_min_max['fans'].get(selected_fan_name, {})
        fan_min = fan_ranges.get('min')
        fan_max = fan_ranges.get('max')
        
        # Nếu không có min/max, không thể đánh giá
        if fan_min is None or fan_max is None:
            return "000"
        
        # Kiểm tra quạt với min/max
        if fan_rpm <= fan_min:
            return "001"
        
        if fan_rpm >= fan_max:
            return "001"
        
        return "000"
    
    def send_status_to_server(self, status_data: Dict):
        """Gửi trạng thái đến server khi có thay đổi QUAN TRỌNG"""
        try:
            # Chỉ gửi khi có sự thay đổi trạng thái
            old_status = status_data['old_status']
            new_status = status_data['new_status']
            
            # Nếu trạng thái mới giống lần gửi trước, không gửi lại
            if new_status == self.last_sent_status:
                return
            
            # Tạo client để lấy key và sal
            client = Client()
            key, sal = client.get_key_and_sal()
            
            # ✅ FIX: Luôn gửi status code hiện tại trong error list
            error_list = [new_status]
            
            payload = {
                'key': key,  
                'sal': sal,  
                'email': 'tranninh903@gmail.com',
                'company_name': 'Viet Son JSC',
                'machine_name': 'PC-01',
                'error': error_list,
            }
            
            status_messages = {
                "000": "Normal",
                "001": "Fan Error"
            }
            
            print(f"SENDING REQUEST:")
            print(f"   - Status: {new_status} ({status_messages[new_status]})")
            print(f"   - Errors: {error_list}")
            print(f"   - Change: {status_messages[old_status]} → {status_messages[new_status]}")
            
            response = requests.post(
                self.server_url,
                data=payload,
                verify=False,
                timeout=20
            )
            
            if response.status_code == 200:
                print(f"Request sent successfully!")
                self.last_sent_status = new_status  # Cập nhật trạng thái đã gửi
            else:
                print(f"Server error: {response.status_code} - {response.text}")
                    
        except requests.exceptions.RequestException as e:
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
            
            # Gửi thông báo đến server cho mọi thay đổi (bao gồm 001→000)
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
    
    def monitor_loop(self):
        """Vòng lặp giám sát chính"""
        print("Starting Fan Monitor...")
        
        # KHỞI TẠO MIN/MAX CHỈ MỘT LẦN DUY NHẤT
        self.initialize_sensor_min_max()
        
        # Đợi một chút để đảm bảo đã có dữ liệu min/max
        time.sleep(1)
        
        try:
            while True:
                fan_rpm = self.get_current_fan_reading()
                
                # Chỉ kiểm tra status sau khi đã khởi tạo min/max
                if self.sensor_min_max_initialized:
                    self.current_status = self.check_fan_status(fan_rpm)
                else:
                    self.current_status = "000"  # Tạm thời coi là normal
                
                # Log thay đổi trạng thái
                self.log_status_change(self.previous_status, self.current_status, fan_rpm)
                
                # Hiển thị trạng thái hiện tại (in ít hơn)
                status_text = {
                    "000": "NORMAL",
                    "001": "FAN ERROR"
                }
                
                display_status = status_text.get(self.current_status, "UNKNOWN")
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {display_status} | Fan: {fan_rpm or 0:.0f} RPM")
                
                self.previous_status = self.current_status
                time.sleep(self.polling_interval) 
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped.")
    
    def get_status_history(self) -> List[Dict]:
        """Lấy lịch sử thay đổi trạng thái"""
        return self.status_changes


if __name__ == "__main__":
    monitor = FanMonitor()
    
    monitor.export_sensors_to_json()
    
    monitor.monitor_loop()