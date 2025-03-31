import scapy.all as scapy
from mac_vendor_lookup import MacLookup
from threading import Thread, Event
import time
import socket
from collections import defaultdict
from src.network_scanner.device import Device
from src.utils.helpers import get_network_info, is_admin
from src.security.firewall import FirewallManager
import logging

class AdvancedNetworkScanner:
    def __init__(self, update_interval=60):
        self.devices = []
        self.known_devices = defaultdict(dict)
        self.update_interval = update_interval
        self.scanning_event = Event()
        self.mac_lookup = MacLookup()
        self.current_network = get_network_info()
        self.scan_thread = None
        self.firewall = FirewallManager() if is_admin() else None
        self.setup_logging()
        
        # Configuration avancée
        self.port_scan_enabled = False
        self.common_ports = [21, 22, 23, 80, 443, 3389]
        self.arp_spoof_detection = True

    def setup_logging(self):
        """Configure le système de journalisation"""
        self.logger = logging.getLogger('network_scanner')
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler('network_scan.log')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def enhanced_arp_scan(self):
        """Scan ARP avec détection d'anomalies"""
        if not is_admin():
            self.logger.warning("Privilèges admin requis pour un scan complet")
            return []

        try:
            # Scan ARP standard
            arp_request = scapy.ARP(pdst=f"{self.current_network['subnet']}/24")
            broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
            arp_request_broadcast = broadcast/arp_request
            answered, unanswered = scapy.srp(arp_request_broadcast, timeout=2, verbose=False)
            
            # Détection des anomalies
            if self.arp_spoof_detection:
                self.detect_arp_spoofing(answered)
            
            return self.process_scan_results(answered)
            
        except Exception as e:
            self.logger.error(f"Échec du scan ARP: {str(e)}")
            return []

    def detect_arp_spoofing(self, answered_packets):
        """Détecte les tentatives d'empoisonnement ARP"""
        ip_mac_mapping = {}
        for packet in answered_packets:
            ip = packet[1].psrc
            mac = packet[1].hwsrc
            
            if ip in ip_mac_mapping and ip_mac_mapping[ip] != mac:
                self.logger.warning(f"Possible ARP spoofing détecté - IP: {ip} avec plusieurs MAC: {mac} et {ip_mac_mapping[ip]}")
                if self.firewall:
                    self.firewall.block_device(ip, mac)
            
            ip_mac_mapping[ip] = mac

    def process_scan_results(self, answered_packets):
        """Traite les résultats du scan et effectue des vérifications supplémentaires"""
        new_devices = []
        current_time = time.strftime('%Y-%m-%d %H:%M:%S')
        
        for packet in answered_packets:
            try:
                ip = packet[1].psrc
                mac = packet[1].hwsrc
                
                # Vérification du fabricant
                try:
                    vendor = self.mac_lookup.lookup(mac)
                except:
                    vendor = "Inconnu"
                
                # Résolution du nom d'hôte
                try:
                    hostname = socket.gethostbyaddr(ip)[0]
                except:
                    hostname = ip
                
                # Scan de ports optionnel
                open_ports = []
                if self.port_scan_enabled:
                    open_ports = self.quick_port_scan(ip)
                
                device = Device(
                    ip=ip,
                    mac=mac,
                    vendor=vendor,
                    hostname=hostname,
                    first_seen=current_time if mac not in self.known_devices else self.known_devices[mac].get('first_seen', current_time),
                    last_seen=current_time,
                    open_ports=open_ports
                )
                
                new_devices.append(device)
                self.update_device_history(device)
                
            except Exception as e:
                self.logger.error(f"Erreur traitement appareil: {str(e)}")
        
        return new_devices

    def quick_port_scan(self, ip, timeout=1):
        """Effectue un scan rapide des ports communs"""
        open_ports = []
        for port in self.common_ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            if result == 0:
                open_ports.append(port)
            sock.close()
        return open_ports

    def update_device_history(self, device):
        """Met à jour l'historique des appareils"""
        if device.mac not in self.known_devices:
            self.known_devices[device.mac] = {
                'first_seen': device.first_seen,
                'connection_count': 0,
                'last_ports': []
            }
        
        self.known_devices[device.mac]['connection_count'] += 1
        self.known_devices[device.mac]['last_seen'] = device.last_seen
        if hasattr(device, 'open_ports'):
            self.known_devices[device.mac]['last_ports'] = device.open_ports

    def start_continuous_monitoring(self, callback):
        """Lance une surveillance continue avec analyse comportementale"""
        def monitoring_loop():
            while not self.scanning_event.is_set():
                start_time = time.time()
                
                devices = self.enhanced_arp_scan()
                if callback:
                    callback(devices)
                
                # Analyse comportementale
                self.behavioral_analysis(devices)
                
                # Ajustement dynamique de l'intervalle
                scan_duration = time.time() - start_time
                adjusted_interval = max(5, self.update_interval - scan_duration)
                time.sleep(adjusted_interval)
        
        self.scan_thread = Thread(target=monitoring_loop, daemon=True)
        self.scanning_event.clear()
        self.scan_thread.start()

    def behavioral_analysis(self, current_devices):
        """Analyse le comportement des appareils pour détecter des anomalies"""
        current_macs = {device.mac for device in current_devices}
        
        # Détection des appareils disparus
        for known_mac in set(self.known_devices.keys()) - current_macs:
            self.logger.info(f"Appareil disparu: {known_mac}")
        
        # Détection des nouveaux appareils
        for device in current_devices:
            if device.mac not in self.known_devices:
                self.logger.warning(f"Nouvel appareil détecté: {device.mac} ({device.vendor})")
                
                # Alerte si l'appareil scanne des ports
                if hasattr(device, 'open_ports') and device.open_ports:
                    self.logger.warning(f"Appareil suspect {device.mac} a des ports ouverts: {device.open_ports}")

    def stop_monitoring(self):
        """Arrête la surveillance continue"""
        self.scanning_event.set()
        if self.scan_thread:
            self.scan_thread.join(timeout=5)
            self.scan_thread = None