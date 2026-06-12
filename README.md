# Système de Reconnaissance Faciale pour la Présence - UCC

Système de reconnaissance faciale 100% local pour remplacer les feuilles de présence traditionnelles à l'université. Ce système utilise des modèles de deep learning modernes pour détecter, aligner et reconnaître les visages des étudiants, avec détection de vivacité anti-spoofing.

## Fonctionnalités

- **Inscription d'étudiants** : Enregistrement des étudiants avec plusieurs photos d'identité (5-10 recommandées)
- **Vérification de présence par photo** : Identification automatique des étudiants présents sur des photos de groupe
- **Vérification de présence en temps réel** : Détection faciale avec caméra en direct
- **Anti-Spoofing** : Détection de vivacité pour bloquer les photos et écrans
- **Interface graphique** : GUI Tkinter pour l'enrôlement facile
- **100% local** : Aucune API cloud, tout fonctionne hors-ligne
- **Haute précision** : Utilisation de modèles state-of-the-art (MTCNN, MediaPipe, InsightFace)

## Architecture du Système

Le système est organisé en modules spécialisés :

### Structure des Dossiers

```
camera_system/
├── data/                      <-- Base de données vectorielle
│   ├── facerec_faiss.index
│   └── students_metadata.pkl
├── reports/                   <-- Rapports CSV de présence
│   └── attendance_*.csv
├── models/                     <-- Modèles ONNX
│   └── silent_face_v2.onnx
├── vector_db.py               # Base de données vectorielle FAISS
├── pipeline.py                # Pipeline de traitement facial
├── enroll.py                  # Application CLI principale
├── realtime_detector.py      # Détection en temps réel avec caméra
├── anti_spoof.py              # Détection de vivacité anti-spoofing
└── enrollment_gui.py         # Interface graphique Tkinter
```

### Modules Principaux

1. **vector_db.py** : Base de données vectorielle locale utilisant FAISS
   - Stockage des embeddings faciaux 512-D
   - Recherche rapide par similarité cosinus
   - Gestion des métadonnées des étudiants

2. **pipeline.py** : Pipeline de traitement facial en 3 étapes
   - Détection MTCNN (Multi-visages)
   - Alignement MediaPipe Face Mesh
   - Extraction InsightFace ArcFace

3. **enroll.py** : Interface CLI pour l'inscription et la présence
   - Enrôlement multi-photos avec embedding moyen
   - Vérification de présence par photo de groupe
   - Gestion des informations étudiant

4. **realtime_detector.py** : Détection faciale en temps réel
   - Capture vidéo avec OpenCV
   - Pipeline complet avec anti-spoofing
   - Génération de rapports CSV automatique

5. **anti_spoof.py** : Détection de vivacité
   - Modèle Silent-Face-Anti-Spoofing ONNX
   - Blocage des photos et écrans
   - Exécution CPU optimisée

## Prérequis

