# MIKANA - Application de Prédiction de Commandes

Cette application permet de prédire les futures commandes de linge en utilisant le modèle Prophet de Facebook. Elle offre une interface utilisateur intuitive pour analyser et visualiser les prévisions de commandes.

## 🚀 Fonctionnalités

- Prédiction des commandes futures basée sur les données historiques
- Visualisation des statistiques de prédiction avec des graphiques interactifs
- Comparaison avec les données historiques des années précédentes
- Analyse des tendances saisonnières
- Analyse de l'impact météorologique sur les volumes
- Export des rapports en plusieurs formats (PDF, Excel, CSV)
- Historique des prédictions avec persistance locale

## 🛠️ Technologies Utilisées

- **Frontend:**
  - React avec TypeScript
  - Chart.js pour les visualisations
  - Tailwind CSS pour le style
  - Axios pour les requêtes API

- **Backend:**
  - Python 3.9+
  - FastAPI pour l'API REST
  - Prophet pour les prédictions
  - Pandas pour la manipulation des données

## 📊 Visualisations Disponibles

- **Comparaison Historique**: Graphique linéaire comparant les prédictions avec les données historiques
- **Tendances Saisonnières**: Visualisation des patterns saisonniers sur plusieurs années
- **Impact Météorologique**: Analyse des corrélations entre conditions météo et volumes
- **Statistiques Détaillées**: Métriques de performance du modèle

## 📤 Options d'Export

- **PDF**: Rapport complet avec graphiques et données détaillées
- **Excel**: Données structurées en plusieurs feuilles (prédictions, comparaisons, stats)
- **CSV**: Format simple pour l'analyse des données brutes

## 🚦 Installation

1. Clonez le repository
```bash
git clone [url-du-repo]
cd mikana
```

2. Installez les dépendances frontend
```bash
npm install
```

3. Installez les dépendances Python
```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

1. Backend (FastAPI)
```bash
uvicorn src.api.prediction_service:app --reload --port 8000
```

2. Frontend (React)
```bash
npm run dev
```

## 📝 Utilisation

1. Accédez à l'interface via `http://localhost:5173`
2. Sélectionnez un établissement et un type de linge (optionnel)
3. Choisissez une date ou une période
4. Lancez la prédiction
5. Analysez les résultats via les différentes visualisations
6. Exportez les données dans le format souhaité

## 🔄 Fonctionnalités à Venir

- [ ] Intégration de données météo réelles
- [ ] Personnalisation avancée des graphiques
- [ ] Gestion des utilisateurs et des droits
- [ ] API pour l'import de données externes
- [ ] Dashboard d'administration

## 👥 Équipe

- 
-

## 📄 License

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.
