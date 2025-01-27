@echo off

REM Gestion des erreurs sans quitter le script

echo Etape 1 : Creation et activation de l'environnement virtuel...
python -m venv venv
IF ERRORLEVEL 1 (
    echo Echec de la creation de l'environnement virtuel
)

call venv\Scripts\activate
IF ERRORLEVEL 1 (
    echo Echec de l'activation de l'environnement virtuel
)


echo Installation des dependances backend...
pip install --quiet Cython
IF ERRORLEVEL 1 (
    echo Echec de l'installation de Cython
)
pip install --quiet prophet
IF ERRORLEVEL 1 (
    echo Echec de l'installation de prophet
)
pip install --quiet pandas
IF ERRORLEVEL 1 (
    echo Echec de l'installation de pandas
)
pip install --quiet numpy
IF ERRORLEVEL 1 (
    echo Echec de l'installation de numpy
)
pip install --quiet matplotlib
IF ERRORLEVEL 1 (
    echo Echec de l'installation de matplotlib
)
pip install --quiet plotly
IF ERRORLEVEL 1 (
    echo Echec de l'installation de plotly
)
pip install --quiet fastapi
IF ERRORLEVEL 1 (
    echo Echec de l'installation de fastapi
)
pip install --quiet uvicorn
IF ERRORLEVEL 1 (
    echo Echec de l'installation de uvicorn
)
pip install --quiet python-dotenv
IF ERRORLEVEL 1 (
    echo Echec de l'installation de python-dotenv
)
pip install --quiet pystan
IF ERRORLEVEL 1 (
    echo Echec de l'installation de pystan
)

echo Installation des dépendances backend terminée.

echo Etape 3 : Installation des dependances frontend...
npm install
IF ERRORLEVEL 1 (
    echo Echec de l'installation des dependances frontend
)

echo Etape 4 : Lancement du backend...
start /B uvicorn src.api.prediction_service:app --reload --port 8000
IF ERRORLEVEL 1 (
    echo Echec du lancement du backend
)

echo Etape 5 : Lancement du frontend...
start /B npm run dev
IF ERRORLEVEL 1 (
    echo Echec du lancement du frontend
)

echo Etape 6 : Attente du demarrage des serveurs...
timeout /t 5
IF ERRORLEVEL 1 (
    echo Echec de l'attente
)

echo Etape 7 : Ouverture de l'application dans le navigateur...
start http://localhost:5173
IF ERRORLEVEL 1 (
    echo Echec de l'ouverture du navigateur
) 