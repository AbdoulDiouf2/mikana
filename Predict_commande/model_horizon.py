import pandas as pd
import numpy as np
import json
import joblib
from prophet import Prophet
import warnings
from datetime import datetime
import os

# Suppression des avertissements
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

def load_model_metrics():
    """Charge les métriques des modèles"""
    with open('models/metrics.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def predict_exponential_smoothing(horizon):
    """Fait des prédictions avec le modèle ExponentialSmoothing"""
    model = joblib.load('models/exp_smoothing_model.joblib')
    predictions = model.forecast(steps=horizon)
    
    return pd.DataFrame({
        'date': predictions.index,
        'prediction': predictions.values.round(0)
    })

def predict_prophet_global(horizon):
    """Fait des prédictions avec le modèle Prophet global"""
    model = Prophet()
    model.load('models/prophet_model.json')
    
    future = model.make_future_dataframe(periods=horizon)
    forecast = model.predict(future)
    
    results = pd.DataFrame({
        'date': forecast.tail(horizon)['ds'],
        'prediction': forecast.tail(horizon)['yhat'].round(0),
        'limite_basse': forecast.tail(horizon)['yhat_lower'].round(0),
        'limite_haute': forecast.tail(horizon)['yhat_upper'].round(0)
    })
    
    return results

def predict_prophet_article(article_name, horizon):
    """Fait des prédictions pour un article spécifique avec Prophet"""
    model_path = f'models/articles/prophet_{article_name.replace("/", "_")}.json'
    
    if not os.path.exists(model_path):
        raise ValueError(f"Pas de modèle trouvé pour l'article '{article_name}'")
    
    model = Prophet()
    model.load(model_path)
    
    future = model.make_future_dataframe(periods=horizon)
    forecast = model.predict(future)
    
    results = pd.DataFrame({
        'date': forecast.tail(horizon)['ds'],
        'prediction': forecast.tail(horizon)['yhat'].round(0),
        'limite_basse': forecast.tail(horizon)['yhat_lower'].round(0),
        'limite_haute': forecast.tail(horizon)['yhat_upper'].round(0),
        'article': article_name
    })
    
    return results

def get_available_articles():
    """Retourne la liste des articles disponibles"""
    articles = []
    for file in os.listdir('models/articles'):
        if file.startswith('prophet_') and file.endswith('.json'):
            article = file[8:-5].replace('_', '/')  # Supprime 'prophet_' et '.json'
            articles.append(article)
    return articles

def main():
    # Affichage des métriques disponibles
    metrics = load_model_metrics()
    print("\nPerformances des modèles disponibles:")
    print("\n1. Exponential Smoothing:")
    print(f"R2: {metrics['exponential_smoothing']['R2']:.3f}")
    print(f"MAPE: {metrics['exponential_smoothing']['MAPE']:.1f}%")
    
    print("\n2. Prophet Global:")
    print(f"R2: {metrics['prophet_global']['R2']:.3f}")
    print(f"MAPE: {metrics['prophet_global']['MAPE']:.1f}%")
    
    # Menu de sélection
    print("\nTypes de prédiction disponibles:")
    print("1. Prédiction globale avec Exponential Smoothing")
    print("2. Prédiction globale avec Prophet")
    print("3. Prédiction par article avec Prophet")
    
    choice = input("\nChoisissez le type de prédiction (1-3): ")
    horizon = int(input("Horizon de prédiction (max 30 jours): "))
    
    if horizon > 30:
        print("L'horizon est limité à 30 jours maximum.")
        return
    
    try:
        if choice == "1":
            results = predict_exponential_smoothing(horizon)
            print("\nPrédictions Exponential Smoothing:")
            
        elif choice == "2":
            results = predict_prophet_global(horizon)
            print("\nPrédictions Prophet Global:")
            
        elif choice == "3":
            articles = get_available_articles()
            print("\nArticles disponibles:")
            for i, article in enumerate(articles, 1):
                print(f"{i}. {article}")
            
            article_idx = int(input("\nChoisissez un article (numéro): ")) - 1
            if 0 <= article_idx < len(articles):
                results = predict_prophet_article(articles[article_idx], horizon)
                print(f"\nPrédictions Prophet pour {articles[article_idx]}:")
            else:
                print("Choix d'article invalide")
                return
        else:
            print("Choix invalide")
            return
        
        # Affichage des résultats
        pd.set_option('display.max_rows', None)
        print(results)
        
    except Exception as e:
        print(f"Erreur lors de la prédiction: {str(e)}")

if __name__ == "__main__":
    main()