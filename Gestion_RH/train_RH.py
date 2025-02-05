import joblib
import pandas as pd
import json
import numpy as np
from datetime import datetime, timedelta
from statsmodels.tsa.statespace.sarimax import SARIMAX
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Sauvegarde et rechargement du modèle
MODEL_PATH = 'sarima_model.joblib'
METRICS_PATH = 'model_metrics.json'

# Définir le chemin du fichier d'entrée
input_file = 'Total_Presents_Final.xlsx'

# Charger les données consolidées
df = pd.read_excel(input_file)
df['Annee'] = df['Annee'].fillna(method='ffill')
df = df.dropna(subset=['Semaines', 'Presences'])
df['Semaines'] = df['Semaines'].str.extract(r'(\d+)').astype(int)

# Convertir Année et Semaines en Date
def year_week_to_date(year, week):
    first_day = datetime(year, 1, 1)
    first_week_start = first_day + timedelta(days=(7 - first_day.weekday()))  # Premier lundi
    return first_week_start + timedelta(weeks=week - 1)

df['Date'] = df.apply(lambda row: year_week_to_date(int(row['Annee']), int(row['Semaines'])), axis=1)
df.set_index('Date', inplace=True)
time_series = df['Presences']

# Diviser en train/test
train = time_series[:-10]
test = time_series[-10:]

# Vérifier si le modèle est déjà sauvegardé
try:
    sarima_model = joblib.load(MODEL_PATH)
    print("Modèle chargé depuis", MODEL_PATH)
except FileNotFoundError:
    # Si le modèle n'existe pas, l'entraîner et le sauvegarder
    p, d, q = 2, 1, 2
    P, D, Q, s = 1, 1, 1, 52
    model = SARIMAX(train, order=(p, d, q), seasonal_order=(P, D, Q, s), enforce_stationarity=False, enforce_invertibility=False)
    sarima_model = model.fit(disp=False)
    joblib.dump(sarima_model, MODEL_PATH)
    print("Modèle entraîné et sauvegardé dans", MODEL_PATH)

# Prédictions et calcul des métriques
forecast = sarima_model.get_forecast(steps=len(test))
forecast_mean = forecast.predicted_mean
forecast_ci = forecast.conf_int()

# Calcul des métriques
mae = mean_absolute_error(test, forecast_mean)
rmse = np.sqrt(mean_squared_error(test, forecast_mean))
r2 = r2_score(test, forecast_mean)
accuracy = 100 - (mae / test.mean() * 100)  # Calcul de la précision comme avant

# Création du dictionnaire des métriques
metrics = {
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "test_r2": r2,
    "test_mae": mae,
    "test_rmse": rmse,
    "accuracy_percentage": accuracy
}

# Sauvegarde des métriques en JSON
with open(METRICS_PATH, 'w') as f:
    json.dump(metrics, f, indent=4)

print("Métriques sauvegardées dans", METRICS_PATH)
print("\nRésumé des métriques :")
print(f"R² Score : {r2:.4f}")
print(f"MAE : {mae:.4f}")
print(f"RMSE : {rmse:.4f}")
print(f"Précision (%) : {accuracy:.2f}%")

# Sauvegarder les modifications dans le modèle
joblib.dump(sarima_model, MODEL_PATH)
print("\nModèle mis à jour et resauvegardé.")

# Afficher quelques détails sur les prédictions pour diagnostic
print("\nDiagnostic des prédictions :")
print(f"Moyenne des valeurs réelles : {test.mean():.2f}")
print(f"Moyenne des prédictions : {forecast_mean.mean():.2f}")
print(f"Écart-type des valeurs réelles : {test.std():.2f}")
print(f"Écart-type des prédictions : {forecast_mean.std():.2f}")

# Décommenter cette section pour afficher les prédictions futures et le graphique
"""
# Prédictions futures
future_forecast = sarima_model.get_forecast(steps=30)
future_index = pd.date_range(start=time_series.index[-1] + timedelta(weeks=1), periods=30, freq='W-MON')
future_mean = future_forecast.predicted_mean
future_ci = future_forecast.conf_int()

# Affichage des prédictions et des intervalles de confiance
plt.figure(figsize=(12, 6))
plt.plot(train, label='Données réelles (Entraînement)', color='blue')
plt.plot(test, label='Données réelles (Test)', color='orange')
plt.fill_between(forecast_mean.index, forecast_ci.iloc[:, 0], forecast_ci.iloc[:, 1], color='green', alpha=0.2)
plt.plot(future_index, future_mean, label='Prédictions futures', color='red')
plt.fill_between(future_index, future_ci.iloc[:, 0], future_ci.iloc[:, 1], color='red', alpha=0.2)
plt.xlim(train.index.min(), future_index.max())
plt.title("Prédictions des présences avec SARIMA")
plt.xlabel("Date")
plt.ylabel("Présences")
plt.legend()
plt.grid()
plt.show()

# Affichage des prédictions futures
print("Prédictions pour les 30 prochaines semaines :")
for date, pred in zip(future_index, future_mean):
    print(f"{date.strftime('%Y-%m-%d')} : {pred:.2f} présences")
"""