"""
Script d'initialisation de la base de données MySQL pour le système de reconnaissance faciale UCC
Crée la base de données et toutes les tables nécessaires
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.mysql_service import MySQLService
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
        print("  - students (étudiants)")
        print("  - faculties (facultés)")
        print("  - departments (départements)")
        print("  - courses (cours)")
        print("  - attendance (présences)")
        print("  - reports (rapports)")
        print("  - settings (paramètres)")
    else:
        print("❌ Erreur lors de la création des tables")
        mysql_service.disconnect()
        return False
    
    # Étape 4: Insérer des données de test
    print("\n🧪 Étape 4: Insertion de données de test...")
    
    # Insérer une faculté de test
    try:
        mysql_service.cursor.execute(
            "INSERT INTO faculties (nom, code, description) VALUES (%s, %s, %s)",
            ("Faculté des Sciences", "FAC_SCI", "Faculté des Sciences et Technologies")
        )
        mysql_service.connection.commit()
        print("✅ Faculté de test insérée")
    except Exception as e:
        print(f"⚠️ Faculté déjà existante ou erreur: {e}")
    
    # Insérer un département de test
    try:
        mysql_service.cursor.execute(
            "INSERT INTO departments (nom, code, faculte_id, description) VALUES (%s, %s, %s, %s)",
            ("Informatique", "DEPT_INFO", 1, "Département d'Informatique")
        )
        mysql_service.connection.commit()
        print("✅ Département de test inséré")
    except Exception as e:
        print(f"⚠️ Département déjà existant ou erreur: {e}")
    
    # Insérer un étudiant de test
    try:
        student_id = mysql_service.insert_student(
            matricule="UCC2024001",
            nom="Doe",
            prenom="John",
            email="john.doe@ucc.edu",
            telephone="+243123456789",
            faculte_id=1,
            departement_id=1,
            annee_etude=3
        )
        if student_id:
            print(f"✅ Étudiant de test inséré (ID: {student_id})")
        else:
            print("⚠️ Étudiant déjà existant ou erreur")
    except Exception as e:
        print(f"⚠️ Étudiant déjà existant ou erreur: {e}")
    
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
