"""
Script pour vider complètement la base de données et les fichiers FAISS
⚠️ ATTENTION: Ce script supprime TOUTES les données de manière irréversible
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.mysql_service import MySQLService
import shutil

def clear_all_data():
    """Vide complètement la base de données MySQL et les fichiers FAISS"""
    
    mysql_config = {
        'host': 'localhost',
        'database': 'ucc_face_recognition',
        'user': 'root',
        'password': 'admin123',
        'port': 3306
    }
    
    print("=" * 70)
    print("⚠️  NETTOYAGE COMPLET DE LA BASE DE DONNÉES - UCC")
    print("=" * 70)
    print(f"Hôte: {mysql_config['host']}:{mysql_config['port']}")
    print(f"Base de données: {mysql_config['database']}")
    print("=" * 70)
    print("⚠️  ATTENTION: Cette action est IRRÉVERSIBLE !")
    print("⚠️  Toutes les données seront supprimées:")
    print("   - Étudiants")
    print("   - Présences")
    print("   - Facultés")
    print("   - Promotions")
    print("   - Rapports")
    print("   - Paramètres")
    print("   - Fichiers FAISS (index et metadata)")
    print("=" * 70)
    
    # Confirmation de sécurité
    confirmation = input("\n🔒 Tapez 'CONFIRMER' pour continuer: ")
    if confirmation != "CONFIRMER":
        print("\n❌ Opération annulée.")
        return False
    
    print("\n🔄 Début du nettoyage...")
    
    try:
        # ÉTAPE 1: Vider les tables MySQL
        print("\n📋 ÉTAPE 1: Vidage des tables MySQL...")
        mysql_service = MySQLService(**mysql_config)
        
        if mysql_service.connect():
            print("✅ Connexion MySQL réussie")
            
            # Liste des tables à vider (dans l'ordre pour respecter les contraintes de clés étrangères)
            tables_to_clear = [
                'attendance',      # D'abord les enregistrements de présence
                'reports',        # Ensuite les rapports
                'students',       # Ensuite les étudiants
                'promotions',     # Ensuite les promotions
                'faculties',      # Ensuite les facultés
                'settings',       # Enfin les paramètres
                'users'           # Et les utilisateurs
            ]
            
            for table in tables_to_clear:
                try:
                    # Vérifier si la table existe
                    mysql_service.cursor.execute(f"SHOW TABLES LIKE '{table}'")
                    if mysql_service.cursor.fetchone():
                        # Compter avant suppression
                        mysql_service.cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
                        count_before = mysql_service.cursor.fetchone()[0]
                        
                        # Vider la table
                        mysql_service.cursor.execute(f"TRUNCATE TABLE `{table}`")
                        mysql_service.connection.commit()
                        
                        print(f"  ✅ Table '{table}' vidée ({count_before} enregistrements supprimés)")
                    else:
                        print(f"  ⚠️  Table '{table}' n'existe pas")
                except Exception as e:
                    print(f"  ❌ Erreur lors du vidage de '{table}': {e}")
            
            mysql_service.disconnect()
            print("\n✅ ÉTAPE 1: Tables MySQL vidées avec succès")
            
        else:
            print("❌ Erreur de connexion MySQL")
            return False
        
        # ÉTAPE 2: Supprimer les fichiers FAISS
        print("\n📋 ÉTAPE 2: Suppression des fichiers FAISS...")
        
        # Chemin vers les fichiers FAISS
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
        faiss_index = os.path.join(data_dir, 'facerec_faiss.index')
        metadata_file = os.path.join(data_dir, 'students_metadata.pkl')
        
        files_deleted = 0
        
        if os.path.exists(faiss_index):
            os.remove(faiss_index)
            print(f"  ✅ Fichier FAISS index supprimé: {faiss_index}")
            files_deleted += 1
        else:
            print(f"  ⚠️  Fichier FAISS index non trouvé: {faiss_index}")
        
        if os.path.exists(metadata_file):
            os.remove(metadata_file)
            print(f"  ✅ Fichier metadata supprimé: {metadata_file}")
            files_deleted += 1
        else:
            print(f"  ⚠️  Fichier metadata non trouvé: {metadata_file}")
        
        if files_deleted > 0:
            print(f"\n✅ ÉTAPE 2: {files_deleted} fichier(s) FAISS supprimé(s)")
        else:
            print("\n⚠️  ÉTAPE 2: Aucun fichier FAISS à supprimer")
        
        # ÉTAPE 3: Supprimer les rapports CSV
        print("\n📋 ÉTAPE 3: Suppression des rapports CSV...")
        
        reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'reports')
        csv_files_deleted = 0
        
        if os.path.exists(reports_dir):
            for filename in os.listdir(reports_dir):
                if filename.endswith('.csv'):
                    file_path = os.path.join(reports_dir, filename)
                    os.remove(file_path)
                    print(f"  ✅ Rapport CSV supprimé: {filename}")
                    csv_files_deleted += 1
            
            if csv_files_deleted > 0:
                print(f"\n✅ ÉTAPE 3: {csv_files_deleted} rapport(s) CSV supprimé(s)")
            else:
                print("\n⚠️  ÉTAPE 3: Aucun rapport CSV à supprimer")
        else:
            print("  ⚠️  Dossier reports non trouvé")
        
        print("\n" + "=" * 70)
        print("✅ NETTOYAGE TERMINÉ AVEC SUCCÈS")
        print("=" * 70)
        print("\n📊 Résumé:")
        print("  - Tables MySQL vidées")
        print("  - Fichiers FAISS supprimés")
        print("  - Rapports CSV supprimés")
        print("\n💡 Vous pouvez maintenant:")
        print("  1. Relancer init_mysql.py pour recréer les tables avec données de test")
        print("  2. Commencer un nouvel enrôlement d'étudiants")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur lors du nettoyage: {e}")
        import traceback
        traceback.print_exc()
        return False


def recreate_tables():
    """Recrée les tables vides après nettoyage"""
    
    mysql_config = {
        'host': 'localhost',
        'database': 'ucc_face_recognition',
        'user': 'root',
        'password': 'admin123',
        'port': 3306
    }
    
    print("\n🔄 Recréation des tables...")
    
    try:
        mysql_service = MySQLService(**mysql_config)
        
        if mysql_service.connect():
            if mysql_service.create_tables():
                print("✅ Tables recréées avec succès")
                mysql_service.disconnect()
                return True
            else:
                print("❌ Erreur lors de la création des tables")
                mysql_service.disconnect()
                return False
        else:
            print("❌ Erreur de connexion MySQL")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("🗑️  SCRIPT DE NETTOYAGE COMPLET - UCC FACE RECOGNITION")
    print("=" * 70)
    
    # Nettoyer toutes les données
    success = clear_all_data()
    
    if success:
        # Demander si l'utilisateur veut recréer les tables
        recreate = input("\n🔄 Voulez-vous recréer les tables vides? (o/n): ")
        if recreate.lower() in ['o', 'oui', 'y', 'yes']:
            recreate_tables()
        
        print("\n🎉 Opération terminée!")
    else:
        print("\n❌ Opération échouée")
        sys.exit(1)
