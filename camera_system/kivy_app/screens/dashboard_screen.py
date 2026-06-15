"""
Écran Dashboard pour l'application Kivy
Tableau de bord avec statistiques et graphiques
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
from kivy.properties import NumericProperty, StringProperty, ListProperty
from kivy.lang import Builder
from kivy.clock import Clock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from services.database_service import DatabaseService
from services.chart_service import ChartService

Builder.load_string('''
<DashboardScreen>:
    name: 'dashboard'
    
    BoxLayout:
        orientation: 'vertical'
        canvas.before:
            Color:
                rgba: 0.97, 0.97, 0.99, 1.0  # Fond très léger
            Rectangle:
                size: self.size
                pos: self.pos
        
        # Header
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: 70
            padding: 25
            spacing: 15
            canvas.before:
                Color:
                    rgba: 0.12, 0.23, 0.37, 1.0  # UCC_BLUE_DARK
                Rectangle:
                    size: self.size
                    pos: self.pos
                # Bordure inférieure
                Color:
                    rgba: 0.29, 0.45, 0.69, 0.5
                Rectangle:
                    size: self.width, 2
                    pos: self.x, self.y
            
            Label:
                text: '🎓 Tableau de Bord - UCC'
                font_name: 'Arial'
                font_size: 22
                bold: True
                color: 1, 1, 1, 1
                size_hint_x: 0.7
                
            BoxLayout:
                orientation: 'horizontal'
                size_hint_x: 0.3
                spacing: 15
                
                Label:
                    text: '📅 ' + root.current_date
                    font_name: 'Arial'
                    font_size: 14
                    color: 0.9, 0.95, 1, 1
                    size_hint_x: 0.5
        
        # Contenu principal
        BoxLayout:
            orientation: 'horizontal'
            padding: 20
            spacing: 20
            
            # Zone principale
            BoxLayout:
                orientation: 'vertical'
                spacing: 20
                size_hint_x: 0.75
                
                # Cartes de statistiques
                GridLayout:
                    cols: 5
                    spacing: 20
                    size_hint_y: None
                    height: 160
                    
                    # Carte 1: Total Étudiants
                    BoxLayout:
                        orientation: 'vertical'
                        canvas.before:
                            Color:
                                rgba: 1, 1, 1, 1
                            Rectangle:
                                size: self.size
                                pos: self.pos
                            # Ombre subtile
                            Color:
                                rgba: 0, 0, 0, 0.08
                            Rectangle:
                                size: self.size
                                pos: self.pos[0] + 3, self.pos[1] - 3
                            # Bordure supérieure colorée
                            Color:
                                rgba: 0.29, 0.56, 0.89, 1.0  # ACCENT_BLUE
                            Rectangle:
                                size: self.width, 4
                                pos: self.x, self.top - 4
                        padding: 20
                        spacing: 8
                        
                        Label:
                            text: '👥'
                            font_size: 36
                            size_hint_y: None
                            height: 45
                            halign: 'center'
                            
                        Label:
                            text: str(root.total_students)
                            font_name: 'Arial'
                            font_size: 32
                            bold: True
                            color: 0.12, 0.23, 0.37, 1  # UCC_BLUE_DARK
                            size_hint_y: None
                            height: 40
                            halign: 'center'
                            
                        Label:
                            text: 'Total Étudiants'
                            font_name: 'Arial'
                            font_size: 12
                            color: 0.42, 0.46, 0.49, 1  # TEXT_SECONDARY
                            size_hint_y: None
                            height: 25
                            halign: 'center'
                    
                    # Carte 2: Présents Aujourd'hui
                    BoxLayout:
                        orientation: 'vertical'
                        canvas.before:
                            Color:
                                rgba: 1, 1, 1, 1
                            Rectangle:
                                size: self.size
                                pos: self.pos
                            Color:
                                rgba: 0, 0, 0, 0.08
                            Rectangle:
                                size: self.size
                                pos: self.pos[0] + 3, self.pos[1] - 3
                            Color:
                                rgba: 0.16, 0.65, 0.26, 1.0  # ACCENT_GREEN
                            Rectangle:
                                size: self.width, 4
                                pos: self.x, self.top - 4
                        padding: 20
                        spacing: 8
                        
                        Label:
                            text: '✅'
                            font_size: 36
                            size_hint_y: None
                            height: 45
                            halign: 'center'
                            
                        Label:
                            text: str(root.present_today)
                            font_name: 'Arial'
                            font_size: 32
                            bold: True
                            color: 0.16, 0.65, 0.26, 1  # ACCENT_GREEN
                            size_hint_y: None
                            height: 40
                            halign: 'center'
                            
                        Label:
                            text: "Présents Aujourd'hui"
                            font_name: 'Arial'
                            font_size: 12
                            color: 0.42, 0.46, 0.49, 1  # TEXT_SECONDARY
                            size_hint_y: None
                            height: 25
                            halign: 'center'
                    
                    # Carte 3: Absents Aujourd'hui
                    BoxLayout:
                        orientation: 'vertical'
                        canvas.before:
                            Color:
                                rgba: 1, 1, 1, 1
                            Rectangle:
                                size: self.size
                                pos: self.pos
                            Color:
                                rgba: 0, 0, 0, 0.08
                            Rectangle:
                                size: self.size
                                pos: self.pos[0] + 3, self.pos[1] - 3
                            Color:
                                rgba: 0.86, 0.21, 0.27, 1.0  # ACCENT_RED
                            Rectangle:
                                size: self.width, 4
                                pos: self.x, self.top - 4
                        padding: 20
                        spacing: 8
                        
                        Label:
                            text: '❌'
                            font_size: 36
                            size_hint_y: None
                            height: 45
                            halign: 'center'
                            
                        Label:
                            text: str(root.absent_today)
                            font_name: 'Arial'
                            font_size: 32
                            bold: True
                            color: 0.86, 0.21, 0.27, 1  # ACCENT_RED
                            size_hint_y: None
                            height: 40
                            halign: 'center'
                            
                        Label:
                            text: "Absents Aujourd'hui"
                            font_name: 'Arial'
                            font_size: 12
                            color: 0.42, 0.46, 0.49, 1  # TEXT_SECONDARY
                            size_hint_y: None
                            height: 25
                            halign: 'center'
                    
                    # Carte 4: Taux de Présence
                    BoxLayout:
                        orientation: 'vertical'
                        canvas.before:
                            Color:
                                rgba: 1, 1, 1, 1
                            Rectangle:
                                size: self.size
                                pos: self.pos
                            Color:
                                rgba: 0, 0, 0, 0.08
                            Rectangle:
                                size: self.size
                                pos: self.pos[0] + 3, self.pos[1] - 3
                            Color:
                                rgba: 0.09, 0.64, 0.72, 1.0  # ACCENT_CYAN
                            Rectangle:
                                size: self.width, 4
                                pos: self.x, self.top - 4
                        padding: 20
                        spacing: 8
                        
                        Label:
                            text: '📊'
                            font_size: 36
                            size_hint_y: None
                            height: 45
                            halign: 'center'
                            
                        Label:
                            text: str(root.attendance_rate) + '%'
                            font_name: 'Arial'
                            font_size: 32
                            bold: True
                            color: 0.09, 0.64, 0.72, 1  # ACCENT_CYAN
                            size_hint_y: None
                            height: 40
                            halign: 'center'
                            
                        Label:
                            text: 'Taux de Présence'
                            font_name: 'Arial'
                            font_size: 12
                            color: 0.42, 0.46, 0.49, 1  # TEXT_SECONDARY
                            size_hint_y: None
                            height: 25
                            halign: 'center'
                    
                    # Carte 5: Retards Aujourd'hui
                    BoxLayout:
                        orientation: 'vertical'
                        canvas.before:
                            Color:
                                rgba: 1, 1, 1, 1
                            Rectangle:
                                size: self.size
                                pos: self.pos
                            Color:
                                rgba: 0, 0, 0, 0.08
                            Rectangle:
                                size: self.size
                                pos: self.pos[0] + 3, self.pos[1] - 3
                            Color:
                                rgba: 0.95, 0.61, 0.07, 1.0  # ACCENT_ORANGE
                            Rectangle:
                                size: self.width, 4
                                pos: self.x, self.top - 4
                        padding: 20
                        spacing: 8
                        
                        Label:
                            text: '⏰'
                            font_size: 36
                            size_hint_y: None
                            height: 45
                            halign: 'center'
                            
                        Label:
                            text: str(root.late_today)
                            font_name: 'Arial'
                            font_size: 32
                            bold: True
                            color: 0.95, 0.61, 0.07, 1  # ACCENT_ORANGE
                            size_hint_y: None
                            height: 40
                            halign: 'center'
                            
                        Label:
                            text: "Retards Aujourd'hui"
                            font_name: 'Arial'
                            font_size: 12
                            color: 0.42, 0.46, 0.49, 1  # TEXT_SECONDARY
                            size_hint_y: None
                            height: 25
                            halign: 'center'
                
                # Zone de contenu supplémentaire
                BoxLayout:
                    orientation: 'vertical'
                    canvas.before:
                        Color:
                            rgba: 1, 1, 1, 1
                        Rectangle:
                            size: self.size
                            pos: self.pos
                        # Ombre subtile
                        Color:
                            rgba: 0, 0, 0, 0.05
                        Rectangle:
                            size: self.size
                            pos: self.pos[0] + 2, self.pos[1] - 2
                    padding: 25
                    spacing: 15
                    
                    Label:
                        text: '📈 Statistiques de Présence'
                        font_name: 'Arial'
                        font_size: 18
                        bold: True
                        color: 0.12, 0.23, 0.37, 1  # UCC_BLUE_DARK
                        size_hint_y: None
                        height: 30
                    
                    # Zone de graphiques professionnels
                    ScrollView:
                        size_hint_y: 1
                        
                        BoxLayout:
                            orientation: 'vertical'
                            size_hint_y: None
                            height: self.minimum_height
                            spacing: 20
                            padding: 10
                            
                            # Graphique 1: Tendance de présence
                            BoxLayout:
                                orientation: 'vertical'
                                size_hint_y: None
                                height: 350
                                canvas.before:
                                    Color:
                                        rgba: 1, 1, 1, 1
                                    Rectangle:
                                        size: self.size
                                        pos: self.pos
                                padding: 15
                                spacing: 10
                                
                                Label:
                                    text: '📊 Tendance de Présence - 7 Derniers Jours'
                                    font_name: 'Arial'
                                    font_size: 14
                                    bold: True
                                    color: 0.12, 0.23, 0.37, 1
                                    size_hint_y: None
                                    height: 25
                                
                                Image:
                                    source: root.trend_chart_path if root.trend_chart_path else ''
                                    size_hint_y: None
                                    height: 300
                                    allow_stretch: True
                            
                            # Graphique 2: Taux de présence
                            BoxLayout:
                                orientation: 'vertical'
                                size_hint_y: None
                                height: 350
                                canvas.before:
                                    Color:
                                        rgba: 1, 1, 1, 1
                                    Rectangle:
                                        size: self.size
                                        pos: self.pos
                                padding: 15
                                spacing: 10
                                
                                Label:
                                    text: '📈 Taux de Présence Quotidien'
                                    font_name: 'Arial'
                                    font_size: 14
                                    bold: True
                                    color: 0.12, 0.23, 0.37, 1
                                    size_hint_y: None
                                    height: 25
                                
                                Image:
                                    source: root.rate_chart_path if root.rate_chart_path else ''
                                    size_hint_y: None
                                    height: 300
                                    allow_stretch: True
                            
                            # Graphique 3: Distribution horaire
                            BoxLayout:
                                orientation: 'vertical'
                                size_hint_y: None
                                height: 350
                                canvas.before:
                                    Color:
                                        rgba: 1, 1, 1, 1
                                    Rectangle:
                                        size: self.size
                                        pos: self.pos
                                padding: 15
                                spacing: 10
                                
                                Label:
                                    text: '⏰ Distribution Horaire des Présences'
                                    font_name: 'Arial'
                                    font_size: 14
                                    bold: True
                                    color: 0.12, 0.23, 0.37, 1
                                    size_hint_y: None
                                    height: 25
                                
                                Image:
                                    source: root.hourly_chart_path if root.hourly_chart_path else ''
                                    size_hint_y: None
                                    height: 300
                                    allow_stretch: True
            
            # Sidebar
            BoxLayout:
                orientation: 'vertical'
                size_hint_x: 0.25
                canvas.before:
                    Color:
                        rgba: 1, 1, 1, 1
                    Rectangle:
                        size: self.size
                        pos: self.pos
                    # Ombre subtile
                    Color:
                        rgba: 0, 0, 0, 0.05
                    Rectangle:
                        size: self.size
                        pos: self.pos[0] + 2, self.pos[1] - 2
                padding: 20
                spacing: 15
                
                Label:
                    text: '⚡ Actions Rapides'
                    font_name: 'Arial'
                    font_size: 16
                    bold: True
                    color: 0.12, 0.23, 0.37, 1  # UCC_BLUE_DARK
                    size_hint_y: None
                    height: 30
                
                BoxLayout:
                    orientation: 'vertical'
                    spacing: 10
                    
                    Button:
                        text: '👥 Ajouter Étudiant'
                        background_color: 0.29, 0.56, 0.89, 1.0  # ACCENT_BLUE
                        color: 1, 1, 1, 1
                        size_hint_y: None
                        height: 45
                        font_name: 'Arial'
                        font_size: 12
                        on_release: root.go_to_students()
                        
                    Button:
                        text: '📸 Démarrer Pointage'
                        background_color: 0.16, 0.65, 0.27, 1.0  # ACCENT_GREEN
                        color: 1, 1, 1, 1
                        size_hint_y: None
                        height: 45
                        font_name: 'Arial'
                        font_size: 12
                        on_release: root.go_to_attendance()
                        
                    Button:
                        text: '📊 Générer Rapport'
                        background_color: 0.43, 0.26, 0.76, 1.0  # ACCENT_PURPLE
                        color: 1, 1, 1, 1
                        size_hint_y: None
                        height: 45
                        font_name: 'Arial'
                        font_size: 12
                        on_release: root.go_to_reports()
                        
                    Button:
                        text: '🔄 Redémarrer Système'
                        background_color: 0.86, 0.21, 0.27, 1.0  # ACCENT_RED
                        color: 1, 1, 1, 1
                        size_hint_y: None
                        height: 45
                        font_name: 'Arial'
                        font_size: 12
                        on_release: root.restart_system()
                
                BoxLayout:
                    size_hint_y: 1
                
                Label:
                    text: '📋 Derniers Pointages'
                    font_name: 'Arial'
                    font_size: 16
                    bold: True
                    color: 0.12, 0.23, 0.37, 1  # UCC_BLUE_DARK
                    size_hint_y: None
                    height: 30
                
                # Liste des derniers pointages
                ScrollView:
                    size_hint_y: None
                    height: 150 if root.recent_attendance_text and root.recent_attendance_text != 'Aucun pointage récent' else 25
                    
                    Label:
                        text: root.recent_attendance_text
                        font_name: 'Arial'
                        font_size: 12
                        color: 0.12, 0.23, 0.37, 1  # UCC_BLUE_DARK
                        size_hint_y: None
                        height: self.texture_size[1]
                        text_size: self.width, None
                        valign: 'top'
''')

class DashboardScreen(Screen):
    """Écran Dashboard avec statistiques"""
    
    total_students = NumericProperty(0)
    present_today = NumericProperty(0)
    absent_today = NumericProperty(0)
    late_today = NumericProperty(0)
    attendance_rate = NumericProperty(0.0)
    current_date = StringProperty("")
    recent_attendance = ListProperty([])
    recent_attendance_text = StringProperty("Aucun pointage récent")
    trend_chart_path = StringProperty("")
    rate_chart_path = StringProperty("")
    hourly_chart_path = StringProperty("")
    
    def __init__(self, **kwargs):
        super(DashboardScreen, self).__init__(**kwargs)
        self.db_service = DatabaseService(
            host='localhost',
            database='ucc_face_recognition',
            user='root',
            password='admin123',
            port=3306
        )
        self.chart_service = ChartService()
        self.update_datetime()
        self.update_statistics()
    
    def on_enter(self):
        """Appelé lorsque l'écran est affiché"""
        self.update_statistics()
    
    def update_datetime(self):
        """Met à jour la date actuelle"""
        from datetime import datetime
        self.current_date = datetime.now().strftime("%d/%m/%Y")
    
    def update_statistics(self):
        """Met à jour les statistiques du dashboard avec les données réelles de MySQL"""
        try:
            stats = self.db_service.get_statistics()
            self.total_students = stats['total_students']
            
            # Récupérer les statistiques de présence du jour depuis get_statistics
            self.present_today = stats.get('present_today', 0)
            self.late_today = stats.get('late_today', 0)
            
            # Calculer les absents et le taux de présence
            if self.total_students > 0:
                self.absent_today = self.total_students - self.present_today
                self.attendance_rate = (self.present_today / self.total_students) * 100
            else:
                self.absent_today = 0
                self.attendance_rate = 0.0
            
            # Récupérer les derniers pointages
            self.recent_attendance = self.db_service.mysql_service.get_recent_attendance(limit=5)
            
            # Générer le texte des derniers pointages
            if self.recent_attendance:
                attendance_text = "Derniers pointages:\n"
                for i, attendance in enumerate(self.recent_attendance, 1):
                    date_str = attendance['date_presence'].strftime("%H:%M") if hasattr(attendance['date_presence'], 'strftime') else str(attendance['date_presence'])
                    attendance_text += f"{i}. {attendance['nom']} {attendance['prenom']} ({attendance['matricule']}) - {date_str} - {attendance['statut']}\n"
                self.recent_attendance_text = attendance_text
            else:
                self.recent_attendance_text = "Aucun pointage récent"
            
            # Générer les graphiques professionnels
            self.generate_charts()
                
        except Exception as e:
            print(f"Erreur lors de la mise à jour des statistiques: {e}")
            # Valeurs par défaut en cas d'erreur
            self.total_students = 0
            self.present_today = 0
            self.absent_today = 0
            self.attendance_rate = 0.0
            self.recent_attendance = []
            self.recent_attendance_text = "Aucun pointage récent"
    
    def generate_charts(self):
        """Génère tous les graphiques professionnels"""
        try:
            # Récupérer toutes les données de présence pour les graphiques
            attendance_data = self.db_service.mysql_service.get_recent_attendance(limit=1000)
            
            # Générer le graphique de tendance
            if attendance_data:
                self.trend_chart_path = self.chart_service.generate_attendance_trend_chart(attendance_data)
                self.rate_chart_path = self.chart_service.generate_attendance_rate_chart(attendance_data, self.total_students)
                self.hourly_chart_path = self.chart_service.generate_hourly_distribution_chart(attendance_data)
                print(f"✅ Graphiques générés avec succès")
            else:
                print("Pas assez de données pour générer les graphiques")
                
        except Exception as e:
            print(f"Erreur lors de la génération des graphiques: {e}")
    
    def go_to_students(self):
        """Navigue vers l'écran des étudiants"""
        self.manager.current = 'students'
    
    def go_to_attendance(self):
        """Navigue vers l'écran de pointage"""
        self.manager.current = 'attendance'
    
    def go_to_reports(self):
        """Navigue vers l'écran des rapports"""
        self.manager.current = 'reports'
    
    def restart_system(self):
        """Redémarre l'application Kivy"""
        try:
            from kivy.app import App
            import sys
            
            print("🔄 Redémarrage du système...")
            
            # Fermer proprement les connexions
            if hasattr(self, 'db_service') and self.db_service:
                try:
                    self.db_service.disconnect()
                except:
                    pass
            
            # Arrêter l'application
            app = App.get_running_app()
            app.stop()
            
            # Relancer l'application
            import os
            import subprocess
            python = sys.executable
            script = os.path.abspath(sys.argv[0])
            subprocess.Popen([python, script])
            sys.exit(0)
            
        except Exception as e:
            print(f"❌ Erreur lors du redémarrage: {e}")
            # Alternative: fermer simplement l'application
            from kivy.app import App
            App.get_running_app().stop()
