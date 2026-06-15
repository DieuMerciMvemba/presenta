# Documentation du Système de Reconnaissance Faciale UCC

## 📋 Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Architecture de l'application](#architecture-de-lapplication)
3. [Écrans de l'application](#écrans-de-lapplication)
4. [Services Backend](#services-backend)
5. [Système de Reconnaissance Faciale](#système-de-reconnaissance-faciale)
6. [Graphiques Professionnels](#graphiques-professionnels)
7. [Base de Données](#base-de-données)
8. [Configuration](#configuration)

---

## 🎯 Vue d'ensemble

Le système de reconnaissance faciale UCC est une application Kivy complète pour le pointage automatique des étudiants utilisant:
- **Reconnaissance faciale en temps réel** avec InsightFace
- **Détection anti-spoofing** pour prévenir les fraudes
- **Base de données MySQL** pour stocker les données
- **Graphiques professionnels** avec matplotlib pour l'analyse
- **Interface utilisateur moderne** avec Kivy

---

## 🏗️ Architecture de l'application

### Structure des fichiers

```
d:\cnn_sys\camera_system\
├── kivy_app/
│   ├── main.py                 # Point d'entrée principal
│   ├── screens/                # Écrans de l'application
│   │   ├── dashboard_screen.py      # Tableau de bord
│   │   ├── students_screen.py       # Gestion des étudiants
│   │   ├── enrollment_screen.py     # Enrôlement des étudiants
│   │   ├── attendance_screen.py     # Pointage caméra
│   │   ├── organization_screen.py    # Organisation
│   │   ├── reports_screen.py         # Rapports
│   │   └── settings_screen.py        # Paramètres
│   ├── services/               # Services backend
│   │   ├── database_service.py      # Service de base de données
│   │   ├── mysql_service.py         # Service MySQL direct
│   │   └── chart_service.py         # Service de graphiques
│   ├── widgets/                # Widgets personnalisés
│   │   ├── sidebar.py               # Barre latérale
│   │   ├── header.py                # En-tête
│   │   └── ucc_button.py            # Boutons personnalisés
│   └── temp_charts/            # Répertoire pour les graphiques générés
├── config/
│   └── settings.json          # Configuration de l'application
└── data/
    ├── facerec_faiss.index    # Index FAISS pour la recherche
    └── students_metadata.pkl  # Métadonnées des étudiants
```

---

## 📱 Écrans de l'application

### 1. Dashboard (Tableau de bord)

**Fichier:** `dashboard_screen.py`

**Fonctionnalités:**
- **Cartes de statistiques:**
  - Total Étudiants
  - Présents Aujourd'hui
  - Absents Aujourd'hui
  - Taux de Présence

- **Graphiques professionnels:**
  - 📊 Tendance de présence sur 7 jours (barres)
  - 📈 Taux de présence quotidien (ligne)
  - ⏰ Distribution horaire des présences (barres)

- **Actions rapides:**
  - 👥 Ajouter Étudiant
  - 📸 Démarrer Pointage
  - 📊 Générer Rapport
  - 🔄 Redémarrer Système

- **Derniers pointages:** Liste des 5 derniers enregistrements

**Comment ça marche:**
1. À l'initialisation, le dashboard se connecte à `DatabaseService`
2. Il récupère les statistiques via `get_statistics()`
3. Il génère automatiquement les graphiques avec `ChartService`
4. Les graphiques sont sauvegardés dans `temp_charts/`
5. Les données sont mises à jour automatiquement à chaque entrée sur l'écran

---

### 2. Students Screen (Gestion des étudiants)

**Fichier:** `students_screen.py`

**Fonctionnalités:**
- **Liste des étudiants:** Affiche tous les étudiants avec leurs informations
- **Ajout d'étudiant:** Formulaire pour ajouter un nouvel étudiant
- **Modification:** Éditer les informations d'un étudiant existant
- **Suppression:** Supprimer un étudiant de la base
- **Recherche:** Filtrer les étudiants par nom ou matricule

**Comment ça marche:**
1. Utilise `DatabaseService` pour les opérations CRUD
2. Charge les étudiants via `get_all_students()`
3. Affiche les données dans une grille scrollable
4. Les modifications sont synchronisées avec MySQL en temps réel

---

### 3. Enrollment Screen (Enrôlement)

**Fichier:** `enrollment_screen.py`

**Fonctionnalités:**
- **Capture de visage:** Utilise la caméra pour capturer des photos
- **Extraction d'embeddings:** Génère des vecteurs faciaux avec InsightFace
- **Enregistrement:** Sauvegarde les embeddings dans FAISS
- **Validation:** Vérifie la qualité des captures

**Comment ça marche:**
1. Active la caméra pour capturer des visages
2. Utilise MTCNN pour détecter et aligner les visages
3. Extrait les embeddings avec ArcFace (512 dimensions)
4. Ajoute les vecteurs à l'index FAISS
5. Sauvegarde les métadonnées dans `students_metadata.pkl`

---

### 4. Attendance Screen (Pointage caméra)

**Fichier:** `attendance_screen.py`

**Fonctionnalités:**
- **Reconnaissance en temps réel:** Détecte et identifie les visages
- **Anti-spoofing:** Détecte les tentatives de fraude (photos, vidéos)
- **Enregistrement automatique:** Sauvegarde les présences dans MySQL
- **Affichage en direct:** Montre le flux vidéo avec les annotations
- **Statistiques:** Affiche le nombre de présents en temps réel

**Comment ça marche:**
1. **Pipeline de reconnaissance:**
   - Capture les frames de la caméra
   - Détecte les visages avec MTCNN
   - Aligne les visages pour améliorer la précision
   - Extrait les embeddings (512 dimensions)
   - Recherche dans FAISS (recherche de similarité)

2. **Anti-spoofing:**
   - Analyse la vivacité du visage
   - Score > 0.5 = visage réel
   - Score < 0.5 = tentative de fraude

3. **Enregistrement:**
   - Si similarité >= seuil (0.5) → Étudiant reconnu
   - Enregistre la présence via `DatabaseService.record_attendance()`
   - Stocke: student_id, statut, méthode, confiance, timestamp

---

### 5. Organization Screen (Organisation)

**Fichier:** `organization_screen.py`

**Fonctionnalités:**
- Gestion des facultés
- Gestion des départements
- Structure organisationnelle

---

### 6. Reports Screen (Rapports)

**Fichier:** `reports_screen.py`

**Fonctionnalités:**
- **Surveillance automatique:** Watchdog surveille le dossier `reports/`
- **Chargement automatique:** Les nouveaux rapports sont chargés automatiquement
- **Statistiques:** Affiche le nombre total de rapports
- **Graphiques:** Zone pour les graphiques de rapport (à implémenter)

**Comment ça marche:**
1. Utilise `watchdog` pour surveiller le dossier `reports/`
2. Détecte les nouveaux fichiers CSV/Excel
3. Charge les données avec `ReportAnalyticsService`
4. Affiche les statistiques et graphiques

---

### 7. Settings Screen (Paramètres)

**Fichier:** `settings_screen.py`

**Fonctionnalités:**
- **Seuil de reconnaissance:** Ajuster le seuil de similarité (0.0-1.0)
- **Anti-spoofing:** Activer/désactiver la détection de fraude
- **Configuration caméra:** Choisir l'index de la caméra
- **Sauvegarde:** Les paramètres sont sauvegardés dans `settings.json`

**Comment ça marche:**
1. Charge les paramètres depuis `config/settings.json`
2. Affiche les valeurs actuelles dans l'interface
3. Permet la modification via sliders et switches
4. Sauvegarde automatiquement lors des modifications

---

## 🔧 Services Backend

### DatabaseService

**Fichier:** `services/database_service.py`

**Rôle:** Couche d'abstraction au-dessus de MySQLService

**Méthodes principales:**
- `get_statistics()` - Récupère les statistiques globales
- `get_all_students()` - Liste tous les étudiants
- `find_student_by_matricule(matricule)` - Trouve un étudiant par matricule
- `find_student_by_id(student_id)` - Trouve un étudiant par ID
- `add_student()` - Ajoute un nouvel étudiant
- `update_student_info()` - Met à jour les informations
- `delete_student()` - Supprime un étudiant
- `record_attendance()` - Enregistre une présence

**Comment ça marche:**
1. Initialise `MySQLService` avec les credentials
2. Fournit une API de haut niveau pour les opérations
3. Gère les erreurs et la validation
4. Retourne des structures de données cohérentes

---

### MySQLService

**Fichier:** `services/mysql_service.py`

**Rôle:** Interaction directe avec la base de données MySQL

**Méthodes principales:**
- `connect()` / `disconnect()` - Gestion de la connexion
- `create_tables()` - Crée les tables si elles n'existent pas
- `insert_student()` - Insère un étudiant
- `get_student_by_matricule()` - Recherche par matricule
- `get_student_by_id()` - Recherche par ID
- `insert_attendance()` - Insère un enregistrement de présence
- `get_statistics()` - Calcule les statistiques
- `get_recent_attendance()` - Récupère les derniers enregistrements

**Structure de la base de données:**
```sql
- students (id, matricule, nom, prenom, email, photo_path, faculty_id, department_id)
- attendance (id, student_id, date_presence, statut, methode, confiance, ...)
- faculties (id, nom, description)
- departments (id, nom, faculty_id)
```

---

### ChartService

**Fichier:** `services/chart_service.py`

**Rôle:** Génération de graphiques professionnels avec matplotlib

**Méthodes principales:**
- `generate_attendance_trend_chart()` - Graphique de tendance sur 7 jours
- `generate_attendance_rate_chart()` - Taux de présence quotidien
- `generate_hourly_distribution_chart()` - Distribution horaire
- `generate_top_students_chart()` - Top étudiants par présence
- `generate_pie_chart()` - Graphique circulaire présence/absence

**Comment ça marche:**
1. Utilise matplotlib avec style seaborn
2. Génère des graphiques professionnels avec annotations
3. Sauvegarde les images dans `temp_charts/`
4. Retourne le chemin de l'image pour affichage dans Kivy

**Style professionnel:**
- Couleurs cohérentes (bleu, vert, rouge, orange)
- Grilles et annotations
- Labels clairs et lisibles
- Format PNG haute résolution (100 DPI)

---

## 🤖 Système de Reconnaissance Faciale

### Pipeline de reconnaissance

1. **Détection de visage (MTCNN)**
   - Détecte les visages dans l'image
   - Retourne les coordonnées et les points clés
   - Peut détecter plusieurs visages simultanément

2. **Alignement du visage**
   - Utilise les points clés MTCNN pour aligner
   - Corrige la rotation du visage
   - Normalise la taille (112x112 pour ArcFace)

3. **Extraction d'embeddings (ArcFace)**
   - Modèle: InsightFace buffalo_l
   - Dimension: 512 vecteurs
   - Normalisation: Norme = 1.0

4. **Recherche FAISS**
   - Index: Index L2 pour recherche rapide
   - Recherche: k-NN (k=1 pour le plus proche)
   - Similarité: Distance euclidienne convertie en score

5. **Décision**
   - Si similarité >= seuil (0.5) → Reconnu
   - Sinon → Non reconnu
   - Enregistrement automatique si reconnu

### Anti-Spoofing

**Modèle:** SilentFace v2 (ONNX)

**Fonctionnement:**
- Analyse la vivacité du visage
- Score de vivacité: 0.0 (faux) à 1.0 (vrai)
- Seuil: 0.5
- Si score < 0.5 → 🚨 TENTATIVE DE FRAUDE DÉTECTÉE

**Types de fraude détectés:**
- Photos de visage
- Vidéos de visage
- Masques 3D
- Écrans

---

## 📊 Graphiques Professionnels

### Types de graphiques

1. **Tendance de présence (Barres)**
   - Présents vs Absents sur 7 jours
   - Annotations sur chaque barre
   - Couleurs: Vert (présents), Rouge (absents)

2. **Taux de présence (Ligne)**
   - Évolution du taux quotidien
   - Zone remplie sous la courbe
   - Annotations en pourcentage

3. **Distribution horaire (Barres)**
   - Présences par heure de la journée
   - Identifie les heures de pointe
   - Utile pour l'optimisation

### Intégration

**Dans le Dashboard:**
- Générés automatiquement à l'initialisation
- Mis à jour lors de l'entrée sur l'écran
- Affichés dans une zone scrollable
- Chemins: `temp_charts/attendance_trend.png`, etc.

**Service ChartService:**
- Backend non-interactif matplotlib ('Agg')
- Répertoire temporaire: `kivy_app/temp_charts/`
- Style seaborn professionnel
- Résolution: 100 DPI

---

## 🗄️ Base de Données

### Configuration MySQL

**Host:** localhost  
**Port:** 3306  
**Database:** ucc_face_recognition  
**User:** root  
**Password:** admin123

### Tables principales

**students:**
- id (INT, AUTO_INCREMENT, PRIMARY KEY)
- matricule (VARCHAR, UNIQUE)
- nom (VARCHAR)
- prenom (VARCHAR)
- email (VARCHAR)
- photo_path (VARCHAR)
- faculty_id (INT)
- department_id (INT)
- created_at (TIMESTAMP)

**attendance:**
- id (INT, AUTO_INCREMENT, PRIMARY KEY)
- student_id (INT, FOREIGN KEY)
- date_presence (DATETIME, DEFAULT NOW())
- statut (ENUM: 'present', 'absent')
- methode (ENUM: 'facial', 'manuel', 'qrcode')
- confiance (FLOAT)
- photo_capture_path (VARCHAR)
- camera_id (VARCHAR)
- notes (TEXT)

**faculties:**
- id (INT, AUTO_INCREMENT, PRIMARY KEY)
- nom (VARCHAR)
- description (TEXT)

**departments:**
- id (INT, AUTO_INCREMENT, PRIMARY KEY)
- nom (VARCHAR)
- faculty_id (INT, FOREIGN KEY)

---

## ⚙️ Configuration

### Fichier settings.json

**Emplacement:** `d:\cnn_sys\camera_system\config\settings.json`

**Paramètres:**
```json
{
  "recognition_threshold": 0.5,
  "anti_spoofing_enabled": true,
  "camera_index": 0,
  "database": {
    "host": "localhost",
    "port": 3306,
    "database": "ucc_face_recognition",
    "user": "root",
    "password": "admin123"
  }
}
```

**Chargement:**
- Les écrans chargent les paramètres au démarrage
- Modifications sauvegardées automatiquement
- Utilisé dans AttendanceScreen et SettingsScreen

---

## 🔄 Bouton de Redémarrage

**Emplacement:** Dashboard → Sidebar → "Actions Rapides"

**Fonctionnalité:**
- Ferme proprement les connexions à la base de données
- Arrête l'application Kivy
- Relance automatiquement l'application
- Utile pour appliquer les modifications de code

**Implémentation:**
```python
def restart_system(self):
    # 1. Fermer les connexions
    self.db_service.disconnect()
    
    # 2. Arrêter l'application
    app = App.get_running_app()
    app.stop()
    
    # 3. Relancer
    subprocess.Popen([python, script])
    sys.exit(0)
```

---

## 📱 Sidebar (Barre latérale)

**Fichier:** `widgets/sidebar.py`

**Fonctionnalités:**
- Navigation entre les écrans
- Statistiques en temps réel (étudiants, présents)
- Mise à jour automatique toutes les secondes
- Boutons de navigation stylisés

**Comment ça marche:**
1. Initialise `MySQLService` pour les statistiques
2. Utilise `Clock.schedule_interval` pour les mises à jour
3. Appelle `get_statistics()` toutes les secondes
4. Met à jour les labels avec les nouvelles valeurs

---

## 🚀 Flux de travail typique

### Enrôlement d'un étudiant

1. Naviguer vers "Enrôlement des étudiants"
2. Entrer les informations (nom, prénom, matricule)
3. Capturer plusieurs photos du visage
4. Le système génère les embeddings
5. Les embeddings sont ajoutés à FAISS
6. Les métadonnées sont sauvegardées

### Pointage automatique

1. Naviguer vers "Pointage caméra"
2. Cliquer sur "Démarrer Pointage"
3. La caméra s'active
4. Le système détecte les visages
5. Si reconnu → Présence enregistrée automatiquement
6. Les données sont sauvegardées dans MySQL

### Analyse des données

1. Naviguer vers "Tableau de bord"
2. Voir les statistiques en temps réel
3. Consulter les graphiques professionnels
4. Analyser les tendances de présence
5. Identifier les heures de pointe

---

## 🎨 Design et UX

### Palette de couleurs

- **UCC_BLUE_DARK:** #1E3A8A
- **ACCENT_BLUE:** #3B82F6
- **ACCENT_GREEN:** #10B981
- **ACCENT_RED:** #EF4444
- **ACCENT_CYAN:** #0990C8
- **ACCENT_PURPLE:** #6B46A8

### Typographie

- **Police:** Arial
- **Titres:** 20-22px, Bold
- **Sous-titres:** 16px, Bold
- **Texte:** 12-14px

### Composants UI

- **UCCButton:** Bouton personnalisé avec coins arrondis
- **Sidebar:** Barre latérale avec navigation
- **Header:** En-tête avec titre et date
- **Cards:** Cartes de statistiques avec ombres

---

## 🔒 Sécurité

### Anti-spoofing

- **Modèle:** SilentFace v2
- **Détection:** Photos, vidéos, masques
- **Seuil:** 0.5
- **Action:** Bloque l'enregistrement si fraude détectée

### Base de données

- **Connexion sécurisée:** MySQL avec credentials
- **Validation:** Données validées avant insertion
- **Transactions:** Opérations atomiques

---

## 📈 Performance

### Optimisation FAISS

- **Index:** Index L2 pour recherche rapide
- **Dimension:** 512 vecteurs
- **Recherche:** k-NN avec k=1
- **Performance:** < 10ms par recherche

### Pipeline de reconnaissance

- **Détection MTCNN:** ~50ms
- **Alignement:** ~10ms
- **Extraction ArcFace:** ~30ms
- **Recherche FAISS:** ~5ms
- **Total:** ~100ms par visage

---

## 🐛 Dépannage

### Problèmes courants

**Graphiques ne s'affichent pas:**
- Vérifier que matplotlib est installé
- Vérifier le répertoire `temp_charts/`
- Redémarrer l'application

**Reconnaissance échoue:**
- Vérifier le seuil de reconnaissance (settings.json)
- Vérifier que des embeddings sont enregistrés
- Vérifier l'éclairage de la caméra

**Anti-spoofing trop sensible:**
- Ajuster le seuil dans settings.json
- Désactiver temporairement pour tester

**Connexion MySQL échoue:**
- Vérifier que MySQL est démarré
- Vérifier les credentials dans settings.json
- Vérifier que la base de données existe

---

## 📝 Notes de développement

### Récentes modifications

1. **Correction des appels DatabaseService:**
   - Changé de `get_student_by_matricule` à `find_student_by_matricule`
   - Changé de `get_student_by_id` à `find_student_by_id`
   - Changé de `insert_attendance` à `record_attendance`

2. **Ajout des graphiques professionnels:**
   - Service ChartService avec matplotlib
   - 3 graphiques dans le dashboard
   - Style seaborn professionnel

3. **Bouton de redémarrage:**
   - Ajout dans la sidebar du dashboard
   - Redémarrage automatique de l'application

4. **Correction des chemins:**
   - Chemin absolu pour temp_charts
   - Création automatique du répertoire

---

## 🚧 Améliorations futures

- [ ] Graphiques dans l'écran Reports
- [ ] Export PDF des rapports
- [ ] Notifications par email
- [ ] Mode multi-caméra
- [ ] Reconnaissance par empreinte digitale
- [ ] Application mobile

---

## 📞 Support

Pour toute question ou problème, consultez les logs dans la console pour plus de détails sur les erreurs.

---

**Version:** 1.0  
**Dernière mise à jour:** Juin 2026  
**Développé pour:** Université Catholique du Congo (UCC)
