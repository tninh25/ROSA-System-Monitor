# frontend/update/styles/update_styles.py

def get_main_styles():
    return """
        QWidget {
            background: transparent;
            border: none;
        }
    """

def get_left_panel_styles():
    return """
        QWidget {
            background-color: #F8F9FA;
            border-radius: 15px;
            border: 1px solid #E0E0E0;
        }
    """

def get_right_panel_styles():
    return """
        QWidget {
            background-color: #FFFFFF;
            border-radius: 15px;
            border: 1px solid #E0E0E0;
        }
    """

def get_input_styles(font_family):
    return f"""
        QLineEdit {{
            font-family: '{font_family}';
            font-size: 14px;
            padding: 0px 15px;
            border: 1px solid #DCDFE6;
            border-radius: 8px;
            background-color: #FFFFFF;
            height: 45px;
        }}
        QLineEdit:focus {{
            border: 1px solid #2E86AB;
        }}
    """

def get_button_styles(font_family):
    return f"""
        QPushButton {{
            font-family: '{font_family}';
            font-size: 16px;
            font-weight: bold;
            color: white;
            background-color: #004386;
            border: none;
            border-radius: 8px;
            padding: 0px 20px;
            height: 50px;
        }}
        QPushButton:hover {{
            background-color: #003366;
        }}
        QPushButton:pressed {{
            background-color: #00274D;
        }}
    """

def get_logo_styles(font_family):
    return f"""
        QLabel {{
            background-color: #2E86AB;
            border-radius: 10px;
            color: white;
            font-family: '{font_family}';
            font-size: 12px;
            font-weight: bold;
            border: none;
        }}
    """

def get_title_styles(font_family):
    return f"""
        QLabel {{
            color: #2C3E50;
            font-family: '{font_family}';
            font-size: 28px;
            font-weight: bold;
            background: transparent;
            border: none;
            padding: 0px;
            margin: 0px;
        }}
    """

def get_desc_styles(font_family):
    return f"""
        QLabel {{
            color: #7F8C8D;
            font-family: '{font_family}';
            font-size: 14px;
            font-weight: normal;
            background: transparent;
            border: none;
            padding: 0px;
            margin: 0px;
            line-height: 1.4;
        }}
    """

def get_status_styles(font_family, status="active"):
    color = "#27AE60" if status == "active" else "#E74C3C"
    return f"""
        QLabel {{
            color: {color};
            font-family: '{font_family}';
            font-size: 12px;
            font-weight: normal;
            background: transparent;
            border: none;
            padding: 0px;
            margin: 0px;
        }}
    """

def get_monitoring_styles(font_family):
    return f"""
        QLabel {{
            color: #2C3E50;
            font-family: '{font_family}';
            font-size: 17px;
            font-weight: 600;
            background: transparent;
            border: none;
            padding: 0px;
            margin: 0px;
            qproperty-alignment: 'AlignCenter';  /* THÊM DÒNG NÀY */
        }}
    """

def get_info_label_styles(font_family):
    return f"""
        QLabel {{
            color: #7F8C8D;
            font-family: '{font_family}';
            font-size: 12px;
            font-weight: normal;
            background: transparent;
            border: none;
            padding: 0px;
            margin: 0px;
        }}
    """

def get_info_value_styles(font_family):
    return f"""
        QLabel {{
            color: #2C3E50;
            font-family: '{font_family}';
            font-size: 14px;
            font-weight: 600;
            background: transparent;
            border: none;
            padding: 0px;
            margin: 0px;
        }}
    """
def get_minimize_button_styles():
    return """
        QPushButton {
            background-color: #FFA500;
            border: none;
            border-radius: 10px;
            color: white;
            font-weight: bold;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #FF8C00;
        }
        QPushButton:pressed {
            background-color: #FF7F00;
        }
    """

def get_close_button_styles():
    return """
        QPushButton {
            background-color: #FF4444;
            border: none;
            border-radius: 10px;
            color: white;
            font-weight: bold;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #CC0000;
        }
        QPushButton:pressed {
            background-color: #990000;
        }
    """

def get_value_frame_styles():
    """Style cho khung giá trị chỉ đọc"""
    return """
        QFrame {
            background: #F8F9FA;
            border: 1.5px solid #E0E0E0;
            border-radius: 8px;
        }
    """

def get_edit_button_styles(font_family):
    """Style cho nút chỉnh sửa"""
    return f"""
        QPushButton {{
            font-family: '{font_family}';
            font-size: 14px;
            font-weight: bold;
            color: #FFFFFF;
            background-color: #004386;
            border: none;
            border-radius: 10px;
            padding: 0px 20px;
        }}
        QPushButton:hover {{
            background-color: #2980B9;
        }}
        QPushButton:pressed {{
            background-color: #21618C;
        }}
    """

def get_update_button_styles(font_family):
    """Style cho nút cập nhật"""
    return f"""
        QPushButton {{
            font-family: '{font_family}';
            font-size: 14px;
            font-weight: bold;
            color: #FFFFFF;
            background-color: #27AE60;
            border: none;
            border-radius: 10px;
            padding: 0px 20px;
        }}
        QPushButton:hover {{
            background-color: #219653;
        }}
        QPushButton:pressed {{
            background-color: #1E8449;
        }}
    """