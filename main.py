import sys
from PyQt5.QtWidgets import QApplication
from src.gui.main_window import MainWindow
from src.database.db_manager import DatabaseManager
from src.network_scanner.scanner import NetworkScanner

def main():
    # Initialisation de l'application
    app = QApplication(sys.argv)
    
    # Configuration de la base de données
    db = DatabaseManager()
    db.initialize_db()
    
    # Initialisation du scanner réseau
    scanner = NetworkScanner()
    
    # Création de l'interface
    window = MainWindow(scanner, db)
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()