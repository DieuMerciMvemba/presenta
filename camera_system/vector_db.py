"""
Module de base de données vectorielle locale pour la reconnaissance faciale.
Utilise FAISS pour le stockage des embeddings et pickle pour les métadonnées.

Phase d'Enrôlement: Photo d'identité ➔ MTCNN ➔ Alignement ➔ ArcFace ➔ Stockage FAISS (.index + .pkl)
"""

import pickle
import numpy as np
import faiss
import os
import logging
import sys

# Importer la configuration
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from config import Config
except ImportError:
    # Fallback si config n'est pas disponible
    class Config:
        DATA_PATH = "data"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LocalVectorDB:
    """
    Classe pour gérer la base de données vectorielle locale avec FAISS.
    
    Phase d'Enrôlement (Une seule fois par étudiant):
    Photo d'identité ➔ MTCNN ➔ Alignement ➔ ArcFace ➔ Stockage dans le fichier FAISS (.index + .pkl)
    """
    
    def __init__(self, index_path=None, metadata_path=None, dimension=512):
        """
        Initialise ou charge une base de données FAISS existante.
        
        Args:
            index_path (str): Chemin vers le fichier d'index FAISS (utilise Config.DATA_PATH par défaut)
            metadata_path (str): Chemin vers le fichier de métadonnées pickle (utilise Config.DATA_PATH par défaut)
            dimension (int): Dimension des embeddings (512 pour ArcFace)
        """ 
        # Utiliser Config.DATA_PATH si les chemins ne sont pas fournis
        if index_path is None:
            index_path = os.path.join(Config.DATA_PATH, "facerec_faiss.index")
        if metadata_path is None:
            metadata_path = os.path.join(Config.DATA_PATH, "students_metadata.pkl")
        
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.dimension = dimension
        self.next_id = 0
        
        # Sécurité : Créer automatiquement le dossier parent (ex: 'data/') s'il n'existe pas
        if os.path.dirname(index_path):
            os.makedirs(os.path.dirname(index_path), exist_ok=True)
        if os.path.dirname(metadata_path):
            os.makedirs(os.path.dirname(metadata_path), exist_ok=True)
        
        # Charger ou créer l'index FAISS
        if os.path.exists(index_path):
            logger.info(f"Chargement de l'index FAISS existant depuis {index_path}")
            self.index = faiss.read_index(index_path)
            
            # Déterminer le prochain ID disponible
            if self.index.ntotal > 0:
                self.next_id = self.index.ntotal
                logger.info(f"Index chargé avec {self.index.ntotal} vecteurs. Prochain ID: {self.next_id}")
        else:
            logger.info(f"Création d'un nouvel index FAISS avec dimension {dimension}")
            # Utiliser IndexIDMap avec IndexFlatIP pour similarité cosinus (embeddings normalisés)
            base_index = faiss.IndexFlatIP(dimension)
            self.index = faiss.IndexIDMap(base_index)
        
        # Charger ou créer le dictionnaire de métadonnées
        if os.path.exists(metadata_path):
            logger.info(f"Chargement des métadonnées depuis {metadata_path}")
            with open(metadata_path, 'rb') as f:
                self.metadata = pickle.load(f)
        else:
            logger.info(f"Création d'un nouveau dictionnaire de métadonnées")
            self.metadata = {}
    
    def register_student(self, id_num, matricule, nom, prenom, embeddings):
        """
        Enregistre un nouvel étudiant dans la base de données avec support d'embeddings multiples.
        
        Phase d'Enrôlement: Stockage dans le fichier FAISS (.index + .pkl)
        """
        if id_num in self.metadata:
            raise ValueError(f"L'ID {id_num} existe déjà dans la base de données.")
        
        # Convertir en liste si c'est un seul embedding
        if isinstance(embeddings, np.ndarray) and embeddings.ndim == 1:
            embeddings = [embeddings]
        elif isinstance(embeddings, np.ndarray) and embeddings.ndim == 2:
            embeddings = list(embeddings)
        
        # Calculer l'embedding moyen si plusieurs embeddings sont fournis
        if len(embeddings) > 1:
            logger.info(f"Calcul de l'embedding moyen à partir de {len(embeddings)} photos...")
            mean_embedding = np.mean(embeddings, axis=0)
        else:
            mean_embedding = embeddings[0]
            logger.info(f"Utilisation d'un seul embedding (dimension: {mean_embedding.shape})")
        
        # CORRECTION 1 : Normalisation systématique de l'embedding (Crucial pour IndexFlatIP)
        norm = np.linalg.norm(mean_embedding)
        if norm > 0:
            mean_embedding = mean_embedding / norm
            logger.info(f"Embedding inséré normalisé avec succès. Norme forcée à 1.000000")
        else:
            logger.warning("Embedding avec norme zéro, normalisation ignorée")
        
        # Convertir l'embedding moyen en float32
        embedding_float32 = np.array(mean_embedding, dtype=np.float32).reshape(1, -1)
        
        # Ajouter à l'index FAISS avec l'ID personnalisé
        self.index.add_with_ids(embedding_float32, np.array([id_num]))
        
        # Mettre à jour les métadonnées avec le nombre de photos utilisées
        self.metadata[id_num] = {
            "matricule": matricule,
            "nom": nom,
            "prenom": prenom,
            "num_photos": len(embeddings),
            "original_embeddings": embeddings  # Stocker pour futur ajout
        }
        
        # Sauvegarder les fichiers
        self.save()
    
    def search_face(self, embedding, threshold=0.5):
        """
        Recherche le visage le plus proche dans la base de données avec similarité cosinus (IndexFlatIP).
        """
        if self.index.ntotal == 0:
            logger.warning("La base de données est vide.")
            return None
        
        # CORRECTION 2 : Normalisation de la requête pour garantir une métrique stricte
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        # Convertir l'embedding en float32
        embedding_float32 = np.array(embedding, dtype=np.float32).reshape(1, -1)
        
        # Rechercher le vecteur le plus proche (top-1)
        distances, indices = self.index.search(embedding_float32, k=1)
        
        # CORRECTION 3 : IndexFlatIP retourne DIRECTEMENT la similarité cosinus.
        similarity = float(distances[0][0])
        matched_id = int(indices[0][0])
        
        logger.info(f"Recherche FAISS: Similarité={similarity:.4f}, ID correspondant={matched_id}, Seuil={threshold}")
        
        # Vérifier si la similarité est supérieure au seuil
        if similarity > threshold:
            student_info = self.metadata.get(matched_id)
            if student_info:
                logger.info(f"Correspondance trouvée: {student_info['nom']} {student_info['prenom']} (similarité: {similarity:.4f})")
                return {
                    "metadata": student_info,
                    "similarity": similarity,
                    "id": matched_id
                }
        
        logger.info(f"Aucune correspondance trouvée (similarité {similarity:.4f} <= seuil {threshold})")
        return None
    
    def save(self):
        """Sauvegarde l'index FAISS et les métadonnées sur le disque."""
        faiss.write_index(self.index, self.index_path)
        logger.info(f"Index FAISS sauvegardé dans {self.index_path}")
        
        with open(self.metadata_path, 'wb') as f:
            pickle.dump(self.metadata, f)
        logger.info(f"Métadonnées sauvegardées dans {self.metadata_path}")
    
    def get_next_id(self):
        """Retourne le prochain ID disponible."""
        return self.next_id
    
    def increment_id(self):
        """Incrémente le compteur d'ID."""
        self.next_id += 1
    
    def get_student_count(self):
        """Retourne le nombre d'étudiants enregistrés."""
        return self.index.ntotal
    
    def find_student_by_matricule(self, matricule):
        """Trouve un étudiant par son matricule."""
        for student_id, metadata in self.metadata.items():
            if metadata.get('matricule') == matricule:
                return {
                    'id': student_id,
                    'metadata': metadata
                }
        return None
    
    def update_student_info(self, student_id, new_matricule=None, new_nom=None, new_prenom=None):
        """Met à jour les informations d'un étudiant."""
        if student_id not in self.metadata:
            raise ValueError(f"L'étudiant avec ID {student_id} n'existe pas.")
        
        if new_matricule is not None:
            self.metadata[student_id]['matricule'] = new_matricule
        if new_nom is not None:
            self.metadata[student_id]['nom'] = new_nom
        if new_prenom is not None:
            self.metadata[student_id]['prenom'] = new_prenom
        
        logger.info(f"Informations mises à jour pour l'étudiant ID={student_id}")
        self.save()
    
    def add_photos_to_student(self, student_id, new_embeddings, replace=False):
        """Ajoute de nouvelles photos à un étudiant existant et recalcule l'embedding moyen."""
        if student_id not in self.metadata:
            raise ValueError(f"L'étudiant avec ID {student_id} n'existe pas.")
        
        if 'original_embeddings' not in self.metadata[student_id]:
            logger.warning("Les embeddings originaux ne sont pas stockés. Utilisation de replace=True recommandé.")
            if not replace:
                logger.warning("Ajout impossible sans embeddings originaux. Passage en mode remplacement.")
                replace = True
        
        if replace:
            if isinstance(new_embeddings, np.ndarray) and new_embeddings.ndim == 1:
                new_embeddings = [new_embeddings]
            elif isinstance(new_embeddings, np.ndarray) and new_embeddings.ndim == 2:
                new_embeddings = list(new_embeddings)
            
            mean_embedding = np.mean(new_embeddings, axis=0)
            
            norm = np.linalg.norm(mean_embedding)
            if norm > 0:
                mean_embedding = mean_embedding / norm
            
            self.index.remove_ids(np.array([student_id]))
            
            embedding_float32 = np.array(mean_embedding, dtype=np.float32).reshape(1, -1)
            self.index.add_with_ids(embedding_float32, np.array([student_id]))
            
            self.metadata[student_id]['num_photos'] = len(new_embeddings)
            self.metadata[student_id]['original_embeddings'] = new_embeddings
            
            logger.info(f"Embeddings remplacés pour l'étudiant ID={student_id}. Nouveau nombre de photos: {len(new_embeddings)}")
        else:
            existing_embeddings = self.metadata[student_id].get('original_embeddings', [])
            
            if isinstance(new_embeddings, np.ndarray) and new_embeddings.ndim == 1:
                new_embeddings = [new_embeddings]
            elif isinstance(new_embeddings, np.ndarray) and new_embeddings.ndim == 2:
                new_embeddings = list(new_embeddings)
            
            all_embeddings = existing_embeddings + new_embeddings
            
            mean_embedding = np.mean(all_embeddings, axis=0)
            
            norm = np.linalg.norm(mean_embedding)
            if norm > 0:
                mean_embedding = mean_embedding / norm
            
            self.index.remove_ids(np.array([student_id]))
            
            embedding_float32 = np.array(mean_embedding, dtype=np.float32).reshape(1, -1)
            self.index.add_with_ids(embedding_float32, np.array([student_id]))
            
            self.metadata[student_id]['num_photos'] = len(all_embeddings)
            self.metadata[student_id]['original_embeddings'] = all_embeddings
            
            logger.info(f"Embeddings ajoutés pour l'étudiant ID={student_id}. Nouveau nombre de photos: {len(all_embeddings)}")
        
        self.save()