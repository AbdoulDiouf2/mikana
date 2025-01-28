@echo off

REM Configuration initiale et installation des dependances

echo Etape 1 : Creation de l'environnement virtuel...
python -m venv venv
IF ERRORLEVEL 1 (
    echo --> echec de la creation de l'environnement virtuel
)

echo Activation de l'environnement virtuel...
call venv\Scripts\activate
IF ERRORLEVEL 1 (
    echo --> echec de l'activation de l'environnement virtuel
)

echo Installation des dependances backend...
echo Installation de Cython...
pip install --quiet Cython
IF ERRORLEVEL 1 (
    echo --> echec de l'installation de Cython
)
echo Installation de scikit-learn...
pip install --quiet scikit-learn
IF ERRORLEVEL 1 (
    echo --> echec de l'installation de scikit-learn
)
echo Installation de Prophet...
pip install --quiet prophet
IF ERRORLEVEL 1 (
    echo --> echec de l'installation de prophet
)
echo Installation de pandas...  
pip install --quiet pandas
IF ERRORLEVEL 1 (
    echo --> echec de l'installation de pandas
)
echo Installation de numpy...
pip install --quiet numpy
IF ERRORLEVEL 1 (
    echo --> echec de l'installation de numpy
)
echo Installation de matplotlib...
pip install --quiet matplotlib
IF ERRORLEVEL 1 (
    echo --> echec de l'installation de matplotlib
)
echo Installation de plotly...
pip install --quiet plotly
IF ERRORLEVEL 1 (
    echo --> echec de l'installation de plotly
)
echo Installation de fastapi...
pip install --quiet fastapi
IF ERRORLEVEL 1 (
    echo --> echec de l'installation de fastapi
)
echo Installation de uvicorn...
pip install --quiet uvicorn
IF ERRORLEVEL 1 (
    echo --> echec de l'installation de uvicorn
)
echo Installation de python-dotenv...
pip install --quiet python-dotenv
IF ERRORLEVEL 1 (
    echo --> echec de l'installation de python-dotenv
)
echo Installation de pystan...
pip install --quiet pystan
IF ERRORLEVEL 1 (
    echo --> echec de l'installation de pystan
)

echo Installation des dependances backend terminee.

echo Etape 2 : Installation des dependances frontend...
npm install
IF ERRORLEVEL 1 (
    echo --> echec de l'installation des dependances frontend
)

echo ✅ Configuration et installation des dependances terminees avec succès.