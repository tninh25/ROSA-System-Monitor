# backend/register.py
import json
import os
from datetime import datetime
import logging

class RegistrationManager:
    def __init__(self, config_dir="config"):
        self.config_dir = config_dir
        self.config_file = os.path.join(config_dir, "settings.json")
        self.setup_logging()
        self.ensure_config_dir()
    
    def setup_logging(self):
        """Thiết lập logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('registration.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def ensure_config_dir(self):
        """Đảm bảo thư mục config tồn tại"""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
            self.logger.info(f"Created config directory: {self.config_dir}")
    
    def validate_registration_data(self, company, machine, email):
        """Validate dữ liệu đăng ký"""
        errors = []
        
        if not company or len(company.strip()) < 2:
            errors.append("Tên công ty phải có ít nhất 2 ký tự")
        
        if not machine or len(machine.strip()) < 2:
            errors.append("Tên máy phải có ít nhất 2 ký tự")
        
        if not email or "@" not in email or "." not in email:
            errors.append("Email không hợp lệ")
        elif len(email) < 5:
            errors.append("Email quá ngắn")
        
        return errors
    
    def register_system(self, company, machine, email, **additional_info):
        """Đăng ký hệ thống và lưu thông tin vào file JSON"""
        try:
            # Validate dữ liệu
            errors = self.validate_registration_data(company, machine, email)
            if errors:
                return False, errors
            
            # Tạo dữ liệu đăng ký
            registration_data = {
                "registration": {
                    "company_name": company.strip(),
                    "machine_name": machine.strip(),
                    "email": email.strip(),
                    "registration_date": datetime.now().isoformat(),
                    "status": "activated",
                    "version": "1.0.0"
                },
                "system_info": {
                    **additional_info
                },
                "settings": {
                    "monitoring_enabled": True,
                    "alert_enabled": True,
                    "auto_start": False
                }
            }
            
            # Lưu vào file JSON
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(registration_data, f, ensure_ascii=False, indent=4)
            
            self.logger.info(f"System registered successfully: {company} - {machine}")
            return True, ["Đăng ký thành công!"]
            
        except Exception as e:
            error_msg = f"Lỗi khi đăng ký: {str(e)}"
            self.logger.error(error_msg)
            return False, [error_msg]
    
    def is_registered(self):
        """Kiểm tra xem hệ thống đã đăng ký chưa"""
        return os.path.exists(self.config_file)
    
    def get_registration_info(self):
        """Lấy thông tin đăng ký nếu có"""
        if not self.is_registered():
            return None
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error reading config file: {e}")
            return None
    
    def update_registration(self, **updates):
        """Cập nhật thông tin đăng ký"""
        try:
            current_data = self.get_registration_info()
            if not current_data:
                return False, "Hệ thống chưa được đăng ký"
            
            # Cập nhật thông tin
            for key, value in updates.items():
                if key in current_data.get("registration", {}):
                    current_data["registration"][key] = value
                elif key in current_data.get("settings", {}):
                    current_data["settings"][key] = value
                else:
                    current_data["system_info"][key] = value
            
            # Lưu file
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(current_data, f, ensure_ascii=False, indent=4)
            
            self.logger.info("Registration updated successfully")
            return True, "Cập nhật thành công"
            
        except Exception as e:
            error_msg = f"Lỗi khi cập nhật: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def delete_registration(self):
        """Xóa thông tin đăng ký"""
        try:
            if os.path.exists(self.config_file):
                os.remove(self.config_file)
                self.logger.info("Registration deleted successfully")
                return True, "Đã xóa thông tin đăng ký"
            return False, "Không tìm thấy file đăng ký"
        except Exception as e:
            error_msg = f"Lỗi khi xóa đăng ký: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg