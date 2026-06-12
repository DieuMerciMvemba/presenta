L'**UCC**, ou **Université Catholique du Congo**, est une institution d'enseignement supérieur de premier plan en République Démocratique du Congo, basée à Kinshasa. Fondée sur des valeurs chrétiennes d'excellence, d'éthique et de rigueur scientifique, elle accueille une population estudiantine nombreuse et diversifiée à travers ses différentes facultés (Droit, Économie, Théologie, Communication sociale, etc.).

Dans le cadre de votre projet de fin d'études — **« Mise en place d’un système de reconnaissance faciale basé sur les réseaux de neurones convolutifs (CNN) pour le pointage automatique des étudiants : Cas de l’UCC »** — voici une description structurée pour alimenter votre travail de recherche.

---

### Description de l'UCC dans le cadre de votre problématique

L'UCC se distingue par son organisation académique structurée, mais fait face, comme beaucoup d'institutions à forte fréquentation, au défi de la gestion administrative de ses auditoires.

#### 1. Le contexte opérationnel actuel

Actuellement, le contrôle de présence est réalisé de manière **manuelle et traditionnelle**. Les professeurs ou les délégués circulent avec des listes papier sur lesquelles les étudiants doivent émarger. Ce processus présente des limites majeures que votre système vise à corriger :

* **Perte de temps :** La signature des listes prend une partie significative du temps de cours (parfois 10 à 15 minutes dans des auditoires de 200 personnes).
* **Risque de fraude :** Le phénomène des « signatures par procuration » (un étudiant signant pour un camarade absent) est fréquent.
* **Archivage laborieux :** La saisie des données papier vers un système numérique est une tâche fastidieuse, sujette à des erreurs de saisie humaine.

#### 2. Pourquoi le choix de l'UCC comme cas d'étude ?

L'UCC constitue un environnement idéal pour implémenter un système de reconnaissance faciale pour plusieurs raisons :

* **Évolutivité :** L'université dispose de multiples sites et auditoires, permettant de tester le système à petite échelle (un cours spécifique) avant une généralisation.
* **Discipline académique :** La culture de l'institution impose une assiduité stricte, ce qui justifie l'investissement technologique.
* **Modernisation :** L'UCC cherche constamment à s'aligner sur les standards internationaux de gestion universitaire numérique (E-learning, gestion des notes en ligne), ce qui rend votre système de pointage biométrique parfaitement cohérent avec sa vision stratégique.

#### 3. Le projet : Vers un « Smart Campus »

Votre système propose une transformation digitale profonde :

* **La technologie CNN (Convolutional Neural Networks) :** En utilisant des architectures comme *ArcFace* (que vous utilisez déjà dans votre code), votre système va extraire des caractéristiques faciales uniques pour identifier l'étudiant avec une précision proche de 100%.
* **Le passage au « Zéro Papier » :** En remplaçant la feuille de présence par une capture vidéo (traitée via votre module `RealtimeFaceDetector`), vous supprimez non seulement le papier, mais aussi la logistique associée (achat de papier, stockage physique, risques de perte des listes).
* **Gain de fiabilité :** Chaque pointage sera horodaté automatiquement dans une base de données (`FAISS`), garantissant une transparence totale pour l'administration et les étudiants.

---
