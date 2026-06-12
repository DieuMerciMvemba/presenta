"""
Écran Dashboard pour l'application Kivy
Tableau de bord avec statistiques et graphiques
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.properties import NumericProperty, StringProperty
from kivy.lang import Builder
from kivy.clock import Clock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from services.database_service import DatabaseService

Builder.load_string('''
<DashboardScreen>:
    name: 'dashboard'
    
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
                text: '🎓 Tableau de Bord - UCC'
                font_name: 'Arial'
                font_size: 22
                bold: True
                color: 1, 1, 1, 1
                size_hint_x: 0.7
                
            BoxLayout:
                orientation: 'horizontal'
                size_hint_x: 0.3
                spacing: 15
                
                Label:
                    text: '📅 ' + root.current_date
                    font_name: 'Arial'
                    font_size: 14
                    color: 0.9, 0.95, 1, 1
                    size_hint_x: 0.5
        
        # Contenu principal
        BoxLayout:
            orientation: 'horizontal'
            padding: 20
            spacing: 20
            
            # Zone principale
            BoxLayout:
                orientation: 'vertical'
                spacing: 20
                size_hint_x: 0.75
                
                # Cartes de statistiques
                GridLayout:
                    cols: 4
                    spacing: 20
                    size_hint_y: None
                    height: 160
                    
                    # Carte 1: Total Étudiants
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
                                rgba: 0, 0, 0, 0.08
                            Rectangle:
                                size: self.size
                                pos: self.pos[0] + 3, self.pos[1] - 3
                            # Bordure supérieure colorée
                            Color:
                                rgba: 0.29, 0.56, 0.89, 1.0  # ACCENT_BLUE
                            Rectangle:
                                size: self.width, 4
                                pos: self.x, self.top - 4
                        padding: 20
                        spacing: 8
                        
                        Label:
                            text: '👥'
                            font_size: 36
                            size_hint_y: None
                            height: 45
                            halign: 'center'
                            
                        Label:
                            text: str(root.total_students)
                            font_name: 'Arial'
                            font_size: 32
                            bold: True
                            color: 0.12, 0.23, 0.37, 1  # UCC_BLUE_DARK
                            size_hint_y: None
                            height: 40
                            halign: 'center'
                            
                        Label:
                            text: 'Total Étudiants'
                            font_name: 'Arial'
                            font_size: 12
                            color: 0.42, 0.46, 0.49, 1  # TEXT_SECONDARY
                            size_hint_y: None
                            height: 25
                            halign: 'center'
                    
                    # Carte 2: Présents Aujourd'hui
                    BoxLayout:
                        orientation: 'vertical'
                        canvas.before:
                            Color:
                                rgba: 1, 1, 1, 1
                            Rectangle:
                                size: self.size
                                pos: self.pos
                            Color:
                                rgba: 0, 0, 0, 0.08
                            Rectangle:
                                size: self.size
                                pos: self.pos[0] + 3, self.pos[1] - 3
                            Color:
                                rgba: 0.16, 0.65, 0.26, 1.0  # ACCENT_GREEN
                            Rectangle:
                                size: self.width, 4
                                pos: self.x, self.top - 4
                        padding: 20
                        spacing: 8
                        
                        Label:
                            text: '✅'
                            font_size: 36
                            size_hint_y: None
                            height: 45
                            halign: 'center'
                            
                        Label:
                            text: str(root.present_today)
                            font_name: 'Arial'
                            font_size: 32
                            bold: True
                            color: 0.16, 0.65, 0.26, 1  # ACCENT_GREEN
                            size_hint_y: None
                            height: 40
                            halign: 'center'
                            
                        Label:
                            text: "Présents Aujourd'hui"
                            font_name: 'Arial'
                            font_size: 12
                            color: 0.42, 0.46, 0.49, 1  # TEXT_SECONDARY
                            size_hint_y: None
                            height: 25
                            halign: 'center'
                    
                    # Carte 3: Absents Aujourd'hui
                    BoxLayout:
                        orientation: 'vertical'
                        canvas.before:
                            Color:
                                rgba: 1, 1, 1, 1
                            Rectangle:
                                size: self.size
                                pos: self.pos
                            Color:
                                rgba: 0, 0, 0, 0.08
                            Rectangle:
                                size: self.size
                                pos: self.pos[0] + 3, self.pos[1] - 3
                            Color:
                                rgba: 0.86, 0.21, 0.27, 1.0  # ACCENT_RED
                            Rectangle:
                                size: self.width, 4
                                pos: self.x, self.top - 4
                        padding: 20
                        spacing: 8
                        
                        Label:
                            text: '❌'
                            font_size: 36
                            size_hint_y: None
                            height: 45
                            halign: 'center'
                            
                        Label:
                            text: str(root.absent_today)
                            font_name: 'Arial'
                            font_size: 32
                            bold: True
                            color: 0.86, 0.21, 0.27, 1  # ACCENT_RED
                            size_hint_y: None
                            height: 40
                            halign: 'center'
                            
                        Label:
                            text: "Absents Aujourd'hui"
                            font_name: 'Arial'
                            font_size: 12
                            color: 0.42, 0.46, 0.49, 1  # TEXT_SECONDARY
                            size_hint_y: None
                            height: 25
                            halign: 'center'
                    
                    # Carte 4: Taux de Présence
                    BoxLayout:
                        orientation: 'vertical'
                        canvas.before:
                            Color:
                                rgba: 1, 1, 1, 1
                            Rectangle:
                                size: self.size
                                pos: self.pos
                            Color:
                                rgba: 0, 0, 0, 0.08
                            Rectangle:
                                size: self.size
                                pos: self.pos[0] + 3, self.pos[1] - 3
                            Color:
                                rgba: 0.09, 0.64, 0.72, 1.0  # ACCENT_CYAN
                            Rectangle:
                                size: self.width, 4
                                pos: self.x, self.top - 4
                        padding: 20
                        spacing: 8
                        
                        Label:
                            text: '📊'
                            font_size: 36
                            size_hint_y: None
                            height: 45
                            halign: 'center'
                            
                        Label:
                            text: str(root.attendance_rate) + '%'
                            font_name: 'Arial'
                            font_size: 32
                            bold: True
                            color: 0.09, 0.64, 0.72, 1  # ACCENT_CYAN
                            size_hint_y: None
                            height: 40
                            halign: 'center'
                            
                        Label:
                            text: 'Taux de Présence'
                            font_name: 'Arial'
                            font_size: 12
                            color: 0.42, 0.46, 0.49, 1  # TEXT_SECONDARY
                            size_hint_y: None
                            height: 25
                            halign: 'center'
                
                # Zone de contenu supplémentaire
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
                    padding: 25
                    spacing: 15
                    
                    Label:
                        text: '📈 Statistiques de Présence'
                        font_name: 'Arial'
                        font_size: 18
                        bold: True
                        color: 0.12, 0.23, 0.37, 1  # UCC_BLUE_DARK
                        size_hint_y: None
                        height: 30
                    
                    Label:
                        text: 'Les graphiques de présence seront affichés ici.'
                        font_name: 'Arial'
                        font_size: 13
                        color: 0.42, 0.46, 0.49, 1  # TEXT_SECONDARY
                        size_hint_y: 1
            
            # Sidebar
            BoxLayout:
                orientation: 'vertical'
                size_hint_x: 0.25
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
                padding: 20
                spacing: 15
                
                Label:
                    text: '⚡ Actions Rapides'
                    font_name: 'Arial'
                    font_size: 16
                    bold: True
                    color: 0.12, 0.23, 0.37, 1  # UCC_BLUE_DARK
                    size_hint_y: None
                    height: 30
                
                BoxLayout:
                    orientation: 'vertical'
                    spacing: 10
                    
                    Button:
                        text: '👥 Ajouter Étudiant'
                        background_color: 0.29, 0.56, 0.89, 1.0  # ACCENT_BLUE
                        color: 1, 1, 1, 1
                        size_hint_y: None
                        height: 45
                        font_name: 'Arial'
                        font_size: 12
                        
                    Button:
                        text: '📸 Démarrer Pointage'
                        background_color: 0.16, 0.65, 0.26, 1.0  # ACCENT_GREEN
                        color: 1, 1, 1, 1
                        size_hint_y: None
                        height: 45
                        font_name: 'Arial'
                        font_size: 12
                        
                    Button:
                        text: '📊 Générer Rapport'
                        background_color: 0.43, 0.26, 0.76, 1.0  # ACCENT_PURPLE
                        color: 1, 1, 1, 1
                        size_hint_y: None
                        height: 45
                        font_name: 'Arial'
                        font_size: 12
                
                BoxLayout:
                    size_hint_y: 1
                
                Label:
                    text: '📋 Derniers Pointages'
                    font_name: 'Arial'
                    font_size: 16
                    bold: True
                    color: 0.12, 0.23, 0.37, 1  # UCC_BLUE_DARK
                    size_hint_y: None
                    height: 30
                
                Label:
                    text: 'Aucun pointage récent'
                    font_name: 'Arial'
                    font_size: 13
                    color: 0.42, 0.46, 0.49, 1  # TEXT_SECONDARY
                    size_hint_y: None
                    height: 25
''')

class DashboardScreen(Screen):
    """Écran Dashboard avec statistiques"""
    
    total_students = NumericProperty(0)
    present_today = NumericProperty(0)
    absent_today = NumericProperty(0)
    attendance_rate = NumericProperty(0.0)
    current_date = StringProperty("")
    
    def __init__(self, **kwargs):
        super(DashboardScreen, self).__init__(**kwargs)
        self.db_service = DatabaseService()
        self.update_datetime()
        self.update_statistics()
    
    def on_enter(self):
        """Appelé lorsque l'écran est affiché"""
        self.update_statistics()
    
    def update_datetime(self):
        """Met à jour la date actuelle"""
        from datetime import datetime
        self.current_date = datetime.now().strftime("%d/%m/%Y")
    
    def update_statistics(self):
        """Met à jour les statistiques du dashboard"""
        try:
            stats = self.db_service.get_statistics()
            self.total_students = stats['total_students']
            self.present_today = 0  # Pour l'instant, valeur par défaut
            self.absent_today = self.total_students
            self.attendance_rate = 0.0
        except Exception as e:
            print(f"Erreur lors de la mise à jour des statistiques: {e}")
