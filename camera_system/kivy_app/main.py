"""
Application Kivy pour le Système de Reconnaissance Faciale - UCC
Mise en place d'un système de reconnaissance faciale basé sur les réseaux de neurones convolutifs
pour le pointage automatique des étudiants. Cas de l'UCC
"""

import sys
import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.config import Config

# Configuration de la fenêtre
Config.set('graphics', 'resizable', '1')
Config.set('graphics', 'width', '1200')
Config.set('graphics', 'height', '800')

# Ajouter le répertoire parent au path pour accéder aux modules existants
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# =============================================================================
# IMPORT DES SCREENS ET WIDGETS
# =============================================================================

from screens.dashboard_screen import DashboardScreen
from screens.students_screen import StudentsScreen
from screens.attendance_screen import AttendanceScreen
from screens.organization_screen import OrganizationScreen
from screens.reports_screen import ReportsScreen
from screens.settings_screen import SettingsScreen

from widgets.ucc_button import UCCButton
from widgets.header import Header
from widgets.sidebar import Sidebar

# =============================================================================
# DESIGN SYSTEM UCC
# =============================================================================

class UCCColors:
    """Palette de couleurs UCC - Design Professionnel"""
    # Couleurs principales
    UCC_BLUE = "#1E3A5F"           # Bleu UCC (principal - plus profond)
    UCC_BLUE_LIGHT = "#2D5A87"      # Bleu UCC clair
    UCC_BLUE_DARK = "#152A45"       # Bleu UCC foncé
    UCC_WHITE = "#FFFFFF"           # Blanc pur
    UCC_OFF_WHITE = "#F8F9FA"       # Blanc cassé (fond)
    UCC_LIGHT_GRAY = "#E9ECEF"      # Gris très clair
    UCC_GRAY = "#6C757D"            # Gris moyen
    UCC_DARK_GRAY = "#343A40"       # Gris foncé
    
    # Couleurs d'accentuation
    ACCENT_BLUE = "#4A90E2"         # Bleu accent
    ACCENT_GREEN = "#28A745"        # Vert accent
    ACCENT_YELLOW = "#FFC107"       # Jaune accent
    ACCENT_ORANGE = "#FD7E14"       # Orange accent
    ACCENT_RED = "#DC3545"          # Rouge accent
    ACCENT_PURPLE = "#6F42C1"       # Violet accent
    ACCENT_CYAN = "#17A2B8"         # Cyan accent
    
    # Couleurs boutons (avec états)
    BUTTON_PRIMARY = "#4A90E2"      # Bouton principal
    BUTTON_PRIMARY_HOVER = "#357ABD" # Bouton principal survolé
    BUTTON_SUCCESS = "#28A745"       # Bouton succès
    BUTTON_SUCCESS_HOVER = "#218838" # Bouton succès survolé
    BUTTON_WARNING = "#FFC107"       # Bouton avertissement
    BUTTON_WARNING_HOVER = "#E0A800" # Bouton avertissement survolé
    BUTTON_DANGER = "#DC3545"       # Bouton danger
    BUTTON_DANGER_HOVER = "#C82333"  # Bouton danger survolé
    BUTTON_INFO = "#17A2B8"         # Bouton info
    BUTTON_INFO_HOVER = "#138496"    # Bouton info survolé
    BUTTON_SECONDARY = "#6C757D"    # Bouton secondaire
    BUTTON_SECONDARY_HOVER = "#5A6268" # Bouton secondaire survolé
    
    # Couleurs de fond et bordures
    BACKGROUND = "#F8F9FA"          # Fond principal
    CARD_BACKGROUND = "#FFFFFF"     # Fond des cartes
    BORDER_COLOR = "#DEE2E6"        # Couleur des bordures
    SHADOW_COLOR = "rgba(0, 0, 0, 0.1)" # Couleur des ombres
    
    # Couleurs de texte
    TEXT_PRIMARY = "#212529"        # Texte principal
    TEXT_SECONDARY = "#6C757D"      # Texte secondaire
    TEXT_MUTED = "#ADB5BD"          # Texte atténué
    TEXT_WHITE = "#FFFFFF"          # Texte blanc
    TEXT_DARK = "#343A40"           # Texte foncé

class UCCTypography:
    """Typographie UCC"""
    TITLE_FONT = 'Arial'
    TITLE_SIZE = 20
    TITLE_BOLD = True
    
    SUBTITLE_FONT = 'Arial'
    SUBTITLE_SIZE = 16
    SUBTITLE_BOLD = True
    
    TEXT_FONT = 'Arial'
    TEXT_SIZE = 12
    TEXT_BOLD = False
    
    LABEL_FONT = 'Arial'
    LABEL_SIZE = 11
    LABEL_BOLD = False

# =============================================================================
# APPLICATION PRINCIPALE
# =============================================================================

class UCCFaceRecognitionApp(App):
    """Application principale de reconnaissance faciale UCC"""
    
    def build(self):
        """Construit l'interface de l'application"""
        # Configuration de la fenêtre
        Window.title = "Système de Reconnaissance Faciale - UCC"
        Window.size = (1200, 800)
        Window.minimum_width = 1000
        Window.minimum_height = 700
        
        # Créer le layout principal
        main_layout = BoxLayout(orientation='horizontal')
        
        # Créer le ScreenManager
        sm = ScreenManager()
        
        # Ajouter les écrans
        dashboard = DashboardScreen(name='dashboard')
        students = StudentsScreen(name='students')
        attendance = AttendanceScreen(name='attendance')
        organization = OrganizationScreen(name='organization')
        reports = ReportsScreen(name='reports')
        settings = SettingsScreen(name='settings')
        
        sm.add_widget(dashboard)
        sm.add_widget(students)
        sm.add_widget(attendance)
        sm.add_widget(organization)
        sm.add_widget(reports)
        sm.add_widget(settings)
        
        # Créer le Sidebar avec navigation
        sidebar = Sidebar()
        sidebar.screen_manager = sm
        
        # Ajouter le Sidebar et le ScreenManager au layout principal
        main_layout.add_widget(sidebar)
        main_layout.add_widget(sm)
        
        return main_layout
    
    def on_start(self):
        """Initialisation au démarrage"""
        print("=" * 70)
        print("SYSTÈME DE RECONNAISSANCE FACIALE - UCC")
        print("=" * 70)
        print("Mise en place d'un système de reconnaissance faciale basé sur les")
        print("réseaux de neurones convolutifs pour le pointage automatique")
        print("des étudiants. Cas de l'UCC")
        print("=" * 70)
        print(f"Application Kivy démarrée avec succès")
        print(f"Fenêtre: {Window.size}")
        print("=" * 70)
        print("Écrans disponibles:")
        print("  - dashboard: Tableau de bord")
        print("  - students: Gestion des étudiants")
        print("  - attendance: Pointage caméra")
        print("  - organization: Organisation")
        print("  - reports: Rapports")
        print("  - settings: Paramètres")
        print("=" * 70)

if __name__ == '__main__':
    app = UCCFaceRecognitionApp()
    app.run()
