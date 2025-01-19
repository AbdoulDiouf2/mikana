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

## 🚀 Guide de démarrage

Suivez les étapes ci-dessous pour configurer votre environnement et tester l'application sur un nouvel ordinateur.

### 1. Installer Git

Téléchargez et installez Git depuis [le site officiel](https://git-scm.com/downloads). Suivez les instructions spécifiques à votre système d'exploitation.

### 2. Installer Git LFS

Git LFS est nécessaire pour gérer les fichiers volumineux. Après avoir installé Git, exécutez les commandes suivantes dans votre terminal :

```bash
git lfs install
```

### 3. Installer Python

Téléchargez et installez Python 3.9+ depuis [le site officiel](https://www.python.org/downloads/). Assurez-vous d'ajouter Python à votre PATH lors de l'installation.

### 4. Installer Node.js et npm

Téléchargez et installez Node.js (qui inclut npm) depuis [le site officiel](https://nodejs.org/). Suivez les instructions spécifiques à votre système d'exploitation.

### 5. Cloner le dépôt

Clonez le projet en utilisant Git :

```bash
git clone https://github.com/AbdoulDiouf2/mikana.git
cd mikana
```

### 6. Installer les dépendances Python

Créez un environnement virtuel et installez les dépendances :

```bash
python -m venv venv
source venv/bin/activate  # Sur Windows : venv\Scripts\activate
pip install -r requirements.txt
```

### 7. Installer les dépendances frontend

Installez les dépendances Node.js :

```bash
npm install
```

### 8. Configurer les variables d'environnement

Créez un fichier `.env` à la racine du projet et ajoutez-y les configurations nécessaires. Vous pouvez vous référer à `.env.example` pour les variables requises.

### 9. Démarrer les services

Ouvrez deux terminaux :

- **Terminal 1** : Démarrez le backend FastAPI
  ```bash
  uvicorn src.api.prediction_service:app --reload --port 8000
  ```

- **Terminal 2** : Démarrez le frontend React
  ```bash
  npm run dev
  ```

### 10. Accéder à l'application

Ouvrez votre navigateur et allez à [http://localhost:5173](http://localhost:5173) pour accéder à l'interface utilisateur de l'application.

### ⚠️ Remarques

- Assurez-vous que tous les prérequis sont installés correctement.
- Si vous rencontrez des problèmes lors de l'installation des dépendances, vérifiez les versions de Python et Node.js.
- Consultez la section [Dépannage](#-dépannage) en cas de problèmes avec Git LFS ou d'autres erreurs.

## 🤝 Comment Contribuer

Nous sommes ravis d'accueillir des contributions ! Voici comment participer :

### Prérequis
1. Installez Git LFS (voir section Installation)
2. Configurez votre environnement de développement Python et Node.js

### Processus de contribution
1. Forkez le projet
   1. Rendez-vous sur la page GitHub du projet.
   2. Cliquez sur le bouton "Fork" situé en haut à droite de la page.
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
