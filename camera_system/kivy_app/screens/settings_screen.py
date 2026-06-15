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
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
from kivy.properties import NumericProperty, BooleanProperty, StringProperty
from kivy.lang import Builder
from kivy.uix.popup import Popup
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from services.mysql_service import MySQLService

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
                size_hint_x: 0.15
                font_name: 'Arial'
                font_size: 12
                on_release: root.save_settings()
                
            Button:
                text: '❌ Annuler'
                background_color: 0.86, 0.21, 0.27, 1.0
                color: 1, 1, 1, 1
                size_hint_x: 0.15
                font_name: 'Arial'
                font_size: 12
                on_release: root.cancel_changes()
        
        # Contenu principal
        BoxLayout:
            orientation: 'horizontal'
            padding: 20
            spacing: 20
            
            # Zone principale des paramètres avec ScrollView
            ScrollView:
                size_hint_x: 0.7
                do_scroll_x: False
                do_scroll_y: True
                
                BoxLayout:
                    orientation: 'vertical'
                    size_hint_y: None
                    height: self.minimum_height
                    canvas.before:
                        Color:
                            rgba: 1, 1, 1, 1
                        Rectangle:
                            size: self.size
                            pos: self.pos
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
                                on_value: root.mark_unsaved_changes()
                                
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
                                on_value: root.mark_unsaved_changes()
                                
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
                            on_text: root.mark_unsaved_changes()
                            
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
                            on_text: root.mark_unsaved_changes()
                    
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
                            on_text: root.mark_unsaved_changes()
                            
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
                            on_text: root.mark_unsaved_changes()
                    
                    # Règles de présence
                    Label:
                        text: '📋 Règles de Présence'
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
                            text: 'Heure Limite Retard:'
                            font_name: 'Arial'
                            font_size: 12
                            color: 0.2, 0.2, 0.2, 1
                            size_hint_x: 0.4
                            
                        TextInput:
                            id: late_time_input
                            text: root.late_time_limit
                            font_name: 'Arial'
                            font_size: 12
                            size_hint_x: 0.2
                            multiline: False
                            on_text: root.mark_unsaved_changes()
                            
                        Label:
                            text: '(ex: 08:00)'
                            font_name: 'Arial'
                            font_size: 11
                            color: 0.4, 0.4, 0.4, 1
                            size_hint_x: 0.4
                    
                    BoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: 50
                        spacing: 10
                        
                        Label:
                            text: 'Détection Auto Retard:'
                            font_name: 'Arial'
                            font_size: 12
                            color: 0.2, 0.2, 0.2, 1
                            size_hint_x: 0.4
                            
                        Switch:
                            id: auto_late_switch
                            active: root.enable_auto_late_detection
                            size_hint_x: 0.1
                            on_active: root.mark_unsaved_changes()
                            
                        Label:
                            text: 'Anti-Doublon Journalier:'
                            font_name: 'Arial'
                            font_size: 12
                            color: 0.2, 0.2, 0.2, 1
                            size_hint_x: 0.3
                            
                        Switch:
                            id: duplicate_check_switch
                            active: root.enable_daily_duplicate_check
                            size_hint_x: 0.1
                            on_active: root.mark_unsaved_changes()
                    
                    BoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: 50
                        spacing: 10
                        
                        Label:
                            text: 'Calcul Auto Absences:'
                            font_name: 'Arial'
                            font_size: 12
                            color: 0.2, 0.2, 0.2, 1
                            size_hint_x: 0.4
                            
                        Switch:
                            id: absence_calc_switch
                            active: root.enable_auto_absence_calculation
                            size_hint_x: 0.1
                            on_active: root.mark_unsaved_changes()
                    
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
                            on_active: root.mark_unsaved_changes()
                            
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
                            on_active: root.mark_unsaved_changes()
                    
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
    
    # Règles de présence
    late_time_limit = StringProperty("08:00")
    enable_auto_late_detection = BooleanProperty(True)
    enable_daily_duplicate_check = BooleanProperty(True)
    enable_auto_absence_calculation = BooleanProperty(True)
    
    # Suivi des modifications
    has_unsaved_changes = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)
        self.settings_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'config', 'settings.json')
        self.mysql_service = MySQLService(
            host='localhost',
            database='ucc_face_recognition',
            user='root',
            password='admin123',
            port=3306
        )
        self.load_settings()
    
    def on_enter(self):
        """Appelé lorsque l'écran est affiché"""
        self.load_settings()
        self.has_unsaved_changes = False
    
    def on_pre_leave(self):
        """Appelé avant de quitter l'écran - vérifie les modifications non sauvegardées"""
        if self.has_unsaved_changes:
            # Empêcher la sortie si des modifications non sauvegardées
            return True
        return False
    
    def mark_unsaved_changes(self, *args):
        """Marque qu'il y a des modifications non sauvegardées"""
        self.has_unsaved_changes = True
    
    def save_settings(self):
        """Sauvegarde les paramètres dans MySQL"""
        try:
            # Récupérer les valeurs depuis les widgets
            threshold = self.ids.threshold_slider.value if hasattr(self.ids, 'threshold_slider') else self.threshold
            spoof_threshold = self.ids.spoof_slider.value if hasattr(self.ids, 'spoof_slider') else self.spoof_threshold
            
            try:
                camera_index = int(self.ids.camera_index_input.text) if hasattr(self.ids, 'camera_index_input') else self.camera_index
            except ValueError:
                camera_index = self.camera_index
                
            resolution = self.ids.resolution_input.text if hasattr(self.ids, 'resolution_input') else self.resolution
            
            try:
                session_duration = int(self.ids.duration_input.text) if hasattr(self.ids, 'duration_input') else self.session_duration
            except ValueError:
                session_duration = self.session_duration
                
            try:
                cooldown = float(self.ids.cooldown_input.text) if hasattr(self.ids, 'cooldown_input') else self.cooldown
            except ValueError:
                cooldown = self.cooldown
                
            anti_spoof_enabled = self.ids.anti_spoof_switch.active if hasattr(self.ids, 'anti_spoof_switch') else self.anti_spoof_enabled
            debug_mode = self.ids.debug_switch.active if hasattr(self.ids, 'debug_switch') else self.debug_mode
            
            late_time_input = self.ids.late_time_input.text if hasattr(self.ids, 'late_time_input') else self.late_time_limit
            auto_late_switch = self.ids.auto_late_switch.active if hasattr(self.ids, 'auto_late_switch') else self.enable_auto_late_detection
            duplicate_check_switch = self.ids.duplicate_check_switch.active if hasattr(self.ids, 'duplicate_check_switch') else self.enable_daily_duplicate_check
            absence_calc_switch = self.ids.absence_calc_switch.active if hasattr(self.ids, 'absence_calc_switch') else self.enable_auto_absence_calculation
            
            # Sauvegarder chaque paramètre individuellement dans MySQL
            self.mysql_service.save_setting('threshold', threshold, 'Seuil de reconnaissance faciale')
            self.mysql_service.save_setting('spoof_threshold', spoof_threshold, 'Seuil de détection de fraude')
            self.mysql_service.save_setting('camera_index', camera_index, 'Index de la caméra')
            self.mysql_service.save_setting('resolution', resolution, 'Résolution de la caméra')
            self.mysql_service.save_setting('session_duration', session_duration, 'Durée de la session (secondes)')
            self.mysql_service.save_setting('cooldown', cooldown, 'Temps de refroidissement entre détections')
            self.mysql_service.save_setting('anti_spoof_enabled', int(anti_spoof_enabled), 'Activation de l\'anti-spoofing')
            self.mysql_service.save_setting('debug_mode', int(debug_mode), 'Mode debug')
            
            # Sauvegarder les règles de présence
            attendance_rules = {
                'late_time_limit': late_time_input,
                'enable_auto_late_detection': auto_late_switch,
                'enable_daily_duplicate_check': duplicate_check_switch,
                'enable_auto_absence_calculation': absence_calc_switch
            }
            self.mysql_service.save_setting('attendance_rules', attendance_rules, 'Règles de présence')
            
            # Mettre à jour les propriétés locales
            self.threshold = threshold
            self.spoof_threshold = spoof_threshold
            self.camera_index = camera_index
            self.resolution = resolution
            self.session_duration = session_duration
            self.cooldown = cooldown
            self.anti_spoof_enabled = anti_spoof_enabled
            self.debug_mode = debug_mode
            self.late_time_limit = late_time_input
            self.enable_auto_late_detection = auto_late_switch
            self.enable_daily_duplicate_check = duplicate_check_switch
            self.enable_auto_absence_calculation = absence_calc_switch
            
            self.has_unsaved_changes = False
            
            print("✅ Paramètres sauvegardés dans MySQL")
            
            # Afficher le popup de confirmation de redémarrage
            self.show_restart_popup()
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde des paramètres dans MySQL: {e}")
            return False
    
    def cancel_changes(self):
        """Annule les modifications et recharge les paramètres"""
        self.load_settings()
        self.has_unsaved_changes = False
        print("❌ Modifications annulées, paramètres rechargés")
    
    def show_restart_popup(self):
        """Affiche un popup informant du redémarrage nécessaire"""
        content = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        message = Label(
            text='✅ Paramètres sauvegardés avec succès!\n\n⚠️ Redémarrage automatique de l\'application\npour que les modifications prennent effet...',
            font_name='Arial',
            font_size=14,
            color=(0.2, 0.2, 0.2, 1),
            halign='center',
            text_size=(400, None)
        )
        
        content.add_widget(message)
        
        popup = Popup(
            title='Sauvegarde Réussie',
            content=content,
            size_hint=(0.5, 0.3),
            auto_dismiss=True
        )
        
        popup.bind(on_dismiss=self.restart_application)
        popup.open()
    
    def restart_application(self, instance):
        """Redémarre l'application"""
        print("🔄 Redémarrage de l'application...")
        # Redémarrer l'application
        os.execv(sys.executable, [sys.executable] + sys.argv)
    
    def load_settings(self):
        """Charge les paramètres depuis MySQL"""
        try:
            # Charger depuis MySQL
            self.threshold = self.mysql_service.get_setting('threshold', 0.5)
            self.spoof_threshold = self.mysql_service.get_setting('spoof_threshold', 0.85)
            self.camera_index = self.mysql_service.get_setting('camera_index', 0)
            self.resolution = self.mysql_service.get_setting('resolution', "1280x720")
            self.session_duration = self.mysql_service.get_setting('session_duration', 60)
            self.cooldown = self.mysql_service.get_setting('cooldown', 3.0)
            self.anti_spoof_enabled = self.mysql_service.get_setting('anti_spoof_enabled', True)
            self.debug_mode = self.mysql_service.get_setting('debug_mode', False)
            
            # Charger les règles de présence
            attendance_rules = self.mysql_service.get_setting('attendance_rules', {})
            self.late_time_limit = attendance_rules.get('late_time_limit', "08:00")
            self.enable_auto_late_detection = attendance_rules.get('enable_auto_late_detection', True)
            self.enable_daily_duplicate_check = attendance_rules.get('enable_daily_duplicate_check', True)
            self.enable_auto_absence_calculation = attendance_rules.get('enable_auto_absence_calculation', True)
            
            # Mettre à jour les widgets si disponibles
            if hasattr(self.ids, 'threshold_slider'):
                self.ids.threshold_slider.value = self.threshold
            if hasattr(self.ids, 'spoof_slider'):
                self.ids.spoof_slider.value = self.spoof_threshold
            if hasattr(self.ids, 'duration_input'):
                self.ids.duration_input.text = str(self.session_duration)
            if hasattr(self.ids, 'late_time_input'):
                self.ids.late_time_input.text = self.late_time_limit
            if hasattr(self.ids, 'auto_late_switch'):
                self.ids.auto_late_switch.active = self.enable_auto_late_detection
            if hasattr(self.ids, 'duplicate_check_switch'):
                self.ids.duplicate_check_switch.active = self.enable_daily_duplicate_check
            if hasattr(self.ids, 'absence_calc_switch'):
                self.ids.absence_calc_switch.active = self.enable_auto_absence_calculation
            
            print(f"✅ Paramètres chargés depuis MySQL: threshold={self.threshold}, anti_spoof={self.anti_spoof_enabled}")
            
        except Exception as e:
            print(f"❌ Erreur lors du chargement des paramètres depuis MySQL: {e}")
            print("⚠️ Utilisation des valeurs par défaut")
