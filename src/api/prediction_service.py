from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
import pandas as pd
from model_prophet import PredicteurTemporel

app = FastAPI()

# Configuration CORS modifiée
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialisation du prédicteur
predicteur = PredicteurTemporel()

class PredictionRequest(BaseModel):
    dateType: str
    date: str
    endDate: Optional[str] = None
    establishment: Optional[str] = None
    linenType: Optional[str] = None
    factors: List[str]

@app.get("/api/establishments")
async def get_establishments():
    try:
        establishments = predicteur.df_historique['ETBDES'].unique().tolist()
        return {"establishments": establishments}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/linen-types")
async def get_linen_types():
    try:
        linen_types = predicteur.df_historique['ARTDES'].unique().tolist()
        return {"linenTypes": linen_types}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/predict")
async def predict(request: PredictionRequest):
    try:
        print("\n=== Nouvelle requête de prédiction ===")
        print(f"Type de date: {request.dateType}")
        print(f"Date: {request.date}")
        print(f"Date fin: {request.endDate}")
        print(f"Établissement: {request.establishment}")
        
        if request.dateType == 'single':
            # Cas d'une seule date
            dates_prediction = pd.DatetimeIndex([pd.to_datetime(request.date)])
            print(f"Date unique: {request.date}")
        elif request.dateType == 'period':
            # Cas d'une période
            start_date = pd.to_datetime(request.date)
            end_date = pd.to_datetime(request.endDate)
            dates_prediction = pd.date_range(
                start=start_date,
                end=end_date,
                freq='D',
                inclusive='both'
            )
            print(f"Période: du {request.date} au {request.endDate}")
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Type de date invalide: {request.dateType}. Attendu: 'single' ou 'period'"
            )

        print(f"Dates à traiter: {[d.strftime('%Y-%m-%d') for d in dates_prediction]}")
        
        predictions = predicteur.predire(
            dates_prediction=dates_prediction,
            etablissement=request.establishment if request.establishment else None,
            article=request.linenType if request.linenType else None
        )
        
        return {"predictions": predictions}
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 

@app.get("/api/historical-data")
async def get_historical_data(establishment: str = None, linenType: str = None, month: int = None, day: int = None):
    try:
        print(f"\n=== Recherche données historiques ===")
        print(f"Établissement: {establishment}")
        print(f"Type de linge: {linenType}")
        print(f"Date: {day}/{month}")

        # Convertir les colonnes de date
        df_filtered = predicteur.df_historique.copy()
        df_filtered['DATE'] = pd.to_datetime(df_filtered['DATE'])

        # Appliquer les filtres seulement s'ils sont spécifiés
        if establishment:
            df_filtered = df_filtered[df_filtered['ETBDES'] == establishment]
        if linenType:
            df_filtered = df_filtered[df_filtered['ARTDES'] == linenType]

        # Filtrer par jour et mois
        historical_data = df_filtered[
            (df_filtered['DATE'].dt.month == month) &
            (df_filtered['DATE'].dt.day == day)
        ]

        print("Données filtrées:", historical_data)

        # Grouper par année
        historical_values = historical_data.groupby(historical_data['DATE'].dt.year)['QUANTITE'].sum()
        
        print("Valeurs par année:", historical_values)

        # Convertir en dictionnaire et gérer les valeurs manquantes
        values_dict = historical_values.to_dict()

        return {
            "value2024": float(values_dict.get(2024, 0)),
            "value2023": float(values_dict.get(2023, 0)),
            "date": f"{day:02d}/{month:02d}",
            "establishment": establishment,
            "linenType": linenType
        }

    except Exception as e:
        print(f"❌ Erreur lors de la récupération des données historiques: {str(e)}")
        print(f"Pour: {establishment}, {linenType}, {month}/{day}")
        raise HTTPException(status_code=500, detail=str(e)) 

