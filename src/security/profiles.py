import json
import os
from enum import Enum
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from datetime import datetime

class SecurityLevel(Enum):
    LOW = "Faible"
    MEDIUM = "Moyen"
    HIGH = "Élevé"
    PARANOID = "Paranoïaque"

@dataclass
class SecurityProfile:
    name: str
    level: SecurityLevel
    description: str
    scan_interval: int  # en secondes
    port_scan_enabled: bool
    arp_spoof_detection: bool
    auto_block_new_devices: bool
    notify_on_new_device: bool
    created_at: str = datetime.now().isoformat()
    updated_at: str = datetime.now().isoformat()
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict):
        return cls(**data)

class ProfileManager:
    def __init__(self):
        self.profiles_file = os.path.join("data", "security_profiles.json")
        self.profiles = self.load_profiles()
        self.setup_default_profiles()
        
    def setup_default_profiles(self):
        """Crée les profils par défaut s'ils n'existent pas"""
        default_profiles = [
            SecurityProfile(
                name="Domestique",
                level=SecurityLevel.LOW,
                description="Profil pour usage domestique - surveillance minimale",
                scan_interval=300,
                port_scan_enabled=False,
                arp_spoof_detection=False,
                auto_block_new_devices=False,
                notify_on_new_device=True
            ),
            SecurityProfile(
                name="Bureau",
                level=SecurityLevel.MEDIUM,
                description="Profil pour petit bureau - surveillance modérée",
                scan_interval=120,
                port_scan_enabled=True,
                arp_spoof_detection=True,
                auto_block_new_devices=False,
                notify_on_new_device=True
            ),
            SecurityProfile(
                name="Entreprise",
                level=SecurityLevel.HIGH,
                description="Profil pour environnement professionnel - sécurité renforcée",
                scan_interval=60,
                port_scan_enabled=True,
                arp_spoof_detection=True,
                auto_block_new_devices=True,
                notify_on_new_device=True
            ),
            SecurityProfile(
                name="Sensible",
                level=SecurityLevel.PARANOID,
                description="Profil pour données sensibles - sécurité maximale",
                scan_interval=30,
                port_scan_enabled=True,
                arp_spoof_detection=True,
                auto_block_new_devices=True,
                notify_on_new_device=True
            )
        ]
        
        # Ajouter les profils manquants
        for default_profile in default_profiles:
            if not any(p.name == default_profile.name for p in self.profiles):
                self.profiles.append(default_profile)
        
        self.save_profiles()
    
    def load_profiles(self) -> List[SecurityProfile]:
        """Charge les profils depuis le fichier"""
        os.makedirs("data", exist_ok=True)
        
        if os.path.exists(self.profiles_file):
            with open(self.profiles_file, 'r') as f:
                try:
                    profiles_data = json.load(f)
                    return [SecurityProfile.from_dict(p) for p in profiles_data]
                except json.JSONDecodeError:
                    return []
        return []
    
    def save_profiles(self):
        """Sauvegarde les profils dans le fichier"""
        with open(self.profiles_file, 'w') as f:
            json.dump([p.to_dict() for p in self.profiles], f, indent=2)
    
    def get_profile(self, name: str) -> Optional[SecurityProfile]:
        """Récupère un profil par son nom"""
        for profile in self.profiles:
            if profile.name == name:
                return profile
        return None
    
    def add_profile(self, profile: SecurityProfile):
        """Ajoute un nouveau profil"""
        if not self.get_profile(profile.name):
            self.profiles.append(profile)
            self.save_profiles()
    
    def update_profile(self, name: str, updated_profile: SecurityProfile):
        """Met à jour un profil existant"""
        for i, profile in enumerate(self.profiles):
            if profile.name == name:
                updated_profile.updated_at = datetime.now().isoformat()
                self.profiles[i] = updated_profile
                self.save_profiles()
                return True
        return False
    
    def delete_profile(self, name: str) -> bool:
        """Supprime un profil"""
        initial_count = len(self.profiles)
        self.profiles = [p for p in self.profiles if p.name != name]
        
        if len(self.profiles) < initial_count:
            self.save_profiles()
            return True
        return False
    
    def apply_to_scanner(self, profile_name: str, scanner) -> bool:
        """Applique les paramètres d'un profil au scanner"""
        profile = self.get_profile(profile_name)
        if not profile:
            return False
            
        scanner.update_interval = profile.scan_interval
        scanner.port_scan_enabled = profile.port_scan_enabled
        scanner.arp_spoof_detection = profile.arp_spoof_detection
        
        return True

# Exemple d'utilisation
if __name__ == "__main__":
    manager = ProfileManager()
    
    # Créer un nouveau profil
    new_profile = SecurityProfile(
        name="Test",
        level=SecurityLevel.MEDIUM,
        description="Profil de test",
        scan_interval=90,
        port_scan_enabled=True,
        arp_spoof_detection=False,
        auto_block_new_devices=False,
        notify_on_new_device=False
    )
    manager.add_profile(new_profile)
    
    # Appliquer un profil
    from src.network_scanner.scanner import AdvancedNetworkScanner
    scanner = AdvancedNetworkScanner()
    manager.apply_to_scanner("Bureau", scanner)
    
    print(f"Intervalle de scan: {scanner.update_interval}")
    print(f"Scan de ports activé: {scanner.port_scan_enabled}")