"""
Écran Paramètres pour l'application Kivy
Configuration des seuils, caméra et autres paramètres
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.slider import Slider
from kivy.uix.button import Button
from kivy.uix.switch import Switch
from kivy.graphics import Color, Rectangle
from kivy.properties import NumericProperty, BooleanProperty, StringProperty
from kivy.lang import Builder
import json
import os

Builder.load_string('''
<SettingsScreen>:
    name: 'settings'
    
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
                text: '⚙️ Paramètres - UCC'
                font_name: 'Arial'
                font_size: 22
                bold: True
                color: 1, 1, 1, 1
                size_hint_x: 0.7
                
            Button:
                text: '💾 Sauvegarder'
                background_color: 0.16, 0.65, 0.26, 1.0
                color: 1, 1, 1, 1
                size_hint_x: 0.3
                font_name: 'Arial'
                font_size: 12
                on_release: root.save_settings()
        
        # Contenu principal
        BoxLayout:
            orientation: 'horizontal'
            padding: 20
            spacing: 20
            
            # Zone principale des paramètres
            BoxLayout:
                orientation: 'vertical'
                canvas.before:
                    Color:
                        rgba: 1, 1, 1, 1
                    Rectangle:
                        size: self.size
                        pos: self.pos
                size_hint_x: 0.7
                padding: 20
                spacing: 15
                
                # Paramètres de reconnaissance
                Label:
                    text: '🎯 Paramètres de Reconnaissance'
                    font_name: 'Arial'
                    font_size: 16
                    bold: True
                    color: 0.0, 0.2, 0.4, 1
                    size_hint_y: None
                    height: 30
                
                BoxLayout:
                    orientation: 'horizontal'
                    size_hint_y: None
                    height: 50
                    spacing: 10
                    
                    Label:
                        text: 'Seuil de Similarité:'
                        font_name: 'Arial'
                        font_size: 12
                        color: 0.2, 0.2, 0.2, 1
                        size_hint_x: 0.4
                        
                    BoxLayout:
                        orientation: 'horizontal'
                        size_hint_x: 0.6
                        spacing: 10
                        
                        Slider:
                            id: threshold_slider
                            min: 0.1
                            max: 0.9
                            value: root.threshold
                            size_hint_x: 0.7
                            
                        Label:
                            text: str(round(root.threshold, 2))
                            font_name: 'Arial'
                            font_size: 12
                            color: 0.0, 0.5, 1.0, 1
                            size_hint_x: 0.3
                
                BoxLayout:
                    orientation: 'horizontal'
                    size_hint_y: None
                    height: 50
                    spacing: 10
                    
                    Label:
                        text: 'Seuil Anti-Spoofing:'
                        font_name: 'Arial'
                        font_size: 12
                        color: 0.2, 0.2, 0.2, 1
                        size_hint_x: 0.4
                        
                    BoxLayout:
                        orientation: 'horizontal'
                        size_hint_x: 0.6
                        spacing: 10
                        
                        Slider:
                            id: spoof_slider
                            min: 0.5
                            max: 0.99
                            value: root.spoof_threshold
                            size_hint_x: 0.7
                            
                        Label:
                            text: str(round(root.spoof_threshold, 2))
                            font_name: 'Arial'
                            font_size: 12
                            color: 0.0, 0.5, 1.0, 1
                            size_hint_x: 0.3
                
                # Paramètres de caméra
                Label:
                    text: '📸 Paramètres de Caméra'
                    font_name: 'Arial'
                    font_size: 16
                    bold: True
                    color: 0.0, 0.2, 0.4, 1
                    size_hint_y: None
                    height: 30
                
                BoxLayout:
                    orientation: 'horizontal'
                    size_hint_y: None
                    height: 50
                    spacing: 10
                    
                    Label:
                        text: 'Index de Caméra:'
                        font_name: 'Arial'
                        font_size: 12
                        color: 0.2, 0.2, 0.2, 1
                        size_hint_x: 0.4
                        
                    TextInput:
                        id: camera_index_input
                        text: str(root.camera_index)
                        font_name: 'Arial'
                        font_size: 12
                        size_hint_x: 0.2
                        multiline: False
                        
                    Label:
                        text: 'Résolution:'
                        font_name: 'Arial'
                        font_size: 12
                        color: 0.2, 0.2, 0.2, 1
                        size_hint_x: 0.15
                        
                    TextInput:
                        id: resolution_input
                        text: root.resolution
                        font_name: 'Arial'
                        font_size: 12
                        size_hint_x: 0.25
                        multiline: False
                
                # Paramètres de session
                Label:
                    text: '⏱️ Paramètres de Session'
                    font_name: 'Arial'
                    font_size: 16
                    bold: True
                    color: 0.0, 0.2, 0.4, 1
                    size_hint_y: None
                    height: 30
                
                BoxLayout:
                    orientation: 'horizontal'
                    size_hint_y: None
                    height: 50
                    spacing: 10
                    
                    Label:
                        text: 'Durée Session (min):'
                        font_name: 'Arial'
                        font_size: 12
                        color: 0.2, 0.2, 0.2, 1
                        size_hint_x: 0.4
                        
                    TextInput:
                        id: duration_input
                        text: str(root.session_duration)
                        font_name: 'Arial'
                        font_size: 12
                        size_hint_x: 0.2
                        multiline: False
                        
                    Label:
                        text: 'Cooldown (sec):'
                        font_name: 'Arial'
                        font_size: 12
                        color: 0.2, 0.2, 0.2, 1
                        size_hint_x: 0.2
                        
                    TextInput:
                        id: cooldown_input
                        text: str(root.cooldown)
                        font_name: 'Arial'
                        font_size: 12
                        size_hint_x: 0.2
                        multiline: False
                
                # Options avancées
                Label:
                    text: '🔧 Options Avancées'
                    font_name: 'Arial'
                    font_size: 16
                    bold: True
                    color: 0.0, 0.2, 0.4, 1
                    size_hint_y: None
                    height: 30
                
                BoxLayout:
                    orientation: 'horizontal'
                    size_hint_y: None
                    height: 50
                    spacing: 10
                    
                    Label:
                        text: 'Anti-Spoofing Actif:'
                        font_name: 'Arial'
                        font_size: 12
                        color: 0.2, 0.2, 0.2, 1
                        size_hint_x: 0.4
                        
                    Switch:
                        id: anti_spoof_switch
                        active: root.anti_spoof_enabled
                        size_hint_x: 0.1
                        
                    Label:
                        text: 'Debug Mode:'
                        font_name: 'Arial'
                        font_size: 12
                        color: 0.2, 0.2, 0.2, 1
                        size_hint_x: 0.3
                        
                    Switch:
                        id: debug_switch
                        active: root.debug_mode
                        size_hint_x: 0.1
                
                BoxLayout:
                    size_hint_y: 1
            
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
                    text: 'ℹ️ Informations'
                    font_name: 'Arial'
                    font_size: 16
                    bold: True
                    color: 0.0, 0.2, 0.4, 1
                    size_hint_y: None
                    height: 30
                
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
                            text: 'Version:'
                            font_name: 'Arial'
                            font_size: 11
                            color: 0.4, 0.4, 0.4, 1
                            size_hint_x: 0.5
                            
                        Label:
                            text: '1.0.0'
                            font_name: 'Arial'
                            font_size: 11
                            bold: True
                            color: 0.0, 0.5, 1.0, 1
                            size_hint_x: 0.5
                    
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
                            text: 'Kivy Version:'
                            font_name: 'Arial'
                            font_size: 11
                            color: 0.4, 0.4, 0.4, 1
                            size_hint_x: 0.5
                            
                        Label:
                            text: '2.x'
                            font_name: 'Arial'
                            font_size: 11
                            bold: True
                            color: 0.0, 0.5, 1.0, 1
                            size_hint_x: 0.5
                
                BoxLayout:
                    size_hint_y: 1
                
                Label:
                    text: '🎓 À propos'
                    font_name: 'Arial'
                    font_size: 14
                    bold: True
                    color: 0.0, 0.2, 0.4, 1
                    size_hint_y: None
                    height: 30
                
                Label:
                    text: "Système de Reconnaissance Faciale basé sur les réseaux de neurones convolutifs pour le pointage automatique des étudiants. Cas de l'UCC."
                    font_name: 'Arial'
                    font_size: 10
                    color: 0.4, 0.4, 0.4, 1
                    size_hint_y: None
                    height: 80
                    text_size: self.width, None
''')

class SettingsScreen(Screen):
    """Écran Paramètres"""
    
    threshold = NumericProperty(0.5)
    spoof_threshold = NumericProperty(0.85)
    camera_index = NumericProperty(0)
    resolution = StringProperty("1280x720")
    session_duration = NumericProperty(60)
    cooldown = NumericProperty(3.0)
    anti_spoof_enabled = BooleanProperty(True)
    debug_mode = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)
        self.settings_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'config', 'settings.json')
        self.load_settings()
    
    def on_enter(self):
        """Appelé lorsque l'écran est affiché"""
        self.load_settings()
    
    def save_settings(self):
        """Sauvegarde les paramètres dans un fichier JSON"""
        try:
            settings = {
                'threshold': self.threshold,
                'spoof_threshold': self.spoof_threshold,
                'camera_index': self.camera_index,
                'resolution': self.resolution,
                'session_duration': self.session_duration,
                'cooldown': self.cooldown,
                'anti_spoof_enabled': self.anti_spoof_enabled,
                'debug_mode': self.debug_mode
            }
            
            # Créer le dossier config s'il n'existe pas
            config_dir = os.path.dirname(self.settings_file)
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)
            
            # Sauvegarder les paramètres
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=4)
            
            print(f"✅ Paramètres sauvegardés dans {self.settings_file}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde des paramètres: {e}")
            return False
    
    def load_settings(self):
        """Charge les paramètres depuis un fichier JSON"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                
                # Appliquer les paramètres chargés
                self.threshold = settings.get('threshold', 0.5)
                self.spoof_threshold = settings.get('spoof_threshold', 0.85)
                self.camera_index = settings.get('camera_index', 0)
                self.resolution = settings.get('resolution', "1280x720")
                self.session_duration = settings.get('session_duration', 60)
                self.cooldown = settings.get('cooldown', 3.0)
                self.anti_spoof_enabled = settings.get('anti_spoof_enabled', True)
                self.debug_mode = settings.get('debug_mode', False)
                
                print(f"✅ Paramètres chargés depuis {self.settings_file}")
            else:
                print(f"ℹ️ Fichier de paramètres non trouvé, utilisation des valeurs par défaut")
                
        except Exception as e:
            print(f"❌ Erreur lors du chargement des paramètres: {e}")
            print(f"ℹ️ Utilisation des valeurs par défaut")
        # Cette fonction sera implémentée pour sauvegarder dans un fichier de configuration
