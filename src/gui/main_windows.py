from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QVBoxLayout, QWidget, 
                            QLabel, QPushButton, QTableWidget, QTableWidgetItem,
                            QHeaderView, QMessageBox, QSystemTrayIcon, QMenu,
                            QInputDialog, QAction, QStatusBar)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QIcon, QColor
from src.gui.device_list import AdvancedDeviceListWidget
from src.gui.network_graph import NetworkGraphWidget
from src.gui.alerts import AlertsWidget
import json
import os
import platform
from datetime import datetime

class AdvancedMainWindow(QMainWindow):
    def __init__(self, scanner, db):
        super().__init__()
        self.scanner = scanner
        self.db = db
        self.settings = {}
        self.alert_history = []
        self.setup_ui()
        self.load_settings()
        self.setup_tray_icon()
        
        # Configuration de la fenêtre
        self.setWindowTitle("Surveillance WiFi Avancée")
        self.setWindowIcon(QIcon(os.path.join("assets", "icon.png")))
        self.setGeometry(100, 100, 1000, 700)
        
        # Configuration du statut
        self.statusBar().showMessage("Prêt")
        self.update_status_timer = QTimer()
        self.update_status_timer.timeout.connect(self.update_status)
        self.update_status_timer.start(5000)
        
        # Premier scan
        self.scanner.start_continuous_monitoring(self.update_device_list)

    def setup_ui(self):
        # Création du widget central et layout principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Barre d'outils
        self.setup_toolbar()
        
        # Onglets principaux
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Onglet Tableau de bord
        self.setup_dashboard_tab()
        
        # Onglet Appareils
        self.device_tab = AdvancedDeviceListWidget(self.scanner, self.db)
        self.tabs.addTab(self.device_tab, "Appareils")
        
        # Onglet Graphique réseau
        self.graph_tab = NetworkGraphWidget(self.scanner)
        self.tabs.addTab(self.graph_tab, "Topologie")
        
        # Onglet Alertes
        self.alerts_tab = AlertsWidget()
        self.tabs.addTab(self.alerts_tab, "Alertes")
        
        # Onglet Paramètres
        self.setup_settings_tab()

    def setup_toolbar(self):
        """Configure la barre d'outils avec des actions rapides"""
        toolbar = self.addToolBar("Actions")
        toolbar.setIconSize(QSize(32, 32))
        
        # Actions
        scan_action = QAction(QIcon(os.path.join("assets", "scan.png")), "Scan maintenant", self)
        scan_action.triggered.connect(self.manual_scan)
        toolbar.addAction(scan_action)
        
        block_action = QAction(QIcon(os.path.join("assets", "block.png")), "Bloquer un appareil", self)
        block_action.triggered.connect(self.show_block_dialog)
        toolbar.addAction(block_action)
        
        toolbar.addSeparator()
        
        log_action = QAction(QIcon(os.path.join("assets", "logs.png")), "Voir les logs", self)
        log_action.triggered.connect(self.show_logs)
        toolbar.addAction(log_action)
        
        help_action = QAction(QIcon(os.path.join("assets", "help.png")), "Aide", self)
        help_action.triggered.connect(self.show_help)
        toolbar.addAction(help_action)

    def setup_dashboard_tab(self):
        """Configure l'onglet tableau de bord avec des statistiques"""
        dashboard_tab = QWidget()
        layout = QVBoxLayout()
        dashboard_tab.setLayout(layout)
        
        # Statistiques en temps réel
        stats_widget = QWidget()
        stats_layout = QVBoxLayout()
        stats_widget.setLayout(stats_layout)
        
        self.stats_label = QLabel("Statistiques du réseau en temps réel")
        stats_layout.addWidget(self.stats_label)
        
        # Widgets visuels
        self.device_count_label = QLabel("Appareils connectés: 0")
        stats_layout.addWidget(self.device_count_label)
        
        self.threat_level_label = QLabel("Niveau de menace: Faible")
        stats_layout.addWidget(self.threat_level_label)
        
        layout.addWidget(stats_widget)
        self.tabs.addTab(dashboard_tab, "Tableau de bord")

    def setup_settings_tab(self):
        """Configure l'onglet paramètres"""
        settings_tab = QWidget()
        layout = QVBoxLayout()
        settings_tab.setLayout(layout)
        
        # Section scan
        scan_group = QWidget()
        scan_layout = QVBoxLayout()
        scan_group.setLayout(scan_layout)
        
        scan_layout.addWidget(QLabel("Paramètres de scan:"))
        self.scan_interval_input = QSpinBox()
        self.scan_interval_input.setRange(5, 3600)
        self.scan_interval_input.setValue(self.scanner.update_interval)
        self.scan_interval_input.valueChanged.connect(self.update_scan_interval)
        scan_layout.addWidget(QLabel("Intervalle de scan (secondes):"))
        scan_layout.addWidget(self.scan_interval_input)
        
        layout.addWidget(scan_group)
        self.tabs.addTab(settings_tab, "Paramètres")

    def setup_tray_icon(self):
        """Configure l'icône de la barre des tâches"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
            
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(os.path.join("assets", "icon.png")))
        
        menu = QMenu()
        
        show_action = menu.addAction("Afficher")
        show_action.triggered.connect(self.show_normal)
        
        scan_action = menu.addAction("Scan maintenant")
        scan_action.triggered.connect(self.manual_scan)
        
        menu.addSeparator()
        
        quit_action = menu.addAction("Quitter")
        quit_action.triggered.connect(self.close)
        
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.tray_icon_activated)

    def update_device_list(self, devices):
        """Met à jour l'interface avec les nouveaux appareils détectés"""
        self.device_tab.update_device_list(devices)
        self.graph_tab.update_graph(devices)
        
        # Mise à jour des statistiques
        self.device_count_label.setText(f"Appareils connectés: {len(devices)}")
        
        # Détection des nouveaux appareils
        known_macs = {device['mac'] for device in self.db.load_devices()}
        new_devices = [d for d in devices if d.mac not in known_macs]
        
        if new_devices:
            self.handle_new_devices(new_devices)

    def handle_new_devices(self, new_devices):
        """Gère la détection de nouveaux appareils"""
        for device in new_devices:
            msg = f"Nouvel appareil détecté: {device.mac} ({device.vendor})"
            self.statusBar().showMessage(msg, 5000)
            self.alert_history.append({
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'message': msg,
                'device': device.to_dict(),
                'severity': 'warning'
            })
            
            self.alerts_tab.add_alert(msg, 'warning')
            
            # Notification système
            if hasattr(self, 'tray_icon'):
                self.tray_icon.showMessage(
                    "Nouvel appareil détecté",
                    msg,
                    QSystemTrayIcon.Warning,
                    5000
                )

    def update_status(self):
        """Met à jour la barre de statut avec des informations système"""
        status = f"Dernier scan: {datetime.now().strftime('%H:%M:%S')}"
        if platform.system() == "Linux":
            status += " | Mode: Admin" if os.geteuid() == 0 else " | Mode: Standard"
        self.statusBar().showMessage(status)

    def manual_scan(self):
        """Lance un scan manuel"""
        self.statusBar().showMessage("Scan en cours...")
        QApplication.processEvents()  # Force la mise à jour de l'interface
        devices = self.scanner.enhanced_arp_scan()
        self.update_device_list(devices)
        self.statusBar().showMessage("Scan terminé", 3000)

    def show_block_dialog(self):
        """Affiche la boîte de dialogue pour bloquer un appareil"""
        ip, ok = QInputDialog.getText(
            self, 
            "Bloquer un appareil",
            "Entrez l'adresse IP ou MAC à bloquer:"
        )
        
        if ok and ip:
            self.block_device(ip)

    def closeEvent(self, event):
        """Gère la fermeture de l'application"""
        self.scanner.stop_monitoring()
        self.save_settings()
        
        if hasattr(self, 'tray_icon'):
            self.tray_icon.hide()
            
        event.accept()