"""
Widget Sidebar pour Kivy
Menu latéral de navigation avec les options principales - Design Professionnel
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.properties import StringProperty, ObjectProperty
from kivy.graphics import Color, Rectangle, Line
from kivy.lang import Builder
from .ucc_button import UCCButton


Builder.load_string('''
<Sidebar>:
    orientation: 'vertical'
    size_hint_x: None
    width: 250
    spacing: 0
    canvas.before:
        Color:
            rgba: 0.12, 0.23, 0.37, 1.0  # UCC_BLUE_DARK
        Rectangle:
            size: self.size
            pos: self.pos
        # Bordure droite
        Color:
            rgba: 0.18, 0.35, 0.56, 1.0  # UCC_BLUE_LIGHT
        Rectangle:
            size: 2, self.height
            pos: self.right - 2, self.y
    
    # Logo UCC
    BoxLayout:
        orientation: 'vertical'
        size_hint_y: None
        height: 100
        padding: 20
        spacing: 8
        
        Label:
            text: '🎓'
            font_size: 36
            size_hint_y: None
            height: 45
            halign: 'center'
            
        Label:
            text: 'UCC'
            font_name: 'Arial'
            font_size: 24
            bold: True
            color: 1, 1, 1, 1
            halign: 'center'
            
        Label:
            text: 'Reconnaissance Faciale'
            font_name: 'Arial'
            font_size: 10
            color: 0.8, 0.9, 1, 1
            halign: 'center'
    
    # Séparateur
    BoxLayout:
        size_hint_y: None
        height: 1
        canvas.before:
            Color:
                rgba: 0.29, 0.45, 0.69, 0.3
            Rectangle:
                size: self.size
                pos: self.pos
    
    # Menu items
    BoxLayout:
        orientation: 'vertical'
        spacing: 2
        padding: 10
        
        UCCButton:
            text: '🏠 Tableau de bord'
            btn_color: [0.29, 0.56, 0.89, 1.0]  # ACCENT_BLUE
            size_hint_y: None
            height: 48
            on_release: root.go_to_dashboard()
            
        UCCButton:
            text: '👥 Gestion Étudiants'
            btn_color: [0.16, 0.65, 0.27, 1.0]  # ACCENT_GREEN
            size_hint_y: None
            height: 48
            on_release: root.go_to_students()
            
        UCCButton:
            text: '📸 Pointage Caméra'
            btn_color: [1.0, 0.76, 0.03, 1.0]  # ACCENT_YELLOW
            size_hint_y: None
            height: 48
            on_release: root.go_to_attendance()
            
        UCCButton:
            text: '🏛️ Organisation'
            btn_color: [0.09, 0.64, 0.72, 1.0]  # ACCENT_CYAN
            size_hint_y: None
            height: 48
            on_release: root.go_to_organization()
            
        UCCButton:
            text: '📊 Rapports'
            btn_color: [0.43, 0.26, 0.76, 1.0]  # ACCENT_PURPLE
            size_hint_y: None
            height: 48
            on_release: root.go_to_reports()
            
        UCCButton:
            text: '⚙️ Paramètres'
            btn_color: [0.42, 0.46, 0.49, 1.0]  # BUTTON_SECONDARY
            size_hint_y: None
            height: 48
            on_release: root.go_to_settings()
    
    # Espaceur
    BoxLayout:
        size_hint_y: 1
    
    # Statistiques rapides
    BoxLayout:
        orientation: 'vertical'
        size_hint_y: None
        height: 140
        padding: 15
        spacing: 8
        
        Label:
            text: '📊 Statistiques'
            font_name: 'Arial'
            font_size: 13
            bold: True
            color: 0.9, 0.95, 1, 1
            size_hint_y: None
            height: 25
            
        # Carte statistique 1
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: 32
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
            padding: 10
            spacing: 8
            
            Label:
                text: '👥'
                font_size: 16
                size_hint_x: None
                width: 25
                
            Label:
                text: str(root.student_count)
                font_name: 'Arial'
                font_size: 14
                bold: True
                color: 1, 1, 1, 1
                size_hint_x: 0.4
                
            Label:
                text: 'Étudiants'
                font_name: 'Arial'
                font_size: 11
                color: 0.8, 0.9, 1, 1
                size_hint_x: 0.6
        
        # Carte statistique 2
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: 32
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
            padding: 10
            spacing: 8
            
            Label:
                text: '✅'
                font_size: 16
                size_hint_x: None
                width: 25
                
            Label:
                text: str(root.present_count)
                font_name: 'Arial'
                font_size: 14
                bold: True
                color: 0.16, 0.65, 0.26, 1
                size_hint_x: 0.4
                
            Label:
                text: 'Présents'
                font_name: 'Arial'
                font_size: 11
                color: 0.8, 0.9, 1, 1
                size_hint_x: 0.6
    
    # Séparateur
    BoxLayout:
        size_hint_y: None
        height: 1
        canvas.before:
            Color:
                rgba: 0.29, 0.45, 0.69, 0.3
            Rectangle:
                size: self.size
                pos: self.pos
    
    # Bouton déconnexion
    BoxLayout:
        orientation: 'vertical'
        size_hint_y: None
        height: 70
        padding: 15
        spacing: 5
        
        UCCButton:
            text: '🚪 Déconnexion'
            btn_color: [0.86, 0.21, 0.27, 1.0]  # ACCENT_RED
            size_hint_y: None
            height: 42
            on_release: root.logout()
''')

class Sidebar(BoxLayout):
    """Widget Sidebar avec navigation UCC - Design Professionnel"""
    
    screen_manager = ObjectProperty(None)
    student_count = 0
    present_count = 0
    
    def __init__(self, **kwargs):
        super(Sidebar, self).__init__(**kwargs)
    
    def go_to_dashboard(self):
        """Navigue vers le tableau de bord"""
        if self.screen_manager:
            self.screen_manager.current = 'dashboard'
    
    def go_to_students(self):
        """Navigue vers la gestion des étudiants"""
        if self.screen_manager:
            self.screen_manager.current = 'students'
    
    def go_to_attendance(self):
        """Navigue vers le pointage caméra"""
        if self.screen_manager:
            self.screen_manager.current = 'attendance'
    
    def go_to_organization(self):
        """Navigue vers l'organisation"""
        if self.screen_manager:
            self.screen_manager.current = 'organization'
    
    def go_to_reports(self):
        """Navigue vers les rapports"""
        if self.screen_manager:
            self.screen_manager.current = 'reports'
    
    def go_to_settings(self):
        """Navigue vers les paramètres"""
        if self.screen_manager:
            self.screen_manager.current = 'settings'
    
    def logout(self):
        """Déconnexion de l'application"""
        if self.screen_manager:
            # Pour l'instant, on affiche un message
            print("Déconnexion...")
    
    def update_statistics(self, student_count, present_count):
        """Met à jour les statistiques affichées"""
        self.student_count = student_count
        self.present_count = present_count
