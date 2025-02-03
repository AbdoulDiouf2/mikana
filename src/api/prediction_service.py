from fastapi import FastAPI, HTTPException, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Dict, Any
import pandas as pd
import numpy as np
from pathlib import Path
import uuid
from .hr_prediction import HRPredictor

app = FastAPI()

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)                                                                                                                                                                                                                                                                                               

# Initialisation du prédicteur RH
hr_predictor = HRPredictor()

class RHPredictionRequest(BaseModel):
    date: str
    currentStaff: int
    turnoverRate: float
    workload: float
    department: str

class RHPredictionResponse(BaseModel):
    id: str
    date: str
    weekly_predictions: List[Dict[str, Any]]
    confidence_intervals: List[Dict[str, Any]]
    status: str
    warning: Optional[str] = None
    department: str

@app.get("/")
async def root():
    return {"message": "API de prédiction RH active"}

@app.post("/api/predict-rh", response_model=RHPredictionResponse)
async def predict_rh(request: RHPredictionRequest):
    try:
        print(f"Demande de prédiction reçue pour la date: {request.date}")
        
        # Convertir la date en datetime
        target_date = datetime.strptime(request.date, "%Y-%m-%d")
        current_date = datetime.now()
        
        if target_date <= current_date:
            raise HTTPException(
                status_code=400,
                detail="La date de prédiction doit être dans le futur"
            )
        
        # Obtenir les prédictions hebdomadaires
        predictions = hr_predictor.predict_staff(
            current_staff=request.currentStaff,
            turnover_rate=request.turnoverRate,
            workload=request.workload,
            target_date=target_date,
            department=request.department
        )
        
        response = RHPredictionResponse(
            id=str(uuid.uuid4())[:8],
            date=request.date,
            weekly_predictions=predictions['weekly_predictions'],
            confidence_intervals=predictions['confidence_intervals'],
            status="completed",
            warning=predictions.get('warning'),
            department=request.department
        )
        print("Réponse générée avec succès")
        return response
        
    except Exception as e:
        print(f"ERREUR lors de la prédiction: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la prédiction RH: {str(e)}"
        )

# Constants
DEPARTMENTS = ["IT", "Sales", "HR", "Finance", "Marketing", "Operations"]
MAX_WEEKS_AHEAD = 52  # Maximum number of weeks to predict
MIN_STAFF = 5  # Minimum staff per department
MAX_STAFF = 100  # Maximum staff per department

# Initialisation du prédicteur
predicteur = PredicteurTemporel()

# Initialisation du prédicteur RH
hr_predictor = HRPredictor()

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

class RHPredictionRequest(BaseModel):
    date: str
    department: str
    currentStaff: int
    turnoverRate: float
    workload: float

class RHPredictionResponse(BaseModel):
    id: str
    date: str
    weekly_predictions: List[Dict[str, Any]]
    confidence_intervals: List[Dict[str, Any]]
    status: str
    warning: Optional[str] = None
    department: str

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

class DepartmentStats(BaseModel):
    id: str
    name: str
    currentStaff: int
    targetStaff: int
    turnoverRate: float
    avgPerformance: float

class HRPrediction(BaseModel):
    id: str
    date: str
    department: str
    predicted_staff: int
    predictedStaff: Optional[int] = None
    actualStaff: Optional[int] = None
    accuracy: Optional[float] = None
    confidence_min: Optional[int] = None
    confidence_max: Optional[int] = None
    recommendations: Optional[List[str]] = []
    status: str = "completed"
    warning: Optional[str] = None
    reliability_score: Optional[float] = 85.0  # Score de fiabilité par défaut

