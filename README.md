#### 🎯 **Pourquoi Cet Outil ?**  
- **Pédagogique** : Comprendre les **attaques réseau** (ARP Spoofing, intrusions)  
- **Pratique** : Apprendre à manipuler **Scapy, iptables/netsh, PyQt5**  
- **Modulable** : Architecture basée sur **plugins** pour ajouter des fonctionnalités  

---

### **Fonctionnalités Clés**  
| Fonctionnalité               | Utilité pour votre Formation          |  
|------------------------------|---------------------------------------|  
| **Scan ARP temps réel**       | Analyser les appareils connectés      |  
| **Détection d'intrusions**    | Identifier les MAC non autorisées     |  
| **Blocage dynamique**         | Apprendre les règles firewall (iptables/netsh) |  
| **API REST sécurisée (JWT)**  | Comprendre l'authentification web     |  
| **Analyse trafic (plugins)**  | Détecter des anomalies avec Python    |  

---

### **Cas d'Usage Pédagogiques**  
1. **TP Sécurité Réseau** :  
   - Étudier les **requêtes ARP** et leur vulnérabilité  
   - Simuler une attaque **MITM** et la contrer  

2. **Projet de Fin de Module** :  
   - Étendre l'outil avec un **plugin de détection d'attaques** (ex: DHCP Spoofing)  
   - Intégrer une **base de données** pour l'historique des scans  

3. **Préparation aux Certifications** :  
   - Manipuler des **outils pro** (Scapy, Wireshark, iptables)  
   - Comprendre les **logs de sécurité** et leur analyse  

---

### **Technologies Utilisées**  
- **Python 3** (avec typage statique pour la clarté)  
- **Scapy** : Analyse réseau avancée  
- **PyQt5** : Interface graphique moderne  
- **Flask/JWT** : API sécurisée  
- **Docker** : Déploiement simplifié  

---

### **Comment Commencer ?  
1. **Cloner le dépôt** :  
   ```bash
   git clone https://github.com/ssu-cyber/WiFi-Monitor.git
   cd wiFi-Monitor
   ```

2. **Installer les dépendances** :  
   ```bash
   pip install -r requirements.txt
   ```

3. **Lancer l'application** :  
   ```bash
   python main.py
   ```

---

### **Compétences Acquises**  
✅ **Analyse réseau** avec Scapy  
✅ **Gestion des firewall** (Linux/Windows)  
✅ **Développement sécurisé** (JWT, chiffrement)  
✅ **Automatisation** (scripts Bash, CI/CD)  

---

**Idéal pour** :  
- **Prototypes de sécurité**  
- **Apprentissage actif des réseaux**  
- **Préparation aux pentests**  

Un outil **par les étudiants, pour les étudiants** ! 🎓🔒  

> *"WiFi Monitor  m'a permis de comprendre en pratique ce qu'on voyait en cours sur les attaques réseau."*  
> — Étudiant en cybersécurité, Université ESA


## L'architecture du programme du projet

wifi-monitor/
├── .gitignore
├── README.md
├── requirements.txt
├── config.json
├── main.py
├── assets/
│   ├── icons/
│   │   ├── scan.png
│   │   └── block.png
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── application.py
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── network/
│   │   │   ├── scanner.py
│   │   │   └── device.py
│   │   └── security/
│   │       ├── firewall.py
│   │       └── alert_manager.py
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── main_window.py
│   │   ├── components/
│   │   │   ├── device_table.py
│   │   │   └── toolbar.py
│   │   └── styles/
│   │       └── dark_theme.css
│   ├── api/
│   │   ├── __init__.py
│   │   ├── rest_api.py
│   │   └── websocket.py
│   ├── plugins/
│   │   ├── __init__.py
│   │   ├── plugin_manager.py
│   │   └── examples/
│   │       ├── traffic_analyzer.py
│   │       └── intrusion_detector.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── helpers.py
│   │   ├── logger.py
│   │   └── constants.py
│   └── i18n/
│       ├── __init__.py
│       ├── en.json
│       └── fr.json
├── tests/
│   ├── __init__.py
│   ├── test_network.py
│   └── test_security.py
└── scripts/
    ├── install.sh
    └── deploy.sh