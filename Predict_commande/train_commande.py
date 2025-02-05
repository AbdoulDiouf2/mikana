import pandas as pd
import numpy as np
from prophet import Prophet
import logging
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import json

class PredicteurTemporel:
    def __init__(self, chemin_donnees='donnees_completes_logistique_formatted.csv'):
        """Initialise le prédicteur avec Prophet"""
        self.models = {}  # Dictionnaire pour stocker les modèles par établissement/article
        
        # Configuration du logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        try:
            # Chargement des données
            self.df_historique = pd.read_csv(chemin_donnees, low_memory=False)
            self.df_historique['DATE'] = pd.to_datetime(self.df_historique['DATE'])
            self.logger.info("✅ Prédicteur temporel initialisé")
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de l'initialisation: {str(e)}")
            raise e

    def split_data(self, df, split_ratio=0.8):
        """Sépare les données en train/test (80/20 par défaut)"""
        split_point = int(len(df) * split_ratio)
        train_data = df.iloc[:split_point]
        test_data = df.iloc[split_point:]
        return train_data, test_data

    def preparer_donnees_prophet(self, df):
        """Prépare les données pour Prophet"""
        df_agg = df.groupby('DATE')['QUANTITE'].sum().reset_index()
        df_prophet = df_agg.rename(columns={'DATE': 'ds', 'QUANTITE': 'y'})
        return df_prophet

    def entrainer_modele(self, df_train):
        """Entraîne un modèle Prophet"""
        model = Prophet(
            changepoint_prior_scale=0.05,
            seasonality_prior_scale=1.0,
            seasonality_mode='multiplicative',
            daily_seasonality=True
        )
        model.fit(df_train)
        return model

    def predire(self, model, df_test):
        """Prédit les valeurs sur les données de test"""
        future = pd.DataFrame({'ds': df_test['ds']})
        forecast = model.predict(future)
        return forecast

    def evaluer_performances(self, y_true, y_pred):
        """Calcule les métriques de performance"""
        metrics = {
            'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
            'mae': mean_absolute_error(y_true, y_pred),
            'r2': r2_score(y_true, y_pred)
        }
        return metrics

# Code de test
if __name__ == "__main__":
    predicteur = PredicteurTemporel()

    # Séparation des données (80% entraînement, 20% test)
    train_data, test_data = predicteur.split_data(predicteur.df_historique)

    # Préparation des données
    df_train_prophet = predicteur.preparer_donnees_prophet(train_data)
    df_test_prophet = predicteur.preparer_donnees_prophet(test_data)

    # Entraînement du modèle
    modele = predicteur.entrainer_modele(df_train_prophet)

    # Prédictions sur les données de test
    previsions = predicteur.predire(modele, df_test_prophet)

    # Évaluation des performances
    metrics = predicteur.evaluer_performances(df_test_prophet['y'].values, previsions['yhat'].values)

    # Export des metrics en JSON
    metrics['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    metrics['test_r2'] = metrics.pop('r2')
    metrics['test_mae'] = metrics.pop('mae')
    metrics['test_rmse'] = metrics.pop('rmse')
    with open('./trained_models/model_metrics.json', 'w') as f:
        json.dump(metrics, f, indent=4)
