# Guide d'Utilisation - Système de Reconnaissance Faciale UCC

## 🎓 Système Complet de Reconnaissance Faciale

Ce guide explique comment utiliser le système de reconnaissance faciale de l'Université Catholique du Congo (UCC) pour gérer la présence des étudiants.

---

## 📋 Vue d'ensemble des Pipelines

### Phase 1 : Enrôlement (Une seule fois par étudiant)
```
Photo d'identité ➔ MTCNN ➔ Alignement ➔ ArcFace ➔ Stockage FAISS (.index + .pkl)
```

### Phase 2 : Pointage (À chaque début de cours)
```
CAMERA ➔ MTCNN (Multi-visages) ➔ Alignement ➔ ArcFace ➔ Recherche FAISS ➔ Présent
```

---

## 🚀 Guide d'Installation Rapide

### Prérequis
- Python 3.11+ ou 3.13
- Bibliothèques installées : opencv-python, mtcnn, mediapipe, insightface, onnxruntime, faiss-cpu

### Vérification de l'environnement
```bash
# Vérifier la version de Python
python --version

# Vérifier les bibliothèques installées
pip list | findstr "opencv mtcnn mediapipe insightface faiss"
```

### Structure des dossiers
```
D:\cnn_sys\
├── camera_system\          # Dossier principal du système
│   ├── enroll.py          # Script d'enrôlement
│   ├── camera_attendance.py  # Script de pointage avec caméra
│   ├── realtime_detector.py  # Module de détection temps réel
│   ├── vector_db.py       # Base de données FAISS
│   ├── pipeline.py        # Pipeline de traitement
│   └── README.md          # Documentation technique
└── Dataset\               # Dossier avec les photos des étudiants
```

---

## 👨‍🎓 PHASE 1 : Enrôlement des Étudiants

### Étape 1 : Préparer les photos d'identité
- **Format** : JPG ou PNG
- **Qualité** : Haute résolution, visage clair et bien éclairé
- **Composition** : Un seul visage par photo, face centrée
- **Nom du fichier** : Utiliser le matricule ou le nom de l'étudiant

### Étape 2 : Lancer l'enrôlement

#### Navigation vers le dossier
```bash
cd D:\cnn_sys\camera_system
```

#### Méthode 1 : Interface Graphique (Recommandée)
```bash
# Lancer l'interface graphique
python enrollment_gui.py

# Ou utiliser le raccourci
lancer_gui.bat
```

L'interface graphique offre :
- 🖥️ Interface intuitive avec formulaire
- 📁 Sélecteur de fichier intégré
- 📋 Journal d'activité en temps réel
- 📊 Visualisation de la base de données
- ✅ Validation automatique des champs

#### Méthode 2 : Ligne de commande
```bash
python enroll.py enroll --matricule "UCC2024001" --nom "Doe" --prenom "John" --photo "../Dataset/john_doe.jpg"
```

#### Paramètres expliqués
- `--matricule` : Identifiant unique de l'étudiant (ex: UCC2024001)
- `--nom` : Nom de famille de l'étudiant
- `--prenom` : Prénom de l'étudiant
- `--photo` : Chemin vers la photo d'identité

### Étape 3 : Vérifier le succès de l'enrôlement
Le système affichera :
```
============================================================
PHASE D'ENrôLEMENT D'ÉTUDIANT - UCC
============================================================
Pipeline: Photo d'identité ➔ MTCNN ➔ Alignement ➔ ArcFace ➔ Stockage FAISS
============================================================
Base de données chargée. Étudiants actuels: 0
ÉTAPE 1: Photo d'identité chargée: ../Dataset/john_doe.jpg
ÉTAPE 2: MTCNN - Détection du visage...
1 visage(s) détecté(s) avec MTCNN.
ÉTAPE 3: Alignement - Visage aligné avec succès
ÉTAPE 4: ArcFace - Embedding facial 512-D extrait
ÉTAPE 5: Stockage FAISS (.index + .pkl)
============================================================
INSCRIPTION RÉUSSIE!
ID: 0
Matricule: UCC2024001
Nom: Doe
Prénom: John
Total étudiants: 1
============================================================
```

