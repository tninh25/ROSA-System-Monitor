import os
import pytz
import base64
import subprocess
import winreg as reg  

from datetime import datetime

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class Authentication:
    def __init__(self):
        self.salt = os.urandom(16)
        self.password = 'ROSAComputer'

    def get_osid(self):
        try:
            key = reg.OpenKey(reg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography", 0, reg.KEY_READ)
            machine_guid, _ = reg.QueryValueEx(key, "MachineGuid")
            reg.CloseKey(key)
            return machine_guid.strip()
        except Exception:
            return None

    def get_mbid(self):
        try:
            command = [
                "powershell",
                "-NoProfile",
                "-Command",
                "(Get-CimInstance Win32_BaseBoard).SerialNumber"
            ]
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            serial = result.stdout.strip()
            return serial if serial else None
        except Exception:
            return None
        
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
            iterations=100000
        )
        return kdf.derive(password.encode())

    def encrypt_data(self, data):
        key = self.generate_key(self.password, self.salt)
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)
        encrypted = aesgcm.encrypt(nonce, data.encode(), None)
        return base64.b64encode(nonce + encrypted).decode(), base64.b64encode(self.salt).decode()

    def get_key_and_salt(self):
        # osid = self.get_osid()
        # mbid = self.get_mbid()
        osid = "045c0333-9682-4fa3-a464-b75927330f11"
        mbid = "230926374300040"
        seconds = self.get_time_seconds()

        combined = f"{osid}?{mbid}?{seconds}"
        encrypted_data, salt_b64 = self.encrypt_data(combined)
        return encrypted_data, salt_b64