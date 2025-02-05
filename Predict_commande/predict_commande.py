import pandas as pd
import numpy as np
import json
import joblib
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from prophet import Prophet
from sklearn.metrics import r2_score, mean_absolute_percentage_error
import os

# Créer le dossier models s'il n'existe pas
os.makedirs('models/articles', exist_ok=True)

def train_exponential_smoothing(df):
    model = ExponentialSmoothing(df['y'], trend='add', seasonal='add', seasonal_periods=12)
    model_fit = model.fit()
    joblib.dump(model_fit, 'models/exp_smoothing_model.joblib')
    predictions = model_fit.fittedvalues
    
    return {
        'R2': r2_score(df['y'], predictions),
        'MAPE': mean_absolute_percentage_error(df['y'], predictions) * 100
    }

def train_prophet_global(df):
    model = Prophet()
    model.fit(df)
    model.save('models/prophet_model.json')
    forecast = model.predict(df)
    
    return {
        'R2': r2_score(df['y'], forecast['yhat']),
        'MAPE': mean_absolute_percentage_error(df['y'], forecast['yhat']) * 100
    }

def train_prophet_articles(df):
    articles_metrics = {}
    model = Prophet()
    model.add_regressor('article')
    model.fit(df)
    joblib.dump(model, 'models/prophet_articles_model.joblib')
    forecast = model.predict(df)

    articles_metrics['global'] = {
        'R2': r2_score(df['y'], forecast['yhat']),
        'MAPE': mean_absolute_percentage_error(df['y'], forecast['yhat']) * 100
    }

    return articles_metrics

def main():
    df = pd.read_csv('donnees_finales.csv')  # Assurez-vous d'avoir ce fichier
    df['ds'] = pd.to_datetime(df['date'])
    df['y'] = df['quantite']
    
    metrics = {}
    
    # Entraînement des modèles
    print("Entraînement du modèle Exponential Smoothing...")
    metrics['exponential_smoothing'] = train_exponential_smoothing(df)
    
    print("Entraînement du modèle Prophet global...")
    metrics['prophet_global'] = train_prophet_global(df[['ds', 'y']])

    print("Entraînement du modèle Prophet par article...")
    metrics['prophet_articles'] = train_prophet_articles(df[['ds', 'y', 'article']])

    # Sauvegarde des métriques
    with open('models/metrics.json', 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=4)
    
    print("Entraînement terminé. Les modèles et les métriques ont été sauvegardés.")

if __name__ == "__main__":
    main()