### Exemples d'enrôlement multiples
```bash
# Étudiant 1
python enroll.py enroll --matricule "UCC2024001" --nom "Doe" --prenom "John" --photo "../Dataset/john_doe.jpg"

# Étudiant 2
python enroll.py enroll --matricule "UCC2024002" --nom "Smith" --prenom "Jane" --photo "../Dataset/jane_smith.jpg"

# Étudiant 3
python enroll.py enroll --matricule "UCC2024003" --nom "Dupont" --prenom "Pierre" --photo "../Dataset/pierre_dupont.jpg"
```

---

## 📸 PHASE 2 : Pointage des Étudiants

### Méthode 1 : Pointage avec Caméra en Temps Réel

#### Étape 1 : Lancer le système de caméra
```bash
cd D:\cnn_sys\camera_system
python camera_attendance.py
```

#### Étape 2 : Configuration par défaut
- **Caméra** : Caméra 0 (webcam par défaut)
- **Durée** : 60 minutes
- **Seuil** : 0.6
- **Résolution** : 1280x720

#### Étape 3 : Options avancées
```bash
# Durée de 30 minutes
python camera_attendance.py --duration 30

# Utiliser la caméra 1
python camera_attendance.py --camera 1

# Seuil de reconnaissance plus strict
python camera_attendance.py --threshold 0.5

# Haute définition
python camera_attendance.py --width 1920 --height 1080

# Fichier de sortie personnalisé
python camera_attendance.py --output presence_cours_maths.csv
```

#### Étape 4 : Contrôles pendant la session
- **'q'** : Quitter la session
- **'s'** : Sauvegarder le rapport intermédiaire

#### Étape 5 : Affichage en temps réel
```
┌─────────────────────────────────────────────────────────┐
│ Pointage Facial en Temps Réel - UCC                    │
│                                                         │
│ ┌─────────────────────────────────────────────────┐   │
│ │ [Visage détecté]                              │   │
│ │ ┌─────────┐                                   │   │
│ │ │ ████████│  John Doe (UCC2024001) - 0.25     │   │
│ │ │ ████████│                                   │   │
│ │ └─────────┘                                   │   │
│ └─────────────────────────────────────────────────┘   │
│                                                         │
│ Pointage en cours - Temps restant: 45:30 | Étudiants présents: 12
└─────────────────────────────────────────────────────────┘
```

### Méthode 2 : Pointage avec Photo de Groupe

#### Étape 1 : Préparer la photo de groupe
- Prendre une photo de la classe/auditoire
- Assurer un bon éclairage
- Visages bien visibles

#### Étape 2 : Lancer le pointage avec photo
```bash
cd D:\cnn_sys\camera_system
python enroll.py attendance --photo "../Dataset/classe_photo.jpg"
```

#### Étape 3 : Options avancées
```bash
# Seuil de reconnaissance personnalisé
python enroll.py attendance --photo "../Dataset/classe_photo.jpg" --threshold 0.5
```

#### Étape 4 : Résultat du pointage
```
============================================================
PHASE DE VÉRIFICATION DE PRÉSENCE - UCC
============================================================
Pipeline: MTCNN (Multi-visages) ➔ Alignement ➔ ArcFace ➔ Recherche FAISS ➔ Présent
============================================================
Base de données chargée. Étudiants inscrits: 25
ÉTAPE 1: MTCNN (Multi-visages) - Détection des visages...
15 visage(s) détecté(s) avec MTCNN
============================================================
RAPPORT DE PRÉSENCE
============================================================
Visages détectés: 15
Étudiants identifiés: 12
Fichier CSV généré: attendance_UCC_20260611_143022.csv
============================================================
Étudiants présents:
  - Doe John (Matricule: UCC2024001, Distance: 0.1234)
  - Smith Jane (Matricule: UCC2024002, Distance: 0.2345)
  - Dupont Pierre (Matricule: UCC2024003, Distance: 0.1456)
  ...
```

---

## 📊 Gestion des Rapports de Présence

### Format des fichiers CSV
Les rapports sont générés automatiquement avec le format suivant :

