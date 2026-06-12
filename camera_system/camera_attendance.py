"""
Script principal pour le système de pointage avec caméra.
UCC - Système de Reconnaissance Faciale en Temps Réel
"""

import argparse
import sys
import os
import logging

from realtime_detector import RealtimeFaceDetector

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    """Fonction principale pour lancer le système de pointage avec caméra."""
    parser = argparse.ArgumentParser(
        description="Système de pointage facial en temps réel avec caméra - UCC",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  # Lancer une session de pointage de 60 minutes (défaut)
  python camera_attendance.py
  
  # Lancer une session de 30 minutes
  python camera_attendance.py --duration 30
  
  # Utiliser la caméra 1 au lieu de la caméra 0
  python camera_attendance.py --camera 1
  
  # Ajuster le seuil de reconnaissance
  python camera_attendance.py --threshold 0.5
  
  # Spécifier le fichier de sortie
  python camera_attendance.py --output ma_presence.csv

Contrôles pendant la session:
  - 'q': Quitter la session
  - 's': Sauvegarder le rapport intermédiaire
        """
    )
    
    parser.add_argument('--camera', type=int, default=0, 
                       help='Index de la caméra à utiliser (défaut: 0)')
    parser.add_argument('--duration', type=int, default=60,
                       help='Durée de la session en minutes (défaut: 60)')
    parser.add_argument('--threshold', type=float, default=0.5,
                       help='Seuil de reconnaissance (défaut: 0.5 - recommandé pour meilleure robustesse)')
    parser.add_argument('--output', type=str, default=None,
                       help='Chemin du fichier CSV de sortie (défaut: auto-généré)')
    parser.add_argument('--width', type=int, default=1280,
                       help='Largeur de la fenêtre (défaut: 1280)')
    parser.add_argument('--height', type=int, default=720,
                       help='Hauteur de la fenêtre (défaut: 720)')
    
    args = parser.parse_args()
    
    try:
        logger.info("=" * 70)
        logger.info("SYSTÈME DE POINTAGE AVEC CAMÉRA - UCC")
        logger.info("=" * 70)
        logger.info(f"Caméra: {args.camera}")
        logger.info(f"Durée: {args.duration} minutes")
        logger.info(f"Seuil de reconnaissance: {args.threshold}")
        logger.info(f"Résolution: {args.width}x{args.height}")
        if args.output:
            logger.info(f"Fichier de sortie: {args.output}")
        else:
            logger.info("Fichier de sortie: Auto-généré")
        logger.info("=" * 70)
        
        # Créer le détecteur en temps réel
        detector = RealtimeFaceDetector(
            camera_index=args.camera,
            recognition_threshold=args.threshold,
            display_size=(args.width, args.height)
        )
        
        # Lancer la session de pointage
        detector.run_attendance_session(
            duration_minutes=args.duration,
            output_csv=args.output
        )
        
        logger.info("Système de pointage terminé avec succès")
        
    except KeyboardInterrupt:
        logger.info("Interruption par l'utilisateur")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
