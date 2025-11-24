import asyncio
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QLabel, QStatusBar, QLineEdit, QMessageBox,
                             QComboBox, QGroupBox, QFormLayout, QTabWidget, QDoubleSpinBox)
from PyQt6.QtCore import QTimer, pyqtSignal, QObject, QThread
from PyQt6.QtGui import QColor, QPalette
from core.network_manager import NetworkManager

class AsyncWorker(QObject):
    finished = pyqtSignal()
    
    def __init__(self, loop):
        super().__init__()
        self.loop = loop

    def run_coroutine(self, coro):
        asyncio.run_coroutine_threadsafe(coro, self.loop)

class MainWindow(QMainWindow):
    scan_finished = pyqtSignal(str)

    def __init__(self, manager, loop):
        super().__init__()
        self.manager = manager
        self.loop = loop
        self.net_manager = NetworkManager()
        self.setWindowTitle("Multi-IP Modbus Server Manager")
        self.resize(1000, 700)
        
        self.scan_finished.connect(self.on_scan_finished)
        
        self._setup_ui()
        self._setup_timer()

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Tab 1: Server Management
        self.tab_management = QWidget()
        self._setup_management_tab()
        self.tabs.addTab(self.tab_management, "Server Management")
        
        # Tab 2: Data Simulation
        self.tab_simulation = QWidget()
        self._setup_simulation_tab()
        self.tabs.addTab(self.tab_simulation, "Data Simulation")
        
        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def _setup_management_tab(self):
        layout = QVBoxLayout(self.tab_management)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Modbus Server Control Panel")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Network Setup Group
        net_group = QGroupBox("Network Auto-Setup (Requires Admin)")
        net_layout = QHBoxLayout()
        
        self.combo_iface = QComboBox()
        self.refresh_interfaces()
        
        self.input_scan_ip = QLineEdit()
        self.input_scan_ip.setPlaceholderText("Start IP (e.g. 192.168.1.50)")
        
        self.input_scan_port = QLineEdit()
        self.input_scan_port.setPlaceholderText("Port")
        self.input_scan_port.setText("5020")
        self.input_scan_port.setFixedWidth(60)

        self.input_scan_count = QLineEdit()
        self.input_scan_count.setPlaceholderText("Count")
        self.input_scan_count.setText("5")
        self.input_scan_count.setFixedWidth(50)
        
        self.btn_scan = QPushButton("Scan & Claim IPs")
        self.btn_scan.clicked.connect(self.scan_and_claim)
        
        net_layout.addWidget(QLabel("Interface:"))
        net_layout.addWidget(self.combo_iface)
        net_layout.addWidget(QLabel("Start IP:"))
        net_layout.addWidget(self.input_scan_ip)
        net_layout.addWidget(QLabel("Port:"))
        net_layout.addWidget(self.input_scan_port)
        net_layout.addWidget(QLabel("Count:"))
        net_layout.addWidget(self.input_scan_count)
        net_layout.addWidget(self.btn_scan)
        net_group.setLayout(net_layout)
        layout.addWidget(net_group)
        
        # Manual Add Group
        add_group = QGroupBox("Manual Add")
        add_layout = QHBoxLayout()
        self.input_ip = QLineEdit()
        self.input_ip.setPlaceholderText("IP Address")
        self.input_ip.setText("127.0.0.1")
        
        self.input_port = QLineEdit()
        self.input_port.setPlaceholderText("Port")
        self.input_port.setText("5020")
        self.input_port.setFixedWidth(100)
        
        self.btn_add = QPushButton("Add Server")
        self.btn_add.clicked.connect(self.add_server)
        
        add_layout.addWidget(QLabel("IP:"))
        add_layout.addWidget(self.input_ip)
        add_layout.addWidget(QLabel("Port:"))
        add_layout.addWidget(self.input_port)
        add_layout.addWidget(self.btn_add)
        add_group.setLayout(add_layout)
        layout.addWidget(add_group)
        
        # Global Controls
        control_layout = QHBoxLayout()
        self.btn_start_all = QPushButton("Start All")
        self.btn_start_all.clicked.connect(self.start_all_servers)
        self.btn_stop_all = QPushButton("Stop All")
        self.btn_stop_all.clicked.connect(self.stop_all_servers)
        self.btn_remove = QPushButton("Remove Selected")
        self.btn_remove.clicked.connect(self.remove_selected_server)
        
        control_layout.addWidget(self.btn_start_all)
        control_layout.addWidget(self.btn_stop_all)
        control_layout.addStretch()
        control_layout.addWidget(self.btn_remove)
        layout.addLayout(control_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "IP Address", "Port", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        
        self.refresh_table()

    def _setup_simulation_tab(self):
        layout = QVBoxLayout(self.tab_simulation)
        
        # Top Controls
        top_layout = QHBoxLayout()
        
        self.combo_sim_server = QComboBox()
        self.combo_sim_server.currentIndexChanged.connect(self.on_sim_server_changed)
        top_layout.addWidget(QLabel("Select Server:"))
        top_layout.addWidget(self.combo_sim_server)
        top_layout.addStretch()
        
        layout.addLayout(top_layout)
        
        # Simulation Rule Configuration
        config_group = QGroupBox("Configure Rule")
        config_layout = QHBoxLayout()
        
        self.combo_sim_type = QComboBox()
        self.combo_sim_type.addItems(["None", "Toggle (0/1)", "Counter"])
        
        self.spin_sim_interval = QDoubleSpinBox()
        self.spin_sim_interval.setRange(0.1, 60.0)
        self.spin_sim_interval.setValue(1.0)
        self.spin_sim_interval.setSingleStep(0.1)
        self.spin_sim_interval.setSuffix(" sec")
        
        self.btn_apply_rule = QPushButton("Apply to Selected Register(s)")
        self.btn_apply_rule.clicked.connect(self.apply_simulation_rule)
        
        config_layout.addWidget(QLabel("Function:"))
        config_layout.addWidget(self.combo_sim_type)
        config_layout.addWidget(QLabel("Interval:"))
        config_layout.addWidget(self.spin_sim_interval)
        config_layout.addWidget(self.btn_apply_rule)
        config_group.setLayout(config_layout)
        
        layout.addWidget(config_group)
        
        # Registers Table
        self.sim_table = QTableWidget()
        self.sim_table.setColumnCount(4)
        self.sim_table.setHorizontalHeaderLabels(["Address", "Current Function", "Interval", "Params"])
        self.sim_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.sim_table.setRowCount(10)
        for i in range(10):
            self.sim_table.setItem(i, 0, QTableWidgetItem(f"Holding Register {i}"))
            self.sim_table.setItem(i, 1, QTableWidgetItem("None"))
            self.sim_table.setItem(i, 2, QTableWidgetItem("-"))
            self.sim_table.setItem(i, 3, QTableWidgetItem("-"))
            
        layout.addWidget(self.sim_table)

    def refresh_interfaces(self):
        self.combo_iface.clear()
        interfaces = self.net_manager.get_interfaces()
        for iface in interfaces:
            # Display Name (IP)
            ip_str = iface['ip'][0] if iface['ip'] else "No IP"
            self.combo_iface.addItem(f"{iface['name']} ({ip_str})", iface)

    def scan_and_claim(self):
        start_ip = self.input_scan_ip.text()
        try:
            count = int(self.input_scan_count.text())
        except ValueError:
            QMessageBox.warning(self, "Error", "Count must be a number")
            return
            
        try:
            port = int(self.input_scan_port.text())
        except ValueError:
            QMessageBox.warning(self, "Error", "Port must be a number")
            return
            
        if not start_ip:
            QMessageBox.warning(self, "Error", "Please enter Start IP")
            return
            
        iface_data = self.combo_iface.currentData()
        if not iface_data:
            QMessageBox.warning(self, "Error", "No interface selected")
            return

        self.status_bar.showMessage(f"Scanning {count} IPs starting from {start_ip}...")
        self.btn_scan.setEnabled(False)
        
        # Run async scan
        asyncio.run_coroutine_threadsafe(self._async_scan_and_claim(iface_data, start_ip, count, port), self.loop)

    async def _async_scan_and_claim(self, iface_data, start_ip, count, port):
        msg = ""
        try:
            # 1. Scan for free IPs
            free_ips = await self.net_manager.scan_network(start_ip, count)
            
            if not free_ips:
                msg = "No free IPs found in range."
                return

            # 2. Claim IPs (Add alias)
            # We need the mask.
            mask = iface_data['mask'][0] if iface_data['mask'] else "255.255.255.0"
            
            added_ips = []
            for ip in free_ips:
                success, err_msg = self.net_manager.add_virtual_ip(iface_data['name'], ip, mask)
                if success:
                    added_ips.append(ip)
                    # Add to Server Manager
                    self.manager.add_server(ip, port)
                else:
                    print(f"Failed to claim {ip}: {err_msg}")
            
            msg = f"Added {len(added_ips)} servers."
            
        except Exception as e:
            msg = f"Scan error: {e}"
        finally:
            self.scan_finished.emit(msg)

    def on_scan_finished(self, msg):
        self.btn_scan.setEnabled(True)
        self.status_bar.showMessage(msg)
        self.refresh_table()

    def refresh_table(self):
        self.table.setRowCount(len(self.manager.servers))
        for i, server in enumerate(self.manager.servers):
            self.table.setItem(i, 0, QTableWidgetItem(str(i+1)))
            self.table.setItem(i, 1, QTableWidgetItem(server.ip))
            self.table.setItem(i, 2, QTableWidgetItem(str(server.port)))
            
            status_text = "Running" if server.server else "Stopped"
            status_item = QTableWidgetItem(status_text)
            if server.server:
                status_item.setBackground(QColor("#ccffcc"))
            else:
                status_item.setBackground(QColor("#ffcccc"))
            self.table.setItem(i, 3, status_item)
            
        if hasattr(self, 'combo_sim_server'):
            self.refresh_simulation_servers()

    def _setup_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(1000)  # Update every second

    def update_status(self):
        # Only update status column to avoid flickering whole table
        if self.table.rowCount() != len(self.manager.servers):
            self.refresh_table()
            return

        for i in range(len(self.manager.servers)):
            status = self.manager.get_server_status(i)
            item = self.table.item(i, 3)
            if status["running"]:
                item.setText("Running")
                item.setBackground(QColor("#ccffcc"))
            else:
                item.setText("Stopped")
                item.setBackground(QColor("#ffcccc"))

    def add_server(self):
        ip = self.input_ip.text()
        port_str = self.input_port.text()
        
        try:
            port = int(port_str)
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Port must be a number.")
            return
            
        if self.manager.add_server(ip, port):
            self.refresh_table()
            self.status_bar.showMessage(f"Added server {ip}:{port}")
        else:
            QMessageBox.warning(self, "Error", "Server already exists.")

    def remove_selected_server(self):
        row = self.table.currentRow()
        if row >= 0:
            ip = self.table.item(row, 1).text()
            port = self.table.item(row, 2).text()
            
            # We need to remove async, but for UI responsiveness we might just fire and forget
            # or block slightly. Since we have the loop, let's use it.
            asyncio.run_coroutine_threadsafe(self.manager.remove_server(row), self.loop)
            
            # We can't immediately refresh table because removal is async.
            # But our timer will catch it or we can delay refresh.
            # For better UX, let's assume success or wait a bit.
            # Ideally we would have a signal from manager.
            self.status_bar.showMessage(f"Removing server {ip}:{port}...")
        else:
            QMessageBox.warning(self, "Selection", "Please select a server to remove.")

    def start_all_servers(self):
        self.status_bar.showMessage("Starting all servers...")
        asyncio.run_coroutine_threadsafe(self.manager.start_all(), self.loop)

    def stop_all_servers(self):
        self.status_bar.showMessage("Stopping all servers...")
        asyncio.run_coroutine_threadsafe(self.manager.stop_all(), self.loop)

    # Simulation Tab Methods
    def refresh_simulation_servers(self):
        current_idx = self.combo_sim_server.currentIndex()
        self.combo_sim_server.clear()
        
        if not self.manager.servers:
            self.combo_sim_server.addItem("No Servers Available")
            self.combo_sim_server.setEnabled(False)
            return

        self.combo_sim_server.setEnabled(True)
        for i, server in enumerate(self.manager.servers):
            self.combo_sim_server.addItem(f"Server {i+1} ({server.ip}:{server.port})", i)
            
        # Restore selection if possible
        if current_idx >= 0 and current_idx < self.combo_sim_server.count():
            self.combo_sim_server.setCurrentIndex(current_idx)

    def on_sim_server_changed(self, index):
        if index < 0:
            return
        
        server_idx = self.combo_sim_server.currentData()
        if server_idx is None:
            return

        # Refresh table with current rules for this server
        # Since we don't have a direct way to get rules from manager yet without accessing private members or adding a getter,
        # let's assume we can access server.simulation_rules if we are careful, or add a getter in manager.
        # For now, let's access directly for speed, as we are in the same process (mostly).
        # Actually, manager.servers is a list of VirtualModbusServer objects.
        
        server = self.manager.servers[server_idx]
        rules = server.simulation_rules
        
        for i in range(10):
            rule = rules.get(i)
            if rule:
                func_type = rule['type']
                interval = rule['interval']
                params = rule['params']
                
                type_str = "Toggle" if func_type == 'toggle' else "Counter" if func_type == 'counter' else "Unknown"
                self.sim_table.setItem(i, 1, QTableWidgetItem(type_str))
                self.sim_table.setItem(i, 2, QTableWidgetItem(f"{interval}s"))
                self.sim_table.setItem(i, 3, QTableWidgetItem(str(params)))
            else:
                self.sim_table.setItem(i, 1, QTableWidgetItem("None"))
                self.sim_table.setItem(i, 2, QTableWidgetItem("-"))
                self.sim_table.setItem(i, 3, QTableWidgetItem("-"))

    def apply_simulation_rule(self):
        server_idx = self.combo_sim_server.currentData()
        if server_idx is None:
            QMessageBox.warning(self, "Error", "No server selected")
            return

        selected_rows = set()
        for item in self.sim_table.selectedItems():
            selected_rows.add(item.row())
            
        if not selected_rows:
            QMessageBox.warning(self, "Selection", "Please select registers from the table to apply the rule.")
            return

        rule_type_idx = self.combo_sim_type.currentIndex()
        # 0: None, 1: Toggle, 2: Counter
        rule_type_map = {0: 'none', 1: 'toggle', 2: 'counter'}
        rule_type = rule_type_map.get(rule_type_idx, 'none')
        
        interval = self.spin_sim_interval.value()
        
        for row in selected_rows:
            # Address is the row index (0-9)
            address = row
            self.manager.set_simulation_rule(server_idx, address, rule_type, interval)
            
        self.status_bar.showMessage(f"Applied rule {rule_type} to {len(selected_rows)} registers.")
        self.on_sim_server_changed(self.combo_sim_server.currentIndex())
