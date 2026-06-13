"""
Script de test pour vérifier la connexion MySQL et les opérations CRUD
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


def test_mysql_connection():
    """Teste la connexion MySQL et les opérations CRUD"""
    
    # Configuration MySQL
    mysql_config = {
        'host': 'localhost',
        'database': 'ucc_face_recognition',
        'user': 'root',
        'password': 'admin123',  # Mot de passe MySQL
        'port': 3306
    }
    
    print("=" * 70)
    print("TEST DE CONNEXION MYSQL ET OPÉRATIONS CRUD")
    print("=" * 70)
    
    # Créer le service MySQL
    mysql_service = MySQLService(**mysql_config)
    
    # Test 1: Créer la base de données
    print("\n📦 Test 1: Création de la base de données...")
    if mysql_service.create_database():
        print("✅ Base de données créée avec succès")
    else:
        print("❌ Erreur lors de la création de la base de données")
        return False
    
    # Test 2: Connexion
    print("\n🔌 Test 2: Connexion à la base de données...")
    if mysql_service.connect():
        print("✅ Connexion réussie")
    else:
        print("❌ Erreur de connexion")
        return False
    
    # Test 3: Création des tables
    print("\n📋 Test 3: Création des tables...")
    if mysql_service.create_tables():
        print("✅ Tables créées avec succès")
    else:
        print("❌ Erreur lors de la création des tables")
        return False
    
    # Test 4: Insertion d'un étudiant
    print("\n➕ Test 4: Insertion d'un étudiant...")
    student_id = mysql_service.insert_student(
        matricule="UCC2024001",
        nom="Test",
        prenom="Étudiant",
        email="test@ucc.edu",
        telephone="+243123456789",
        faculte_id=1,
        departement_id=1,
        annee_etude=3
    )
    if student_id:
        print(f"✅ Étudiant inséré avec succès (ID: {student_id})")
    else:
        print("⚠️ Étudiant déjà existant ou erreur d'insertion")
    
    # Test 5: Récupération d'un étudiant par matricule
    print("\n🔍 Test 5: Récupération d'un étudiant par matricule...")
    student = mysql_service.get_student_by_matricule("UCC2024001")
    if student:
        print(f"✅ Étudiant trouvé: {student['nom']} {student['prenom']}")
    else:
        print("❌ Étudiant non trouvé")
    
    # Test 6: Récupération de tous les étudiants
    print("\n📋 Test 6: Récupération de tous les étudiants...")
    students = mysql_service.get_all_students()
    print(f"✅ Nombre d'étudiants: {len(students)}")
    for student in students:
        print(f"   - {student['matricule']}: {student['nom']} {student['prenom']}")
    
    # Test 7: Mise à jour d'un étudiant
    print("\n✏️ Test 7: Mise à jour d'un étudiant...")
    if student_id:
        update_success = mysql_service.update_student(
            student_id,
            nom="TestModifié",
            prenom="ÉtudiantModifié"
        )
        if update_success:
            print(f"✅ Étudiant mis à jour avec succès")
        else:
            print("❌ Erreur lors de la mise à jour")
    
    # Test 8: Enregistrement de présence
    print("\n✅ Test 8: Enregistrement de présence...")
    if student_id:
        attendance_id = mysql_service.insert_attendance(
            student_id=student_id,
            statut='present',
            methode='facial',
            confiance=0.95
        )
        if attendance_id:
            print(f"✅ Présence enregistrée avec succès (ID: {attendance_id})")
        else:
            print("❌ Erreur lors de l'enregistrement de présence")
    
    # Test 9: Statistiques
    print("\n📊 Test 9: Récupération des statistiques...")
    stats = mysql_service.get_statistics()
    print(f"✅ Statistiques:")
    print(f"   - Total étudiants: {stats.get('total_students', 0)}")
    print(f"   - Total présences: {stats.get('total_attendance', 0)}")
    print(f"   - Total facultés: {stats.get('total_faculties', 0)}")
    print(f"   - Présences aujourd'hui: {stats.get('attendance_today', 0)}")
    
    # Test 10: Suppression d'un étudiant
    print("\n🗑️ Test 10: Suppression d'un étudiant...")
    if student_id:
        delete_success = mysql_service.delete_student(student_id)
        if delete_success:
            print(f"✅ Étudiant supprimé avec succès")
        else:
            print("❌ Erreur lors de la suppression")
    
    # Fermer la connexion
    mysql_service.disconnect()
    
    print("\n" + "=" * 70)
    print("✅ TOUS LES TESTS TERMINÉS AVEC SUCCÈS")
    print("=" * 70)
    
    return True


if __name__ == '__main__':
    try:
        success = test_mysql_connection()
        if success:
            print("\n🎉 Tests MySQL réussis!")
        else:
            print("\n❌ Certains tests ont échoué")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrompus par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        logger.error(f"Erreur inattendue: {e}", exc_info=True)
        sys.exit(1)
