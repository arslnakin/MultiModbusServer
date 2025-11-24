import asyncio
import logging
from pymodbus.server import ModbusTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusServerContext
from pymodbus.server import ModbusTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusServerContext
from pymodbus import ModbusDeviceIdentification
try:
    from pymodbus.datastore import ModbusSlaveContext
except ImportError:
    from pymodbus.datastore import ModbusDeviceContext as ModbusSlaveContext

class VirtualModbusServer:
    def __init__(self, ip, port, server_id=1):
        self.ip = ip
        self.port = port
        self.server_id = server_id
        self.context = None
        self.server = None
        self.server_task = None
        self.simulation_task = None
        # Rules: { address: { 'type': 'toggle'|'counter', 'interval': float, 'last_update': float, 'params': {} } }
        self.simulation_rules = {}
        self._setup_context()

    def _setup_context(self):
        store = ModbusSlaveContext(
            di=ModbusSequentialDataBlock(0, [0]*100),
            co=ModbusSequentialDataBlock(0, [0]*100),
            hr=ModbusSequentialDataBlock(0, [0]*100),
            ir=ModbusSequentialDataBlock(0, [0]*100)
        )
        self.context = ModbusServerContext(devices=store, single=True)
        
        self.identity = ModbusDeviceIdentification()
        self.identity.VendorName = 'Pymodbus'
        self.identity.ProductCode = 'PM'
        self.identity.ProductName = 'Pymodbus Server'
        self.identity.ModelName = 'Pymodbus Server'
        self.identity.MajorMinorRevision = '1.0'

    async def start(self):
        if self.server:
            return

        logging.info(f"Starting server at {self.ip}:{self.port}")
        
        self.server = ModbusTcpServer(
            context=self.context,
            identity=self.identity,
            address=(self.ip, self.port)
        )
        
        self.server_task = asyncio.create_task(self.server.serve_forever())
        self.start_simulation()

    async def stop(self):
        self.stop_simulation()
        if self.server:
            logging.info(f"Stopping server at {self.ip}:{self.port}")
            await self.server.shutdown()
            if self.server_task:
                self.server_task.cancel()
                try:
                    await self.server_task
                except asyncio.CancelledError:
                    pass
            self.server = None
            self.server_task = None

    def start_simulation(self):
        if not self.simulation_task:
            self.simulation_task = asyncio.create_task(self._simulation_loop())

    def stop_simulation(self):
        if self.simulation_task:
            self.simulation_task.cancel()
            self.simulation_task = None

    def update_simulation_rule(self, address, rule_type, interval, params=None):
        """
        Update or add a simulation rule for a specific register address.
        rule_type: 'none', 'toggle', 'counter'
        interval: seconds (float)
        params: dict of extra parameters (e.g. min/max for counter)
        """
        if rule_type == 'none':
            if address in self.simulation_rules:
                del self.simulation_rules[address]
        else:
            self.simulation_rules[address] = {
                'type': rule_type,
                'interval': max(0.1, interval), # Minimum 100ms
                'last_update': 0,
                'params': params or {}
            }

    async def _simulation_loop(self):
        try:
            while True:
                current_time = asyncio.get_event_loop().time()
                slave_id = 1
                
                # Iterate over a copy of keys to avoid runtime errors if dict changes
                for address, rule in list(self.simulation_rules.items()):
                    if current_time - rule['last_update'] >= rule['interval']:
                        try:
                            # Read current value
                            # Note: getValues(function_code, address, count)
                            # 3 = Holding Register
                            values = self.context[slave_id].getValues(3, address, count=1)
                            current_val = values[0]
                            new_val = current_val

                            if rule['type'] == 'toggle':
                                new_val = 1 if current_val == 0 else 0
                            
                            elif rule['type'] == 'counter':
                                new_val = current_val + 1
                                # Optional: Reset if overflow (Modbus registers are 16-bit usually)
                                if new_val > 65535:
                                    new_val = 0
                            
                            self.context[slave_id].setValues(3, address, [new_val])
                            rule['last_update'] = current_time
                            # logging.debug(f"Server {self.ip} updated reg {address} to {new_val}")
                            
                        except Exception as e:
                            logging.error(f"Error updating rule for {address}: {e}")

                # Check frequently enough to satisfy the fastest interval
                await asyncio.sleep(0.1)
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logging.error(f"Simulation error on {self.ip}: {e}")
