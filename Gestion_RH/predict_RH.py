import pandas as pd
import numpy as np
import joblib
from datetime import datetime, timedelta
from ..config import *

def load_model():
    """Charge le modèle entraîné."""
    model_path = MODELS_DIR / "sarima_model.joblib"
    return joblib.load(model_path)

def generate_future_dates(start_date, periods):
    """Génère les dates futures pour la prédiction."""
    return pd.date_range(start=start_date, periods=periods, freq='D')

def make_predictions(model, start_date, periods=PREDICTION_HORIZON):
    """Génère les prédictions pour la période spécifiée."""
    # Faire les prédictions
    forecast = model.get_forecast(steps=periods)
    
    # Obtenir les prédictions et les intervalles de confiance
    mean_forecast = forecast.predicted_mean
    confidence_int = forecast.conf_int(alpha=1-CONFIDENCE_INTERVAL)
    
    # Créer un DataFrame avec les résultats
    future_dates = generate_future_dates(start_date, periods)
    
    results = pd.DataFrame({
        'date': future_dates,
        'prediction': mean_forecast,
        'lower_bound': confidence_int.iloc[:, 0],
        'upper_bound': confidence_int.iloc[:, 1]
    })
    
    return results

def save_predictions(predictions):
    """Sauvegarde les prédictions dans un fichier."""
    output_path = PROCESSED_DATA_DIR / f"predictions_{datetime.now().strftime('%Y%m%d')}.csv"
    predictions.to_csv(output_path, index=False)
    return output_path

def main():
    """Point d'entrée principal pour la génération des prédictions."""
    # Charger le modèle
    model = load_model()
    
    # Définir la date de début des prédictions
    start_date = datetime.now()
    
    # Générer les prédictions
    predictions = make_predictions(model, start_date)
    
    # Sauvegarder les résultats
    output_path = save_predictions(predictions)
    print(f"Prédictions sauvegardées dans : {output_path}")

if __name__ == "__main__":
    main()
