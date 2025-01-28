#!/bin/bash

# Configuration initiale et installation des dépendances

echo "🔧 Étape 1 : Création de l'environnement virtuel..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "❌ Échec de la création de l'environnement virtuel"
fi

echo "🔧 Activation de l'environnement virtuel..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "❌ Échec de l'activation de l'environnement virtuel"
fi


echo "📦 Étape 2 : Installation des dépendances backend..."
echo "[1/14] | 🔧 Installation de Cython..."
pip install --quiet Cython
if [ $? -ne 0 ]; then
    echo "❌ Échec de l'installation de Cython"
fi
echo "[2/14] | 🔧 Installation de prophet..."
pip install --quiet prophet
if [ $? -ne 0 ]; then
    echo "❌ Échec de l'installation de prophet"
fi
echo "[3/14] | 🔧 Installation de pandas..."
pip install --quiet pandas
if [ $? -ne 0 ]; then
    echo "❌ Échec de l'installation de pandas"
fi
echo "[4/14] | 🔧 Installation de numpy..."
pip install --quiet numpy
if [ $? -ne 0 ]; then
    echo "❌ Échec de l'installation de numpy"
fi
echo "[5/14] | 🔧 Installation de matplotlib..."
pip install --quiet matplotlib
if [ $? -ne 0 ]; then
    echo "❌ Échec de l'installation de matplotlib"
fi
echo "[6/14] | 🔧 Installation de plotly..."
pip install --quiet plotly
if [ $? -ne 0 ]; then
    echo "❌ Échec de l'installation de plotly"
fi
echo "[7/14] | 🔧 Installation de fastapi..."
pip install --quiet fastapi
if [ $? -ne 0 ]; then
    echo "❌ Échec de l'installation de fastapi"
fi
echo "[8/14] | 🔧 Installation de uvicorn..."
pip install --quiet uvicorn
if [ $? -ne 0 ]; then
    echo "❌ Échec de l'installation de uvicorn"
fi
echo "[9/14] | 🔧 Installation de python-dotenv..."
pip install --quiet python-dotenv
if [ $? -ne 0 ]; then
    echo "❌ Échec de l'installation de python-dotenv"
fi
echo "[10/14] | 🔧 Installation de pystan..."
pip install --quiet pystan
if [ $? -ne 0 ]; then
    echo "❌ Échec de l'installation de pystan"
fi
echo "[11/14] | 🔧 Installation de scikit-learn..."
pip install --quiet scikit-learn
if [ $? -ne 0 ]; then
    echo "❌ Échec de l'installation de scikit-learn"
fi
echo "[12/14] | 🔧 Installation de sqlalchemy..."
pip install --quiet sqlalchemy==1.4.41
if [ $? -ne 0 ]; then
    echo "❌ Échec de l'installation de sqlalchemy"
fi
echo "[13/14] | 🔧 Installation de openpyxl..."
pip install --quiet openpyxl==3.1.2
if [ $? -ne 0 ]; then
    echo "❌ Échec de l'installation de openpyxl"
fi
echo "[14/14] | 🔧 Installation de reportlab..."
pip install --quiet reportlab==3.6.12
if [ $? -ne 0 ]; then
    echo "❌ Échec de l'installation de reportlab"
fi
apt install -y libfreetype6-dev libjpeg-dev zlib1g-dev build-essential
apt install -y xdg-utils
echo "✅ Installation des dépendances backend terminée."

echo "📦 Étape 3 : Installation des dépendances frontend..."
echo "[1/1] | 🔧 npm install..."
npm install
if [ $? -ne 0 ]; then
    echo "❌ Échec de l'installation des dépendances frontend"
fi

echo "✅ Configuration et installation des dépendances terminées avec succès." 