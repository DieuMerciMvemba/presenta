"""
Module de détection faciale en temps réel avec caméra.
Utilise OpenCV pour capturer le flux vidéo et le pipeline existant pour la reconnaissance.
Intègre un mécanisme d'Anti-Spoofing (détection de vivacité) pour bloquer les photos et écrans.
"""

import cv2
import numpy as np
import sys
import os
import time
import logging
from datetime import datetime

from vector_db import LocalVectorDB
from pipeline import FacePipeline
from anti_spoof import AntiSpoofDetector  # Importation du nouveau module anti-spoofing

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RealtimeFaceDetector:
    """
    Classe pour la détection faciale en temps réel avec caméra.
    
    Pipeline de Phase de Pointage avec Anti-Spoofing (À chaque début de cours):
    1. CAMERA ➔ Capture du flux vidéo en temps réel
    2. MTCNN (Multi-visages) ➔ Détection de tous les visages dans la frame
    3. ANTI-SPOOFING ➔ Filtrage immédiat des attaques (photos, écrans)
    4. ALIGNEMENT ➔ Alignement facial avec MediaPipe/MTCNN keypoints (si visage réel)
    5. ArcFace ➔ Extraction de l'embedding facial 512-D
    6. Recherche FAISS ➔ Recherche dans la base de données vectorielle
    7. MARQUAGE PRÉSENT ➔ Marquage de l'étudiant comme présent
    """
    
    def __init__(self, camera_index=0, recognition_threshold=0.5, display_size=(1280, 720), spoof_threshold=0.85):
        """
        Initialise le détecteur facial en temps réel.
        
        Args:
            camera_index (int): Index de la caméra (défaut: 0)
            recognition_threshold (float): Seuil de reconnaissance (défaut: 0.5)
            display_size (tuple): Taille de la fenêtre d'affichage (défaut: 1280x720)
            spoof_threshold (float): Seuil de vivacité pour l'anti-spoofing (défaut: 0.85)
        """
        self.camera_index = camera_index
        self.threshold = recognition_threshold
        self.display_size = display_size
        self.spoof_threshold = spoof_threshold
        
        # Initialiser la base de données dans le sous-dossier dédié 'data' (chemin absolu)
        logger.info("Chargement de la base de données...")
        try:
            from config import Config
            data_path = Config.DATA_PATH
        except ImportError:
            # Fallback: chemin absolu basé sur l'emplacement de ce script
            data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        os.makedirs(data_path, exist_ok=True)
        self.db = LocalVectorDB(
            index_path=os.path.join(data_path, "facerec_faiss.index"),
            metadata_path=os.path.join(data_path, "students_metadata.pkl")
        )
        logger.info(f"Base de données chargée: {self.db.get_student_count()} étudiants")
        
        # Initialiser le pipeline de reconnaissance
        logger.info("Initialisation du pipeline de reconnaissance...")
        self.pipeline = FacePipeline()
        logger.info("Pipeline initialisé")
        
        # Initialiser le détecteur d'anti-spoofing
        logger.info("Initialisation du détecteur d'Anti-Spoofing...")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(script_dir, "models", "silent_face_v2.onnx")
        self.anti_spoof = AntiSpoofDetector(model_path=model_path)
        
        # Initialiser la caméra
        logger.info(f"Ouverture de la caméra {camera_index}...")
        self.cap = cv2.VideoCapture(camera_index)
        
        if not self.cap.isOpened():
            raise RuntimeError(f"Impossible d'ouvrir la caméra {camera_index}")
        
        # Configurer la résolution de la caméra
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, display_size[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, display_size[1])
        
        logger.info("Caméra initialisée avec succès")
        
        # Afficher le pipeline de pointage mis à jour
        self.display_attendance_pipeline()
        
        # Variables pour le suivi des étudiants présents
        self.present_students = set()
        self.last_recognition_time = {}
        self.recognition_cooldown = 3.0  # Secondes entre deux reconnaissances du même étudiant
    
    def display_attendance_pipeline(self):
        """Affiche le pipeline de pointage actualisé pour information."""
        logger.info("=" * 70)
        logger.info("PIPELINE DE PHASE DE POINTAGE MIS À JOUR (Sécurisé avec Anti-Spoof)")
        logger.info("=" * 70)
        logger.info("1. CAMERA ➔ Capture du flux vidéo en temps réel")
        logger.info("2. MTCNN (Multi-visages) ➔ Détection de tous les visages")
        logger.info("3. ANTI-SPOOFING ➔ Détection de vivacité (Blocage photo/écran)")
        logger.info("4. ALIGNEMENT ➔ Alignement facial avec keypoints (Visages réels uniquement)")
        logger.info("5. ArcFace ➔ Extraction embedding facial 512-D")
        logger.info("6. Recherche FAISS ➔ Recherche dans base de données vectorielle")
        logger.info("7. MARQUAGE PRÉSENT ➔ Marquage étudiant comme présent")
        logger.info("=" * 70)
    
    def process_frame(self, frame):
        """
        Traite une frame vidéo pour détecter, vérifier la vivacité et reconnaître les visages.
        
        Args:
            frame (np.ndarray): Frame vidéo en format BGR
        
        Returns:
            tuple: (frame_processed, detected_faces)
        """
        # ÉTAPE 1: CAMERA - Frame déjà capturée
        
        # ÉTAPE 2: MTCNN (Multi-visages) - Détection de tous les visages dans la frame
        faces = self.pipeline.detector.detect_faces(frame)
        if len(faces) > 0:
            logger.info(f"MTCNN: {len(faces)} visage(s) détecté(s)")
        
        detected_info = []
        
        for face in faces:
            bbox = face['box']
            keypoints = face.get('keypoints', None)
            confidence = face.get('confidence', 0.0)
            
            x, y, w, h = bbox
            
            # ----------------------------------------------------------------
            # ÉTAPE 3: BARRIÈRE ANTI-SPOOFING (Vérification de vivacité)
            # ----------------------------------------------------------------
            is_real, spoof_score = self.anti_spoof.is_real(frame, bbox, threshold=self.spoof_threshold)
            
            if not is_real:
                logger.warning(f"🚨 TENTATIVE DE FRAUDE DÉTECTÉE ! Score de vivacité : {spoof_score:.4f}")
                
                # Dessiner un cadre ROUGE d'alerte critique
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 3)
                label = f"SPOOF / PHOTO ({spoof_score:.2f})"
                cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                
                detected_info.append({
                    'name': 'FRAUDE DETECTEE',
                    'matricule': 'N/A',
                    'similarity': None,
                    'bbox': bbox,
                    'recognized': False,
                    'spoof': True
                })
                continue  # COURT-CIRCUIT : On passe immédiatement au visage suivant (pas d'ArcFace/FAISS)
            
            # Si le visage est validé comme RÉEL, on applique un cadre VERT
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            try:
                # ÉTAPE 4: ALIGNEMENT - Alignement du visage avec MediaPipe/MTCNN keypoints
                aligned_face = self.pipeline.align_face(frame, bbox, keypoints=keypoints)
                logger.debug(f"Alignement: Visage aligné avec succès (shape: {aligned_face.shape})")
                
                # ÉTAPE 5: ArcFace - Extraction de l'embedding facial 512-D
                embedding = self.pipeline.get_embedding(aligned_face)
                logger.debug(f"ArcFace: Embedding extrait (dimension: {embedding.shape})")
                
                # ÉTAPE 6: Recherche FAISS - Recherche du visage dans la base de données vectorielle
                result = self.db.search_face(embedding, threshold=self.threshold)
                logger.debug(f"Recherche FAISS: Résultat = {result is not None}")
                
                current_time = time.time()
                
                if result:
                    student_info = result['metadata']
                    similarity = result['similarity']
                    student_id = result['id']
                    
                    # Vérifier le cooldown pour éviter les reconnaissances multiples saccadées
                    if student_id not in self.last_recognition_time or \
                       (current_time - self.last_recognition_time[student_id]) > self.recognition_cooldown:
                        
                        # ÉTAPE 7: MARQUAGE PRÉSENT - Marquer l'étudiant comme présent
                        self.present_students.add(student_id)
                        self.last_recognition_time[student_id] = current_time
                        logger.info(f"Marquage Présent: Étudiant {student_info['prenom']} {student_info['nom']} marqué PRÉSENT")
                        
                        # Informations sur l'étudiant reconnu
                        name = f"{student_info['prenom']} {student_info['nom']}"
                        matricule = student_info['matricule']
                        
                        detected_info.append({
                            'name': name,
                            'matricule': matricule,
                            'similarity': similarity,
                            'bbox': bbox,
                            'recognized': True,
                            'spoof': False
                        })
                        
                        # Dessiner les informations de validation sur la frame
                        label = f"{name} ({matricule}) - {similarity:.2f}"
                        cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                                    0.6, (0, 255, 0), 2)
                        logger.info(f"Visage reconnu: {name} (Matricule: {matricule}, Similarité: {similarity:.4f})")
                    else:
                        # Étudiant déjà reconnu récemment
                        name = f"{student_info['prenom']} {student_info['nom']}"
                        label = f"{name} (deja compte)"
                        cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                                    0.6, (255, 255, 0), 2)
                else:
                    # Visage réel mais non présent dans la base FAISS
                    detected_info.append({
                        'name': 'Inconnu',
                        'matricule': 'N/A',
                        'similarity': None,
                        'bbox': bbox,
                        'recognized': False,
                        'spoof': False
                    })
                    
                    label = f"Inconnu - {confidence:.2f}"
                    cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                               0.6, (0, 0, 255), 2)
                    
            except Exception as e:
                logger.error(f"Erreur lors du traitement d'un visage: {e}")
                label = "Erreur traitement"
                cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                            0.6, (255, 0, 255), 2)
        
        return frame, detected_info
    
    def run_attendance_session(self, duration_minutes=60, output_csv=None):
        """
        Lance une session de pointage avec caméra.
        """
        logger.info("=" * 70)
        logger.info("DÉBUT DE LA SESSION DE POINTAGE SÉCURISÉE - UCC")
        logger.info("=" * 70)
        logger.info(f"Durée: {duration_minutes} minutes")
        logger.info(f"Seuil de reconnaissance: {self.threshold}")
        logger.info(f"Étudiants dans la base: {self.db.get_student_count()}")
        logger.info("Pipeline actif: CAMERA ➔ MTCNN ➔ ANTI-SPOOF ➔ ALIGNEMENT ➔ ArcFace ➔ FAISS ➔ PRÉSENT")
        logger.info("=" * 70)
        
        # Générer le nom du fichier CSV si non spécifié
        if output_csv is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_csv = f"attendance_camera_{timestamp}.csv"
        
        # Forcer le stockage organisé à l'intérieur du dossier 'reports'
        os.makedirs("reports", exist_ok=True)
        if not output_csv.startswith("reports/") and not os.path.isabs(output_csv):
            output_csv = os.path.join("reports", output_csv)
        
        # Timer pour la durée de la session
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        # Compteur de frames et FPS
        frame_count = 0
        fps_start_time = time.time()
        fps_frame_count = 0
        fps = 0.0
        
        try:
            while True:
                # Lire une frame de la caméra
                ret, frame = self.cap.read()
                
                if not ret:
                    logger.error("Impossible de lire la frame de la caméra")
                    break
                
                # Vérifier si la session est terminée
                current_time = time.time()
                if current_time >= end_time:
                    logger.info("Session terminée (durée écoulée)")
                    break
                
                # Traiter la frame (Détection -> Anti-Spoof -> Alignement -> Extraction -> FAISS)
                frame_processed, detected_info = self.process_frame(frame)
                
                # Calculer les FPS de manière robuste
                fps_frame_count += 1
                if current_time - fps_start_time >= 1.0:
                    fps = fps_frame_count / (current_time - fps_start_time)
                    fps_frame_count = 0
                    fps_start_time = current_time
                
                # Afficher la bannière d'information sur le flux
                time_remaining = int(end_time - current_time)
                info_text = f"Temps restant: {time_remaining//60}:{time_remaining%60:02d} | Presents: {len(self.present_students)} | FPS: {fps:.1f}"
                cv2.putText(frame_processed, info_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                            0.7, (255, 255, 255), 2)
                
                # Afficher la frame à l'écran
                cv2.imshow('Pointage Facial Securise - UCC', frame_processed)
                frame_count += 1
                
                # ÉCOUTE DES TOUCHES (Optimisée pour éviter les pertes de pression)
                key = cv2.waitKey(1) & 0xFF
                
                # Quitter avec la touche 'q'
                if key == ord('q'):
                    logger.info("Session interrompue par l'utilisateur (Touche Q)")
                    break
                
                # Sauvegarder manuellement avec la touche 's' tout en continuant
                if key == ord('s'):
                    self.save_attendance_report(output_csv)
                    logger.info(f"Rapport intermédiaire sauvegardé temporairement dans {output_csv}")
                
        except KeyboardInterrupt:
            logger.info("Session interrompue (Ctrl+C)")
        
        finally:
            # Libérer les ressources via la méthode de nettoyage
            self.cleanup()
            
            # Sauvegarder le rapport final nominatif
            self.save_attendance_report(output_csv)
            
            logger.info("=" * 60)
            logger.info("SESSION DE POINTAGE TERMINÉE")
            logger.info(f"Total frames traitées: {frame_count}")
            logger.info(f"Total étudiants uniques présents: {len(self.present_students)}")
            logger.info(f"Rapport final CSV sauvegardé: {output_csv}")
            logger.info("=" * 60)
    
    def save_attendance_report(self, output_csv):
        """
        Sauvegarde le rapport de présence dans un fichier CSV local.
        """
        import csv
        
        # Sécurité : Vérifier et créer l'arborescence parente si elle manque (ex: dossier 'reports')
        if os.path.dirname(output_csv):
            os.makedirs(os.path.dirname(output_csv), exist_ok=True)
        
        with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Matricule', 'Nom', 'Prénom', 'Statut', 'Heure de pointage']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            
            for student_id in self.present_students:
                student_info = self.db.metadata.get(student_id)
                if student_info:
                    recognition_time = self.last_recognition_time.get(student_id, time.time())
                    time_str = datetime.fromtimestamp(recognition_time).strftime("%H:%M:%S")
                    
                    writer.writerow({
                        'Matricule': student_info['matricule'],
                        'Nom': student_info['nom'],
                        'Prénom': student_info['prenom'],
                        'Statut': 'PRESENT',
                        'Heure de pointage': time_str
                    })
        
        logger.info(f"Rapport de présence actualisé avec succès: {output_csv}")
    
    def cleanup(self):
        """Libère proprement les ressources matérielles et fenêtres graphiques."""
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()
        cv2.destroyAllWindows()
        logger.info("Ressources de capture vidéo libérées.")