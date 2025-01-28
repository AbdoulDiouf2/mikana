#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import joblib
from datetime import datetime
import os

def load_model_and_columns(model_filename='xgb_model.joblib', columns_filename='model_columns.joblib'):
    """
    Charge le modèle et les colonnes sauvegardés
    """
    model = joblib.load(model_filename)
    columns = joblib.load(columns_filename)
    return model, columns

def load_model():
    """Charge le modèle de prédiction"""
    try:
        model_path = os.path.join(os.path.dirname(__file__), 'xgb_model.joblib')
        print(f"Tentative de chargement du modèle depuis: {model_path}")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Le fichier du modèle n'existe pas: {model_path}")
        model = joblib.load(model_path)
        print("Modèle chargé avec succès")
        return model
    except Exception as e:
        raise Exception(f"Erreur lors du chargement du modèle: {str(e)}")

def prepare_input_data(date: datetime, article: str, quantity: float, model_columns=None):
    """Prépare les données d'entrée pour la prédiction"""
    print(f"Création du DataFrame initial avec date={date}, article={article}, quantity={quantity}")
    
    input_data = pd.DataFrame({
        'Year': [date.year],
        'Month': [date.month],
        'Day': [date.day],
        'Qté cdée': [quantity]
    })
    
    if model_columns is not None:
        print(f"Colonnes du modèle: {model_columns}")
        
        # Créer un dictionnaire pour les colonnes one-hot de l'article
        article_cols = {}
        for col in model_columns:
            if col.startswith('article_'):
                article_cols[col] = [1 if col == f'article_{article}' else 0]
        
        # Ajouter les colonnes one-hot
        for col, value in article_cols.items():
            input_data[col] = value
            
        print(f"Colonnes après one-hot encoding: {input_data.columns.tolist()}")
                
        # S'assurer que toutes les colonnes nécessaires sont présentes
        model_cols_set = set(model_columns)
        input_cols_set = set(input_data.columns)
        missing_cols = model_cols_set - input_cols_set - {'Qté livrée'}
        
        print(f"Colonnes manquantes: {missing_cols}")
        
        # Ajouter les colonnes manquantes avec des zéros
        for col in missing_cols:
            input_data[col] = [0]
        
        # Réorganiser les colonnes dans le même ordre que le modèle
        final_columns = [col for col in model_columns if col != 'Qté livrée']
        input_data = input_data[final_columns]
        
        print(f"Colonnes finales: {input_data.columns.tolist()}")
    
    return input_data

def predict_quantity(model, colonnes_modele, annee, mois, jour, qte_commandee, designation_article=None):
    """
    Prédit la quantité livrée en fonction des paramètres d'entrée
    """
    # Créer un dictionnaire avec toutes les colonnes initialisées à 0
    data_dict = {col: 0 for col in colonnes_modele}
    
    # Mettre à jour les valeurs de base
    data_dict.update({
        'Year': annee,
        'Month': mois,
        'Day': jour,
        'Qté cdée': qte_commandee
    })
    
    # Si un article est spécifié, mettre à jour sa colonne
    if designation_article is not None:
        col_article = f'article_{designation_article}'
        if col_article in colonnes_modele:
            data_dict[col_article] = 1
        else:
            print(f"Attention: L'article '{designation_article}' n'est pas dans le modèle!")
    
    # Créer le DataFrame en une seule fois
    input_data = pd.DataFrame([data_dict])[colonnes_modele]
    
    # Prédire la quantité livrée
    qte_livree_predite = model.predict(input_data)[0]
    return qte_livree_predite

