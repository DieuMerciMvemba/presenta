"""
Système de Pointage Facial en Temps Réel - UCC
Package pour la reconnaissance faciale avec caméra en temps réel.

Pipeline de Phase de Pointage:
CAMERA ➔ MTCNN (Multi-visages) ➔ ALIGNEMENT ➔ ArcFace ➔ Recherche FAISS ➔ Marquage Présent
"""

__version__ = "1.0"
__author__ = "UCC Technical Team"

from .realtime_detector import RealtimeFaceDetector
from .camera_attendance import main

__all__ = ['RealtimeFaceDetector', 'main']
