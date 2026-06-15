"""
Écran Pointage Caméra pour l'application Kivy
Détection faciale en temps réel avec anti-spoofing
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.camera import Camera
from kivy.graphics import Color, Rectangle
from kivy.properties import BooleanProperty, StringProperty, NumericProperty, ListProperty
from kivy.lang import Builder
from kivy.clock import Clock
import sys
import os
import threading
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from realtime_detector import RealtimeFaceDetector
from services.database_service import DatabaseService

Builder.load_string('''
<AttendanceScreen>:
    name: 'attendance'
    
    BoxLayout:
        orientation: 'vertical'
        
        # Header
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: 70
            padding: 20
            spacing: 10
            canvas.before:
                Color:
                    rgba: 0.0, 0.2, 0.4, 1.0  # UCC_BLUE
                Rectangle:
                    size: self.size
                    pos: self.pos
            
            Label:
                text: '📸 Pointage Caméra - UCC'
                font_name: 'Arial'
                font_size: 22
                bold: True
                color: 1, 1, 1, 1
                size_hint_x: 0.7
                
            BoxLayout:
                orientation: 'horizontal'
                size_hint_x: 0.3
                spacing: 10
                
                Label:
                    text: '🟢 ' + ('Actif' if root.is_active else 'Inactif')
                    font_name: 'Arial'
                    font_size: 14
                    color: 1, 1, 1, 1
                    size_hint_x: 0.5
                    
                Label:
                    text: '👥 ' + str(root.detected_count)
                    font_name: 'Arial'
                    font_size: 14
                    color: 1, 1, 1, 1
                    size_hint_x: 0.5
        
        # Contenu principal
        BoxLayout:
            orientation: 'horizontal'
            padding: 20
            spacing: 20
            
            # Zone caméra
            BoxLayout:
                orientation: 'vertical'
                canvas.before:
                    Color:
                        rgba: 0.0, 0.0, 0.0, 1
                    Rectangle:
                        size: self.size
                        pos: self.pos
                size_hint_x: 0.7
                padding: 15
                spacing: 10
                
                # Placeholder pour la caméra (Kivy Camera sera utilisé ici)
                BoxLayout:
                    orientation: 'vertical'
                    canvas.before:
                        Color:
                            rgba: 0.1, 0.1, 0.1, 1
                        Rectangle:
                            size: self.size
                            pos: self.pos
                    size_hint_y: 0.7
                    
                    # Placeholder pour le widget Camera (créé dynamiquement)
                    BoxLayout:
                        id: camera_container
                        orientation: 'vertical'
                        
                        Label:
                            text: '📷 Flux Caméra'
                            font_name: 'Arial'
                            font_size: 18
                            bold: True
                            color: 0.5, 0.5, 0.5, 1
                            halign: 'center'
                            
                        Label:
                            text: 'Cliquez sur "Démarrer" pour activer la caméra'
                            font_name: 'Arial'
                            font_size: 12
                            color: 0.4, 0.4, 0.4, 1
                            halign: 'center'
                
                # Contrôles caméra
                BoxLayout:
                    orientation: 'horizontal'
                    size_hint_y: None
                    height: 60
                    spacing: 10
                    
                    Button:
                        text: '▶️ Démarrer'
                        background_color: 0.16, 0.65, 0.26, 1.0
                        color: 1, 1, 1, 1
                        size_hint_x: 0.3
                        font_name: 'Arial'
                        font_size: 12
                        on_release: root.start_attendance()
                        
                    Button:
                        text: '⏸️ Pause'
                        background_color: 1.0, 0.75, 0.07, 1.0
                        color: 0, 0, 0, 1
                        size_hint_x: 0.3
                        font_name: 'Arial'
                        font_size: 12
                        on_release: root.pause_attendance()
                        
                    Button:
                        text: '⏹️ Arrêter'
                        background_color: 0.86, 0.21, 0.27, 1.0
                        color: 1, 1, 1, 1
                        size_hint_x: 0.25
                        font_name: 'Arial'
                        font_size: 12
                        on_release: root.stop_attendance()
                        
                    Button:
                        text: '🔄 Recharger'
                        background_color: 0.09, 0.64, 0.72, 1.0
                        color: 1, 1, 1, 1
                        size_hint_x: 0.25
                        font_name: 'Arial'
                        font_size: 12
                        on_release: root.load_settings()
                
                # Informations de session
                BoxLayout:
                    orientation: 'horizontal'
                    size_hint_y: None
                    height: 40
                    spacing: 10
                    
                    Label:
                        text: '⏱️ Durée: ' + root.session_duration
                        font_name: 'Arial'
                        font_size: 11
                        color: 0.4, 0.4, 0.4, 1
                        size_hint_x: 0.5
                        
                    Label:
                        text: '🎯 Seuil: ' + str(root.threshold)
                        font_name: 'Arial'
                        font_size: 11
                        color: 0.4, 0.4, 0.4, 1
                        size_hint_x: 0.5
                
                # Dernier étudiant reconnu
                BoxLayout:
                    orientation: 'horizontal'
                    size_hint_y: None
                    height: 30
                    spacing: 10
                    
                    Label:
                        text: '👤 Dernier reconnu:'
                        font_name: 'Arial'
                        font_size: 11
                        color: 0.4, 0.4, 0.4, 1
                        size_hint_x: 0.5
                        
                    Label:
                        text: root.last_recognized
                        font_name: 'Arial'
                        font_size: 11
                        bold: True
                        color: 0.16, 0.65, 0.26, 1
                        size_hint_x: 0.5
            
            # Sidebar informations
            BoxLayout:
                orientation: 'vertical'
                canvas.before:
                    Color:
                        rgba: 1, 1, 1, 1
                    Rectangle:
                        size: self.size
                        pos: self.pos
                size_hint_x: 0.3
                padding: 15
                spacing: 10
                
                Label:
                    text: '📊 Session en Cours'
                    font_name: 'Arial'
                    font_size: 16
                    bold: True
                    color: 0.0, 0.2, 0.4, 1
                    size_hint_y: None
                    height: 30
                
                # Statistiques
                BoxLayout:
                    orientation: 'vertical'
                    spacing: 8
                    
                    BoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: 30
                        canvas.before:
                            Color:
                                rgba: 0.95, 0.95, 0.95, 1
                            Rectangle:
                                size: self.size
                                pos: self.pos
                        padding: 10
                        spacing: 5
                        
                        Label:
                            text: 'Visages détectés:'
                            font_name: 'Arial'
                            font_size: 11
                            color: 0.4, 0.4, 0.4, 1
                            size_hint_x: 0.6
                            
                        Label:
                            text: str(root.detected_count)
                            font_name: 'Arial'
                            font_size: 11
                            bold: True
                            color: 0.0, 0.5, 1.0, 1
                            size_hint_x: 0.4
                    
                    BoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: 30
                        canvas.before:
                            Color:
                                rgba: 0.95, 0.95, 0.95, 1
                            Rectangle:
                                size: self.size
                                pos: self.pos
                        padding: 10
                        spacing: 5
                        
                        Label:
                            text: 'Étudiants reconnus:'
                            font_name: 'Arial'
                            font_size: 11
                            color: 0.4, 0.4, 0.4, 1
                            size_hint_x: 0.6
                            
                        Label:
                            text: str(root.recognized_count)
                            font_name: 'Arial'
                            font_size: 11
                            bold: True
                            color: 0.16, 0.65, 0.26, 1
                            size_hint_x: 0.4
                    
                    BoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: 30
                        canvas.before:
                            Color:
                                rgba: 0.95, 0.95, 0.95, 1
                            Rectangle:
                                size: self.size
                                pos: self.pos
                        padding: 10
                        spacing: 5
                        
                        Label:
                            text: 'Fraudes détectées:'
                            font_name: 'Arial'
                            font_size: 11
                            color: 0.4, 0.4, 0.4, 1
                            size_hint_x: 0.6
                            
                        Label:
                            text: str(root.spoof_count)
                            font_name: 'Arial'
                            font_size: 11
                            bold: True
                            color: 0.86, 0.21, 0.27, 1
                            size_hint_x: 0.4
                
                BoxLayout:
                    size_hint_y: 1
                
                Label:
                    text: '👥 Étudiants Présents'
                    font_name: 'Arial'
                    font_size: 14
                    bold: True
                    color: 0.0, 0.2, 0.4, 1
                    size_hint_y: None
                    height: 30
                
                Label:
                    text: 'Aucun étudiant détecté'
                    font_name: 'Arial'
                    font_size: 11
                    color: 0.4, 0.4, 0.4, 1
                    size_hint_y: None
                    height: 20
                
                BoxLayout:
                    orientation: 'vertical'
                    size_hint_y: None
                    height: 50
                    spacing: 5
                    
                    Button:
                        text: '💾 Sauvegarder Rapport'
                        background_color: 0.43, 0.26, 0.76, 1.0
                        color: 1, 1, 1, 1
                        font_name: 'Arial'
                        font_size: 11
                        on_release: root.save_report()
                        
                    Button:
                        text: '🔄 Réinitialiser Session'
                        background_color: 0.42, 0.46, 0.49, 1.0
                        color: 1, 1, 1, 1
                        font_name: 'Arial'
                        font_size: 11
                        on_release: root.reset_session()
''')

class AttendanceScreen(Screen):
    """Écran Pointage Caméra avec Anti-Spoofing"""
    
    is_active = BooleanProperty(False)
    anti_spoof_active = BooleanProperty(False)
    detected_count = NumericProperty(0)
    recognized_count = NumericProperty(0)
    spoof_count = NumericProperty(0)
    threshold = NumericProperty(0.5)
    spoof_threshold = NumericProperty(0.85)
    session_duration = StringProperty("00:00:00")
    anti_spoof_color = ListProperty([0.16, 0.65, 0.26, 1])
    last_recognized = StringProperty("Aucun")
    camera_index = NumericProperty(0)
    resolution = StringProperty("1280x720")
    
    def get_resolution_list(self):
        """Retourne la résolution sous forme de liste d'entiers"""
        try:
            return [int(x) for x in self.resolution.split('x')]
        except:
            return [1280, 720]
    
    def __init__(self, **kwargs):
        super(AttendanceScreen, self).__init__(**kwargs)
        self.session_timer = None
        self.session_seconds = 0
        self.update_anti_spoof_color()
        
        # Initialiser les paramètres de règles par défaut
        self.late_time_limit = "08:00"
        self.enable_auto_late_detection = True
        self.enable_daily_duplicate_check = True
        self.enable_auto_absence_calculation = True
        
        # Charger les paramètres de configuration
        self.load_settings()
        
        # Initialiser RealtimeFaceDetector avec les paramètres de configuration (sans caméra)
        try:
            # Créer une instance de RealtimeFaceDetector sans ouvrir la caméra
            # Nous allons initialiser manuellement les composants sans la caméra
            from vector_db import LocalVectorDB
            from pipeline import FacePipeline
            from anti_spoof import AntiSpoofDetector
            from config import Config
            
            # Initialiser la base de données (chemin absolu via Config pour éviter les erreurs de CWD)
            os.makedirs(Config.DATA_PATH, exist_ok=True)
            self.db = LocalVectorDB(
                index_path=os.path.join(Config.DATA_PATH, "facerec_faiss.index"),
                metadata_path=os.path.join(Config.DATA_PATH, "students_metadata.pkl")
            )
            print(f"✅ Base de données chargée: {self.db.get_student_count()} étudiants")
            
            # Initialiser le pipeline
            self.pipeline = FacePipeline()
            print("✅ Pipeline initialisé")
            
            # Initialiser le détecteur d'anti-spoofing
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_path = os.path.join(script_dir, "models", "silent_face_v2.onnx")
            self.anti_spoof = AntiSpoofDetector(model_path=model_path)
            print("✅ Anti-spoofing initialisé")
            
            # Stocker les paramètres pour la caméra
            self.camera_index = self.camera_index
            self.threshold = self.threshold
            
            # Variables pour le suivi des étudiants présents
            self.present_students = set()
            self.last_recognition_time = {}
            self.recognition_cooldown = 3.0
            
            print("✅ Composants RealtimeFaceDetector initialisés sans caméra")
        except Exception as e:
            print(f"❌ Erreur lors de l'initialisation des composants RealtimeFaceDetector: {e}")
            self.db = None
            self.pipeline = None
            self.anti_spoof = None
        
        # Initialiser DatabaseService pour l'enregistrement des présences
        try:
            self.db_service = DatabaseService(
                host='localhost',
                database='ucc_face_recognition',
                user='root',
                password='admin123',
                port=3306
            )
            print("✅ DatabaseService initialisé")
        except Exception as e:
            print(f"❌ Erreur lors de l'initialisation de DatabaseService: {e}")
            self.db_service = None
    
    def update_anti_spoof_color(self):
        """Met à jour la couleur de l'indicateur anti-spoofing"""
        if self.anti_spoof_active:
            self.anti_spoof_color = [0.16, 0.65, 0.26, 1]  # Vert
        else:
            self.anti_spoof_color = [0.86, 0.21, 0.27, 1]  # Rouge
    
    def on_anti_spoof_active(self, instance, value):
        """Appelé quand anti_spoof_active change"""
        self.update_anti_spoof_color()
    
    def on_enter(self):
        """Appelé lorsque l'écran est affiché"""
        self.reset_session()
        self.load_settings()  # Recharger les paramètres à chaque entrée
    
    def load_settings(self):
        """Charge les paramètres de configuration depuis MySQL"""
        try:
            from services.mysql_service import MySQLService
            
            mysql_service = MySQLService(
                host='localhost',
                database='ucc_face_recognition',
                user='root',
                password='admin123',
                port=3306
            )
            
            # Charger depuis MySQL
            self.threshold = mysql_service.get_setting('threshold', 0.5)
            self.spoof_threshold = mysql_service.get_setting('spoof_threshold', 0.85)
            self.anti_spoof_active = mysql_service.get_setting('anti_spoof_enabled', False)
            self.camera_index = mysql_service.get_setting('camera_index', 0)
            self.resolution = mysql_service.get_setting('resolution', "1280x720")
            self.session_duration_limit = mysql_service.get_setting('session_duration', 60)
            
            # Charger les paramètres de règles de présence
            attendance_rules = mysql_service.get_setting('attendance_rules', {})
            self.late_time_limit = attendance_rules.get('late_time_limit', "08:00")
            self.enable_auto_late_detection = attendance_rules.get('enable_auto_late_detection', True)
            self.enable_daily_duplicate_check = attendance_rules.get('enable_daily_duplicate_check', True)
            self.enable_auto_absence_calculation = attendance_rules.get('enable_auto_absence_calculation', True)
            
            print(f"✅ Paramètres chargés dans AttendanceScreen depuis MySQL: threshold={self.threshold}, spoof_threshold={self.spoof_threshold}, anti_spoof={self.anti_spoof_active}")
            print(f"✅ Règles de présence: late_time_limit={self.late_time_limit}, auto_late={self.enable_auto_late_detection}, duplicate_check={self.enable_daily_duplicate_check}")
            
            # Mettre à jour l'indicateur anti-spoofing
            self.update_anti_spoof_color()
                
        except Exception as e:
            print(f"❌ Erreur lors du chargement des paramètres depuis MySQL: {e}")
            print(f"ℹ️ Utilisation des valeurs par défaut")
            # Valeurs par défaut pour les règles
            self.late_time_limit = "08:00"
            self.enable_auto_late_detection = True
            self.enable_daily_duplicate_check = True
            self.enable_auto_absence_calculation = True
    
    def on_leave(self):
        """Appelé lorsque l'écran est quitté"""
        self.stop_attendance()
    
    def start_attendance(self):
        """Démarre la session de pointage"""
        self.is_active = True
        self.session_timer = Clock.schedule_interval(self.update_session_time, 1)
        print("Session de pointage démarrée")
        
        # Créer dynamiquement le widget Camera
        try:
            from kivy.uix.camera import Camera
            camera_container = self.ids.camera_container
            camera_container.clear_widgets()
            
            # Créer le widget Camera avec les paramètres de configuration
            camera_widget = Camera(
                index=self.camera_index,
                resolution=self.get_resolution_list(),
                play=True,
                size_hint_y=1
            )
            camera_container.add_widget(camera_widget)
            
            # Stocker la référence pour pouvoir l'arrêter plus tard
            self.camera_widget = camera_widget
            
            print(f"📷 Caméra démarrée (index: {self.camera_index}, résolution: {self.resolution})")
            
            # Démarrer la boucle de traitement des frames
            self.frame_processor = Clock.schedule_interval(self.process_camera_frame, 0.1)  # 10 FPS
            print("🔄 Boucle de traitement des frames démarrée")
            
            # Démarrer la reconnaissance faciale en temps réel
            if self.pipeline:
                print("✅ Reconnaissance faciale en temps réel activée")
                
        except Exception as e:
            print(f"❌ Erreur lors du démarrage de la caméra: {e}")
    
    def pause_attendance(self):
        """Met en pause la session de pointage"""
        self.is_active = False
        if self.session_timer:
            self.session_timer.cancel()
        
        # Arrêter le processeur de frames mais garder la caméra active
        if hasattr(self, 'frame_processor') and self.frame_processor:
            self.frame_processor.cancel()
            print("⏸️ Processeur de frames en pause")
        
        # Mettre la caméra en pause
        if hasattr(self, 'camera_widget') and self.camera_widget:
            self.camera_widget.play = False
            print("📷 Caméra mise en pause")
        
        print("Session de pointage en pause")
    
    def stop_attendance(self):
        """Arrête la session de pointage"""
        self.is_active = False
        if self.session_timer:
            self.session_timer.cancel()
        
        # Arrêter le processeur de frames
        if hasattr(self, 'frame_processor') and self.frame_processor:
            self.frame_processor.cancel()
            print("⏹️ Processeur de frames arrêté")
        
        # Arrêter et supprimer la caméra
        if hasattr(self, 'camera_widget') and self.camera_widget:
            self.camera_widget.play = False
            camera_container = self.ids.camera_container
            camera_container.remove_widget(self.camera_widget)
            self.camera_widget = None
            print("📷 Caméra arrêtée et supprimée")
        
        # Restaurer le placeholder
        from kivy.uix.label import Label
        camera_container = self.ids.camera_container
        camera_container.clear_widgets()
        camera_container.add_widget(Label(
            text='📷 Flux Caméra',
            font_name='Arial',
            font_size=18,
            bold=True,
            color=[0.5, 0.5, 0.5, 1],
            halign='center',
            size_hint_y=None,
            height=30
        ))
        camera_container.add_widget(Label(
            text='Cliquez sur "Démarrer" pour activer la caméra',
            font_name='Arial',
            font_size=12,
            color=[0.4, 0.4, 0.4, 1],
            halign='center',
            size_hint_y=None,
            height=25
        ))
        
        print("Session de pointage arrêtée")
    
    def reset_session(self):
        """Réinitialise la session"""
        self.detected_count = 0
        self.recognized_count = 0
        self.spoof_count = 0
        self.session_seconds = 0
        self.session_duration = "00:00:00"
        if self.session_timer:
            self.session_timer.cancel()
        self.is_active = False
    
    def update_session_time(self, dt):
        """Met à jour le temps de session"""
        self.session_seconds += 1
        hours = self.session_seconds // 3600
        minutes = (self.session_seconds % 3600) // 60
        seconds = self.session_seconds % 60
        self.session_duration = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        # Vérifier si la durée de session est atteinte
        if hasattr(self, 'session_duration_limit') and self.session_seconds >= self.session_duration_limit:
            print(f"⏱️ Durée de session atteinte ({self.session_duration_limit} secondes)")
            self.stop_attendance()
    
    def process_camera_frame(self, dt):
        """
        Traite une image de la caméra pour la reconnaissance faciale en utilisant les composants de RealtimeFaceDetector
        
        Args:
            dt: Delta time (non utilisé)
        """
        if not self.pipeline or not self.is_active:
            return
        
        try:
            # Capturer la frame depuis le widget Camera Kivy dynamique
            if not hasattr(self, 'camera_widget') or not self.camera_widget:
                return
            
            camera_widget = self.camera_widget
            if not camera_widget.play:
                return
            
            # Convertir la texture de la caméra en numpy array
            texture = camera_widget.texture
            if texture is None:
                return
            
            # Obtenir les pixels de la texture
            pixels = texture.pixels
            if pixels is None:
                return
            
            # Convertir en numpy array de manière robuste selon le format de couleur
            import numpy as np
            import cv2
            import time
            
            colorfmt = texture.colorfmt
            channels = 4 if 'alpha' in colorfmt or len(colorfmt) == 4 else 3
            
            frame = np.frombuffer(pixels, dtype=np.uint8)
            frame = frame.reshape(texture.height, texture.width, channels)
            
            # Convertir dans le format BGR attendu par OpenCV
            if colorfmt == 'rgba':
                frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)
            elif colorfmt == 'rgb':
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            elif colorfmt == 'bgra':
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            else:
                # Fallback
                frame = frame[:, :, :3]
            
            # ÉTAPE 2: MTCNN (Multi-visages) - Détection de tous les visages dans la frame
            faces = self.pipeline.detector.detect_faces(frame)
            if len(faces) > 0:
                print(f"MTCNN: {len(faces)} visage(s) détecté(s)")
            
            detected_info = []
            
            for face in faces:
                bbox = face['box']
                keypoints = face.get('keypoints', None)
                confidence = face.get('confidence', 0.0)
                
                x, y, w, h = bbox
                
                # ÉTAPE 3: BARRIÈRE ANTI-SPOOFING (Vérification de vivacité)
                # Vérifier si l'anti-spoofing est activé dans les paramètres
                if self.anti_spoof_active and self.anti_spoof:
                    is_real, spoof_score = self.anti_spoof.is_real(frame, bbox, threshold=self.spoof_threshold)
                else:
                    # Si l'anti-spoofing est désactivé, considérer tous les visages comme réels
                    is_real, spoof_score = True, 1.0
                
                if not is_real:
                    print(f"🚨 TENTATIVE DE FRAUDE DÉTECTÉE ! Score de vivacité : {spoof_score:.4f}")
                    self.spoof_count += 1
                    detected_info.append({
                        'name': 'FRAUDE DETECTEE',
                        'matricule': 'N/A',
                        'similarity': None,
                        'bbox': bbox,
                        'recognized': False,
                        'spoof': True
                    })
                    continue  # Court-circuit : On passe immédiatement au visage suivant
                
                # Si le visage est validé comme RÉEL
                try:
                    # ÉTAPE 4: ALIGNEMENT - Alignement du visage avec MediaPipe/MTCNN keypoints
                    aligned_face = self.pipeline.align_face(frame, bbox, keypoints=keypoints)
                    
                    # ÉTAPE 5: ArcFace - Extraction de l'embedding facial 512-D
                    embedding = self.pipeline.get_embedding(aligned_face)
                    
                    # ÉTAPE 6: Recherche FAISS - Recherche du visage dans la base de données vectorielle
                    result = self.db.search_face(embedding, threshold=self.threshold)
                    
                    current_time = time.time()
                    
                    if result:
                        student_info = result['metadata']
                        similarity = result['similarity']
                        student_id = result['id']
                        
                        # Vérifier le cooldown pour éviter les reconnaissances multiples saccadées
                        if student_id not in self.last_recognition_time or \
                           (current_time - self.last_recognition_time[student_id]) > self.recognition_cooldown:
                            
                            # ÉTAPE 7: MARQUAGE PRÉSENT - Marquer l'étudiant comme présent
                            self.present_students.add(student_id)
                            self.last_recognition_time[student_id] = current_time
                            
                            # Informations sur l'étudiant reconnu
                            name = f"{student_info['prenom']} {student_info['nom']}"
                            matricule = student_info['matricule']
                            
                            detected_info.append({
                                'name': name,
                                'matricule': matricule,
                                'similarity': similarity,
                                'bbox': bbox,
                                'recognized': True,
                                'spoof': False
                            })
                            
                            self.recognized_count += 1
                            self.last_recognized = f"{name} ({matricule})"
                            self.record_attendance_from_info(detected_info[-1])
                            print(f"✅ Étudiant reconnu: {name} ({matricule}) - Similarité: {similarity:.2f}")
                    else:
                        print("⚠️ Visage détecté mais non reconnu")
                        
                except Exception as e:
                    print(f"❌ Erreur lors du traitement du visage: {e}")
            
            # Mettre à jour le compteur de visages détectés
            if faces and len(faces) > 0:
                self.detected_count += len(faces)
                        
        except Exception as e:
            print(f"❌ Erreur lors du traitement de l'image: {e}")
    
    def recognize_student(self, embedding):
        """
        Reconnaît un étudiant à partir de son embedding
        
        Args:
            embedding: Embedding facial (numpy array)
            
        Returns:
            dict: Informations de l'étudiant ou None si non reconnu
        """
        try:
            # Importer la base de données vectorielle locale
            from vector_db import LocalVectorDB
            db = LocalVectorDB()
            
            # Rechercher l'étudiant le plus proche
            result = db.search(embedding, k=1)
            
            if result and len(result) > 0:
                # Vérifier si la similarité est suffisante
                similarity = result[0]['similarity']
                if similarity >= self.threshold:
                    student_id = result[0]['student_id']
                    # Récupérer les informations de l'étudiant depuis MySQL
                    student_data = self.db_service.find_student_by_id(student_id)
                    if student_data:
                        # Accéder aux métadonnées de l'étudiant
                        return student_data.get('metadata', student_data)
            
            return None
            
        except Exception as e:
            print(f"❌ Erreur lors de la reconnaissance: {e}")
            return None
    
    def record_attendance(self, student):
        """
        Enregistre la présence d'un étudiant dans MySQL
        
        Args:
            student: Informations de l'étudiant
        """
        if not self.db_service:
            return
        
        try:
            # Vérifier si l'étudiant n'a pas déjà été pointé aujourd'hui
            from datetime import datetime
            today = datetime.now().date()
            
            # Enregistrer la présence
            attendance_id = self.db_service.record_attendance(
                student_id=student['id'],
                statut='present',
                methode='facial',
                confiance=0.95  # Confiance par défaut
            )
            
            if attendance_id:
                print(f"✅ Présence enregistrée pour {student['matricule']}")
            else:
                print(f"⚠️ Erreur lors de l'enregistrement de la présence")
                
        except Exception as e:
            print(f"❌ Erreur lors de l'enregistrement de la présence: {e}")
    
    def record_attendance_from_info(self, face_info):
        """
        Enregistre la présence d'un étudiant depuis les informations de RealtimeFaceDetector
        
        Args:
            face_info: Dictionnaire contenant les informations du visage reconnu
        """
        if not self.db_service:
            return
        
        try:
            # Extraire le matricule depuis les informations de visage
            matricule = face_info.get('matricule', None)
            if not matricule:
                return
            
            # Récupérer l'étudiant depuis MySQL pour obtenir son ID
            student_data = self.db_service.find_student_by_matricule(matricule)
            if not student_data:
                print(f"❌ Étudiant avec matricule {matricule} non trouvé dans MySQL")
                return
            
            # Accéder aux métadonnées de l'étudiant
            student = student_data.get('metadata', student_data)
            student_id = student['id']
            
            # RÈGLE 4: Anti-doublon journalier
            if self.enable_daily_duplicate_check:
                from datetime import datetime
                today = datetime.now().date()
                
                # Vérifier si l'étudiant a déjà été enregistré aujourd'hui
                existing_attendance = self.db_service.get_student_attendance_today(student_id)
                if existing_attendance:
                    print(f"⚠️ Étudiant {matricule} déjà enregistré aujourd'hui (anti-doublon)")
                    return
            
            # RÈGLE 5: Détermination automatique du retard
            statut = 'present'
            if self.enable_auto_late_detection:
                from datetime import datetime
                current_time = datetime.now().time()
                
                # Convertir l'heure limite en objet time
                try:
                    late_limit = datetime.strptime(self.late_time_limit, "%H:%M").time()
                    
                    # Si l'heure actuelle est après l'heure limite, statut = retard
                    if current_time > late_limit:
                        statut = 'retard'
                        print(f"⏰ Étudiant {matricule} en retard (heure: {current_time}, limite: {late_limit})")
                except Exception as e:
                    print(f"❌ Erreur lors de la détermination du retard: {e}")
            
            # Enregistrer la présence dans MySQL
            from datetime import datetime
            attendance_id = self.db_service.record_attendance(
                student_id=student_id,
                course_id=None,
                statut=statut,
                methode='facial',
                confiance=face_info.get('similarity', 0.0),
                photo_capture_path=None,
                camera_id=str(self.camera_index),
                notes=None
            )
            
            if attendance_id:
                print(f"✅ Présence enregistrée pour {matricule} (statut: {statut}, ID: {attendance_id})")
            else:
                print(f"❌ Erreur lors de l'enregistrement de la présence pour {matricule}")
        except Exception as e:
            print(f"❌ Erreur lors de l'enregistrement de la présence: {e}")
    
    def save_report(self):
        """Sauvegarde le rapport de présence"""
        print("Sauvegarde du rapport...")
        # Cette fonction sera implémentée avec le service AttendanceService
    
    def increment_detected(self):
        """Incrémente le compteur de visages détectés"""
        self.detected_count += 1
    
    def increment_recognized(self):
        """Incrémente le compteur d'étudiants reconnus"""
        self.recognized_count += 1
    
    def increment_spoof(self):
        """Incrémente le compteur de fraudes détectées"""
        self.spoof_count += 1
