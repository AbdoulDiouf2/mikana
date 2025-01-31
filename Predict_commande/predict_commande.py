import pandas as pd
import numpy as np
import joblib
import json
import logging
from datetime import datetime, timedelta
import os
from prophet.forecaster import Prophet

class UnifiedPredictor:
    def __init__(self, model_dir='trained_models'):
        """Initialise le prédicteur unifié"""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.model_dir = model_dir
        
        try:
            # Charger le modèle unifié
            model_path = os.path.join(model_dir, 'unified_model.joblib')
            self.unified_data = joblib.load(model_path)
            self.model = self.unified_data['model']
            self.establishments = self.unified_data['establishments']
            self.articles = self.unified_data['articles']
            self.establishment_mapping = self.unified_data['establishment_mapping']
            self.article_mapping = self.unified_data['article_mapping']
            
            # Charger les métriques
            metrics_path = os.path.join(model_dir, 'model_metrics.json')
            with open(metrics_path, 'r', encoding='utf-8') as f:
                self.metrics_data = json.load(f)
            
            self.logger.info("✅ Modèle et métriques chargés avec succès")
            self.logger.info(f"Date d'entraînement: {self.unified_data['last_training_date']}")
            self.logger.info(f"Nombre d'établissements: {len(self.establishments)}")
            self.logger.info(f"Nombre d'articles: {len(self.articles)}")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur lors du chargement du modèle: {str(e)}")
            raise e

    def get_ids(self, establishment=None, article=None):
        """Convertit les noms en IDs pour le modèle"""
        try:
            establishment_id = -1
            article_id = -1
            
            if establishment:
                if establishment in self.establishments:
                    establishment_id = list(self.establishment_mapping.keys())[
                        list(self.establishment_mapping.values()).index(establishment)
                    ]
                else:
                    self.logger.warning(f"⚠️ Établissement '{establishment}' non trouvé")
            
            if article:
                if article in self.articles:
                    article_id = list(self.article_mapping.keys())[
                        list(self.article_mapping.values()).index(article)
                    ]
                else:
                    self.logger.warning(f"⚠️ Article '{article}' non trouvé")
            
            return establishment_id, article_id
            
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de la conversion des IDs: {str(e)}")
            raise e

    def check_data_freshness(self):
        """Vérifie la fraîcheur des données du modèle"""
        last_training = datetime.fromisoformat(self.unified_data['last_training_date'])
        days_since_training = (datetime.now() - last_training).days
        
        if days_since_training > 30:
            self.logger.warning(f"⚠️ Modèle entraîné il y a {days_since_training} jours")
            return "old"
        return "fresh"

    def calculate_prediction_confidence(self, establishment=None, article=None):
        """Calcule le niveau de confiance de la prédiction"""
        base_confidence = float(self.metrics_data['model_metrics']['r2'])
        
        # Ajuster la confiance selon la présence d'établissement/article
        if establishment and establishment not in self.establishments:
            base_confidence *= 0.7
        if article and article not in self.articles:
            base_confidence *= 0.7
            
        return base_confidence

    def predict(self, dates, establishment=None, article=None):
        """Génère des prédictions pour les dates données"""
        try:
            # Vérifier la fraîcheur des données
            data_freshness = self.check_data_freshness()
            
            # Obtenir les IDs pour l'établissement et l'article
            establishment_id, article_id = self.get_ids(establishment, article)
            
            # Préparer les données pour la prédiction
            if isinstance(dates, (str, datetime)):
                dates = pd.DatetimeIndex([pd.to_datetime(dates)])
            elif isinstance(dates, tuple):
                start_date, end_date = pd.to_datetime(dates[0]), pd.to_datetime(dates[1])
                dates = pd.date_range(start=start_date, end=end_date, freq='D')
            
            future_df = pd.DataFrame({
                'ds': dates,
                'establishment_id': establishment_id,
                'article_id': article_id
            })
            
            # Générer les prédictions
            forecast = self.model.predict(future_df)
            
            # Calculer le niveau de confiance
            confidence = self.calculate_prediction_confidence(establishment, article)
            
            # Préparer les résultats
            predictions = []
            for i, row in forecast.iterrows():
                prediction = {
                    'date': row['ds'].strftime('%Y-%m-%d'),
                    'prediction': max(0, round(row['yhat'])),
                    'intervalle_confiance': {
                        'min': max(0, round(row['yhat_lower'])),
                        'max': round(row['yhat_upper'])
                    },
                    'statistiques': {
                        'fiabilite': 'haute' if confidence > 0.8 else 'moyenne' if confidence > 0.6 else 'basse',
                        'tendance': float(row['trend']),
                        'saisonnalite': float(row.get('yearly', 0)),
                        'confiance': round(confidence * 100, 2)
                    },
                    'metadata': {
                        'establishment': establishment,
                        'article': article,
                        'model_freshness': data_freshness,
                        'prediction_timestamp': datetime.now().isoformat()
                    }
                }
                predictions.append(prediction)
            
            return predictions
            
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de la prédiction: {str(e)}")
            return self._handle_prediction_error(establishment, article)

    def _handle_prediction_error(self, establishment=None, article=None):
        """Gère les erreurs de prédiction en fournissant une estimation de secours"""
        self.logger.warning("⚠️ Utilisation du système de secours pour la prédiction")
        
        # Chercher des données similaires dans les métriques
        avg_value = 100  # Valeur par défaut
        if self.metrics_data and 'data_summary' in self.metrics_data:
            # Utiliser la moyenne historique si disponible
            avg_value = self.metrics_data['model_metrics'].get('average_value', 100)
        
        return [{
            'date': datetime.now().strftime('%Y-%m-%d'),
            'prediction': round(avg_value),
            'intervalle_confiance': {
                'min': round(avg_value * 0.7),
                'max': round(avg_value * 1.3)
            },
            'statistiques': {
                'fiabilite': 'basse',
                'confiance': 30.0,
                'message': 'Prédiction de secours - erreur dans le modèle principal'
            },
            'metadata': {
                'establishment': establishment,
                'article': article,
                'is_fallback': True,
                'prediction_timestamp': datetime.now().isoformat()
            }
        }]

    def get_model_info(self, establishment=None, article=None):
        """Retourne les informations sur le modèle"""
        try:
            confidence = self.calculate_prediction_confidence(establishment, article)
            
            return {
                'model_type': 'Prophet Unifié',
                'last_training_date': self.unified_data['last_training_date'],
                'data_freshness': self.check_data_freshness(),
                'confidence_level': confidence,
                'metrics': self.metrics_data['model_metrics'],
                'coverage': {
                    'establishments': len(self.establishments),
                    'articles': len(self.articles),
                    'data_points': self.metrics_data['model_info']['total_data_points']
                },
                'parameters': self.metrics_data['model_info']['prophet_params'],
                'specific_info': {
                    'establishment': {
                        'name': establishment,
                        'found': establishment in self.establishments if establishment else None
                    },
                    'article': {
                        'name': article,
                        'found': article in self.articles if article else None
                    }
                }
            }
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de la récupération des informations du modèle: {str(e)}")
            raise e

