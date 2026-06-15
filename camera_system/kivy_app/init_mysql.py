"""
Script d'initialisation de la base de données MySQL pour le système de reconnaissance faciale UCC
Crée la base de données et toutes les tables nécessaires
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Assurer le support des caractères UTF-8 (emojis) sur la console Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from services.mysql_service import MySQLService
from config import UCC_FACULTIES, UCC_PROMOTIONS
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def init_mysql_database():
    """Initialise la base de données MySQL et les tables"""
    
    # Configuration MySQL - À modifier selon votre installation
    mysql_config = {
        'host': 'localhost',
        'database': 'ucc_face_recognition',
        'user': 'root',
        'password': 'admin123',  # Mot de passe MySQL
        'port': 3306
    }
    
    print("=" * 70)
    print("INITIALISATION DE LA BASE DE DONNÉES MYSQL - UCC")
    print("=" * 70)
    print(f"Hôte: {mysql_config['host']}:{mysql_config['port']}")
    print(f"Base de données: {mysql_config['database']}")
    print(f"Utilisateur: {mysql_config['user']}")
    print("=" * 70)
    
    # Créer le service MySQL
    mysql_service = MySQLService(**mysql_config)
    
    # Étape 1: Créer la base de données
    print("\n📦 Étape 1: Création de la base de données...")
    if mysql_service.create_database():
        print("✅ Base de données créée avec succès")
    else:
        print("❌ Erreur lors de la création de la base de données")
        return False
    
    # Étape 2: Se connecter à la base de données
    print("\n🔌 Étape 2: Connexion à la base de données...")
    if mysql_service.connect():
        print("✅ Connexion réussie")
    else:
        print("❌ Erreur de connexion")
        return False
    
    # Étape 3: Créer les tables
    print("\n📋 Étape 3: Création des tables...")
    if mysql_service.create_tables():
        print("✅ Tables créées avec succès")
        print("\nTables créées:")
        print("  - users (utilisateurs/admin)")
        print("  - faculties (facultés)")
        print("  - promotions (promotions)")
        print("  - students (étudiants)")
        print("  - attendance (présences)")
        print("  - reports (rapports)")
        print("  - settings (paramètres)")
    else:
        print("❌ Erreur lors de la création des tables")
        mysql_service.disconnect()
        return False
    
    # Étape 4: Insérer les facultés et promotions UCC depuis la configuration
    print("\n📚 Étape 4: Insertion des facultés et promotions UCC...")
    
    # Insérer les facultés UCC
    for i, faculty_name in enumerate(UCC_FACULTIES, 1):
        try:
            # Vérifier si la faculté existe déjà
            mysql_service.cursor.execute(
                "SELECT id FROM faculties WHERE nom = %s",
                (faculty_name,)
            )
            existing = mysql_service.cursor.fetchone()
            
            if existing:
                print(f"  ⚠️ Faculté déjà existante: {faculty_name} (ID: {existing[0]})")
            else:
                # Générer un code unique à partir du nom (ex: "Faculté de Médecine" -> "FAC_MED")
                # Extraire les mots clés après "Faculté de" ou "Faculté des"
                words = faculty_name.replace("Faculté de ", "").replace("Faculté des ", "").replace("Faculté d'", "").split()
                # Prendre les premières lettres de chaque mot clé
                code_parts = [word[:3].upper() for word in words if len(word) > 2]
                code = "FAC_" + "".join(code_parts)
                # Si le code est trop court ou vide, utiliser l'index
                if len(code) <= 4:
                    code = f"FAC_{i:02d}"
                
                # Insérer la faculté avec le code
                mysql_service.cursor.execute(
                    "INSERT INTO faculties (nom, code, description) VALUES (%s, %s, %s)",
                    (faculty_name, code, f"Faculté {faculty_name} de l'UCC")
                )
                mysql_service.connection.commit()
                print(f"  ✅ Faculté insérée: {faculty_name} (Code: {code}, ID: {i})")
        except Exception as e:
            print(f"  ❌ Erreur lors de l'insertion de {faculty_name}: {e}")
    
    # Insérer les promotions UCC
    for i, promotion_name in enumerate(UCC_PROMOTIONS, 1):
        try:
            # Vérifier si la promotion existe déjà
            mysql_service.cursor.execute(
                "SELECT id FROM promotions WHERE nom = %s",
                (promotion_name,)
            )
            existing = mysql_service.cursor.fetchone()
            
            if existing:
                print(f"  ⚠️ Promotion déjà existante: {promotion_name} (ID: {existing[0]})")
            else:
                # Insérer la promotion
                code = promotion_name  # L1, L2, etc.
                mysql_service.cursor.execute(
                    "INSERT INTO promotions (nom, code, description) VALUES (%s, %s, %s)",
                    (promotion_name, code, f"Promotion {promotion_name} du système LMD")
                )
                mysql_service.connection.commit()
                print(f"  ✅ Promotion insérée: {promotion_name} (ID: {i})")
        except Exception as e:
            print(f"  ❌ Erreur lors de l'insertion de {promotion_name}: {e}")
    
    # Étape 5: Insertion des paramètres système par défaut
    print("\n⚙️ Étape 5: Insertion des paramètres par défaut...")
    default_settings = [
        ('threshold', '0.5', 'Seuil de similarité cosinus pour la reconnaissance faciale (0.0 à 1.0)'),
        ('spoof_threshold', '0.85', 'Seuil de vivacité pour l\'anti-spoofing (0.0 à 1.0)'),
        ('anti_spoof_enabled', '0', 'Activer (1) ou désactiver (0) l\'anti-spoofing (vivacité)'),
        ('camera_index', '0', 'Index de la caméra par défaut (0, 1, 2...)'),
        ('resolution', '"1280x720"', 'Résolution de la caméra ("640x480", "1280x720"...)'),
        ('session_duration', '60', 'Durée par défaut d\'une session de pointage en secondes'),
        ('attendance_rules', '{"late_time_limit": "08:00", "enable_auto_late_detection": true, "enable_daily_duplicate_check": true, "enable_auto_absence_calculation": true}', 'Règles de présence et retard au format JSON')
    ]
    
    for cle, valeur, description in default_settings:
        try:
            if mysql_service.save_setting(cle, valeur, description):
                print(f"  ✅ Paramètre initialisé: {cle} = {valeur}")
            else:
                print(f"  ❌ Échec de l'initialisation du paramètre: {cle}")
        except Exception as e:
            print(f"  ❌ Erreur lors de l'insertion du paramètre {cle}: {e}")
            
    # Fermer la connexion 
    mysql_service.disconnect()
    
    print("\n" + "=" * 70)
    print("✅ INITIALISATION TERMINÉE AVEC SUCCÈS")
    print("=" * 70)
    print("\nLa base de données MySQL est prête à être utilisée.")
    print("Vous pouvez maintenant lancer l'application Kivy.")
    print("=" * 70)
    
    return True


if __name__ == '__main__':
    try:
        success = init_mysql_database()
        if success:
            print("\n🎉 Base de données MySQL initialisée avec succès!")
        else:
            print("\n❌ Erreur lors de l'initialisation de la base de données")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Initialisation interrompue par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        logger.error(f"Erreur inattendue: {e}", exc_info=True)
        sys.exit(1)


"""
(learning) PS D:\cnn_sys> & C:/Users/dM/anaconda3/envs/learning/python.exe d:/cnn_sys/camera_system/kivy_app/init_mysql.py

