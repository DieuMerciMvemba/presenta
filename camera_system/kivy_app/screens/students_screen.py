"""
Écran Gestion Étudiants pour l'application Kivy
Liste, ajout, modification et suppression des étudiants
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty, ListProperty
from kivy.graphics import Color, Rectangle
from kivy.lang import Builder
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from services.database_service import DatabaseService

Builder.load_string('''
<StudentsScreen>:
    name: 'students'
    
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
                text: '👥 Gestion des Étudiants - UCC'
                font_name: 'Arial'
                font_size: 22
                bold: True
                color: 1, 1, 1, 1
                size_hint_x: 0.7
                
            BoxLayout:
                orientation: 'horizontal'
                size_hint_x: 0.3
                spacing: 10
                
                Button:
                    text: '➕ Ajouter'
                    background_color: 0.16, 0.65, 0.26, 1.0
                    color: 1, 1, 1, 1
                    size_hint_x: 0.5
                    font_name: 'Arial'
                    font_size: 12
                    on_release: root.show_add_student_popup()
                    
                Button:
                    text: '📥 Importer'
                    background_color: 0.09, 0.63, 0.72, 1.0
                    color: 1, 1, 1, 1
                    size_hint_x: 0.5
                    font_name: 'Arial'
                    font_size: 12
        
        # Barre de recherche et filtres
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: 50
            padding: 20
            spacing: 10
            
            Label:
                text: '🔍'
                font_size: 20
                size_hint_x: None
                width: 40
                
            TextInput:
                id: search_input
                hint_text: 'Rechercher par matricule, nom ou prénom...'
                size_hint_x: 0.6
                font_name: 'Arial'
                font_size: 12
                multiline: False
                
            Button:
                text: 'Filtrer'
                background_color: 0.0, 0.5, 1.0, 1.0
                color: 1, 1, 1, 1
                size_hint_x: 0.15
                font_name: 'Arial'
                font_size: 12
                
            Button:
                text: 'Réinitialiser'
                background_color: 0.42, 0.46, 0.49, 1.0
                color: 1, 1, 1, 1
                size_hint_x: 0.15
                font_name: 'Arial'
                font_size: 12
        
        # Contenu principal avec liste des étudiants
        BoxLayout:
            orientation: 'horizontal'
            padding: 20
            spacing: 20
            
            # Liste des étudiants
            BoxLayout:
                orientation: 'vertical'
                canvas.before:
                    Color:
                        rgba: 1, 1, 1, 1
                    Rectangle:
                        size: self.size
                        pos: self.pos
                padding: 15
                spacing: 10
                
                # En-tête du tableau
                BoxLayout:
                    orientation: 'horizontal'
                    size_hint_y: None
                    height: 40
                    canvas.before:
                        Color:
                            rgba: 0.9, 0.9, 0.9, 1
                        Rectangle:
                            size: self.size
                            pos: self.pos
                    padding: 10
                    spacing: 5
                    
                    Label:
                        text: 'Matricule'
                        font_name: 'Arial'
                        font_size: 11
                        bold: True
                        color: 0.0, 0.2, 0.4, 1
                        size_hint_x: 0.2
                        
                    Label:
                        text: 'Nom'
                        font_name: 'Arial'
                        font_size: 11
                        bold: True
                        color: 0.0, 0.2, 0.4, 1
                        size_hint_x: 0.25
                        
                    Label:
                        text: 'Prénom'
                        font_name: 'Arial'
                        font_size: 11
                        bold: True
                        color: 0.0, 0.2, 0.4, 1
                        size_hint_x: 0.25
                        
                    Label:
                        text: 'Photos'
                        font_name: 'Arial'
                        font_size: 11
                        bold: True
                        color: 0.0, 0.2, 0.4, 1
                        size_hint_x: 0.1
                        
                    Label:
                        text: 'Actions'
                        font_name: 'Arial'
                        font_size: 11
                        bold: True
                        color: 0.0, 0.2, 0.4, 1
                        size_hint_x: 0.2
                
                # Liste déroulante des étudiants
                ScrollView:
                    id: student_scroll
                    BoxLayout:
                        id: student_list
                        orientation: 'vertical'
                        spacing: 5
                        size_hint_y: None
                        height: self.minimum_height
                
                # Informations de pagination
                BoxLayout:
                    orientation: 'horizontal'
                    size_hint_y: None
                    height: 35
                    spacing: 10
                    
                    Label:
                        text: 'Total: ' + str(root.total_students) + ' étudiants'
                        font_name: 'Arial'
                        font_size: 11
                        color: 0.4, 0.4, 0.4, 1
                        
                    BoxLayout:
                        size_hint_x: 1
                        
                    Label:
                        text: 'Page 1/1'
                        font_name: 'Arial'
                        font_size: 11
                        color: 0.4, 0.4, 0.4, 1
''')

class StudentsScreen(Screen):
    """Écran Gestion des Étudiants"""
    
    total_students = 0
    students = ListProperty([])
    
    def __init__(self, **kwargs):
        super(StudentsScreen, self).__init__(**kwargs)
        self.db_service = DatabaseService()
    
    def on_enter(self):
        """Appelé lorsque l'écran est affiché"""
        self.load_students()
    
    def load_students(self):
        """Charge la liste des étudiants depuis la base de données"""
        try:
            self.students = self.db_service.get_all_students()
            self.total_students = len(self.students)
            self.populate_student_list()
        except Exception as e:
            print(f"Erreur lors du chargement des étudiants: {e}")
    
    def populate_student_list(self):
        """Remplit la liste des étudiants dans l'interface"""
        student_list = self.ids.student_list
        student_list.clear_widgets()
        
        for student in self.students:
            # Créer une ligne pour chaque étudiant
            row = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=45,
                padding=10,
                spacing=5
            )
            
            # Fond alterné
            bg_color = (0.97, 0.97, 0.97, 1) if self.students.index(student) % 2 == 0 else (1, 1, 1, 1)
            with row.canvas.before:
                Color(*bg_color)
                Rectangle(size=row.size, pos=row.pos)
            
            # Matricule
            matricule_label = Label(
                text=student['matricule'],
                font_name='Arial',
                font_size=11,
                color=(0.2, 0.2, 0.2, 1),
                size_hint_x=0.2
            )
            
            # Nom
            nom_label = Label(
                text=student['nom'],
                font_name='Arial',
                font_size=11,
                color=(0.2, 0.2, 0.2, 1),
                size_hint_x=0.25
            )
            
            # Prénom
            prenom_label = Label(
                text=student['prenom'],
                font_name='Arial',
                font_size=11,
                color=(0.2, 0.2, 0.2, 1),
                size_hint_x=0.25
            )
            
            # Nombre de photos
            photos_label = Label(
                text=str(student['num_photos']),
                font_name='Arial',
                font_size=11,
                color=(0.2, 0.2, 0.2, 1),
                size_hint_x=0.1
            )
            
            # Actions
            actions_layout = BoxLayout(
                orientation='horizontal',
                size_hint_x=0.2,
                spacing=5
            )
            
            edit_btn = Button(
                text='✏️',
                font_size=14,
                background_color=(0.0, 0.5, 1.0, 1.0),
                color=(1, 1, 1, 1),
                size_hint_x=0.5
            )
            
            delete_btn = Button(
                text='🗑️',
                font_size=14,
                background_color=(0.86, 0.21, 0.27, 1.0),
                color=(1, 1, 1, 1),
                size_hint_x=0.5
            )
            
            actions_layout.add_widget(edit_btn)
            actions_layout.add_widget(delete_btn)
            
            row.add_widget(matricule_label)
            row.add_widget(nom_label)
            row.add_widget(prenom_label)
            row.add_widget(photos_label)
            row.add_widget(actions_layout)
            
            student_list.add_widget(row)
        
        # Ajuster la hauteur de la liste
        student_list.height = len(self.students) * 50
    
    def show_add_student_popup(self):
        """Affiche le popup d'ajout d'étudiant"""
        content = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Matricule
        content.add_widget(Label(text='Matricule:', font_name='Arial', font_size=12, color=(0.2, 0.2, 0.2, 1)))
        matricule_input = TextInput(hint_text='Ex: UCC2024001', font_name='Arial', font_size=12)
        content.add_widget(matricule_input)
        
        # Nom
        content.add_widget(Label(text='Nom:', font_name='Arial', font_size=12, color=(0.2, 0.2, 0.2, 1)))
        nom_input = TextInput(hint_text='Ex: Doe', font_name='Arial', font_size=12)
        content.add_widget(nom_input)
        
        # Prénom
        content.add_widget(Label(text='Prénom:', font_name='Arial', font_size=12, color=(0.2, 0.2, 0.2, 1)))
        prenom_input = TextInput(hint_text='Ex: John', font_name='Arial', font_size=12)
        content.add_widget(prenom_input)
        
        # Boutons
        btn_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=40)
        
        cancel_btn = Button(text='Annuler', background_color=(0.42, 0.46, 0.49, 1.0), color=(1, 1, 1, 1))
        save_btn = Button(text='Enregistrer', background_color=(0.16, 0.65, 0.26, 1.0), color=(1, 1, 1, 1))
        
        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(save_btn)
        content.add_widget(btn_layout)
        
        popup = Popup(
            title='Ajouter un Étudiant',
            content=content,
            size_hint=(0.4, 0.5)
        )
        
        def dismiss_popup(instance):
            popup.dismiss()
        
        cancel_btn.bind(on_release=dismiss_popup)
        save_btn.bind(on_release=dismiss_popup)
        
        popup.open()
