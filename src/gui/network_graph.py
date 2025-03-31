from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsTextItem
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QColor, QPen, QFont
import math
import networkx as nx
from src.network_scanner.device import Device

class NetworkGraphWidget(QGraphicsView):
    def __init__(self, scanner):
        super().__init__()
        self.scanner = scanner
        self.graph = nx.Graph()
        self.setup_ui()
        self.last_positions = {}

    def setup_ui(self):
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        
        # Configuration visuelle
        self.setBackgroundBrush(QColor(240, 240, 240))
        self.node_colors = {
            'router': QColor(65, 105, 225),  # RoyalBlue
            'default': QColor(100, 149, 237),  # CornflowerBlue
            'suspicious': QColor(220, 20, 60),  # Crimson
            'new': QColor(255, 165, 0)   # Orange
        }

    def update_graph(self, devices):
        """Met à jour le graphique avec les appareils actuels"""
        self.scene.clear()
        self.graph.clear()
        
        # Identifier le routeur (premier appareil)
        router_device = next((d for d in devices if d.ip == self.scanner.current_network['gateway']), None)
        
        # Créer les nœuds
        for device in devices:
            node_type = 'router' if device == router_device else 'default'
            if any(port in [21, 22, 23] for port in getattr(device, 'open_ports', [])):
                node_type = 'suspicious'
            elif device.mac not in self.last_positions:
                node_type = 'new'
                
            self.add_device_node(device, node_type)
        
        # Dessiner les connexions
        if router_device:
            for device in devices:
                if device != router_device:
                    self.draw_connection(router_device, device)
        
        # Mise en page automatique
        self.arrange_nodes(router_device)
        
    def add_device_node(self, device, node_type):
        """Ajoute un nœud pour un appareil"""
        color = self.node_colors.get(node_type, self.node_colors['default'])
        
        # Création du cercle
        node = QGraphicsEllipseItem(-30, -30, 60, 60)
        node.setBrush(color)
        node.setPen(QPen(Qt.black, 1))
        node.setZValue(1)
        
        # Texte (nom ou IP)
        text = QGraphicsTextItem(device.hostname if device.hostname != device.ip else device.ip)
        text.setFont(QFont("Arial", 8))
        text.setDefaultTextColor(Qt.white if color.lightness() < 150 else Qt.black)
        
        # Positionnement
        if device.mac in self.last_positions:
            pos = self.last_positions[device.mac]
        else:
            pos = QPointF(0, 0)
            
        node.setPos(pos)
        text.setPos(pos.x() - text.boundingRect().width()/2, pos.y() - 10)
        
        self.scene.addItem(node)
        self.scene.addItem(text)
        self.graph.add_node(device.mac, item=node, pos=pos)
        
    def draw_connection(self, device1, device2):
        """Dessine une connexion entre deux appareils"""
        if device1.mac in self.graph and device2.mac in self.graph:
            node1 = self.graph.nodes[device1.mac]
            node2 = self.graph.nodes[device2.mac]
            
            line = self.scene.addLine(
                node1['pos'].x(), node1['pos'].y(),
                node2['pos'].x(), node2['pos'].y(),
                QPen(QColor(150, 150, 150), 1)
            line.setZValue(0)
            
            self.graph.add_edge(device1.mac, device2.mac, item=line)
            
    def arrange_nodes(self, router_device):
        """Organise les nœuds automatiquement"""
        if not self.graph.nodes:
            return
            
        # Utiliser un layout en étoile si routeur détecté
        if router_device and router_device.mac in self.graph:
            center = self.graph.nodes[router_device.mac]['pos']
            devices = [n for n in self.graph.nodes if n != router_device.mac]
            
            for i, mac in enumerate(devices):
                angle = 2 * math.pi * i / len(devices)
                radius = 200
                x = center.x() + radius * math.cos(angle)
                y = center.y() + radius * math.sin(angle)
                
                self.graph.nodes[mac]['pos'] = QPointF(x, y)
                self.graph.nodes[mac]['item'].setPos(x, y)
                
                # Mettre à jour les connexions
                for _, _, data in self.graph.edges(data=True):
                    if 'item' in data:
                        self.scene.removeItem(data['item'])
                self.draw_connection(router_device, mac)
                
            self.last_positions = {mac: self.graph.nodes[mac]['pos'] for mac in self.graph.nodes}
            
        else:
            # Fallback: layout de printemps
            pos = nx.spring_layout(self.graph, scale=200)
            for mac, (x, y) in pos.items():
                self.graph.nodes[mac]['pos'] = QPointF(x, y)
                self.graph.nodes[mac]['item'].setPos(x, y)
                self.last_positions[mac] = QPointF(x, y)