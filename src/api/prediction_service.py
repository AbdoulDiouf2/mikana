from fastapi import FastAPI, HTTPException, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Dict, Any
import pandas as pd
from model_prophet import PredicteurTemporel
from Planif_Livraisons.predict import predict_delivery
from io import BytesIO
from fastapi.responses import StreamingResponse, FileResponse
from sqlalchemy.orm import Session
from .database import get_db, PredictionHistory
import joblib
import os
import numpy as np
from pathlib import Path
import uuid
import aioredis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph

app = FastAPI()

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)                                                                                                                                                                                                                                                                                               

# @app.get("/")
# async def root():
#     return {"message": "API de prédiction RH active"}

# Initialisation du prédicteur
predicteur = PredicteurTemporel()

# Initialisation du prédicteur RH
# hr_predictor = HRPredictor()

class PredictionRequest(BaseModel):
    dateType: str
    date: str
    endDate: Optional[str] = None
    establishment: Optional[str] = None
    linenType: Optional[str] = None
    factors: List[str]

class DeliveryPredictionRequest(BaseModel):
    date: str
    article: str
    quantity: float

class Alert(BaseModel):
    id: str
    type: str
    message: str
    severity: str
    timestamp: datetime
    department: Optional[str] = None
    status: str = "active"
    value: Optional[float] = None
    threshold: Optional[float] = None
    date: Optional[str] = None

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

# @app.post("/api/predict-delivery")
# async def predict_delivery_endpoint(
#     request: DeliveryPredictionRequest,
#     db: Session = Depends(get_db)
# ):
#     try:
#         # Convertir la date ISO en datetime
#         delivery_date = datetime.fromisoformat(request.date.replace('Z', '+00:00'))
#         
#         # Appeler la fonction de prédiction
#         result = predict_delivery(
#             date=delivery_date,
#             article=request.article,
#             quantity=request.quantity
#         )
#         
#         # Créer l'entrée dans l'historique
#         history_entry = PredictionHistory(
#             date=delivery_date.date(),  # Stocker seulement la date
#             article=request.article,
#             quantity_ordered=request.quantity,
#             quantity_predicted=result["predicted_quantity"],
#             delivery_rate=result["delivery_rate"],
#             status=result["status"],
#             recommendation=result["recommendation"],
#             created_at=datetime.now()
#         )
#         
#         db.add(history_entry)
#         db.commit()
#         
#         return result
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Erreur lors de la prédiction: {str(e)}")

@app.post("/api/predict-delivery")
async def predict_delivery_endpoint(
   request: DeliveryPredictionRequest,
   db: Session = Depends(get_db)
):
   try:
       # Convertir la date ISO en datetime
       delivery_date = datetime.fromisoformat(request.date.replace('Z', '+00:00'))

       # Appeler la fonction de prédiction
       result = predict_delivery(
           date=delivery_date,
           article=request.article,
           quantity=request.quantity
       )

       # Créer l'entrée dans l'historique avec une requête SQL directe
       query = """
           INSERT INTO prediction_history 
           (date, article, quantity_ordered, quantity_predicted, delivery_rate, status, recommendation, created_at)
           VALUES 
           (:date, :article, :quantity_ordered, :quantity_predicted, :delivery_rate, :status, :recommendation, :created_at)
       """
        
       db.execute(query, {
           "date": delivery_date,
           "article": request.article,
           "quantity_ordered": request.quantity,
           "quantity_predicted": result["predicted_quantity"],
           "delivery_rate": result["delivery_rate"],
           "status": result["status"],
           "recommendation": result["recommendation"],
           "created_at": datetime.now()
       })
        
       db.commit()
       
       return result

   except Exception as e:
       raise HTTPException(status_code=500, detail=f"Erreur lors de la prédiction: {str(e)}")

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

@app.get("/api/articles")
async def get_articles(db: Session = Depends(get_db)):
    try:
        # Requête SQL pour récupérer les articles uniques
        query = """
            SELECT DISTINCT `Désignation article` as article
            FROM livraisons 
            ORDER BY `Désignation article`
        """
        
        articles = db.execute(query).fetchall()
        # Convertir les résultats en liste
        articles_list = [row[0] for row in articles]
        
        # print(f"Articles trouvés dans la BD: {articles_list}")
        return {"articles": articles_list}
        
    except Exception as e:
        print(f"Erreur lors de la récupération des articles: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history")
async def get_prediction_history(
    db: Session = Depends(get_db),
    limit: int = 10,
    offset: int = 0
):
    try:
        total = db.execute("SELECT COUNT(*) FROM prediction_history").scalar()
        query = f"""
            SELECT * FROM prediction_history 
            ORDER BY created_at DESC 
            LIMIT {limit} OFFSET {offset}
        """
        records = db.execute(query).fetchall()
        
        result = [{
            "id": row[0],
            "date": str(row[1]),
            "article": row[2],
            "quantity_ordered": float(row[3]),
            "quantity_predicted": float(row[4]),
            "delivery_rate": float(row[5]),
            "status": row[6],
            "recommendation": row[7],
            "created_at": str(row[8])
        } for row in records]
        
        print("Résultat formaté (premières lignes):")
        for r in result[:3]:
            print(r)

        return {
            "success": True,
            "data": result,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"success": False, "error": str(e)}

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://redis:6379", encoding="utf8")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

