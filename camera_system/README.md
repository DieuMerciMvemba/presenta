# Système Complet de Reconnaissance Faciale - UCC

Système de reconnaissance faciale complet pour l'Université Catholique du Congo (UCC) avec deux phases principales :
1. **Phase d'Enrôlement** (Une seule fois par étudiant)
2. **Phase de Pointage** (À chaque début de cours)

## 📋 Pipelines du Système

### Phase d'Enrôlement (Une seule fois par étudiant) :
```
Photo d'identité ➔ MTCNN ➔ Alignement ➔ ArcFace ➔ Stockage dans le fichier FAISS (.index + .pkl)
```

### Phase de Pointage (À chaque début de cours) :
```
CAMERA ➔ MTCNN (Multi-visages) ➔ Alignement ➔ ArcFace ➔ Recherche FAISS ➔ Marquage Présent
```

## 🚀 Installation

Assurez-vous d'avoir Python 3.11+ et les bibliothèques requises installées :
- opencv-python
- mtcnn
- mediapipe
- insightface
- onnxruntime
- faiss-cpu

## 📖 Utilisation

### Phase d'Enrôlement - Inscrire un nouvel étudiant

#### Méthode 1 : Interface Graphique (Recommandée)
```bash
# Lancer l'interface graphique
python enrollment_gui.py

# Ou utiliser le raccourci Windows
lancer_gui.bat
```

#### Méthode 2 : Ligne de commande
```bash
# Inscrire un étudiant avec sa photo d'identité
python enroll.py enroll --matricule "UCC2024001" --nom "Doe" --prenom "John" --photo "photo.jpg"
```

### Phase de Pointage - Deux méthodes disponibles

#### Méthode 1 : Pointage avec caméra en temps réel

```bash
# Lancer une session de pointage avec caméra (60 minutes par défaut)
python camera_attendance.py

# Session de 30 minutes
python camera_attendance.py --duration 30

# Avec seuil personnalisé
python camera_attendance.py --threshold 0.5
```

#### Méthode 2 : Pointage avec photo de groupe

```bash
# Vérifier la présence à partir d'une photo de groupe
python enroll.py attendance --photo "classe_photo.jpg"

# Avec seuil personnalisé
python enroll.py attendance --photo "classe_photo.jpg" --threshold 0.5
```

## 📁 Structure du Projet

```
camera_system/
├── enrollment_gui.py          # Interface graphique d'enrôlement
├── launcher_gui.bat           # Raccourci Windows pour l'interface graphique
├── enroll.py                  # Phase d'Enrôlement (ligne de commande)
├── camera_attendance.py       # Phase de Pointage avec caméra
├── realtime_detector.py       # Module de détection en temps réel
├── vector_db.py               # Base de données FAISS
├── pipeline.py                # Pipeline de traitement facial
├── README.md                  # Documentation technique
├── GUIDE_UTILISATION.md       # Guide d'utilisation complet
├── __init__.py                # Package Python
├── facerec_faiss.index       # Index FAISS (créé automatiquement)
└── students_metadata.pkl     # Métadonnées (créé automatiquement)
```

Le système suit précisément ce pipeline à chaque début de cours :

```
CAMERA ➔ MTCNN (Multi-visages) ➔ ALIGNEMENT ➔ ArcFace ➔ Recherche FAISS ➔ Marquage Présent
```

### Étapes détaillées :

1. **CAMERA** - Capture du flux vidéo en temps réel
   - Utilise OpenCV pour capturer les frames de la caméra
   - Résolution configurable (défaut: 1280x720)
   - Support de multiples caméras

2. **MTCNN (Multi-visages)** - Détection de tous les visages dans la frame
   - Algorithme MTCNN pour la détection faciale multi-visages
   - Détection simultanée de plusieurs visages dans une seule frame
   - Extraction des boîtes englobantes et points clés

3. **ALIGNEMENT** - Alignement facial avec keypoints
   - Utilisation des points clés de MTCNN (yeux, nez, bouche)
   - Alignement géométrique pour normaliser l'orientation du visage
   - Redimensionnement à 112x112 pixels pour ArcFace

