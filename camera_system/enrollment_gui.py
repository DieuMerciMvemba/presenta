"""
Interface Graphique Tkinter pour l'Enrôlement des Étudiants - UCC
Phase d'Enrôlement: Photo d'identité ➔ MTCNN ➔ Alignement ➔ ArcFace ➔ Stockage FAISS
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import sys
import os
import threading
from datetime import datetime
import numpy as np

# Ajouter le répertoire parent au path pour accéder aux modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vector_db import LocalVectorDB


class EnrollmentGUI:
    """Interface graphique pour l'enrôlement des étudiants."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Système d'Enrôlement Facial - UCC")
        self.root.geometry("700x600")
        self.root.resizable(False, False)
        
        # Configuration du style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Couleurs personnalisées
        self.primary_color = "#2c3e50"
        self.secondary_color = "#3498db"
        self.success_color = "#27ae60"
        self.warning_color = "#f39c12"
        self.error_color = "#e74c3c"
        
        # Variables
        self.matricule_var = tk.StringVar()
        self.nom_var = tk.StringVar()
        self.prenom_var = tk.StringVar()
        self.photo_path_var = tk.StringVar()
        self.photo_paths_list = []  # Liste pour stocker plusieurs photos
        
        self.create_widgets()
    
    def create_widgets(self):
        """Crée tous les widgets de l'interface."""
        
        # Header
        self.create_header()
        
        # Formulaire principal
        self.create_form()
        
        # Boutons d'action
        self.create_action_buttons()
        
        # Zone de logs
        self.create_log_area()
        
        # Footer
        self.create_footer()
    
    def create_header(self):
        """Crée l'en-tête de l'application."""
        header_frame = ttk.Frame(self.root, padding="20")
        header_frame.pack(fill=tk.X)
        
        # Titre principal
        title_label = ttk.Label(
            header_frame, 
            text="🎓 Système d'Enrôlement Facial - UCC",
            font=("Arial", 18, "bold"),
            foreground=self.primary_color
        )
        title_label.pack()
        
        # Sous-titre
        subtitle_label = ttk.Label(
            header_frame,
            text="Phase d'Enrôlement: Photo ➔ MTCNN ➔ Alignement ➔ ArcFace ➔ Stockage FAISS",
            font=("Arial", 10),
            foreground="#7f8c8d"
        )
        subtitle_label.pack(pady=(5, 0))
        
        # Séparateur
        ttk.Separator(header_frame, orient='horizontal').pack(fill='x', pady=(15, 0))
    
    def create_form(self):
        """Crée le formulaire d'enrôlement."""
        form_frame = ttk.Frame(self.root, padding="20")
        form_frame.pack(fill=tk.X)
        
        # Matricule
        self.create_form_field(
            form_frame, 
            "Matricule:", 
            self.matricule_var, 
            "Ex: UCC2024001",
            0
        )
        
        # Nom
        self.create_form_field(
            form_frame, 
            "Nom:", 
            self.nom_var, 
            "Ex: Doe",
            1
        )
        
        # Prénom
        self.create_form_field(
            form_frame, 
            "Prénom:", 
            self.prenom_var, 
            "Ex: John",
            2
        )
        
        # Photo
        photo_frame = ttk.Frame(form_frame)
        photo_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(10, 5))
        
        photo_label = ttk.Label(
            photo_frame, 
            text="Photo d'identité:",
            font=("Arial", 10, "bold")
        )
        photo_label.pack(anchor="w")
        
        photo_path_frame = ttk.Frame(photo_frame)
        photo_path_frame.pack(fill="x", pady=(5, 0))
        
        photo_entry = ttk.Entry(
            photo_path_frame, 
            textvariable=self.photo_path_var,
            font=("Arial", 10)
        )
        photo_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        browse_button = ttk.Button(
            photo_path_frame,
            text="Parcourir...",
            command=self.browse_photo,
            style="Accent.TButton"
        )
        browse_button.pack(side="right")
        
        photo_hint = ttk.Label(
            photo_frame,
            text="💡 Recommandé: 5-10 photos avec différents angles (Face, Gauche, Droite, Haut, Bas)",
            font=("Arial", 8),
            foreground="#7f8c8d"
        )
        photo_hint.pack(anchor="w", pady=(2, 0))
        
        photo_hint2 = ttk.Label(
            photo_frame,
            text="   Variation: Sourire/Sans sourire pour améliorer la reconnaissance",
            font=("Arial", 8),
            foreground="#7f8c8d"
        )
        photo_hint2.pack(anchor="w", pady=(0, 0))
        
        # Configuration du grid
        form_frame.columnconfigure(1, weight=1)
    
    def create_form_field(self, parent, label_text, variable, placeholder, row):
        """Crée un champ de formulaire."""
        label = ttk.Label(
            parent, 
            text=label_text,
            font=("Arial", 10, "bold")
        )
        label.grid(row=row, column=0, sticky="w", pady=(10, 5))
        
        entry = ttk.Entry(
            parent, 
            textvariable=variable,
            font=("Arial", 10)
        )
        entry.grid(row=row, column=1, sticky="ew", pady=(10, 5))
        
        # Placeholder
        if placeholder:
            entry.insert(0, placeholder)
            entry.bind("<FocusIn>", lambda e: self.clear_placeholder(entry, placeholder))
            entry.bind("<FocusOut>", lambda e: self.restore_placeholder(entry, placeholder, variable))
    
    def clear_placeholder(self, entry, placeholder):
        """Efface le placeholder lorsque le champ obtient le focus."""
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
    
    def restore_placeholder(self, entry, placeholder, variable):
        """Restaure le placeholder si le champ est vide."""
        if not entry.get():
            entry.insert(0, placeholder)
    
    def browse_photo(self):
        """Ouvre une boîte de dialogue pour sélectionner plusieurs photos."""
        file_paths = filedialog.askopenfilenames(
            title="Sélectionner les photos d'identité (5-10 photos recommandées)",
            filetypes=[
                ("Images", "*.jpg *.jpeg *.png"),
                ("Tous les fichiers", "*.*")
            ],
            initialdir="../Dataset"
        )
        
        if file_paths:
            self.photo_paths_list = list(file_paths)
            self.photo_path_var.set(f"{len(file_paths)} photo(s) sélectionnée(s)")
            self.log_message(f"Photos sélectionnées: {len(file_paths)}")
            for i, path in enumerate(file_paths, 1):
                self.log_message(f"  {i}. {path}")
    
    def create_action_buttons(self):
        """Crée les boutons d'action."""
        button_frame = ttk.Frame(self.root, padding="20")
        button_frame.pack(fill=tk.X)
        
        # Bouton d'enrôlement
        enroll_button = ttk.Button(
            button_frame,
            text="🚀 Enrôler l'étudiant",
            command=self.enroll_student,
            style="Success.TButton",
            width=25
        )
        enroll_button.pack(side="left", padx=(0, 10))
        
        # Bouton de réinitialisation
        reset_button = ttk.Button(
            button_frame,
            text="🔄 Réinitialiser",
            command=self.reset_form,
            width=15
        )
        reset_button.pack(side="left")
        
        # Bouton pour voir la base de données
        db_button = ttk.Button(
            button_frame,
            text="📊 Voir la base",
            command=self.show_database_info,
            width=15
        )
        db_button.pack(side="right", padx=(5, 0))
        
        # Bouton pour modifier un étudiant
        modify_button = ttk.Button(
            button_frame,
            text="✏️ Modifier",
            command=self.open_modify_window,
            width=15
        )
        modify_button.pack(side="right")
        
        # Configuration des styles personnalisés
        self.style.configure("Success.TButton", 
                           background=self.success_color, 
                           foreground="white")
        self.style.configure("Accent.TButton", 
                           background=self.secondary_color, 
                           foreground="white")
    
    def create_log_area(self):
        """Crée la zone de logs."""
        log_frame = ttk.Frame(self.root, padding="20")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # Label
        log_label = ttk.Label(
            log_frame,
            text="📋 Journal d'activité:",
            font=("Arial", 10, "bold")
        )
        log_label.pack(anchor="w")
        
        # Zone de texte avec scrollbar
        log_text = scrolledtext.ScrolledText(
            log_frame,
            height=12,
            font=("Consolas", 9),
            wrap="word"
        )
        log_text.pack(fill="both", expand=True, pady=(5, 0))
        
        self.log_text = log_text
        
        # Configuration des tags pour les couleurs
        log_text.tag_config("info", foreground="black")
        log_text.tag_config("success", foreground=self.success_color)
        log_text.tag_config("error", foreground=self.error_color)
        log_text.tag_config("warning", foreground=self.warning_color)
        log_text.tag_config("header", foreground=self.primary_color, font=("Consolas", 9, "bold"))
    
    def create_footer(self):
        """Crée le pied de page."""
        footer_frame = ttk.Frame(self.root, padding="10")
        footer_frame.pack(fill=tk.X)
        
        info_label = ttk.Label(
            footer_frame,
            text="🎓 Université Catholique du Congo (UCC) - Système de Reconnaissance Faciale",
            font=("Arial", 8),
            foreground="#7f8c8d"
        )
        info_label.pack()
    
    def log_message(self, message, level="info"):
        """Ajoute un message dans la zone de logs."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, formatted_message, level)
        self.log_text.see(tk.END)
        self.root.update()
    
    def reset_form(self):
        """Réinitialise le formulaire."""
        self.matricule_var.set("Ex: UCC2024001")
        self.nom_var.set("Ex: Doe")
        self.prenom_var.set("Ex: John")
        self.photo_path_var.set("")
        self.photo_paths_list = []
        self.log_message("Formulaire réinitialisé", "warning")
    
    def validate_form(self):
        """Valide les données du formulaire."""
        matricule = self.matricule_var.get().strip()
        nom = self.nom_var.get().strip()
        prenom = self.prenom_var.get().strip()
        
        # Vérifier que les champs ne sont pas des placeholders
        if matricule in ["Ex: UCC2024001", ""]:
            messagebox.showerror("Erreur", "Veuillez entrer un matricule valide.")
            return False
        
        if nom in ["Ex: Doe", ""]:
            messagebox.showerror("Erreur", "Veuillez entrer un nom valide.")
            return False
        
        if prenom in ["Ex: John", ""]:
            messagebox.showerror("Erreur", "Veuillez entrer un prénom valide.")
            return False
        
        if len(self.photo_paths_list) == 0:
            messagebox.showerror("Erreur", "Veuillez sélectionner au moins une photo.")
            return False
        
        # Vérifier que tous les fichiers existent
        for photo_path in self.photo_paths_list:
            if not os.path.exists(photo_path):
                messagebox.showerror("Erreur", f"Photo introuvable: {photo_path}")
                return False
        
        return True
    
    def enroll_student(self):
        """Enrôle l'étudiant avec les données du formulaire."""
        if not self.validate_form():
            return
        
        # Récupérer les données
        matricule = self.matricule_var.get().strip()
        nom = self.nom_var.get().strip()
        prenom = self.prenom_var.get().strip()
        photo_paths = self.photo_paths_list
        
        # Désactiver le bouton pendant le traitement
        self.log_message(f"Début de l'enrôlement pour {prenom} {nom}...", "header")
        self.log_message(f"Nombre de photos: {len(photo_paths)}", "info")
        
        # Exécuter dans un thread séparé pour ne pas bloquer l'interface
        thread = threading.Thread(
            target=self.execute_enrollment,
            args=(matricule, nom, prenom, photo_paths)
        )
        thread.daemon = True
        thread.start()
    
    def execute_enrollment(self, matricule, nom, prenom, photo_paths):
        """Exécute la commande d'enrôlement via subprocess dans un thread séparé."""
        try:
            # Chemin absolu du script enroll.py
            script_dir = os.path.dirname(os.path.abspath(__file__))
            enroll_script = os.path.join(script_dir, "enroll.py")
            
            # Construire la commande avec toutes les photos
            command = [
                sys.executable,
                enroll_script,
                "enroll",
                "--matricule", matricule,
                "--nom", nom,
                "--prenom", prenom,
                "--photos"
            ]
            
            # Ajouter toutes les photos à la commande (une seule fois --photos)
            command.extend(photo_paths)
            
            self.log_message(f"Commande: {' '.join(command)}", "info")
            
            # Exécuter la commande avec le bon répertoire de travail
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            
            # Lire la sortie en temps réel
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.log_message(output.strip(), "info")
            
            # Vérifier le code de retour
            return_code = process.poll()
            
            if return_code == 0:
                self.log_message("✅ Enrôlement réussi !", "success")
                messagebox.showinfo("Succès", 
                    f"L'étudiant {prenom} {nom} a été enrôlé avec succès !\n\n"
                    f"Matricule: {matricule}\n"
                    f"Photos utilisées: {len(photo_paths)}")
            else:
                error_output = process.stderr.read()
                self.log_message(f"❌ Erreur lors de l'enrôlement: {error_output}", "error")
                messagebox.showerror("Erreur", f"Erreur lors de l'enrôlement:\n{error_output}")
            
        except Exception as e:
            self.log_message(f"❌ Exception: {str(e)}", "error")
            messagebox.showerror("Erreur", f"Exception lors de l'enrôlement:\n{str(e)}")
    
    def show_database_info(self):
        """Affiche les informations de la base de données."""
        try:
            command = [sys.executable, "-c", 
                       "from vector_db import LocalVectorDB; db = LocalVectorDB(); "
                       f"print(f'Total étudiants: {db.get_student_count()}'); "
                       "print('\\nÉtudiants:'); "
                       "[print(f'  - {info[\"nom\"]} {info[\"prenom\"]} ({info[\"matricule\"]})') "
                       "for sid, info in db.metadata.items()]"]
            
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            
            output, error = process.communicate()
            
            if process.returncode == 0:
                info_text = f"📊 Base de Données\n\n{output}"
                messagebox.showinfo("Base de Données", info_text)
                self.log_message("Informations de la base de données affichées", "info")
            else:
                messagebox.showerror("Erreur", f"Erreur lors de la lecture de la base:\n{error}")
        
        except Exception as e:
            messagebox.showerror("Erreur", f"Exception: {str(e)}")
    
    def open_modify_window(self):
        """Ouvre une fenêtre pour modifier les informations d'un étudiant."""
        modify_window = tk.Toplevel(self.root)
        modify_window.title("Modifier Étudiant")
        modify_window.geometry("600x500")
        modify_window.resizable(False, False)
        
        # Frame principal
        main_frame = ttk.Frame(modify_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titre
        title_label = ttk.Label(
            main_frame,
            text="✏️ Modifier/Supprimer Étudiant",
            font=("Arial", 14, "bold"),
            foreground=self.primary_color
        )
        title_label.pack(pady=(0, 20))
        
        # Recherche par matricule
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="Matricule:", font=("Arial", 10, "bold")).pack(side="left")
        
        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=search_var, font=("Arial", 10))
        search_entry.pack(side="left", padx=(5, 5), fill=tk.X, expand=True)
        
        def search_student():
            matricule = search_var.get().strip()
            if not matricule:
                messagebox.showerror("Erreur", "Veuillez entrer un matricule.")
                return
            
            # Charger les infos de l'étudiant
            try:
                db = LocalVectorDB()
                student = db.find_student_by_matricule(matricule)
                
                if not student:
                    messagebox.showerror("Erreur", f"Étudiant avec matricule '{matricule}' non trouvé.")
                    return
                
                # Remplir les champs
                student_id = student['id']
                info = student['metadata']
                
                id_var.set(str(student_id))
                nom_var.set(info['nom'])
                prenom_var.set(info['prenom'])
                matricule_var.set(info['matricule'])
                num_photos_var.set(str(info.get('num_photos', 'N/A')))
                
                # Activer les boutons
                update_button.config(state="normal")
                add_photos_button.config(state="normal")
                delete_button.config(state="normal")
                
                self.log_message(f"Étudiant chargé: {info['prenom']} {info['nom']} ({matricule})", "info")
                
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la recherche: {e}")
        
        search_button = ttk.Button(
            search_frame,
            text="🔍 Rechercher",
            command=search_student
        )
        search_button.pack(side="right")
        
        # Séparateur
        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=15)
        
        # Informations de l'étudiant
        info_frame = ttk.LabelFrame(main_frame, text="Informations de l'étudiant", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 15))
        
        # ID (lecture seule)
        ttk.Label(info_frame, text="ID:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=5)
        id_var = tk.StringVar()
        id_entry = ttk.Entry(info_frame, textvariable=id_var, font=("Arial", 10), state="readonly")
        id_entry.grid(row=0, column=1, sticky="ew", pady=5, padx=(5, 0))
        
        # Matricule
        ttk.Label(info_frame, text="Matricule:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", pady=5)
        matricule_var = tk.StringVar()
        matricule_entry = ttk.Entry(info_frame, textvariable=matricule_var, font=("Arial", 10))
        matricule_entry.grid(row=1, column=1, sticky="ew", pady=5, padx=(5, 0))
        
        # Nom
        ttk.Label(info_frame, text="Nom:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="w", pady=5)
        nom_var = tk.StringVar()
        nom_entry = ttk.Entry(info_frame, textvariable=nom_var, font=("Arial", 10))
        nom_entry.grid(row=2, column=1, sticky="ew", pady=5, padx=(5, 0))
        
        # Prénom
        ttk.Label(info_frame, text="Prénom:", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky="w", pady=5)
        prenom_var = tk.StringVar()
        prenom_entry = ttk.Entry(info_frame, textvariable=prenom_var, font=("Arial", 10))
        prenom_entry.grid(row=3, column=1, sticky="ew", pady=5, padx=(5, 0))
        
        # Nombre de photos (lecture seule)
        ttk.Label(info_frame, text="Photos:", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky="w", pady=5)
        num_photos_var = tk.StringVar()
        num_photos_entry = ttk.Entry(info_frame, textvariable=num_photos_var, font=("Arial", 10), state="readonly")
        num_photos_entry.grid(row=4, column=1, sticky="ew", pady=5, padx=(5, 0))
        
        info_frame.columnconfigure(1, weight=1)
        
        # Boutons d'action
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 15))
        
        def execute_update():
            """Exécute la mise à jour des informations."""
            student_id = id_var.get()
            new_matricule = matricule_var.get().strip()
            new_nom = nom_var.get().strip()
            new_prenom = prenom_var.get().strip()
            
            if not student_id:
                messagebox.showerror("Erreur", "Veuillez d'abord rechercher un étudiant.")
                return
            
            try:
                db = LocalVectorDB()
                db.update_student_info(
                    int(student_id),
                    new_matricule if new_matricule else None,
                    new_nom if new_nom else None,
                    new_prenom if new_prenom else None
                )
                messagebox.showinfo("Succès", "Informations mises à jour avec succès !")
                self.log_message(f"Informations mises à jour pour l'étudiant ID={student_id}", "success")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la mise à jour: {e}")
        
        def open_add_photos():
            """Ouvre une fenêtre pour ajouter des photos."""
            add_window = tk.Toplevel(modify_window)
            add_window.title("Ajouter Photos")
            add_window.geometry("500x400")
            
            add_frame = ttk.Frame(add_window, padding="20")
            add_frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(add_frame, text="📷 Ajouter des photos", font=("Arial", 12, "bold")).pack(pady=(0, 15))
            
            photo_list_var = tk.StringVar()
            photo_list = []
            
            def browse_photos():
                files = filedialog.askopenfilenames(
                    title="Sélectionner des photos",
                    filetypes=[("Images", "*.jpg *.jpeg *.png"), ("Tous les fichiers", "*.*")],
                    initialdir="../Dataset"
                )
                if files:
                    photo_list.extend(files)
                    photo_list_var.set(f"{len(photo_list)} photo(s) sélectionnée(s)")
            
            ttk.Button(add_frame, text="Parcourir...", command=browse_photos).pack(pady=5)
            ttk.Label(add_frame, textvariable=photo_list_var).pack(pady=5)
            
            replace_var = tk.BooleanVar(value=False)
            ttk.Checkbutton(add_frame, text="Remplacer toutes les photos", variable=replace_var).pack(pady=10)
            
            def confirm_add():
                if not photo_list:
                    messagebox.showerror("Erreur", "Veuillez sélectionner au moins une photo.")
                    return
                
                student_id = id_var.get()
                matricule = matricule_var.get().strip()
                
                if not student_id:
                    messagebox.showerror("Erreur", "Veuillez d'abord rechercher un étudiant.")
                    return
                
                try:
                    # Chemin absolu du script enroll.py
                    script_dir = os.path.dirname(os.path.abspath(__file__))
                    enroll_script = os.path.join(script_dir, "enroll.py")
                    
                    # Utiliser subprocess pour appeler la commande
                    command = [
                        sys.executable,
                        enroll_script,
                        "add-photos",
                        "--matricule", matricule
                    ]
                    command.extend(["--photos"])
                    command.extend(photo_list)
                    
                    if replace_var.get():
                        command.append("--replace")
                    
                    process = subprocess.Popen(
                        command,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        cwd=os.path.dirname(os.path.abspath(__file__))
                    )
                    
                    output, error = process.communicate()
                    
                    if process.returncode == 0:
                        messagebox.showinfo("Succès", "Photos ajoutées avec succès !")
                        add_window.destroy()
                        # Recharger les infos
                        search_student()
                    else:
                        messagebox.showerror("Erreur", f"Erreur: {error}")
                        
                except Exception as e:
                    messagebox.showerror("Erreur", f"Exception: {e}")
            
            ttk.Button(add_frame, text="Confirmer", command=confirm_add).pack(pady=10)
        
        def delete_student():
            """Supprime un étudiant."""
            student_id = id_var.get()
            if not student_id:
                messagebox.showerror("Erreur", "Veuillez d'abord rechercher un étudiant.")
                return
            
            if messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir supprimer cet étudiant ?"):
                try:
                    db = LocalVectorDB()
                    # Supprimer de FAISS
                    db.index.remove_ids(np.array([int(student_id)]))
                    # Supprimer des métadonnées
                    del db.metadata[int(student_id)]
                    db.save()
                    
                    messagebox.showinfo("Succès", "Étudiant supprimé avec succès !")
                    modify_window.destroy()
                    self.log_message(f"Étudiant ID={student_id} supprimé", "warning")
                    
                    # Réinitialiser les champs
                    id_var.set("")
                    matricule_var.set("")
                    nom_var.set("")
                    prenom_var.set("")
                    num_photos_var.set("")
                    
                except Exception as e:
                    messagebox.showerror("Erreur", f"Erreur lors de la suppression: {e}")
        
        update_button = ttk.Button(button_frame, text="💾 Mettre à jour", command=execute_update, state="disabled")
        update_button.pack(side="left", padx=(0, 5))
        
        add_photos_button = ttk.Button(button_frame, text="📷 Ajouter photos", command=open_add_photos, state="disabled")
        add_photos_button.pack(side="left", padx=(0, 5))
        
        delete_button = ttk.Button(button_frame, text="🗑️ Supprimer", command=delete_student, state="disabled")
        delete_button.pack(side="right")


def main():
    """Fonction principale pour lancer l'interface graphique."""
    root = tk.Tk()
    
    # Icône de l'application (optionnel)
    try:
        # Vous pouvez ajouter une icône personnalisée ici
        pass
    except:
        pass
    
    app = EnrollmentGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
