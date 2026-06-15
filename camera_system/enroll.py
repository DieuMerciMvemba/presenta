"""
Application CLI pour la Phase d'Enrôlement du système de reconnaissance faciale.
Phase d'Enrôlement (Une seule fois par étudiant):
Photo d'identité ➔ MTCNN ➔ Alignement ➔ ArcFace ➔ Stockage dans le fichier FAISS (.index + .pkl)
"""

import argparse
import sys
import os
from datetime import datetime
import csv
import logging

from vector_db import LocalVectorDB
from pipeline import FacePipeline

# Import pour la sauvegarde MySQL
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from kivy_app.services.mysql_service import MySQLService
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    logger.warning("MySQL non disponible, seule la sauvegarde FAISS sera effectuée")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def enroll_student(matricule, nom, prenom, photo_paths, email=None, telephone=None, faculte_id=None, promotion_id=None):
    """
    Inscrit un nouvel étudiant dans le système avec support multi-photos.
    
    Phase d'Enrôlement: Photos multiples ➔ MTCNN ➔ Alignement ➔ ArcFace ➔ Embedding Moyen ➔ Stockage FAISS (.index + .pkl)
    
    Args:
        matricule (str): Matricule de l'étudiant
        nom (str): Nom de l'étudiant
        prenom (str): Prénom de l'étudiant
        photo_paths (str or list): Chemin vers la photo (single) ou liste de chemins (multi)
        email (str): Email de l'étudiant (optionnel)
        telephone (str): Téléphone de l'étudiant (optionnel)
        faculte_id (int): ID de la faculté (optionnel)
        promotion_id (int): ID de la promotion (optionnel)
    """
    logger.info("=" * 70)
    logger.info("PHASE D'ENRÔLEMENT D'ÉTUDIANT - UCC")
    logger.info("=" * 70)
    logger.info("Pipeline: Photos multiples ➔ MTCNN ➔ Alignement ➔ ArcFace ➔ Embedding Moyen ➔ Stockage FAISS")
    logger.info("=" * 70)
    
    # Gérer le cas d'une seule photo (string) ou plusieurs photos (liste)
    if isinstance(photo_paths, str):
        photo_paths = [photo_paths]
    
    # Vérifier que les fichiers existent
    for photo_path in photo_paths:
        if not os.path.exists(photo_path):
            logger.error(f"Le fichier photo n'existe pas: {photo_path}")
            sys.exit(1)
    
    try:
        # Initialiser la base de données
        db = LocalVectorDB()
        logger.info(f"Base de données chargée. Étudiants actuels: {db.get_student_count()}")
        
        # Initialiser le pipeline
        pipeline = FacePipeline()
        
        # ÉTAPE 1: Photos multiples - Déjà fournies
        logger.info(f"ÉTAPE 1: Photos chargées: {len(photo_paths)}")
        for i, path in enumerate(photo_paths, 1):
            logger.info(f"  Photo {i}: {path}")
        
        # ÉTAPE 2: MTCNN + Alignement + ArcFace - Extraction des embeddings
        logger.info("ÉTAPE 2: Extraction des embeddings depuis toutes les photos...")
        embeddings = pipeline.get_embeddings_from_multiple_paths(photo_paths)
        logger.info(f"ÉTAPE 2: {len(embeddings)} embeddings extraits")
        
        # ÉTAPE 3: Calcul de l'embedding moyen (automatique dans register_student)
        if len(embeddings) > 1:
            logger.info("ÉTAPE 3: Calcul de l'embedding moyen pour plus de robustesse")
        else:
            logger.info("ÉTAPE 3: Utilisation d'un seul embedding")
        
        # Obtenir le prochain ID
        student_id = db.get_next_id()
        
        # ÉTAPE 4: Stockage dans le fichier FAISS (.index + .pkl) avec embedding moyen
        logger.info("ÉTAPE 4: Stockage FAISS (.index + .pkl)")
        db.register_student(student_id, matricule, nom, prenom, embeddings)
        db.increment_id()
        
        logger.info("=" * 70)
        logger.info("INSCRIPTION RÉUSSIE!")
        logger.info(f"ID: {student_id}")
        logger.info(f"Matricule: {matricule}")
        logger.info(f"Nom: {nom}")
        logger.info(f"Prénom: {prenom}")
        logger.info(f"Photos utilisées: {len(embeddings)}")
        logger.info(f"Total étudiants: {db.get_student_count()}")
        logger.info("=" * 70)
        
        # Sauvegarde MySQL si les paramètres sont fournis
        if MYSQL_AVAILABLE and (faculte_id is not None or promotion_id is not None):
            logger.info("ÉTAPE 5: Sauvegarde dans MySQL...")
            try:
                mysql_service = MySQLService(
                    host='localhost',
                    database='ucc_face_recognition',
                    user='root',
                    password='admin123',
                    port=3306
                )
                
                if mysql_service.connect():
                    mysql_student_id = mysql_service.insert_student(
                        matricule=matricule,
                        nom=nom,
                        prenom=prenom,
                        email=email,
                        telephone=telephone,
                        faculte_id=faculte_id,
                        promotion_id=promotion_id
                    )
                    
                    if mysql_student_id:
                        logger.info(f"✅ Étudiant sauvegardé dans MySQL (ID: {mysql_student_id})")
                    else:
                        logger.warning("⚠️ Étudiant existe déjà dans MySQL")
                    
                    mysql_service.disconnect()
                else:
                    logger.warning("⚠️ Impossible de se connecter à MySQL")
                    
            except Exception as e:
                logger.error(f"❌ Erreur lors de la sauvegarde MySQL: {e}")
        elif MYSQL_AVAILABLE:
            logger.info("⚠️ Sauvegarde MySQL ignorée: faculte_id et promotion_id non fournis")
            logger.info("💡 Pour sauvegarder dans MySQL, utilisez --faculte-id et --promotion-id")
        
    except ValueError as e:
        logger.error(f"Erreur de validation: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Erreur lors de l'inscription: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def update_student_info(matricule, new_matricule=None, new_nom=None, new_prenom=None):
    """
    Met à jour les informations d'un étudiant existant.
    
    Args:
        matricule (str): Matricule actuel de l'étudiant
        new_matricule (str): Nouveau matricule (optionnel)
        new_nom (str): Nouveau nom (optionnel)
        new_prenom (str): Nouveau prénom (optionnel)
    """
    logger.info("=" * 70)
    logger.info("MISE À JOUR DES INFORMATIONS ÉTUDIANT - UCC")
    logger.info("=" * 70)
    
    try:
        # Initialiser la base de données
        db = LocalVectorDB()
        
        # Trouver l'étudiant par matricule
        student = db.find_student_by_matricule(matricule)
        
        if not student:
            logger.error(f"Étudiant avec matricule '{matricule}' non trouvé.")
            sys.exit(1)
        
        student_id = student['id']
        current_info = student['metadata']
        
        logger.info(f"Étudiant trouvé: ID={student_id}")
        logger.info(f"Informations actuelles:")
        logger.info(f"  Matricule: {current_info['matricule']}")
        logger.info(f"  Nom: {current_info['nom']}")
        logger.info(f"  Prénom: {current_info['prenom']}")
        
        # Mettre à jour les informations
        db.update_student_info(student_id, new_matricule, new_nom, new_prenom)
        
        logger.info("✅ Informations mises à jour avec succès !")
        logger.info(f"Nouvelles informations:")
        if new_matricule:
            logger.info(f"  Matricule: {new_matricule}")
        else:
            logger.info(f"  Matricule: {current_info['matricule']}")
        if new_nom:
            logger.info(f"  Nom: {new_nom}")
        else:
            logger.info(f"  Nom: {current_info['nom']}")
        if new_prenom:
            logger.info(f"  Prénom: {new_prenom}")
        else:
            logger.info(f"  Prénom: {current_info['prenom']}")
        
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def add_photos_to_student(matricule, photo_paths, replace=False):
    """
    Ajoute de nouvelles photos à un étudiant existant.
    
    Args:
        matricule (str): Matricule de l'étudiant
        photo_paths (list): Liste des chemins vers les nouvelles photos
        replace (bool): Si True, remplace toutes les photos; si False, ajoute aux existantes
    """
    logger.info("=" * 70)
    logger.info("AJOUT DE PHOTOS À UN ÉTUDIANT EXISTANT - UCC")
    logger.info("=" * 70)
    
    # Gérer le cas d'une seule photo
    if isinstance(photo_paths, str):
        photo_paths = [photo_paths]
    
    # Vérifier que les fichiers existent
    for photo_path in photo_paths:
        if not os.path.exists(photo_path):
            logger.error(f"Le fichier photo n'existe pas: {photo_path}")
            sys.exit(1)
    
    try:
        # Initialiser la base de données
        db = LocalVectorDB()
        
        # Trouver l'étudiant par matricule
        student = db.find_student_by_matricule(matricule)
        
        if not student:
            logger.error(f"Étudiant avec matricule '{matricule}' non trouvé.")
            sys.exit(1)
        
        student_id = student['id']
        current_info = student['metadata']
        
        logger.info(f"Étudiant trouvé: ID={student_id}")
        logger.info(f"Informations actuelles:")
        logger.info(f"  Matricule: {current_info['matricule']}")
        logger.info(f"  Nom: {current_info['nom']}")
        logger.info(f"  Prénom: {current_info['prenom']}")
        logger.info(f"  Photos actuelles: {current_info.get('num_photos', 'N/A')}")
        
        # Initialiser le pipeline
        logger.info("Initialisation du pipeline...")
        pipeline = FacePipeline()
        
        # Extraire les embeddings des nouvelles photos
        logger.info(f"Extraction des embeddings depuis {len(photo_paths)} nouvelles photos...")
        new_embeddings = pipeline.get_embeddings_from_multiple_paths(photo_paths)
        logger.info(f"{len(new_embeddings)} embeddings extraits")
        
        # Ajouter les photos
        mode = "remplacement" if replace else "ajout"
        logger.info(f"Mode: {mode} des photos")
        db.add_photos_to_student(student_id, new_embeddings, replace=replace)
        
        logger.info("✅ Photos ajoutées avec succès !")
        
        # Afficher les nouvelles informations
        updated_info = db.metadata[student_id]
        logger.info(f"Nouvelles informations:")
        logger.info(f"  Matricule: {updated_info['matricule']}")
        logger.info(f"  Nom: {updated_info['nom']}")
        logger.info(f"  Prénom: {updated_info['prenom']}")
        logger.info(f"  Photos totales: {updated_info['num_photos']}")
        
    except Exception as e:
        logger.error(f"Erreur lors de l'ajout des photos: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def check_attendance(group_photo_path, threshold=0.5):
    """
    Vérifie la présence des étudiants à partir d'une photo de groupe.
    
    Phase de Pointage: MTCNN (Multi-visages) ➔ Alignement ➔ ArcFace ➔ Recherche FAISS ➔ Marquage Présent
    
    Args:
        group_photo_path (str): Chemin vers la photo de groupe
        threshold (float): Seuil de similarité cosinus pour la correspondance (défaut: 0.5 - recommandé)
    """
    logger.info("=" * 70)
    logger.info("PHASE DE VÉRIFICATION DE PRÉSENCE - UCC")
    logger.info("=" * 70)
    logger.info("Pipeline: MTCNN (Multi-visages) ➔ Alignement ➔ ArcFace ➔ Recherche FAISS ➔ Présent")
    logger.info("=" * 70)
    
    # Vérifier que le fichier existe
    if not os.path.exists(group_photo_path):
        logger.error(f"Le fichier photo n'existe pas: {group_photo_path}")
        sys.exit(1)
    
    try:
        # Initialiser la base de données
        db = LocalVectorDB()
        student_count = db.get_student_count()
        
        if student_count == 0:
            logger.error("Aucun étudiant inscrit dans la base de données. Veuillez d'abord inscrire des étudiants.")
            sys.exit(1)
        
        logger.info(f"Base de données chargée. Étudiants inscrits: {student_count}")
        
        # Initialiser le pipeline
        pipeline = FacePipeline()
        
        # ÉTAPE 1: MTCNN (Multi-visages) - Détection de tous les visages
        logger.info(f"ÉTAPE 1: MTCNN (Multi-visages) - Détection des visages...")
        embeddings = pipeline.get_embedding_from_path(group_photo_path, detect_all=True)
        
        if len(embeddings) == 0:
            logger.warning("Aucun visage détecté dans la photo de groupe.")
            return
        
        logger.info(f"{len(embeddings)} visage(s) détecté(s) avec MTCNN")
        
        # Rechercher chaque visage dans la base de données
        present_students = []
        for i, embedding in enumerate(embeddings):
            logger.info(f"Traitement du visage #{i+1}/{len(embeddings)}...")
            
            # ÉTAPE 2: Alignement - Déjà effectué dans le pipeline
            # ÉTAPE 3: ArcFace - Déjà effectué dans le pipeline
            
            # ÉTAPE 4: Recherche FAISS
            logger.info("ÉTAPE 4: Recherche FAISS...")
            result = db.search_face(embedding, threshold=threshold)
            
            if result:
                student_info = result['metadata']
                similarity = result['similarity']
                
                # Vérifier si l'étudiant n'est pas déjà marqué présent
                already_present = any(s['matricule'] == student_info['matricule'] for s in present_students)
                
                if not already_present:
                    # ÉTAPE 5: Marquage Présent
                    present_students.append({
                        'matricule': student_info['matricule'],
                        'nom': student_info['nom'],
                        'prenom': student_info['prenom'],
                        'similarity': similarity
                    })
                    logger.info(f"ÉTAPE 5: Marquage Présent - {student_info['nom']} {student_info['prenom']} (similarité: {similarity:.4f})")
                else:
                    logger.info(f"Étudiant déjà identifié: {student_info['nom']} {student_info['prenom']}")
            else:
                logger.info(f"Visage #{i+1} non reconnu (similarité <= {threshold})")
        
        # Sécurité : Créer le dossier 'reports/' s'il n'existe pas encore
        reports_dir = "reports"
        os.makedirs(reports_dir, exist_ok=True)

        # Générer le rapport CSV à l'intérieur du dossier 'reports/'
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = os.path.join(reports_dir, f"attendance_UCC_{timestamp}.csv")
        
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Matricule', 'Nom', 'Prénom', 'Statut', 'Similarité']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for student in present_students:
                writer.writerow({
                    'Matricule': student['matricule'],
                    'Nom': student['nom'],
                    'Prénom': student['prenom'],
                    'Statut': 'PRESENT',
                    'Similarité': f"{student['similarity']:.4f}"
                })
        
        logger.info("=" * 70)
        logger.info("RAPPORT DE PRÉSENCE")
        logger.info("=" * 70)
        logger.info(f"Visages détectés: {len(embeddings)}")
        logger.info(f"Étudiants identifiés: {len(present_students)}")
        logger.info(f"Fichier CSV généré: {csv_filename}")
        logger.info("=" * 70)
        
        # Afficher le résumé des étudiants présents
        if present_students:
            logger.info("Étudiants présents:")
            for student in present_students:
                logger.info(f"  - {student['nom']} {student['prenom']} (Matricule: {student['matricule']}, Similarité: {student['similarity']:.4f})")
        else:
            logger.warning("Aucun étudiant identifié.")
        
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de présence: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """Fonction principale de l'application CLI."""
    parser = argparse.ArgumentParser(
        description="Système de reconnaissance faciale pour la présence des étudiants - UCC",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Phase d'Enrôlement (Une seule fois par étudiant):
Photos multiples (5-10 recommandées) ➔ MTCNN ➔ Alignement ➔ ArcFace ➔ Embedding Moyen ➔ Stockage FAISS (.index + .pkl)

Angles recommandés: Face, Gauche, Droite, Haut, Bas, Sourire, Sans sourire

Phase de Pointage (À chaque début de cours):
MTCNN (Multi-visages) ➔ Alignement ➔ ArcFace ➔ Recherche FAISS ➔ Marquage Présent

Phase de Modification:
Mise à jour des informations ou ajout de photos à un étudiant existant

Exemples d'utilisation:
  # Inscrire un nouvel étudiant avec plusieurs photos (Recommandé)
  python enroll.py enroll --matricule "UCC2024001" --nom "Doe" --prenom "John" --photos photo1.jpg photo2.jpg photo3.jpg
  
  # Inscrire un nouvel étudiant avec une seule photo (Compatibilité)
  python enroll.py enroll --matricule "UCC2024001" --nom "Doe" --prenom "John" --photo "john_doe.jpg"
  
  # Mettre à jour les informations d'un étudiant
  python enroll.py update --matricule "UCC2024001" --new-nom "Smith" --new-prenom "Jane"
  
  # Ajouter des photos à un étudiant existant
  python enroll.py add-photos --matricule "UCC2024001" --photos new_photo1.jpg new_photo2.jpg
  
  # Remplacer toutes les photos d'un étudiant
  python enroll.py add-photos --matricule "UCC2024001" --photos new_photo1.jpg new_photo2.jpg --replace
  
  # Vérifier la présence à partir d'une photo de groupe (Phase de Pointage)
  python enroll.py attendance --photo "classe_photo.jpg"
  
  # Vérifier la présence avec un seuil personnalisé
  python enroll.py attendance --photo "classe_photo.jpg" --threshold 0.5
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commande à exécuter')
    
    # Sous-commande pour l'inscription (Phase d'Enrôlement)
    enroll_parser = subparsers.add_parser('enroll', help='Inscrire un nouvel étudiant (Phase d\'Enrôlement)')
    enroll_parser.add_argument('--matricule', required=True, help='Matricule de l\'étudiant')
    enroll_parser.add_argument('--nom', required=True, help='Nom de l\'étudiant')
    enroll_parser.add_argument('--prenom', required=True, help='Prénom de l\'étudiant')
    enroll_parser.add_argument('--email', help='Email de l\'étudiant (optionnel)')
    enroll_parser.add_argument('--telephone', help='Téléphone de l\'étudiant (optionnel)')
    enroll_parser.add_argument('--faculte-id', type=int, help='ID de la faculté (optionnel, requis pour sauvegarde MySQL)')
    enroll_parser.add_argument('--promotion-id', type=int, help='ID de la promotion (optionnel, requis pour sauvegarde MySQL)')
    enroll_parser.add_argument('--photos', nargs='+', required=True, 
                              help='Chemin(s) vers la/les photo(s) d\'identité (5-10 photos recommandées)')
    enroll_parser.add_argument('--photo', help='Chemin vers une photo d\'identité unique (compatibilité)')
    
    # Sous-commande pour la vérification de présence (Phase de Pointage)
    attendance_parser = subparsers.add_parser('attendance', help='Vérifier la présence des étudiants (Phase de Pointage)')
    attendance_parser.add_argument('--photo', required=True, help='Chemin vers la photo de groupe')
    attendance_parser.add_argument('--threshold', type=float, default=0.5, 
                                    help='Seuil de similarité cosinus pour la correspondance (défaut: 0.5 - recommandé)')
    
    # Sous-commande pour la mise à jour des informations
    update_parser = subparsers.add_parser('update', help='Mettre à jour les informations d\'un étudiant existant')
    update_parser.add_argument('--matricule', required=True, help='Matricule actuel de l\'étudiant')
    update_parser.add_argument('--new-matricule', help='Nouveau matricule (optionnel)')
    update_parser.add_argument('--new-nom', help='Nouveau nom (optionnel)')
    update_parser.add_argument('--new-prenom', help='Nouveau prénom (optionnel)')
    
    # Sous-commande pour l'ajout de photos
    add_photos_parser = subparsers.add_parser('add-photos', help='Ajouter des photos à un étudiant existant')
    add_photos_parser.add_argument('--matricule', required=True, help='Matricule de l\'étudiant')
    add_photos_parser.add_argument('--photos', nargs='+', required=True, 
                                   help='Chemins vers les nouvelles photos')
    add_photos_parser.add_argument('--replace', action='store_true', 
                                   help='Remplacer toutes les photos au lieu d\'ajouter')
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        sys.exit(1)
    
    if args.command == 'enroll':
        # Gérer à la fois --photos (nouveau) et --photo (compatibilité)
        if hasattr(args, 'photos') and args.photos:
            photo_paths = args.photos
        elif hasattr(args, 'photo') and args.photo:
            photo_paths = args.photo
        else:
            logger.error("Erreur: Veuillez spécifier au moins une photo avec --photos ou --photo")
            sys.exit(1)
        
        enroll_student(
            args.matricule, 
            args.nom, 
            args.prenom, 
            photo_paths,
            email=getattr(args, 'email', None),
            telephone=getattr(args, 'telephone', None),
            faculte_id=getattr(args, 'faculte_id', None),
            promotion_id=getattr(args, 'promotion_id', None)
        )
    elif args.command == 'attendance':
        check_attendance(args.photo, args.threshold)
    elif args.command == 'update':
        update_student_info(args.matricule, args.new_matricule, args.new_nom, args.new_prenom)
    elif args.command == 'add-photos':
        add_photos_to_student(args.matricule, args.photos, args.replace)


if __name__ == "__main__":
    main()
