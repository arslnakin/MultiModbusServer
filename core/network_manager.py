import subprocess
import re
import platform
import asyncio
import logging
import socket

class NetworkManager:
    def __init__(self):
        pass

    def get_interfaces(self):
        """
        Returns a list of dicts: {'name': 'Ethernet', 'ip': '192.168.1.10', 'mask': '255.255.255.0'}
        This is tricky cross-platform, but for Windows we can parse ipconfig or netsh.
        Using netsh is more robust for interface names.
        """
        interfaces = []
        try:
            # Run netsh interface ip show config
            result = subprocess.run(['netsh', 'interface', 'ip', 'show', 'config'], capture_output=True, text=True)
            output = result.stdout
            
            # Parse output
            current_iface = None
            for line in output.splitlines():
                line = line.strip()
                if not line:
                    continue
                    
                # "Configuration for interface "Wi-Fi""
                match_name = re.match(r'Configuration for interface "(.*)"', line)
                if match_name:
                    current_iface = {'name': match_name.group(1), 'ip': [], 'mask': []}
                    interfaces.append(current_iface)
                    continue
                
                if current_iface:
                    # "IP Address:                           192.168.1.45"
                    match_ip = re.match(r'IP Address.*:\s+([0-9.]+)', line)
                    if match_ip:
                        current_iface['ip'].append(match_ip.group(1))
                    
                    # "Subnet Prefix:                        192.168.1.0/24 (mask 255.255.255.0)"
                    # Or "Subnet Mask:                        255.255.255.0"
                    match_mask = re.match(r'Subnet Mask.*:\s+([0-9.]+)', line)
                    if match_mask:
                        current_iface['mask'].append(match_mask.group(1))
                        
        except Exception as e:
            logging.error(f"Error getting interfaces: {e}")
            
        # Filter out interfaces without IP
        return [i for i in interfaces if i['ip']]

    async def scan_network(self, start_ip, count, timeout=0.2):
        """
        Pings IPs starting from start_ip for count times.
        Returns list of FREE IPs (those that did NOT respond).
        """
        free_ips = []
        base_parts = list(map(int, start_ip.split('.')))
        
        tasks = []
        for i in range(count):
            # Increment IP
            # Handle simple carry over for last octet
            current_parts = base_parts.copy()
            current_parts[3] += i
            while current_parts[3] > 255:
                current_parts[3] -= 256
                current_parts[2] += 1
                # ... and so on, but let's assume simple range for now
            
            ip = ".".join(map(str, current_parts))
            tasks.append(self._ping(ip, timeout))
            
        results = await asyncio.gather(*tasks)
        
        for ip, is_alive in results:
            if not is_alive:
                free_ips.append(ip)
                
        return free_ips

    async def _ping(self, ip, timeout):
        # Windows ping uses -n for count, -w for timeout (ms)
        timeout_ms = int(timeout * 1000)
        proc = await asyncio.create_subprocess_exec(
            'ping', '-n', '1', '-w', str(timeout_ms), ip,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        await proc.wait()
        return ip, proc.returncode == 0

    def add_virtual_ip(self, interface_name, ip, mask):
        """
        Adds an IP alias to the interface using netsh.
        Requires Admin privileges.
        netsh interface ip add address "Interface Name" IP Mask
        """
        try:
            cmd = ['netsh', 'interface', 'ip', 'add', 'address', interface_name, ip, mask]
            logging.info(f"Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return True, "Success"
            else:
                return False, result.stderr or result.stdout
        except Exception as e:
            return False, str(e)

    def remove_virtual_ip(self, interface_name, ip):
        """
        Removes an IP alias.
        netsh interface ip delete address "Interface Name" IP
        """
        try:
            cmd = ['netsh', 'interface', 'ip', 'delete', 'address', interface_name, ip]
            logging.info(f"Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return True, "Success"
            else:
                return False, result.stderr or result.stdout
        except Exception as e:
            return False, str(e)
