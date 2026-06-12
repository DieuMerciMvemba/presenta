import cv2
import numpy as np
import os
import logging

logger = logging.getLogger(__name__)

class AntiSpoofDetector:
    """
    Détecteur de vivacité (Liveness Detection) basé sur Silent-Face-Anti-Spoofing.
    Idéal pour une exécution CPU locale et rapide.
    """
    def __init__(self, model_path="models/silent_face_v2.onnx"):
        self.model_path = model_path
        
        if not os.path.exists(model_path):
            logger.warning(f"⚠️ Modèle Anti-Spoofing introuvable à '{model_path}'.")
            logger.warning("Le système fonctionnera en mode BYPASS (pas de vérification de vivacité).")
            self.net = None
        else:
            # Chargement du modèle ONNX via OpenCV DNN
            self.net = cv2.dnn.readNetFromONNX(model_path)
            # Forcer l'exécution sur CPU pour coller à ton architecture locale
            self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
            self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
            logger.info("✅ Modèle Anti-Spoofing ONNX chargé avec succès sur CPU.")

    def is_real(self, frame, bbox, threshold=0.90):
        """
        Analyse si le visage dans la bounding box est réel ou une tentative de fraude.
        """
        if self.net is None:
            return True, 1.0  # Bypass si le modèle n'est pas là

        h, w, _ = frame.shape
        x, y, wb, hb = bbox

        # Élargissement de la zone (le modèle a besoin du contexte autour du visage)
        cx, cy = x + wb // 2, y + hb // 2
        side = int(max(wb, hb) * 2.7)  # Ratio standard pour Silent-Face

        x1 = max(0, cx - side // 2)
        y1 = max(0, cy - side // 2)
        x2 = min(w, cx + side // 2)
        y2 = min(h, cy + side // 2)

        face_crop = frame[y1:y2, x1:x2]
        if face_crop.size == 0 or face_crop.shape[0] < 10 or face_crop.shape[1] < 10:
            return False, 0.0

        # Préparation du blob (Silent-Face prend généralement du 80x80 ou 128x128)
        # On utilise 80x80 ici, à adapter selon la version de ton modèle
        blob = cv2.dnn.blobFromImage(face_crop, scalefactor=1.0, size=(80, 80), swapRB=True, crop=False)
        
        self.net.setInput(blob)
        preds = self.net.forward()

        # Calcul du Softmax sur les sorties du modèle
        # Output type: [Fake_Score, Real_Score] ou [Fake, Real, Fake_v2]
        exp_preds = np.exp(preds - np.max(preds))
        prob = exp_preds / np.sum(exp_preds)
        
        # Sur le modèle Minivision standard, l'index 1 correspond au score "Vrai Visage"
        real_score = float(prob[0][1]) 
        
        return real_score > threshold, real_score