@app.get("/api/export/{format}")
async def export_predictions(
    format: str,
    db: Session = Depends(get_db),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    try:
        query = db.query(PredictionHistory)
        
        if start_date:
            query = query.filter(PredictionHistory.created_at >= start_date)
        if end_date:
            query = query.filter(PredictionHistory.created_at <= end_date)
            
        predictions = query.order_by(PredictionHistory.created_at.desc()).all()
        
        # Convertir en DataFrame
        df = pd.DataFrame([{
            "Date de livraison": p.date,
            "Article": p.article,
            "Quantité commandée": p.quantity_ordered,
            "Quantité prévue": p.quantity_predicted,
            "Taux de livraison (%)": p.delivery_rate,
            "Statut": p.status,
            "Recommandation": p.recommendation,
            "Date de prédiction": p.created_at
        } for p in predictions])
        
        if format.lower() == "excel":
            # Export Excel (inchangé)
            output = BytesIO()
            df.to_excel(output, index=False, sheet_name="Prédictions")
            output.seek(0)
            
            return StreamingResponse(
                output,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": f"attachment; filename=predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"}
            )
        elif format.lower() == "pdf":
            # Création du PDF
            output = BytesIO()
            doc = SimpleDocTemplate(
                output,
                pagesize=landscape(letter),
                rightMargin=30,
                leftMargin=30,
                topMargin=30,
                bottomMargin=30
            )
            
            elements = []
            
            # Style pour le titre
            styles = getSampleStyleSheet()
            title = Paragraph("Historique des Prédictions", styles['Title'])
            elements.append(title)
            
            # Préparation des données pour le tableau
            data = [list(df.columns)]  # En-têtes
            for _, row in df.iterrows():
                formatted_row = []
                for item in row:
                    if isinstance(item, (datetime, pd.Timestamp)):
                        formatted_row.append(item.strftime('%d/%m/%Y'))
                    elif isinstance(item, float):
                        formatted_row.append(f"{item:.2f}")
                    else:
                        formatted_row.append(str(item))
                data.append(formatted_row)
            
            # Création du tableau
            table = Table(data, repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
            ]))
            
            elements.append(table)
            
            # Construction du document
            doc.build(elements)
            
            output.seek(0)
            return StreamingResponse(
                output,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename=predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                }
            )
        else:
            raise HTTPException(status_code=400, detail="Format non supporté. Utilisez 'excel' ou 'pdf'")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'export: {str(e)}")

@app.get("/api/delivery-stats")
async def get_delivery_stats(db: Session = Depends(get_db)):
    try:
        # Tendance annuelle
        yearly_trend = db.execute("""
            SELECT YEAR(`Date expédition`) as year, SUM(`Qté livrée`) as delivered 
            FROM livraisons 
            GROUP BY YEAR(`Date expédition`)
            ORDER BY year
        """).fetchall()

        # Comparaison mensuelle
        monthly_comparison = db.execute("""
            SELECT 
                DATE_FORMAT(`Date expédition`, '%b') as month,
                SUM(CASE WHEN YEAR(`Date expédition`) = 2022 THEN `Qté livrée` ELSE 0 END) as year2022,
                SUM(CASE WHEN YEAR(`Date expédition`) = 2023 THEN `Qté livrée` ELSE 0 END) as year2023,
                SUM(CASE WHEN YEAR(`Date expédition`) = 2024 THEN `Qté livrée` ELSE 0 END) as year2024
            FROM livraisons 
            GROUP BY MONTH(`Date expédition`), month
            ORDER BY MONTH(`Date expédition`)
        """).fetchall()

        # Distribution articles
        article_distribution = db.execute("""
            SELECT `Désignation article` as name, SUM(`Qté livrée`) as value
            FROM livraisons 
            GROUP BY `Désignation article`
            HAVING SUM(`Qté livrée`) >= (
                SELECT SUM(`Qté livrée`) * 0.05 
                FROM livraisons
            )
            ORDER BY value DESC
        """).fetchall()

        # Comparaison commandes/livraisons
        comparison_data = db.execute("""
            SELECT 
                YEAR(`Date expédition`) as year,
                SUM(`Qté cdée`) as ordered,
                SUM(`Qté livrée`) as delivered
            FROM livraisons 
            GROUP BY YEAR(`Date expédition`)
            ORDER BY year
        """).fetchall()

        return {
            "yearlyTrend": [dict(row) for row in yearly_trend],
            "monthlyComparison": [dict(row) for row in monthly_comparison],
            "articleDistribution": [dict(row) for row in article_distribution],
            "orderDeliveryComparison": [dict(row) for row in comparison_data]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