class HRPredictionRequest(BaseModel):
    date: str
    department: str
    currentStaff: int
    turnoverRate: float
    workload: float

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
        
        # Créer l'entrée dans l'historique
        history_entry = PredictionHistory(
            date=delivery_date.date(),  # Stocker seulement la date
            article=request.article,
            quantity_ordered=request.quantity,
            quantity_predicted=result["predicted_quantity"],
            delivery_rate=result["delivery_rate"],
            status=result["status"],
            recommendation=result["recommendation"],
            created_at=datetime.now()
        )
        
        db.add(history_entry)
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
async def get_articles():
    try:
        # Charger les colonnes du modèle
        columns_path = os.path.join(os.path.dirname(__file__), '..', '..', 'Planif_Livraisons', 'model_columns.joblib')
        print(f"Chargement des colonnes depuis: {columns_path}")
        
        if not os.path.exists(columns_path):
            raise FileNotFoundError(f"Le fichier des colonnes n'existe pas: {columns_path}")
            
        model_columns = joblib.load(columns_path)
        
        # Extraire les noms d'articles (enlever le préfixe 'article_')
        articles = [col[8:] for col in model_columns if col.startswith('article_')]
        articles.sort()  # Trier par ordre alphabétique
        
        print(f"Articles trouvés: {articles}")
        return {"articles": articles}
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des articles: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history")
async def get_prediction_history(
    db: Session = Depends(get_db),
    limit: int = 10,  # Par défaut 10 éléments
    offset: int = 0
):
    try:
        # Log pour debug
        print(f"Tentative de récupération de l'historique: limit={limit}, offset={offset}")

        # Requête avec gestion explicite des erreurs
        query = db.query(PredictionHistory)\
            .order_by(PredictionHistory.created_at.desc())
        
        # Compter le total avant pagination
        total = query.count()
        print(f"Nombre total d'enregistrements: {total}")

        # Appliquer la pagination
        records = query.offset(offset).limit(limit).all()
        print(f"Nombre d'enregistrements récupérés: {len(records)}")

        # Conversion en dictionnaire avec gestion des erreurs
        result = []
        for record in records:
            try:
                result.append({
                    "date": record.date.strftime("%Y-%m-%d") if record.date else None,
                    "article": str(record.article),
                    "quantity_ordered": float(record.quantity_ordered),
                    "quantity_predicted": float(record.quantity_predicted),
                    "delivery_rate": float(record.delivery_rate),
                    "status": str(record.status),
                    "recommendation": str(record.recommendation),
                    "created_at": record.created_at.strftime("%Y-%m-%d %H:%M:%S") if record.created_at else None
                })
            except Exception as e:
                print(f"Erreur lors de la conversion d'un enregistrement: {e}")
                continue

        return {
            "success": True,
            "data": result,
            "total": total,
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        print(f"Erreur dans get_prediction_history: {str(e)}")
        # Renvoyer une réponse plus détaillée pour le debug
        return {
            "success": False,
            "error": str(e),
            "detail": "Erreur lors de la récupération de l'historique"
        }

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
async def get_delivery_stats():
    try:
        # Charger le fichier Excel
        df = pd.read_excel('Planif_Livraisons/Planif livraisons.xlsx')
        df['Date expédition'] = pd.to_datetime(df['Date expédition'])
        df['Année'] = df['Date expédition'].dt.year
        df['Mois'] = df['Date expédition'].dt.month

        # Données pour la tendance annuelle
        yearly_trend = df.groupby('Année')['Qté livrée'].sum().reset_index()
        yearly_trend = yearly_trend.rename(columns={
            'Année': 'year',
            'Qté livrée': 'delivered'
        }).to_dict('records')

        # Données pour la comparaison mensuelle
        monthly_comparison = df[df['Année'].isin([2022, 2023, 2024])]
        monthly_data = []
        month_names = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 
                      'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']
        
        for month in range(1, 13):
            month_data = {'month': month_names[month-1]}
            for year in [2022, 2023, 2024]:
                quantity = monthly_comparison[
                    (monthly_comparison['Année'] == year) & 
                    (monthly_comparison['Mois'] == month)
                ]['Qté livrée'].sum()
                month_data[f'year{year}'] = float(quantity)
            monthly_data.append(month_data)

        # Données pour la distribution des articles
        article_distribution = df.groupby('Désignation article')['Qté livrée'].sum()
        threshold = article_distribution.sum() * 0.05  # seuil de 5%
        major_articles = article_distribution[article_distribution >= threshold]
        others = pd.Series({
            'Autres': article_distribution[article_distribution < threshold].sum()
        })
        article_distribution = pd.concat([major_articles, others])
        article_data = [
            {'name': name, 'value': float(value)} 
            for name, value in article_distribution.items()
        ]

        # Données pour la comparaison commandes/livraisons
        comparison_data = df.groupby('Année').agg({
            'Qté cdée': 'sum',
            'Qté livrée': 'sum'
        }).reset_index()
        comparison_data = comparison_data.rename(columns={
            'Année': 'year',
            'Qté cdée': 'ordered',
            'Qté livrée': 'delivered'
        }).to_dict('records')

        return {
            "yearlyTrend": yearly_trend,
            "monthlyComparison": monthly_data,
            "articleDistribution": article_data,
            "orderDeliveryComparison": comparison_data
        }

    except Exception as e:
        print(f"❌ Erreur lors de la récupération des statistiques: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des statistiques: {str(e)}"
        )

@app.get("/api/hr/alerts", response_model=List[Alert])
async def get_alerts():
    # Simulation de données d'alerte
    alerts = [
        Alert(
            id="1",
            type="warning",
            department="IT",
            message="Taux de rotation élevé ce mois-ci",
            value=15,
            threshold=10,
            date=datetime.now().isoformat()
        ),
        Alert(
            id="2",
            type="danger",
            department="Sales",
            message="Sous-effectif critique",
            value=5,
            threshold=8,
            date=datetime.now().isoformat()
        ),
        Alert(
            id="3",
            type="info",
            department="HR",
            message="Nouveau processus de recrutement mis en place",
            date=datetime.now().isoformat()
        )
    ]
    return alerts