@app.get("/api/seasonal-trends")
async def get_seasonal_trends(establishment: str = None, linenType: str = None):
    try:
        df = predicteur.df_historique.copy()
        df['DATE'] = pd.to_datetime(df['DATE'])

        # Filtrer par établissement et type de linge si spécifiés
        if establishment:
            df = df[df['ETBDES'] == establishment]
        if linenType:
            df = df[df['ARTDES'] == linenType]

        # Extraire le mois et calculer la moyenne par mois
        df['month'] = df['DATE'].dt.month
        df['year'] = df['DATE'].dt.year
        
        # Grouper par mois et année et calculer la MOYENNE au lieu de la somme
        monthly_data = df.groupby(['year', 'month'])['QUANTITE'].mean().reset_index()
        
        # Créer une matrice pour le graphique
        heatmap_data = []
        years = sorted(monthly_data['year'].unique().tolist())
        
        for year in years:
            year_data = monthly_data[monthly_data['year'] == year]
            monthly_values = []
            for month in range(1, 13):
                value = float(year_data[year_data['month'] == month]['QUANTITE'].iloc[0]) if month in year_data['month'].values else 0.0
                monthly_values.append(value)
            heatmap_data.append({
                'year': int(year),
                'values': monthly_values
            })

        return {
            "years": [int(y) for y in years],
            "months": list(range(1, 13)),
            "data": heatmap_data
        }

    except Exception as e:
        print(f"❌ Erreur lors de la récupération des tendances saisonnières: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 

@app.get("/api/weather-impact")
async def get_weather_impact(establishment: str = None, linenType: str = None):
    try:
        df = predicteur.df_historique.copy()
        df['DATE'] = pd.to_datetime(df['DATE'])

        # Simuler des données météo (à remplacer par de vraies données)
        # Vous pouvez intégrer une API météo comme OpenWeatherMap ici
        weather_data = {
            'temperature': {
                'low': df['QUANTITE'].mean() * 0.8,    # Impact négatif
                'medium': df['QUANTITE'].mean(),        # Impact neutre
                'high': df['QUANTITE'].mean() * 1.2     # Impact positif
            },
            'precipitation': {
                'none': df['QUANTITE'].mean() * 1.1,    # Impact positif
                'light': df['QUANTITE'].mean(),         # Impact neutre
                'heavy': df['QUANTITE'].mean() * 0.9    # Impact négatif
            },
            'humidity': {
                'low': df['QUANTITE'].mean() * 0.9,
                'medium': df['QUANTITE'].mean(),
                'high': df['QUANTITE'].mean() * 1.1
            }
        }

        # Calculer les corrélations
        correlations = {
            'temperature': {
                'impact': 0.7,  # Corrélation positive forte
                'values': [
                    {'condition': 'Basse (<15°C)', 'volume': float(weather_data['temperature']['low'])},
                    {'condition': 'Moyenne (15-25°C)', 'volume': float(weather_data['temperature']['medium'])},
                    {'condition': 'Haute (>25°C)', 'volume': float(weather_data['temperature']['high'])}
                ]
            },
            'precipitation': {
                'impact': -0.5,  # Corrélation négative modérée
                'values': [
                    {'condition': 'Aucune', 'volume': float(weather_data['precipitation']['none'])},
                    {'condition': 'Légère', 'volume': float(weather_data['precipitation']['light'])},
                    {'condition': 'Forte', 'volume': float(weather_data['precipitation']['heavy'])}
                ]
            },
            'humidity': {
                'impact': 0.3,  # Corrélation positive faible
                'values': [
                    {'condition': 'Faible (<40%)', 'volume': float(weather_data['humidity']['low'])},
                    {'condition': 'Moyenne (40-60%)', 'volume': float(weather_data['humidity']['medium'])},
                    {'condition': 'Élevée (>60%)', 'volume': float(weather_data['humidity']['high'])}
                ]
            }
        }

        return correlations

    except Exception as e:
        print(f"❌ Erreur lors de l'analyse de l'impact météorologique: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 