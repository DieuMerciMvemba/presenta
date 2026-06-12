"""
Service de reconnaissance faciale pour l'application Kivy
Interface avec pipeline.py pour l'extraction d'embeddings
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pipeline import FacePipeline
import logging
import numpy as np

logger = logging.getLogger(__name__)


class FaceRecognitionService:
    """Service pour la reconnaissance faciale"""
    
    def __init__(self):
        """Initialise le service de reconnaissance faciale"""
        self.pipeline = None
        self._initialize_pipeline()
    
    def _initialize_pipeline(self):
        """Initialise le pipeline de reconnaissance"""
        try:
            self.pipeline = FacePipeline()
            logger.info("Service de reconnaissance faciale initialisé avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du pipeline: {e}")
            raise
    
    def extract_embedding_from_photo(self, photo_path):
        """
        Extrait l'embedding facial depuis une photo
        
        Args:
            photo_path (str): Chemin vers la photo
            
        Returns:
            numpy.ndarray: Embedding facial 512-D ou None si erreur
        """
        if not self.pipeline:
            return None
        
        try:
            embedding = self.pipeline.get_embedding_from_path(photo_path)
            if len(embedding) > 0:
                return embedding[0]  # Retourne le premier embedding
            return None
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction de l'embedding: {e}")
            return None
    
    def extract_embeddings_from_photos(self, photo_paths):
        """
        Extrait les embeddings faciaux depuis plusieurs photos
        
        Args:
            photo_paths (list): Liste des chemins vers les photos
            
        Returns:
            list: Liste des embeddings faciaux 512-D
        """
        if not self.pipeline:
            return []
        
        try:
            embeddings = self.pipeline.get_embeddings_from_multiple_paths(photo_paths)
            return embeddings
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des embeddings: {e}")
            return []
    
    def compute_mean_embedding(self, embeddings):
        """
        Calcule l'embedding moyen à partir de plusieurs embeddings
        
        Args:
            embeddings (list): Liste des embeddings
            
        Returns:
            numpy.ndarray: Embedding moyen
        """
        if not embeddings or len(embeddings) == 0:
            return None
        
        try:
            mean_embedding = np.mean(embeddings, axis=0)
            # Normalisation
            norm = np.linalg.norm(mean_embedding)
            if norm > 0:
                mean_embedding = mean_embedding / norm
            return mean_embedding
        except Exception as e:
            logger.error(f"Erreur lors du calcul de l'embedding moyen: {e}")
            return None
    
    def detect_faces(self, image):
        """
        Détecte les visages dans une image
        
        Args:
            image (numpy.ndarray): Image en format BGR
            
        Returns:
            list: Liste des visages détectés avec leurs boîtes englobantes
        """
        if not self.pipeline:
            return []
        
        try:
            faces = self.pipeline.detector.detect_faces(image)
            return faces
        except Exception as e:
            logger.error(f"Erreur lors de la détection des visages: {e}")
            return []
    
    def align_face(self, image, bbox, keypoints=None):
        """
        Aligne un visage
        
        Args:
            image (numpy.ndarray): Image en format BGR
            bbox (list): Boîte englobante [x, y, w, h]
            keypoints (dict): Points clés optionnels
            
        Returns:
            numpy.ndarray: Visage aligné ou None si erreur
        """
        if not self.pipeline:
            return None
        
        try:
            aligned_face = self.pipeline.align_face(image, bbox, keypoints=keypoints)
            return aligned_face
        except Exception as e:
            logger.error(f"Erreur lors de l'alignement du visage: {e}")
            return None
