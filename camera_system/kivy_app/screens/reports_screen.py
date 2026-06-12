"""
Écran Rapports pour l'application Kivy
Export CSV et visualisation des rapports de présence avec chargement automatique
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.graphics import Color, Rectangle
from kivy.properties import StringProperty, NumericProperty, ListProperty, BooleanProperty
from kivy.lang import Builder
from kivy.clock import Clock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.report_watcher_service import ReportWatcherService
from services.report_analytics_service import ReportAnalyticsService

Builder.load_string('''
<ReportsScreen>:
    name: 'reports'
    
    BoxLayout:
        orientation: 'vertical'
        canvas.before:
            Color:
                rgba: 0.97, 0.97, 0.99, 1.0  # Fond très léger
            Rectangle:
                size: self.size
                pos: self.pos
        
        # Header
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: 70
            padding: 25
            spacing: 15
            canvas.before:
                Color:
                    rgba: 0.12, 0.23, 0.37, 1.0  # UCC_BLUE_DARK
                Rectangle:
                    size: self.size
                    pos: self.pos
                # Bordure inférieure
                Color:
                    rgba: 0.29, 0.45, 0.69, 0.5
                Rectangle:
                    size: self.width, 2
                    pos: self.x, self.y
            
            Label:
                text: '📊 Rapports - UCC'
                font_name: 'Arial'
                font_size: 22
                bold: True
                color: 1, 1, 1, 1
                size_hint_x: 0.5
                
            # Indicateur de surveillance
            BoxLayout:
                orientation: 'horizontal'
                size_hint_x: 0.3
                spacing: 10
                padding: 10
                canvas.before:
                    Color:
                        rgba: 0.18, 0.35, 0.56, 0.5
                    Rectangle:
                        size: self.size
                        pos: self.pos
                    Color:
                        rgba: 0.29, 0.45, 0.69, 0.3
                    Line:
                        rectangle: self.x, self.y, self.width, self.height
                
                Label:
                    text: '📁'
                    font_size: 18
                    size_hint_x: None
                    width: 25
                    
                Label:
                    text: 'Surveillance: ' + ('✅ Actif' if root.watcher_active else '⚠️ Inactif')
                    font_name: 'Arial'
                    font_size: 12
                    color: 0.9, 0.95, 1, 1
            
            Button:
                text: '📤 Exporter CSV'
                background_color: 0.43, 0.26, 0.76, 1.0  # ACCENT_PURPLE
                color: 1, 1, 1, 1
                size_hint_x: 0.2
                font_name: 'Arial'
                font_size: 12
        
        # Filtres
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: 50
            padding: 20
            spacing: 10
            
            Label:
                text: '📅 Période:'
                font_size: 14
                size_hint_x: None
                width: 80
                
            Button:
                text: "Aujourd'hui"
                background_color: 0.29, 0.56, 0.89, 1.0  # ACCENT_BLUE
                color: 1, 1, 1, 1
                size_hint_x: 0.2
                font_name: 'Arial'
                font_size: 12
                
            Button:
                text: 'Cette Semaine'
                background_color: 0.42, 0.46, 0.49, 1.0  # BUTTON_SECONDARY
                color: 1, 1, 1, 1
                size_hint_x: 0.2
                font_name: 'Arial'
                font_size: 12
                
            Button:
                text: 'Ce Mois'
                background_color: 0.42, 0.46, 0.49, 1.0  # BUTTON_SECONDARY
                color: 1, 1, 1, 1
                size_hint_x: 0.2
                font_name: 'Arial'
                font_size: 12
                
            Button:
                text: 'Tout'
                background_color: 0.42, 0.46, 0.49, 1.0  # BUTTON_SECONDARY
                color: 1, 1, 1, 1
                size_hint_x: 0.2
                font_name: 'Arial'
                font_size: 12
        
        # Contenu principal
        BoxLayout:
            orientation: 'horizontal'
            padding: 20
            spacing: 20
            
            # Liste des rapports
            BoxLayout:
                orientation: 'vertical'
                canvas.before:
                    Color:
                        rgba: 1, 1, 1, 1
                    Rectangle:
                        size: self.size
                        pos: self.pos
                    # Ombre subtile
                    Color:
                        rgba: 0, 0, 0, 0.05
                    Rectangle:
                        size: self.size
                        pos: self.pos[0] + 2, self.pos[1] - 2
                size_hint_x: 0.6
                padding: 20
                spacing: 15
                
                Label:
                    text: '📋 Rapports de Présence'
                    font_name: 'Arial'
                    font_size: 18
                    bold: True
                    color: 0.12, 0.23, 0.37, 1  # UCC_BLUE_DARK
                    size_hint_y: None
                    height: 30
                
                # Info dossier surveillé
                BoxLayout:
                    orientation: 'horizontal'
                    size_hint_y: None
                    height: 35
                    canvas.before:
                        Color:
                            rgba: 0.91, 0.96, 1, 1  # Fond bleu très clair
                        Rectangle:
                            size: self.size
                            pos: self.pos
                    padding: 10
                    spacing: 8
                    
                    Label:
                        text: '📁'
                        font_size: 16
                        size_hint_x: None
                        width: 25
                        
                    Label:
                        text: 'Dossier: reports/ (surveillance auto)'
                        font_name: 'Arial'
                        font_size: 11
                        color: 0.42, 0.46, 0.49, 1  # TEXT_SECONDARY
                
                # Liste des rapports
                ScrollView:
                    BoxLayout:
                        orientation: 'vertical'
                        spacing: 8
                        size_hint_y: None
                        height: self.minimum_height
                        id: reports_list
                        
                        # Rapport 1
                        BoxLayout:
                            orientation: 'horizontal'
                            size_hint_y: None
                            height: 50
                            canvas.before:
                                Color:
                                    rgba: 0.97, 0.97, 0.97, 1
                                Rectangle:
                                    size: self.size
                                    pos: self.pos
                            padding: 10
                            spacing: 5
                            
                            Label:
                                text: '📄'
                                font_size: 20
                                size_hint_x: None
                                width: 40
                                
                            Label:
                                text: 'attendance_UCC_20260612_211646.csv'
                                font_name: 'Arial'
                                font_size: 12
                                color: 0.2, 0.2, 0.2, 1
                                size_hint_x: 0.6
                                
                            Label:
                                text: '12/06/2026 21:16'
                                font_name: 'Arial'
                                font_size: 11
                                color: 0.4, 0.4, 0.4, 1
                                size_hint_x: 0.2
                                
                            Button:
                                text: '👁️'
                                font_size: 14
                                background_color: 0.0, 0.5, 1.0, 1.0
                                color: 1, 1, 1, 1
                                size_hint_x: None
                                width: 40
                        
                        # Rapport 2
                        BoxLayout:
                            orientation: 'horizontal'
                            size_hint_y: None
                            height: 50
                            canvas.before:
                                Color:
                                    rgba: 1, 1, 1, 1
                                Rectangle:
                                    size: self.size
                                    pos: self.pos
                            padding: 10
                            spacing: 5
                            
                            Label:
                                text: '📄'
                                font_size: 20
                                size_hint_x: None
                                width: 40
                                
                            Label:
                                text: 'attendance_camera_20260612_211143.csv'
                                font_name: 'Arial'
                                font_size: 12
                                color: 0.2, 0.2, 0.2, 1
                                size_hint_x: 0.6
                                
                            Label:
                                text: '12/06/2026 21:11'
                                font_name: 'Arial'
                                font_size: 11
                                color: 0.4, 0.4, 0.4, 1
                                size_hint_x: 0.2
                                
                            Button:
                                text: '👁️'
                                font_size: 14
                                background_color: 0.0, 0.5, 1.0, 1.0
                                color: 1, 1, 1, 1
                                size_hint_x: None
                                width: 40
            
            # Sidebar statistiques
            BoxLayout:
                orientation: 'vertical'
                canvas.before:
                    Color:
                        rgba: 1, 1, 1, 1
                    Rectangle:
                        size: self.size
                        pos: self.pos
                    # Ombre subtile
                    Color:
                        rgba: 0, 0, 0, 0.05
                    Rectangle:
                        size: self.size
                        pos: self.pos[0] + 2, self.pos[1] - 2
                size_hint_x: 0.4
                padding: 20
                spacing: 15
                
                Label:
                    text: '📈 Statistiques Globales'
                    font_name: 'Arial'
                    font_size: 18
                    bold: True
                    color: 0.12, 0.23, 0.37, 1  # UCC_BLUE_DARK
                    size_hint_y: None
                    height: 30
                
                BoxLayout:
                    orientation: 'vertical'
                    spacing: 10
                    
                    # Statistique 1
                    BoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: 40
                        canvas.before:
                            Color:
                                rgba: 1, 1, 1, 1
                            Rectangle:
                                size: self.size
                                pos: self.pos
                            # Bordure gauche colorée
                            Color:
                                rgba: 0.29, 0.56, 0.89, 1.0  # ACCENT_BLUE
                            Rectangle:
                                size: 4, self.height
                                pos: self.x, self.y
                        padding: 12
                        spacing: 10
                        
                        Label:
                            text: '📄'
                            font_size: 18
                            size_hint_x: None
                            width: 30
                            
                        BoxLayout:
                            orientation: 'vertical'
                            spacing: 2
                            
                            Label:
                                text: 'Total Rapports'
                                font_name: 'Arial'
                                font_size: 11
                                color: 0.42, 0.46, 0.49, 1  # TEXT_SECONDARY
                                size_hint_y: None
                                height: 18
                                
                            Label:
                                text: str(root.total_reports)
                                font_name: 'Arial'
                                font_size: 20
                                bold: True
                                color: 0.29, 0.56, 0.89, 1  # ACCENT_BLUE
                                size_hint_y: None
                                height: 20
                    
                    # Statistique 2
                    BoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: 40
                        canvas.before:
                            Color:
                                rgba: 1, 1, 1, 1
                            Rectangle:
                                size: self.size
                                pos: self.pos
                            Color:
                                rgba: 0.16, 0.65, 0.26, 1.0  # ACCENT_GREEN
                            Rectangle:
                                size: 4, self.height
                                pos: self.x, self.y
                        padding: 12
                        spacing: 10
                        
                        Label:
                            text: '👥'
                            font_size: 18
                            size_hint_x: None
                            width: 30
                            
                        BoxLayout:
                            orientation: 'vertical'
                            spacing: 2
                            
                            Label:
                                text: 'Total Lignes'
                                font_name: 'Arial'
                                font_size: 11
                                color: 0.42, 0.46, 0.49, 1  # TEXT_SECONDARY
                                size_hint_y: None
                                height: 18
                                
                            Label:
                                text: str(root.total_rows)
                                font_name: 'Arial'
                                font_size: 20
                                bold: True
                                color: 0.16, 0.65, 0.26, 1  # ACCENT_GREEN
                                size_hint_y: None
                                height: 20
                    
                    # Statistique 3
                    BoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: 40
                        canvas.before:
                            Color:
                                rgba: 1, 1, 1, 1
                            Rectangle:
                                size: self.size
                                pos: self.pos
                            Color:
                                rgba: 0.09, 0.64, 0.72, 1.0  # ACCENT_CYAN
                            Rectangle:
                                size: 4, self.height
                                pos: self.x, self.y
                        padding: 12
                        spacing: 10
                        
                        Label:
                            text: '📊'
                            font_size: 18
                            size_hint_x: None
                            width: 30
                            
                        BoxLayout:
                            orientation: 'vertical'
                            spacing: 2
                            
                            Label:
                                text: 'Types Fichiers'
                                font_name: 'Arial'
                                font_size: 11
                                color: 0.42, 0.46, 0.49, 1  # TEXT_SECONDARY
                                size_hint_y: None
                                height: 18
                                
                            Label:
                                text: str(root.file_types_count)
                                font_name: 'Arial'
                                font_size: 20
                                bold: True
                                color: 0.09, 0.64, 0.72, 1  # ACCENT_CYAN
                                size_hint_y: None
                                height: 20
                
                BoxLayout:
                    size_hint_y: 1
                
                Label:
                    text: '📊 Graphiques'
                    font_name: 'Arial'
                    font_size: 16
                    bold: True
                    color: 0.12, 0.23, 0.37, 1  # UCC_BLUE_DARK
                    size_hint_y: None
                    height: 30
                
                # Zone de graphiques
                BoxLayout:
                    orientation: 'vertical'
                    canvas.before:
                        Color:
                            rgba: 0.95, 0.97, 0.99, 1  # Fond très léger
                        Rectangle:
                            size: self.size
                            pos: self.pos
                    size_hint_y: None
                    height: 250
                    padding: 20
                    spacing: 10
                    
                    Label:
                        text: '📈 Graphique de Présence'
                        font_name: 'Arial'
                        font_size: 13
                        bold: True
                        color: 0.12, 0.23, 0.37, 1
                        size_hint_y: None
                        height: 25
                    
                    Label:
                        text: 'Les graphiques seront générés automatiquement à partir des fichiers de rapports'
                        font_name: 'Arial'
                        font_size: 11
                        color: 0.42, 0.46, 0.49, 1  # TEXT_SECONDARY
                        halign: 'center'
                        size_hint_y: None
                        height: 40
''')

class ReportsScreen(Screen):
    """Écran Rapports avec chargement automatique et graphiques"""
    
    watcher_active = BooleanProperty(False)
    total_reports = NumericProperty(0)
    total_rows = NumericProperty(0)
    file_types_count = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super(ReportsScreen, self).__init__(**kwargs)
        
        # Initialiser les services
        self.report_watcher = ReportWatcherService(watch_folder="reports")
        self.report_analytics = ReportAnalyticsService()
        
        # Configurer le callback pour les nouveaux fichiers
        self.report_watcher.add_callback(self.on_new_report)
        
        # Charger les fichiers existants
        Clock.schedule_once(self.load_existing_reports, 0.5)
    
    def on_enter(self):
        """Appelé lorsque l'écran est affiché"""
        # Démarrer la surveillance du dossier
        self.report_watcher.start_watching()
        self.watcher_active = True
        print("📁 Surveillance des rapports démarrée")
    
    def on_leave(self):
        """Appelé lorsque l'écran est quitté"""
        # Arrêter la surveillance du dossier
        self.report_watcher.stop_watching()
        self.watcher_active = False
        print("📁 Surveillance des rapports arrêtée")
    
    def load_existing_reports(self, dt):
        """Charge les rapports existants dans le dossier"""
        self.report_watcher.load_existing_files()
        self.update_statistics()
    
    def on_new_report(self, file_path: str, parsed_data: dict):
        """Callback appelé quand un nouveau rapport est détecté"""
        print(f"📄 Nouveau rapport chargé: {file_path}")
        
        # Ajouter les données au service d'analyse
        self.report_analytics.add_report_data(file_path, parsed_data)
        
        # Mettre à jour les statistiques
        self.update_statistics()
        
        # Mettre à jour l'interface (à implémenter)
        self.refresh_report_list()
    
    def update_statistics(self):
        """Met à jour les statistiques affichées"""
        summary = self.report_analytics.get_summary_report()
        
        self.total_reports = summary.get('total_reports', 0)
        self.total_rows = summary.get('total_rows', 0)
        self.file_types_count = len(summary.get('report_types', {}))
    
    def refresh_report_list(self):
        """Rafraîchit la liste des rapports affichée"""
        # À implémenter: mettre à jour la liste des rapports dans l'interface
        pass
