import subprocess
import platform
import os
import logging
from datetime import datetime
from threading import Lock

class AdvancedFirewallManager:
    def __init__(self):
        self.os_type = platform.system()
        self.rules_lock = Lock()
        self.setup_logging()
        self.backup_dir = "firewall_backups"
        os.makedirs(self.backup_dir, exist_ok=True)

    def setup_logging(self):
        """Configure le système de journalisation"""
        self.logger = logging.getLogger('firewall_manager')
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler('firewall.log')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def block_device(self, ip_address, mac_address=None, permanent=True):
        """Bloque un appareil avec différentes méthodes"""
        with self.rules_lock:
            try:
                # Méthode 1: Blocage par IP
                self._block_by_ip(ip_address)
                
                # Méthode 2: Blocage par MAC si disponible
                if mac_address:
                    self._block_by_mac(mac_address)
                
                # Méthode 3: Isolation réseau (pour les routeurs pris en charge)
                    self._isolate_device(ip_address, mac_address)
                
                if permanent:
                    self._save_rule(ip_address, mac_address)
                
                self.logger.info(f"Appareil bloqué - IP: {ip_address}, MAC: {mac_address}")
                return True
                
            except Exception as e:
                self.logger.error(f"Échec du blocage: {str(e)}")
                return False

    def _block_by_ip(self, ip_address):
        """Implémentation spécifique au système d'exploitation pour bloquer par IP"""
        if self.os_type == "Linux":
            # Blocage avec iptables
            subprocess.run(
                ["sudo", "iptables", "-A", "INPUT", "-s", ip_address, "-j", "DROP"],
                check=True
            )
            subprocess.run(
                ["sudo", "iptables", "-A", "OUTPUT", "-d", ip_address, "-j", "DROP"],
                check=True
            )
            
        elif self.os_type == "Windows":
            # Blocage avec le firewall Windows
            rule_name = f"Block_{ip_address}"
            subprocess.run(
                ["netsh", "advfirewall", "firewall", "add", "rule",
                f"name={rule_name}", "dir=in", "action=block",
                "remoteip="+ip_address, "protocol=any"],
                check=True
            )
            
        elif self.os_type == "Darwin":  # macOS
            subprocess.run(
                ["sudo", "pfctl", "-t", "blocked", "-T", "add", ip_address],
                check=True
            )

    def _block_by_mac(self, mac_address):
        """Bloque un appareil par son adresse MAC"""
        if self.os_type == "Linux":
            subprocess.run(
                ["sudo", "iptables", "-A", "INPUT", "-m", "mac", "--mac-source", 
                 mac_address, "-j", "DROP"],
                check=True
            )
            
        elif self.os_type == "Windows":
            # Windows nécessite des outils supplémentaires pour le blocage MAC
            try:
                subprocess.run(
                    ["arp", "-s", "192.168.1.1", mac_address],  # Exemple, à adapter
                    check=True
                )
            except:
                self.logger.warning("Le blocage MAC nécessite des outils supplémentaires sur Windows")

    def _isolate_device(self, ip_address, mac_address):
        """Isole l'appareil du réseau (nécessite un accès routeur)"""
        try:
            # Essayer de se connecter au routeur via API/SSH
            self._configure_router_acl(ip_address, mac_address)
        except Exception as e:
            self.logger.warning(f"Impossible d'isoler l'appareil via le routeur: {str(e)}")

    def _configure_router_acl(self, ip_address, mac_address):
        """Exemple pour les routeurs TP-Link"""
        # Ceci est un exemple simplifié - à adapter selon le modèle de routeur
        try:
            subprocess.run(
                ["ssh", "admin@router", f"configure terminal\n"
                 f"ip access-list extended BLOCK_DEVICE\n"
                 f"deny ip host {ip_address} any\n"
                 f"deny any host {ip_address}\n"
                 f"exit"],
                timeout=10
            )
            self.logger.info(f"Règle ACL appliquée sur le routeur pour {ip_address}")
        except:
            raise Exception("Échec de la configuration du routeur")

    def _save_rule(self, ip_address, mac_address=None):
        """Sauvegarde les règles pour persistance"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(self.backup_dir, f"rule_{timestamp}.bak")
        
        if self.os_type == "Linux":
            with open(backup_file, "w") as f:
                subprocess.run(["iptables-save"], stdout=f)
                
        elif self.os_type == "Windows":
            with open(backup_file, "w") as f:
                subprocess.run(["netsh", "advfirewall", "firewall", "show", "rule", "name=all"], stdout=f)

    def restore_rules(self):
        """Restaure les règles à partir de la sauvegarde"""
        if self.os_type == "Linux":
            latest_backup = self._get_latest_backup()
            if latest_backup:
                subprocess.run(["iptables-restore", "<", latest_backup], shell=True)
                
        elif self.os_type == "Windows":
            self.logger.info("La restauration sous Windows nécessite une reconfiguration manuelle")

    def _get_latest_backup(self):
        """Trouve la dernière sauvegarde disponible"""
        backups = [f for f in os.listdir(self.backup_dir) if f.endswith('.bak')]
        if not backups:
            return None
        backups.sort(reverse=True)
        return os.path.join(self.backup_dir, backups[0])

    def schedule_block_cleanup(self, ip_address, mac_address=None, hours=24):
        """Planifie la suppression automatique du blocage"""
        def cleanup():
            time.sleep(hours * 3600)
            self.unblock_device(ip_address, mac_address)
            
        Thread(target=cleanup, daemon=True).start()