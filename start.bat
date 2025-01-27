@echo off

REM Lancement des serveurs backend et frontend

echo Etape 1 : Lancement du backend...
start /B uvicorn src.api.prediction_service:app --reload --port 8000
IF ERRORLEVEL 1 (
    echo --> Echec du lancement du backend
)

echo Etape 2 : Lancement du frontend...
start /B npm run dev
IF ERRORLEVEL 1 (
    echo --> Echec du lancement du frontend
)

echo Etape 3 : Attente du démarrage des serveurs...
timeout /t 5
IF ERRORLEVEL 1 (
    echo --> Echec de l'attente
)

echo Etape 4 : Ouverture de l'application dans le navigateur...
start http://localhost:5173
IF ERRORLEVEL 1 (
    echo --> Echec de l'ouverture du navigateur
) 

echo ✅ Application lancee avec succès. 