```csv
Matricule,Nom,Prénom,Statut,Distance,Heure de pointage
UCC2024001,Doe,John,PRESENT,0.1234,08:15:32
UCC2024002,Smith,Jane,PRESENT,0.2345,08:16:01
UCC2024003,Dupont,Pierre,PRESENT,0.1456,08:16:45
```

### Emplacement des fichiers
- **Enrôlement** : `facerec_faiss.index` et `students_metadata.pkl` dans `camera_system/`
- **Pointage** : `attendance_UCC_YYYYMMDD_HHMMSS.csv` dans `camera_system/`
- **Caméra** : `attendance_camera_YYYYMMDD_HHMMSS.csv` dans `camera_system/`

---

## 🔧 Dépannage

### Problèmes courants d'enrôlement

#### "Aucun visage détecté dans l'image"
- **Cause** : Photo de mauvaise qualité ou visage non visible
- **Solution** : Utiliser une photo de meilleure qualité avec un visage clair

#### "Plusieurs visages détectés"
- **Cause** : Photo contient plusieurs personnes
- **Solution** : Recadrer la photo pour ne montrer que l'étudiant

#### "L'ID existe déjà dans la base de données"
- **Cause** : Étudiant déjà inscrit
- **Solution** : Vérifier le matricule ou utiliser un ID différent

### Problèmes courants de pointage

#### "Impossible d'ouvrir la caméra"
- **Cause** : Caméra non connectée ou utilisée par une autre application
- **Solution** : 
  - Vérifier que la caméra est connectée
  - Fermer les autres applications utilisant la caméra
  - Essayer `--camera 1` ou `--camera 2`

#### "Faible taux de reconnaissance"
- **Cause** : Seuil trop strict ou mauvaises conditions d'éclairage
- **Solution** :
  - Ajuster le seuil (`--threshold 0.7`)
  - Améliorer l'éclairage
  - Demander aux étudiants de se rapprocher de la caméra

#### "Aucun étudiant inscrit dans la base de données"
- **Cause** : Aucun enrôlement effectué
- **Solution** : D'abord inscrire des étudiants avec la Phase d'Enrôlement

---

## 💡 Bonnes Pratiques

### Phase d'Enrôlement
1. **Photos de qualité** : Utiliser des photos d'identité professionnelles
2. **Un seul visage** : Une seule personne par photo
3. **Bon éclairage** : Visage bien éclairé et visible
4. **Matricules uniques** : Chaque étudiant doit avoir un matricule unique

### Phase de Pointage
1. **Position de caméra** : Placer la caméra à une hauteur optimale
2. **Éclairage** : Assurer un bon éclairage de la salle
3. **Distance** : Étudiants à une distance raisonnable de la caméra
4. **Test préalable** : Tester le système avant le début du cours

---

## 📞 Support Technique

Pour toute question ou problème technique :
1. Consulter le README.md pour la documentation technique
2. Vérifier les logs pour les messages d'erreur détaillés
3. Consulter ce guide d'utilisation

---

## 🎓 Workflow Complet Recommandé

### Pour un nouveau semestre :
1. **Préparer** les photos d'identité de tous les étudiants
2. **Enroller** tous les étudiants avec la Phase d'Enrôlement
3. **Tester** le système de pointage avec quelques étudiants
4. **Déployer** le système de pointage au début de chaque cours

### Pour chaque cours :
1. **Lancer** le système de pointage (caméra ou photo)
2. **Surveiller** les reconnaissances en temps réel
3. **Sauvegarder** le rapport de présence à la fin
4. **Archiver** les rapports CSV pour le suivi administratif

---

## 🔒 Sécurité et Confidentialité

- **100% local** : Toutes les données restent sur la machine locale
- **Air-gapped** : Fonctionne sans connexion internet
- **Embeddings sécurisés** : Les embeddings faciaux ne peuvent pas être reconvertis en images
- **Base de données locale** : FAISS + pickle pour stockage sécurisé

---

**Version** : 1.0  
**Date** : 2026-06-11  
**Institution** : Université Catholique du Congo (UCC)  
**Contact** : Support Technique UCC
