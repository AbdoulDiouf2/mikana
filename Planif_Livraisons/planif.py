#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score
import xgboost as xgb
import joblib

def load_and_preprocess_data(file_path):
    """
    Charge et prétraite les données depuis le fichier Excel
    """
    # Chargement des données
    data = pd.read_excel(file_path)
    
    # Gestion des valeurs manquantes
    if 'Poids' in data.columns:
        data = data.drop(['Poids', 'Poids total'], axis=1)
    
    # Encodage one-hot des variables catégorielles
    data_encoded = pd.get_dummies(data, columns=['Désignation article'], prefix='article')
    
    # Conversion des dates
    if 'Date expédition' in data_encoded.columns:
        data_encoded['Year'] = pd.to_datetime(data_encoded['Date expédition']).dt.year
        data_encoded['Month'] = pd.to_datetime(data_encoded['Date expédition']).dt.month
        data_encoded['Day'] = pd.to_datetime(data_encoded['Date expédition']).dt.day
        data_encoded.drop('Date expédition', axis=1, inplace=True)
    
    return data_encoded

def prepare_train_test_data(data):
    """
    Prépare les données d'entraînement et de test
    """
    X = data.drop('Qté livrée', axis=1)
    y = data['Qté livrée']
    return train_test_split(X, y, test_size=0.2, random_state=42)

def train_xgboost_model(X_train, y_train):
    """
    Entraîne le modèle XGBoost
    """
    xgb_model = xgb.XGBRegressor(random_state=42)
    xgb_model.fit(X_train, y_train)
    return xgb_model

def evaluate_model(model, X_train, y_train, X_test, y_test):
    """
    Évalue le modèle avec cross-validation et sur l'ensemble de test
    """
    # Cross-validation
    cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='neg_mean_squared_error')
    mse_cv = -cv_scores
    print(f"Moyenne des MSE en cross-validation: {np.mean(mse_cv)}")
    
    # Évaluation sur l'ensemble de test
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    print(f"MSE sur test: {mse}")
    print(f"R² sur test: {r2}")
    
    return mse, r2

def save_model(model, filename='xgb_model.joblib'):
    """
    Sauvegarde le modèle entraîné
    """
    joblib.dump(model, filename)
    print(f"Modèle sauvegardé sous: {filename}")

def predict_quantity(model, annee, mois, jour, qte_commandee, designation_article=None, colonnes_modele=None):
    """
    Prédit la quantité livrée en fonction des paramètres d'entrée
    
    Parameters:
    -----------
    model : XGBoost model
        Le modèle entraîné
    annee : int
        Année de la livraison
    mois : int
        Mois de la livraison
    jour : int
        Jour de la livraison
    qte_commandee : float
        Quantité commandée
    designation_article : str, optional
        Désignation de l'article (si applicable)
    colonnes_modele : list, optional
        Liste des colonnes utilisées par le modèle
    
    Returns:
    --------
    float
        Quantité livrée prédite
    """
    # Créer un DataFrame avec les informations de base
    input_data = pd.DataFrame({
        'Year': [annee],
        'Month': [mois],
        'Day': [jour],
        'Qté cdée': [qte_commandee]
    })
    
    # Si nous avons une désignation d'article et les colonnes du modèle
    if designation_article is not None and colonnes_modele is not None:
        # Créer les colonnes one-hot pour tous les articles possibles
        for col in colonnes_modele:
            if col.startswith('article_'):
                input_data[col] = 0
        
        # Mettre à 1 la colonne correspondant à l'article
        col_article = f'article_{designation_article}'
        if col_article in colonnes_modele:
            input_data[col_article] = 1
    
    # Assurer que toutes les colonnes nécessaires sont présentes
    if colonnes_modele is not None:
        for col in colonnes_modele:
            if col not in input_data.columns and col not in ['Qté livrée']:
                input_data[col] = 0
        
        # Réorganiser les colonnes dans le même ordre que le modèle
        input_data = input_data[colonnes_modele]
    
    # Prédire la quantité livrée
    qte_livree_predite = model.predict(input_data)[0]
    return qte_livree_predite

def main():
    # Chemin du fichier
    file_path = 'Planif livraisons.xlsx'
    
    # Chargement et prétraitement des données
    print("Chargement et prétraitement des données...")
    data = load_and_preprocess_data(file_path)
    
    # Préparation des données d'entraînement et de test
    print("Préparation des données d'entraînement et de test...")
    X_train, X_test, y_train, y_test = prepare_train_test_data(data)
    
    # Entraînement du modèle
    print("Entraînement du modèle XGBoost...")
    model = train_xgboost_model(X_train, y_train)
    
    # Évaluation du modèle
    print("Évaluation du modèle...")
    mse, r2 = evaluate_model(model, X_train, y_train, X_test, y_test)
    
    # Sauvegarde du modèle
    save_model(model)
    
    # Exemple de prédiction
    print("\nExemple de prédiction:")
    colonnes_modele = X_train.columns.tolist()
    qte_livree_predite = predict_quantity(
        model=model,
        annee=2025,
        mois=1,
        jour=31,
        qte_commandee=84627,
        colonnes_modele=colonnes_modele
    )
    print(f"La quantité livrée prédite pour le 31/1/2025 avec 84627 unités commandées est : {qte_livree_predite:.2f}")

if __name__ == "__main__":
    main()