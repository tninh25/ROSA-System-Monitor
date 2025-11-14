import wmi
import json
import pythoncom
import requests
import time

from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime

class FanMonitor:
    def __init__(self, config_file: str = "config/settings.json", state_file: str = "last_state.json"):
        self.config_file = config_file
        self.state_file = state_file

        # Tên quạt
        self.selected_fan_name = "CPU Fan #1"

        # Lưu trạng thái
        self.previous_status = "000"
        self.current_status  = "000"
        self.last_sent_status = "000"
        self.status_changes = []

        # Sensor
        self.sensor_min_max_initialized = False

        self.server_url = "https://rosaai_server1.rosachatbot.com/error/send/email"
        self.polling_interval = 2  # Đọc mỗi 2 giây
        
        # Thêm: Bộ đếm để theo dõi trạng thái liên tục
        self.consecutive_low_count = 0   # Đếm số lần rpm < min liên tiếp
        self.consecutive_high_count = 0  # Đếm số lần rpm > max liên tiếp
        self.consecutive_error_count = 0 # Đếm số lần không đọc được sensor
        
        # Thêm: Ngưỡng thời gian (tính theo số lần đọc)
        self.low_rpm_threshold = 15   # 30 giây liên tục
        self.high_rpm_threshold = 10  # 20 giây liên tục
        self.sensor_error_threshold = 3

        # KHÔNG khởi tạo WMI ở đây - sẽ khởi tạo trong thread
        self.wmi_connection = None
        
        # Load config
        self.config = self._load_config()
        self.sensor_min_max = {'fans': {}}
        
        # Thêm: Load trạng thái cuối từ file
        self._load_last_state()

    def initialize_wmi(self):
        """Khởi tạo WMI connection - gọi trong worker thread"""
        if self.wmi_connection is None:
            try:
                pythoncom.CoInitialize()
                self.wmi_connection = wmi.WMI(namespace="root\\LibreHardwareMonitor")
            except Exception as e:
                raise

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
            
            return config
        except Exception as e:
            # Fallback config để chương trình không crash
            return {
                'registration': {
                    'company_name': 'Unknown',
                    'machine_name': 'Unknown', 
                    'email': 'unknown@example.com'
                }
            }

    def _load_last_state(self):
        """Load trạng thái cuối cùng từ file JSON"""
        try:
            state_path = Path(self.state_file)
            if state_path.exists():
                with open(state_path, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                
                self.last_sent_status = state.get('status', '000')
                last_rpm = state.get('rpm', 0)
                last_time = state.get('timestamp', 'Unknown')
                
                print(f"[RESTORE] Last state: {self.last_sent_status} @ {last_rpm} RPM (Time: {last_time})")
            else:
                print(f"[INFO] No previous state file found. Starting fresh with status 000.")
        except Exception as e:
            print(f"[WARNING] Failed to load last state: {e}. Starting with default state 000.")
            self.last_sent_status = "000"

    def _save_last_state(self, status: str, rpm: float):
        """Lưu trạng thái hiện tại vào file JSON"""
        try:
            state = {
                'timestamp': datetime.now().isoformat(),
                'status': status,
                'rpm': rpm
            }
            
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
            
            print(f"[SAVE] Updated state to {status} @ {rpm} RPM")
        except Exception as e:
            print(f"[ERROR] Failed to save state: {e}")

    def initialize_sensor_min_max(self):
        """Khởi tạo min/max chỉ MỘT LẦN"""
        if not self.sensor_min_max_initialized:
            if self.wmi_connection is None:
                self.initialize_wmi()
                
            try:
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
                            print(f"✅ Initialized fan: {sensor.Name} (Min: {sensor.Min}, Max: {sensor.Max})")
                
                self.sensor_min_max_initialized = True
                print("✅ Sensor min/max initialization completed")
                
            except Exception as e:
                print(f"❌ Error initializing sensor min/max: {e}")
    
    def get_fan_sensors(self) -> Dict:
        """Lấy tất cả sensor fan"""
        if self.wmi_connection is None:
            self.initialize_wmi()
        
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
                        'value': float(sensor.Value) if sensor.Value is not None else None,
                        'min': float(sensor.Min) if sensor.Min is not None else None,
                        'max': float(sensor.Max) if sensor.Max is not None else None,
                    }
                    fan_sensors['fans'].append(sensor_data)
            
            return fan_sensors
        except Exception as e:
            print(f"❌ Error getting fan sensors: {e}")
            return {'fans': [], 'timestamp': datetime.now().isoformat()}
    
    def get_current_fan_reading(self) -> Optional[float]:
        """Lấy tốc độ quạt hiện tại"""
        sensors = self.get_fan_sensors()

        for fan in sensors['fans']:
            if fan['name'] == self.selected_fan_name and fan['value'] is not None:
                return fan['value']
        
        # Fallback: Lấy fan đầu tiên có RPM > 0
        for fan in sensors['fans']:
            if fan['value'] is not None and fan['value'] > 0:
                print(f"Using fallback fan: {fan['name']} = {fan['value']} RPM")
                return fan['value']
        
        return None
        
    def check_fan_status(self, fan_rpm: Optional[float]) -> str: 
        """
        Kiểm tra và trả về mã trạng thái
        Returns: status_code
        """
        # Kiểm tra nếu không lấy được giá trị fan
        if fan_rpm is None:
            self.consecutive_error_count += 1
            
            # Nếu lỗi liên tục >= 3 lần
            if self.consecutive_error_count >= self.sensor_error_threshold:
                return "001"  # Quạt không hoạt động
            else:
                return self.current_status
        
        # Reset bộ đếm lỗi nếu đọc được RPM
        self.consecutive_error_count = 0
        
        # Kiểm tra nếu chưa khởi tạo min/max
        if not self.sensor_min_max_initialized:
            return "000"
        
        # Lấy min/max cho quạt được chọn
        fan_ranges = self.sensor_min_max['fans'].get(self.selected_fan_name, {})
        fan_min = fan_ranges.get('min')
        fan_max = fan_ranges.get('max')

        # Nếu không có min/max, không thể đánh giá
        if fan_min is None or fan_max is None:
            return "000"
        
        # Kiểm tra RPM = 0 → Quạt dừng hoặc mất kết nối
        if fan_rpm == 0:
            self.consecutive_low_count = 0
            self.consecutive_high_count = 0
            return "001"  # Quạt không hoạt động
        
        # Kiểm tra RPM < min → Quạt yếu
        if fan_rpm < fan_min:
            self.consecutive_low_count += 1
            self.consecutive_high_count = 0
            
            if self.consecutive_low_count >= self.low_rpm_threshold:
                return "002"  # Quạt quay chậm
            else:
                return self.current_status
        
        # Kiểm tra RPM > max → Quạt quay quá nhanh
        elif fan_rpm > (fan_max + 100):
            self.consecutive_high_count += 1
            self.consecutive_low_count = 0
            
            if self.consecutive_high_count >= self.high_rpm_threshold:
                return "003"  # Quạt quay quá nhanh
            else:
                return self.current_status
        
        # RPM nằm trong khoảng bình thường
        else:
            self.consecutive_low_count = 0
            self.consecutive_high_count = 0
            return "000"  # Bình thường
    
    def send_status_to_server(self, status_data: Dict):
        """Gửi trạng thái đến server khi có sự thay đổi"""
        try:
            new_status = status_data['new_status']

            # Nếu trạng thái mới giống lần gửi trước → không gửi lại
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

            print(f"[SEND] Sending payload: {payload}") 

            response = requests.post(
                self.server_url,
                data=payload,
                verify=False,
                timeout=20
            )
            
            if response.status_code == 200:
                self.last_sent_status = new_status
                print(f"[SUCCESS] Status {new_status} sent successfully")
            else:
                print(f"[ERROR] Server error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"[ERROR] Failed to send to server: {e}")
    
    def log_status_change(self, old_status: str, new_status: str, fan_rpm: float):
        """Ghi lại sự thay đổi trạng thái"""
        if old_status != new_status:
            change_record = {
                'timestamp': datetime.now().isoformat(),
                'from_status': old_status,
                'to_status': new_status,
                'fan_speed': fan_rpm
            }
            self.status_changes.append(change_record)
            
            status_names = {
                "000": "Normal",
                "001": "Fan Stopped", 
                "002": "Fan Slow",
                "003": "Fan Fast"
            }
            
            print(f"[ALERT] Status changed: {status_names[old_status]} → {status_names[new_status]} | RPM: {fan_rpm}")
            
            # Lưu trạng thái vào file
            self._save_last_state(new_status, fan_rpm)
            
            # Gửi thông báo đến server
            server_data = {
                'timestamp': change_record['timestamp'],
                'old_status': old_status,
                'new_status': new_status,
                'fan_speed': fan_rpm,
            }
            self.send_status_to_server(server_data)
        else:
            # Không có thay đổi, chỉ log đơn giản
            if new_status == "000":
                print(f"[INFO] RPM: {fan_rpm} (Normal)")
            else:
                status_names = {
                    "001": "Fan Stopped", 
                    "002": "Fan Slow",
                    "003": "Fan Fast"
                }
                print(f"[MONITORING] {status_names[new_status]} ({fan_rpm} RPM) - Status unchanged")

    def monitor_loop(self):
        """Vòng lặp giám sát"""
        self.initialize_sensor_min_max()
        time.sleep(1)
        
        try:
            while True:
                fan_rpm = self.get_current_fan_reading()

                # Chỉ kiểm tra status sau khi đã khởi tạo min/max
                if self.sensor_min_max_initialized:
                    self.current_status = self.check_fan_status(fan_rpm)  # CHỈ LẤY STATUS
                else:
                    self.current_status = "000"

                self.log_status_change(
                    self.previous_status, 
                    self.current_status, 
                    fan_rpm if fan_rpm is not None else 0
                )

                self.previous_status = self.current_status
                
                time.sleep(self.polling_interval)
        except KeyboardInterrupt:
            print("\n[INFO] Monitoring stopped by user.")

    def cleanup(self):
        """Dọn dẹp resources"""
        try:
            pythoncom.CoUninitialize()
        except Exception as e:
            print(f"Cleanup error: {e}")

if __name__ == "__main__":
    monitor = FanMonitor()
    monitor.monitor_loop()