- Python 3.11+ ou 3.13
- Bibliothèques installées :
  - opencv-python
  - mtcnn
  - mediapipe
  - insightface
  - onnxruntime
  - faiss-cpu
  - numpy
  - tkinter (pour l'interface graphique)

## Installation

Les bibliothèques nécessaires sont déjà installées dans votre environnement. Si vous devez les réinstaller :

```bash
pip install opencv-python mtcnn mediapipe insightface onnxruntime faiss-cpu numpy
```

## Utilisation

### Phase d'Enrôlement (Une seule fois par étudiant)

L'enrôlement enregistre les embeddings faciaux des étudiants dans la base de données FAISS.

#### Option 1 : Interface CLI

Pour inscrire un nouvel étudiant avec plusieurs photos (recommandé) :

```bash
cd camera_system
python enroll.py enroll --matricule "UCC2024001" --nom "Doe" --prenom "John" --photos photo1.jpg photo2.jpg photo3.jpg
```

**Arguments requis :**
- `--matricule` : Matricule unique de l'étudiant
- `--nom` : Nom de l'étudiant
- `--prenom` : Prénom de l'étudiant
- `--photos` : Chemins vers les photos d'identité (5-10 recommandées)

**Angles recommandés :** Face, Gauche, Droite, Haut, Bas, Sourire, Sans sourire

#### Option 2 : Interface Graphique

```bash
cd camera_system
python enrollment_gui.py
```

L'interface graphique permet de :
- Sélectionner plusieurs photos facilement
- Visualiser les logs en temps réel
- Modifier les informations des étudiants
- Consulter la base de données

### Phase de Pointage (À chaque début de cours)

#### Option 1 : Vérification par Photo de Groupe

```bash
cd camera_system
python enroll.py attendance --photo "chemin/vers/photo_groupe.jpg"
```

**Arguments optionnels :**
- `--threshold` : Seuil de similarité cosinus (défaut: 0.5 - recommandé)

#### Option 2 : Détection en Temps Réel avec Caméra

```bash
cd camera_system
python camera_attendance.py
```

**Fonctionnalités :**
- Capture vidéo en temps réel
- Détection de vivacité anti-spoofing
- Marquage automatique des présents
- Génération de rapport CSV automatique
- Touche `q` pour quitter, `s` pour sauvegarder manuellement

### Gestion des Étudiants

#### Mettre à jour les informations

```bash
python enroll.py update --matricule "UCC2024001" --new-nom "Smith" --new-prenom "Jane"
```

#### Ajouter des photos à un étudiant existant

```bash
python enroll.py add-photos --matricule "UCC2024001" --photos new_photo1.jpg new_photo2.jpg
```

#### Remplacer toutes les photos d'un étudiant

```bash
python enroll.py add-photos --matricule "UCC2024001" --photos new_photo1.jpg new_photo2.jpg --replace
```

## Pipeline de Traitement Facial

### Phase d'Enrôlement (Une seule fois par étudiant)

```
Photos multiples (5-10 recommandées) ➔ MTCNN ➔ Alignement ➔ ArcFace ➔ Embedding Moyen ➔ Stockage FAISS
```

1. **Détection MTCNN** : Localisation des visages dans chaque photo
2. **Alignement MediaPipe** : Normalisation des angles de rotation
3. **Extraction ArcFace** : Génération d'embeddings 512-D par photo
4. **Calcul de la moyenne** : Embedding moyen pour plus de robustesse
5. **Stockage FAISS** : Sauvegarde dans l'index vectoriel

### Phase de Pointage par Photo

```
MTCNN (Multi-visages) ➔ Alignement ➔ ArcFace ➔ Recherche FAISS ➔ Marquage Présent
```

1. **MTCNN Multi-visages** : Détection de tous les visages dans la photo de groupe
2. **Alignement** : Normalisation de chaque visage détecté
3. **ArcFace** : Extraction de l'embedding facial 512-D
4. **Recherche FAISS** : Comparaison avec la base de données (similarité cosinus)
5. **Marquage Présent** : Identification et enregistrement si similarité > seuil

### Phase de Pointage en Temps Réel (avec Anti-Spoofing)

```
CAMERA ➔ MTCNN ➔ ANTI-SPOOFING ➔ ALIGNEMENT ➔ ArcFace ➔ FAISS ➔ PRÉSENT
```

1. **CAMERA** : Capture du flux vidéo en temps réel
2. **MTCNN** : Détection de tous les visages dans la frame
3. **ANTI-SPOOFING** : Vérification de vivacité (blocage photo/écran)
4. **ALIGNEMENT** : Normalisation des visages réels uniquement
5. **ArcFace** : Extraction de l'embedding facial 512-D
6. **Recherche FAISS** : Comparaison avec la base de données
7. **Marquage Présent** : Identification et enregistrement

## Fichiers Générés

### Base de Données (dossier `data/`)
- `facerec_faiss.index` : Index FAISS contenant les embeddings faciaux
- `students_metadata.pkl` : Métadonnées des étudiants (nom, prénom, matricule, nombre de photos)

### Rapports (dossier `reports/`)
- `attendance_UCC_[DATE].csv` : Rapport de présence par photo
- `attendance_camera_[DATE].csv` : Rapport de présence par caméra

### Modèles (dossier `models/`)
- `silent_face_v2.onnx` : Modèle ONNX pour l'anti-spoofing

## Rapport de Présence

Le fichier CSV généré contient les colonnes suivantes :
- `Matricule` : Identifiant unique de l'étudiant
- `Nom` : Nom de l'étudiant
- `Prénom` : Prénom de l'étudiant
- `Statut` : "PRESENT" si l'étudiant est identifié
- `Similarité` : Score de similarité cosinus (indicateur de confiance, 0.0 à 1.0)
- `Heure de pointage` : Heure de détection (pour les sessions caméra)

## Anti-Spoofing (Détection de Vivacité)

Le système inclut une protection contre les tentatives de fraude :
- **Modèle** : Silent-Face-Anti-Spoofing ONNX
- **Seuil par défaut** : 0.85 (85% de confiance requis)
- **Fonctionnement** : Analyse les textures et micro-mouvements pour distinguer les visages réels des photos/écrans
- **Comportement** : Bloque automatiquement les visages suspects et les marque comme "FRAUDE DETECTEE"

## Gestion des Erreurs

Le système inclut une gestion robuste des erreurs :
- Détection de 0 visage lors de l'inscription (message d'avertissement)
- Base de données vide lors du pointage (erreur claire)
- Échec de l'alignement (continuation avec les autres visages)
- Modèle anti-spoofing introuvable (mode BYPASS automatique)
- Chemins de fichiers incorrects (création automatique des dossiers)

