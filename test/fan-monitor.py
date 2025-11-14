import sys
import ctypes
from PyQt5 import QtWidgets, QtGui, QtCore


def resource_path(relative_path):
    import os
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class FontTestWindow(QtWidgets.QWidget):
    """Cửa sổ nhỏ hiển thị để kiểm tra font"""
    def __init__(self, font_family):
        super().__init__()
        self.setWindowTitle("ROSA AIPC - Font Test")
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint |  # luôn trên cùng
            QtCore.Qt.Tool  # không hiển thị trên taskbar
        )
        self.resize(300, 100)

        layout = QtWidgets.QVBoxLayout(self)
        label = QtWidgets.QLabel("Font test: Montserrat 10pt", self)
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setFont(QtGui.QFont(font_family, 10))
        layout.addWidget(label)

        # Ẩn sau 5 giây
        QtCore.QTimer.singleShot(5000, self.hide)


class SystemTrayApp(QtWidgets.QSystemTrayIcon):
    def __init__(self, app, font_family, icon_path="assets/icon/icon.png"):
        icon = QtGui.QIcon(resource_path(icon_path))
        super().__init__(icon, app)

        self.font_family = font_family

        menu = QtWidgets.QMenu()
        show_action = menu.addAction("Hiển thị kiểm tra font")
        quit_action = menu.addAction("Thoát")

        show_action.triggered.connect(self.show_font_test)
        quit_action.triggered.connect(app.quit)

        self.setContextMenu(menu)
        self.setToolTip("ROSA AIPC đang chạy ngầm")
        self.show()

        # Hiển thị cửa sổ kiểm tra font khi khởi động
        self.show_font_test()

    def show_font_test(self):
        self.test_window = FontTestWindow(self.font_family)
        self.test_window.show()


def main():
    user32 = ctypes.windll.user32
    app_name = "ROSA.AIPC.APPLICATION"
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, app_name)
    last_error = ctypes.windll.kernel32.GetLastError()

    if last_error == 183:  # ERROR_ALREADY_EXISTS
        ctypes.windll.kernel32.CloseHandle(mutex)
        print("Ứng dụng đã được chạy. Kích hoạt cửa sổ hiện tại...")
        hwnd = user32.FindWindowW(None, "ROSA AIPC - Font Test")
        if hwnd:
            user32.ShowWindow(hwnd, 9)
            user32.SetForegroundWindow(hwnd)
        sys.exit(0)

    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    # === LOAD FONT ===
    font_db = QtGui.QFontDatabase()
    font_id = font_db.addApplicationFont(resource_path(r"assets/font/Montserrat-Regular.ttf"))
    if font_id == -1:
        print("❌ Load font thất bại.")
        font_family = "Arial"
    else:
        families = font_db.applicationFontFamilies(font_id)
        if families:
            font_family = families[0]
            app.setFont(QtGui.QFont(font_family, 10))
            print(f"✅ Font đã load: {font_family}")
        else:
            print("❌ Không tìm thấy family trong font.")
            font_family = "Arial"

    tray = SystemTrayApp(app, font_family)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
