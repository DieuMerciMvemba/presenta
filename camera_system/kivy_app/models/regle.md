# 📋 Règles de Fonctionnement du Système de Pointage Automatique

## 1. Règle d'Enrôlement des Étudiants

Avant de pouvoir être reconnu par le système, chaque étudiant doit être enregistré.

Lors de l'enrôlement, les informations suivantes sont associées à l'étudiant :

* Matricule
* Nom et prénom
* Faculté
* Promotion
* Photographie faciale

Le système extrait ensuite les caractéristiques biométriques du visage afin de créer une empreinte faciale numérique unique qui servira lors des futures reconnaissances.

---

# 2. Règle de Détection et de Reconnaissance

Lorsqu'un étudiant se présente devant la caméra :

1. Le système détecte automatiquement le visage.
2. Le système vérifie qu'il s'agit d'une personne réelle et non d'une photo ou d'une tentative de fraude.
3. Les caractéristiques du visage sont extraites.
4. Le visage est comparé aux visages enregistrés dans la base de données.
5. Si une correspondance fiable est trouvée, l'étudiant est identifié.

---

# 3. Règle de Validation de Présence

Une présence est validée uniquement lorsque :

* Le visage est reconnu avec un niveau de confiance suffisant ;
* Le contrôle anti-fraude est réussi ;
* L'étudiant n'a pas déjà été enregistré pour la même journée.

Si toutes ces conditions sont réunies, la présence est enregistrée automatiquement.

---

# 4. Règle Anti-Doublon

Le système ne doit enregistrer qu'une seule présence par étudiant et par jour.

Si un étudiant déjà enregistré repasse devant la caméra durant la même journée :

* son identité peut être reconnue ;
* mais aucune nouvelle présence n'est enregistrée.

Cette règle garantit la fiabilité des statistiques de présence.

---

# 5. Règle de Détermination du Retard

L'établissement définit une heure limite de présence.

Exemple :

```text
Heure normale d'arrivée : 08h00
```

Si l'étudiant est reconnu avant cette heure, son statut est :

```text
Présent
```

Si l'étudiant est reconnu après cette heure, son statut devient :

```text
Retard
```

Cette règle permet de distinguer les étudiants ponctuels des étudiants arrivés en retard.

---

# 6. Règle de Détermination des Absences

Un étudiant est considéré absent lorsqu'aucune présence n'a été enregistrée pour lui durant la journée concernée.

L'absence n'est donc pas détectée directement par la caméra.

Elle est calculée automatiquement en comparant :

* le nombre total d'étudiants enregistrés ;
* le nombre d'étudiants effectivement pointés.

Cette méthode permet d'obtenir la liste complète des absents.

---

# 7. Règle de Mise à Jour des Statistiques

Chaque nouveau pointage met automatiquement à jour :

* le nombre de présents ;
* le nombre de retardataires ;
* le nombre d'absents ;
* le taux global de présence.

Les statistiques sont ainsi disponibles en temps réel sur le tableau de bord.

---

# 8. Règle des Rapports Journaliers

Le rapport journalier présente :

* la date du pointage ;
* le nombre total d'étudiants ;
* le nombre de présents ;
* le nombre de retardataires ;
* le nombre d'absents ;
* le taux de présence ;
* la liste détaillée des étudiants pointés.

---

# 9. Règle des Rapports par Faculté

Le système regroupe les données selon les facultés.

Pour chaque faculté, il fournit :

* le nombre total d'étudiants ;
* le nombre de présents ;
* le nombre de retardataires ;
* le nombre d'absents ;
* le taux de présence.

Cette vue permet aux responsables académiques d'évaluer la participation des étudiants de leur faculté.

---

# 10. Règle des Rapports par Promotion

Le système regroupe également les données par promotion (L1, L2, L3, M1, M2).

Pour chaque promotion, il affiche :

* le nombre total d'étudiants ;
* le nombre de présents ;
* le nombre de retardataires ;
* le nombre d'absents ;
* le taux de présence.

Cette analyse facilite le suivi de l'assiduité des différentes promotions.

---


Cette logique est parfaitement cohérente avec le sujet : **système de reconnaissance faciale basé sur les réseaux de neurones convolutifs pour le pointage automatique des étudiants à l'UCC**.

