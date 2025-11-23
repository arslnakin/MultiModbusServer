import asyncio
import logging
from pymodbus.client import AsyncModbusTcpClient
from core.server_manager import ServerManager

# Configure logging
logging.basicConfig(level=logging.INFO)

async def test_server_connectivity():
    # 1. Start Servers
    print("Initializing Server Manager...")
    manager = ServerManager() 
    
    print("Adding servers...")
    # Add a few servers for testing
    manager.add_server("127.0.0.1", 5020)
    manager.add_server("127.0.0.2", 5021)
    
    print("Starting servers...")
    await manager.start_all()
    
    # Give them a moment to start
    await asyncio.sleep(2)
    
    # 2. Test Connectivity
    success_count = 0
    for i, server in enumerate(manager.servers):
        print(f"Testing connection to {server.ip}:{server.port}...")
        client = AsyncModbusTcpClient(server.ip, port=server.port)
        await client.connect()
        
        if client.connected:
            # Try reading a register
            try:
                rr = await client.read_holding_registers(0, count=1, device_id=1)
                if not rr.isError():
                    print(f"  [PASS] Read register from {server.ip}: {rr.registers}")
                    success_count += 1
                else:
                    print(f"  [FAIL] Read error: {rr}")
            except Exception as e:
                print(f"  [FAIL] Exception during read: {e}")
            finally:
                client.close()
        else:
            print(f"  [FAIL] Could not connect to {server.ip}")
            
    # 3. Stop Servers
    print("Stopping servers...")
    await manager.stop_all()
    
    print(f"Test Complete. Success: {success_count}/{len(manager.servers)}")

if __name__ == "__main__":
    # We need to run this in an event loop
    # Since we are in a script, we can use asyncio.run
    try:
        asyncio.run(test_server_connectivity())
    except KeyboardInterrupt:
        pass
