"""
Configuration du système UCC Face Recognition
Charge les variables d'environnement depuis le fichier .env
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

class Config:
    """Configuration centralisée du système"""
    
    # Chemins du projet
    PROJECT_ROOT = os.getenv('PROJECT_ROOT', 'd:\\cnn_sys')
    CAMERA_SYSTEM_PATH = os.getenv('CAMERA_SYSTEM_PATH', 'd:\\cnn_sys\\camera_system')
    KIVY_APP_PATH = os.getenv('KIVY_APP_PATH', 'd:\\cnn_sys\\camera_system\\kivy_app')
    DATASET_PATH = os.getenv('DATASET_PATH', 'd:\\cnn_sys\\Dataset')
    DATA_PATH = os.getenv('DATA_PATH', 'd:\\cnn_sys\\camera_system\\data')
    CONFIG_PATH = os.getenv('CONFIG_PATH', 'd:\\cnn_sys\\camera_system\\config')
    REPORTS_PATH = os.getenv('REPORTS_PATH', 'd:\\cnn_sys\\reports')
    TEMP_CHARTS_PATH = os.getenv('TEMP_CHARTS_PATH', 'd:\\cnn_sys\\temp_charts')
    DOCS_PATH = os.getenv('DOCS_PATH', 'd:\\cnn_sys\\docs')
    
    # Configuration Conda
    CONDA_ENV_PATH = os.getenv('CONDA_ENV_PATH', '')
    CONDA_PYTHON_PATH = os.getenv('CONDA_PYTHON_PATH', '')
    
    # Configuration MySQL
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', '3306'))
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'ucc_face_recognition')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'admin123')
    
    # Configuration de l'application
    APP_NAME = os.getenv('APP_NAME', 'Système de Reconnaissance Faciale - UCC')
    APP_VERSION = os.getenv('APP_VERSION', '1.0.0')
    
    @classmethod
    def get_python_executable(cls):
        """Retourne le chemin de l'exécutable Python à utiliser"""
        if cls.CONDA_PYTHON_PATH and os.path.exists(cls.CONDA_PYTHON_PATH):
            return cls.CONDA_PYTHON_PATH
        return "python"
    
    @classmethod
    def get_enroll_script_path(cls):
        """Retourne le chemin du script enroll.py"""
        return os.path.join(cls.CAMERA_SYSTEM_PATH, 'enroll.py')
    
    @classmethod
    def get_settings_path(cls):
        """Retourne le chemin du fichier settings.json"""
        return os.path.join(cls.CONFIG_PATH, 'settings.json')


# Facultés et promotions de l'UCC (basé sur docs/ucc-fac-promotion.md)
UCC_FACULTIES = [
    "Faculté de Médecine",
    "Faculté de Droit",
    "Faculté de Droit Canonique",
    "Faculté d'Économie et Développement",
    "Faculté de Théologie",
    "Faculté de Philosophie",
    "Faculté des Communications Sociales",
    "Faculté d'Informatique",
    "Faculté des Sciences Politiques"
]

UCC_PROMOTIONS = [
    "L1",
    "L2",
    "L3",
    "M1",
    "M2"
]
