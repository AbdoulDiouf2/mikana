#!/bin/bash

# Étape 1 : Créer et activer l'environnement virtuel
echo "🔧 Étape 1 : Création et activation de l'environnement virtuel..."
python3 -m venv venv || { echo "❌ Échec de la création de l'environnement virtuel"; }
source venv/bin/activate || { echo "❌ Échec de l'activation de l'environnement virtuel"; }

# Étape 2 : Installer Cython
echo "🔧 Installation de Cython..."
pip install --quiet Cython || { echo "❌ Échec de l'installation de Cython"; }

# Étape 3 : Installer les dépendances backend
echo "📦 Étape 3 : Installation des dépendances backend..."
pip install --quiet prophet || { echo "❌ Échec de l'installation de prophet"; }
pip install --quiet pandas || { echo "❌ Échec de l'installation de pandas"; }
pip install --quiet numpy || { echo "❌ Échec de l'installation de numpy"; }
pip install --quiet matplotlib || { echo "❌ Échec de l'installation de matplotlib"; }
pip install --quiet plotly || { echo "❌ Échec de l'installation de plotly"; }
pip install --quiet fastapi || { echo "❌ Échec de l'installation de fastapi"; }
pip install --quiet uvicorn || { echo "❌ Échec de l'installation de uvicorn"; }
pip install --quiet python-dotenv || { echo "❌ Échec de l'installation de python-dotenv"; }
pip install --quiet pystan || { echo "❌ Échec de l'installation de pystan"; }

echo "✅ Installation des dépendances backend terminée."

# Étape 4 : Installer les dépendances frontend
echo "📦 Étape 4 : Installation des dépendances frontend..."
npm install || { echo "❌ Échec de l'installation des dépendances frontend"; }

# Étape 5 : Lancer le backend
echo "🚀 Étape 5 : Lancement du backend..."
uvicorn src.api.prediction_service:app --reload --port 8000 & || { echo "❌ Échec du lancement du backend"; }

# Étape 6 : Lancer le frontend
echo "🚀 Étape 6 : Lancement du frontend..."
npm run dev & || { echo "❌ Échec du lancement du frontend"; }

# Étape 7 : Attendre que les serveurs démarrent
echo "⏳ Étape 7 : Attente du démarrage des serveurs..."
sleep 5 || { echo "❌ Échec de l'attente"; }

# Étape 8 : Ouvrir l'application dans le navigateur
echo "🌐 Étape 8 : Ouverture de l'application dans le navigateur..."
xdg-open http://localhost:5173 || { echo "❌ Échec de l'ouverture du navigateur"; }

echo "✅ Installation des dépendances terminée avec succès." 