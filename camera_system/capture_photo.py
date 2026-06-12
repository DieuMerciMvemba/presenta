"""
Script pour capturer une photo depuis la webcam, la renommer et la sauvegarder dans le Dataset.
"""

import cv2
import os
import sys
from datetime import datetime

def capture_and_save_photo():
    """Capture une photo depuis la webcam et la sauvegarde dans le Dataset."""
    
    # Définir le chemin du dossier Dataset
    dataset_dir = "D:/cnn_sys/Dataset"
    
    # Vérifier si le dossier Dataset existe
    if not os.path.exists(dataset_dir):
        os.makedirs(dataset_dir)
        print(f"Dossier Dataset créé: {dataset_dir}")
    
    # Initialiser la webcam
    print("Initialisation de la webcam...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Erreur: Impossible d'ouvrir la webcam")
        sys.exit(1)
    
    print("Webcam initialisée avec succès")
    print("=" * 60)
    print("Instructions:")
    print("- Appuyez sur 'ESPACE' pour capturer la photo")
    print("- Appuyez sur 'q' ou 'ESC' pour quitter sans capturer")
    print("=" * 60)
    
    captured = False
    frame = None
    
    while not captured:
        # Lire un frame de la webcam
        ret, frame = cap.read()
        
        if not ret:
            print("Erreur: Impossible de lire le frame")
            break
        
        # Afficher le frame
        cv2.imshow('Capture Photo - Espace: Capturer | q/ESC: Quitter', frame)
        
        # Attendre une touche
        key = cv2.waitKey(1) & 0xFF
        
        # Capturer avec ESPACE
        if key == ord(' '):
            captured = True
            print("Photo capturée!")
        
        # Quitter avec q ou ESC
        elif key == ord('q') or key == 27:
            print("Annulation par l'utilisateur")
            cap.release()
            cv2.destroyAllWindows()
            sys.exit(0)
    
    # Libérer la webcam
    cap.release()
    cv2.destroyAllWindows()
    
    if not captured or frame is None:
        print("Erreur: Aucune photo capturée")
        sys.exit(1)
    
    # Demander le nom du fichier
    print("=" * 60)
    print("Entrez le nom du fichier (sans extension)")
    print("Exemple: dieudonne, john_doe, photo_001")
    print("=" * 60)
    
    filename = input("Nom du fichier: ").strip()
    
    if not filename:
        print("Erreur: Nom de fichier vide")
        sys.exit(1)
    
    # Nettoyer le nom du fichier (remplacer les espaces par des underscores)
    filename = filename.replace(" ", "_")
    
    # Générer le chemin complet
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    full_filename = f"{filename}_{timestamp}.jpg"
    output_path = os.path.join(dataset_dir, full_filename)
    
    # Sauvegarder l'image
    success = cv2.imwrite(output_path, frame)
    
    if success:
        print("=" * 60)
        print("Photo sauvegardée avec succès!")
        print(f"Chemin: {output_path}")
        print("=" * 60)
    else:
        print("Erreur: Impossible de sauvegarder la photo")
        sys.exit(1)

if __name__ == "__main__":
    try:
        capture_and_save_photo()
    except KeyboardInterrupt:
        print("\nInterruption par l'utilisateur")
        sys.exit(0)
    except Exception as e:
        print(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