4. **ArcFace** - Extraction de l'embedding facial 512-D
   - Modèle InsightFace ArcFace (buffalo_l)
   - Extraction de vecteur caractéristique de 512 dimensions
   - Normalisation des embeddings pour la comparaison

5. **Recherche FAISS** - Recherche dans la base de données vectorielle
   - Recherche du vecteur le plus proche dans l'index FAISS
   - Calcul de la distance L2 pour la similarité
   - Application du seuil de reconnaissance (défaut: 0.6)

6. **Marquage Présent** - Marquage automatique de la présence
   - Ajout de l'étudiant à la liste des présents
   - Horodatage précis de la reconnaissance
   - Gestion du cooldown pour éviter les doublons

## 🚀 Installation

Assurez-vous que le système principal de reconnaissance faciale est déjà configuré dans le dossier parent.

### Prérequis :
- Python 3.11+ ou 3.13
- OpenCV installé (`pip install opencv-python`)
- Les modules du système principal (`vector_db.py`, `pipeline.py`)
- Base de données FAISS avec étudiants inscrits

## 📖 Utilisation

### Lancer une session de pointage par défaut (60 minutes) :
```bash
cd camera_system
python camera_attendance.py
```

### Lancer une session de 30 minutes :
```bash
python camera_attendance.py --duration 30
```

### Utiliser une caméra spécifique :
```bash
python camera_attendance.py --camera 1
```

### Ajuster le seuil de reconnaissance :
```bash
python camera_attendance.py --threshold 0.5
```

### Spécifier le fichier de sortie :
```bash
python camera_attendance.py --output presence_cours_1.csv
```

### Changer la résolution de la fenêtre :
```bash
python camera_attendance.py --width 1920 --height 1080
```

## 🎮 Contrôles pendant la session (Caméra)

- **'q'** - Quitter la session
- **'s'** - Sauvegarder le rapport intermédiaire

## ⚙️ Paramètres Configurables (Caméra)

| Paramètre | Défaut | Description |
|-----------|--------|-------------|
| `--camera` | 0 | Index de la caméra |
| `--duration` | 60 | Durée en minutes |
| `--threshold` | 0.6 | Seuil de reconnaissance (0.0-1.0) |
| `--width` | 1280 | Largeur de la fenêtre |
| `--height` | 720 | Hauteur de la fenêtre |
| `--output` | auto | Fichier CSV de sortie |

## ⚙️ Paramètres Configurables (Enrôlement)

| Paramètre | Requis | Description |
|-----------|--------|-------------|
| `--matricule` | Oui | Matricule de l'étudiant |
| `--nom` | Oui | Nom de l'étudiant |
| `--prenom` | Oui | Prénom de l'étudiant |
| `--photo` | Oui | Chemin vers la photo d'identité |

## 🔧 Fonctionnalités Avancées

- **'q'** - Quitter la session
- **'s'** - Sauvegarder le rapport intermédiaire

## 📁 Structure du Projet

```
camera_system/
├── realtime_detector.py      # Module de détection en temps réel
├── camera_attendance.py      # Script principal d'exécution
├── README.md                 # Documentation
└── (accès aux modules parent)
    ├── ../vector_db.py       # Base de données FAISS
    ├── ../pipeline.py        # Pipeline de traitement facial
    └── ../facerec_faiss.index # Index FAISS
```

## 📊 Rapport de Présence

Le système génère automatiquement un fichier CSV avec les informations suivantes :

- **Matricule** : Identifiant unique de l'étudiant
- **Nom** : Nom de l'étudiant
- **Prénom** : Prénom de l'étudiant
- **Statut** : "PRESENT" si reconnu
- **Heure de pointage** : Horodatage précis de la reconnaissance

### Exemple de rapport :
```csv
Matricule,Nom,Prénom,Statut,Heure de pointage
UCC2024001,Doe,John,PRESENT,08:15:32
UCC2024002,Smith,Jane,PRESENT,08:15:45
UCC2024003,Johnson,Bob,PRESENT,08:16:01
```

## ⚙️ Paramètres Configurables

