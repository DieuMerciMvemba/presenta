"""
Écran Organisation pour l'application Kivy
Gestion des facultés, départements et cours
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.lang import Builder

Builder.load_string('''
<OrganizationScreen>:
    name: 'organization'
    
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
                text: '🏛️ Organisation - UCC'
                font_name: 'Arial'
                font_size: 22
                bold: True
                color: 1, 1, 1, 1
                size_hint_x: 0.7
                
            Button:
                text: '➕ Ajouter Faculté'
                background_color: 0.16, 0.65, 0.26, 1.0
                color: 1, 1, 1, 1
                size_hint_x: 0.3
                font_name: 'Arial'
                font_size: 12
        
        # Contenu principal
        BoxLayout:
            orientation: 'horizontal'
            padding: 20
            spacing: 20
            
            # Liste des facultés
            BoxLayout:
                orientation: 'vertical'
                canvas.before:
                    Color:
                        rgba: 1, 1, 1, 1
                    Rectangle:
                        size: self.size
                        pos: self.pos
                size_hint_x: 0.6
                padding: 15
                spacing: 10
                
                Label:
                    text: '📚 Facultés'
                    font_name: 'Arial'
                    font_size: 16
                    bold: True
                    color: 0.0, 0.2, 0.4, 1
                    size_hint_y: None
                    height: 30
                
                # Liste des facultés (placeholder)
                BoxLayout:
                    orientation: 'vertical'
                    canvas.before:
                        Color:
                            rgba: 0.95, 0.95, 0.95, 1
                        Rectangle:
                            size: self.size
                            pos: self.pos
                    size_hint_y: 1
                    padding: 20
                    
                    Label:
                        text: 'Faculté de Droit'
                        font_name: 'Arial'
                        font_size: 13
                        color: 0.2, 0.2, 0.2, 1
                        size_hint_y: None
                        height: 35
                        
                    Label:
                        text: "Faculté d'Économie"
                        font_name: 'Arial'
                        font_size: 13
                        color: 0.2, 0.2, 0.2, 1
                        size_hint_y: None
                        height: 35
                        
                    Label:
                        text: 'Faculté de Théologie'
                        font_name: 'Arial'
                        font_size: 13
                        color: 0.2, 0.2, 0.2, 1
                        size_hint_y: None
                        height: 35
                        
                    Label:
                        text: 'Faculté de Communication Sociale'
                        font_name: 'Arial'
                        font_size: 13
                        color: 0.2, 0.2, 0.2, 1
                        size_hint_y: None
                        height: 35
            
            # Sidebar détails
            BoxLayout:
                orientation: 'vertical'
                canvas.before:
                    Color:
                        rgba: 1, 1, 1, 1
                    Rectangle:
                        size: self.size
                        pos: self.pos
                size_hint_x: 0.4
                padding: 15
                spacing: 10
                
                Label:
                    text: '📋 Détails'
                    font_name: 'Arial'
                    font_size: 16
                    bold: True
                    color: 0.0, 0.2, 0.4, 1
                    size_hint_y: None
                    height: 30
                
                Label:
                    text: 'Sélectionnez une faculté pour voir les détails'
                    font_name: 'Arial'
                    font_size: 12
                    color: 0.4, 0.4, 0.4, 1
                    size_hint_y: None
                    height: 40
                
                BoxLayout:
                    size_hint_y: 1
                
                Label:
                    text: '📊 Statistiques'
                    font_name: 'Arial'
                    font_size: 14
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
                            text: 'Total Facultés:'
                            font_name: 'Arial'
                            font_size: 11
                            color: 0.4, 0.4, 0.4, 1
                            size_hint_x: 0.6
                            
                        Label:
                            text: '4'
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
                            text: 'Total Départements:'
                            font_name: 'Arial'
                            font_size: 11
                            color: 0.4, 0.4, 0.4, 1
                            size_hint_x: 0.6
                            
                        Label:
                            text: '12'
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
                            text: 'Total Cours:'
                            font_name: 'Arial'
                            font_size: 11
                            color: 0.4, 0.4, 0.4, 1
                            size_hint_x: 0.6
                            
                        Label:
                            text: '48'
                            font_name: 'Arial'
                            font_size: 11
                            bold: True
                            color: 0.0, 0.5, 1.0, 1
                            size_hint_x: 0.4
''')

class OrganizationScreen(Screen):
    """Écran Organisation"""
    
    def __init__(self, **kwargs):
        super(OrganizationScreen, self).__init__(**kwargs)
