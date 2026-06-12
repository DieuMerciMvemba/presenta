"""
Widget Header pour Kivy
Bandeau supérieur avec logo, titre et informations utilisateur
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.properties import StringProperty
from kivy.graphics import Color, Rectangle
from kivy.lang import Builder


Builder.load_string('''
<Header>:
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
    
    # Logo et titre
    BoxLayout:
        orientation: 'horizontal'
        size_hint_x: 0.6
        spacing: 15
        
        Label:
            text: '🎓'
            font_size: 32
            color: 1, 1, 1, 1
            size_hint_x: None
            width: 50
        
        BoxLayout:
            orientation: 'vertical'
            spacing: 2
            
            Label:
                text: root.title
                font_name: 'Arial'
                font_size: 20
                bold: True
                color: 1, 1, 1, 1
                size_hint_y: 0.6
                text_size: self.width, None
                
            Label:
                text: root.subtitle
                font_name: 'Arial'
                font_size: 12
                color: 0.9, 0.9, 0.9, 1
                size_hint_y: 0.4
                text_size: self.width, None
    
    # Informations utilisateur
    BoxLayout:
        orientation: 'horizontal'
        size_hint_x: 0.4
        spacing: 10
        
        Label:
            text: '👤 Admin'
            font_name: 'Arial'
            font_size: 14
            color: 1, 1, 1, 1
            size_hint_x: 0.5
        
        BoxLayout:
            orientation: 'vertical'
            size_hint_x: 0.5
            spacing: 5
            
            Label:
                text: '📅 ' + root.current_date
                font_name: 'Arial'
                font_size: 11
                color: 0.9, 0.9, 0.9, 1
                size_hint_y: 0.5
                
            Label:
                text: '🕐 ' + root.current_time
                font_name: 'Arial'
                font_size: 11
                color: 0.9, 0.9, 0.9, 1
                size_hint_y: 0.5
''')

class Header(BoxLayout):
    """Widget Header avec style UCC"""
    
    title = StringProperty("Système de Reconnaissance Faciale - UCC")
    subtitle = StringProperty("Pointage Automatique des Étudiants")
    current_date = StringProperty("")
    current_time = StringProperty("")
    
    def __init__(self, **kwargs):
        super(Header, self).__init__(**kwargs)
        self.update_datetime()
    
    def update_datetime(self):
        """Met à jour la date et l'heure actuelles"""
        from datetime import datetime
        now = datetime.now()
        self.current_date = now.strftime("%d/%m/%Y")
        self.current_time = now.strftime("%H:%M")
