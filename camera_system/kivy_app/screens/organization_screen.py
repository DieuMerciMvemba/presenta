"""
Écran Organisation pour l'application Kivy
Navigation professionnelle : Facultés → Promotions → Étudiants
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
from kivy.lang import Builder
from kivy.properties import ListProperty, ObjectProperty
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config import UCC_FACULTIES, UCC_PROMOTIONS
from services.database_service import DatabaseService

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
                size_hint_x: 0.5
                
            Button:
                text: '🔄 Refresh'
                background_color: 0.09, 0.64, 0.72, 1.0
                color: 1, 1, 1, 1
                size_hint_x: 0.15
                font_name: 'Arial'
                font_size: 12
                on_release: root.refresh_data()
                
            Button:
                text: '⬅️ Retour'
                background_color: 0.5, 0.5, 0.5, 1.0
                color: 1, 1, 1, 1
                size_hint_x: 0.15
                font_name: 'Arial'
                font_size: 12
                on_release: root.go_back()
        
        # Contenu principal - Navigation en 3 colonnes
        BoxLayout:
            orientation: 'horizontal'
            padding: 15
            spacing: 15
            
            # Colonne 1: Facultés
            BoxLayout:
                orientation: 'vertical'
                canvas.before:
                    Color:
                        rgba: 1, 1, 1, 1
                    Rectangle:
                        size: self.size
                        pos: self.pos
                size_hint_x: 0.3
                spacing: 10
                
                Label:
                    text: '📚 Facultés'
                    font_name: 'Arial'
                    font_size: 16
                    bold: True
                    color: 0.0, 0.2, 0.4, 1
                    size_hint_y: None
                    height: 40
                    canvas.before:
                        Color:
                            rgba: 0.95, 0.95, 0.95, 1
                        Rectangle:
                            size: self.size
                            pos: self.pos
                
                ScrollView:
                    id: faculty_scroll
                    BoxLayout:
                        id: faculty_list
                        orientation: 'vertical'
                        spacing: 5
                        size_hint_y: None
                        height: self.minimum_height
                        padding: 10
            
            # Colonne 2: Promotions
            BoxLayout:
                orientation: 'vertical'
                canvas.before:
                    Color:
                        rgba: 1, 1, 1, 1
                    Rectangle:
                        size: self.size
                        pos: self.pos
                size_hint_x: 0.3
                spacing: 10
                
                Label:
                    text: '🎓 Promotions'
                    font_name: 'Arial'
                    font_size: 16
                    bold: True
                    color: 0.0, 0.2, 0.4, 1
                    size_hint_y: None
                    height: 40
                    canvas.before:
                        Color:
                            rgba: 0.95, 0.95, 0.95, 1
                        Rectangle:
                            size: self.size
                            pos: self.pos
                
                ScrollView:
                    id: promotion_scroll
                    BoxLayout:
                        id: promotion_list
                        orientation: 'vertical'
                        spacing: 5
                        size_hint_y: None
                        height: self.minimum_height
                        padding: 10
            
            # Colonne 3: Étudiants
            BoxLayout:
                orientation: 'vertical'
                canvas.before:
                    Color:
                        rgba: 1, 1, 1, 1
                    Rectangle:
                        size: self.size
                        pos: self.pos
                size_hint_x: 0.4
                spacing: 10
                
                Label:
                    text: '👥 Étudiants'
                    font_name: 'Arial'
                    font_size: 16
                    bold: True
                    color: 0.0, 0.2, 0.4, 1
                    size_hint_y: None
                    height: 40
                    canvas.before:
                        Color:
                            rgba: 0.95, 0.95, 0.95, 1
                        Rectangle:
                            size: self.size
                            pos: self.pos
                
                ScrollView:
                    id: student_scroll
                    BoxLayout:
                        id: student_list
                        orientation: 'vertical'
                        spacing: 5
                        size_hint_y: None
                        height: self.minimum_height
                        padding: 10
''')

class OrganizationScreen(Screen):
    """Écran Organisation avec navigation professionnelle"""
    
    selected_faculty = ObjectProperty(None, allownone=True)
    selected_promotion = ObjectProperty(None, allownone=True)
    faculties_data = ListProperty([])
    promotions_data = ListProperty([])
    students_data = ListProperty([])
    
    def __init__(self, **kwargs):
        super(OrganizationScreen, self).__init__(**kwargs)
        self.db_service = DatabaseService(
            host='localhost',
            database='ucc_face_recognition',
            user='root',
            password='admin123',
            port=3306
        )
        self.current_view = 'faculties'  # faculties, promotions, students
    
    def on_enter(self):
        """Appelé lorsque l'écran est affiché"""
        self.load_data_from_mysql()
    
    def load_data_from_mysql(self):
        """Charge les données depuis MySQL"""
        try:
            # Charger les facultés depuis MySQL
            mysql_faculties = self.db_service.get_all_faculties()
            if mysql_faculties:
                self.faculties_data = mysql_faculties
                print(f"✅ {len(self.faculties_data)} facultés chargées depuis MySQL")
            else:
                print("⚠️ Aucune faculté trouvée dans MySQL")
                self.faculties_data = []
            
            # Charger les promotions depuis MySQL
            mysql_promotions = self.db_service.get_all_promotions()
            if mysql_promotions:
                self.promotions_data = mysql_promotions
                print(f"✅ {len(self.promotions_data)} promotions chargées depuis MySQL")
            else:
                print("⚠️ Aucune promotion trouvée dans MySQL")
                self.promotions_data = []
            
            # Réinitialiser la sélection
            self.selected_faculty = None
            self.selected_promotion = None
            
            # Mettre à jour l'affichage
            self.update_display()
            
        except Exception as e:
            print(f"❌ Erreur lors du chargement des données depuis MySQL: {e}")
    
    def refresh_data(self):
        """Rafraîchit les données depuis MySQL"""
        print("🔄 Rafraîchissement des données...")
        self.load_data_from_mysql()
    
    def update_display(self):
        """Met à jour l'affichage selon la vue actuelle"""
        # Afficher les facultés
        self.display_faculties()
        
        # Afficher les promotions (vides par défaut)
        self.display_promotions([])
        
        # Afficher les étudiants (vides par défaut)
        self.display_students([])
    
    def display_faculties(self):
        """Affiche la liste des facultés"""
        faculty_list = self.ids.faculty_list
        faculty_list.clear_widgets()
        
        if not self.faculties_data:
            label = Label(
                text='Aucune faculté disponible',
                font_name='Arial',
                font_size=12,
                color=(0.4, 0.4, 0.4, 1),
                size_hint_y=None,
                height=40
            )
            faculty_list.add_widget(label)
            return
        
        for faculty in self.faculties_data:
            btn = Button(
                text=f"{faculty['nom']}",
                font_name='Arial',
                font_size=13,
                background_normal='',
                background_color=(0.97, 0.97, 0.97, 1) if faculty != self.selected_faculty else (0.09, 0.64, 0.72, 1),
                color=(1, 1, 1, 1) if faculty == self.selected_faculty else (0.2, 0.2, 0.2, 1),
                size_hint_y=None,
                height=45,
                padding=10
            )
            btn.bind(on_release=lambda instance, f=faculty: self.select_faculty(f))
            faculty_list.add_widget(btn)
    
    def display_promotions(self, promotions):
        """Affiche la liste des promotions"""
        promotion_list = self.ids.promotion_list
        promotion_list.clear_widgets()
        
        if not promotions:
            label = Label(
                text='Sélectionnez une faculté pour voir les promotions',
                font_name='Arial',
                font_size=12,
                color=(0.4, 0.4, 0.4, 1),
                size_hint_y=None,
                height=40
            )
            promotion_list.add_widget(label)
            return
        
        for promotion in promotions:
            btn = Button(
                text=f"{promotion['nom']}",
                font_name='Arial',
                font_size=13,
                background_normal='',
                background_color=(0.97, 0.97, 0.97, 1) if promotion != self.selected_promotion else (0.09, 0.64, 0.72, 1),
                color=(1, 1, 1, 1) if promotion == self.selected_promotion else (0.2, 0.2, 0.2, 1),
                size_hint_y=None,
                height=45,
                padding=10
            )
            btn.bind(on_release=lambda instance, p=promotion: self.select_promotion(p))
            promotion_list.add_widget(btn)
    
    def display_students(self, students):
        """Affiche la liste des étudiants"""
        student_list = self.ids.student_list
        student_list.clear_widgets()
        
        if not students:
            label = Label(
                text='Sélectionnez une promotion pour voir les étudiants',
                font_name='Arial',
                font_size=12,
                color=(0.4, 0.4, 0.4, 1),
                size_hint_y=None,
                height=40
            )
            student_list.add_widget(label)
            return
        
        # Header
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=30,
            spacing=5
        )
        header.canvas.before.add(Color(rgba=(0.9, 0.9, 0.9, 1)))
        header.canvas.before.add(Rectangle(size=header.size, pos=header.pos))
        
        header.add_widget(Label(text='Matricule', font_name='Arial', font_size=11, bold=True, color=(0.2, 0.2, 0.2, 1), size_hint_x=0.25))
        header.add_widget(Label(text='Nom', font_name='Arial', font_size=11, bold=True, color=(0.2, 0.2, 0.2, 1), size_hint_x=0.35))
        header.add_widget(Label(text='Prénom', font_name='Arial', font_size=11, bold=True, color=(0.2, 0.2, 0.2, 1), size_hint_x=0.4))
        student_list.add_widget(header)
        
        for student in students:
            row = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=35,
                spacing=5
            )
            
            # Fond alterné
            bg_color = (0.97, 0.97, 0.97, 1) if students.index(student) % 2 == 0 else (1, 1, 1, 1)
            row.canvas.before.add(Color(rgba=bg_color))
            row.canvas.before.add(Rectangle(size=row.size, pos=row.pos))
            
            matricule_label = Label(
                text=student.get('matricule', ''),
                font_name='Arial',
                font_size=11,
                color=(0.2, 0.2, 0.2, 1),
                size_hint_x=0.25
            )
            
            nom_label = Label(
                text=student.get('nom', ''),
                font_name='Arial',
                font_size=11,
                color=(0.2, 0.2, 0.2, 1),
                size_hint_x=0.35
            )
            
            prenom_label = Label(
                text=student.get('prenom', ''),
                font_name='Arial',
                font_size=11,
                color=(0.2, 0.2, 0.2, 1),
                size_hint_x=0.4
            )
            
            row.add_widget(matricule_label)
            row.add_widget(nom_label)
            row.add_widget(prenom_label)
            student_list.add_widget(row)
    
    def select_faculty(self, faculty):
        """Sélectionne une faculté et affiche ses promotions"""
        self.selected_faculty = faculty
        self.selected_promotion = None
        
        # Réafficher les facultés avec la sélection mise en évidence
        self.display_faculties()
        
        # Afficher toutes les promotions (pas filtrées par faculté pour l'instant)
        self.display_promotions(self.promotions_data)
        
        # Vider la liste des étudiants
        self.display_students([])
        
        print(f"📚 Faculté sélectionnée: {faculty['nom']}")
    
    def select_promotion(self, promotion):
        """Sélectionne une promotion et affiche les étudiants correspondants"""
        self.selected_promotion = promotion
        
        # Réafficher les promotions avec la sélection mise en évidence
        self.display_promotions(self.promotions_data)
        
        # Charger les étudiants filtrés par faculté et promotion
        self.load_students_filtered()
        
        print(f"🎓 Promotion sélectionnée: {promotion['nom']}")
    
    def load_students_filtered(self):
        """Charge les étudiants filtrés par faculté et promotion"""
        try:
            all_students = self.db_service.get_all_students()
            
            # Filtrer par faculté et promotion
            filtered_students = []
            for student in all_students:
                if self.selected_faculty and student.get('faculte_id') != self.selected_faculty.get('id'):
                    continue
                if self.selected_promotion and student.get('promotion_id') != self.selected_promotion.get('id'):
                    continue
                filtered_students.append(student)
            
            self.students_data = filtered_students
            self.display_students(filtered_students)
            
            print(f"👥 {len(filtered_students)} étudiants trouvés")
            
        except Exception as e:
            print(f"❌ Erreur lors du chargement des étudiants: {e}")
            self.display_students([])
    
    def go_back(self):
        """Retour à la vue précédente"""
        if self.current_view == 'students' and self.selected_promotion:
            self.selected_promotion = None
            self.display_promotions(self.promotions_data)
            self.display_students([])
            self.current_view = 'promotions'
        elif self.current_view == 'promotions' and self.selected_faculty:
            self.selected_faculty = None
            self.display_faculties()
            self.display_promotions([])
            self.current_view = 'faculties'
