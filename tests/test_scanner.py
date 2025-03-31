import unittest
from unittest.mock import patch, MagicMock
from src.network_scanner.scanner import AdvancedNetworkScanner
from src.network_scanner.device import Device
import scapy.all as scapy
import socket

class TestNetworkScanner(unittest.TestCase):
    @patch('scapy.all.srp')
    @patch('socket.gethostbyaddr')
    @patch('src.network_scanner.scanner.MacLookup')
    def test_arp_scan(self, mock_mac, mock_host, mock_srp):
        # Configurer les mocks
        mock_srp.return_value = (
            [(None, scapy.ARP(psrc="192.168.1.1", hwsrc="00:11:22:33:44:55"))],
            []
        )
        mock_host.return_value = ("router.local", [], ["192.168.1.1"])
        mock_mac.return_value.lookup.return_value = "Cisco Systems"
        
        # Initialiser le scanner
        scanner = AdvancedNetworkScanner()
        scanner.current_network = {'subnet': '192.168.1.0'}
        
        # Exécuter le scan
        devices = scanner.enhanced_arp_scan()
        
        # Vérifications
        self.assertEqual(len(devices), 1)
        self.assertEqual(devices[0].ip, "192.168.1.1")
        self.assertEqual(devices[0].mac, "00:11:22:33:44:55")
        self.assertEqual(devices[0].vendor, "Cisco Systems")
        self.assertEqual(devices[0].hostname, "router.local")
        
    @patch('src.network_scanner.scanner.socket.socket.connect_ex')
    def test_port_scan(self, mock_connect):
        # Configurer le mock pour simuler les ports ouverts/fermés
        mock_connect.side_effect = lambda x: 0 if x[1] in [80, 443] else 1
        
        scanner = AdvancedNetworkScanner()
        scanner.port_scan_enabled = True
        open_ports = scanner.quick_port_scan("192.168.1.1")
        
        self.assertIn(80, open_ports)
        self.assertIn(443, open_ports)
        self.assertNotIn(22, open_ports)
        
    def test_device_history(self):
        scanner = AdvancedNetworkScanner()
        device = Device(
            ip="192.168.1.2",
            mac="00:11:22:33:44:56",
            vendor="Test Vendor",
            hostname="test.device"
        )
        
        # Premier ajout
        scanner.update_device_history(device)
        self.assertEqual(scanner.known_devices[device.mac]['connection_count'], 1)
        
        # Deuxième ajout
        scanner.update_device_history(device)
        self.assertEqual(scanner.known_devices[device.mac]['connection_count'], 2)
        
    @patch('src.network_scanner.scanner.AdvancedNetworkScanner.enhanced_arp_scan')
    def test_behavioral_analysis(self, mock_scan):
        scanner = AdvancedNetworkScanner()
        
        # Configurer des appareils connus
        scanner.known_devices = {
            "00:11:22:33:44:55": {'first_seen': '2023-01-01', 'connection_count': 5},
            "00:11:22:33:44:56": {'first_seen': '2023-01-01', 'connection_count': 3}
        }
        
        # Simuler un scan avec un nouvel appareil et un appareil manquant
        mock_device = MagicMock()
        mock_device.mac = "00:11:22:33:44:57"
        mock_scan.return_value = [mock_device]
        
        with self.assertLogs('network_scanner', level='INFO') as cm:
            scanner.behavioral_analysis(mock_scan.return_value)
            self.assertTrue(any("Nouvel appareil détecté" in log for log in cm.output))
            self.assertTrue(any("Appareil disparu" in log for log in cm.output))

class TestDevice(unittest.TestCase):
    def test_device_creation(self):
        device = Device(
            ip="192.168.1.1",
            mac="00:11:22:33:44:55",
            vendor="Test Vendor",
            hostname="test.device"
        )
        
        self.assertEqual(device.ip, "192.168.1.1")
        self.assertEqual(device.mac, "00:11:22:33:44:55")
        self.assertEqual(device.vendor, "Test Vendor")
        self.assertEqual(device.hostname, "test.device")
        self.assertFalse(device.is_authorized)
        self.assertFalse(device.is_blocked)
        
    def test_to_dict(self):
        device = Device(
            ip="192.168.1.1",
            mac="00:11:22:33:44:55",
            vendor="Test Vendor",
            hostname="test.device"
        )
        
        device_dict = device.to_dict()
        self.assertEqual(device_dict['ip'], "192.168.1.1")
        self.assertEqual(device_dict['mac'], "00:11:22:33:44:55")
        self.assertEqual(device_dict['vendor'], "Test Vendor")
        self.assertEqual(device_dict['hostname'], "test.device")

if __name__ == '__main__':
    unittest.main()