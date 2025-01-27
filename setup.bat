@echo off

REM Configuration initiale et installation des dépendances

echo Etape 1 : Création de l'environnement virtuel...
python -m venv venv
IF ERRORLEVEL 1 (
    echo ❌ Échec de la création de l'environnement virtuel
)

echo Activation de l'environnement virtuel...
call venv\Scripts\activate
IF ERRORLEVEL 1 (
    echo ❌ Échec de l'activation de l'environnement virtuel
)

echo Installation de Cython...
pip install --quiet Cython
IF ERRORLEVEL 1 (
    echo ❌ Échec de l'installation de Cython
)

echo Installation des dépendances backend...
pip install --quiet prophet
IF ERRORLEVEL 1 (
    echo ❌ Échec de l'installation de prophet
)
pip install --quiet pandas
IF ERRORLEVEL 1 (
    echo ❌ Échec de l'installation de pandas
)
pip install --quiet numpy
IF ERRORLEVEL 1 (
    echo ❌ Échec de l'installation de numpy
)
pip install --quiet matplotlib
IF ERRORLEVEL 1 (
    echo ❌ Échec de l'installation de matplotlib
)
pip install --quiet plotly
IF ERRORLEVEL 1 (
    echo ❌ Échec de l'installation de plotly
)
pip install --quiet fastapi
IF ERRORLEVEL 1 (
    echo ❌ Échec de l'installation de fastapi
)
pip install --quiet uvicorn
IF ERRORLEVEL 1 (
    echo ❌ Échec de l'installation de uvicorn
)
pip install --quiet python-dotenv
IF ERRORLEVEL 1 (
    echo ❌ Échec de l'installation de python-dotenv
)
pip install --quiet pystan
IF ERRORLEVEL 1 (
    echo ❌ Échec de l'installation de pystan
)

echo Installation des dépendances backend terminée.

echo Étape 2 : Installation des dépendances frontend...
npm install
IF ERRORLEVEL 1 (
    echo ❌ Échec de l'installation des dépendances frontend
)

echo ✅ Configuration et installation des dépendances terminées avec succès. 