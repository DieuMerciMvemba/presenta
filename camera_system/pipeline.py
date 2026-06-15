"""
Module de pipeline de traitement facial en 3 étapes:
Phase d'Enrôlement: Photo d'identité ➔ MTCNN ➔ Alignement ➔ ArcFace
Phase de Pointage: CAMERA ➔ MTCNN (Multi-visages) ➔ Alignement ➔ ArcFace
"""

import cv2
import numpy as np
import mediapipe as mp
from mtcnn import MTCNN
from insightface.app import FaceAnalysis
import logging

# Utilisation de l'API MediaPipe Tasks pour les versions récentes
try:
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision
    # Créer un détecteur FaceMesh avec l'API Tasks
    def create_face_mesh():
        base_options = python.BaseOptions(model_asset_path='face_landmarker.task')
        options = vision.FaceLandmarkerOptions(base_options=base_options,
                                               output_face_blendshapes=False,
                                               output_facial_transformation_matrixes=False,
                                               num_faces=1)
        return vision.FaceLandmarker.create_from_options(options)
    USE_NEW_API = True
except ImportError:
    # Fallback pour les versions plus anciennes
    try:
        from mediapipe.python.solutions import face_mesh as mp_face_mesh
        FaceMeshClass = mp_face_mesh.FaceMesh
        USE_NEW_API = False
    except (ImportError, AttributeError):
        raise ImportError("Impossible d'importer MediaPipe FaceMesh. Vérifiez l'installation de mediapipe.")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FacePipeline:
    """
    Classe pour le pipeline de reconnaissance faciale.
    
    Phase d'Enrôlement (Une seule fois par étudiant):
    Photo d'identité ➔ MTCNN ➔ Alignement ➔ ArcFace
    
    Phase de Pointage (À chaque début de cours):
    CAMERA ➔ MTCNN (Multi-visages) ➔ Alignement ➔ ArcFace
    """
    
    def __init__(self):
        """Initialise les modèles de détection, alignement et embedding."""
        logger.info("Initialisation du pipeline de reconnaissance faciale...")
        
        # Étape A: Détection avec MTCNN
        logger.info("Chargement du modèle MTCNN...")
        self.detector = MTCNN()
        
        # Étape B: Alignement avec MediaPipe Face Mesh
        logger.info("Chargement du modèle MediaPipe Face Mesh...")
        if USE_NEW_API:
            # Utiliser l'API Tasks
            try:
                self.face_mesh = create_face_mesh()
                self.use_new_api = True
                logger.info("API MediaPipe Tasks activée")
            except Exception as e:
                logger.warning(f"Échec de l'initialisation API Tasks: {e}")
                # Désactiver l'alignement avec MediaPipe, utiliser une méthode alternative
                self.face_mesh = None
                self.use_new_api = False
                logger.warning("Alignement MediaPipe désactivé, utilisation de l'alignement simple")
        else:
            # Utiliser l'API Solutions
            self.face_mesh = FaceMeshClass(
                static_image_mode=True,
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5
            )
            self.use_new_api = False
            logger.info("API MediaPipe Solutions activée")
        
        # Étape C: Embedding avec InsightFace ArcFace
        logger.info("Chargement du modèle InsightFace ArcFace (buffalo_l)...")
        self.embedder = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
        self.embedder.prepare(ctx_id=-1)  # ctx_id=-1 pour CPU
        
        logger.info("Pipeline initialisé avec succès.")
    
    def detect_faces(self, image):
        """
        Détecte les visages dans une image avec MTCNN.
        
        Args:
            image (np.ndarray): Image en format BGR (OpenCV)
        
        Returns:
            list: Liste des boîtes englobantes des visages détectés
        """
        # Redimensionner l'image si elle est trop grande pour éviter les erreurs de mémoire
        max_dimension = 1600
        height, width = image.shape[:2]
        
        if max(height, width) > max_dimension:
            scale_factor = max_dimension / max(height, width)
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
            logger.info(f"Image redimensionnée de {width}x{height} à {new_width}x{new_height}")
        
        if len(image.shape) == 3:
            # MTCNN attend des images RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            image_rgb = image
        
        faces = self.detector.detect_faces(image_rgb)
        
        # Si l'image a été redimensionnée, remettre les boîtes à l'échelle originale
        if max(height, width) > max_dimension:
            scale_back = 1.0 / scale_factor
            for face in faces:
                face['box'] = [int(coord * scale_back) for coord in face['box']]
                if 'keypoints' in face:
                    for key in face['keypoints']:
                        face['keypoints'][key] = [int(coord * scale_back) for coord in face['keypoints'][key]]
        
        logger.info(f"{len(faces)} visage(s) détecté(s) avec MTCNN.")
        return faces
    
    def align_face(self, image, bbox, keypoints=None):
        """
        Aligne un visage en utilisant les points clés des yeux.
        
        Args:
            image (np.ndarray): Image d'origine en format BGR
            bbox (list or dict): Boîte englobante du visage (list: [x, y, width, height] ou dict: {'x':, 'y':, 'width':, 'height':})
            keypoints (dict): Points clés optionnels de MTCNN (left_eye, right_eye, etc.)
        
        Returns:
            np.ndarray: Visage aligné et redimensionné à 112x112 pixels
        """
        # Gérer les deux formats de bbox: liste [x, y, w, h] ou dictionnaire
        if isinstance(bbox, list):
            x, y, w, h = bbox[0], bbox[1], bbox[2], bbox[3]
        elif isinstance(bbox, dict):
            x, y, w, h = bbox['x'], bbox['y'], bbox['width'], bbox['height']
        else:
            raise ValueError(f"Format de bbox non supporté: {type(bbox)}")
        
        # Protection contre les coordonnées négatives
        x = max(0, x)
        y = max(0, y)
        
        # S'assurer que la boîte ne dépasse pas l'image
        height, width = image.shape[:2]
        w = min(w, width - x)
        h = min(h, height - y)
        
        if w <= 0 or h <= 0:
            raise ValueError("Boîte englobante invalide après correction des bords.")
        
        # Extraire le visage
        face_crop = image[y:y+h, x:x+w]
        
        # Utiliser les points clés de MTCNN si disponibles, sinon essayer MediaPipe
        if keypoints and 'left_eye' in keypoints and 'right_eye' in keypoints:
            # Utiliser les points clés de MTCNN
            left_eye = keypoints['left_eye']
            right_eye = keypoints['right_eye']
            
            # Convertir les coordonnées relatives en pixels dans le crop
            h_crop, w_crop = face_crop.shape[:2]
            left_eye_pos = (
                int((left_eye[0] - x) / w * w_crop),
                int((left_eye[1] - y) / h * h_crop)
            )
            right_eye_pos = (
                int((right_eye[0] - x) / w * w_crop),
                int((right_eye[1] - y) / h * h_crop)
            )
            
            logger.info("Utilisation des points clés MTCNN pour l'alignement")
        elif self.face_mesh and not self.use_new_api:
            # Utiliser MediaPipe avec l'ancienne API
            face_rgb = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(face_rgb)
            
            if results.multi_face_landmarks is None:
                logger.warning("Aucun point clé détecté par MediaPipe, utilisation du crop original.")
                return cv2.resize(face_crop, (112, 112))
            
            landmarks = results.multi_face_landmarks[0].landmark
            
            # Indices des yeux (gauche = 33, droit = 263 selon MediaPipe Face Mesh)
            left_eye = landmarks[33]
            right_eye = landmarks[263]
            
            # Convertir les coordonnées normalisées en pixels
            h_crop, w_crop = face_crop.shape[:2]
            left_eye_pos = (int(left_eye.x * w_crop), int(left_eye.y * h_crop))
            right_eye_pos = (int(right_eye.x * w_crop), int(right_eye.y * h_crop))
        else:
            # Pas de points clés disponibles, utiliser le crop original
            logger.warning("Pas de points clés disponibles, utilisation du crop original.")
            return cv2.resize(face_crop, (112, 112))
        
        # Calculer l'angle de rotation
        dy = right_eye_pos[1] - left_eye_pos[1]
        dx = right_eye_pos[0] - left_eye_pos[0]
        angle = np.degrees(np.arctan2(dy, dx))
        
        # Calculer le centre du visage
        h_crop, w_crop = face_crop.shape[:2]
        center_x = w_crop // 2
        center_y = h_crop // 2
        
        # Créer la matrice de rotation
        rotation_matrix = cv2.getRotationMatrix2D((center_x, center_y), angle, 1.0)
        
        # Appliquer la rotation
        aligned_face = cv2.warpAffine(face_crop, rotation_matrix, (w_crop, h_crop), 
                                      flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        
        # Redimensionner à 112x112 (taille standard pour ArcFace)
        aligned_face = cv2.resize(aligned_face, (112, 112))
        
        logger.info(f"Visage aligné avec succès. Angle de rotation: {angle:.2f}°")
        return aligned_face
    
    def get_embedding(self, aligned_face):
        """
        Extrait l'embedding facial 512-D avec InsightFace ArcFace.
        
        Args:
            aligned_face (np.ndarray): Visage aligné de taille 112x112 en format BGR
        
        Returns:
            np.ndarray: Vecteur d'embedding normalisé de 512 dimensions
        """
        # InsightFace attend des images BGR
        if len(aligned_face.shape) == 2:
            aligned_face = cv2.cvtColor(aligned_face, cv2.COLOR_GRAY2BGR)
        
        # Extraire l'embedding via le modèle de reconnaissance ArcFace directement
        # (évite de relancer RetinaFace sur un crop 112x112 déjà aligné, ce qui échoue souvent)
        if hasattr(self.embedder, 'models') and 'recognition' in self.embedder.models:
            rec_model = self.embedder.models['recognition']
            # ArcFaceONNX expose get_feat (pas get_embedding)
            if hasattr(rec_model, 'get_feat'):
                embedding = rec_model.get_feat(aligned_face)
            elif hasattr(rec_model, 'get_embedding'):
                embedding = rec_model.get_embedding(aligned_face)
            else:
                raise AttributeError(
                    f"Le modèle de reconnaissance ({type(rec_model).__name__}) ne dispose "
                    f"ni de 'get_feat' ni de 'get_embedding'. "
                    f"Attributs disponibles: {[a for a in dir(rec_model) if not a.startswith('_')]}"
                )
            if embedding.ndim > 1:
                embedding = embedding.flatten()
        else:
            faces = self.embedder.get(aligned_face)
            if len(faces) == 0:
                raise ValueError("Aucun visage détecté par InsightFace lors de l'extraction d'embedding.")
            embedding = faces[0].embedding
        
        # Normalisation L2 de l'embedding
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
            logger.info(f"Embedding normalisé. Norme: {norm:.6f} → 1.000000")
        else:
            logger.warning("Embedding avec norme zéro, normalisation ignorée")
        
        logger.info(f"Embedding extrait avec succès. Dimension: {embedding.shape}")
        
        return embedding
    
    def process_image(self, image_path, detect_all=False):
        """
        Traite une image complète: détection, alignement et embedding.
        
        Args:
            image_path (str): Chemin vers l'image
            detect_all (bool): Si True, détecte tous les visages; sinon, attend exactement 1 visage
        
        Returns:
            list: Liste de tuples (aligned_face, bbox) pour chaque visage détecté
        """
        # Charger l'image
        logger.info(f"Chargement de l'image: {image_path}")
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Impossible de charger l'image: {image_path}")
        logger.info(f"Image chargée: shape={image.shape}")
        
        # Détecter les visages
        faces = self.detect_faces(image)
        
        if not detect_all:
            if len(faces) == 0:
                raise ValueError("Aucun visage détecté dans l'image.")
            elif len(faces) > 1:
                raise ValueError(f"Plusieurs visages détectés ({len(faces)}). Un seul visage est attendu pour l'inscription.")
        else:
            if len(faces) == 0:
                logger.warning("Aucun visage détecté dans l'image de groupe.")
                return []
        
        logger.info(f"{len(faces)} visage(s) à traiter")
        
        # Traiter chaque visage
        results = []
        for i, face in enumerate(faces):
            logger.info(f"Traitement du visage {i+1}/{len(faces)}")
            bbox = face['box']
            keypoints = face.get('keypoints', None)  # MTCNN fournit des points clés
            logger.info(f"BBox: {bbox}, Keypoints: {keypoints}")
            try:
                aligned_face = self.align_face(image, bbox, keypoints=keypoints)
                results.append((aligned_face, bbox))
                logger.info(f"Visage {i+1} traité avec succès.")
            except Exception as e:
                logger.error(f"Erreur lors de l'alignement du visage {i+1}: {e}")
                import traceback
                logger.error(traceback.format_exc())
                continue
        
        return results
    
    def get_embedding_from_path(self, image_path, detect_all=False):
        """
        Extrait l'embedding directement depuis un chemin d'image.
        
        Args:
            image_path (str): Chemin vers l'image
            detect_all (bool): Si True, détecte tous les visages; sinon, attend exactement 1 visage
        
        Returns:
            list or np.ndarray: Si detect_all=True, liste d'embeddings; sinon, un seul embedding
        """
        results = self.process_image(image_path, detect_all=detect_all)
        
        embeddings = []
        for aligned_face, bbox in results:
            embedding = self.get_embedding(aligned_face)
            embeddings.append(embedding)
        
        if not detect_all:
            if len(embeddings) == 0:
                raise ValueError("Aucun embedding extrait.")
            return embeddings[0]
        else:
            return embeddings
    
    def get_embeddings_from_multiple_paths(self, image_paths):
        """
        Extrait les embeddings faciaux à partir de plusieurs chemins d'images.
        
        Args:
            image_paths (list): Liste des chemins vers les images
        
        Returns:
            list: Liste des embeddings faciaux (chaque 512 dimensions)
        """
        embeddings = []
        
        logger.info(f"Traitement de {len(image_paths)} images pour l'extraction des embeddings...")
        
        for i, image_path in enumerate(image_paths):
            try:
                logger.info(f"  Image {i+1}/{len(image_paths)}: {image_path}")
                embedding = self.get_embedding_from_path(image_path, detect_all=False)
                embeddings.append(embedding)
                logger.info(f"  ✓ Embedding extrait avec succès (dimension: {embedding.shape})")
            except Exception as e:
                logger.error(f"  ✗ Erreur pour {image_path}: {e}")
                continue
        
        if len(embeddings) == 0:
            raise ValueError("Aucun embedding n'a pu être extrait des images fournies.")
        
        logger.info(f"{len(embeddings)} embeddings extraits avec succès sur {len(image_paths)} images.")
        
        return embeddings
