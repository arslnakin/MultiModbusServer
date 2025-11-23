import asyncio
import logging
from core.network_manager import NetworkManager

# Configure logging
logging.basicConfig(level=logging.INFO)

async def test_network():
    nm = NetworkManager()
    
    print("1. Getting Interfaces...")
    interfaces = nm.get_interfaces()
    for iface in interfaces:
        print(f"  Found: {iface}")
        
    if not interfaces:
        print("  [WARN] No interfaces found (might be normal in some envs)")
    
    print("\n2. Scanning Localhost (127.0.0.1)...")
    # We scan 127.0.0.1 to 127.0.0.5. 
    # Usually 127.0.0.1 is taken, others might be free or taken if we ran previous tests.
    free_ips = await nm.scan_network("127.0.0.1", 5)
    print(f"  Free IPs: {free_ips}")
    
    # Note: We cannot test add_virtual_ip without Admin rights and risking config change.
    print("\nSkipping add_virtual_ip test (requires Admin).")

if __name__ == "__main__":
    try:
        asyncio.run(test_network())
    except KeyboardInterrupt:
        pass