## Performances

- **Base de données** : FAISS permet une recherche rapide même avec des milliers d'étudiants
- **Modèles** : Les modèles utilisés sont optimisés pour CPU
- **Seuil par défaut** : 0.5 offre un bon équilibre entre précision et rappel
- **Anti-spoofing** : Exécution CPU optimisée avec OpenCV DNN
- **Multi-photos** : L'embedding moyen améliore la robustesse de la reconnaissance

## Dépannage

### Problème : "Aucun visage détecté"
- Vérifiez que la photo est de bonne qualité
- Assurez-vous que le visage est bien visible et éclairé
- Essayez avec une photo différente

### Problème : "Plusieurs visages détectés" lors de l'inscription
- Utilisez une photo d'identité avec un seul visage
- Recadrez la photo pour ne montrer que l'étudiant

### Problème : Similarité faible (< seuil)
- Le visage peut être sous un angle différent
- L'éclairage peut être différent
- Ajustez le seuil avec l'option `--threshold`
- Ajoutez plus de photos avec différents angles

### Problème : "Modèle Anti-Spoofing introuvable"
- Vérifiez que le fichier `models/silent_face_v2.onnx` existe
- Le système fonctionnera en mode BYPASS si le modèle est absent

### Problème : Caméra ne s'ouvre pas
- Vérifiez que la caméra n'est pas utilisée par une autre application
- Essayez un index de caméra différent (ex: `--camera 1`)

## Sécurité et Confidentialité

- **100% local** : Toutes les données sont stockées localement
- **Aucune API cloud** : Aucune donnée n'est envoyée vers des serveurs externes
- **Embeddings irréversibles** : Les embeddings faciaux ne peuvent pas être reconvertis en images
- **Hors-ligne** : Le système fonctionne entièrement sans connexion internet (air-gapped)
- **Anti-spoofing** : Protection contre les tentatives de fraude par photo/écran

## Auteur

Système développé pour l'Université Catholique du Congo (UCC).

## Licence

Usage académique et interne à l'université.
