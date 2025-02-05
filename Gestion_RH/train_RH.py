import joblib
import pandas as pd
import json
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from statsmodels.tsa.statespace.sarimax import SARIMAX

# Définir le chemin du modèle
MODEL_PATH = 'sarima_model.joblib'
DATA_PATH = 'Total_Presents_Final.xlsx'

# Charger les données
print("Chargement des données...")
df = pd.read_excel(DATA_PATH)
df['Date'] = pd.to_datetime(df['Date'])
df.set_index('Date', inplace=True)
time_series = df['Presences']

# Diviser en train/test
train = time_series[:-10]
test = time_series[-10:]

# Paramètres du modèle SARIMA
p, d, q = 2, 1, 2
P, D, Q, s = 1, 1, 1, 52

print("Entraînement du modèle SARIMA...")
model = SARIMAX(train, order=(p, d, q), seasonal_order=(P, D, Q, s), 
                 enforce_stationarity=False, enforce_invertibility=False)
sarima_model = model.fit(disp=False)

# Sauvegarder le modèle
joblib.dump(sarima_model, MODEL_PATH)
print(f"Modèle entraîné et sauvegardé sous {MODEL_PATH}")

# Faire des prédictions sur l'ensemble de test pour calculer les métriques
test_predictions = sarima_model.get_forecast(steps=len(test))
test_predictions = test_predictions.predicted_mean

# Calculer les métriques de performance sur l'ensemble de test
rmse = np.sqrt(mean_squared_error(test, test_predictions))
mae = mean_absolute_error(test, test_predictions)
r2 = r2_score(test, test_predictions)

# Sauvegarder les métriques du modèle
metrics = {
    'performance_metrics': {
        'rmse': float(rmse),
        'mae': float(mae),
        'r2': float(r2)
    },
    'statistical_metrics': {
        'aic': float(sarima_model.aic),
        'bic': float(sarima_model.bic),
        'loglikelihood': float(sarima_model.llf)
    },
    'params': {
        'p': p, 'd': d, 'q': q,
        'P': P, 'D': D, 'Q': Q, 's': s
    },
    'test_set_info': {
        'test_size': len(test),
        'test_period': f"du {test.index[0].strftime('%Y-%m-%d')} au {test.index[-1].strftime('%Y-%m-%d')}"
    }
}

with open('Gestion_RH/model_metrics.json', 'w') as f:
    json.dump(metrics, f, indent=4)
print("Métriques du modèle sauvegardées dans model_metrics.json")
print(f"\nPerformances du modèle sur l'ensemble de test:")
print(f"RMSE: {rmse:.2f}")
print(f"MAE: {mae:.2f}")
print(f"R²: {r2:.2f}")
print(f"Période de test: {metrics['test_set_info']['test_period']}")
