# Système de Reconnaissance Faciale pour la Présence - UCC

Système de reconnaissance faciale 100% local pour remplacer les feuilles de présence traditionnelles à l'université. Ce système utilise des modèles de deep learning modernes pour détecter, aligner et reconnaître les visages des étudiants.

## Fonctionnalités

- **Inscription d'étudiants** : Enregistrement des étudiants avec leurs photos d'identité
- **Vérification de présence** : Identification automatique des étudiants présents sur des photos de groupe
- **100% local** : Aucune API cloud, tout fonctionne hors-ligne
- **Haute précision** : Utilisation de modèles state-of-the-art (MTCNN, MediaPipe, InsightFace)

## Architecture du Système

Le système est composé de trois modules principaux :

1. **vector_db.py** : Base de données vectorielle locale utilisant FAISS
2. **pipeline.py** : Pipeline de traitement facial en 3 étapes
3. **main.py** : Interface en ligne de commande pour l'inscription et la présence

## Prérequis

- Python 3.11+ ou 3.13
- Bibliothèques installées :
  - opencv-python
  - mtcnn
  - mediapipe
  - insightface
  - onnxruntime
  - faiss-cpu

## Installation

Les bibliothèques nécessaires sont déjà installées dans votre environnement. Si vous devez les réinstaller :

```bash
pip install opencv-python mtcnn mediapipe insightface onnxruntime faiss-cpu
```

## Structure du Projet

```
cnn_sys/
├── vector_db.py           # Module de base de données vectorielle
├── pipeline.py            # Pipeline de traitement facial
├── main.py                # Application CLI principale
├── README.md              # Documentation
├── facerec_faiss.index   # Index FAISS (créé automatiquement)
└── students_metadata.pkl  # Métadonnées des étudiants (créé automatiquement)
```

## Utilisation

### 1. Inscription d'un Étudiant

Pour inscrire un nouvel étudiant dans le système :

```bash
python main.py enroll --matricule "UCC2024001" --nom "Doe" --prenom "John" --photo "chemin/vers/photo.jpg"
```

**Arguments requis :**
- `--matricule` : Matricule unique de l'étudiant
- `--nom` : Nom de l'étudiant
- `--prenom` : Prénom de l'étudiant
- `--photo` : Chemin vers la photo d'identité (format JPG/PNG)

**Note :** La photo doit contenir exactement un visage clair et bien éclairé.

### 2. Vérification de Présence

Pour vérifier la présence des étudiants à partir d'une photo de groupe :

```bash
python main.py attendance --photo "chemin/vers/photo_groupe.jpg"
```

**Arguments requis :**
- `--photo` : Chemin vers la photo de groupe de la classe

**Arguments optionnels :**
- `--threshold` : Seuil de distance pour la correspondance (défaut: 0.6). Une valeur plus basse augmente la précision mais peut réduire le taux de détection.

**Exemple avec seuil personnalisé :**
```bash
python main.py attendance --photo "classe_photo.jpg" --threshold 0.5
```

## Pipeline de Traitement Facial

Le système utilise un pipeline en 3 étapes :

1. **Détection (MTCNN)** : Localisation des visages dans l'image
2. **Alignement (MediaPipe Face Mesh)** : 
   - Extraction des points clés des yeux (index 33 et 263)
   - Calcul de l'angle de rotation
   - Transformation affine pour aligner horizontalement le visage
   - Redimensionnement à 112x112 pixels
3. **Embedding (InsightFace ArcFace)** : Extraction du vecteur de 512 dimensions caractéristique du visage

## Fichiers Générés

- `facerec_faiss.index` : Index FAISS contenant les embeddings faciaux
- `students_metadata.pkl` : Dictionnaire Python contenant les informations des étudiants
- `attendance_UCC_[DATE].csv` : Rapport de présence généré lors de chaque vérification

## Rapport de Présence

Le fichier CSV généré contient les colonnes suivantes :
- `Matricule` : Identifiant unique de l'étudiant
- `Nom` : Nom de l'étudiant
- `Prénom` : Prénom de l'étudiant
- `Statut` : "PRESENT" si l'étudiant est identifié
- `Distance` : Distance L2 entre les embeddings (indicateur de confiance)

## Gestion des Erreurs

Le système inclut une gestion robuste des erreurs :
- Détection de 0 ou plusieurs visages lors de l'inscription (erreur)
- Coordonnées de boîte englobante négatives (correction automatique)
- Échec de l'alignement (continuation avec les autres visages)
- Base de données vide (message d'erreur clair)

## Performances

- **Base de données** : FAISS permet une recherche rapide même avec des milliers d'étudiants
- **Modèles** : Les modèles utilisés sont optimisés pour CPU
- **Seuil par défaut** : 0.6 offre un bon équilibre entre précision et rappel

## Dépannage

### Problème : "Aucun visage détecté"
- Vérifiez que la photo est de bonne qualité
- Assurez-vous que le visage est bien visible et éclairé
- Essayez avec une photo différente

### Problème : "Plusieurs visages détectés" lors de l'inscription
- Utilisez une photo d'identité avec un seul visage
- Recadrez la photo pour ne montrer que l'étudiant

### Problème : Distance élevée (> seuil)
- Le visage peut être sous un angle différent
- L'éclairage peut être différent
- Ajustez le seuil avec l'option `--threshold`

## Sécurité et Confidentialité

- Tous les données sont stockées localement
- Aucune donnée n'est envoyée vers des serveurs externes
- Les embeddings faciaux ne peuvent pas être reconvertis en images
- Le système fonctionne entièrement hors-ligne (air-gapped)

## Auteur

Système développé pour l'Université Catholique du Congo (UCC).

## Licence

Usage académique et interne à l'université.
