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
                on_release: root.filter_students()
                
            Button:
                text: 'Réinitialiser'
                background_color: 0.42, 0.46, 0.49, 1.0
                color: 1, 1, 1, 1
                size_hint_x: 0.15
                font_name: 'Arial'
                font_size: 12
                on_release: root.reset_filter()
        
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
                        size_hint_x: 0.3
                
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
        self.db_service = DatabaseService(
            host='localhost',
            database='ucc_face_recognition',
            user='root',
            password='admin123',
            port=3306
        )
    
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
                size_hint_x=0.3,
                spacing=5
            )
            
            history_btn = Button(
                text='📅',
                font_size=14,
                background_color=(0.43, 0.26, 0.76, 1.0),
                color=(1, 1, 1, 1),
                size_hint_x=0.33
            )
            
            edit_btn = Button(
                text='✏️',
                font_size=14,
                background_color=(0.0, 0.5, 1.0, 1.0),
                color=(1, 1, 1, 1),
                size_hint_x=0.33
            )
            
            delete_btn = Button(
                text='🗑️',
                font_size=14,
                background_color=(0.86, 0.21, 0.27, 1.0),
                color=(1, 1, 1, 1),
                size_hint_x=0.33
            )
            
            actions_layout.add_widget(history_btn)
            actions_layout.add_widget(edit_btn)
            actions_layout.add_widget(delete_btn)
            
            # Connecter les boutons aux méthodes
            history_btn.bind(on_release=lambda instance: self.show_student_history(student['id']))
            edit_btn.bind(on_release=lambda instance: self.edit_student(student['id']))
            delete_btn.bind(on_release=lambda instance: self.delete_student(student['id']))
            
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
        
        # Email
        content.add_widget(Label(text='Email:', font_name='Arial', font_size=12, color=(0.2, 0.2, 0.2, 1)))
        email_input = TextInput(hint_text='Ex: john.doe@ucc.edu', font_name='Arial', font_size=12)
        content.add_widget(email_input)
        
        # Téléphone
        content.add_widget(Label(text='Téléphone:', font_name='Arial', font_size=12, color=(0.2, 0.2, 0.2, 1)))
        telephone_input = TextInput(hint_text='Ex: +243123456789', font_name='Arial', font_size=12)
        content.add_widget(telephone_input)
        
        # Boutons
        btn_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=40)
        
        cancel_btn = Button(text='Annuler', background_color=(0.42, 0.46, 0.49, 1.0), color=(1, 1, 1, 1))
        save_btn = Button(text='Enregistrer', background_color=(0.16, 0.65, 0.27, 1.0), color=(1, 1, 1, 1))
        
        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(save_btn)
        content.add_widget(btn_layout)
        
        popup = Popup(
            title='Ajouter un Étudiant',
            content=content,
            size_hint=(0.4, 0.6)
        )
        
        def dismiss_popup(instance):
            popup.dismiss()
        
        def save_student(instance):
            """Sauvegarde l'étudiant dans MySQL"""
            try:
                matricule = matricule_input.text.strip()
                nom = nom_input.text.strip()
                prenom = prenom_input.text.strip()
                email = email_input.text.strip()
                telephone = telephone_input.text.strip()
                
                if not matricule or not nom or not prenom:
                    print("❌ Veuillez remplir les champs obligatoires")
                    return
                
                student_id = self.db_service.insert_student(
                    matricule=matricule,
                    nom=nom,
                    prenom=prenom,
                    email=email if email else None,
                    telephone=telephone if telephone else None
                )
                
                if student_id:
                    print(f"✅ Étudiant ajouté avec succès (ID: {student_id})")
                    self.load_students()  # Recharger la liste
                    popup.dismiss()
                else:
                    print("❌ Erreur lors de l'ajout de l'étudiant")
                    
            except Exception as e:
                print(f"❌ Erreur: {e}")
        
        cancel_btn.bind(on_release=dismiss_popup)
        save_btn.bind(on_release=save_student)
        
        popup.open()
    
    def edit_student(self, student_id):
        """Affiche le popup d'édition d'étudiant"""
        # Récupérer les données de l'étudiant
        student_data = self.db_service.find_student_by_id(student_id)
        if not student_data:
            print("❌ Étudiant non trouvé")
            return
        
        # Accéder aux métadonnées de l'étudiant
        student = student_data.get('metadata', student_data)
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Matricule (non modifiable)
        content.add_widget(Label(text='Matricule:', font_name='Arial', font_size=12, color=(0.2, 0.2, 0.2, 1)))
        matricule_input = TextInput(text=student['matricule'], font_name='Arial', font_size=12, readonly=True)
        content.add_widget(matricule_input)
        
        # Nom
        content.add_widget(Label(text='Nom:', font_name='Arial', font_size=12, color=(0.2, 0.2, 0.2, 1)))
        nom_input = TextInput(text=student['nom'], font_name='Arial', font_size=12)
        content.add_widget(nom_input)
        
        # Prénom
        content.add_widget(Label(text='Prénom:', font_name='Arial', font_size=12, color=(0.2, 0.2, 0.2, 1)))
        prenom_input = TextInput(text=student['prenom'], font_name='Arial', font_size=12)
        content.add_widget(prenom_input)
        
        # Email
        content.add_widget(Label(text='Email:', font_name='Arial', font_size=12, color=(0.2, 0.2, 0.2, 1)))
        email_input = TextInput(text=student.get('email', ''), font_name='Arial', font_size=12)
        content.add_widget(email_input)
        
        # Téléphone
        content.add_widget(Label(text='Téléphone:', font_name='Arial', font_size=12, color=(0.2, 0.2, 0.2, 1)))
        telephone_input = TextInput(text=student.get('telephone', ''), font_name='Arial', font_size=12)
        content.add_widget(telephone_input)
        
        # Boutons
        btn_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=40)
        
        cancel_btn = Button(text='Annuler', background_color=(0.42, 0.46, 0.49, 1.0), color=(1, 1, 1, 1))
        save_btn = Button(text='Mettre à jour', background_color=(0.16, 0.65, 0.27, 1.0), color=(1, 1, 1, 1))
        
        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(save_btn)
        content.add_widget(btn_layout)
        
        popup = Popup(
            title='Modifier un Étudiant',
            content=content,
            size_hint=(0.4, 0.6)
        )
        
        def dismiss_popup(instance):
            popup.dismiss()
        
        def update_student(instance):
            """Met à jour l'étudiant dans MySQL"""
            try:
                nom = nom_input.text.strip()
                prenom = prenom_input.text.strip()
                email = email_input.text.strip()
                telephone = telephone_input.text.strip()
                
                if not nom or not prenom:
                    print("❌ Veuillez remplir les champs obligatoires")
                    return
                
                success = self.db_service.update_student(
                    student_id=student_id,
                    nom=nom,
                    prenom=prenom,
                    email=email if email else None,
                    telephone=telephone if telephone else None
                )
                
                if success:
                    print(f"✅ Étudiant mis à jour avec succès")
                    self.load_students()  # Recharger la liste
                    popup.dismiss()
                else:
                    print("❌ Erreur lors de la mise à jour de l'étudiant")
                    
            except Exception as e:
                print(f"❌ Erreur: {e}")
        
        cancel_btn.bind(on_release=dismiss_popup)
        save_btn.bind(on_release=update_student)
        
        popup.open()
    
    def delete_student(self, student_id):
        """Supprime un étudiant"""
        try:
            success = self.db_service.delete_student(student_id)
            if success:
                print(f"✅ Étudiant supprimé avec succès")
                self.load_students()  # Recharger la liste
            else:
                print("❌ Erreur lors de la suppression de l'étudiant")
        except Exception as e:
            print(f"❌ Erreur: {e}")
    
    def filter_students(self):
        """Filtre la liste des étudiants selon le critère de recherche"""
        try:
            search_input = self.ids.search_input
            search_term = search_input.text.strip().lower()
            
            if not search_term:
                self.load_students()  # Si recherche vide, charger tous les étudiants
                return
            
            # Filtrer les étudiants localement
            all_students = self.db_service.get_all_students()
            filtered_students = []
            
            for student in all_students:
                # Rechercher dans matricule, nom et prénom
                if (search_term in student.get('matricule', '').lower() or
                    search_term in student.get('nom', '').lower() or
                    search_term in student.get('prenom', '').lower()):
                    filtered_students.append(student)
            
            self.students = filtered_students
            self.total_students = len(filtered_students)
            self.populate_student_list()
            print(f"🔍 {len(filtered_students)} étudiants trouvés pour '{search_term}'")
            
        except Exception as e:
            print(f"❌ Erreur lors du filtrage: {e}")
    
    def reset_filter(self):
        """Réinitialise le filtre et affiche tous les étudiants"""
        try:
            self.ids.search_input.text = ""
            self.load_students()
            print("🔄 Filtre réinitialisé")
        except Exception as e:
            print(f"❌ Erreur lors de la réinitialisation: {e}")
    
    def show_student_history(self, student_id):
        """Affiche l'historique de présence d'un étudiant"""
        try:
            # Récupérer l'historique depuis la base de données
            history = self.db_service.get_student_attendance_history(student_id)
            
            # Récupérer les informations de l'étudiant
            student_data = None
            for student in self.students:
                if student['id'] == student_id:
                    student_data = student
                    break
            
            if not student_data:
                print("❌ Étudiant non trouvé")
                return
            
            # Créer le contenu du popup
            content = BoxLayout(orientation='vertical', padding=20, spacing=10)
            
            # Informations de l'étudiant
            info_label = Label(
                text=f"📅 Historique: {student_data['nom']} {student_data['prenom']} ({student_data['matricule']})",
                font_name='Arial',
                font_size=14,
                bold=True,
                color=(0.12, 0.23, 0.37, 1),
                size_hint_y=None,
                height=30
            )
            content.add_widget(info_label)
            
            # Liste de l'historique
            if history:
                scroll = ScrollView(size_hint=(1, 1))
                history_layout = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None)
                
                for record in history:
                    # Déterminer la couleur selon le statut
                    if record['statut'] == 'present':
                        status_color = (0.16, 0.65, 0.26, 1)  # Vert
                        status_text = '✅ Présent'
                    elif record['statut'] == 'absent':
                        status_color = (0.86, 0.21, 0.27, 1)  # Rouge
                        status_text = '❌ Absent'
                    elif record['statut'] == 'retard':
                        status_color = (0.93, 0.62, 0.13, 1)  # Orange
                        status_text = '⏰ Retard'
                    else:
                        status_color = (0.42, 0.46, 0.49, 1)  # Gris
                        status_text = record['statut']
                    
                    record_layout = BoxLayout(
                        orientation='horizontal',
                        size_hint_y=None,
                        height=35,
                        padding=10,
                        spacing=10
                    )
                    
                    # Fond alterné
                    bg_color = (0.97, 0.97, 0.97, 1) if history.index(record) % 2 == 0 else (1, 1, 1, 1)
                    with record_layout.canvas.before:
                        Color(*bg_color)
                        Rectangle(size=record_layout.size, pos=record_layout.pos)
                    
                    date_label = Label(
                        text=record['date'],
                        font_name='Arial',
                        font_size=11,
                        color=(0.2, 0.2, 0.2, 1),
                        size_hint_x=0.4
                    )
                    
                    status_label = Label(
                        text=status_text,
                        font_name='Arial',
                        font_size=11,
                        color=status_color,
                        size_hint_x=0.3
                    )
                    
                    method_label = Label(
                        text=f"📷 {record['methode']}",
                        font_name='Arial',
                        font_size=10,
                        color=(0.42, 0.46, 0.49, 1),
                        size_hint_x=0.3
                    )
                    
                    record_layout.add_widget(date_label)
                    record_layout.add_widget(status_label)
                    record_layout.add_widget(method_label)
                    history_layout.add_widget(record_layout)
                
                history_layout.height = len(history) * 40
                scroll.add_widget(history_layout)
                content.add_widget(scroll)
            else:
                no_history_label = Label(
                    text="Aucun historique de présence disponible",
                    font_name='Arial',
                    font_size=12,
                    color=(0.42, 0.46, 0.49, 1),
                    size_hint_y=None,
                    height=40
                )
                content.add_widget(no_history_label)
            
            # Bouton de fermeture
            close_btn = Button(
                text='Fermer',
                background_color=(0.42, 0.46, 0.49, 1.0),
                color=(1, 1, 1, 1),
                size_hint_y=None,
                height=40,
                font_name='Arial',
                font_size=12
            )
            content.add_widget(close_btn)
            
            popup = Popup(
                title='Historique de Présence',
                content=content,
                size_hint=(0.6, 0.7)
            )
            
            def dismiss_popup(instance):
                popup.dismiss()
            
            close_btn.bind(on_release=dismiss_popup)
            popup.open()
            
            print(f"📅 Historique affiché pour étudiant {student_id}: {len(history)} enregistrements")
            
        except Exception as e:
            print(f"❌ Erreur lors de l'affichage de l'historique: {e}")
