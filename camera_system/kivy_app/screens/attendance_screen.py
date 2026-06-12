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

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

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
                    
                    Label:
                        text: '📷 Flux Caméra'
                        font_name: 'Arial'
                        font_size: 18
                        bold: True
                        color: 0.5, 0.5, 0.5, 1
                        halign: 'center'
                        
                    Label:
                        text: 'La caméra sera intégrée ici avec OpenCV'
                        font_name: 'Arial'
                        font_size: 12
                        color: 0.4, 0.4, 0.4, 1
                        halign: 'center'
                        
                    Label:
                        text: 'Anti-Spoofing: ' + ('✅ Actif' if root.anti_spoof_active else '⚠️ Inactif')
                        font_name: 'Arial'
                        font_size: 12
                        color: root.anti_spoof_color
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
                        size_hint_x: 0.3
                        font_name: 'Arial'
                        font_size: 12
                        on_release: root.stop_attendance()
                
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
    anti_spoof_active = BooleanProperty(True)
    detected_count = NumericProperty(0)
    recognized_count = NumericProperty(0)
    spoof_count = NumericProperty(0)
    threshold = 0.5
    session_duration = StringProperty("00:00:00")
    anti_spoof_color = ListProperty([0.16, 0.65, 0.26, 1])
    
    def __init__(self, **kwargs):
        super(AttendanceScreen, self).__init__(**kwargs)
        self.session_timer = None
        self.session_seconds = 0
        self.update_anti_spoof_color()
    
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
    
    def on_leave(self):
        """Appelé lorsque l'écran est quitté"""
        self.stop_attendance()
    
    def start_attendance(self):
        """Démarre la session de pointage"""
        self.is_active = True
        self.session_timer = Clock.schedule_interval(self.update_session_time, 1)
        print("Session de pointage démarrée")
    
    def pause_attendance(self):
        """Met en pause la session de pointage"""
        self.is_active = False
        if self.session_timer:
            self.session_timer.cancel()
        print("Session de pointage en pause")
    
    def stop_attendance(self):
        """Arrête la session de pointage"""
        self.is_active = False
        if self.session_timer:
            self.session_timer.cancel()
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
