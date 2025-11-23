import sys
import asyncio
import threading
import ctypes
from PyQt6.QtWidgets import QApplication, QMessageBox
from gui.main_window import MainWindow
from core.server_manager import ServerManager

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def start_asyncio_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

def main():
    app = QApplication(sys.argv)
    
    if not is_admin():
        QMessageBox.warning(None, "Admin Rights Required", 
                            "This application requires Administrator privileges to manage network settings (IP claiming).\n"
                            "Please restart as Administrator for full functionality.")
    
    # Create a new event loop for asyncio
    loop = asyncio.new_event_loop()
    
    # Start the asyncio loop in a separate thread
    t = threading.Thread(target=start_asyncio_loop, args=(loop,), daemon=True)
    t.start()
    
    # Initialize Server Manager
    manager = ServerManager()
    
    # Initialize Main Window
    window = MainWindow(manager, loop)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
