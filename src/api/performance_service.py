from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel, Field
from pathlib import Path
from typing import Dict, List, Optional
import json
import os
import shutil
import logging
import subprocess
from datetime import datetime
import aiofiles
from pathlib import Path
from fastapi import HTTPException

# Configuration des logs
logging.basicConfig(level=logging.DEBUG)
ALLOWED_EXTENSIONS = {".csv", ".xlsx"}

# ------------------- Middleware de logging -------------------
class LogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logging.debug(f"\n=== Requête reçue: {request.method} {request.url} ===")
        
        if request.method == "POST":
            body = await request.body()
            logging.debug(f"Body preview: {body[:500]}...")
        
        response = await call_next(request)
        return response

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
    timestamp: str
    metrics: BaseMetrics
    model_info: Optional[ModelInfo] = None
    data_points: Optional[int] = None

class PerformanceResponse(BaseModel):
    overall_performance: float
    models_metrics: List[ModelMetrics]
    last_update: str

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

# ------------------- Chemins des modèles -------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_PATHS = {
    "Prédiction Commandes": BASE_DIR / "Predict_commande" / "trained_models" / "model_metrics.json",
    "Planification Livraisons": BASE_DIR / "Planif_Livraisons" / "model_metrics.json",
    "Gestion RH": BASE_DIR / "Gestion_RH" / "model_metrics.json"
}

# ------------------- Logique métier -------------------
def normalize_metrics(data: Dict, model_name: str) -> Optional[ModelMetrics]:
    """Normalise les formats de données variants des modèles"""
    try:
        if "metrics" in data:
            return ModelMetrics(
                model_name=model_name,
                timestamp=data.get("timestamp", datetime.now().isoformat()),
                metrics=BaseMetrics(
                    test_mse=data["metrics"].get("test_mse", 0.0),
                    test_rmse=data["metrics"].get("test_rmse", data["metrics"].get("rmse", 0.0)),
                    test_mae=data["metrics"].get("test_mae", data["metrics"].get("mae", 0.0)),
                    test_r2=data["metrics"].get("test_r2", 0.0)
                )
            )
        elif "model_metrics" in data:
            return ModelMetrics(
                model_name=model_name,
                timestamp=data.get("last_updated", datetime.now().isoformat()),
                metrics=BaseMetrics(**data["model_metrics"]),
                data_points=data.get("data_points")
            )
        else:
            logging.error(f"Format non reconnu pour {model_name}")
            return None
    except Exception as e:
        logging.error(f"Erreur de normalisation pour {model_name}: {str(e)}")
        return None

def load_model_metrics(path: Path, model_name: str) -> Optional[ModelMetrics]:
    """Charge et valide les métriques d'un fichier JSON"""
    try:
        if not path.exists():
            logging.warning(f"Fichier manquant: {path}")
            return None
            
        with open(path, "r") as f:
            data = json.load(f)
            
        return normalize_metrics(data, model_name)
        
    except json.JSONDecodeError:
        logging.error(f"Fichier JSON invalide: {path}")
        return None
    except Exception as e:
        logging.error(f"Erreur générale: {str(e)}")
        return None
    
def get_last_logistic_file(base_dir: Path) -> Optional[str]:
    """Récupère le dernier fichier logistique présent"""
    try:
        # Chemin vers le dossier logistique_new
        logistic_dir = base_dir / "Predict_commande" / "Logistique-old"
        logging.info(f"Chemin du dossier logistique : {logistic_dir}")

        if not logistic_dir.exists():
            logging.error(f"Dossier logistique introuvable : {logistic_dir}")
            return None
        
        # Obtenir l'année en cours et l'année précédente
        current_year = datetime.now().year
        years_to_check = [current_year, current_year - 1]
        
        # Parcourir les années pour trouver le dernier fichier
        for year in years_to_check:
            year_dir = logistic_dir / str(year)
            logging.info(f"Vérification du dossier de l'année : {year_dir}")
            if year_dir.exists() and year_dir.is_dir():
                # Lister les fichiers et trier par date de modification
                files = sorted(
                    year_dir.glob("*.xlsx"),  # ou "*.xlsx" si nécessaire
                    key=lambda f: f.stat().st_mtime,
                    reverse=True
                )
                if files:
                    logging.info(f"Dernier fichier trouvé : {files[0].name}")
                    return files[0].name  # Retourne le nom du dernier fichier
        logging.warning("Aucun fichier logistique trouvé")
        return None  # Aucun fichier trouvé
    except Exception as e:
        logging.error(f"Erreur lors de la recherche du dernier fichier : {str(e)}")
        return None
    
# ------------------- Endpoints -------------------
@app.get("/api/performance/overview", response_model=PerformanceResponse)
async def get_performance_overview():
    """Endpoint principal pour les performances"""
    try:
        metrics = []
        for model_name, path in MODEL_PATHS.items():
            model_data = load_model_metrics(path, model_name)
            if model_data:
                metrics.append(model_data)

        if not metrics:
            return JSONResponse(
                status_code=404,
                content={"detail": "Aucune métrique trouvée"}
            )

        r2_scores = [m.metrics.r2 for m in metrics if m.metrics.r2 is not None]
        overall = sum(r2_scores)/len(r2_scores) if r2_scores else 0.0

        return PerformanceResponse(
            overall_performance=overall,
            models_metrics=metrics,
            last_update=datetime.now().isoformat()
        )

    except Exception as e:
        logging.error(f"Erreur critique: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Erreur serveur: {str(e)}"}
        )

# Dans performance_service.py

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
        # Définir le répertoire de base pour les uploads
        base_dir = Path(__file__).resolve().parent.parent.parent
        
        # Mapper le module au bon dossier
        module_dirs = {
            "commandes": base_dir / "Predict_commande",       # ✅
            "livraisons": base_dir / "Planif_Livraisons",     # ✅
            "rh": base_dir / "Gestion_RH"                     # ✅
        }
        
        if module not in module_dirs:
            raise HTTPException(
                status_code=400,
                detail=f"Module invalide: {module}"
            )
            
        target_dir = module_dirs[module]
        logging.info(f"Dossier cible: {target_dir}")
        
        # Créer le dossier s'il n'existe pas
        target_dir.mkdir(parents=True, exist_ok=True)
        
        saved_files = []
        for file, path in zip(files, paths):
            # Nettoyer le chemin du fichier
            file_path = target_dir / path
            # Créer les répertoires parents si nécessaire
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            logging.info(f"Sauvegarde du fichier: {file_path}")
            
            # Sauvegarder le fichier
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

@app.get("/api/performance/last-logistic-file")
async def get_last_logistic_file_endpoint():
    """Endpoint pour récupérer le dernier fichier logistique"""
    try:
        base_dir = Path(__file__).resolve().parent.parent.parent
        last_file = get_last_logistic_file(base_dir)
        
        if not last_file:
            raise HTTPException(
                status_code=404,
                detail="Aucun fichier logistique trouvé"
            )
        
        return {"last_file": last_file}
    except Exception as e:
        logging.error(f"Erreur critique : {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur serveur : {str(e)}"
        )
    
