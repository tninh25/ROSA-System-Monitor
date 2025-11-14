import os, sys

def resource_path(relative_path: str) -> str:
    """Lấy đường dẫn thực tế đến resource"""
    # .exe build
    if getattr(sys, 'frozen', False):
        try:
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.dirname(sys.executable)
    
    # .py source
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)
