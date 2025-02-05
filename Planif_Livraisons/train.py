#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from xgboost import XGBRegressor
import joblib
import json
from datetime import datetime

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
    xgb_model = XGBRegressor(
        n_estimators=200,
        learning_rate=0.1,
        max_depth=6,
        random_state=42
    )
    xgb_model.fit(X_train, y_train)
    return xgb_model

def evaluate_model(model, X_train, y_train, X_test, y_test):
    """
    Évalue le modèle et retourne un dictionnaire de métriques
    """
    metrics = {}
    
    # Évaluation sur l'ensemble d'entraînement
    y_train_pred = model.predict(X_train)
    metrics['train_mse'] = mean_squared_error(y_train, y_train_pred)
    metrics['train_rmse'] = np.sqrt(metrics['train_mse'])
    metrics['train_mae'] = mean_absolute_error(y_train, y_train_pred)
    metrics['train_r2'] = r2_score(y_train, y_train_pred)
    
    # Évaluation sur l'ensemble de test
    y_test_pred = model.predict(X_test)
    metrics['test_mse'] = mean_squared_error(y_test, y_test_pred)
    metrics['test_rmse'] = np.sqrt(metrics['test_mse'])
    metrics['test_mae'] = mean_absolute_error(y_test, y_test_pred)
    metrics['test_r2'] = r2_score(y_test, y_test_pred)
    
    # Remove cross-validation for now
    metrics['cv_rmse'] = 0.0
    metrics['cv_rmse_std'] = 0.0
    
    return metrics

def save_model_and_metadata(model, columns, metrics, 
                          model_filename='xgb_model.joblib', 
                          columns_filename='model_columns.joblib',
                          metrics_filename='model_metrics.json'):
    """
    Sauvegarde le modèle, les colonnes et les métriques avec horodatage
    """
    # Création d'un dictionnaire de métadonnées
    metadata = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'metrics': metrics
    }
    
    # Sauvegarde du modèle et des colonnes
    joblib.dump(model, model_filename)
    joblib.dump(columns, columns_filename)
    
    # Sauvegarde des métriques et métadonnées
    with open(metrics_filename, 'w') as f:
        json.dump(metadata, f, indent=4)
    
    return metadata

def print_metrics(metrics):
    """
    Affiche les métriques de manière formatée
    """
    print("\n=== Performances du modèle ===")
    print("\nEnsemble d'entraînement:")
    print(f"R² Score: {metrics['train_r2']:.4f}")
    print(f"RMSE: {metrics['train_rmse']:.4f}")
    print(f"MAE: {metrics['train_mae']:.4f}")
    
    print("\nEnsemble de test:")
    print(f"R² Score: {metrics['test_r2']:.4f}")
    print(f"RMSE: {metrics['test_rmse']:.4f}")
    print(f"MAE: {metrics['test_mae']:.4f}")
    
    print("\nCross-validation (5-fold):")
    print(f"RMSE moyen: {metrics['cv_rmse']:.4f} (±{metrics['cv_rmse_std']:.4f})")

def save_metrics_to_json(metrics, filename='model_metrics.json'):
    """
    Sauvegarde uniquement les métriques dans un fichier JSON
    """
    metrics_dict = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'metrics': {          
            'test_r2': metrics['test_r2'],
            'test_rmse': metrics['test_rmse'],
            'test_mae': metrics['test_mae']
        }
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(metrics_dict, f, indent=4, ensure_ascii=False)

def main():
    # Chemin du fichier
    file_path = 'Planif livraisons.xlsx'
    
    try:
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
        metrics = evaluate_model(model, X_train, y_train, X_test, y_test)
        
        # Affichage des métriques
        print_metrics(metrics)

        metrics = evaluate_model(model, X_train, y_train, X_test, y_test)
        save_metrics_to_json(metrics)
        
        # Sauvegarde du modèle et des métadonnées
        metadata = save_model_and_metadata(model, X_train.columns, metrics)
        
        print("\nEntraînement terminé avec succès!")
        print(f"Modèle sauvegardé le: {metadata['timestamp']}")
        
        # Retourner les métriques pour utilisation ultérieure si nécessaire
        return metrics
        
    except Exception as e:
        print(f"\nErreur lors de l'entraînement: {str(e)}")
        return None

if __name__ == "__main__":
    metrics = main()