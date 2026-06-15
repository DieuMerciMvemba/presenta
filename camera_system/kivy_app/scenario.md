Voici le scénario que je présenterais dans le mémoire et qui correspond parfaitement au sujet :

> **"Mise en place d'un système de reconnaissance faciale basé sur les réseaux de neurones convolutifs pour le pointage automatique des étudiants. Cas de l'UCC."**

---

# 🎬 SCÉNARIO GLOBAL DU SYSTÈME

## Phase 1 : Authentification

L'agent de scolarité ou l'administrateur lance l'application.

Le système affiche l'écran de connexion.

```text
+--------------------------------+
|      UCC FACE ATTENDANCE       |
+--------------------------------+
| Nom utilisateur : ________     |
| Mot de passe : ________        |
|                                |
| [ Se connecter ]              |
+--------------------------------+
```

Après vérification des identifiants, l'utilisateur accède au portail principal.

---

# Phase 2 : Portail Principal

Le portail constitue le centre de contrôle du système.C'est déjà bien fait

---

# Phase 3 : Enrôlement des Étudiants

Avant toute reconnaissance faciale, les étudiants doivent être enregistrés. C'est déjà bien fait

L'administrateur clique sur :

```text
➕ Enrôlement
```

```

---

## Traitement

### MySQL

Le système enregistre :

```text
Matricule
Nom
Prénom
Faculté
Promotion
```

dans la table Students.

---

### Reconnaissance 

Comme d'habitude qui est fait est déjà bon.

---

### FAISS

comme c'est déjà fait, c'est bon
---

### Résultat

```text
✅ Étudiant enregistré avec succès
```

---

# Phase 4 : Gestion Académique

L'utilisateur peut consulter les étudiants par faculté et promotion.

---

## Facultés

```text
🏫 FACULTÉS

Sciences Informatiques
Droit
Économie
Communication
Médecine
...
```

---

## Promotion

En cliquant sur une faculté :

```text
Sciences Informatiques
```

Le système affiche :

```text
L1
L2
L3
M1
M2
```

---

## Liste des étudiants

Exemple :

```text
SCIENCES INFORMATIQUES
LICENCE 2

---------------------------------
Matricule
Nom
Présence du jour
---------------------------------

UCC001
Jean Kabila
✅

UCC002
Marie Ilunga
❌
```

---

# Phase 5 : Pointage Automatique

C'est la partie centrale du projet.

L'utilisateur ouvre :

```text
📸 Pointage Temps Réel
```

---

## Interface

```text
+--------------------------------+
|                                |
|        FLUX CAMÉRA             |
|                                |
+--------------------------------+

Dernier étudiant reconnu :

Nom :
Matricule :
Faculté :
Promotion :

Statut :
```

---

## Fonctionnement

L'étudiant se présente devant la caméra.

### Étape 1

Détection du visage.

```text
Visage détecté
```

---

### Étape 2

Extraction des caractéristiques.

```text
CNN
 ↓
Embedding
```

---

### Étape 3

Recherche dans FAISS.

```text
Embedding
 ↓
FAISS
 ↓
Étudiant correspondant
```

---

### Étape 4

Validation.

Exemple :

```text
Confiance = 0.92
```

---

### Étape 5

Enregistrement.

MySQL ajoute automatiquement :

```text
Étudiant
Date
Heure
Confiance
Méthode = Facial
```

dans Attendance.

---

### Affichage

```text
✅ Présence enregistrée

Jean Kabila

08:02:15
```

---

# Phase 6 : Tableau de Bord Temps Réel

Pendant le pointage, les statistiques se mettent à jour automatiquement.

```text
Étudiants enregistrés : 1250

Présents : 890

Absents : 360

Retards : 95

Taux de présence : 71.2%
```

---

# Phase 7 : Génération des Rapports

L'utilisateur accède au module :

```text
📊 Rapports
```

---

## Rapport Journalier

Permet de consulter la présence d'une journée.

```text
Date : 15/06/2026

Présents : 890

Absents : 360

Retards : 95

Taux : 71.2%
```

Liste détaillée :

```text
Jean Kabila
08:02
Présent

Marie Ilunga
08:15
Retard
```

Export :

```text
PDF
Excel
CSV
```

---

## Rapport par Faculté

Exemple :

```text
Sciences Informatiques

Étudiants : 220

Présents : 205

Absents : 15

Retards : 12

Taux : 93%
```

Graphique comparatif entre toutes les facultés.

---

## Rapport par Promotion

Exemple :

```text
Licence 2

Étudiants : 65

Présents : 60

Absents : 5

Retards : 3

Taux : 92%
```

Graphique comparatif des promotions.

---

## Rapport Individuel Étudiant

Recherche :

```text
Matricule : UCC001
```

Résultat :

```text
Jean Kabila

Présences : 45

Retards : 2

Absences : 1

Taux de présence : 95%
```

Historique complet des présences.

---

# Phase 8 : Administration

Le module Paramètres permet :

```text
Changer mot de passe

Configurer la caméra

Modifier le seuil de reconnaissance

Sauvegarder les données

Exporter la base
```

---

# 🎯 Résumé du flux principal

```text
Connexion
    ↓
Dashboard
    ↓
Enrôlement Étudiant
    ↓
Capture Faciale
    ↓
Stockage MySQL + FAISS
    ↓
Reconnaissance Temps Réel
    ↓
Pointage Automatique
    ↓
Mise à jour des Statistiques
    ↓
Rapports & Analyses
```