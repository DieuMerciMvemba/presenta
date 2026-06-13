"""
Service de base de données pour l'application Kivy
Interface avec MySQL pour la gestion des étudiants et des données du système
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.mysql_service import MySQLService
import logging

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service pour la gestion de la base de données MySQL"""
    
    def __init__(self, host='localhost', database='ucc_face_recognition', 
                 user='root', password='', port=3306):
        """
        Initialise le service de base de données
        
        Args:
            host: Hôte MySQL (défaut: localhost)
            database: Nom de la base de données (défaut: ucc_face_recognition)
            user: Utilisateur MySQL (défaut: root)
            password: Mot de passe MySQL (défaut: vide)
            port: Port MySQL (défaut: 3306)
        """
        self.mysql_service = MySQLService(host, database, user, password, port)
        self._initialize_db()
    
    def _initialize_db(self):
        """Initialise la connexion à la base de données"""
        try:
            if self.mysql_service.connect():
                logger.info("Service de base de données initialisé avec succès")
            else:
                logger.warning("Connexion MySQL échouée, utilisation du mode hors-ligne")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de la base de données: {e}")
    
    def get_student_count(self):
        """Retourne le nombre d'étudiants enregistrés"""
        try:
            return self.mysql_service.get_student_count()
        except Exception as e:
            logger.error(f"Erreur lors du comptage des étudiants: {e}")
            return 0
    
    def get_all_students(self):
        """Retourne tous les étudiants avec leurs métadonnées"""
        try:
            students = self.mysql_service.get_all_students()
            # Transformer les données pour correspondre au format attendu
            formatted_students = []
            for student in students:
                student_info = {
                    'id': student['id'],
                    'matricule': student['matricule'],
                    'nom': student['nom'],
                    'prenom': student['prenom'],
                    'num_photos': student.get('num_photos', 0),
                    'email': student.get('email', ''),
                    'telephone': student.get('telephone', ''),
                    'faculte_id': student.get('faculte_id'),
                    'departement_id': student.get('departement_id'),
                    'annee_etude': student.get('annee_etude')
                }
                formatted_students.append(student_info)
            return formatted_students
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des étudiants: {e}")
            return []
    
    def find_student_by_matricule(self, matricule):
        """Trouve un étudiant par son matricule"""
        try:
            student = self.mysql_service.get_student_by_matricule(matricule)
            if student:
                return {
                    'id': student['id'],
                    'metadata': student
                }
            return None
        except Exception as e:
            logger.error(f"Erreur lors de la recherche par matricule: {e}")
            return None
    
    def find_student_by_id(self, student_id):
        """Trouve un étudiant par son ID"""
        try:
            # MySQL utilise des IDs auto-incrémentés, pas des IDs FAISS
            students = self.mysql_service.get_all_students()
            for student in students:
                if student['id'] == student_id:
                    return {
                        'id': student['id'],
                        'metadata': student
                    }
            return None
        except Exception as e:
            logger.error(f"Erreur lors de la recherche par ID: {e}")
            return None
    
    def update_student_info(self, student_id, new_matricule=None, new_nom=None, new_prenom=None):
        """Met à jour les informations d'un étudiant"""
        try:
            return self.mysql_service.update_student(
                student_id, 
                matricule=new_matricule, 
                nom=new_nom, 
                prenom=new_prenom
            )
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour: {e}")
            return False
    
    def delete_student(self, student_id):
        """Supprime un étudiant de la base de données"""
        try:
            return self.mysql_service.delete_student(student_id)
        except Exception as e:
            logger.error(f"Erreur lors de la suppression: {e}")
            return False
    
    def add_student(self, matricule, nom, prenom, email=None, telephone=None, 
                   faculte_id=None, departement_id=None, annee_etude=None):
        """Ajoute un nouvel étudiant"""
        try:
            student_id = self.mysql_service.insert_student(
                matricule=matricule,
                nom=nom,
                prenom=prenom,
                email=email,
                telephone=telephone,
                faculte_id=faculte_id,
                departement_id=departement_id,
                annee_etude=annee_etude
            )
            return student_id
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout de l'étudiant: {e}")
            return None
    
    def get_statistics(self):
        """Retourne des statistiques sur la base de données"""
        try:
            stats = self.mysql_service.get_statistics()
            return {
                'total_students': stats.get('total_students', 0),
                'total_photos': 0,  # À implémenter avec une table séparée pour les photos
                'avg_photos_per_student': 0
            }
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des statistiques: {e}")
            return {
                'total_students': 0,
                'total_photos': 0,
                'avg_photos_per_student': 0
            }
    
    def record_attendance(self, student_id, course_id=None, statut='present', 
                         methode='facial', confiance=0.0, photo_capture_path=None,
                         camera_id=None, notes=None):
        """Enregistre une présence"""
        try:
            attendance_id = self.mysql_service.insert_attendance(
                student_id=student_id,
                course_id=course_id,
                statut=statut,
                methode=methode,
                confiance=confiance,
                photo_capture_path=photo_capture_path,
                camera_id=camera_id,
                notes=notes
            )
            return attendance_id
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement de présence: {e}")
            return None
    
    def disconnect(self):
        """Ferme la connexion à la base de données"""
        try:
            self.mysql_service.disconnect()
        except Exception as e:
            logger.error(f"Erreur lors de la déconnexion: {e}")
