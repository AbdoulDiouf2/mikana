# MIKANA - Plateforme de Prédiction Logistique Intelligente

[![Docker](https://img.shields.io/badge/Docker-Containers-blue?logo=docker)](https://www.docker.com)

Une solution complète de prédiction des besoins logistiques intégrant l'IA et des tableaux de bord interactifs.

---

## Sommaire
1. [Fonctionnalités Clés](#-fonctionnalités-clés)
2. [Stack Technique](#-stack-technique)
3. [Démarrage Rapide avec Docker](#-démarrage-rapide-avec-docker)
4. [Architecture des Services](#-architecture-des-services)
5. [Installation Manuelle](#-installation-manuelle)
6. [Fonctionnalités Avancées](#-fonctionnalités-avancées)
7. [Documentation Technique](#-documentation-technique)
8. [Contribution](#-contribution)

---

## 🌟 Fonctionnalités Clés

- 🔮 Prédictions temps réel avec Facebook Prophet
- 📈 Tableaux de bord interactifs (Recharts)
- 📦 Gestion multi-entrepôts
- 📊 Analyse des tendances saisonnières
- 📥 Export PDF/Excel automatisé

## 🛠 Stack Technique

**Frontend**  
⚛️ React 18 + TypeScript  
🎨 MUI X Data Grid & Date Pickers  
📊 Recharts & Chart.js  
📄 React PDF Renderer

**Backend**  
🐍 Python FastAPI  
📈 Facebook Prophet  
🗄️ SQLite + Pandas  
📦 Docker Compose

## 🐳 Démarrage Rapide avec Docker

```bash
git clone https://github.com/AbdoulDiouf2/mikana
cd mikana
docker-compose up --build
```

Accédez à l'application : [http://localhost:5173](http://localhost:5173)

### Architecture des Services

- **frontend** : Vite + React (Port 5173)
- **backend** : FastAPI + Prophet (Port 8000)
- **db** : SQLite (Volume persistant)

## 🔧 Installation Manuelle

### Prérequis

- Node.js 18+ & npm
- Python 3.9+
- Git LFS

```bash
git clone https://github.com/AbdoulDiouf2/mikana
cd mikana
# Frontend
npm install
npm run dev
# Backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn src.api.prediction_service:app --reload
```

## 📊 Fonctionnalités Avancées

1. **Prédiction Temps Réel**
   - Sélection de plages personnalisées
   - Comparaison historique

2. **Visualisations**
   - Tendances saisonnières hebdomadaires/mensuelles
   - Heatmaps de demande

3. **Gestion des Données**
   - Import/Export CSV
   - Historique versionné

## 📚 Documentation Technique

```
src/
├── api/           # Endpoints FastAPI
├── model/         # Modèles Prophet
├── pages/         # Routes React
│   └── Delivery/  # Module de prédiction
└── components/    # UI réutilisable
```

## 🤝 Contribution

1. Forkez le dépôt
2. Créez une feature branch :
   ```bash
   git checkout -b feat/nouvelle-fonctionnalite
   ```
3. Soumettez une Pull Request

**Équipe :**  
BOUGA Paule Audrey | BOHI Franck Junior | DIOUF Abdoul Ahad  
GANKPEZOUNDE Ange | NOUBOM Michelle D'Or | SOW Aminata
