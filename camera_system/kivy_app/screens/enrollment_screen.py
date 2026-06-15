"""
Écran d'Enrôlement pour l'application Kivy
Intègre la logique d'enrôlement existante avec sauvegarde automatique MySQL
Phase d'Enrôlement: Photo ➔ MTCNN ➔ Alignement ➔ ArcFace ➔ Stockage FAISS + MySQL
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.properties import StringProperty, ListProperty, BooleanProperty
from kivy.graphics import Color, Rectangle
from kivy.lang import Builder
from kivy.clock import Clock
import sys
import os
import threading
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.database_service import DatabaseService

# Importer les modules de reconnaissance existants
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from enroll import enroll_student
from vector_db import LocalVectorDB

# Importer la configuration
from config import Config, UCC_FACULTIES, UCC_PROMOTIONS

Builder.load_string('''
<EnrollmentScreen>:
    name: 'enrollment'
    
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
                text: '🎓 Enrôlement Étudiants - UCC'
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
                    text: '🔄 Réinitialiser'
                    background_color: 0.42, 0.46, 0.49, 1.0
                    color: 1, 1, 1, 1
                    size_hint_x: 0.5
                    font_name: 'Arial'
                    font_size: 12
                    on_release: root.reset_form()
                    
                Button:
                    text: '📊 Voir Base'
                    background_color: 0.09, 0.63, 0.72, 1.0
                    color: 1, 1, 1, 1
                    size_hint_x: 0.5
                    font_name: 'Arial'
                    font_size: 12
                    on_release: root.show_database_info()
        
        # Zone principale
        BoxLayout:
            orientation: 'horizontal'
            padding: 20
            spacing: 20
            
            # Formulaire
            ScrollView:
                BoxLayout:
                    orientation: 'vertical'
                    canvas.before:
                        Color:
                            rgba: 1, 1, 1, 1
                        Rectangle:
                            size: self.size
                            pos: self.pos
                    padding: 20
                    spacing: 15
                    size_hint_y: None
                    height: self.minimum_height
                    
                    Label:
                        text: '📝 Formulaire d\\'Enrôlement'
                        font_name: 'Arial'
                        font_size: 16
                        bold: True
                        color: 0.0, 0.2, 0.4, 1
                        size_hint_y: None
                        height: 30
                    
                    # Matricule
                    Label:
                        text: 'Matricule:'
                        font_name: 'Arial'
                        font_size: 12
                        color: 0.2, 0.2, 0.2, 1
                        size_hint_y: None
                        height: 25
                    TextInput:
                        id: matricule_input
                        hint_text: 'Ex: UCC2024001'
                        font_name: 'Arial'
                        font_size: 12
                        multiline: False
                        size_hint_y: None
                        height: 40
                    
                    # Nom
                    Label:
                        text: 'Nom:'
                        font_name: 'Arial'
                        font_size: 12
                        color: 0.2, 0.2, 0.2, 1
                        size_hint_y: None
                        height: 25
                    TextInput:
                        id: nom_input
                        hint_text: 'Ex: Doe'
                        font_name: 'Arial'
                        font_size: 12
                        multiline: False
                        size_hint_y: None
                        height: 40
                    
                    # Prénom
                    Label:
                        text: 'Prénom:'
                        font_name: 'Arial'
                        font_size: 12
                        color: 0.2, 0.2, 0.2, 1
                        size_hint_y: None
                        height: 25
                    TextInput:
                        id: prenom_input
                        hint_text: 'Ex: John'
                        font_name: 'Arial'
                        font_size: 12
                        multiline: False
                        size_hint_y: None
                        height: 40
                    
                    # Email
                    Label:
                        text: 'Email (optionnel):'
                        font_name: 'Arial'
                        font_size: 12
                        color: 0.2, 0.2, 0.2, 1
                        size_hint_y: None
                        height: 25
                    TextInput:
                        id: email_input
                        hint_text: 'Ex: john.doe@ucc.edu'
                        font_name: 'Arial'
                        font_size: 12
                        multiline: False
                        size_hint_y: None
                        height: 40
                    
                    # Téléphone
                    Label:
                        text: 'Téléphone (optionnel):'
                        font_name: 'Arial'
                        font_size: 12
                        color: 0.2, 0.2, 0.2, 1
                        size_hint_y: None
                        height: 25
                    TextInput:
                        id: telephone_input
                        hint_text: 'Ex: +243123456789'
                        font_name: 'Arial'
                        font_size: 12
                        multiline: False
                        size_hint_y: None
                        height: 40
                    
                    # Faculté
                    Label:
                        text: 'Faculté:'
                        font_name: 'Arial'
                        font_size: 12
                        color: 0.2, 0.2, 0.2, 1
                        size_hint_y: None
                        height: 25
                    Spinner:
                        id: faculte_spinner
                        text: 'Sélectionner une faculté'
                        font_name: 'Arial'
                        font_size: 12
                        size_hint_y: None
                        height: 40
                    
                    # Promotion
                    Label:
                        text: 'Promotion:'
                        font_name: 'Arial'
                        font_size: 12
                        color: 0.2, 0.2, 0.2, 1
                        size_hint_y: None
                        height: 25
                    Spinner:
                        id: promotion_spinner
                        text: 'Sélectionner une promotion'
                        font_name: 'Arial'
                        font_size: 12
                        size_hint_y: None
                        height: 40
                    
                    # Photos
                    Label:
                        text: '📷 Photos d\\'identité (5-10 recommandées):'
                        font_name: 'Arial'
                        font_size: 12
                        bold: True
                        color: 0.0, 0.2, 0.4, 1
                        size_hint_y: None
                        height: 25
                    
                    Button:
                        text: '📁 Sélectionner Photos'
                        background_color: 0.29, 0.56, 0.89, 1.0
                        color: 1, 1, 1, 1
                        font_name: 'Arial'
                        font_size: 12
                        size_hint_y: None
                        height: 40
                        on_release: root.select_photos()
                    
                    Label:
                        id: photo_count_label
                        text: '0 photo(s) sélectionnée(s)'
                        font_name: 'Arial'
                        font_size: 11
                        color: 0.4, 0.4, 0.4, 1
                        size_hint_y: None
                        height: 25
                    
                    Label:
                        text: '💡 Recommandé: 5-10 photos avec différents angles'
                        font_name: 'Arial'
                        font_size: 10
                        color: 0.6, 0.6, 0.6, 1
                        size_hint_y: None
                        height: 20
                    
                    # Zone d'affichage de la commande
                    BoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: 25
                        spacing: 10
                        
                        Label:
                            text: '🔧 Commande à exécuter:'
                            font_name: 'Arial'
                            font_size: 11
                            bold: True
                            color: 0.0, 0.2, 0.4, 1
                            size_hint_x: 0.7
                        
                        Button:
                            text: '📋 Copier'
                            background_color: 0.29, 0.56, 0.89, 1.0
                            color: 1, 1, 1, 1
                            font_name: 'Arial'
                            font_size: 10
                            size_hint_x: 0.3
                            size_hint_y: None
                            height: 25
                            on_release: root.copy_command()
                    
                    ScrollView:
                        size_hint_y: None
                        height: 60
                        
                        Label:
                            id: command_display
                            text: 'Aucune commande générée'
                            font_name: 'Arial'
                            font_size: 9
                            color: 0.4, 0.4, 0.4, 1
                            size_hint_y: None
                            height: self.texture_size[1]
                            text_size: self.width, None
                    
                    Label:
                        text: '   (Face, Gauche, Droite, Haut, Bas, Sourire/Sans sourire)'
                        font_name: 'Arial'
                        font_size: 10
                        color: 0.6, 0.6, 0.6, 1
                        size_hint_y: None
                        height: 20
                    
                    # Bouton d'enrôlement
                    Button:
                        text: '🚀 Enrôler l\\'Étudiant'
                        background_color: 0.16, 0.65, 0.26, 1.0
                        color: 1, 1, 1, 1
                        font_name: 'Arial'
                        font_size: 14
                        bold: True
                        size_hint_y: None
                        height: 50
                        on_release: root.enroll_student()
                    
                    # Espaceur
                    BoxLayout:
                        size_hint_y: 1
            
            # Zone de logs
            BoxLayout:
                orientation: 'vertical'
                canvas.before:
                    Color:
                        rgba: 1, 1, 1, 1
                    Rectangle:
                        size: self.size
                        pos: self.pos
                padding: 20
                spacing: 10
                
                Label:
                    text: '📋 Journal d\\'Activité'
                    font_name: 'Arial'
                    font_size: 14
                    bold: True
                    color: 0.0, 0.2, 0.4, 1
                    size_hint_y: None
                    height: 30
                
                ScrollView:
                    id: log_scroll
                    BoxLayout:
                        id: log_container
                        orientation: 'vertical'
                        spacing: 5
                        size_hint_y: None
                        height: self.minimum_height
''')

class EnrollmentScreen(Screen):
    """Écran d'Enrôlement avec intégration MySQL"""
    
    photo_paths = ListProperty([])
    is_processing = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super(EnrollmentScreen, self).__init__(**kwargs)
        self.db_service = DatabaseService(
            host='localhost',
            database='ucc_face_recognition',
            user='root',
            password='admin123',
            port=3306
        )
        
        # Ne pas changer le répertoire de travail pour éviter les problèmes de chemins relatifs
    
    def on_enter(self):
        """Appelé lorsque l'écran est affiché"""
        self.log_message("🎓 Écran d'Enrôlement initialisé", "header")
        self.log_message("Pipeline: Photos ➔ MTCNN ➔ Alignement ➔ ArcFace ➔ Stockage FAISS + MySQL", "info")
        
        # Charger les facultés et promotions depuis MySQL
        self.load_faculties_and_promotions()
    
    def load_faculties_and_promotions(self):
        """Charge les facultés et promotions depuis la configuration dans les spinners"""
        try:
            # Charger les facultés depuis la configuration
            self.ids.faculte_spinner.values = UCC_FACULTIES
            self.log_message(f"✅ {len(UCC_FACULTIES)} faculté(s) chargée(s) depuis la configuration", "info")
            
            # Charger les promotions depuis la configuration
            self.ids.promotion_spinner.values = UCC_PROMOTIONS
            self.log_message(f"✅ {len(UCC_PROMOTIONS)} promotion(s) chargée(s) depuis la configuration", "info")
                
        except Exception as e:
            self.log_message(f"❌ Erreur lors du chargement des données: {e}", "error")
    
    def select_photos(self):
        """Ouvre un sélecteur de fichiers pour choisir les photos"""
        content = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # FileChooser avec sélection multiple activée
        # Utiliser le répertoire Dataset depuis la configuration
        dataset_path = Config.DATASET_PATH
        if not os.path.exists(dataset_path):
            dataset_path = Config.PROJECT_ROOT
        
        self.log_message(f"📁 FileChooser - Dataset path (Config): {dataset_path}", "info")
        self.log_message(f"📁 FileChooser - Dataset exists: {os.path.exists(dataset_path)}", "info")
        
        filechooser = FileChooserListView(
            path=dataset_path,
            filters=['*.jpg', '*.jpeg', '*.png'],
            multiselect=True
        )
        content.add_widget(filechooser)
        
        # Boutons
        btn_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=40)
        
        cancel_btn = Button(text='Annuler', background_color=(0.42, 0.46, 0.49, 1.0), color=(1, 1, 1, 1))
        select_btn = Button(text='Sélectionner', background_color=(0.16, 0.65, 0.26, 1.0), color=(1, 1, 1, 1))
        
        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(select_btn)
        content.add_widget(btn_layout)
        
        popup = Popup(
            title='Sélectionner Photos (5-10 recommandées)',
            content=content,
            size_hint=(0.8, 0.7)
        )
        
        def dismiss_popup(instance):
            popup.dismiss()
        
        def confirm_selection(instance):
            selected_files = filechooser.selection
            if selected_files:
                self.photo_paths = list(selected_files)
                self.ids.photo_count_label.text = f'{len(selected_files)} photo(s) sélectionnée(s)'
                self.log_message(f'Photos sélectionnées: {len(selected_files)}', "info")
                for i, path in enumerate(selected_files, 1):
                    self.log_message(f'  {i}. {os.path.basename(path)}', "info")
            popup.dismiss()
        
        cancel_btn.bind(on_release=dismiss_popup)
        select_btn.bind(on_release=confirm_selection)
        
        popup.open()
    
    def reset_form(self):
        """Réinitialise le formulaire"""
        self.ids.matricule_input.text = ''
        self.ids.nom_input.text = ''
        self.ids.prenom_input.text = ''
        self.ids.email_input.text = ''
        self.ids.telephone_input.text = ''
        self.photo_paths = []
        self.ids.photo_count_label.text = '0 photo(s) sélectionnée(s)'
        
        # NE PAS vider les logs automatiquement - l'admin le fera seul
        # self.ids.log_container.clear_widgets()
        
        self.log_message("Formulaire réinitialisé", "warning")
    
    def validate_form(self):
        """Valide les données du formulaire"""
        matricule = self.ids.matricule_input.text.strip()
        nom = self.ids.nom_input.text.strip()
        prenom = self.ids.prenom_input.text.strip()
        
        if not matricule:
            self.log_message("❌ Erreur: Matricule requis", "error")
            return False
        
        if not nom:
            self.log_message("❌ Erreur: Nom requis", "error")
            return False
        
        if not prenom:
            self.log_message("❌ Erreur: Prénom requis", "error")
            return False
        
        if len(self.photo_paths) == 0:
            self.log_message("❌ Erreur: Au moins une photo requise", "error")
            return False
        
        # Vérifier que tous les fichiers existent
        for photo_path in self.photo_paths:
            if not os.path.exists(photo_path):
                self.log_message(f"❌ Erreur: Photo introuvable {photo_path}", "error")
                return False
        
        return True
    
    def enroll_student(self):
        """Enrôle l'étudiant avec les données du formulaire"""
        if not self.validate_form():
            return
        
        if self.is_processing:
            self.log_message("⚠️ Traitement en cours, veuillez patienter...", "warning")
            return
        
        # Récupérer les données
        matricule = self.ids.matricule_input.text.strip()
        nom = self.ids.nom_input.text.strip()
        prenom = self.ids.prenom_input.text.strip()
        email = self.ids.email_input.text.strip() or None
        telephone = self.ids.telephone_input.text.strip() or None
        
        # Récupérer les IDs depuis les spinners
        faculte_name = self.ids.faculte_spinner.text
        promotion_name = self.ids.promotion_spinner.text
        faculte_id = self.get_faculty_id_by_name(faculte_name)
        promotion_id = self.get_promotion_id_by_name(promotion_name)
        
        # Validation des IDs
        if faculte_id is None:
            self.log_message("❌ Veuillez sélectionner une faculté", "error")
            return
        
        if promotion_id is None:
            self.log_message("❌ Veuillez sélectionner une promotion", "error")
            return
        
        photo_paths = self.photo_paths
        
        self.is_processing = True
        self.log_message(f"Début de l'enrôlement pour {prenom} {nom}...", "header")
        self.log_message(f"Nombre de photos: {len(photo_paths)}", "info")
        self.log_message(f"Faculté: {faculte_name} (ID: {faculte_id})", "info")
        self.log_message(f"Promotion: {promotion_name} (ID: {promotion_id})", "info")
        
        # Exécuter dans un thread séparé pour ne pas bloquer l'interface
        thread = threading.Thread(
            target=self.execute_enrollment,
            args=(matricule, nom, prenom, email, telephone, faculte_id, promotion_id, photo_paths)
        )
        thread.daemon = True
        thread.start()
    
    def get_faculty_id_by_name(self, faculty_name):
        """Récupère l'ID de la faculté par son nom depuis la configuration"""
        if faculty_name == "Sélectionner une faculté":
            return None
        try:
            # Utiliser l'index + 1 comme ID (basé sur la configuration)
            if faculty_name in UCC_FACULTIES:
                return UCC_FACULTIES.index(faculty_name) + 1
        except Exception as e:
            self.log_message(f"❌ Erreur lors de la récupération de l'ID de faculté: {e}", "error")
        return None
    
    def get_promotion_id_by_name(self, promotion_name):
        """Récupère l'ID de la promotion par son nom depuis la configuration"""
        if promotion_name == "Sélectionner une promotion":
            return None
        try:
            # Utiliser l'index + 1 comme ID (basé sur la configuration)
            if promotion_name in UCC_PROMOTIONS:
                return UCC_PROMOTIONS.index(promotion_name) + 1
        except Exception as e:
            self.log_message(f"❌ Erreur lors de la récupération de l'ID de promotion: {e}", "error")
        return None
    
    def execute_enrollment(self, matricule, nom, prenom, email, telephone, faculte_id, promotion_id, photo_paths):
        """Exécute l'enrôlement via subprocess comme dans enrollment_gui.py"""
        try:
            # Utiliser les chemins depuis la configuration
            project_root = Config.PROJECT_ROOT
            enroll_script = Config.get_enroll_script_path()
            python_exe = Config.get_python_executable()
            
            self.log_message(f"📁 Répertoire de travail actuel: {os.getcwd()}", "info")
            self.log_message(f"📁 Racine du projet (Config): {project_root}", "info")
            self.log_message(f"📁 Script enroll.py: {enroll_script}", "info")
            self.log_message(f"📁 Vérification existence enroll.py: {os.path.exists(enroll_script)}", "info")
            self.log_message(f"🐍 Python utilisé: {python_exe}", "info")
            
            # Construire la commande avec le Python détecté
            command = [
                python_exe,
                enroll_script,
                "enroll",
                "--matricule", matricule,
                "--nom", nom,
                "--prenom", prenom,
                "--faculte-id", str(faculte_id),
                "--promotion-id", str(promotion_id)
            ]
            
            # Ajouter email et téléphone si disponibles (AVANT --photos)
            if email:
                command.extend(["--email", email])
            if telephone:
                command.extend(["--telephone", telephone])
            
            # Ajouter --photos après les autres options
            command.append("--photos")
            
            # Utiliser des chemins absolus pour éviter les erreurs de résolution
            absolute_photo_paths = []
            for photo_path in photo_paths:
                self.log_message(f"📷 Photo originale: {photo_path}", "info")
                self.log_message(f"📷 Existe: {os.path.exists(photo_path)}", "info")
                # Convertir en chemin absolu
                abs_path = os.path.abspath(photo_path)
                absolute_photo_paths.append(abs_path)
                self.log_message(f"📷 Photo absolue: {abs_path}", "info")
            
            command.extend(absolute_photo_paths)
            
            # Afficher la commande exacte dans l'interface UI
            command_str = ' '.join(command)
            self.ids.command_display.text = command_str
            
            # Afficher la commande exacte dans les logs comme dans enrollment_gui.py
            self.log_message(f"🔧 Commande complète: {command_str}", "info")
            
            # ÉTAPE 1: Enrôlement via subprocess
            self.log_message("ÉTAPE 1: Traitement des images (MTCNN ➔ Alignement ➔ ArcFace)...", "info")
            self.log_message("🔧 Démarrage du subprocess...", "info")
            
            # Exécuter la commande avec subprocess
            import subprocess
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # Combiner stderr dans stdout pour voir tous les logs
                text=True,
                bufsize=1,
                universal_newlines=True,
                cwd=project_root,
                env=os.environ.copy()  # Utiliser l'environnement actuel
            )
            
            self.log_message(f"🔧 Processus démarré (PID: {process.pid})", "info")
            
            # Lire la sortie en temps réel
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    # Afficher chaque ligne du log
                    line = output.strip()
                    if line:
                        self.log_message(f"  {line}", "info")
            
            # Vérifier le code de retour
            return_code = process.poll()
            self.log_message(f"🔧 Code de retour: {return_code}", "info")
            
            # Lire les erreurs s'il y en a
            if return_code != 0:
                self.log_message(f"❌ Erreur lors de l'exécution (code: {return_code})", "error")
            
            if return_code == 0:
                self.log_message("✅ ÉTAPE 1: Enrôlement FAISS réussi !", "success")
                
                # ÉTAPE 2: Sauvegarde dans MySQL
                self.log_message("ÉTAPE 2: Sauvegarde dans MySQL...", "info")
                
                # Récupérer les informations de l'étudiant depuis FAISS
                db = LocalVectorDB()
                student = db.find_student_by_matricule(matricule)
                
                if student:
                    student_id = student['id']
                    metadata = student['metadata']
                    num_photos = metadata.get('num_photos', len(photo_paths))
                    
                    # Insérer dans MySQL
                    mysql_student_id = self.db_service.add_student(
                        matricule=matricule,
                        nom=nom,
                        prenom=prenom,
                        email=email,
                        telephone=telephone,
                        faculte_id=faculte_id,
                        promotion_id=promotion_id
                    )
                    
                    if mysql_student_id:
                        self.log_message(f"✅ ÉTAPE 2: Étudiant sauvegardé dans MySQL (ID: {mysql_student_id})", "success")
                    else:
                        self.log_message("⚠️ ÉTAPE 2: Étudiant existe déjà dans MySQL", "warning")
                else:
                    self.log_message("❌ Erreur: Étudiant non trouvé dans FAISS après enrôlement", "error")
                
                self.log_message("=" * 50, "header")
                self.log_message("🎉 ENRÔLEMENT TERMINÉ AVEC SUCCÈS !", "success")
                self.log_message(f"Matricule: {matricule}", "info")
                self.log_message(f"Nom: {nom}", "info")
                self.log_message(f"Prénom: {prenom}", "info")
                self.log_message(f"Photos utilisées: {len(photo_paths)}", "info")
                self.log_message("Stockage: FAISS + MySQL", "info")
                self.log_message("=" * 50, "header")
                
                # Afficher un popup de succès
                Clock.schedule_once(lambda dt: self.show_success_popup(matricule, nom, prenom), 0.5)
                
                # Réinitialiser le formulaire après succès
                Clock.schedule_once(lambda dt: self.reset_form(), 2)
            else:
                error_output = process.stderr.read()
                self.log_message(f"❌ Erreur lors de l'enrôlement: {error_output}", "error")
                # Afficher un popup d'erreur
                Clock.schedule_once(lambda dt: self.show_error_popup(str(error_output)), 0.5)
            
        except Exception as e:
            self.log_message(f"❌ Exception: {str(e)}", "error")
            import traceback
            self.log_message(f"Détails: {traceback.format_exc()}", "error")
            # Afficher un popup d'erreur
            Clock.schedule_once(lambda dt: self.show_error_popup(str(e)), 0.5)
        
        finally:
            self.is_processing = False
    
    def show_success_popup(self, matricule, nom, prenom):
        """Affiche un popup de succès après l'enrôlement"""
        content = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        label = Label(
            text=f"✅ Enrôlement réussi !\n\nMatricule: {matricule}\nNom: {nom}\nPrénom: {prenom}",
            font_size=16,
            color=(0, 0.5, 0, 1),
            halign='center'
        )
        content.add_widget(label)
        
        btn = Button(
            text='OK',
            size_hint_y=None,
            height=40,
            background_color=(0.16, 0.65, 0.26, 1.0),
            color=(1, 1, 1, 1)
        )
        content.add_widget(btn)
        
        popup = Popup(
            title='Succès',
            content=content,
            size_hint=(0.4, 0.3),
            auto_dismiss=True
        )
        
        btn.bind(on_release=popup.dismiss)
        popup.open()
    
    def show_error_popup(self, error_message):
        """Affiche un popup d'erreur après l'échec de l'enrôlement"""
        content = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        label = Label(
            text=f"❌ Erreur lors de l'enrôlement\n\n{error_message[:200]}...",
            font_size=14,
            color=(0.8, 0, 0, 1),
            halign='center'
        )
        content.add_widget(label)
        
        btn = Button(
            text='OK',
            size_hint_y=None,
            height=40,
            background_color=(0.8, 0.2, 0.2, 1.0),
            color=(1, 1, 1, 1)
        )
        content.add_widget(btn)
        
        popup = Popup(
            title='Erreur',
            content=content,
            size_hint=(0.4, 0.3),
            auto_dismiss=True
        )
        
        btn.bind(on_release=popup.dismiss)
        popup.open()
    
    def copy_command(self):
        """Copie la commande affichée dans le presse-papiers"""
        try:
            command_text = self.ids.command_display.text
            if command_text and command_text != 'Aucune commande générée':
                # Utiliser le presse-papiers système
                from kivy.core.clipboard import Clipboard
                Clipboard.copy(command_text)
                self.log_message("✅ Commande copiée dans le presse-papiers", "success")
            else:
                self.log_message("⚠️ Aucune commande à copier", "warning")
        except Exception as e:
            self.log_message(f"❌ Erreur lors de la copie: {e}", "error")
    
    def show_database_info(self):
        """Affiche les informations de la base de données"""
        try:
            # Informations FAISS
            db = LocalVectorDB()
            faiss_count = db.get_student_count()
            
            # Informations MySQL
            mysql_count = self.db_service.get_student_count()
            
            info_text = f"📊 Base de Données\n\n"
            info_text += f"FAISS (Reconnaissance): {faiss_count} étudiants\n"
            info_text += f"MySQL (Métadonnées): {mysql_count} étudiants\n"
            
            if mysql_count > 0:
                info_text += f"\nDerniers étudiants MySQL:\n"
                students = self.db_service.get_all_students()
                for student in students[-5:]:  # Derniers 5
                    info_text += f"  - {student['nom']} {student['prenom']} ({student['matricule']})\n"
            
            content = BoxLayout(orientation='vertical', padding=20, spacing=10)
            label = Label(text=info_text, font_name='Arial', font_size=12, color=(0.2, 0.2, 0.2, 1))
            content.add_widget(label)
            
            btn = Button(text='Fermer', size_hint_y=None, height=40, background_color=(0.42, 0.46, 0.49, 1.0), color=(1, 1, 1, 1))
            content.add_widget(btn)
            
            popup = Popup(title='Base de Données', content=content, size_hint=(0.5, 0.5))
            
            def dismiss_popup(instance):
                popup.dismiss()
            
            btn.bind(on_release=dismiss_popup)
            popup.open()
            
            self.log_message("Informations de la base de données affichées", "info")
            
        except Exception as e:
            self.log_message(f"Erreur lors de l'affichage de la base: {e}", "error")
    
    def log_message(self, message, level="info"):
        """Ajoute un message dans la zone de logs"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Couleurs selon le niveau
        colors = {
            "header": (0.0, 0.2, 0.4, 1.0),
            "info": (0.2, 0.2, 0.2, 1.0),
            "success": (0.16, 0.65, 0.26, 1.0),
            "warning": (0.8, 0.5, 0.0, 1.0),
            "error": (0.86, 0.21, 0.27, 1.0)
        }
        
        color = colors.get(level, (0.2, 0.2, 0.2, 1.0))
        
        # Utiliser Clock.schedule_once pour créer le widget dans le thread principal
        def add_log_label(dt):
            log_label = Label(
                text=f"[{timestamp}] {message}",
                font_size=10,
                color=color,
                size_hint_y=None,
                height=20,
                text_size=(None, 20)
            )
            self.ids.log_container.add_widget(log_label)
        
        Clock.schedule_once(add_log_label)
