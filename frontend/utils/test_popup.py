# frontend/popup/test_popup.py
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from popup_notification import PopupMessage
import time

def test_popups():
    app = QApplication(sys.argv)
    
    # Danh sách các loại popup cần test
    # popup_types = ["normal"]
    # popup_types = ["fan_error"]
    popup_types = ["fan_slow"]
    # popup_types = ["fan_fast"]

    
    current_index = 0
    
    def show_next_popup():
        nonlocal current_index
        if current_index < len(popup_types):
            popup_type = popup_types[current_index]
            print(f"Đang hiển thị popup: {popup_type}")
            
            popup = PopupMessage(message_type=popup_type, font_family="Arial")
            
            # Khi popup đóng, hiển thị popup tiếp theo
            def on_popup_closed():
                nonlocal current_index
                current_index += 1
                QTimer.singleShot(1000, show_next_popup)  # Đợi 1 giây trước khi hiển thị popup tiếp theo
            
            # Kết nối sự kiện đóng popup
            popup.destroyed.connect(on_popup_closed)
            
            # Tự động đóng sau 3 giây để test nhanh
            QTimer.singleShot(3000, popup.close_with_animation)
    
    # Bắt đầu hiển thị popup đầu tiên
    QTimer.singleShot(1000, show_next_popup)
    
    print("Bắt đầu test popup. Sẽ hiển thị lần lượt:")
    for i, popup_type in enumerate(popup_types, 1):
        print(f"{i}. {popup_type}")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    test_popups()