"""
Widget pour afficher des images de graphiques matplotlib dans Kivy
"""

from kivy.uix.image import Image
from kivy.properties import StringProperty
import os


class ChartImage(Image):
    """Widget personnalisé pour afficher des graphiques"""
    
    source = StringProperty('')
    
    def __init__(self, **kwargs):
        super(ChartImage, self).__init__(**kwargs)
        self.allow_stretch = True
        self.keep_ratio = True
    
    def on_source(self, instance, value):
        """Appelé quand la source change"""
        if value and os.path.exists(value):
            self.reload()
