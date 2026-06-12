"""
Service d'analyse et de génération de graphiques pour les rapports
Génère des graphiques, courbes et statistiques à partir des données de rapports
"""

import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime
import json


class ReportAnalyticsService:
    """Service d'analyse et de génération de graphiques pour les rapports"""
    
    def __init__(self):
        """Initialise le service d'analyse"""
        self.report_data = {}
        self.statistics = {}
    
    def add_report_data(self, file_path: str, parsed_data: Dict):
        """
        Ajoute les données d'un rapport pour l'analyse
        
        Args:
            file_path: Chemin du fichier
            parsed_data: Données parsées du fichier
        """
        self.report_data[file_path] = parsed_data
        self._calculate_statistics(file_path, parsed_data)
    
    def _calculate_statistics(self, file_path: str, parsed_data: Dict):
        """
        Calcule les statistiques pour un rapport
        
        Args:
            file_path: Chemin du fichier
            parsed_data: Données parsées
        """
        if 'error' in parsed_data:
            return
        
        stats = {
            'file_name': parsed_data.get('file_name', ''),
            'file_type': parsed_data.get('file_type', ''),
            'row_count': parsed_data.get('row_count', 0),
            'parsed_at': parsed_data.get('parsed_at', ''),
            'columns': parsed_data.get('headers', []),
            'numeric_stats': {},
            'categorical_stats': {}
        }
        
        # Analyser les données numériques
        if 'data' in parsed_data and parsed_data['data']:
            data = parsed_data['data']
            
            # Identifier les colonnes numériques
            numeric_columns = self._identify_numeric_columns(data, parsed_data.get('headers', []))
            
            for col in numeric_columns:
                values = [float(row.get(col, 0)) for row in data if row.get(col) and str(row.get(col)).replace('.', '').isdigit()]
                
                if values:
                    stats['numeric_stats'][col] = {
                        'count': len(values),
                        'mean': np.mean(values),
                        'median': np.median(values),
                        'std': np.std(values),
                        'min': np.min(values),
                        'max': np.max(values),
                        'sum': np.sum(values)
                    }
            
            # Analyser les colonnes catégorielles
            categorical_columns = [col for col in parsed_data.get('headers', []) if col not in numeric_columns]
            
            for col in categorical_columns:
                values = [row.get(col, '') for row in data if row.get(col)]
                
                if values:
                    # Compter les occurrences
                    value_counts = {}
                    for val in values:
                        value_counts[val] = value_counts.get(val, 0) + 1
                    
                    stats['categorical_stats'][col] = {
                        'unique_count': len(value_counts),
                        'most_common': max(value_counts.items(), key=lambda x: x[1]) if value_counts else None,
                        'distribution': value_counts
                    }
        
        self.statistics[file_path] = stats
    
    def _identify_numeric_columns(self, data: List[Dict], headers: List[str]) -> List[str]:
        """
        Identifie les colonnes numériques dans les données
        
        Args:
            data: Données du rapport
            headers: En-têtes des colonnes
            
        Returns:
            Liste des colonnes numériques
        """
        numeric_columns = []
        
        for col in headers:
            is_numeric = True
            sample_count = 0
            
            for row in data[:min(10, len(data))]:  # Échantillon de 10 lignes
                value = row.get(col, '')
                if value and str(value).strip():
                    try:
                        float(value)
                        sample_count += 1
                    except (ValueError, TypeError):
                        is_numeric = False
                        break
            
            if is_numeric and sample_count > 0:
                numeric_columns.append(col)
        
        return numeric_columns
    
    def get_statistics(self, file_path: str) -> Dict:
        """
        Retourne les statistiques pour un fichier
        
        Args:
            file_path: Chemin du fichier
            
        Returns:
            Dictionnaire des statistiques
        """
        return self.statistics.get(file_path, {})
    
    def get_all_statistics(self) -> Dict:
        """Retourne toutes les statistiques"""
        return self.statistics
    
    def generate_chart_data(self, file_path: str, chart_type: str, column: str = None) -> Dict:
        """
        Génère les données pour un graphique
        
        Args:
            file_path: Chemin du fichier
            chart_type: Type de graphique ('bar', 'line', 'pie', 'scatter')
            column: Colonne à analyser
            
        Returns:
            Données pour le graphique
        """
        if file_path not in self.report_data:
            return {'error': 'Fichier non trouvé'}
        
        parsed_data = self.report_data[file_path]
        stats = self.statistics.get(file_path, {})
        
        chart_data = {
            'chart_type': chart_type,
            'title': f'{chart_type.capitalize()} - {parsed_data.get("file_name", "")}',
            'labels': [],
            'values': [],
            'colors': []
        }
        
        if chart_type == 'bar' and column:
            # Graphique à barres pour distribution catégorielle
            if column in stats.get('categorical_stats', {}):
                distribution = stats['categorical_stats'][column]['distribution']
                chart_data['labels'] = list(distribution.keys())
                chart_data['values'] = list(distribution.values())
                chart_data['colors'] = self._generate_colors(len(distribution))
        
        elif chart_type == 'line' and column:
            # Graphique linéaire pour données numériques
            if column in stats.get('numeric_stats', {}):
                data = parsed_data.get('data', [])
                values = [float(row.get(column, 0)) for row in data if row.get(column)]
                chart_data['labels'] = list(range(len(values)))
                chart_data['values'] = values
                chart_data['colors'] = [[0.29, 0.56, 0.89, 1.0]]  # Bleu accent
        
        elif chart_type == 'pie' and column:
            # Graphique circulaire pour distribution
            if column in stats.get('categorical_stats', {}):
                distribution = stats['categorical_stats'][column]['distribution']
                chart_data['labels'] = list(distribution.keys())
                chart_data['values'] = list(distribution.values())
                chart_data['colors'] = self._generate_colors(len(distribution))
        
        elif chart_type == 'scatter' and column:
            # Nuage de points
            if column in stats.get('numeric_stats', {}):
                data = parsed_data.get('data', [])
                values = [float(row.get(column, 0)) for row in data if row.get(column)]
                chart_data['labels'] = list(range(len(values)))
                chart_data['values'] = values
                chart_data['colors'] = [[0.29, 0.56, 0.89, 1.0]] * len(values)
        
        return chart_data
    
    def _generate_colors(self, count: int) -> List[List[float]]:
        """
        Génère une palette de couleurs pour les graphiques
        
        Args:
            count: Nombre de couleurs à générer
            
        Returns:
            Liste de couleurs RGBA
        """
        colors = [
            [0.29, 0.56, 0.89, 1.0],   # Bleu accent
            [0.16, 0.65, 0.26, 1.0],   # Vert accent
            [1.0, 0.76, 0.03, 1.0],    # Jaune accent
            [0.86, 0.21, 0.27, 1.0],   # Rouge accent
            [0.43, 0.26, 0.76, 1.0],   # Violet accent
            [0.09, 0.64, 0.72, 1.0],   # Cyan accent
            [0.99, 0.49, 0.13, 1.0],   # Orange accent
            [0.42, 0.46, 0.49, 1.0],   # Gris accent
        ]
        
        # Répéter les couleurs si nécessaire
        while len(colors) < count:
            colors.extend(colors)
        
        return colors[:count]
    
    def get_summary_report(self) -> Dict:
        """
        Génère un rapport récapitulatif de tous les rapports
        
        Returns:
            Dictionnaire avec le récapitulatif
        """
        summary = {
            'total_reports': len(self.report_data),
            'total_rows': sum(stats.get('row_count', 0) for stats in self.statistics.values()),
            'report_types': {},
            'last_updated': datetime.now().isoformat(),
            'reports': []
        }
        
        # Compter les types de rapports
        for stats in self.statistics.values():
            file_type = stats.get('file_type', 'unknown')
            summary['report_types'][file_type] = summary['report_types'].get(file_type, 0) + 1
        
        # Liste des rapports
        for file_path, stats in self.statistics.items():
            summary['reports'].append({
                'file_name': stats.get('file_name', ''),
                'file_type': stats.get('file_type', ''),
                'row_count': stats.get('row_count', 0),
                'columns': stats.get('columns', []),
                'parsed_at': stats.get('parsed_at', '')
            })
        
        return summary
    
    def export_statistics(self, output_path: str):
        """
        Exporte les statistiques vers un fichier JSON
        
        Args:
            output_path: Chemin du fichier de sortie
        """
        summary = self.get_summary_report()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Statistiques exportées vers: {output_path}")
