"""
Service de graphiques professionnels pour l'application Kivy
Génère des graphiques matplotlib pour la prise de décision
"""

import matplotlib
matplotlib.use('Agg')  # Backend non-interactif pour Kivy
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import numpy as np
import io
import base64
import os
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class ChartService:
    """Service de génération de graphiques professionnels"""
    
    def __init__(self):
        """Initialise le service de graphiques"""
        # Style professionnel
        try:
            plt.style.use('seaborn-v0_8-darkgrid')
        except:
            plt.style.use('seaborn-darkgrid')
        
        self.colors = {
            'primary': '#1E3A8A',      # Bleu foncé
            'secondary': '#3B82F6',    # Bleu clair
            'success': '#10B981',      # Vert
            'warning': '#F59E0B',      # Orange
            'danger': '#EF4444',       # Rouge
            'info': '#6366F1',         # Indigo
            'purple': '#8B5CF6',       # Violet
        }
        
        # Créer le répertoire temporaire pour les graphiques
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.temp_dir = os.path.join(script_dir, 'temp_charts')
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def generate_attendance_trend_chart(self, attendance_data: List[Dict]) -> str:
        """
        Génère un graphique de tendance de présence sur 7 jours
        
        Args:
            attendance_data: Liste des données de présence
            
        Returns:
            Chemin de l'image générée
        """
        try:
            # Préparer les données
            dates = []
            present_counts = []
            absent_counts = []
            
            # Grouper par date
            date_groups = {}
            for record in attendance_data:
                date = record['date_presence'].date() if hasattr(record['date_presence'], 'date') else record['date_presence']
                if date not in date_groups:
                    date_groups[date] = {'present': 0, 'absent': 0}
                if record['statut'] == 'present':
                    date_groups[date]['present'] += 1
                else:
                    date_groups[date]['absent'] += 1
            
            # Trier par date
            sorted_dates = sorted(date_groups.keys())[-7:]  # 7 derniers jours
            
            for date in sorted_dates:
                dates.append(date)
                present_counts.append(date_groups[date]['present'])
                absent_counts.append(date_groups[date]['absent'])
            
            # Créer le graphique
            fig, ax = plt.subplots(figsize=(10, 5))
            
            x = np.arange(len(dates))
            width = 0.35
            
            bars1 = ax.bar(x - width/2, present_counts, width, label='Présents', 
                          color=self.colors['success'], alpha=0.8)
            bars2 = ax.bar(x + width/2, absent_counts, width, label='Absents', 
                          color=self.colors['danger'], alpha=0.8)
            
            ax.set_xlabel('Date', fontsize=12, fontweight='bold')
            ax.set_ylabel('Nombre d\'étudiants', fontsize=12, fontweight='bold')
            ax.set_title('Tendance de Présence - 7 Derniers Jours', fontsize=14, fontweight='bold')
            ax.set_xticks(x)
            ax.set_xticklabels([d.strftime('%d/%m') for d in dates], rotation=45)
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # Ajouter les valeurs sur les barres
            for bar in bars1:
                height = bar.get_height()
                ax.annotate(f'{int(height)}',
                           xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 3), textcoords="offset points",
                           ha='center', va='bottom', fontsize=9)
            
            for bar in bars2:
                height = bar.get_height()
                ax.annotate(f'{int(height)}',
                           xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 3), textcoords="offset points",
                           ha='center', va='bottom', fontsize=9)
            
            plt.tight_layout()
            
            # Sauvegarder
            output_path = os.path.join(self.temp_dir, 'attendance_trend.png')
            plt.savefig(output_path, dpi=100, bbox_inches='tight')
            plt.close()
            
            return output_path
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du graphique de tendance: {e}")
            return None
    
    def generate_attendance_rate_chart(self, attendance_data: List[Dict], total_students: int) -> str:
        """
        Génère un graphique de taux de présence
        
        Args:
            attendance_data: Liste des données de présence
            total_students: Nombre total d'étudiants
            
        Returns:
            Chemin de l'image générée
        """
        try:
            # Préparer les données
            dates = []
            rates = []
            
            # Grouper par date
            date_groups = {}
            for record in attendance_data:
                date = record['date_presence'].date() if hasattr(record['date_presence'], 'date') else record['date_presence']
                if date not in date_groups:
                    date_groups[date] = 0
                if record['statut'] == 'present':
                    date_groups[date] += 1
            
            # Trier par date
            sorted_dates = sorted(date_groups.keys())[-7:]
            
            for date in sorted_dates:
                dates.append(date)
                rate = (date_groups[date] / total_students * 100) if total_students > 0 else 0
                rates.append(rate)
            
            # Créer le graphique
            fig, ax = plt.subplots(figsize=(10, 5))
            
            ax.plot(dates, rates, marker='o', linewidth=2, markersize=8, 
                   color=self.colors['primary'], label='Taux de présence')
            ax.fill_between(dates, rates, alpha=0.3, color=self.colors['primary'])
            
            ax.set_xlabel('Date', fontsize=12, fontweight='bold')
            ax.set_ylabel('Taux de présence (%)', fontsize=12, fontweight='bold')
            ax.set_title('Taux de Présence Quotidien - 7 Derniers Jours', fontsize=14, fontweight='bold')
            ax.set_ylim(0, 100)
            ax.grid(True, alpha=0.3)
            ax.legend()
            
            # Formater les dates
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
            plt.xticks(rotation=45)
            
            # Ajouter les valeurs
            for i, (date, rate) in enumerate(zip(dates, rates)):
                ax.annotate(f'{rate:.1f}%',
                           xy=(date, rate),
                           xytext=(0, 10), textcoords="offset points",
                           ha='center', va='bottom', fontsize=9,
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
            
            plt.tight_layout()
            
            # Sauvegarder
            output_path = os.path.join(self.temp_dir, 'attendance_rate.png')
            plt.savefig(output_path, dpi=100, bbox_inches='tight')
            plt.close()
            
            return output_path
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du graphique de taux: {e}")
            return None
    
    def generate_hourly_distribution_chart(self, attendance_data: List[Dict]) -> str:
        """
        Génère un graphique de distribution horaire des présences
        
        Args:
            attendance_data: Liste des données de présence
            
        Returns:
            Chemin de l'image générée
        """
        try:
            # Préparer les données par heure
            hour_counts = {}
            for record in attendance_data:
                if record['statut'] == 'present':
                    hour = record['date_presence'].hour if hasattr(record['date_presence'], 'hour') else 0
                    hour_counts[hour] = hour_counts.get(hour, 0) + 1
            
            # Créer le graphique
            fig, ax = plt.subplots(figsize=(10, 5))
            
            hours = sorted(hour_counts.keys())
            counts = [hour_counts[h] for h in hours]
            
            bars = ax.bar(hours, counts, color=self.colors['secondary'], alpha=0.8, edgecolor=self.colors['primary'])
            
            ax.set_xlabel('Heure de la journée', fontsize=12, fontweight='bold')
            ax.set_ylabel('Nombre de présences', fontsize=12, fontweight='bold')
            ax.set_title('Distribution Horaire des Présences', fontsize=14, fontweight='bold')
            ax.set_xticks(hours)
            ax.set_xticklabels([f'{h:02d}:00' for h in hours], rotation=45)
            ax.grid(True, alpha=0.3, axis='y')
            
            # Ajouter les valeurs
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f'{int(height)}',
                           xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 3), textcoords="offset points",
                           ha='center', va='bottom', fontsize=9)
            
            plt.tight_layout()
            
            # Sauvegarder
            output_path = os.path.join(self.temp_dir, 'hourly_distribution.png')
            plt.savefig(output_path, dpi=100, bbox_inches='tight')
            plt.close()
            
            return output_path
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du graphique horaire: {e}")
            return None
    
    def generate_top_students_chart(self, student_data: List[Dict], limit: int = 10) -> str:
        """
        Génère un graphique des top étudiants par présence
        
        Args:
            student_data: Liste des données d'étudiants avec leurs présences
            limit: Nombre d'étudiants à afficher
            
        Returns:
            Chemin de l'image générée
        """
        try:
            # Trier par nombre de présences
            sorted_students = sorted(student_data, key=lambda x: x.get('attendance_count', 0), reverse=True)[:limit]
            
            names = [f"{s['nom']} {s['prenom'][:1]}." for s in sorted_students]
            counts = [s.get('attendance_count', 0) for s in sorted_students]
            
            # Créer le graphique horizontal
            fig, ax = plt.subplots(figsize=(10, 6))
            
            y_pos = np.arange(len(names))
            bars = ax.barh(y_pos, counts, color=self.colors['info'], alpha=0.8)
            
            ax.set_yticks(y_pos)
            ax.set_yticklabels(names, fontsize=10)
            ax.invert_yaxis()
            ax.set_xlabel('Nombre de présences', fontsize=12, fontweight='bold')
            ax.set_title(f'Top {limit} Étudiants par Présence', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3, axis='x')
            
            # Ajouter les valeurs
            for i, (bar, count) in enumerate(zip(bars, counts)):
                ax.annotate(f'{int(count)}',
                           xy=(count, bar.get_y() + bar.get_height() / 2),
                           xytext=(5, 0), textcoords="offset points",
                           ha='left', va='center', fontsize=9,
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
            
            plt.tight_layout()
            
            # Sauvegarder
            output_path = os.path.join(self.temp_dir, 'top_students.png')
            plt.savefig(output_path, dpi=100, bbox_inches='tight')
            plt.close()
            
            return output_path
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du graphique top étudiants: {e}")
            return None
    
    def generate_pie_chart(self, present: int, absent: int) -> str:
        """
        Génère un graphique circulaire de présence
        
        Args:
            present: Nombre de présents
            absent: Nombre d'absents
            
        Returns:
            Chemin de l'image générée
        """
        try:
            # Créer le graphique
            fig, ax = plt.subplots(figsize=(8, 8))
            
            labels = ['Présents', 'Absents']
            sizes = [present, absent]
            colors = [self.colors['success'], self.colors['danger']]
            explode = (0.05, 0.05)  # Séparer légèrement les sections
            
            wedges, texts, autotexts = ax.pie(sizes, explode=explode, labels=labels, colors=colors,
                                              autopct='%1.1f%%', shadow=True, startangle=90,
                                              textprops={'fontsize': 12, 'fontweight': 'bold'})
            
            ax.set_title('Répartition Présence/Absence', fontsize=14, fontweight='bold', pad=20)
            
            # Améliorer le style
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontsize(14)
            
            plt.tight_layout()
            
            # Sauvegarder
            output_path = os.path.join(self.temp_dir, 'pie_chart.png')
            plt.savefig(output_path, dpi=100, bbox_inches='tight')
            plt.close()
            
            return output_path
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du graphique circulaire: {e}")
            return None
    
    def generate_pie_chart_custom(self, labels: List[str], values: List[int], title: str, output_name: str) -> str:
        """
        Génère un graphique circulaire personnalisé
        
        Args:
            labels: Liste des labels
            values: Liste des valeurs
            title: Titre du graphique
            output_name: Nom du fichier de sortie
            
        Returns:
            Chemin de l'image générée
        """
        try:
            # Créer le graphique
            fig, ax = plt.subplots(figsize=(8, 8))
            
            # Éviter la division par zéro si toutes les valeurs sont à 0
            if sum(values) == 0:
                ax.text(0.5, 0.5, "Pas de données pour générer le graphique", 
                        horizontalalignment='center', verticalalignment='center',
                        fontsize=14, fontweight='bold', color=self.colors['primary'])
                ax.set_xticks([])
                ax.set_yticks([])
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['bottom'].set_visible(False)
                ax.spines['left'].set_visible(False)
                ax.grid(False)
            else:
                colors = [self.colors['success'], self.colors['danger'], self.colors['warning']]
                # Adapter la palette si plus de labels que de couleurs par défaut
                while len(colors) < len(labels):
                    colors.extend(colors)
                colors = colors[:len(labels)]
                
                explode = [0.05] * len(labels)  # Séparer légèrement les sections
                
                wedges, texts, autotexts = ax.pie(values, explode=explode, labels=labels, colors=colors,
                                                  autopct='%1.1f%%', shadow=True, startangle=90,
                                                  textprops={'fontsize': 12, 'fontweight': 'bold'})
                
                # Améliorer le style
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontsize(14)
            
            ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
            
            plt.tight_layout()
            
            # Sauvegarder
            output_path = os.path.join(self.temp_dir, f'{output_name}.png')
            plt.savefig(output_path, dpi=100, bbox_inches='tight')
            plt.close()
            
            return output_path
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du graphique circulaire personnalisé: {e}")
            return None
    
    def generate_attendance_rate_chart_custom(self, faculty_names: List[str], presents: List[int], 
                                               absents: List[int], title: str, output_name: str) -> str:
        """
        Génère un graphique à barres personnalisé pour les présences par faculté/promotion
        
        Args:
            faculty_names: Liste des noms de facultés/promotions
            presents: Liste des présents
            absents: Liste des absents
            title: Titre du graphique
            output_name: Nom du fichier de sortie
            
        Returns:
            Chemin de l'image générée
        """
        try:
            # Créer le graphique
            fig, ax = plt.subplots(figsize=(10, 6))
            
            x = np.arange(len(faculty_names))
            width = 0.35
            
            bars1 = ax.bar(x - width/2, presents, width, label='Présents', 
                          color=self.colors['success'], alpha=0.8)
            bars2 = ax.bar(x + width/2, absents, width, label='Absents', 
                          color=self.colors['danger'], alpha=0.8)
            
            ax.set_xlabel('Faculté/Promotion', fontsize=12, fontweight='bold')
            ax.set_ylabel('Nombre d\'étudiants', fontsize=12, fontweight='bold')
            ax.set_title(title, fontsize=14, fontweight='bold')
            ax.set_xticks(x)
            ax.set_xticklabels(faculty_names, rotation=45, ha='right')
            ax.legend()
            ax.grid(True, alpha=0.3, axis='y')
            
            # Ajouter les valeurs sur les barres
            for bar in bars1:
                height = bar.get_height()
                if height > 0:
                    ax.annotate(f'{int(height)}',
                               xy=(bar.get_x() + bar.get_width() / 2, height),
                               xytext=(0, 3), textcoords="offset points",
                               ha='center', va='bottom', fontsize=9)
            
            for bar in bars2:
                height = bar.get_height()
                if height > 0:
                    ax.annotate(f'{int(height)}',
                               xy=(bar.get_x() + bar.get_width() / 2, height),
                               xytext=(0, 3), textcoords="offset points",
                               ha='center', va='bottom', fontsize=9)
            
            plt.tight_layout()
            
            # Sauvegarder
            output_path = os.path.join(self.temp_dir, f'{output_name}.png')
            plt.savefig(output_path, dpi=100, bbox_inches='tight')
            plt.close()
            
            return output_path
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du graphique à barres personnalisé: {e}")
            return None