======================================================================
INITIALISATION DE LA BASE DE DONNÉES MYSQL - UCC
======================================================================
Hôte: localhost:3306
Base de données: ucc_face_recognition
Utilisateur: root
======================================================================

✅ Tables créées avec succès

Tables créées:
  - users (utilisateurs/admin)
  - faculties (facultés)
  - promotions (promotions)
  - students (étudiants)
  - attendance (présences)
  - reports (rapports)
  - settings (paramètres)

📚 Étape 4: Insertion des facultés et promotions UCC...      
  ✅ Faculté insérée: Faculté de Médecine (Code: FAC_MÉD, ID: 1)
  ✅ Faculté insérée: Faculté de Droit (Code: FAC_DRO, ID: 2)
  ✅ Faculté insérée: Faculté de Droit Canonique (Code: FAC_DROCAN, ID: 3)
  ✅ Faculté insérée: Faculté d'Économie et Développement (Code: FAC_ÉCODÉV, ID: 4)
  ✅ Faculté insérée: Faculté de Théologie (Code: FAC_THÉ, ID: 5)
  ✅ Faculté insérée: Faculté de Philosophie (Code: FAC_PHI, ID: 6)
  ✅ Faculté insérée: Faculté des Communications Sociales (Code: FAC_COMSOC, ID: 7)
  ✅ Faculté insérée: Faculté d'Informatique (Code: FAC_INF, ID: 8)
  ✅ Faculté insérée: Faculté des Sciences Politiques (Code: FAC_SCIPOL, ID: 9)
  ✅ Promotion insérée: L1 (ID: 1)
  ✅ Promotion insérée: L2 (ID: 2)
  ✅ Promotion insérée: L3 (ID: 3)
  ✅ Promotion insérée: M1 (ID: 4)
  ✅ Promotion insérée: M2 (ID: 5)
2026-06-14 20:17:24,986 - services.mysql_service - INFO - Connexion MySQL fermée

======================================================================
✅ INITIALISATION TERMINÉE AVEC SUCCÈS
======================================================================

La base de données MySQL est prête à être utilisée.
Vous pouvez maintenant lancer l'application Kivy.
======================================================================

🎉 Base de données MySQL initialisée avec succès!
(learning) PS D:\cnn_sys> 
"""