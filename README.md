# Système de Reconnaissance Faciale pour la Présence

**Développé par :** Mvemba Dieu Merci | https://dieumercimvemba.web.app  
*(Cas d'usage et exemple concret : Université Catholique du Congo - UCC)*

Système de reconnaissance faciale 100% local conçu pour automatiser l'émargement et remplacer les feuilles de présence traditionnelles, en prenant pour exemple d'application concrète l'Université Catholique du Congo (UCC). Ce système s'appuie sur des modèles de Deep Learning (CNN) de pointe pour détecter, aligner et reconnaître les visages des étudiants, intègre une détection de vivacité anti-usurpation (Anti-Spoofing) et propose une suite complète articulée autour d'une **application moderne Kivy**, d'une base vectorielle **FAISS** et d'un système de gestion relationnel **MySQL**.

## Fonctionnalités

- **Inscription d'étudiants (Multi-photos)** : Enregistrement robuste avec calcul d'embedding moyen à partir de 5 à 10 clichés par étudiant.
- **Vérification de présence par photo de groupe** : Identification automatique et simultanée des étudiants présents sur une photo de classe.
- **Vérification de présence en temps réel** : Détection faciale continue via flux vidéo caméra avec marquage automatique et gestion de cooldown (3s).
- **Anti-Spoofing (Liveness Detection)** : Filtrage de vivacité par modèle CNN Silent-Face v2 ONNX bloquant les attaques par présentation (photos imprimées, écrans de smartphone ou tablettes).
- **Interface Graphique Moderne (Kivy)** : Application desktop complète multi-écrans sous Kivy (Tableau de bord dynamique avec graphiques décisionnels, gestion des étudiants, enrôlement assisté, pointage caméra en direct, structure académique des facultés & promotions, rapports d'assiduité, et réglages système).
- **Interface Graphique d'Enrôlement Rapide (Tkinter)** : Outil historique/léger conservé pour des sessions d'enrôlement directes et rapides.
- **Persistance Hybride (FAISS + MySQL)** : Recherche biométrique vectorielle ultra-rapide en similarité cosinus via FAISS (`IndexFlatIP`) combinée à la gestion relationnelle complète sous MySQL (étudiants, présences, retards, facultés, promotions).
- **Règles Métier Intégrées (Cas UCC)** : Détection automatique des retards (seuil horaire paramétrable, ex: 08h00), calcul automatique des absences et règle anti-doublon journalier.
- **100% Local & Hors-Ligne (Air-Gapped)** : Aucune API tierce, aucune donnée biométrique transmise dans le cloud, respect strict de la confidentialité.
- **Haute Précision** : Pipeline intégrant MTCNN, alignement géométrique par points clés (yeux) et ArcFace (`buffalo_l`).

## Architecture du Système

Le système est organisé selon une architecture modulaire et orientée services :

### Structure des Dossiers

```
cnn_sys/
├── .env                              # Variables d'environnement globales
├── requirements.txt                  # Dépendances Python du projet
├── README.md                         # Documentation générale du projet
├── Dataset/                          # Clichés d'entraînement et d'enrôlement
├── docs/                             # Spécifications et documentation métier UCC
├── reports/                          # Feuilles d'émargement et rapports de présence CSV
├── temp_charts/                      # Graphiques décisionnels générés (Matplotlib)
└── camera_system/                    # Cœur du système de vision et de pointage
    ├── config/                       # Configuration applicative (settings.json)
    ├── data/                         # Persistance vectorielle FAISS
    │   ├── facerec_faiss.index       # Index FAISS (similarité cosinus IndexFlatIP)
    │   └── students_metadata.pkl     # Métadonnées locales sérialisées
    ├── models/                       # Modèles de Deep Learning ONNX
    │   └── silent_face_v2.onnx       # Modèle Anti-Spoofing (Silent-Face v2)
    ├── config.py                     # Module centralisé de configuration (.env)
    ├── pipeline.py                   # Pipeline de traitement facial (MTCNN + ArcFace)
    ├── vector_db.py                  # Gestionnaire de base vectorielle locale FAISS
    ├── anti_spoof.py                 # Détecteur de vivacité (Liveness Detection)
    ├── realtime_detector.py          # Boucle de détection et reconnaissance temps réel
    ├── enroll.py                     # CLI d'enrôlement et de pointage par photo
    ├── camera_attendance.py          # Point d'entrée pour session de pointage caméra
    ├── capture_photo.py              # Utilitaire de capture webcam vers Dataset
    ├── enrollment_gui.py             # Interface graphique historique d'enrôlement (Tkinter)
    └── kivy_app/                     # Application Desktop Moderne (Kivy)
        ├── main.py                   # Point d'entrée de l'application Kivy
        ├── init_mysql.py             # Initialisation et création du schéma MySQL
        ├── batch_enroll.py           # Enrôlement automatique en lot depuis Dataset/
        ├── clear_database.py         # Réinitialisation sécurisée des données
        ├── screens/                  # Vues de l'application Kivy
        │   ├── dashboard_screen.py   # Tableau de bord et métriques de présence
        │   ├── students_screen.py    # Annuaire et gestion des étudiants
        │   ├── enrollment_screen.py  # Écran d'enrôlement avec aperçu photo
        │   ├── attendance_screen.py  # Écran de pointage caméra en temps réel
        │   ├── organization_screen.py# Arborescence des Facultés & Promotions UCC
        │   ├── reports_screen.py     # Consultation et export des rapports
        │   └── settings_screen.py    # Configuration des seuils et paramètres
        ├── services/                 # Couche de services métier
        │   ├── mysql_service.py      # Connecteur CRUD et schéma relationnel MySQL
        │   ├── database_service.py   # Couche d'abstraction des données
        │   ├── face_recognition_service.py # Service de reconnaissance pour l'UI
        │   ├── attendance_service.py # Logique de présence et calculs d'assiduité
        │   ├── chart_service.py      # Génération de graphiques Matplotlib
        │   ├── report_analytics_service.py # Statistiques sur les rapports
        │   └── report_watcher_service.py   # Surveillance automatique des rapports
        └── widgets/                  # Composants UI Kivy réutilisables
            ├── header.py             # En-tête personnalisé UCC
            ├── sidebar.py            # Menu latéral de navigation
            ├── ucc_button.py         # Boutons stylisés selon la charte UCC
            └── chart_image.py        # Conteneur d'affichage des graphiques
```

### Modules Principaux

1. **vector_db.py** : Base de données vectorielle locale utilisant FAISS
   - Stockage et indexation des embeddings faciaux 512-D normalisés ($L_2$).
   - Recherche $O(1)$ par produit scalaire (similarité cosinus via `IndexFlatIP`).
   - Fusion vectorielle multi-photos (calcul du centroïde d'embedding) et persistance pickle des métadonnées.

2. **pipeline.py** : Pipeline de traitement facial
   - Détection MTCNN multi-visages robuste aux variations de pose.
   - Alignement géométrique par rapport aux axes oculaires et redimensionnement strict en $112 \times 112$ pixels.
   - Extraction directe des caractéristiques via InsightFace ArcFace (`buffalo_l`).

3. **anti_spoof.py** : Barrière de vivacité anti-fraude
   - Exploitation du modèle ONNX Silent-Face v2 avec exécution optimisée CPU (OpenCV DNN).
   - Recadrage contextuel ($2.7\times$ la boîte englobante) pour capturer les reflets et textures.
   - Court-circuit immédiat du pipeline si le visage est identifié comme un faux (photo ou écran).

4. **realtime_detector.py** : Détection et reconnaissance temps réel
   - Capture continue et traitement dynamique des trames vidéo OpenCV.
   - Cadre vert pour visage réel reconnu, rouge pour tentative d'usurpation (`SPOOF`), jaune pour étudiant déjà pointé.
   - Gestion de l'anti-doublon et du cooldown temporel (3 secondes).

5. **kivy_app/main.py** : Application Kivy d'entreprise
   - Expérience utilisateur riche, fluide et responsive dédiée à la gestion et au suivi des présences.
   - Intégration complète avec MySQL et synchronisation avec l'index FAISS.

6. **enroll.py** : Interface CLI d'administration
   - Enrôlement unitaire ou multiple d'étudiants par lots.
   - Vérification de présence instantanée sur clichés de groupe (photo de classe).

## Prérequis

- **Python** : 3.11+ ou 3.13 (Environnement Anaconda / Conda recommandé)
- **Base de données** : Serveur MySQL 8.0+ (local ou réseau)
- **Caméra** : Webcam intégrée ou caméra USB compatible OpenCV
- **Bibliothèques Python requises** :
  - `kivy`
  - `opencv-python`
  - `mtcnn`
  - `mediapipe`
  - `insightface`
  - `onnxruntime`
  - `faiss-cpu`
  - `mysql-connector-python`
  - `matplotlib`
  - `python-dotenv`
  - `numpy`

## Installation

### 1. Cloner et installer les dépendances

Installez les dépendances depuis le fichier `requirements.txt` :

```bash
pip install -r requirements.txt
```

Ou installez manuellement les paquets essentiels :

```bash
pip install kivy opencv-python mtcnn mediapipe insightface onnxruntime faiss-cpu mysql-connector-python matplotlib python-dotenv numpy
```

### 2. Configuration de l'environnement

Vérifiez et adaptez le fichier `.env` à la racine :

```env
PROJECT_ROOT="d:\cnn_sys"
CAMERA_SYSTEM_PATH="d:\cnn_sys\camera_system"
KIVY_APP_PATH="d:\cnn_sys\camera_system\kivy_app"
DATA_PATH="d:\cnn_sys\camera_system\data"
MYSQL_HOST="localhost"
MYSQL_PORT="3306"
MYSQL_DATABASE="ucc_face_recognition"
MYSQL_USER="root"
MYSQL_PASSWORD="votre_mot_de_passe"
```

### 3. Initialisation de la Base de Données MySQL

Créez automatiquement la base de données, les tables (`users`, `faculties`, `promotions`, `students`, `attendance`, `reports`, `settings`) et chargez les facultés UCC :

```bash
cd camera_system/kivy_app
python init_mysql.py
```

## Utilisation

### Phase d'Enrôlement (Une seule fois par étudiant)

L'enrôlement extrait l'empreinte faciale de l'étudiant et l'enregistre simultanément dans FAISS et MySQL.

#### Option 1 : Application Graphique Kivy (Recommandée)

Lancez l'application principale Kivy et rendez-vous sur l'écran **Enrôlement** :

```bash
cd camera_system/kivy_app
python main.py
```

- Renseignez le matricule, le nom, le prénom, la faculté et la promotion.
- Sélectionnez une ou plusieurs photos (5 à 10 recommandées avec variations d'angles).
- Validez : le calcul de l'embedding moyen et la persistance dans FAISS et MySQL s'effectuent automatiquement.

#### Option 2 : Enrôlement en Lot (Batch Enrollment)

Pour enrôler automatiquement tous les étudiants à partir du dossier `Dataset/` :

```bash
cd camera_system/kivy_app
python batch_enroll.py
```

#### Option 3 : Interface CLI

```bash
cd camera_system
python enroll.py enroll --matricule "UCC2026001" --nom "Kabila" --prenom "Jean" --photos photo1.jpg photo2.jpg photo3.jpg
```

**Arguments :**
- `--matricule` : Matricule unique de l'étudiant (ex: UCC2026001)
- `--nom` : Nom de famille
- `--prenom` : Prénom
- `--photos` : Une ou plusieurs photos d'identité (Face, Légère rotation gauche/droite, expression neutre/souriante)

#### Option 4 : Interface Graphique Historique (Tkinter)

Pour les postes nécessitant un outil d'enrôlement ultra-léger sans Kivy :

```bash
cd camera_system
python enrollment_gui.py
```

---

### Phase de Pointage (À chaque début de cours)

#### Option 1 : Pointage Caméra via l'Application Kivy

Ouvrez l'application Kivy (`python kivy_app/main.py`) et sélectionnez l'onglet **Pointage Caméra** :
- Affichage du flux vidéo en direct avec surimpression dynamique des résultats.
- Les présences validées sont instantanément enregistrées en base MySQL et reflétées sur le **Tableau de Bord**.

#### Option 2 : Pointage Caméra via Script Autonome

```bash
cd camera_system
python camera_attendance.py --duration 60 --threshold 0.5
```

**Paramètres configurables :**
- `--camera` : Index de la webcam (défaut : `0`)
- `--duration` : Durée de la session en minutes (défaut : `60`)
- `--threshold` : Seuil de reconnaissance cosinus (défaut : `0.5`)
- `--output` : Chemin du rapport CSV personnalisé

**Contrôles clavier durant la session :**
- `q` : Quitter la session et finaliser le rapport
- `s` : Sauvegarder un rapport intermédiaire instantané

#### Option 3 : Pointage par Photo de Groupe

Idéal pour pointer toute une classe à partir d'un seul cliché pris au smartphone ou à l'appareil photo :

```bash
cd camera_system
python enroll.py attendance --photo "chemin/vers/photo_classe.jpg" --threshold 0.5
```

---

### Gestion des Étudiants

#### Consultation et Recherche dans l'Application Kivy
L'écran **Gestion des étudiants** permet de filtrer par faculté, promotion, rechercher par nom/matricule et visualiser les statuts de pointage du jour.

#### Mise à jour via CLI

```bash
python enroll.py update --matricule "UCC2026001" --new-nom "Kabila" --new-prenom "Jean-Paul"
```

#### Ajout ou Remplacement de Photos d'un Étudiant

```bash
# Ajout de photos complémentaires (recalcul de l'embedding moyen cumulé) :
python enroll.py add-photos --matricule "UCC2026001" --photos photo_angle1.jpg photo_angle2.jpg

# Remplacement total des photos :
python enroll.py add-photos --matricule "UCC2026001" --photos photo_recente.jpg --replace
```

## Pipeline de Traitement Facial

### Phase d'Enrôlement (Une seule fois par étudiant)

```
Photos Multiples (5-10) ➔ MTCNN ➔ Alignement (Yeux) ➔ ArcFace ➔ Embedding Moyen (512-D) ➔ Normalisation L2 ➔ FAISS + MySQL
```

1. **Détection MTCNN** : Détection du visage et extraction des coordonnées des 5 points clés faciaux.
2. **Alignement Géométrique** : Calcul de l'angle d'inclinaison des yeux, correction affine et redimensionnement $112 \times 112$.
3. **Extraction ArcFace** : Génération d'un descripteur vectoriel de 512 dimensions par photo.
4. **Fusion Barycentrique & Normalisation** : Calcul du vecteur moyen puis normalisation $\|v\|_2 = 1$.
5. **Double Indexation** : Insertion dans `facerec_faiss.index` (IndexFlatIP) et écriture de la fiche étudiant dans MySQL.

### Phase de Pointage par Photo

```
Photo de Classe ➔ MTCNN Multi-visages ➔ Alignement ➔ ArcFace ➔ Recherche FAISS Cosinus ➔ Marquage Présent
```

1. **MTCNN Multi-visages** : Localisation de tous les visages présents dans la scène.
2. **Alignement & Normalisation** : Recadrage et redressement individuel de chaque visage détecté.
3. **ArcFace** : Projection dans l'espace latent 512-D.
4. **Recherche FAISS** : Produit scalaire direct retournant le meilleur candidat et son score de similarité cosinus.
5. **Validation** : Marquage présent si similarité $\ge$ seuil (défaut : 0.50).

### Phase de Pointage en Temps Réel (avec Anti-Spoofing)

```
Flux Caméra ➔ MTCNN ➔ BARRIÈRE ANTI-SPOOFING ➔ ALIGNEMENT ➔ ArcFace ➔ FAISS ➔ VALIDATION & RÈGLES UCC
```

1. **Flux Caméra** : Réception des frames OpenCV (1280x720).
2. **MTCNN** : Détection des visages dans le champ visuel.
3. **Anti-Spoofing (Silent-Face v2 ONNX)** : Analyse immédiate de vivacité. Si score $< 0.85$, le visage est immédiatement rejeté comme fraude (cadre rouge `SPOOF / PHOTO`) sans solliciter le réseau de reconnaissance.
4. **Alignement** : Traitement géométrique des visages authentiques uniquement.
5. **ArcFace** : Extraction de l'embedding facial.
6. **Recherche FAISS** : Comparaison vectorielle immédiate.
7. **Marquage & Règles Métier** : Application du cooldown (3s), vérification anti-doublon journalier, détermination ponctualité/retard, et persistance MySQL/CSV.

## Fichiers Générés

### Base de Données Vectorielle (`camera_system/data/`)
- `facerec_faiss.index` : Index vectoriel binaire FAISS contenant les centroïdes d'embeddings.
- `students_metadata.pkl` : Dictionnaire sérialisé associant chaque identifiant FAISS aux données de l'étudiant.

### Base de Données Relationnelle (MySQL `ucc_face_recognition`)
- Tables : `users`, `faculties`, `promotions`, `students`, `attendance`, `reports`, `settings`.

### Rapports et Exports (`reports/` et `camera_system/kivy_app/reports/`)
- `attendance_camera_[DATE].csv` : Rapports de pointage générés lors des sessions caméra.
- `attendance_UCC_[DATE].csv` : Rapports générés à partir de photos de groupe.

### Graphiques Décisionnels (`temp_charts/` et `camera_system/kivy_app/temp_charts/`)
- `attendance_rate.png` : Jauge du taux de présence global.
- `attendance_trend.png` : Courbe d'évolution de la participation sur 7 jours.
- `faculty_attendance_bar.png` : Taux de présence comparé par faculté.
- `promotion_attendance_bar.png` : Taux de présence par niveau (L1 à M2).
- `daily_attendance_pie.png` : Répartition Présents / Retards / Absents.

### Modèles (`camera_system/models/`)
- `silent_face_v2.onnx` : Modèle ONNX de détection de vivacité.

## Rapport de Présence

Les rapports CSV et les enregistrements MySQL contiennent les colonnes et champs suivants :
- `Matricule` : Identifiant académique unique de l'étudiant
- `Nom` : Nom de famille
- `Prénom` : Prénom
- `Statut` : `PRESENT`, `RETARD` (si pointé après l'heure limite fixée) ou `ABSENT`
- `Similarité` : Degré de similarité cosinus (indicateur de confiance biométrique, échelle 0.0 à 1.0)
- `Heure de pointage` : Horodatage précis de la reconnaissance faciale
- `Méthode` : `facial` (ou manuel/qrcode)

## Anti-Spoofing (Détection de Vivacité)

Le système intègre une barrière active contre les tentatives d'usurpation d'identité :
- **Modèle** : Silent-Face-Anti-Spoofing v2 au format ONNX.
- **Seuil de vivacité** : 0.85 (85% de confiance requis pour qualifier un visage de réel).
- **Principe d'analyse** : Le modèle inspecte le champ étendu ($2.7\times$ la taille du visage) pour détecter les discontinuités de texture, les réflexions d'écran et la pixellisation des supports papier/écrans.
- **Réaction instantanée** : Tout visage jugé non authentique déclenche une alerte visuelle (`SPOOF / PHOTO`) et est exclu de la chaîne de recherche FAISS.

## Gestion des Erreurs

Le système implémente une tolérance aux pannes robuste :
- **Tolérance MySQL hors-ligne** : Si le serveur MySQL n'est pas joignable, l'application bascule automatiquement en mode autonome sur FAISS + CSV.
- **Absence de visage** : Notification informative sans blocage de l'interface en cas de photo non exploitable.
- **Détection de visages multiples** : Contrôle strict lors de l'enrôlement unitaire (rejet si plus d'un visage est visible sur la photo d'identité).
- **Échec d'alignement** : Utilisation d'un découpage de secours centré si les points de repère ne peuvent être résolus.
- **Absence du modèle Anti-Spoofing** : Basculement sécurisé en mode BYPASS avec journalisation d'un avertissement explicite.
- **Arborescences automatiques** : Création automatique des dossiers manquants (`data/`, `reports/`, `temp_charts/`).

## Performances

- **Indexation FAISS** : Recherche vectorielle instantanée ($< 2$ ms) même avec une base de données de plusieurs milliers d'étudiants.
- **Optimisation CPU** : Tous les modèles (MTCNN, Silent-Face, ArcFace) fonctionnent avec fluidité sur les architectures CPU modernes sans exiger de GPU dédié.
- **Seuil de similarité cosinus (0.50)** : Valeur calibrée assurant un compromis idéal entre taux de fausse acceptation (FAR) et taux de faux rejet (FRR).
- **Interface Kivy Réactive** : Les opérations lourdes (inférence biométrique et requêtes SQL) s'exécutent de manière asynchrone pour préserver une fluidité parfaite de l'interface utilisateur.

## Dépannage

### Problème : "Aucun visage détecté"
- Assurez-vous que l'éclairage est uniforme et suffisant sur le visage.
- Vérifiez la résolution et la netteté de la photo d'origine.

### Problème : "Plusieurs visages détectés" lors de l'enrôlement
- Veillez à ce que la photo d'enrôlement soit un portrait individuel sans personnes en arrière-plan.

### Problème : Similarité faible (< seuil)
- Ajustez si nécessaire le seuil avec `--threshold 0.45` pour des conditions d'éclairage difficiles.
- Complétez l'enrôlement en ajoutant 3 à 5 photos supplémentaires avec différents angles.

### Problème : "Modèle Anti-Spoofing introuvable"
- Vérifiez la présence du fichier `camera_system/models/silent_face_v2.onnx`.

### Problème : Caméra non reconnue ou inaccessible
- Assurez-vous qu'aucun autre logiciel (Teams, Zoom, navigateur) n'occupe le périphérique vidéo.
- Testez un autre index de caméra (ex: `--camera 1`).

### Problème : "Erreur de connexion MySQL"
- Vérifiez que le service MySQL est démarré.
- Contrôlez vos identifiants dans le fichier `.env` ou lancez `init_mysql.py` pour valider les tables.

## Sécurité et Confidentialité

- **100% Local & Hors-Ligne (Air-Gapped)** : Aucune donnée biométrique ou personnelle ne transite par Internet.
- **Embeddings Irréversibles** : Les descripteurs vectoriels 512-D ne permettent pas de reconstituer l'image faciale d'origine.
- **Protection Anti-Fraude** : Barrière anti-spoofing empêchant l'émargement frauduleux par photo interposée.
- **Contrôle Total des Données** : Données conservées sous le contrôle exclusif de l'administrateur dans la base locale.

## Auteur

**Développé par :** Mvemba Dieu Merci | https://dieumercimvemba.web.app  
*(Cas d'usage et exemple d'application : Université Catholique du Congo - UCC)*

