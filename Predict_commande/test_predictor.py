from predict_commande import UnifiedPredictor
from datetime import datetime, timedelta
import pandas as pd

def test_predictions():
    """
    Script de test pour démontrer les différents cas d'utilisation du UnifiedPredictor
    """
    try:
        # Initialisation du prédicteur
        predictor = UnifiedPredictor()
        print("✅ Prédicteur initialisé avec succès\n")

        # Cas de test 1: Prédiction pour une seule date
        print("🔍 Test 1: Prédiction pour une seule date")
        date = datetime.now() + timedelta(days=1)
        predictions = predictor.predict(date)
        print(f"Prédiction globale pour {date.strftime('%Y-%m-%d')}:")
        print(f"Quantité prédite: {predictions[0]['prediction']} unités")
        print(f"Intervalle de confiance: {predictions[0]['intervalle_confiance']}")
        print(f"Fiabilité: {predictions[0]['statistiques']['fiabilite']}\n")

        # Cas de test 2: Prédiction pour un établissement spécifique
        print("🔍 Test 2: Prédiction pour un établissement spécifique")
        model_info = predictor.get_model_info()
        test_establishment = model_info['establishments'][0]  # Premier établissement disponible
        predictions = predictor.predict(date, establishment=test_establishment)
        print(f"Prédiction pour {test_establishment} le {date.strftime('%Y-%m-%d')}:")
        print(f"Quantité prédite: {predictions[0]['prediction']} unités")
        print(f"Fiabilité: {predictions[0]['statistiques']['fiabilite']}\n")

        # Cas de test 3: Prédiction pour un article spécifique
        print("🔍 Test 3: Prédiction pour un article spécifique")
        test_article = model_info['articles'][0]  # Premier article disponible
        predictions = predictor.predict(date, article=test_article)
        print(f"Prédiction pour l'article {test_article} le {date.strftime('%Y-%m-%d')}:")
        print(f"Quantité prédite: {predictions[0]['prediction']} unités")
        print(f"Fiabilité: {predictions[0]['statistiques']['fiabilite']}\n")

        # Cas de test 4: Prédiction pour une période
        print("🔍 Test 4: Prédiction sur une période")
        dates = pd.date_range(
            start=datetime.now(),
            end=datetime.now() + timedelta(days=7),
            freq='D'
        )
        predictions = predictor.predict(dates)
        print("Prédictions sur 7 jours:")
        for pred in predictions:
            print(f"Date: {pred['date']}, Quantité: {pred['prediction']} unités")
        print()

        # Cas de test 5: Combinaison établissement et article
        print("🔍 Test 5: Prédiction pour un établissement et un article spécifiques")
        predictions = predictor.predict(
            date,
            establishment=test_establishment,
            article=test_article
        )
        print(f"Prédiction pour {test_establishment}, article {test_article}:")
        print(f"Quantité prédite: {predictions[0]['prediction']} unités")
        print(f"Fiabilité: {predictions[0]['statistiques']['fiabilite']}\n")

        # Cas de test 6: Informations sur le modèle
        print("🔍 Test 6: Informations sur le modèle")
        model_info = predictor.get_model_info()
        print("Informations globales du modèle:")
        print(f"Type de modèle: {model_info['modelType']}")
        print(f"Dernière mise à jour: {model_info['lastTrainingDate']}")
        print(f"Précision (R²): {model_info['accuracy']:.4f}")
        print(f"Nombre de points de données: {model_info['dataPoints']}")
        print(f"Nombre d'établissements: {len(model_info['establishments'])}")
        print(f"Nombre d'articles: {len(model_info['articles'])}")
        
        # Afficher quelques métriques détaillées
        print("\nMétriques détaillées:")
        for metric, value in model_info['metrics'].items():
            if isinstance(value, (int, float)):
                print(f"{metric}: {value:.4f}")

        # Cas de test 7: Gestion des erreurs
        print("\n🔍 Test 7: Test de gestion des erreurs")
        try:
            # Test avec un établissement inexistant
            predictions = predictor.predict(date, establishment="INEXISTANT")
            print("⚠️ Le modèle a utilisé un fallback pour l'établissement inexistant")
        except Exception as e:
            print(f"✅ Erreur gérée correctement: {str(e)}")

        # Test de performances
        print("\n🔍 Test 8: Test de performances")
        import time
        start_time = time.time()
        
        # Faire 100 prédictions
        for _ in range(100):
            predictor.predict(date)
            
        end_time = time.time()
        print(f"Temps moyen par prédiction: {((end_time - start_time) / 100) * 1000:.2f} ms")

    except Exception as e:
        print(f"❌ Erreur lors des tests: {str(e)}")

if __name__ == "__main__":
    test_predictions()