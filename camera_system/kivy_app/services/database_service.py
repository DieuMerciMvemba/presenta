"""
Service de base de données pour l'application Kivy
Interface avec vector_db.py pour la gestion des étudiants
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from vector_db import LocalVectorDB
import logging

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service pour la gestion de la base de données vectorielle"""
    
    def __init__(self):
        """Initialise le service de base de données"""
        self.db = None
        self._initialize_db()
    
    def _initialize_db(self):
        """Initialise la connexion à la base de données"""
        try:
            self.db = LocalVectorDB(
                index_path="data/facerec_faiss.index",
                metadata_path="data/students_metadata.pkl"
            )
            logger.info("Service de base de données initialisé avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de la base de données: {e}")
            raise
    
    def get_student_count(self):
        """Retourne le nombre d'étudiants enregistrés"""
        if self.db:
            return self.db.get_student_count()
        return 0
    
    def get_all_students(self):
        """Retourne tous les étudiants avec leurs métadonnées"""
        if not self.db:
            return []
        
        students = []
        for student_id, metadata in self.db.metadata.items():
            student_info = {
                'id': student_id,
                'matricule': metadata.get('matricule', ''),
                'nom': metadata.get('nom', ''),
                'prenom': metadata.get('prenom', ''),
                'num_photos': metadata.get('num_photos', 0)
            }
            students.append(student_info)
        return students
    
    def find_student_by_matricule(self, matricule):
        """Trouve un étudiant par son matricule"""
        if not self.db:
            return None
        return self.db.find_student_by_matricule(matricule)
    
    def find_student_by_id(self, student_id):
        """Trouve un étudiant par son ID"""
        if not self.db:
            return None
        if student_id in self.db.metadata:
            return {
                'id': student_id,
                'metadata': self.db.metadata[student_id]
            }
        return None
    
    def update_student_info(self, student_id, new_matricule=None, new_nom=None, new_prenom=None):
        """Met à jour les informations d'un étudiant"""
        if not self.db:
            return False
        try:
            self.db.update_student_info(student_id, new_matricule, new_nom, new_prenom)
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour: {e}")
            return False
    
    def delete_student(self, student_id):
        """Supprime un étudiant de la base de données"""
        if not self.db:
            return False
        try:
            import numpy as np
            self.db.index.remove_ids(np.array([student_id]))
            del self.db.metadata[student_id]
            self.db.save()
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la suppression: {e}")
            return False
    
    def get_statistics(self):
        """Retourne des statistiques sur la base de données"""
        if not self.db:
            return {
                'total_students': 0,
                'total_photos': 0,
                'avg_photos_per_student': 0
            }
        
        total_students = self.db.get_student_count()
        total_photos = sum(metadata.get('num_photos', 0) for metadata in self.db.metadata.values())
        avg_photos = total_photos / total_students if total_students > 0 else 0
        
        return {
            'total_students': total_students,
            'total_photos': total_photos,
            'avg_photos_per_student': round(avg_photos, 2)
        }
