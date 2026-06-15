"""
Script pour initialiser les facultés et promotions UCC dans MySQL
Basé sur la configuration définie dans config.py
"""

import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import UCC_FACULTIES, UCC_PROMOTIONS
from services.mysql_service import MySQLService


def init_ucc_faculties_and_promotions():
    """Initialise les facultés et promotions UCC dans MySQL"""
    
    print("=" * 70)
    print("INITIALISATION DES DONNÉES UCC - FACULTÉS ET PROMOTIONS")
    print("=" * 70)
    
    # Connexion à MySQL
    mysql_service = MySQLService(
        host='localhost',
        database='ucc_face_recognition',
        user='root',
        password='admin123',
        port=3306
    )
    
    if not mysql_service.connect():
        print("❌ Impossible de se connecter à MySQL")
        return False
    
    print("✅ Connexion MySQL réussie")
    
    try:
        # Insérer les facultés
        print(f"\n📚 Insertion des {len(UCC_FACULTIES)} facultés UCC...")
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
                    # Insérer la faculté
                    mysql_service.cursor.execute(
                        "INSERT INTO faculties (nom, description) VALUES (%s, %s)",
                        (faculty_name, f"Faculté {faculty_name} de l'UCC")
                    )
                    mysql_service.connection.commit()
                    print(f"  ✅ Faculté insérée: {faculty_name} (ID: {i})")
            except Exception as e:
                print(f"  ❌ Erreur lors de l'insertion de {faculty_name}: {e}")
        
        # Insérer les promotions
        print(f"\n🎓 Insertion des {len(UCC_PROMOTIONS)} promotions UCC...")
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
        
        # Afficher le résumé
        print("\n" + "=" * 70)
        print("RÉSUMÉ")
        print("=" * 70)
        
        mysql_service.cursor.execute("SELECT COUNT(*) FROM faculties")
        faculty_count = mysql_service.cursor.fetchone()[0]
        print(f"Total facultés dans MySQL: {faculty_count}")
        
        mysql_service.cursor.execute("SELECT COUNT(*) FROM promotions")
        promotion_count = mysql_service.cursor.fetchone()[0]
        print(f"Total promotions dans MySQL: {promotion_count}")
        
        print("\n✅ Initialisation terminée avec succès !")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        mysql_service.disconnect()


if __name__ == "__main__":
    init_ucc_faculties_and_promotions()
