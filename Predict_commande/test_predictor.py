import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from prophet import Prophet
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

# Suppression des avertissements
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# Chargement et préparation des données
df = pd.read_excel("./Data/donnees_finales.xlsx")
df = pd.read_csv("donnees_finales.csv", parse_dates=["Date expédition"], dayfirst=True)
df = df.dropna(subset=["Qté cdée"])
df["Qté cdée"] = pd.to_numeric(df["Qté cdée"], errors='coerce')
df = df.drop_duplicates()

def prepare_series(data):
    ts = data.groupby("Date expédition")["Qté cdée"].sum().sort_index()
    ts.index = pd.DatetimeIndex(ts.index)
    ts = ts.asfreq('D', fill_value=0)
    return ts

def prepare_series_prophet(data, article=None):
    if article:
        data = data[data["Désignation article"] == article]
    
    # Grouper par date et article
    ts = data.groupby(["Date expédition"])["Qté cdée"].sum().reset_index()
    ts.columns = ['ds', 'y']
    ts['ds'] = pd.to_datetime(ts['ds'])
    
    return ts

# Point de départ des prédictions
start_date = pd.Timestamp('2023-04-01')

# Préparation des données pour ExponentialSmoothing
ts = prepare_series(df)
train_data = ts[ts.index < start_date]
test_data = ts[ts.index >= start_date][:21]

def evaluate_progressive_forecast(model_name, train_data, test_data, article=None, forecast_days=21):
    performance_metrics = []
    
    if model_name == "Exponential Smoothing":
        for i in range(1, forecast_days + 1):
            try:
                model = ExponentialSmoothing(
                    train_data,
                    seasonal_periods=7,
                    trend='add',
                    seasonal='add'
                )
                model_fit = model.fit(optimized=True)
                predictions = model_fit.forecast(steps=i)
                
                actual = test_data[:i]
                if len(actual) > 0 and len(predictions) > 0:
                    metrics = {
                        'horizon': i,
                        'R2': r2_score(actual, predictions),
                        'MAPE': np.mean(np.abs((actual - predictions) / actual)) * 100,
                        'RMSE': np.sqrt(mean_squared_error(actual, predictions))
                    }
                    performance_metrics.append(metrics)
                
            except Exception as e:
                print(f"Erreur Exp. Smoothing à l'horizon {i}: {e}")
                
    elif model_name == "Prophet":
        # Préparation des données spécifiques à Prophet
        if article:
            ts_prophet = prepare_series_prophet(df, article)
        else:
            ts_prophet = prepare_series_prophet(df)
        
        train_prophet = ts_prophet[ts_prophet['ds'] < start_date]
        test_prophet = ts_prophet[ts_prophet['ds'] >= start_date]
        test_prophet = test_prophet[test_prophet['ds'] < start_date + pd.Timedelta(days=21)]
        
        for i in range(1, forecast_days + 1):
            try:
                model = Prophet(daily_seasonality=True, weekly_seasonality=True)
                model.fit(train_prophet)
                
                future = model.make_future_dataframe(periods=i, freq='D')
                forecast = model.predict(future)
                predictions = forecast.tail(i)['yhat'].values
                
                actual = test_prophet['y'].values[:i]
                if len(actual) > 0 and len(predictions) > 0:
                    metrics = {
                        'horizon': i,
                        'R2': r2_score(actual, predictions),
                        'MAPE': np.mean(np.abs((actual - predictions) / actual)) * 100,
                        'RMSE': np.sqrt(mean_squared_error(actual, predictions))
                    }
                    performance_metrics.append(metrics)
                
            except Exception as e:
                print(f"Erreur Prophet à l'horizon {i}: {e}")
    
    return pd.DataFrame(performance_metrics)

# Exemple d'utilisation avec un article spécifique
article_test = "ALESE LOCATION"  # Choisir un article spécifique
exp_metrics = evaluate_progressive_forecast("Exponential Smoothing", train_data, test_data)
prophet_metrics = evaluate_progressive_forecast("Prophet", train_data, test_data, article=article_test)

# Visualisation des performances
if not prophet_metrics.empty and not exp_metrics.empty:
    plt.figure(figsize=(15, 10))

    # R2 Score
    plt.subplot(3, 1, 1)
    plt.plot(exp_metrics['horizon'], exp_metrics['R2'], label='Exp. Smoothing', marker='o')
    plt.plot(prophet_metrics['horizon'], prophet_metrics['R2'], label=f'Prophet (Article: {article_test})', marker='o')
    plt.title('Évolution du R² selon l\'horizon de prédiction')
    plt.xlabel('Jours')
    plt.ylabel('R²')
    plt.legend()
    plt.grid(True)

    # MAPE
    plt.subplot(3, 1, 2)
    plt.plot(exp_metrics['horizon'], exp_metrics['MAPE'], label='Exp. Smoothing', marker='o')
    plt.plot(prophet_metrics['horizon'], prophet_metrics['MAPE'], label=f'Prophet (Article: {article_test})', marker='o')
    plt.title('Évolution du MAPE selon l\'horizon de prédiction')
    plt.xlabel('Jours')
    plt.ylabel('MAPE (%)')
    plt.legend()
    plt.grid(True)

    # RMSE
    plt.subplot(3, 1, 3)
    plt.plot(exp_metrics['horizon'], exp_metrics['RMSE'], label='Exp. Smoothing', marker='o')
    plt.plot(prophet_metrics['horizon'], prophet_metrics['RMSE'], label=f'Prophet (Article: {article_test})', marker='o')
    plt.title('Évolution du RMSE selon l\'horizon de prédiction')
    plt.xlabel('Jours')
    plt.ylabel('RMSE')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()

    # Affichage des métriques
    print("\nMétriques Exponential Smoothing :")
    print(exp_metrics)
    print(f"\nMétriques Prophet (Article: {article_test}) :")
    print(prophet_metrics)