| Paramètre | Défaut | Description |
|-----------|--------|-------------|
| `--camera` | 0 | Index de la caméra |
| `--duration` | 60 | Durée en minutes |
| `--threshold` | 0.6 | Seuil de reconnaissance (0.0-1.0) |
| `--width` | 1280 | Largeur de la fenêtre |
| `--height` | 720 | Hauteur de la fenêtre |
| `--output` | auto | Fichier CSV de sortie |

## 🔧 Fonctionnalités Avancées

### Détection Multi-Visages
Le système peut détecter et reconnaître plusieurs visages simultanément dans la même frame, idéal pour les salles de classe.

### Cooldown de Reconnaissance
Pour éviter les marquages multiples du même étudiant, un système de cooldown de 3 secondes est implémenté.

### Affichage en Temps Réel
- Boîtes englobantes vertes pour les visages reconnus
- Informations d'identification affichées (Nom, Matricule, Distance)
- Compteur d'étudiants présents en temps réel
- Temps restant de la session

### Gestion des Erreurs
- Gestion robuste des erreurs de traitement
- Logs détaillés pour le débogage
- Reprise automatique en cas d'erreur temporaire

## 📝 Logs et Débogage

Le système génère des logs détaillés pour chaque étape du pipeline :

```
INFO: MTCNN: 3 visage(s) détecté(s)
DEBUG: Alignement: Visage aligné avec succès (shape: (112, 112, 3))
DEBUG: ArcFace: Embedding extrait (dimension: (512,))
DEBUG: Recherche FAISS: Résultat = True
INFO: Marquage Présent: Étudiant John Doe marqué PRÉSENT
```

## 🔒 Sécurité et Confidentialité

- **100% local** : Aucune donnée n'est envoyée vers des serveurs externes
- **Air-gapped** : Fonctionne entièrement hors-ligne
- **Embeddings sécurisés** : Les embeddings faciaux ne peuvent pas être reconvertis en images
- **Base de données locale** : FAISS + pickle pour stockage local uniquement

## ⚡ Performance

- **Temps réel** : Traitement frame par frame avec OpenCV
- **Optimisé CPU** : Utilisation de CPUExecutionProvider pour InsightFace
- **Multi-visages** : Détection et reconnaissance simultanée de plusieurs visages
- **FAISS rapide** : Recherche vectorielle optimisée même avec milliers d'étudiants

## 🛠️ Dépannage

### Problème : "Impossible d'ouvrir la caméra"
- Vérifiez que la caméra est connectée
- Essayez différents indices de caméra (--camera 1, --camera 2)
- Vérifiez les permissions d'accès à la caméra

### Problème : "Aucun visage détecté"
- Assurez-vous que l'éclairage est suffisant
- Vérifiez que les visages sont bien visibles
- Ajustez la position de la caméra

### Problème : "Faible taux de reconnaissance"
- Ajustez le seuil de reconnaissance (--threshold)
- Assurez-vous que les étudiants sont bien inscrits dans la base
- Vérifiez la qualité des photos d'inscription

### Problème : "Reconnaissances multiples du même étudiant"
- Le système de cooldown de 3 secondes devrait éviter cela
- Vérifiez les logs pour confirmer le fonctionnement du cooldown

## 📚 Intégration avec le Système Principal

Ce système de caméra utilise les modules du système principal :
- `vector_db.py` - Base de données FAISS partagée
- `pipeline.py` - Pipeline de traitement facial partagé

Les étudiants inscrits via le système principal sont automatiquement reconnus par le système de caméra.

## 🎓 Cas d'Usage - UCC

Ce système est conçu pour l'Université Catholique du Congo (UCC) pour :
- Automatiser le pointage au début de chaque cours
- Éliminer les feuilles de présence papier
- Réduire le temps de prise de présence
- Améliorer la précision du suivi des étudiants
- Fonctionner hors-ligne dans les salles de classe

## 📞 Support

Pour toute question ou problème, consultez la documentation du système principal ou contactez l'équipe technique de l'UCC.

---

**Version** : 1.0  
**Date** : 2026-06-11  
**Institution** : Université Catholique du Congo (UCC)