def test_predictor():
    """Fonction de test du prédicteur"""
    try:
        predictor = UnifiedPredictor()
        
        # Test 1: Prédiction simple
        print("\n1. Test de prédiction simple")
        tomorrow = datetime.now() + timedelta(days=1)
        predictions = predictor.predict(tomorrow)
        print(f"Prédiction pour demain: {predictions[0]['prediction']} unités")
        
        # Test 2: Prédiction pour un établissement
        print("\n2. Test de prédiction pour un établissement")
        test_establishment = predictor.establishments[0]
        predictions = predictor.predict(tomorrow, establishment=test_establishment)
        print(f"Prédiction pour {test_establishment}: {predictions[0]['prediction']} unités")
        
        # Test 3: Prédiction sur une période
        print("\n3. Test de prédiction sur une période")
        week_dates = pd.date_range(start=tomorrow, periods=7, freq='D')
        predictions = predictor.predict(week_dates)
        print(f"Prédictions sur 7 jours générées: {len(predictions)} prédictions")
        
        # Test 4: Informations sur le modèle
        print("\n4. Informations sur le modèle")
        model_info = predictor.get_model_info()
        print(f"Type de modèle: {model_info['model_type']}")
        print(f"Dernière mise à jour: {model_info['last_training_date']}")
        print(f"Fraîcheur des données: {model_info['data_freshness']}")
        
        print("\n✅ Tests terminés avec succès")
        
    except Exception as e:
        print(f"❌ Erreur lors des tests: {str(e)}")

if __name__ == "__main__":
    test_predictor()