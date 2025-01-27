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

echo "🔧 Installation de Cython..."
pip install --quiet Cython
if [ $? -ne 0 ]; then
    echo "❌ Échec de l'installation de Cython"
fi

echo "📦 Étape 2 : Installation des dépendances backend..."
pip install --quiet prophet
if [ $? -ne 0 ]; then
    echo "❌ Échec de l'installation de prophet"
fi

pip install --quiet pandas
if [ $? -ne 0 ]; then
    echo "❌ Échec de l'installation de pandas"
fi

pip install --quiet numpy
if [ $? -ne 0 ]; then
    echo "❌ Échec de l'installation de numpy"
fi

pip install --quiet matplotlib
if [ $? -ne 0 ]; then
    echo "❌ Échec de l'installation de matplotlib"
fi

pip install --quiet plotly
if [ $? -ne 0 ]; then
    echo "❌ Échec de l'installation de plotly"
fi

pip install --quiet fastapi
if [ $? -ne 0 ]; then
    echo "❌ Échec de l'installation de fastapi"
fi

pip install --quiet uvicorn
if [ $? -ne 0 ]; then
    echo "❌ Échec de l'installation de uvicorn"
fi

pip install --quiet python-dotenv
if [ $? -ne 0 ]; then
    echo "❌ Échec de l'installation de python-dotenv"
fi

pip install --quiet pystan
if [ $? -ne 0 ]; then
    echo "❌ Échec de l'installation de pystan"
fi

echo "✅ Installation des dépendances backend terminée."

echo "📦 Étape 3 : Installation des dépendances frontend..."
npm install
if [ $? -ne 0 ]; then
    echo "❌ Échec de l'installation des dépendances frontend"
fi

echo "✅ Configuration et installation des dépendances terminées avec succès." 