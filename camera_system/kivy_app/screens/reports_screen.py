"""
Ecran Rapports pour l'application Kivy
Export CSV et visualisation des rapports de presence avec chargement automatique
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.graphics import Color, Rectangle
from kivy.properties import StringProperty, NumericProperty, ListProperty, BooleanProperty
from kivy.lang import Builder
from kivy.clock import Clock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.report_watcher_service import ReportWatcherService
from services.report_analytics_service import ReportAnalyticsService
from services.mysql_service import MySQLService
from services.database_service import DatabaseService
from services.chart_service import ChartService

Builder.load_string('''
<ReportsScreen>:
    name: 'reports'
    
    BoxLayout:
        orientation: 'vertical'
        canvas.before:
            Color:
                rgba: 0.97, 0.97, 0.99, 1.0
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
                    rgba: 0.12, 0.23, 0.37, 1.0
                Rectangle:
                    size: self.size
                    pos: self.pos
                Color:
                    rgba: 0.29, 0.45, 0.69, 0.5
                Rectangle:
                    size: self.width, 2
                    pos: self.x, self.y
            
            Label:
                text: 'Rapports - UCC'
                font_name: 'Arial'
                font_size: 22
                bold: True
                color: 1, 1, 1, 1
                size_hint_x: 0.5
            
            BoxLayout:
                orientation: 'horizontal'
                size_hint_x: 0.3
                spacing: 10
                padding: 10
                canvas.before:
                    Color:
                        rgba: 0.18, 0.35, 0.56, 0.5
                    Rectangle:
                        size: self.size
                        pos: self.pos
                    Color:
                        rgba: 0.29, 0.45, 0.69, 0.3
                    Line:
                        rectangle: self.x, self.y, self.width, self.height
                
                Label:
                    text: 'Surveillance: ' + ('Actif' if root.watcher_active else 'Inactif')
                    font_name: 'Arial'
                    font_size: 12
                    color: 0.9, 0.95, 1, 1
            
            Button:
                text: 'Exporter CSV'
                background_color: 0.43, 0.26, 0.76, 1.0
                color: 1, 1, 1, 1
                size_hint_x: 0.2
                font_name: 'Arial'
                font_size: 12
        
        # Section: Rapports
        BoxLayout:
            orientation: 'vertical'
            size_hint_y: None
            height: 60
            padding: 20
            spacing: 15
            
            BoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: 40
                spacing: 15
                
                Button:
                    text: 'Journalier'
                    background_color: 0.16, 0.65, 0.26, 1.0
                    color: 1, 1, 1, 1
                    size_hint_x: 0.33
                    font_name: 'Arial'
                    font_size: 12
                    on_release: root.generate_daily_report()
                    
                Button:
                    text: 'Par Faculte'
                    background_color: 0.09, 0.64, 0.72, 1.0
                    color: 1, 1, 1, 1
                    size_hint_x: 0.33
                    font_name: 'Arial'
                    font_size: 12
                    on_release: root.generate_faculty_report()
                    
                Button:
                    text: 'Par Promotion'
                    background_color: 0.43, 0.26, 0.76, 1.0
                    color: 1, 1, 1, 1
                    size_hint_x: 0.33
                    font_name: 'Arial'
                    font_size: 12
                    on_release: root.generate_promotion_report()
        
        # Contenu principal
        BoxLayout:
            orientation: 'horizontal'
            padding: 25
            spacing: 25
            
            # Zone d'affichage des rapports
            BoxLayout:
                orientation: 'vertical'
                canvas.before:
                    Color:
                        rgba: 1, 1, 1, 1
                    Rectangle:
                        size: self.size
                        pos: self.pos
                    Color:
                        rgba: 0, 0, 0, 0.05
                    Rectangle:
                        size: self.size
                        pos: self.pos[0] + 2, self.pos[1] - 2
                size_hint_x: 0.65
                padding: 25
                spacing: 20
                
                ScrollView:
                    BoxLayout:
                        orientation: 'vertical'
                        spacing: 15
                        size_hint_y: None
                        height: self.minimum_height
                        id: report_results
                        
                        Label:
                            text: 'Selectionnez un rapport pour voir les resultats'
                            font_name: 'Arial'
                            font_size: 14
                            color: 0.42, 0.46, 0.49, 1
                            halign: 'center'
                            size_hint_y: None
                            height: 100
            
            # Sidebar statistiques
            BoxLayout:
                orientation: 'vertical'
                canvas.before:
                    Color:
                        rgba: 1, 1, 1, 1
                    Rectangle:
                        size: self.size
                        pos: self.pos
                    Color:
                        rgba: 0, 0, 0, 0.05
                    Rectangle:
                        size: self.size
                        pos: self.pos[0] + 2, self.pos[1] - 2
                size_hint_x: 0.35
                padding: 20
                spacing: 15
                
                Label:
                    text: 'Statistiques'
                    font_name: 'Arial'
                    font_size: 14
                    bold: True
                    color: 0.12, 0.23, 0.37, 1
                    size_hint_y: None
                    height: 30
                
                BoxLayout:
                    orientation: 'vertical'
                    spacing: 15
                    
                    BoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: 50
                        canvas.before:
                            Color:
                                rgba: 0.95, 0.97, 0.99, 1
                            Rectangle:
                                size: self.size
                                pos: self.pos
                        padding: 15
                        spacing: 10
                        
                        Label:
                            text: 'Total Etudiants'
                            font_name: 'Arial'
                            font_size: 11
                            color: 0.42, 0.46, 0.49, 1
                            size_hint_y: None
                            height: 20
                            
                        Label:
                            text: str(root.total_students)
                            font_name: 'Arial'
                            font_size: 24
                            bold: True
                            color: 0.29, 0.56, 0.89, 1
                            size_hint_y: None
                            height: 30
                    
                    BoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: 50
                        canvas.before:
                            Color:
                                rgba: 0.95, 0.97, 0.99, 1
                            Rectangle:
                                size: self.size
                                pos: self.pos
                        padding: 15
                        spacing: 10
                        
                        Label:
                            text: "Presents Aujourd'hui"
                            font_name: 'Arial'
                            font_size: 11
                            color: 0.42, 0.46, 0.49, 1
                            size_hint_y: None
                            height: 20
                            
                        Label:
                            text: str(root.total_attendance)
                            font_name: 'Arial'
                            font_size: 24
                            bold: True
                            color: 0.16, 0.65, 0.26, 1
                            size_hint_y: None
                            height: 30
                    
                    BoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: 50
                        canvas.before:
                            Color:
                                rgba: 0.95, 0.97, 0.99, 1
                            Rectangle:
                                size: self.size
                                pos: self.pos
                        padding: 15
                        spacing: 10
                        
                        Label:
                            text: 'Total Facultes'
                            font_name: 'Arial'
                            font_size: 11
                            color: 0.42, 0.46, 0.49, 1
                            size_hint_y: None
                            height: 20
                            
                        Label:
                            text: str(root.total_faculties)
                            font_name: 'Arial'
                            font_size: 24
                            bold: True
                            color: 0.29, 0.56, 0.89, 1
                            size_hint_y: None
                            height: 30
''')

class ReportsScreen(Screen):
    """Ecran Rapports avec chargement automatique et graphiques"""
    
    watcher_active = BooleanProperty(False)
    total_students = NumericProperty(0)
    total_attendance = NumericProperty(0)
    total_faculties = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super(ReportsScreen, self).__init__(**kwargs)
        self.report_watcher = ReportWatcherService('reports')
        self.report_analytics = ReportAnalyticsService()
        self.db_service = DatabaseService()
        self.chart_service = ChartService()
        self.total_students = 0
        self.total_attendance = 0
        self.report_watcher.add_callback(self.on_new_report)
        
    def on_enter(self):
        """Appelé lorsque l'écran est affiché"""
        self.report_watcher.start_watching()
        self.watcher_active = True
        print("Surveillance des rapports démarrée")
        Clock.schedule_once(lambda dt: self.generate_daily_report(), 0.5)
    
    def on_leave(self):
        """Appelé lorsque l'écran est quitté"""
        self.report_watcher.stop_watching()
        self.watcher_active = False
        print("Surveillance des rapports arrêtée")
    
    def load_existing_reports(self, dt):
        """Charge les rapports existants dans le dossier"""
        try:
            reports = self.report_watcher.get_existing_reports()
            print(f"Rapports existants chargés: {len(reports)}")
            self.update_statistics()
        except Exception as e:
            print(f"Erreur lors du chargement des rapports: {e}")
    
    def on_new_report(self, report_path):
        """Callback quand un nouveau rapport est détecté"""
        print(f"Nouveau rapport détecté: {report_path}")
        self.update_statistics()
        self.refresh_report_list()
    
    def update_statistics(self):
        """Met à jour les statistiques affichées"""
        if self.db_service:
            try:
                stats = self.db_service.get_statistics()
                self.total_students = stats.get('total_students', 0)
                self.total_attendance = stats.get('total_attendance', 0)
                self.total_faculties = stats.get('total_faculties', 0)
                print(f"Statistiques MySQL: {stats}")
            except Exception as e:
                print(f"Erreur lors de la récupération des statistiques MySQL: {e}")
    
    def refresh_report_list(self):
        """Rafraîchit la liste des rapports affichée"""
        pass
    
    def generate_daily_report(self):
        """Génère le rapport journalier avec graphiques"""
        if not self.db_service:
            self.show_report_error("Service de base de données non disponible")
            return
        
        try:
            report = self.db_service.get_daily_report()
            self.display_report_results("Rapport Journalier", report)
            
            if self.chart_service:
                self.generate_daily_chart(report)
        except Exception as e:
            self.show_report_error(f"Erreur lors de la génération du rapport journalier: {e}")
    
    def generate_faculty_report(self):
        """Génère le rapport par faculté avec graphiques"""
        if not self.db_service:
            self.show_report_error("Service de base de données non disponible")
            return
        
        try:
            report = self.db_service.get_faculty_report()
            self.display_report_results("Rapport par Faculte", report)
            
            if self.chart_service:
                self.generate_faculty_chart(report)
        except Exception as e:
            self.show_report_error(f"Erreur lors de la génération du rapport par faculté: {e}")
    
    def generate_promotion_report(self):
        """Génère le rapport par promotion avec graphiques"""
        if not self.db_service:
            self.show_report_error("Service de base de données non disponible")
            return
        
        try:
            report = self.db_service.get_promotion_report()
            self.display_report_results("Rapport par Promotion", report)
            
            if self.chart_service:
                self.generate_promotion_chart(report)
        except Exception as e:
            self.show_report_error(f"Erreur lors de la génération du rapport par promotion: {e}")
    
    def display_report_results(self, title, report):
        """Affiche les résultats du rapport dans l'interface"""
        results_layout = self.ids.report_results
        results_layout.clear_widgets()
        
        title_label = Label(
            text=f"{title}",
            font_name='Arial',
            font_size=18,
            bold=True,
            color=(0.12, 0.23, 0.37, 1),
            size_hint_y=None,
            height=40
        )
        results_layout.add_widget(title_label)
        
        chart_placeholder = Label(
            text="Graphique sera affiché ici",
            font_name='Arial',
            font_size=14,
            color=(0.42, 0.46, 0.49, 1),
            halign='center',
            size_hint_y=None,
            height=200
        )
        results_layout.add_widget(chart_placeholder)
        
        separator = Label(
            text="-" * 60,
            font_name='Arial',
            font_size=12,
            color=(0.8, 0.8, 0.8, 1),
            size_hint_y=None,
            height=30
        )
        results_layout.add_widget(separator)
        
        data_title = Label(
            text="Details des donnees",
            font_name='Arial',
            font_size=14,
            bold=True,
            color=(0.12, 0.23, 0.37, 1),
            size_hint_y=None,
            height=30
        )
        results_layout.add_widget(data_title)
        
        if isinstance(report, dict):
            for key, value in report.items():
                if key != 'date':
                    label = Label(
                        text=f"  {key.capitalize()}: {value}",
                        font_name='Arial',
                        font_size=13,
                        color=(0.2, 0.2, 0.2, 1),
                        size_hint_y=None,
                        height=30
                    )
                    results_layout.add_widget(label)
        elif isinstance(report, list):
            for item in report:
                if isinstance(item, dict):
                    for key, value in item.items():
                        label = Label(
                            text=f"  {key.capitalize()}: {value}",
                            font_name='Arial',
                            font_size=13,
                            color=(0.2, 0.2, 0.2, 1),
                            size_hint_y=None,
                            height=30
                        )
                        results_layout.add_widget(label)
                    separator = Label(
                        text="-" * 40,
                        font_name='Arial',
                        font_size=10,
                        color=(0.6, 0.6, 0.6, 1),
                        size_hint_y=None,
                        height=25
                    )
                    results_layout.add_widget(separator)
    
    def generate_daily_chart(self, report):
        """Génère un graphique pour le rapport journalier"""
        try:
            labels = ['Presents', 'Absents', 'Retards']
            values = [report.get('presents', 0), report.get('absents', 0), report.get('retards', 0)]
            
            date_str = report.get('date', "Aujourd'hui")
            chart_path = self.chart_service.generate_pie_chart_custom(
                labels=labels,
                values=values,
                title=f"Presences du {date_str}",
                output_name="daily_attendance_pie"
            )
            
            if chart_path:
                self.add_chart_to_results(chart_path)
        except Exception as e:
            print(f"Erreur lors de la génération du graphique journalier: {e}")
    
    def generate_faculty_chart(self, report):
        """Génère un graphique pour le rapport par faculté"""
        try:
            if isinstance(report, list):
                faculty_names = [item.get('faculty_nom', 'Inconnu') for item in report]
                presents = [item.get('presents', 0) for item in report]
                absents = [item.get('absents', 0) for item in report]
                
                chart_path = self.chart_service.generate_attendance_rate_chart_custom(
                    faculty_names=faculty_names,
                    presents=presents,
                    absents=absents,
                    title="Presences par Faculte",
                    output_name="faculty_attendance_bar"
                )
                
                if chart_path:
                    self.add_chart_to_results(chart_path)
        except Exception as e:
            print(f"Erreur lors de la génération du graphique par faculté: {e}")
    
    def generate_promotion_chart(self, report):
        """Génère un graphique pour le rapport par promotion"""
        try:
            if isinstance(report, list):
                promotion_names = [item.get('promotion_nom', 'Inconnu') for item in report]
                presents = [item.get('presents', 0) for item in report]
                absents = [item.get('absents', 0) for item in report]
                
                chart_path = self.chart_service.generate_attendance_rate_chart_custom(
                    faculty_names=promotion_names,
                    presents=presents,
                    absents=absents,
                    title="Presences par Promotion",
                    output_name="promotion_attendance_bar"
                )
                
                if chart_path:
                    self.add_chart_to_results(chart_path)
        except Exception as e:
            print(f"Erreur lors de la génération du graphique par promotion: {e}")
    
    def add_chart_to_results(self, chart_path):
        """Ajoute un graphique aux résultats (remplace le placeholder)"""
        from kivy.uix.image import Image
        
        results_layout = self.ids.report_results
        
        if len(results_layout.children) > 1:
            placeholder = results_layout.children[-2]
            results_layout.remove_widget(placeholder)
        
        chart_image = Image(
            source=chart_path,
            size_hint_y=None,
            height=350,
            allow_stretch=True
        )
        results_layout.add_widget(chart_image)
    
    def show_report_error(self, message):
        """Affiche un message d'erreur"""
        results_layout = self.ids.report_results
        results_layout.clear_widgets()
        
        error_label = Label(
            text=f"{message}",
            font_name='Arial',
            font_size=12,
            color=(0.8, 0.2, 0.2, 1),
            size_hint_y=None,
            height=40
        )
        results_layout.add_widget(error_label)
    
    def export_report_pdf(self):
        """Exporte le rapport actuel en PDF"""
        try:
            self.show_report_error("Export PDF en cours de développement")
        except Exception as e:
            self.show_report_error(f"Erreur lors de l'export PDF: {e}")
    
    def export_report_excel(self):
        """Exporte le rapport actuel en Excel"""
        try:
            self.show_report_error("Export Excel en cours de développement")
        except Exception as e:
            self.show_report_error(f"Erreur lors de l'export Excel: {e}")
    
    def export_report_csv(self):
        """Exporte le rapport actuel en CSV"""
        try:
            self.show_report_error("Export CSV en cours de développement")
        except Exception as e:
            self.show_report_error(f"Erreur lors de l'export CSV: {e}")
