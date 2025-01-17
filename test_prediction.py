import pandas as pd
from model_prophet import PredicteurTemporel

def test_single_date():
    print("\n=== Test avec une date unique ===")
    predicteur = PredicteurTemporel()
    
    # Simulation d'une requête pour une date unique
    date = '2025-01-24'
    etablissement = "CHU ROUEN OISSEL"
    
    print(f"Date: {date}")
    print(f"Établissement: {etablissement}")
    
    # Conversion de la date
    date_prediction = pd.to_datetime(date)
    
    # Obtention des prédictions
    predictions = predicteur.predire(
        dates_prediction=date_prediction,
        etablissement=etablissement,
        article=None
    )
    
    print("\nRésultats:")
    for pred in predictions:
        print(f"\nDate: {pred['date']}")
        print(f"Prédiction: {pred['prediction']} unités")
        if 'intervalle_confiance' in pred:
            print(f"Intervalle de confiance: [{pred['intervalle_confiance']['min']} - {pred['intervalle_confiance']['max']}]")

def test_date_range():
    print("\n=== Test avec une période ===")
    predicteur = PredicteurTemporel()
    
    # Simulation d'une requête pour une période
    date_debut = '2025-01-20'
    date_fin = '2025-01-24'
    etablissement = "CHU ROUEN OISSEL"
    
    print(f"Période: du {date_debut} au {date_fin}")
    print(f"Établissement: {etablissement}")
    
    # Création de la plage de dates
    dates = pd.date_range(
        start=pd.to_datetime(date_debut),
        end=pd.to_datetime(date_fin),
        freq='D'
    )
    
    print(f"\nDates générées ({len(dates)} dates):")
    for date in dates:
        print(f"  - {date.strftime('%Y-%m-%d')}")
    
    # Obtention des prédictions
    predictions = predicteur.predire(
        dates_prediction=dates,
        etablissement=etablissement,
        article=None
    )
    
    print("\nRésultats:")
    for pred in predictions:
        print(f"\nDate: {pred['date']}")
        print(f"Prédiction: {pred['prediction']} unités")
        if 'intervalle_confiance' in pred:
            print(f"Intervalle de confiance: [{pred['intervalle_confiance']['min']} - {pred['intervalle_confiance']['max']}]")

if __name__ == "__main__":
    print("=== Tests de prédiction ===")
    
    # Test avec une date unique
    test_single_date()
    
    # Test avec une période
    test_date_range() 