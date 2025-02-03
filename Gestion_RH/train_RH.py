import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
import joblib
import json
from pathlib import Path
import sys
from datetime import datetime, timedelta

# Ajouter le répertoire parent au PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

# Configuration
DATA_DIR = Path(__file__).parent / "data"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = Path(__file__).parent / "models"

# Configuration du modèle SARIMA
SARIMA_CONFIG = {
    'order': (1, 1, 1),
    'seasonal_order': (1, 1, 1, 12)
}

def generate_sample_data():
    """Génère des données d'exemple si les données réelles ne sont pas disponibles."""
    print("Génération de données d'exemple...")
    dates = pd.date_range(start='2023-01-01', end='2024-12-31', freq='D')
    base_staff = 100
    
    # Générer des données avec tendance et saisonnalité
    trend = np.linspace(0, 20, len(dates))  # Tendance croissante
    seasonal = 10 * np.sin(2 * np.pi * np.arange(len(dates)) / 365)  # Saisonnalité annuelle
    noise = np.random.normal(0, 5, len(dates))  # Bruit aléatoire
    
    staff = base_staff + trend + seasonal + noise
    staff = np.maximum(staff, 50)  # Minimum de 50 employés
    
    df = pd.DataFrame({
        'date': dates,
        'staff': staff.astype(int)
    })
    return df

def load_and_prepare_data():
    """Charge ou génère les données d'entraînement."""
    try:
        # Essayer de charger les données réelles
        if PROCESSED_DATA_DIR.exists():
            data_path = PROCESSED_DATA_DIR / "processed_presence_data.csv"
            if data_path.exists():
                print("Chargement des données réelles...")
                df = pd.read_csv(data_path)
                df['date'] = pd.to_datetime(df['date'])
                return df.set_index('date')['staff']
    except Exception as e:
        print(f"Erreur lors du chargement des données réelles : {str(e)}")
    
    # Si les données réelles ne sont pas disponibles, générer des données d'exemple
    df = generate_sample_data()
    return df.set_index('date')['staff']

def train_sarima_model(data):
    """Entraîne le modèle SARIMA avec la configuration spécifiée."""
    try:
        print("Début de l'entraînement du modèle SARIMA...")
        model = SARIMAX(
            data,
            order=SARIMA_CONFIG['order'],
            seasonal_order=SARIMA_CONFIG['seasonal_order']
        )
        fitted_model = model.fit(disp=False)
        print("Entraînement terminé avec succès")
        return fitted_model
    except Exception as e:
        print(f"Erreur lors de l'entraînement : {str(e)}")
        raise

def save_model(model):
    """Sauvegarde le modèle entraîné."""
    try:
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        model_path = MODELS_DIR / "sarima_model.joblib"
        joblib.dump(model, model_path)
        print(f"Modèle sauvegardé avec succès : {model_path}")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde : {str(e)}")
        raise

def save_metrics(metrics):
    """Sauvegarde les métriques du modèle."""
    try:
        metrics_path = MODELS_DIR / "model_metrics.json"
        with open(metrics_path, 'w') as f:
            json.dump(metrics, f, indent=4)
        print(f"Métriques sauvegardées avec succès : {metrics_path}")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des métriques : {str(e)}")
        raise

def main():
    try:
        print("Début du processus d'entraînement...")
        
        # Charger ou générer les données
        data = load_and_prepare_data()
        print(f"Données chargées : {len(data)} points")
        
        # Entraîner le modèle
        model = train_sarima_model(data)
        
        # Sauvegarder le modèle
        save_model(model)
        
        # Calculer et sauvegarder les métriques
        metrics = {
            'aic': model.aic,
            'bic': model.bic,
            'training_time': str(model.elapsed_time),
            'data_points': len(data),
            'training_date': datetime.now().isoformat()
        }
        save_metrics(metrics)
        
        print("Processus d'entraînement terminé avec succès!")
        
    except Exception as e:
        print(f"Erreur dans le processus d'entraînement : {str(e)}")
        raise

if __name__ == "__main__":
    main()
