#!/bin/bash

# Lancement des serveurs backend et frontend

echo "🔧 Activation de l'environnement virtuel..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "❌ Échec de l'activation de l'environnement virtuel"
fi

echo "🚀 Étape 1 : Lancement du backend..."
uvicorn src.api.prediction_service:app --reload --port 8000 &
if [ $? -ne 0 ]; then
    echo "❌ Échec du lancement du backend"
fi

echo "🚀 Étape 2 : Lancement du frontend..."
# 
npm run dev &
if [ $? -ne 0 ]; then
    echo "❌ Échec du lancement du frontend"
fi

echo "⏳ Étape 3 : Attente du démarrage des serveurs..."
sleep 5
if [ $? -ne 0 ]; then
    echo "❌ Échec de l'attente"
fi

echo "🌐 Étape 4 : Ouverture de l'application dans le navigateur..."
xdg-open http://localhost:5173
if [ $? -ne 0 ]; then
    echo "❌ Échec de l'ouverture du navigateur"
fi

echo "✅ Application lancée avec succès." 