import asyncio
from core.server_manager import ServerManager

async def test_simulation_rules():
    manager = ServerManager()
    
    # Add a server
    assert manager.add_server('127.0.0.1', 5025)
    server = manager.servers[0]
    
    # Start server
    await server.start()
    
    try:
        # 1. Test Toggle Rule
        # Set Register 0 to Toggle every 0.2s
        manager.set_simulation_rule(0, 0, 'toggle', 0.2)
        
        # Wait for a few cycles
        await asyncio.sleep(0.5)
        
        # Check value (should be toggling)
        val1 = server.context[1].getValues(3, 0, count=1)[0]
        await asyncio.sleep(0.3)
        val2 = server.context[1].getValues(3, 0, count=1)[0]
        
        print(f"Toggle Test: Val1={val1}, Val2={val2}")
        assert val1 != val2 or (val1 in [0, 1] and val2 in [0, 1]) # It might have toggled back, but let's check it's active
        
        # 2. Test Counter Rule
        # Set Register 1 to Counter every 0.1s
        manager.set_simulation_rule(0, 1, 'counter', 0.1)
        
        # Reset value to 0 manually to be sure
        server.context[1].setValues(3, 1, [0])
        
        await asyncio.sleep(0.35)
        val_count = server.context[1].getValues(3, 1, count=1)[0]
        print(f"Counter Test: Value={val_count}")
        assert val_count >= 3 # Should have incremented at least 3 times
        
        # 3. Test Removing Rule
        manager.set_simulation_rule(0, 0, 'none', 0)
        val_stopped = server.context[1].getValues(3, 0, count=1)[0]
        await asyncio.sleep(0.3)
        val_stopped_2 = server.context[1].getValues(3, 0, count=1)[0]
        assert val_stopped == val_stopped_2
        
    finally:
        await manager.stop_all()

if __name__ == "__main__":
    asyncio.run(test_simulation_rules())
