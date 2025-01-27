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

if __name__ == "__main__":
    main()