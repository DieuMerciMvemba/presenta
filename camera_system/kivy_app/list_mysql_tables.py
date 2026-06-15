"""
Script pour lister les tables MySQL actuelles dans la base de données ucc_face_recognition
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.mysql_service import MySQLService

def list_mysql_tables():
    """Liste toutes les tables de la base de données MySQL"""
    
    mysql_config = {
        'host': 'localhost',
        'database': 'ucc_face_recognition',
        'user': 'root',
        'password': 'admin123',
        'port': 3306
    }
    
    print("=" * 70)
    print("LISTE DES TABLES MYSQL - UCC FACE RECOGNITION")
    print("=" * 70)
    print(f"Hôte: {mysql_config['host']}:{mysql_config['port']}")
    print(f"Base de données: {mysql_config['database']}")
    print("=" * 70)
    
    try:
        mysql_service = MySQLService(**mysql_config)
        
        if mysql_service.connect():
            print("✅ Connexion réussie\n")
            
            # Lister les tables
            query = "SHOW TABLES"
            mysql_service.cursor.execute(query)
            tables = mysql_service.cursor.fetchall()
            
            if tables:
                print(f"📋 Tables trouvées ({len(tables)}):")
                print("-" * 70)
                for i, (table_name,) in enumerate(tables, 1):
                    print(f"  {i}. {table_name}")
                    
                    # Obtenir le nombre de lignes
                    count_query = f"SELECT COUNT(*) FROM `{table_name}`"
                    mysql_service.cursor.execute(count_query)
                    count = mysql_service.cursor.fetchone()[0]
                    print(f"     Records: {count}")
                    
                    # Obtenir la structure de la table
                    describe_query = f"DESCRIBE `{table_name}`"
                    mysql_service.cursor.execute(describe_query)
                    columns = mysql_service.cursor.fetchall()
                    print(f"     Colonnes: {len(columns)}")
                    print(f"     Structure:")
                    for col in columns:
                        print(f"       - {col[0]} ({col[1]})")
                    print()
            else:
                print("⚠️ Aucune table trouvée dans la base de données")
            
            mysql_service.disconnect()
            
        else:
            print("❌ Erreur de connexion à la base de données")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
    
    print("=" * 70)

if __name__ == '__main__':
    list_mysql_tables()
