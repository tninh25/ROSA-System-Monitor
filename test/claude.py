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
        self.state_file  = state_file

        # Ten quat
        self.selected_fan_name = "Fan #1"

        # Luu trang thai
        self.previous_status = "000"
        self.current_status  = "000"
        self.last_sent_status= "000"

        # Bien luu status text
        self.current_status_text = "Normal"
        self.last_sent_status_text = "Normal"

        # Sensor
        self.sensor_min_max_initialized = False

        # Server
        self.server_url = "https://rosaai_server1.rosachatbot.com/error/send/email"
        self.polling_interval = 2

        # Bo dem de theo doi trang thai lien tuc
        self.consecutive_low_count = 0              # So lan rpm < min lien tiep
        self.consecutive_high_count = 0             # So lan rpm > max lien tuc
        self.consecutive_error_count= 0             # So lan khong doc duoc sensor

        # Nguong thoi gian (tinh theo so lan doc)
        # 30s / 2s = 15 lan doc
        self.low_rpm_threshold = 15                 # 30s lien tuc
        # 20s / 2s = 10 lan doc
        self.high_rpm_threshold = 10                # 20s lien tuc
        # 3 lan doc lien tiep loi
        self.sensor_error_threshold = 3

        # Khoi tao WMI
        pythoncom.CoInitialize()
        self.wmi_connection = wmi.WMI(namespace="root\\LibreHardwareMonitor")

        # Load config
        self.config = self._load_config()
        self.sensor_min_max = {'fans': {}}

        # Load trang thai cuoi tu file
        self._load_last_state()

        