from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                            QHeaderView, QPushButton, QHBoxLayout, QLabel)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QIcon
from datetime import datetime
import json
import os

class AlertsWidget(QWidget):
    alert_triggered = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.alerts = []
        self.setup_ui()
        self.load_alerts()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Barre d'outils
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout()
        toolbar.setLayout(toolbar_layout)
        
        self.clear_btn = QPushButton("Effacer tout")
        self.clear_btn.setIcon(QIcon(os.path.join("assets", "clear.png")))
        self.clear_btn.clicked.connect(self.clear_alerts)
        toolbar_layout.addWidget(self.clear_btn)
        
        self.export_btn = QPushButton("Exporter")
        self.export_btn.setIcon(QIcon(os.path.join("assets", "export.png")))
        self.export_btn.clicked.connect(self.export_alerts)
        toolbar_layout.addWidget(self.export_btn)
        
        toolbar_layout.addStretch()
        self.alert_count = QLabel("0 alertes")
        toolbar_layout.addWidget(self.alert_count)
        
        layout.addWidget(toolbar)
        
        # Tableau des alertes
        self.alert_table = QTableWidget()
        self.alert_table.setColumnCount(5)
        self.alert_table.setHorizontalHeaderLabels([
            "Date/Heure", "Type", "Appareil", "Description", "Actions"
        ])
        self.alert_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.alert_table.verticalHeader().setVisible(False)
        self.alert_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.alert_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        layout.addWidget(self.alert_table)
        
    def add_alert(self, message, alert_type="info", device=None):
        """Ajoute une nouvelle alerte"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        alert = {
            "timestamp": timestamp,
            "type": alert_type,
            "message": message,
            "device": device.to_dict() if device else None
        }
        
        self.alerts.append(alert)
        self.update_alert_table()
        self.alert_triggered.emit(alert)
        self.save_alerts()
        
    def update_alert_table(self):
        """Met à jour le tableau des alertes"""
        self.alert_table.setRowCount(len(self.alerts))
        self.alert_count.setText(f"{len(self.alerts)} alertes")
        
        for row, alert in enumerate(reversed(self.alerts)):
            # Date/Heure
            time_item = QTableWidgetItem(alert['timestamp'])
            time_item.setData(Qt.UserRole, alert)
            
            # Type
            type_item = QTableWidgetItem(alert['type'].capitalize())
            
            # Appareil
            device_text = ""
            if alert['device']:
                device_text = f"{alert['device'].get('hostname', '')} ({alert['device'].get('ip', '')})"
            device_item = QTableWidgetItem(device_text)
            
            # Description
            desc_item = QTableWidgetItem(alert['message'])
            
            # Actions
            action_btn = QPushButton("Détails")
            action_btn.clicked.connect(lambda _, r=row: self.show_alert_details(r))
            
            # Ajout des éléments
            self.alert_table.setItem(row, 0, time_item)
            self.alert_table.setItem(row, 1, type_item)
            self.alert_table.setItem(row, 2, device_item)
            self.alert_table.setItem(row, 3, desc_item)
            self.alert_table.setCellWidget(row, 4, action_btn)
            
            # Coloration selon le type
            color = self.get_alert_color(alert['type'])
            for col in range(4):
                self.alert_table.item(row, col).setBackground(color)
                
    def get_alert_color(self, alert_type):
        """Retourne la couleur correspondant au type d'alerte"""
        colors = {
            'info': QColor(173, 216, 230),  # LightBlue
            'warning': QColor(255, 255, 153),  # LightYellow
            'critical': QColor(255, 182, 193),  # LightPink
            'new_device': QColor(144, 238, 144),  # LightGreen
            'intrusion': QColor(255, 160, 122)   # LightSalmon
        }
        return colors.get(alert_type, QColor(240, 240, 240))
        
    def show_alert_details(self, row):
        """Affiche les détails d'une alerte"""
        alert = self.alerts[len(self.alerts) - 1 - row]
        details = f"""
        <b>Date/Heure:</b> {alert['timestamp']}<br>
        <b>Type:</b> {alert['type']}<br>
        <b>Message:</b> {alert['message']}<br>
        """
        
        if alert['device']:
            details += f"""
            <br><b>Appareil concerné:</b><br>
            - IP: {alert['device'].get('ip', 'N/A')}<br>
            - MAC: {alert['device'].get('mac', 'N/A')}<br>
            - Fabricant: {alert['device'].get('vendor', 'Inconnu')}<br>
            - Nom d'hôte: {alert['device'].get('hostname', 'N/A')}<br>
            """
            
        self.details_dialog = AlertDetailsDialog(details)
        self.details_dialog.exec_()
        
    def clear_alerts(self):
        """Efface toutes les alertes"""
        self.alerts = []
        self.update_alert_table()
        self.save_alerts()
        
    def export_alerts(self):
        """Exporte les alertes au format JSON"""
        filename = f"wifi_alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(self.alerts, f, indent=2)
            
    def save_alerts(self):
        """Sauvegarde les alertes dans un fichier"""
        alert_file = os.path.join("data", "alerts.json")
        os.makedirs("data", exist_ok=True)
        with open(alert_file, 'w') as f:
            json.dump(self.alerts, f)
            
    def load_alerts(self):
        """Charge les alertes depuis un fichier"""
        alert_file = os.path.join("data", "alerts.json")
        if os.path.exists(alert_file):
            with open(alert_file, 'r') as f:
                self.alerts = json.load(f)
            self.update_alert_table()

class AlertDetailsDialog(QDialog):
    def __init__(self, content):
        super().__init__()
        self.setWindowTitle("Détails de l'alerte")
        self.setMinimumSize(400, 300)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        text = QTextEdit()
        text.setReadOnly(True)
        text.setHtml(content)
        layout.addWidget(text)
        
        close_btn = QPushButton("Fermer")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)