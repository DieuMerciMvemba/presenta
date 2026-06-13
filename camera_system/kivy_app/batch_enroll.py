"""
Script d'enrôlement automatique pour toutes les personnes dans le dossier Dataset
Groupe les images par personne et utilise la logique d'enrôlement existante
Sauvegarde automatique dans MySQL après l'enrôlement FAISS
"""

import os
import sys
import re
from collections import defaultdict

# Ajouter le dossier parent au path pour importer les modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from enroll import enroll_student
from vector_db import LocalVectorDB
from services.mysql_service import MySQLService


def extract_person_name(filename):
    """
    Extrait le nom de la personne à partir du nom du fichier
    Gère différents formats de noms de fichiers
    """
    # Supprimer l'extension
    name = os.path.splitext(filename)[0]
    
    # Supprimer les numéros et suffixes comme " 2", " 2(1)", etc.
    name = re.sub(r'\s*\d+(\(\d+\))?$', '', name)
    
    # Supprimer les timestamps (format: _YYYYMMDD_HHMMSS)
    name = re.sub(r'_\d{8}_\d{6}$', '', name)
    
    # Nettoyer les espaces et mettre en majuscule la première lettre
    name = name.strip()
    name = name.capitalize()
    
    return name


def group_images_by_person(dataset_path):
    """
    Groupe les images par personne basé sur le nom du fichier
    """
    person_images = defaultdict(list)
    
    for filename in os.listdir(dataset_path):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            person_name = extract_person_name(filename)
            image_path = os.path.join(dataset_path, filename)
            person_images[person_name].append(image_path)
    
    return person_images


def generate_matricule(person_name, index):
    """
    Génère un matricule unique pour la personne
    """
    # Utiliser les 3 premières lettres du nom + un index
    name_prefix = person_name[:3].upper()
    matricule = f"UCC2026{index:03d}"
    return matricule


def batch_enroll(dataset_path):
    """
    Enrôle toutes les personnes dans le dossier Dataset
    Sauvegarde automatiquement dans MySQL après l'enrôlement FAISS
    """
    print("=" * 80)
    print("SCRIPT D'ENRÔLEMENT AUTOMATIQUE - DATASET")
    print("=" * 80)
    
    # Vérifier que le dossier Dataset existe
    if not os.path.exists(dataset_path):
        print(f"❌ Erreur: Le dossier Dataset n'existe pas: {dataset_path}")
        return
    
    # Grouper les images par personne
    person_images = group_images_by_person(dataset_path)
    
    print(f"\n📊 Analyse du dossier Dataset:")
    print(f"   - Nombre total de personnes: {len(person_images)}")
    print(f"   - Nombre total d'images: {sum(len(images) for images in person_images.values())}")
    
    # Afficher les personnes trouvées
    print(f"\n👥 Personnes détectées:")
    for i, (person_name, images) in enumerate(person_images.items(), 1):
        print(f"   {i}. {person_name}: {len(images)} image(s)")
    
    print(f"\n🚀 Début de l'enrôlement...")
    print("=" * 80)
    
    # Initialiser les bases de données
    db = LocalVectorDB()
    db_service = MySQLService(password='admin123')
    
    success_count = 0
    error_count = 0
    mysql_success_count = 0
    
    # Enrôler chaque personne
    for i, (person_name, images) in enumerate(person_images.items(), 1):
        try:
            print(f"\n[{i}/{len(person_images)}] Enrôlement de: {person_name}")
            print(f"   Images: {len(images)}")
            
            # Générer un matricule
            matricule = generate_matricule(person_name, i)
            print(f"   Matricule: {matricule}")
            
            # Utiliser le nom comme prénom (peut être modifié manuellement)
            nom = person_name
            prenom = ""  # Vide car on n'a pas séparé nom/prénom
            
            # ÉTAPE 1: Enrôler dans FAISS
            enroll_student(matricule, nom, prenom, images)
            print(f"   ✅ Enrôlement FAISS réussi")
            
            # ÉTAPE 2: Sauvegarder dans MySQL
            try:
                # Sauvegarder dans MySQL
                db_service.insert_student(
                    matricule=matricule,
                    nom=nom,
                    prenom=prenom,
                    email="",  # Vide car non disponible
                    telephone=""  # Vide car non disponible
                )
                print(f"   ✅ Sauvegarde MySQL réussie")
                mysql_success_count += 1
            except Exception as mysql_error:
                print(f"   ⚠️ Erreur MySQL: {mysql_error}")
            
            success_count += 1
            
        except Exception as e:
            print(f"   ❌ Erreur lors de l'enrôlement: {e}")
            error_count += 1
    
    # Afficher le résumé
    print("\n" + "=" * 80)
    print("RÉSUMÉ DE L'ENRÔLEMENT")
    print("=" * 80)
    print(f"✅ Enrôlements FAISS réussis: {success_count}/{len(person_images)}")
    print(f"✅ Sauvegardes MySQL réussies: {mysql_success_count}/{len(person_images)}")
    print(f"❌ Erreurs: {error_count}/{len(person_images)}")
    print(f"📊 Total d'étudiants dans FAISS: {db.get_student_count()}")
    print(f"📊 Total d'étudiants dans MySQL: {db_service.get_student_count()}")
    print("=" * 80)


if __name__ == "__main__":
    # Chemin du dossier Dataset (au niveau supérieur de camera_system)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    dataset_path = os.path.join(project_root, "Dataset")
    
    # Exécuter l'enrôlement automatique
    batch_enroll(dataset_path)
