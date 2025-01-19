# MIKANA - Application de Prédiction de Commandes

Cette application permet de prédire les futures commandes de linge en utilisant le modèle Prophet de Facebook. Elle offre une interface utilisateur intuitive pour analyser et visualiser les prévisions de commandes.

---

## Sommaire
1. [Fonctionnalités](#-fonctionnalités)
2. [Technologies Utilisées](#-technologies-utilisées)
3. [Visualisations Disponibles](#-visualisations-disponibles)
4. [Options d'Export](#-options-dexport)
5. [Guide de Démarrage](#-guide-de-démarrage)
6. [Installation](#-installation)
7. [Configuration](#%ef%b8%8f-configuration)
8. [Utilisation](#-utilisation)
9. [Fonctionnalités à Venir](#-fonctionnalités-%c3%a0-venir)
10. [Contribuer](#-comment-contribuer)
11. [Dépannage](#%e2%9d%97-d%C3%A9pannage)

---

## 🚀 Fonctionnalités

- Prédiction des commandes futures basée sur les données historiques.
- Visualisation des statistiques de prédiction avec des graphiques interactifs.
- Comparaison avec les données historiques des années précédentes.
- Analyse des tendances saisonnières.
- Analyse de l'impact météorologique sur les volumes.
- Export des rapports en PDF, Excel et CSV.
- Historique des prédictions avec persistance locale.

## 🛠️ Technologies Utilisées

- **Frontend**
  - React avec TypeScript
  - Chart.js pour les visualisations
  - Tailwind CSS pour le style
  - Axios pour les requêtes API

- **Backend**
  - Python 3.9+
  - FastAPI pour l'API REST
  - Prophet pour les prédictions
  - Pandas pour la manipulation des données

## 📊 Visualisations Disponibles

- **Comparaison Historique** : Graphique linéaire des prédictions et données historiques.
- **Tendances Saisonnières** : Modèles saisonniers sur plusieurs années.
- **Impact Météorologique** : Corrélations entre conditions météo et volumes.
- **Statistiques Détaillées** : Performances du modèle.

## 📤 Options d'Export

- **PDF** : Rapport complet avec graphiques.
- **Excel** : Données structurées en plusieurs feuilles.
- **CSV** : Format brut pour l'analyse.

## 🚦 Guide de Démarrage

### Prérequis
1. Installer [Git](https://git-scm.com/downloads).
2. Installer Git LFS pour les fichiers volumineux :
   ```bash
   git lfs install
   git lsf pull
   ```
3. Installer Python 3.9+ depuis [python.org](https://www.python.org/downloads/).
4. Installer Node.js et npm depuis [nodejs.org](https://nodejs.org/).

### Installation
1. Clonez le repository :
   ```bash
   git clone https://github.com/AbdoulDiouf2/mikana
   cd mikana
   ```
2. Installez les dépendances :
   - **Frontend** :
     ```bash
     npm install
     ```
   - **Backend** :
     ```bash
     python -m venv venv
     source venv/bin/activate  # Windows : venv\Scripts\activate
     pip install -r requirements.txt
     ```

3. Configurez Git LFS si ce n’est pas déjà fait :
   ```bash
   git lfs install
   ```

### Configuration
1. Lancez le backend :
   ```bash
   uvicorn src.api.prediction_service:app --reload --port 8000
   ```
2. Lancez le frontend :
   ```bash
   npm run dev
   ```
3. Accédez à l'application via [http://localhost:5173](http://localhost:5173).

## 📝 Utilisation

1. Sélectionnez un établissement et un type de linge (optionnel).
2. Choisissez une période de prédiction.
3. Lancez la prédiction.
4. Analysez les résultats avec les graphiques interactifs.
5. Exportez les rapports au format souhaité.

## 🔄 Fonctionnalités à Venir

- [ ] Intégration de données météo réelles.
- [ ] Personnalisation avancée des graphiques.
- [ ] Gestion des utilisateurs et des droits.
- [ ] API pour l'import de données externes.
- [ ] Dashboard d'administration.

## 🤝 Comment Contribuer

1. Forkez le projet.
2. Créez une branche pour votre fonctionnalité :
   ```bash
   git checkout -b feature/ma-fonctionnalite
   ```
3. Configurez votre environnement :
   ```bash
   pip install -r requirements-dev.txt
   npm install
   ```
4. Faites vos changements et commitez :
   ```bash
   git commit -m "Ajout : Nouvelle fonctionnalité"
   ```
5. Envoyez vos changements :
   ```bash
   git push origin feature/ma-fonctionnalite
   ```
6. Créez une Pull Request sur GitHub.

## ❗ Dépannage

- **Git LFS** :
  ```bash
  git lfs version  # Vérification
  git lfs pull     # Forcer le téléchargement
  ```

- **Python non reconnu sur Windows** : Consultez la section [Problèmes communs](#d%C3%A9pannage).

- **Tests** :
  - Python :
    ```bash
    pytest
    ```
  - React :
    ```bash
    npm run test
    ```

---

**Equipe :**
- BOUGA Paule Audrey
- BOHI Franck Junior
- DIOUF Abdoul Ahad
- GANKPEZOUNDE Ange
- NOUBOM Michelle D'Or
- SOW Aminata

