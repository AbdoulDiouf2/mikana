from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel, Field
from pathlib import Path
from typing import Dict, List, Optional, Any
import json
import os
import shutil
import logging
import subprocess
from datetime import datetime
import aiofiles
from sqlalchemy.orm import Session
from sqlalchemy import func
from .database import SessionLocal, MetricsHistory, get_db

# Configuration des logs
logging.basicConfig(level=logging.DEBUG)
ALLOWED_EXTENSIONS = {".csv", ".xlsx"}

# Configuration MySQL
MYSQL_CONFIG = {
    'user': 'mikana_user',
    'password': 'mikana_password',
    'host': 'localhost',
    'database': 'mikana_db'
}

# ------------------- Middleware de logging -------------------
class LogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logging.debug(f"\n=== Requête reçue: {request.method} {request.url} ===")
        
        if request.method == "POST":
            body = await request.body()
            logging.debug(f"Body preview: {body[:500]}...")
        
        response = await call_next(request)
        return response

# ------------------- Configuration FastAPI -------------------
app = FastAPI()

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de logging
app.add_middleware(LogMiddleware)

# ------------------- Modèles Pydantic -------------------
class ModelInfo(BaseModel):
    establishments_count: Optional[int] = None
    articles_count: Optional[int] = None
    total_data_points: Optional[int] = None
    training_date: Optional[str] = None

class BaseMetrics(BaseModel):
    mse: float = Field(alias='test_mse', default=0.0)
    rmse: float = Field(alias='test_rmse', default=0.0)
    mae: float = Field(alias='test_mae', default=0.0)
    r2: float = Field(alias='test_r2', default=0.0)

class ModelMetrics(BaseModel):
    model_name: str
    r2_score: float
    rmse: Optional[float] = None
    mae: Optional[float] = None
    timestamp: str

class PerformanceResponse(BaseModel):
    overall_performance: float
    models_metrics: List[ModelMetrics]
    last_update: str

# ------------------- Chemins des modèles -------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ------------------- Fonctions utilitaires -------------------
def get_db_connection():
    """Crée et retourne une connexion à la base de données"""
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        return connection
    except Error as e:
        logging.error(f"Erreur de connexion à MySQL : {e}")
        raise

def save_metrics_to_db(model_name: str, metrics: dict, additional_info: str = None):
    """Sauvegarde les métriques d'entraînement dans la base de données"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        query = """
            INSERT INTO metrics_history 
            (model_name, r2_score, mae, rmse, training_date, additional_info)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (
            model_name,
            metrics.get('test_r2', metrics.get('r2', None)),
            metrics.get('test_mae', metrics.get('mae', None)),
            metrics.get('test_rmse', metrics.get('rmse', None)),
            datetime.utcnow(),
            additional_info
        )
        
        cursor.execute(query, values)
        connection.commit()
        
        logging.info(f"Métriques sauvegardées pour le modèle {model_name}")
        
    except Error as e:
        logging.error(f"Erreur lors de la sauvegarde des métriques : {str(e)}")
        raise
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# ------------------- Endpoints -------------------
@app.get("/api/performance/overview", response_model=PerformanceResponse)
async def get_performance_overview(db: Session = Depends(get_db)):
    """Endpoint principal pour les performances"""
    try:
        query = """
            WITH RankedMetrics AS (
                SELECT 
                    model_name,
                    r2_score,
                    mae,
                    rmse,
                    training_date,
                    ROW_NUMBER() OVER (PARTITION BY model_name ORDER BY training_date DESC) as rn
                FROM metrics_history
            )
            SELECT 
                model_name,
                r2_score,
                mae,
                rmse,
                training_date
            FROM RankedMetrics
            WHERE rn = 1
        """
        
        results = db.execute(query).fetchall()
        
        metrics = []
        for row in results:
            metrics.append(ModelMetrics(
                model_name=row.model_name,
                r2_score=float(row.r2_score) if row.r2_score is not None else 0.0,
                rmse=row.rmse,
                mae=row.mae,
                timestamp=row.training_date.isoformat() if row.training_date else None
            ))

        if not metrics:
            return JSONResponse(
                status_code=404,
                content={"detail": "Aucune métrique trouvée"}
            )

        r2_scores = [m.r2_score for m in metrics if m.r2_score is not None]
        overall = sum(r2_scores)/len(r2_scores) if r2_scores else 0.0

        return PerformanceResponse(
            overall_performance=overall,
            models_metrics=metrics,
            last_update=datetime.now().isoformat()
        )

    except Exception as e:
        logging.error(f"Erreur lors de la récupération des métriques : {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur serveur: {str(e)}"
        )

