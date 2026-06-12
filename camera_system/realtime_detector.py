"""
Module de détection faciale en temps réel avec caméra.
Utilise OpenCV pour capturer le flux vidéo et le pipeline existant pour la reconnaissance.
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RealtimeFaceDetector:
    """
    Classe pour la détection faciale en temps réel avec caméra.
    
    Pipeline de Phase de Pointage (À chaque début de cours):
    1. CAMERA ➔ Capture du flux vidéo en temps réel
    2. MTCNN (Multi-visages) ➔ Détection de tous les visages dans la frame
    3. ALIGNEMENT ➔ Alignement facial avec MediaPipe/MTCNN keypoints
    4. ArcFace ➔ Extraction de l'embedding facial 512-D
    5. Recherche FAISS ➔ Recherche dans la base de données vectorielle
    6. MARQUAGE PRÉSENT ➔ Marquage de l'étudiant comme présent
    """
    
    def __init__(self, camera_index=0, recognition_threshold=0.5, display_size=(1280, 720)):
        """
        Initialise le détecteur facial en temps réel.
        
        Args:
            camera_index (int): Index de la caméra (défaut: 0)
            recognition_threshold (float): Seuil de reconnaissance (défaut: 0.5 - recommandé pour meilleure robustesse)
            display_size (tuple): Taille de la fenêtre d'affichage (défaut: 1280x720)
        """
        self.camera_index = camera_index
        self.threshold = recognition_threshold
        self.display_size = display_size
        
        # Initialiser la base de données
        logger.info("Chargement de la base de données...")
        self.db = LocalVectorDB()
        logger.info(f"Base de données chargée: {self.db.get_student_count()} étudiants")
        
        # Initialiser le pipeline de reconnaissance
        logger.info("Initialisation du pipeline de reconnaissance...")
        self.pipeline = FacePipeline()
        logger.info("Pipeline initialisé")
        
        # Initialiser la caméra
        logger.info(f"Ouverture de la caméra {camera_index}...")
        self.cap = cv2.VideoCapture(camera_index)
        
        if not self.cap.isOpened():
            raise RuntimeError(f"Impossible d'ouvrir la caméra {camera_index}")
        
        # Configurer la résolution de la caméra
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, display_size[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, display_size[1])
        
        logger.info("Caméra initialisée avec succès")
        
        # Afficher le pipeline de pointage
        self.display_attendance_pipeline()
        
        # Variables pour le suivi des étudiants présents
        self.present_students = set()
        self.last_recognition_time = {}
        self.recognition_cooldown = 3.0  # Secondes entre deux reconnaissances du même étudiant
    
    def display_attendance_pipeline(self):
        """Affiche le pipeline de pointage pour information."""
        logger.info("=" * 70)
        logger.info("PIPELINE DE PHASE DE POINTAGE (À chaque début de cours)")
        logger.info("=" * 70)
        logger.info("1. CAMERA ➔ Capture du flux vidéo en temps réel")
        logger.info("2. MTCNN (Multi-visages) ➔ Détection de tous les visages")
        logger.info("3. ALIGNEMENT ➔ Alignement facial avec keypoints")
        logger.info("4. ArcFace ➔ Extraction embedding facial 512-D")
        logger.info("5. Recherche FAISS ➔ Recherche dans base de données vectorielle")
        logger.info("6. MARQUAGE PRÉSENT ➔ Marquage étudiant comme présent")
        logger.info("=" * 70)
    
    def process_frame(self, frame):
        """
        Traite une frame vidéo pour détecter et reconnaître les visages.
        Suit précisément le pipeline: camera ➔ MTCNN (Multi-visages) ➔ Alignement ➔ ArcFace ➔ Recherche FAISS ➔ Marquage Présent
        
        Args:
            frame (np.ndarray): Frame vidéo en format BGR
        
        Returns:
            tuple: (frame_processed, detected_faces) où detected_faces est une liste de dict avec les informations
        """
        # ÉTAPE 1: CAMERA - Frame déjà capturée
        
        # ÉTAPE 2: MTCNN (Multi-visages) - Détection de tous les visages dans la frame
        faces = self.pipeline.detector.detect_faces(frame)
        logger.info(f"MTCNN: {len(faces)} visage(s) détecté(s)")
        
        detected_info = []
        
        for face in faces:
            bbox = face['box']
            keypoints = face.get('keypoints', None)
            confidence = face.get('confidence', 0.0)
            
            # Dessiner la boîte englobante (avant traitement pour éviter les erreurs)
            x, y, w, h = bbox
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            try:
                # ÉTAPE 3: ALIGNEMENT - Alignement du visage avec MediaPipe/MTCNN keypoints
                aligned_face = self.pipeline.align_face(frame, bbox, keypoints=keypoints)
                logger.debug(f"Alignement: Visage aligné avec succès (shape: {aligned_face.shape})")
                
                # ÉTAPE 4: ArcFace - Extraction de l'embedding facial 512-D
                embedding = self.pipeline.get_embedding(aligned_face)
                logger.debug(f"ArcFace: Embedding extrait (dimension: {embedding.shape})")
                
                # ÉTAPE 5: Recherche FAISS - Recherche du visage dans la base de données vectorielle
                result = self.db.search_face(embedding, threshold=self.threshold)
                logger.debug(f"Recherche FAISS: Résultat = {result is not None}")
                
                current_time = time.time()
                
                if result:
                    student_info = result['metadata']
                    similarity = result['similarity']
                    student_id = result['id']
                    
                    # Vérifier le cooldown pour éviter les reconnaissance multiples
                    if student_id not in self.last_recognition_time or \
                       (current_time - self.last_recognition_time[student_id]) > self.recognition_cooldown:
                        
                        # ÉTAPE 6: MARQUAGE PRÉSENT - Marquer l'étudiant comme présent
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
                            'recognized': True
                        })
                        
                        # Dessiner les informations sur la frame
                        label = f"{name} ({matricule}) - {similarity:.2f}"
                        cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                                   0.6, (0, 255, 0), 2)
                        logger.info(f"Visage reconnu: {name} (Matricule: {matricule}, Similarité: {similarity:.4f})")
                    else:
                        # Étudiant déjà reconnu récemment
                        name = f"{student_info['prenom']} {student_info['nom']}"
                        label = f"{name} (déjà compté)"
                        cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                                   0.6, (255, 255, 0), 2)
                else:
                    # Visage non reconnu
                    detected_info.append({
                        'name': 'Inconnu',
                        'matricule': 'N/A',
                        'similarity': None,
                        'bbox': bbox,
                        'recognized': False
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
        Suit le pipeline: camera ➔ MTCNN (Multi-visages) ➔ Alignement ➔ ArcFace ➔ Recherche FAISS ➔ Marquage Présent
        
        Args:
            duration_minutes (int): Durée de la session en minutes (défaut: 60)
            output_csv (str): Chemin du fichier CSV de sortie (défaut: auto-généré)
        """
        logger.info("=" * 70)
        logger.info("DÉBUT DE LA SESSION DE POINTAGE - UCC")
        logger.info("=" * 70)
        logger.info(f"Durée: {duration_minutes} minutes")
        logger.info(f"Seuil de reconnaissance: {self.threshold}")
        logger.info(f"Étudiants dans la base: {self.db.get_student_count()}")
        logger.info("Pipeline actif: CAMERA ➔ MTCNN ➔ ALIGNEMENT ➔ ArcFace ➔ FAISS ➔ PRÉSENT")
        logger.info("=" * 70)
        
        # Générer le nom du fichier CSV si non spécifié
        if output_csv is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_csv = f"attendance_camera_{timestamp}.csv"
        
        # Timer pour la durée de la session
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        # Compteur de frames
        frame_count = 0
        fps_start_time = time.time()
        fps_frame_count = 0
        
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
                
                # Traiter la frame
                frame_processed, detected_info = self.process_frame(frame)
                
                # Calculer et afficher les FPS
                fps_frame_count += 1
                if current_time - fps_start_time >= 1.0:
                    fps = fps_frame_count / (current_time - fps_start_time)
                    fps_frame_count = 0
                    fps_start_time = current_time
                
                # Afficher les informations sur la frame
                time_remaining = int(end_time - current_time)
                info_text = f"Pointage en cours - Temps restant: {time_remaining//60}:{time_remaining%60:02d} | Étudiants présents: {len(self.present_students)}"
                cv2.putText(frame_processed, info_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                           0.7, (255, 255, 255), 2)
                
                # Afficher la frame
                cv2.imshow('Pointage Facial en Temps Réel - UCC', frame_processed)
                frame_count += 1
                
                # Quitter avec la touche 'q'
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    logger.info("Session interrompue par l'utilisateur")
                    break
                
                # Quitter avec la touche 's' pour sauvegarder et continuer
                if cv2.waitKey(1) & 0xFF == ord('s'):
                    self.save_attendance_report(output_csv)
                    logger.info(f"Rapport sauvegardé dans {output_csv}")
                
        except KeyboardInterrupt:
            logger.info("Session interrompue (Ctrl+C)")
        
        finally:
            # Libérer les ressources
            self.cap.release()
            cv2.destroyAllWindows()
            
            # Sauvegarder le rapport final
            self.save_attendance_report(output_csv)
            
            logger.info("=" * 60)
            logger.info("SESSION DE POINTAGE TERMINÉE")
            logger.info(f"Total frames traitées: {frame_count}")
            logger.info(f"Total étudiants uniques présents: {len(self.present_students)}")
            logger.info(f"Rapport sauvegardé: {output_csv}")
            logger.info("=" * 60)
    
    def save_attendance_report(self, output_csv):
        """
        Sauvegarde le rapport de présence dans un fichier CSV.
        
        Args:
            output_csv (str): Chemin du fichier CSV de sortie
        """
        import csv
        
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
        
        logger.info(f"Rapport de présence sauvegardé: {output_csv}")
    
    def cleanup(self):
        """Libère les ressources."""
        if self.cap.isOpened():
            self.cap.release()
        cv2.destroyAllWindows()