def predict_delivery(date: datetime, article: str, quantity: float) -> dict:
    """
    Prédit la quantité qui sera livrée
    
    Args:
        date (datetime): Date de livraison
        article (str): Désignation de l'article
        quantity (float): Quantité commandée
        
    Returns:
        dict: Résultats de la prédiction avec recommandations
    """
    try:
        print(f"Début de la prédiction pour: date={date}, article={article}, quantity={quantity}")
        
        # Charger le modèle et vérifier la validité de l'article
        model = load_model()
        columns_path = os.path.join(os.path.dirname(__file__), 'model_columns.joblib')
        model_columns = joblib.load(columns_path)
        
        # Extraire la liste des articles valides
        valid_articles = [col[8:] for col in model_columns if col.startswith('article_')]
        
        # Vérifier que l'article est valide
        if article not in valid_articles:
            raise ValueError(f"Article non valide: {article}. Articles valides: {', '.join(valid_articles)}")
            
        # Vérifier que la quantité est positive
        if quantity <= 0:
            raise ValueError("La quantité doit être positive")
        
        # Préparer les données
        print("Préparation des données d'entrée...")
        input_data = prepare_input_data(
            date=date,
            article=article,
            quantity=quantity,
            model_columns=model_columns
        )
        
        # Faire la prédiction
        print("Exécution de la prédiction...")
        predicted_qty = float(model.predict(input_data)[0])  # Conversion en float Python standard
        
        # Calculer le taux de livraison
        delivery_rate = float((predicted_qty / quantity) * 100)  # Conversion en float Python standard

        # Calculer l'erreur de prédiction (en pourcentage)
        prediction_error = abs(quantity - predicted_qty) / quantity * 100
        
        # Calculer la précision (100 - erreur)
        prediction_accuracy = 100 - prediction_error
        
        # Déterminer le statut en fonction du taux de livraison
        if delivery_rate >= 95:
            status = "excellent"
            recommendation = "Livraison optimale prévue"
        elif delivery_rate >= 85:
            status = "good"
            recommendation = "Bonne livraison prévue"
        else:
            status = "warning"
            recommendation = "Risque de sous-livraison, considérer l'ajustement de la commande"
        
        return {
            "predicted_quantity": predicted_qty,
            "delivery_rate": delivery_rate,
            "prediction_error": prediction_error,
            "prediction_accuracy": prediction_accuracy,
            "status": status,
            "recommendation": recommendation
        }
        
    except Exception as e:
        print(f"❌ Erreur détaillée lors de la prédiction: {str(e)}")
        raise Exception(f"Erreur lors de la prédiction: {str(e)}")

def main():
    # Charger le modèle et les colonnes
    try:
        model, colonnes_modele = load_model_and_columns()
    except FileNotFoundError:
        print("Erreur: Modèle ou fichier de colonnes non trouvé!")
        print("Assurez-vous d'avoir d'abord exécuté train_model.py")
        return
    
    # Exemple de prédiction
    annee = 2025
    mois = 1
    jour = 31
    qte_commandee = 801
    designation_article = "BANDEAU DE BALAYAGE"  # Remplacer par le nom réel de l'article
    
    qte_livree_predite = predict_quantity(
        model=model,
        colonnes_modele=colonnes_modele,
        annee=annee,
        mois=mois,
        jour=jour,
        qte_commandee=qte_commandee,
        designation_article=designation_article
    )
    
    print(f"\nPrédiction pour:")
    print(f"Date: {jour}/{mois}/{annee}")
    print(f"Article: {designation_article}")
    print(f"Quantité commandée: {qte_commandee}")
    print(f"Quantité livrée prédite: {qte_livree_predite:.2f}")

    # Exemple d'utilisation
    test_date = datetime(2025, 1, 31)
    test_article = "DRAP PLAT"
    test_quantity = 84627
    
    result = predict_delivery(test_date, test_article, test_quantity)
    print("\nRésultat de la prédiction :")
    print(f"Quantité prédite : {result['predicted_quantity']} unités")
    print(f"Taux de livraison : {result['delivery_rate']}%")
    print(f"Erreur de prédiction : {result['prediction_error']}%")
    print(f"Précision de prédiction : {result['prediction_accuracy']}%")
    print(f"Statut : {result['status']}")
    print(f"Recommandation : {result['recommendation']}")

if __name__ == "__main__":
    main()