@app.get("/api/performance/metrics-history")
async def get_metrics_history(db: Session = Depends(get_db)):
    """Récupère l'historique des métriques"""
    try:
        query = """
            SELECT 
                id,
                model_name,
                r2_score,
                mae,
                rmse,
                training_date,
                additional_info
            FROM metrics_history 
            ORDER BY training_date DESC 
            LIMIT 100
        """
        
        results = db.execute(query).fetchall()
        
        if not results:
            return {
                "success": True,
                "data": []
            }

        # Convert result rows to dictionaries
        formatted_results = []
        for row in results:
            formatted_results.append({
                "id": row.id,
                "model_name": row.model_name,
                "r2_score": float(row.r2_score) if row.r2_score is not None else None,
                "mae": float(row.mae) if row.mae is not None else None,
                "rmse": float(row.rmse) if row.rmse is not None else None,
                "training_date": row.training_date.isoformat() if row.training_date else None,
                "additional_info": row.additional_info
            })
        
        return {
            "success": True,
            "data": formatted_results
        }
        
    except Exception as e:
        logging.error(f"Erreur lors de la récupération de l'historique : {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération de l'historique : {str(e)}"
        )

@app.post("/api/performance/upload")
async def upload_files(
    module: str = Form(...),
    is_folder: str = Form(...),
    files: List[UploadFile] = File(...),
    paths: List[str] = Form(...)
):
    logging.info(f"Début de l'upload - Module: {module}")
    logging.info(f"Nombre de fichiers: {len(files)}")
    logging.info(f"Chemins: {paths}")

    try:
        base_dir = BASE_DIR
        module_dirs = {
            "commandes": base_dir / "Predict_commande",
            "livraisons": base_dir / "Planif_Livraisons",
            "rh": base_dir / "Gestion_RH"
        }
        
        if module not in module_dirs:
            raise HTTPException(
                status_code=400,
                detail=f"Module invalide: {module}"
            )
            
        target_dir = module_dirs[module]
        logging.info(f"Dossier cible: {target_dir}")
        
        target_dir.mkdir(parents=True, exist_ok=True)
        
        saved_files = []
        for file, path in zip(files, paths):
            file_path = target_dir / path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            logging.info(f"Sauvegarde du fichier: {file_path}")
            
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            saved_files.append(str(file_path.relative_to(base_dir)))
            logging.info(f"Fichier sauvegardé: {file_path}")

        return JSONResponse({
            "status": "success",
            "message": f"{len(saved_files)} fichier(s) sauvegardé(s)",
            "saved_files": saved_files
        })

    except Exception as e:
        logging.error(f"Erreur lors de l'upload: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.post("/api/performance/train-commandes")
async def train_commandes_model(db: Session = Depends(get_db)):
    """Endpoint pour entraîner le modèle de prédiction des commandes"""
    try:
        base_dir = BASE_DIR / "Predict_commande"
        subprocess.run(["python", "train.py"], cwd=base_dir, check=True)
        
        metrics_path = base_dir / "trained_models" / "model_metrics.json"
        with open(metrics_path, 'r') as f:
            metrics = json.load(f)
        
        save_metrics_to_db(
            "Prédiction Commandes",
            metrics.get('metrics', {}),
            f"Entraînement effectué le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        return {"message": "Entraînement du modèle de prédiction des commandes terminé avec succès"}
    except Exception as e:
        logging.error(f"Erreur lors de l'entraînement du modèle de commandes : {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'entraînement : {str(e)}"
        )

@app.post("/api/performance/train-livraisons")
async def train_livraisons_model(db: Session = Depends(get_db)):
    """Endpoint pour entraîner le modèle de planification des livraisons"""
    try:
        base_dir = BASE_DIR / "Planif_Livraisons"
        subprocess.run(["python", "train.py"], cwd=base_dir, check=True)
        
        metrics_path = base_dir / "model_metrics.json"
        with open(metrics_path, 'r') as f:
            metrics = json.load(f)
        
        save_metrics_to_db(
            "Planification Livraisons",
            metrics.get('metrics', {}),
            f"Entraînement effectué le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        return {"message": "Entraînement du modèle de planification des livraisons terminé avec succès"}
    except Exception as e:
        logging.error(f"Erreur lors de l'entraînement du modèle de livraisons : {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'entraînement : {str(e)}"
        )

@app.post("/api/performance/train-rh")
async def train_rh_model(db: Session = Depends(get_db)):
    """Endpoint pour entraîner le modèle de gestion RH"""
    try:
        base_dir = BASE_DIR / "Gestion_RH"
        subprocess.run(["python", "train.py"], cwd=base_dir, check=True)
        
        metrics_path = base_dir / "model_metrics.json"
        with open(metrics_path, 'r') as f:
            metrics = json.load(f)
        
        save_metrics_to_db(
            "Gestion RH",
            metrics.get('metrics', {}),
            f"Entraînement effectué le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        return {"message": "Entraînement du modèle de gestion RH terminé avec succès"}
    except Exception as e:
        logging.error(f"Erreur lors de l'entraînement du modèle RH : {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'entraînement : {str(e)}"
        )
