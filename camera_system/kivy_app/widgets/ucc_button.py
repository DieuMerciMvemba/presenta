"""
Widget Bouton personnalisé UCC pour Kivy
Boutons avec les couleurs UCC et styles cohérents - Design Professionnel
"""

from kivy.uix.button import Button
from kivy.properties import StringProperty, ColorProperty, ListProperty, NumericProperty
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from kivy.lang import Builder


Builder.load_string('''
<UCCButton>:
    background_color: 0, 0, 0, 0  # Transparent pour utiliser notre propre dessin
    canvas.before:
        # Fond principal avec coins arrondis
        Color:
            rgba: self.btn_color
        RoundedRectangle:
            size: self.size
            pos: self.pos
            radius: self.radius
        
        # Bordure subtile pour effet professionnel
        Color:
            rgba: [1, 1, 1, 0.15]
        Line:
            rounded_rectangle: self.x, self.y, self.width, self.height, self.radius[0]
            width: 1
    
    color: self.text_color
    font_name: 'Arial'
    font_size: self.font_size
    bold: self.bold
    size_hint: 1, None
    height: 48
    padding: 15, 10
''')

class UCCButton(Button):
    """Bouton personnalisé avec style UCC - Design Professionnel"""
    
    btn_color = ColorProperty([0.29, 0.56, 0.89, 1.0])  # ACCENT_BLUE par défaut
    text_color = ColorProperty([1.0, 1.0, 1.0, 1.0])  # Blanc par défaut
    radius = ListProperty([8, 8, 8, 8])  # Coins arrondis plus modernes
    font_size = 14
    bold = True
    
    def __init__(self, **kwargs):
        super(UCCButton, self).__init__(**kwargs)
        self.size_hint = (1, None)
        self.padding = (15, 10)
    
    def on_press(self):
        """Effet visuel lors du pressage"""
        # Assombrir la couleur légèrement
        current_color = list(self.btn_color)
        self.btn_color = [current_color[0] * 0.85, current_color[1] * 0.85, current_color[2] * 0.85, 1.0]
    
    def on_release(self):
        """Effet visuel lors du relâchement"""
        # Restaurer la couleur originale
        self.btn_color = [0.29, 0.56, 0.89, 1.0]  # ACCENT_BLUE par défaut
