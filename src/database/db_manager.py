import sqlite3
import json
from pathlib import Path
from src.utils.constants import DB_NAME

class DatabaseManager:
    def __init__(self):
        self.db_path = Path(__file__).parent.parent.parent / DB_NAME
        self.connection = None

    def initialize_db(self):
        """Initialise la base de données"""
        self.connection = sqlite3.connect(self.db_path)
        cursor = self.connection.cursor()
        
        # Table des appareils
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            mac TEXT PRIMARY KEY,
            ip TEXT,
            vendor TEXT,
            hostname TEXT,
            is_authorized INTEGER DEFAULT 0,
            is_blocked INTEGER DEFAULT 0,
            notes TEXT,
            first_seen TEXT,
            last_seen TEXT
        )
        ''')
        
        # Table des paramètres
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        ''')
        
        self.connection.commit()

    def save_devices(self, devices):
        """Sauvegarde les appareils dans la base de données"""
        cursor = self.connection.cursor()
        
        for device in devices:
            cursor.execute('''
            INSERT OR REPLACE INTO devices 
            (mac, ip, vendor, hostname, is_authorized, is_blocked, notes, last_seen)
            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
            ''', (
                device['mac'],
                device['ip'],
                device['vendor'],
                device['hostname'],
                int(device.get('is_authorized', False)),
                int(device.get('is_blocked', False)),
                device.get('notes', '')
            ))
        
        self.connection.commit()

    def load_devices(self):
        """Charge les appareils depuis la base de données"""
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM devices')
        columns = [column[0] for column in cursor.description]
        devices = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return devices

    def load_settings(self):
        """Charge les paramètres depuis la base de données"""
        cursor = self.connection.cursor()
        cursor.execute('SELECT key, value FROM settings')
        settings = {row[0]: row[1] for row in cursor.fetchall()}
        return settings

    def save_setting(self, key, value):
        """Sauvegarde un paramètre"""
        cursor = self.connection.cursor()
        cursor.execute('''
        INSERT OR REPLACE INTO settings (key, value)
        VALUES (?, ?)
        ''', (key, value))
        self.connection.commit()

    def __del__(self):
        if self.connection:
            self.connection.close()