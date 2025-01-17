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

1. Installez Git LFS (obligatoire pour les fichiers volumineux)
```bash
# Windows (avec chocolatey)
choco install git-lfs

# Mac (avec homebrew)
brew install git-lfs

# Linux (Ubuntu/Debian)
sudo apt install git-lfs
```

2. Initialisez Git LFS
```bash
git lfs install
```

3. Clonez le repository
```bash
git clone https://github.com/AbdoulDiouf2/mikana
cd mikana
```

4. Installez les dépendances frontend
```bash
npm install
```

5. Installez les dépendances Python
```bash
pip install -r requirements.txt
```

⚠️ **Note Importante**: Ce projet utilise Git LFS pour gérer les fichiers volumineux (notamment les données CSV). Sans Git LFS, vous n'aurez pas accès aux fichiers de données complets nécessaires au fonctionnement de l'application.

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

ESIGELEC :
- BOUGA Paule Audrey
- BOHI Franck Junior
- DIOUF Abdoul Ahad
- GANKPEZOUNDE Ange
- NOUBOM Michelle D'Or
- SOW Aminata

## 📄 License

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## ❗ Dépannage

Si vous rencontrez des problèmes avec les fichiers de données :

1. Vérifiez que Git LFS est bien installé :
```bash
git lfs version
```

2. Si les fichiers ne se téléchargent pas, forcez le téléchargement :
```bash
git lfs pull
```

3. Pour vérifier le statut des fichiers LFS :
```bash
git lfs status
```

## 🤝 Comment Contribuer

Nous sommes ravis d'accueillir des contributions ! Voici comment participer :

### Prérequis
1. Installez Git LFS (voir section Installation)
2. Configurez votre environnement de développement Python et Node.js

### Processus de contribution
1. Forkez le projet
2. Créez votre branche de fonctionnalité
```bash
git checkout -b feature/AmazingFeature
```

3. Configurez l'environnement de développement
```bash
# Installation des dépendances de développement Python
pip install -r requirements-dev.txt

# Installation des dépendances de développement Node.js
npm install
```

4. Committez vos changements
```bash
git commit -m 'Add: Amazing Feature'
```

5. Poussez vers votre branche
```bash
git push origin feature/AmazingFeature
```

6. Ouvrez une Pull Request

### Standards de code
- Utilisez le formatage Black pour Python
- Suivez les conventions ESLint pour TypeScript/React
- Écrivez des tests unitaires pour les nouvelles fonctionnalités
- Documentez votre code et mettez à jour la documentation si nécessaire

### Tests
```bash
# Tests Python
pytest

# Tests React
npm run test
```

### Signalement de bugs
Si vous trouvez un bug :
1. Vérifiez qu'il n'a pas déjà été signalé dans les Issues
2. Ouvrez une nouvelle Issue en utilisant le template Bug Report
3. Incluez un exemple minimal reproductible

### Suggestions de fonctionnalités
Pour proposer une nouvelle fonctionnalité :
1. Ouvrez une Issue en utilisant le template Feature Request
2. Décrivez clairement le besoin et l'utilisation prévue
3. Attendez la validation de l'équipe avant de commencer le développement
