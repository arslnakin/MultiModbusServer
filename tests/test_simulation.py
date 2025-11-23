import asyncio
import logging
from pymodbus.client import AsyncModbusTcpClient
from core.server_manager import ServerManager

# Configure logging
logging.basicConfig(level=logging.INFO)

async def test_simulation():
    print("Initializing Server Manager...")
    manager = ServerManager() 
    manager.add_server("127.0.0.1", 5020)
    
    print("Starting server...")
    await manager.start_all()
    
    # Give it a moment to start
    await asyncio.sleep(2)
    
    client = AsyncModbusTcpClient("127.0.0.1", port=5020)
    await client.connect()
    
    if client.connected:
        try:
            # Read initial value
            # Register 1 is address 1
            rr1 = await client.read_holding_registers(1, count=1, device_id=1)
            val1 = rr1.registers[0]
            print(f"Initial value: {val1}")
            
            print("Waiting 6 seconds for simulation toggle...")
            await asyncio.sleep(6)
            
            # Read new value
            rr2 = await client.read_holding_registers(1, count=1, device_id=1)
            val2 = rr2.registers[0]
            print(f"New value: {val2}")
            
            if val1 != val2:
                print("[PASS] Value changed!")
            else:
                print("[FAIL] Value did not change.")
                
        except Exception as e:
            print(f"[FAIL] Exception: {e}")
        finally:
            client.close()
    else:
        print("[FAIL] Could not connect")
            
    print("Stopping server...")
    await manager.stop_all()

if __name__ == "__main__":
    try:
        asyncio.run(test_simulation())
    except KeyboardInterrupt:
        pass
