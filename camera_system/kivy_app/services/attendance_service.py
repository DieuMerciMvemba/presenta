"""
Service de gestion de présence pour l'application Kivy
Interface avec vector_db.py pour la recherche et le marquage de présence
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from vector_db import LocalVectorDB
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class AttendanceService:
    """Service pour la gestion de la présence"""
    
    def __init__(self):
        """Initialise le service de présence"""
        self.db = None
        self._initialize_db()
    
    def _initialize_db(self):
        """Initialise la connexion à la base de données"""
        try:
            self.db = LocalVectorDB(
                index_path="data/facerec_faiss.index",
                metadata_path="data/students_metadata.pkl"
            )
            logger.info("Service de présence initialisé avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du service de présence: {e}")
            raise
    
    def check_attendance_from_embedding(self, embedding, threshold=0.5):
        """
        Vérifie la présence à partir d'un embedding facial
        
        Args:
            embedding (numpy.ndarray): Embedding facial 512-D
            threshold (float): Seuil de similarité (défaut: 0.5)
            
        Returns:
            dict: Informations de l'étudiant si reconnu, None sinon
        """
        if not self.db:
            return None
        
        try:
            result = self.db.search_face(embedding, threshold=threshold)
            if result:
                return {
                    'student_id': result['id'],
                    'metadata': result['metadata'],
                    'similarity': result['similarity']
                }
            return None
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de présence: {e}")
            return None
    
    def mark_student_present(self, student_id, timestamp=None):
        """
        Marque un étudiant comme présent
        
        Args:
            student_id (int): ID de l'étudiant
            timestamp (datetime): Horodatage optionnel
            
        Returns:
            bool: True si succès, False sinon
        """
        # Cette fonction peut être étendue pour enregistrer les présences dans un fichier séparé
        # Pour l'instant, nous utilisons simplement la base de données FAISS
        if timestamp is None:
            timestamp = datetime.now()
        
        logger.info(f"Étudiant ID={student_id} marqué présent à {timestamp}")
        return True
    
    def generate_attendance_report(self, present_students, output_path=None):
        """
        Génère un rapport de présence CSV
        
        Args:
            present_students (list): Liste des IDs d'étudiants présents
            output_path (str): Chemin du fichier CSV de sortie
            
        Returns:
            str: Chemin du fichier CSV généré
        """
        import csv
        import os
        
        # Créer le dossier reports s'il n'existe pas
        reports_dir = "reports"
        os.makedirs(reports_dir, exist_ok=True)
        
        # Générer le nom du fichier si non spécifié
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(reports_dir, f"attendance_UCC_{timestamp}.csv")
        
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Matricule', 'Nom', 'Prénom', 'Statut', 'Similarité']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for student_id in present_students:
                    student_info = self.db.metadata.get(student_id)
                    if student_info:
                        writer.writerow({
                            'Matricule': student_info['matricule'],
                            'Nom': student_info['nom'],
                            'Prénom': student_info['prenom'],
                            'Statut': 'PRESENT',
                            'Similarité': 'N/A'  # La similarité n'est pas stockée ici
                        })
            
            logger.info(f"Rapport de présence généré: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Erreur lors de la génération du rapport: {e}")
            return None
    
    def get_attendance_statistics(self):
        """
        Retourne des statistiques de présence
        
        Returns:
            dict: Statistiques de présence
        """
        if not self.db:
            return {
                'total_students': 0,
                'present_today': 0,
                'absent_today': 0,
                'attendance_rate': 0.0
            }
        
        total_students = self.db.get_student_count()
        # Pour l'instant, nous retournons des valeurs par défaut
        # Cette fonction peut être étendue pour lire les fichiers CSV de présence
        
        return {
            'total_students': total_students,
            'present_today': 0,
            'absent_today': total_students,
            'attendance_rate': 0.0
        }
