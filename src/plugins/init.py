import importlib
import os
import inspect
from typing import Dict, Type
from abc import ABC, abstractmethod
from pathlib import Path

class WifiMonitorPlugin(ABC):
    """Classe de base pour tous les plugins"""
    
    @classmethod
    @abstractmethod
    def get_name(cls) -> str:
        """Retourne le nom du plugin"""
        pass
        
    @abstractmethod
    def initialize(self, app_context: Dict):
        """Initialise le plugin avec le contexte de l'application"""
        pass
        
    @abstractmethod
    def on_device_detected(self, device):
        """Callback appelée quand un nouvel appareil est détecté"""
        pass
        
    @abstractmethod
    def on_alert_triggered(self, alert):
        """Callback appelée quand une alerte est déclenchée"""
        pass

class PluginManager:
    def __init__(self):
        self.plugins: Dict[str, WifiMonitorPlugin] = {}
        self.load_builtin_plugins()
        self.load_external_plugins()
        
    def load_builtin_plugins(self):
        """Charge les plugins intégrés"""
        builtin_plugins = [
            'traffic_analyzer',
            'vulnerability_scanner',
            'report_generator'
        ]
        
        for plugin_name in builtin_plugins:
            try:
                module = importlib.import_module(f'src.plugins.{plugin_name}')
                self._register_plugin(module)
            except ImportError as e:
                print(f"Failed to load builtin plugin {plugin_name}: {str(e)}")
                
    def load_external_plugins(self):
        """Charge les plugins externes depuis le dossier plugins/"""
        plugins_dir = Path("plugins")
        plugins_dir.mkdir(exist_ok=True)
        
        for item in plugins_dir.iterdir():
            if item.is_dir() or (item.is_file() and item.suffix == '.py' and item.name != '__init__.py'):
                try:
                    spec = importlib.util.spec_from_file_location(
                        f"plugins.{item.stem}", item)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    self._register_plugin(module)
                except Exception as e:
                    print(f"Failed to load plugin {item.name}: {str(e)}")
                    
    def _register_plugin(self, module):
        """Enregistre un plugin depuis un module"""
        for name, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and 
                issubclass(obj, WifiMonitorPlugin) and 
                obj != WifiMonitorPlugin):
                plugin_instance = obj()
                self.plugins[plugin_instance.get_name()] = plugin_instance
                
    def initialize_all(self, app_context: Dict):
        """Initialise tous les plugins"""
        for plugin in self.plugins.values():
            plugin.initialize(app_context)
            
    def notify_device_detected(self, device):
        """Notifie tous les plugins d'un nouvel appareil"""
        for plugin in self.plugins.values():
            plugin.on_device_detected(device)
            
    def notify_alert_triggered(self, alert):
        """Notifie tous les plugins d'une nouvelle alerte"""
        for plugin in self.plugins.values():
            plugin.on_alert_triggered(alert)

# Exemple de plugin intégré (src/plugins/traffic_analyzer.py)
class TrafficAnalyzerPlugin(WifiMonitorPlugin):
    @classmethod
    def get_name(cls) -> str:
        return "Traffic Analyzer"
        
    def initialize(self, app_context):
        self.scanner = app_context.get('scanner')
        self.db = app_context.get('db')
        print(f"[{self.get_name()}] Plugin initialized")
        
    def on_device_detected(self, device):
        if len(getattr(device, 'open_ports', [])) > 3:
            print(f"[{self.get_name()}] Device {device.ip} has multiple open ports")
            
    def on_alert_triggered(self, alert):
        if alert['type'] == 'intrusion':
            print(f"[{self.get_name()}] Intrusion alert detected")