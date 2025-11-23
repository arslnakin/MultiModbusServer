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
        self.simulation_task = asyncio.create_task(self._simulation_loop())

    def stop_simulation(self):
        if hasattr(self, 'simulation_task') and self.simulation_task:
            self.simulation_task.cancel()

    async def _simulation_loop(self):
        try:
            while True:
                # Toggle Register 1 (Address 1)
                # Note: pymodbus datastore is usually 0-indexed internally but accessed via address.
                # If we want register 1, we write to address 1.
                # Let's read current value first or just toggle.
                
                # Accessing slave 1, holding registers (3), address 1
                slave_id = 1
                address = 1
                values = self.context[slave_id].getValues(3, address, count=1)
                new_value = 1 if values[0] == 0 else 0
                self.context[slave_id].setValues(3, address, [new_value])
                
                logging.debug(f"Server {self.ip} updated reg {address} to {new_value}")
                await asyncio.sleep(5)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logging.error(f"Simulation error on {self.ip}: {e}")
