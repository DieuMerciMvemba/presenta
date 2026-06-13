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
                 user='root', password='', port=3306):
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
                departement_id INT,
                annee_etude INT,
                photo_path VARCHAR(255),
                embedding_path VARCHAR(255),
                num_photos INT DEFAULT 0,
                date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
                date_modification DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_matricule (matricule),
                INDEX idx_faculte (faculte_id),
                INDEX idx_departement (departement_id)
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
            
            # Table des départements
            departments_table = """
            CREATE TABLE IF NOT EXISTS departments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nom VARCHAR(100) UNIQUE NOT NULL,
                code VARCHAR(20) UNIQUE NOT NULL,
                faculte_id INT,
                description TEXT,
                date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (faculte_id) REFERENCES faculties(id) ON DELETE SET NULL,
                INDEX idx_code (code),
                INDEX idx_faculte (faculte_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            # Table des cours
            courses_table = """
            CREATE TABLE IF NOT EXISTS courses (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nom VARCHAR(100) NOT NULL,
                code VARCHAR(20) UNIQUE NOT NULL,
                departement_id INT,
                credit INT DEFAULT 3,
                description TEXT,
                date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (departement_id) REFERENCES departments(id) ON DELETE SET NULL,
                INDEX idx_code (code),
                INDEX idx_departement (departement_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            # Table des présences
            attendance_table = """
            CREATE TABLE IF NOT EXISTS attendance (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT NOT NULL,
                course_id INT,
                date_presence DATETIME NOT NULL,
                statut ENUM('present', 'absent', 'retard') DEFAULT 'present',
                methode ENUM('facial', 'manuel', 'qrcode') DEFAULT 'facial',
                confiance FLOAT DEFAULT 0.0,
                photo_capture_path VARCHAR(255),
                camera_id VARCHAR(50),
                notes TEXT,
                date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE SET NULL,
                INDEX idx_student (student_id),
                INDEX idx_course (course_id),
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
                students_table,
                faculties_table, 
                departments_table,
                courses_table,
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
    
    def insert_student(self, matricule: str, nom: str, prenom: str, 
                     email: str = None, telephone: str = None, 
                     faculte_id: int = None, departement_id: int = None,
                     annee_etude: int = None, photo_path: str = None,
                     embedding_path: str = None) -> Optional[int]:
        """
        Insère un nouvel étudiant dans la base de données
        
        Args:
            matricule: Matricule de l'étudiant
            nom: Nom de l'étudiant
            prenom: Prénom de l'étudiant
            email: Email de l'étudiant
            telephone: Téléphone de l'étudiant
            faculte_id: ID de la faculté
            departement_id: ID du département
            annee_etude: Année d'étude
            photo_path: Chemin vers la photo
            embedding_path: Chemin vers l'embedding
            
        Returns:
            ID de l'étudiant inséré, None en cas d'erreur
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return None
        
        try:
            query = """
            INSERT INTO students (matricule, nom, prenom, email, telephone, 
                                 faculte_id, departement_id, annee_etude, 
                                 photo_path, embedding_path)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (matricule, nom, prenom, email, telephone, 
                     faculte_id, departement_id, annee_etude, 
                     photo_path, embedding_path)
            
            self.cursor.execute(query, values)
            self.connection.commit()
            
            student_id = self.cursor.lastrowid
            logger.info(f"Étudiant inséré: {matricule} (ID: {student_id})")
            return student_id
            
        except Error as e:
            logger.error(f"Erreur lors de l'insertion de l'étudiant: {e}")
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
            course_id: ID du cours
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
            INSERT INTO attendance (student_id, course_id, date_presence, 
                                   statut, methode, confiance, 
                                   photo_capture_path, camera_id, notes)
            VALUES (%s, %s, NOW(), %s, %s, %s, %s, %s, %s)
            """
            
            values = (student_id, course_id, statut, methode, confiance,
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
            
            # Nombre de départements
            self.cursor.execute("SELECT COUNT(*) FROM departments")
            stats['total_departments'] = self.cursor.fetchone()[0]
            
            # Présences aujourd'hui
            self.cursor.execute("SELECT COUNT(*) FROM attendance WHERE DATE(date_presence) = CURDATE()")
            stats['attendance_today'] = self.cursor.fetchone()[0]
            
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
