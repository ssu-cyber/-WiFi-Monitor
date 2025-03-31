import socket
import psutil
import platform
import subprocess
from datetime import datetime

def get_network_info():
    """Obtient les informations sur le réseau actuel"""
    interfaces = psutil.net_if_addrs()
    gateway = psutil.net_if_stats().items()
    
    for interface, stats in gateway:
        if stats.isup:
            for addr in interfaces[interface]:
                if addr.family == socket.AF_INET:
                    ip_parts = addr.address.split('.')
                    subnet = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.0"
                    return {
                        'interface': interface,
                        'ip': addr.address,
                        'netmask': addr.netmask,
                        'subnet': subnet,
                        'gateway': get_default_gateway()
                    }
    return {}

def get_default_gateway():
    """Obtient la passerelle par défaut"""
    if platform.system() == "Windows":
        result = subprocess.run(["ipconfig"], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        for line in lines:
            if "Default Gateway" in line:
                return line.split(":")[1].strip()
    else:
        result = subprocess.run(["ip", "route"], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        for line in lines:
            if "default via" in line:
                return line.split()[2]
    return ""

def is_admin():
    """Vérifie si l'application a les privilèges administrateur"""
    try:
        if platform.system() == "Windows":
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.geteuid() == 0
    except:
        return False