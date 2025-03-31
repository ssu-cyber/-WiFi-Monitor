from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from typing import List, Optional
from src.network_scanner.device import Device
from src.database.db_manager import DatabaseManager
from threading import Thread
import json

class RESTAPIServer:
    def __init__(self, scanner, db: DatabaseManager, port=8000):
        self.scanner = scanner
        self.db = db
        self.port = port
        self.app = FastAPI(title="Wifi Monitor API")
        self.setup_middleware()
        self.setup_routes()
        self.server_thread = None
        
        # Modèles Pydantic
        class DeviceModel(BaseModel):
            ip: str
            mac: str
            vendor: str
            hostname: str
            is_authorized: bool
            is_blocked: bool
            notes: Optional[str] = None
            
        self.DeviceModel = DeviceModel
        
    def setup_middleware(self):
        """Configure le middleware CORS"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
    def setup_routes(self):
        """Configure les routes de l'API"""
        
        @self.app.get("/devices", response_model=List[self.DeviceModel])
        async def get_devices():
            devices = self.db.load_devices()
            return devices
            
        @self.app.get("/devices/{mac}", response_model=self.DeviceModel)
        async def get_device(mac: str):
            devices = self.db.load_devices()
            for device in devices:
                if device['mac'] == mac:
                    return device
            raise HTTPException(status_code=404, detail="Device not found")
            
        @self.app.post("/devices/{mac}/block")
        async def block_device(mac: str):
            devices = self.db.load_devices()
            device = next((d for d in devices if d['mac'] == mac), None)
            
            if not device:
                raise HTTPException(status_code=404, detail="Device not found")
                
            # Mettre à jour dans la base de données
            device['is_blocked'] = True
            self.db.save_devices(devices)
            
            # Bloquer dans le firewall
            if hasattr(self.scanner, 'firewall'):
                self.scanner.firewall.block_device(device['ip'], device['mac'])
                
            return {"status": "success", "message": f"Device {mac} blocked"}
            
        @self.app.get("/scan")
        async def trigger_scan():
            devices = self.scanner.enhanced_arp_scan()
            return {"status": "success", "devices": [d.to_dict() for d in devices]}
            
        @self.app.get("/stats")
        async def get_stats():
            devices = self.db.load_devices()
            stats = {
                "total_devices": len(devices),
                "authorized": sum(1 for d in devices if d['is_authorized']),
                "blocked": sum(1 for d in devices if d['is_blocked']),
                "new_last_24h": 0  # Implémenter cette logique
            }
            return stats
            
    def start(self):
        """Démarre le serveur API dans un thread séparé"""
        if self.server_thread is None or not self.server_thread.is_alive():
            self.server_thread = Thread(
                target=lambda: uvicorn.run(
                    self.app, 
                    host="0.0.0.0", 
                    port=self.port,
                    log_level="info",
                    access_log=False
                ),
                daemon=True
            )
            self.server_thread.start()
            
    def stop(self):
        """Arrête le serveur API"""
        # Note: uvicorn ne fournit pas d'API propre pour s'arrêter
        # Dans un cas réel, il faudrait implémenter une méthode propre
        pass

# Intégration avec MainWindow
def setup_api_in_main(window):
    window.api_server = RESTAPIServer(window.scanner, window.db)
    window.api_server.start()
    
    # Ajouter un menu pour l'API
    api_menu = window.menuBar().addMenu("API")
    api_status_action = QAction(f"API: Port {window.api_server.port}", window)
    api_status_action.setEnabled(False)
    api_menu.addAction(api_status_action)