@app.get("/api/hr/department-stats", response_model=List[DepartmentStats])
async def get_department_stats():
    # Simulation de statistiques par département
    stats = []
    for i, dept in enumerate(DEPARTMENTS):
        stats.append(
            DepartmentStats(
                id=str(i+1),
                name=dept,
                currentStaff=random.randint(10, 50),
                targetStaff=random.randint(15, 55),
                turnoverRate=round(random.uniform(0.05, 0.20), 2),
                avgPerformance=round(random.uniform(0.70, 0.95), 2)
            )
        )
    return stats

@app.get("/api/hr/predictions")
async def get_hr_predictions(page: int = 0, limit: int = 10):
    # Simulation d'historique de prédictions
    predictions = []
    total = 20  # Nombre total de prédictions

    start_date = datetime.now()
    for i in range(total):
        date = start_date - pd.Timedelta(days=i)
        dept = random.choice(DEPARTMENTS)
        predicted = random.randint(10, 50)
        actual = predicted + random.randint(-5, 5) if random.random() > 0.2 else None
        
        predictions.append(
            HRPrediction(
                id=str(i+1),
                date=date.isoformat(),
                department=dept,
                predicted_staff=predicted,
                actual_staff=actual,
                accuracy=round(random.uniform(0.85, 0.98), 2) if actual else None,
                status="success" if actual else "pending"
            )
        )

    # Pagination
    start = page * limit
    end = start + limit
    return {
        "data": predictions[start:end],
        "total": total
    }

@app.post("/api/hr/predict", response_model=HRPrediction)
async def predict_staffing(request: HRPredictionRequest):
    # Simulation de prédiction
    predicted_staff = int(
        request.currentStaff * 
        (1 - request.turnoverRate) * 
        (1 + 0.1 * request.workload)
    )
    
    # Calculer un score de fiabilité basé sur les facteurs
    reliability_score = 100 - (
        abs(request.turnoverRate * 100) * 0.3 +  # Impact du taux de rotation
        abs(request.workload - 1) * 20  # Impact de la charge de travail
    )
    reliability_score = max(0, min(100, reliability_score))  # Limiter entre 0 et 100
    
    # Calculate confidence intervals (±10% of predicted staff)
    confidence_min = int(predicted_staff * 0.9)
    confidence_max = int(predicted_staff * 1.1)
    
    return HRPrediction(
        id=str(uuid.uuid4()),  # Using UUID for better uniqueness
        date=request.date,
        department=request.department,
        predicted_staff=predicted_staff,
        predictedStaff=predicted_staff,  # Set both fields for compatibility
        actualStaff=request.currentStaff,
        accuracy=None,  # Will be calculated later when actual data is available
        confidence_min=confidence_min,
        confidence_max=confidence_max,
        status="completed",
        warning=None if reliability_score > 70 else "Prédiction de fiabilité moyenne",
        reliability_score=reliability_score,
        recommendations=[
            "Surveiller le taux de rotation du personnel",
            "Évaluer les besoins en formation",
            "Planifier le recrutement à l'avance"
        ]
    )

@app.post("/api/predict-rh", response_model=RHPredictionResponse)
async def predict_rh(request: RHPredictionRequest):
    try:
        print(f"Demande de prédiction reçue pour la date: {request.date}")
        
        # Convertir la date en datetime
        target_date = datetime.strptime(request.date, "%Y-%m-%d")
        current_date = datetime.now()
        
        if target_date <= current_date:
            raise HTTPException(
                status_code=400,
                detail="La date de prédiction doit être dans le futur"
            )
        
        # Obtenir les prédictions hebdomadaires
        predictions = hr_predictor.predict_staff(
            current_staff=request.currentStaff,
            turnover_rate=request.turnoverRate,
            workload=request.workload,
            target_date=target_date,
            department=request.department
        )
        
        response = RHPredictionResponse(
            id=str(uuid.uuid4())[:8],
            date=request.date,
            weekly_predictions=predictions['weekly_predictions'],
            confidence_intervals=predictions['confidence_intervals'],
            status="completed",
            warning=predictions.get('warning'),
            department=request.department
        )
        print("Réponse générée avec succès")
        return response
        
    except Exception as e:
        print(f"ERREUR lors de la prédiction: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la prédiction RH: {str(e)}"
        )

@app.get("/api/hr/departments")
async def get_departments():
    try:
        departments = ["Production", "Logistique", "Maintenance", "Qualité", "Ressources Humaines", "Informatique"]
        return {"departments": departments}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des départements: {str(e)}"
        )

@app.get("/api/hr/stats/{department}")
async def get_department_stats(department: str):
    try:
        # Simulation de statistiques pour le département
        return {
            "currentStaff": random.randint(10, 50),
            "targetStaff": random.randint(15, 55),
            "turnoverRate": round(random.uniform(0.05, 0.20), 2),
            "avgPerformance": round(random.uniform(0.70, 0.95), 2)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des statistiques: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
