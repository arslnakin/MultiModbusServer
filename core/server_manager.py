import asyncio
from .modbus_server import VirtualModbusServer

class ServerManager:
    def __init__(self):
        self.servers = []

    def add_server(self, ip, port):
        # Check if server already exists
        for s in self.servers:
            if s.ip == ip and s.port == port:
                return False
        
        server = VirtualModbusServer(ip, port, server_id=1)
        self.servers.append(server)
        return True

    async def remove_server(self, index):
        if 0 <= index < len(self.servers):
            server = self.servers[index]
            if server.is_running or server.server:
                await server.stop()
            self.servers.pop(index)
            return True
        return False

    async def start_all(self):
        tasks = [server.start() for server in self.servers]
        if tasks:
            await asyncio.gather(*tasks)

    async def stop_all(self):
        tasks = [server.stop() for server in self.servers]
        if tasks:
            await asyncio.gather(*tasks)

    async def start_server(self, index):
        if 0 <= index < len(self.servers):
            await self.servers[index].start()

    async def stop_server(self, index):
        if 0 <= index < len(self.servers):
            await self.servers[index].stop()
            
    def get_server_status(self, index):
        if 0 <= index < len(self.servers):
            server = self.servers[index]
            return {
                "ip": server.ip,
                "port": server.port,
                "running": server.server is not None
            }
        return None
