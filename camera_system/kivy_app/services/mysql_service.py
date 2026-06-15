"""
Service de connexion MySQL pour l'application Kivy
Gère la connexion et les opérations sur la base de données MySQL
"""

import mysql.connector
from mysql.connector import Error
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class MySQLService:
    """Service pour la gestion de la base de données MySQL"""
    
    def __init__(self, host='localhost', database='ucc_face_recognition', 
                 user='root', password='admin123', port=3306):
        """
        Initialise le service MySQL
        
        Args:
            host: Hôte MySQL (défaut: localhost)
            database: Nom de la base de données (défaut: ucc_face_recognition)
            user: Utilisateur MySQL (défaut: root)
            password: Mot de passe MySQL (défaut: vide)
            port: Port MySQL (défaut: 3306)
        """
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port
        self.connection = None
        self.cursor = None
        
    def connect(self) -> bool:
        """
        Établit la connexion à la base de données MySQL
        
        Returns:
            True si la connexion réussit, False sinon
        """
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port
            )
            
            if self.connection.is_connected():
                self.cursor = self.connection.cursor()
                logger.info(f"Connexion MySQL réussie: {self.host}:{self.port}/{self.database}")
                return True
                
        except Error as e:
            logger.error(f"Erreur de connexion MySQL: {e}")
            return False
    
    def disconnect(self):
        """Ferme la connexion à la base de données"""
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("Connexion MySQL fermée")
    
    def create_database(self) -> bool:
        """
        Crée la base de données si elle n'existe pas
        
        Returns:
            True si la création réussit, False sinon
        """
        try:
            # Connexion sans spécifier de base de données
            conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port
            )
            cursor = conn.cursor()
            
            # Créer la base de données
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            cursor.execute(f"USE {self.database}")
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Base de données {self.database} créée avec succès")
            return True
            
        except Error as e:
            logger.error(f"Erreur lors de la création de la base de données: {e}")
            return False
    
    def create_tables(self) -> bool:
        """
        Crée toutes les tables nécessaires pour le système
        
        Returns:
            True si la création réussit, False sinon
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return False
        
        try:
            # Table des utilisateurs (admin)
            users_table = """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                email VARCHAR(100),
                role ENUM('admin', 'user') DEFAULT 'admin',
                date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_username (username)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            # Table des facultés
            faculties_table = """
            CREATE TABLE IF NOT EXISTS faculties (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nom VARCHAR(100) UNIQUE NOT NULL,
                code VARCHAR(20) UNIQUE NOT NULL,
                description TEXT,
                date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_code (code)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            # Table des promotions
            promotions_table = """
            CREATE TABLE IF NOT EXISTS promotions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nom VARCHAR(50) UNIQUE NOT NULL,
                code VARCHAR(20) UNIQUE NOT NULL,
                description TEXT,
                date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_code (code)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            # Table des étudiants
            students_table = """
            CREATE TABLE IF NOT EXISTS students (
                id INT AUTO_INCREMENT PRIMARY KEY,
                matricule VARCHAR(50) UNIQUE NOT NULL,
                nom VARCHAR(100) NOT NULL,
                prenom VARCHAR(100) NOT NULL,
                email VARCHAR(100),
                telephone VARCHAR(20),
                faculte_id INT,
                promotion_id INT,
                photo_path VARCHAR(255),
                embedding_path VARCHAR(255),
                num_photos INT DEFAULT 0,
                date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
                date_modification DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (faculte_id) REFERENCES faculties(id) ON DELETE SET NULL,
                FOREIGN KEY (promotion_id) REFERENCES promotions(id) ON DELETE SET NULL,
                INDEX idx_matricule (matricule),
                INDEX idx_faculte (faculte_id),
                INDEX idx_promotion (promotion_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            # Table des présences
            attendance_table = """
            CREATE TABLE IF NOT EXISTS attendance (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT NOT NULL,
                date_presence DATETIME NOT NULL,
                statut ENUM('present', 'absent', 'retard') DEFAULT 'present',
                methode ENUM('facial', 'manuel', 'qrcode') DEFAULT 'facial',
                confiance FLOAT DEFAULT 0.0,
                photo_capture_path VARCHAR(255),
                camera_id VARCHAR(50),
                notes TEXT,
                date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                INDEX idx_student (student_id),
                INDEX idx_date (date_presence),
                INDEX idx_statut (statut)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            # Table des rapports
            reports_table = """
            CREATE TABLE IF NOT EXISTS reports (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nom VARCHAR(255) NOT NULL,
                type VARCHAR(50) NOT NULL,
                chemin_fichier VARCHAR(255),
                date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
                parametres JSON,
                INDEX idx_type (type),
                INDEX idx_date (date_creation)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            # Table des paramètres système
            settings_table = """
            CREATE TABLE IF NOT EXISTS settings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                cle VARCHAR(100) UNIQUE NOT NULL,
                valeur TEXT,
                description TEXT,
                date_modification DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_cle (cle)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            # Exécuter les créations de tables
            tables = [
                users_table,
                faculties_table,
                promotions_table,
                students_table,
                attendance_table,
                reports_table,
                settings_table
            ]
            
            for table in tables:
                self.cursor.execute(table)
            
            self.connection.commit()
            logger.info("Tables MySQL créées avec succès")
            return True
            
        except Error as e:
            logger.error(f"Erreur lors de la création des tables: {e}")
            return False
    
    def save_setting(self, cle: str, valeur: str, description: str = None) -> bool:
        """
        Sauvegarde ou met à jour un paramètre dans la table settings
        
        Args:
            cle: Clé du paramètre
            valeur: Valeur du paramètre (sera convertie en JSON si c'est un dict)
            description: Description du paramètre (optionnel)
            
        Returns:
            True si réussi, False sinon
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return False
        
        try:
            import json
            
            # Convertir en JSON si c'est un dict
            if isinstance(valeur, (dict, list)):
                valeur = json.dumps(valeur)
            
            query = """
            INSERT INTO settings (cle, valeur, description)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                valeur = VALUES(valeur),
                description = VALUES(description),
                date_modification = CURRENT_TIMESTAMP
            """
            
            self.cursor.execute(query, (cle, valeur, description))
            self.connection.commit()
            
            logger.info(f"Paramètre sauvegardé: {cle}")
            return True
            
        except Error as e:
            logger.error(f"Erreur lors de la sauvegarde du paramètre: {e}")
            return False
    
    def get_setting(self, cle: str, default=None):
        """
        Récupère un paramètre depuis la table settings
        
        Args:
            cle: Clé du paramètre
            default: Valeur par défaut si le paramètre n'existe pas
            
        Returns:
            Valeur du paramètre ou default
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return default
        
        try:
            import json
            
            query = "SELECT valeur FROM settings WHERE cle = %s"
            self.cursor.execute(query, (cle,))
            result = self.cursor.fetchone()
            
            if result:
                valeur = result[0]
                # Essayer de parser comme JSON
                try:
                    parsed = json.loads(valeur)
                    # Convertir les entiers 1/0 en booléens pour les clés spécifiques
                    bool_keys = ['anti_spoof_enabled', 'debug_mode', 'enable_auto_late_detection', 
                                 'enable_daily_duplicate_check', 'enable_auto_absence_calculation']
                    if cle in bool_keys and isinstance(parsed, int):
                        return bool(parsed)
                    # Convertir les entiers 1/0 en booléens si le default est un booléen
                    if isinstance(default, bool) and isinstance(parsed, int):
                        return bool(parsed)
                    return parsed
                except (json.JSONDecodeError, TypeError):
                    # Si ce n'est pas du JSON, essayer de convertir en booléen si nécessaire
                    bool_keys = ['anti_spoof_enabled', 'debug_mode', 'enable_auto_late_detection', 
                                 'enable_daily_duplicate_check', 'enable_auto_absence_calculation']
                    if cle in bool_keys and isinstance(valeur, int):
                        return bool(valeur)
                    if isinstance(default, bool) and isinstance(valeur, int):
                        return bool(valeur)
                    return valeur
            
            return default
            
        except Error as e:
            logger.error(f"Erreur lors de la récupération du paramètre: {e}")
            return default
    
    def get_all_settings(self) -> dict:
        """
        Récupère tous les paramètres depuis la table settings
        
        Returns:
            Dictionnaire des paramètres
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return {}
        
        try:
            import json
            
            query = "SELECT cle, valeur FROM settings"
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            
            settings = {}
            for cle, valeur in results:
                # Essayer de parser comme JSON
                try:
                    settings[cle] = json.loads(valeur)
                except (json.JSONDecodeError, TypeError):
                    settings[cle] = valeur
            
            logger.info(f"Récupéré {len(settings)} paramètres depuis MySQL")
            return settings
            
        except Error as e:
            logger.error(f"Erreur lors de la récupération des paramètres: {e}")
            return {}
    
    def insert_student(self, matricule: str, nom: str, prenom: str, 
                     email: str = None, telephone: str = None, 
                     faculte_id: int = None, promotion_id: int = None,
                     photo_path: str = None,
                     embedding_path: str = None) -> Optional[int]:
        """
        Insère un nouvel étudiant dans la base de données ou met à jour si le matricule existe déjà
        
        Args:
            matricule: Matricule de l'étudiant
            nom: Nom de l'étudiant
            prenom: Prénom de l'étudiant
            email: Email de l'étudiant
            telephone: Téléphone de l'étudiant
            faculte_id: ID de la faculté
            promotion_id: ID de la promotion
            photo_path: Chemin vers la photo
            embedding_path: Chemin vers l'embedding
            
        Returns:
            ID de l'étudiant inséré/mis à jour, None en cas d'erreur
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return None
        
        try:
            # Vérifier si le matricule existe déjà
            self.cursor.execute("SELECT id FROM students WHERE matricule = %s", (matricule,))
            existing = self.cursor.fetchone()
            
            if existing:
                # Mettre à jour l'étudiant existant
                student_id = existing[0]
                query = """
                UPDATE students 
                SET nom = %s, prenom = %s, email = %s, telephone = %s,
                    faculte_id = %s, promotion_id = %s,
                    photo_path = %s, embedding_path = %s
                WHERE id = %s
                """
                values = (nom, prenom, email, telephone, 
                         faculte_id, promotion_id, 
                         photo_path, embedding_path, student_id)
                
                self.cursor.execute(query, values)
                self.connection.commit()
                logger.info(f"Étudiant mis à jour: {matricule} (ID: {student_id})")
                return student_id
            else:
                # Insérer un nouvel étudiant
                query = """
                INSERT INTO students (matricule, nom, prenom, email, telephone, 
                                     faculte_id, promotion_id, 
                                     photo_path, embedding_path)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                values = (matricule, nom, prenom, email, telephone, 
                         faculte_id, promotion_id, 
                         photo_path, embedding_path)
                
                self.cursor.execute(query, values)
                self.connection.commit()
                
                student_id = self.cursor.lastrowid
                logger.info(f"Étudiant inséré: {matricule} (ID: {student_id})")
                return student_id
            
        except Error as e:
            logger.error(f"Erreur lors de l'insertion/mise à jour de l'étudiant: {e}")
            return None
    
    def insert_promotion(self, nom: str, code: str, description: str = None) -> Optional[int]:
        """
        Insère une nouvelle promotion
        
        Args:
            nom: Nom de la promotion (ex: L1, L2, M1, M2)
            code: Code de la promotion
            description: Description de la promotion
            
        Returns:
            ID de la promotion insérée, None en cas d'erreur
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return None
        
        try:
            query = """
            INSERT INTO promotions (nom, code, description)
            VALUES (%s, %s, %s)
            """
            
            values = (nom, code, description)
            
            self.cursor.execute(query, values)
            self.connection.commit()
            
            promotion_id = self.cursor.lastrowid
            logger.info(f"Promotion insérée: {nom} (ID: {promotion_id})")
            return promotion_id
            
        except Error as e:
            logger.error(f"Erreur lors de l'insertion de la promotion: {e}")
            return None
    
    def get_all_faculties(self) -> List[Dict]:
        """
        Récupère toutes les facultés
        
        Returns:
            Liste de dictionnaires contenant les informations des facultés
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return []
        
        try:
            query = "SELECT * FROM faculties ORDER BY nom"
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            
            columns = [desc[0] for desc in self.cursor.description]
            faculties = [dict(zip(columns, row)) for row in results]
            
            logger.info(f"Récupéré {len(faculties)} facultés")
            return faculties
            
        except Error as e:
            logger.error(f"Erreur lors de la récupération des facultés: {e}")
            return []
    
    def get_all_promotions(self) -> List[Dict]:
        """
        Récupère toutes les promotions
        
        Returns:
            Liste de dictionnaires contenant les informations des promotions
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return []
        
        try:
            query = "SELECT * FROM promotions ORDER BY nom"
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            
            columns = [desc[0] for desc in self.cursor.description]
            promotions = [dict(zip(columns, row)) for row in results]
            
            logger.info(f"Récupéré {len(promotions)} promotions")
            return promotions
            
        except Error as e:
            logger.error(f"Erreur lors de la récupération des promotions: {e}")
            return []
    
    def get_promotion_by_id(self, promotion_id: int) -> Optional[Dict]:
        """
        Récupère une promotion par son ID
        
        Args:
            promotion_id: ID de la promotion
            
        Returns:
            Dictionnaire contenant les informations de la promotion, None si non trouvé
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return None
        
        try:
            query = "SELECT * FROM promotions WHERE id = %s"
            self.cursor.execute(query, (promotion_id,))
            result = self.cursor.fetchone()
            
            if result:
                columns = [desc[0] for desc in self.cursor.description]
                return dict(zip(columns, result))
            return None
            
        except Error as e:
            logger.error(f"Erreur lors de la récupération de la promotion: {e}")
            return None
    
    def get_student_by_matricule(self, matricule: str) -> Optional[Dict]:
        """
        Récupère un étudiant par son matricule
        
        Args:
            matricule: Matricule de l'étudiant
            
        Returns:
            Dictionnaire contenant les informations de l'étudiant, None si non trouvé
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return None
        
        try:
            query = "SELECT * FROM students WHERE matricule = %s"
            self.cursor.execute(query, (matricule,))
            result = self.cursor.fetchone()
            
            if result:
                columns = [desc[0] for desc in self.cursor.description]
                return dict(zip(columns, result))
            return None
            
        except Error as e:
            logger.error(f"Erreur lors de la récupération de l'étudiant: {e}")
            return None
    
    def get_all_students(self) -> List[Dict]:
        """
        Récupère tous les étudiants
        
        Returns:
            Liste de dictionnaires contenant les informations des étudiants
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return []
        
        try:
            query = "SELECT * FROM students ORDER BY nom, prenom"
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            
            columns = [desc[0] for desc in self.cursor.description]
            students = [dict(zip(columns, row)) for row in results]
            
            return students
            
        except Error as e:
            logger.error(f"Erreur lors de la récupération des étudiants: {e}")
            return []
    
    def update_student(self, student_id: int, matricule: str = None, 
                      nom: str = None, prenom: str = None, 
                      email: str = None, telephone: str = None,
                      faculte_id: int = None, departement_id: int = None,
                      annee_etude: int = None, photo_path: str = None,
                      embedding_path: str = None) -> bool:
        """
        Met à jour les informations d'un étudiant
        
        Args:
            student_id: ID de l'étudiant
            matricule: Nouveau matricule
            nom: Nouveau nom
            prenom: Nouveau prénom
            email: Nouvel email
            telephone: Nouveau téléphone
            faculte_id: Nouvelle faculté
            departement_id: Nouveau département
            annee_etude: Nouvelle année d'étude
            photo_path: Nouveau chemin photo
            embedding_path: Nouveau chemin embedding
            
        Returns:
            True si la mise à jour réussit, False sinon
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return False
        
        try:
            # Construire la requête dynamiquement
            updates = []
            values = []
            
            if matricule:
                updates.append("matricule = %s")
                values.append(matricule)
            if nom:
                updates.append("nom = %s")
                values.append(nom)
            if prenom:
                updates.append("prenom = %s")
                values.append(prenom)
            if email:
                updates.append("email = %s")
                values.append(email)
            if telephone:
                updates.append("telephone = %s")
                values.append(telephone)
            if faculte_id:
                updates.append("faculte_id = %s")
                values.append(faculte_id)
            if departement_id:
                updates.append("departement_id = %s")
                values.append(departement_id)
            if annee_etude:
                updates.append("annee_etude = %s")
                values.append(annee_etude)
            if photo_path:
                updates.append("photo_path = %s")
                values.append(photo_path)
            if embedding_path:
                updates.append("embedding_path = %s")
                values.append(embedding_path)
            
            if not updates:
                return False
            
            values.append(student_id)
            query = f"UPDATE students SET {', '.join(updates)} WHERE id = %s"
            
            self.cursor.execute(query, values)
            self.connection.commit()
            
            logger.info(f"Étudiant mis à jour: ID {student_id}")
            return True
            
        except Error as e:
            logger.error(f"Erreur lors de la mise à jour de l'étudiant: {e}")
            return False
    
    def delete_student(self, student_id: int) -> bool:
        """
        Supprime un étudiant de la base de données
        
        Args:
            student_id: ID de l'étudiant à supprimer
            
        Returns:
            True si la suppression réussit, False sinon
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return False
        
        try:
            query = "DELETE FROM students WHERE id = %s"
            self.cursor.execute(query, (student_id,))
            self.connection.commit()
            
            logger.info(f"Étudiant supprimé: ID {student_id}")
            return True
            
        except Error as e:
            logger.error(f"Erreur lors de la suppression de l'étudiant: {e}")
            return False
    
    def insert_attendance(self, student_id: int, course_id: int = None,
                         statut: str = 'present', methode: str = 'facial',
                         confiance: float = 0.0, photo_capture_path: str = None,
                         camera_id: str = None, notes: str = None) -> Optional[int]:
        """
        Insère un enregistrement de présence
        
        Args:
            student_id: ID de l'étudiant
            course_id: ID du cours (ignoré, plus utilisé)
            statut: Statut de présence (present, absent, retard)
            methode: Méthode de pointage (facial, manuel, qrcode)
            confiance: Score de confiance de la reconnaissance
            photo_capture_path: Chemin vers la photo capturée
            camera_id: ID de la caméra
            notes: Notes additionnelles
            
        Returns:
            ID de l'enregistrement inséré, None en cas d'erreur
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return None
        
        try:
            query = """
            INSERT INTO attendance (student_id, date_presence, 
                                   statut, methode, confiance, 
                                   photo_capture_path, camera_id, notes)
            VALUES (%s, NOW(), %s, %s, %s, %s, %s, %s)
            """
            
            values = (student_id, statut, methode, confiance,
                     photo_capture_path, camera_id, notes)
            
            self.cursor.execute(query, values)
            self.connection.commit()
            
            attendance_id = self.cursor.lastrowid
            logger.info(f"Présence enregistrée: Étudiant {student_id} (ID: {attendance_id})")
            return attendance_id
            
        except Error as e:
            logger.error(f"Erreur lors de l'enregistrement de présence: {e}")
            return None
    
    def get_student_count(self) -> int:
        """
        Retourne le nombre total d'étudiants
        
        Returns:
            Nombre d'étudiants
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return 0
        
        try:
            query = "SELECT COUNT(*) FROM students"
            self.cursor.execute(query)
            result = self.cursor.fetchone()
            return result[0] if result else 0
            
        except Error as e:
            logger.error(f"Erreur lors du comptage des étudiants: {e}")
            return 0
    
    def get_statistics(self) -> Dict:
        """
        Retourne des statistiques sur la base de données
        
        Returns:
            Dictionnaire contenant les statistiques
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return {}
        
        try:
            stats = {}
            
            # Nombre d'étudiants
            self.cursor.execute("SELECT COUNT(*) FROM students")
            stats['total_students'] = self.cursor.fetchone()[0]
            
            # Nombre de présences
            self.cursor.execute("SELECT COUNT(*) FROM attendance")
            stats['total_attendance'] = self.cursor.fetchone()[0]
            
            # Nombre de facultés
            self.cursor.execute("SELECT COUNT(*) FROM faculties")
            stats['total_faculties'] = self.cursor.fetchone()[0]
            
            # Nombre de promotions
            self.cursor.execute("SELECT COUNT(*) FROM promotions")
            stats['total_promotions'] = self.cursor.fetchone()[0]
            
            # Présences aujourd'hui
            self.cursor.execute("SELECT COUNT(*) FROM attendance WHERE DATE(date_presence) = CURDATE()")
            stats['attendance_today'] = self.cursor.fetchone()[0]
            
            # Présents aujourd'hui
            self.cursor.execute("SELECT COUNT(*) FROM attendance WHERE DATE(date_presence) = CURDATE() AND statut = 'present'")
            stats['present_today'] = self.cursor.fetchone()[0]
            
            # Retards aujourd'hui
            self.cursor.execute("SELECT COUNT(*) FROM attendance WHERE DATE(date_presence) = CURDATE() AND statut = 'retard'")
            stats['late_today'] = self.cursor.fetchone()[0]
            
            return stats
            
        except Error as e:
            logger.error(f"Erreur lors de la récupération des statistiques: {e}")
            return {}
    
    def get_recent_attendance(self, limit: int = 5) -> List[Dict]:
        """
        Récupère les derniers pointages enregistrés
        
        Args:
            limit: Nombre maximum de pointages à récupérer
            
        Returns:
            Liste des derniers pointages
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return []
        
        try:
            query = """
            SELECT a.id, a.date_presence, a.statut, a.methode, a.confiance,
                   s.matricule, s.nom, s.prenom
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            ORDER BY a.date_presence DESC
            LIMIT %s
            """
            self.cursor.execute(query, (limit,))
            results = self.cursor.fetchall()
            
            attendance_list = []
            for row in results:
                attendance_list.append({
                    'id': row[0],
                    'date_presence': row[1],
                    'statut': row[2],
                    'methode': row[3],
                    'confiance': row[4],
                    'matricule': row[5],
                    'nom': row[6],
                    'prenom': row[7]
                })
            
            return attendance_list
            
        except Error as e:
            logger.error(f"Erreur lors de la récupération des derniers pointages: {e}")
            return []
    
    def get_student_attendance_today(self, student_id: int) -> Optional[Dict]:
        """
        Vérifie si un étudiant a déjà été enregistré aujourd'hui (RÈGLE 4: Anti-doublon)
        
        Args:
            student_id: ID de l'étudiant
            
        Returns:
            Dictionnaire avec les informations de présence si trouvé, None sinon
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return None
        
        try:
            query = """
            SELECT id, student_id, date_presence, statut, methode, confiance
            FROM attendance
            WHERE student_id = %s AND DATE(date_presence) = CURDATE()
            LIMIT 1
            """
            self.cursor.execute(query, (student_id,))
            result = self.cursor.fetchone()
            
            if result:
                return {
                    'id': result[0],
                    'student_id': result[1],
                    'date_presence': result[2],
                    'statut': result[3],
                    'methode': result[4],
                    'confiance': result[5]
                }
            
            return None
            
        except Error as e:
            logger.error(f"Erreur lors de la vérification de présence aujourd'hui: {e}")
            return None
    
    def get_daily_report(self, date: str = None) -> Dict:
        """
        Génère le rapport journalier
        
        Args:
            date: Date au format YYYY-MM-DD (défaut: aujourd'hui)
            
        Returns:
            Dictionnaire avec les statistiques du jour
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return {}
        
        try:
            if date is None:
                date = datetime.now().strftime('%Y-%m-%d')
            
            query = """
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN statut = 'present' THEN 1 ELSE 0 END) as presents,
                SUM(CASE WHEN statut = 'absent' THEN 1 ELSE 0 END) as absents,
                SUM(CASE WHEN statut = 'retard' THEN 1 ELSE 0 END) as retards
            FROM attendance
            WHERE DATE(date_presence) = %s
            """
            
            self.cursor.execute(query, (date,))
            result = self.cursor.fetchone()
            
            return {
                'date': date,
                'total': result[0],
                'presents': result[1] or 0,
                'absents': result[2] or 0,
                'retards': result[3] or 0
            }
            
        except Error as e:
            logger.error(f"Erreur lors de la génération du rapport journalier: {e}")
            return {}
    
    def get_faculty_report(self, faculty_id: int = None) -> Dict:
        """
        Génère le rapport par faculté
        
        Args:
            faculty_id: ID de la faculté (si None, rapport pour toutes les facultés)
            
        Returns:
            Dictionnaire avec les statistiques par faculté
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return {}
        
        try:
            if faculty_id:
                query = """
                SELECT 
                    f.nom as faculty_nom,
                    COUNT(DISTINCT s.id) as total_students,
                    COUNT(DISTINCT CASE WHEN a.statut = 'present' THEN a.student_id END) as presents,
                    COUNT(DISTINCT CASE WHEN a.statut = 'retard' THEN a.student_id END) as retards,
                    COUNT(DISTINCT s.id) - COUNT(DISTINCT CASE WHEN a.statut = 'present' THEN a.student_id END) - COUNT(DISTINCT CASE WHEN a.statut = 'retard' THEN a.student_id END) as absents
                FROM faculties f
                LEFT JOIN students s ON f.id = s.faculte_id
                LEFT JOIN attendance a ON s.id = a.student_id AND DATE(a.date_presence) = CURDATE()
                WHERE f.id = %s
                GROUP BY f.id, f.nom
                """
                self.cursor.execute(query, (faculty_id,))
            else:
                query = """
                SELECT 
                    f.nom as faculty_nom,
                    COUNT(DISTINCT s.id) as total_students,
                    COUNT(DISTINCT CASE WHEN a.statut = 'present' THEN a.student_id END) as presents,
                    COUNT(DISTINCT CASE WHEN a.statut = 'retard' THEN a.student_id END) as retards,
                    COUNT(DISTINCT s.id) - COUNT(DISTINCT CASE WHEN a.statut = 'present' THEN a.student_id END) - COUNT(DISTINCT CASE WHEN a.statut = 'retard' THEN a.student_id END) as absents
                FROM faculties f
                LEFT JOIN students s ON f.id = s.faculte_id
                LEFT JOIN attendance a ON s.id = a.student_id AND DATE(a.date_presence) = CURDATE()
                GROUP BY f.id, f.nom
                """
                self.cursor.execute(query)
            
            results = self.cursor.fetchall()
            
            if faculty_id and results:
                return {
                    'faculty_nom': results[0][0],
                    'total_students': results[0][1],
                    'presents': results[0][2],
                    'retards': results[0][3],
                    'absents': results[0][4]
                }
            else:
                return [
                    {
                        'faculty_nom': row[0],
                        'total_students': row[1],
                        'presents': row[2],
                        'retards': row[3],
                        'absents': row[4]
                    }
                    for row in results
                ]
            
        except Error as e:
            logger.error(f"Erreur lors de la génération du rapport par faculté: {e}")
            return {}
    
    def get_promotion_report(self, promotion_id: int = None) -> Dict:
        """
        Génère le rapport par promotion
        
        Args:
            promotion_id: ID de la promotion (si None, rapport pour toutes les promotions)
            
        Returns:
            Dictionnaire avec les statistiques par promotion
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return {}
        
        try:
            if promotion_id:
                query = """
                SELECT 
                    p.nom as promotion_nom,
                    COUNT(DISTINCT s.id) as total_students,
                    COUNT(DISTINCT CASE WHEN a.statut = 'present' THEN a.student_id END) as presents,
                    COUNT(DISTINCT CASE WHEN a.statut = 'retard' THEN a.student_id END) as retards,
                    COUNT(DISTINCT s.id) - COUNT(DISTINCT CASE WHEN a.statut = 'present' THEN a.student_id END) - COUNT(DISTINCT CASE WHEN a.statut = 'retard' THEN a.student_id END) as absents
                FROM promotions p
                LEFT JOIN students s ON p.id = s.promotion_id
                LEFT JOIN attendance a ON s.id = a.student_id AND DATE(a.date_presence) = CURDATE()
                WHERE p.id = %s
                GROUP BY p.id, p.nom
                """
                self.cursor.execute(query, (promotion_id,))
            else:
                query = """
                SELECT 
                    p.nom as promotion_nom,
                    COUNT(DISTINCT s.id) as total_students,
                    COUNT(DISTINCT CASE WHEN a.statut = 'present' THEN a.student_id END) as presents,
                    COUNT(DISTINCT CASE WHEN a.statut = 'retard' THEN a.student_id END) as retards,
                    COUNT(DISTINCT s.id) - COUNT(DISTINCT CASE WHEN a.statut = 'present' THEN a.student_id END) - COUNT(DISTINCT CASE WHEN a.statut = 'retard' THEN a.student_id END) as absents
                FROM promotions p
                LEFT JOIN students s ON p.id = s.promotion_id
                LEFT JOIN attendance a ON s.id = a.student_id AND DATE(a.date_presence) = CURDATE()
                GROUP BY p.id, p.nom
                """
                self.cursor.execute(query)
            
            results = self.cursor.fetchall()
            
            if promotion_id and results:
                return {
                    'promotion_nom': results[0][0],
                    'total_students': results[0][1],
                    'presents': results[0][2],
                    'retards': results[0][3],
                    'absents': results[0][4]
                }
            else:
                return [
                    {
                        'promotion_nom': row[0],
                        'total_students': row[1],
                        'presents': row[2],
                        'retards': row[3],
                        'absents': row[4]
                    }
                    for row in results
                ]
            
        except Error as e:
            logger.error(f"Erreur lors de la génération du rapport par promotion: {e}")
            return {}
    
    def get_student_attendance_history(self, student_id: int, limit: int = 30) -> List[Dict]:
        """
        Récupère l'historique de présence d'un étudiant
        
        Args:
            student_id: ID de l'étudiant
            limit: Nombre maximum d'enregistrements à récupérer
            
        Returns:
            Liste des enregistrements de présence avec date et statut
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return []
        
        try:
            query = """
            SELECT a.date_presence, a.statut, a.methode, a.confiance
            FROM attendance a
            WHERE a.student_id = %s
            ORDER BY a.date_presence DESC
            LIMIT %s
            """
            
            self.cursor.execute(query, (student_id, limit))
            results = self.cursor.fetchall()
            
            attendance_history = []
            for row in results:
                attendance_history.append({
                    'date': row[0].strftime('%d/%m/%Y %H:%M') if row[0] else '',
                    'statut': row[1],
                    'methode': row[2],
                    'confiance': row[3]
                })
            
            logger.info(f"Historique récupéré pour étudiant {student_id}: {len(attendance_history)} enregistrements")
            return attendance_history
            
        except Error as e:
            logger.error(f"Erreur lors de la récupération de l'historique: {e}")
            return []
