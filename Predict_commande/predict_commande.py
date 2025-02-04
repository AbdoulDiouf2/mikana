import pandas as pd
import joblib
import json
from prophet import Prophet

def load_metrics():
    with open('models/metrics.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def predict_exponential_smoothing(horizon):
    model = joblib.load('models/exp_smoothing_model.joblib')
    forecast = model.forecast(steps=horizon)
    return pd.DataFrame({'date': forecast.index, 'prediction': forecast.values.round(0)})

def predict_prophet_global(horizon):
    model = Prophet()
    model = joblib.load('models/prophet_model.json')
    future = model.make_future_dataframe(periods=horizon)
    forecast = model.predict(future)
    return forecast[['ds', 'yhat']].tail(horizon).rename(columns={'ds': 'date', 'yhat': 'prediction'})

def predict_prophet_article(article, date):
    model = joblib.load('models/prophet_articles_model.joblib')
    future = pd.DataFrame({'ds': [date], 'article': [article]})
    forecast = model.predict(future)
    return forecast[['ds', 'yhat']].rename(columns={'ds': 'date', 'yhat': 'prediction'})

def main():
    print("\nPerformances des modèles disponibles:")
    metrics = load_metrics()
    for model_name, metric in metrics.items():
        print(f"{model_name}: R2={metric['R2']:.3f}, MAPE={metric['MAPE']:.1f}%")

    print("\nTypes de prédictions disponibles:")
    print("1. Prédiction Exponential Smoothing")
    print("2. Prédiction Prophet global")
    print("3. Prédiction Prophet par article")
    
    choice = input("Choisissez le type de prédiction (1-3): ")
    
    if choice == "1":
        horizon = int(input("Entrez l'horizon de prédiction (jours): "))
        result = predict_exponential_smoothing(horizon)

    elif choice == "2":
        horizon = int(input("Entrez l'horizon de prédiction (jours): "))
        result = predict_prophet_global(horizon)

    elif choice == "3":
        article = input("Entrez le nom de l'article: ")
        date = input("Entrez la date de prédiction (YYYY-MM-DD): ")
        result = predict_prophet_article(article, date)

    else:
        print("Choix invalide")
        return

    print("\nRésultats de la prédiction:")
    print(result)

if __name__ == "__main__":
    main()
