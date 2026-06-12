"""
Service de surveillance de dossier pour les rapports
Détecte automatiquement les nouveaux fichiers de rapports déposés dans un dossier
"""

import os
import time
import threading
from pathlib import Path
from typing import Callable, List, Dict
import json
import csv
from datetime import datetime


class ReportWatcherService:
    """Service de surveillance de dossier pour charger automatiquement les rapports"""
    
    def __init__(self, watch_folder: str = "reports"):
        """
        Initialise le service de surveillance
        
        Args:
            watch_folder: Dossier à surveiller pour les rapports
        """
        self.watch_folder = Path(watch_folder)
        self.watch_folder.mkdir(parents=True, exist_ok=True)
        
        self.is_running = False
        self.watch_thread = None
        self.callbacks = []
        self.known_files = set()
        self.last_check_time = time.time()
        
        # Extensions de fichiers supportées
        self.supported_extensions = {'.csv', '.json', '.xlsx', '.xls'}
        
    def add_callback(self, callback: Callable[[str, Dict], None]):
        """
        Ajoute un callback appelé quand un nouveau fichier est détecté
        
        Args:
            callback: Fonction appelée avec (file_path, parsed_data)
        """
        self.callbacks.append(callback)
    
    def start_watching(self):
        """Démarre la surveillance du dossier"""
        if not self.is_running:
            self.is_running = True
            self.watch_thread = threading.Thread(target=self._watch_loop, daemon=True)
            self.watch_thread.start()
            print(f"📁 Surveillance du dossier démarrée: {self.watch_folder}")
    
    def stop_watching(self):
        """Arrête la surveillance du dossier"""
        self.is_running = False
        if self.watch_thread:
            self.watch_thread.join(timeout=2)
        print("📁 Surveillance du dossier arrêtée")
    
    def _watch_loop(self):
        """Boucle de surveillance du dossier"""
        while self.is_running:
            try:
                self._check_for_new_files()
                time.sleep(2)  # Vérifier toutes les 2 secondes
            except Exception as e:
                print(f"❌ Erreur dans la boucle de surveillance: {e}")
                time.sleep(5)
    
    def _check_for_new_files(self):
        """Vérifie si de nouveaux fichiers ont été ajoutés"""
        current_files = set()
        
        # Parcourir tous les fichiers supportés dans le dossier
        for file_path in self.watch_folder.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                current_files.add(str(file_path))
                
                # Vérifier si c'est un nouveau fichier
                if str(file_path) not in self.known_files:
                    print(f"📄 Nouveau fichier détecté: {file_path.name}")
                    
                    # Parser le fichier
                    parsed_data = self._parse_file(file_path)
                    
                    # Notifier les callbacks
                    for callback in self.callbacks:
                        try:
                            callback(str(file_path), parsed_data)
                        except Exception as e:
                            print(f"❌ Erreur dans le callback: {e}")
        
        # Mettre à jour les fichiers connus
        self.known_files = current_files
        self.last_check_time = time.time()
    
    def _parse_file(self, file_path: Path) -> Dict:
        """
        Parse un fichier de rapport selon son extension
        
        Args:
            file_path: Chemin du fichier à parser
            
        Returns:
            Dictionnaire contenant les données parsées
        """
        try:
            if file_path.suffix.lower() == '.csv':
                return self._parse_csv(file_path)
            elif file_path.suffix.lower() == '.json':
                return self._parse_json(file_path)
            elif file_path.suffix.lower() in {'.xlsx', '.xls'}:
                return self._parse_excel(file_path)
            else:
                return {'error': f'Extension non supportée: {file_path.suffix}'}
        except Exception as e:
            return {'error': f'Erreur de parsing: {str(e)}'}
    
    def _parse_csv(self, file_path: Path) -> Dict:
        """Parse un fichier CSV"""
        data = []
        headers = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)  # Première ligne = headers
            
            for row in reader:
                if row:  # Ignorer les lignes vides
                    data.append(dict(zip(headers, row)))
        
        return {
            'file_type': 'csv',
            'file_name': file_path.name,
            'headers': headers,
            'data': data,
            'row_count': len(data),
            'parsed_at': datetime.now().isoformat()
        }
    
    def _parse_json(self, file_path: Path) -> Dict:
        """Parse un fichier JSON"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return {
            'file_type': 'json',
            'file_name': file_path.name,
            'data': data,
            'parsed_at': datetime.now().isoformat()
        }
    
    def _parse_excel(self, file_path: Path) -> Dict:
        """Parse un fichier Excel (nécessite pandas/openpyxl)"""
        try:
            import pandas as pd
            
            # Lire le fichier Excel
            df = pd.read_excel(file_path)
            
            # Convertir en dictionnaire
            data = df.to_dict('records')
            headers = list(df.columns)
            
            return {
                'file_type': 'excel',
                'file_name': file_path.name,
                'headers': headers,
                'data': data,
                'row_count': len(data),
                'parsed_at': datetime.now().isoformat()
            }
        except ImportError:
            return {'error': 'pandas ou openpyxl non installé pour lire les fichiers Excel'}
        except Exception as e:
            return {'error': f'Erreur de lecture Excel: {str(e)}'}
    
    def get_existing_files(self) -> List[str]:
        """
        Retourne la liste des fichiers existants dans le dossier
        
        Returns:
            Liste des chemins de fichiers
        """
        files = []
        for file_path in self.watch_folder.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                files.append(str(file_path))
        return files
    
    def load_existing_files(self):
        """Charge tous les fichiers existants dans le dossier"""
        existing_files = self.get_existing_files()
        for file_path in existing_files:
            if file_path not in self.known_files:
                print(f"📄 Chargement du fichier existant: {Path(file_path).name}")
                parsed_data = self._parse_file(Path(file_path))
                for callback in self.callbacks:
                    try:
                        callback(file_path, parsed_data)
                    except Exception as e:
                        print(f"❌ Erreur dans le callback: {e}")
                self.known_files.add(file_path)
