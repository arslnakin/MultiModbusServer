import sys
import asyncio
import threading
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow
from core.server_manager import ServerManager

def start_asyncio_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

def main():
    app = QApplication(sys.argv)
    
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
