import pandas as pd
import numpy as np
from prophet import Prophet
import logging
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

class PredicteurTemporel:
    def __init__(self, chemin_donnees='donnees_completes_logistique_formatted.csv'):
        """Initialise le prédicteur avec Prophet"""
        self.models = {}  # Dictionnaire pour stocker les modèles par établissement/article
        
        # Configuration du logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        try:
            # Chargement des données
            self.df_historique = pd.read_csv(chemin_donnees, low_memory=False)
            self.df_historique['DATE'] = pd.to_datetime(self.df_historique['DATE'])
            self.logger.info("✅ Prédicteur temporel initialisé")
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de l'initialisation: {str(e)}")
            raise e

    def preparer_donnees_prophet(self, df, etablissement=None, article=None):
        """Prépare les données pour Prophet"""
        try:
            # Filtrage des données
            df_filtered = df.copy()
            if etablissement:
                df_filtered = df_filtered[df_filtered['ETBDES'] == etablissement]
            if article:
                df_filtered = df_filtered[df_filtered['ARTDES'] == article]
            
            # Agrégation par date
            df_agg = df_filtered.groupby('DATE')['QUANTITE'].sum().reset_index()
            
            # Renommage des colonnes pour Prophet
            df_prophet = df_agg.rename(columns={
                'DATE': 'ds',
                'QUANTITE': 'y'
            })
            
            return df_prophet
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de la préparation des données: {str(e)}")
            raise e

    def entrainer_modele(self, etablissement=None, article=None):
        """Entraîne un modèle Prophet pour une combinaison établissement/article"""
        try:
            # Création de la clé unique pour le modèle
            model_key = f"{etablissement}_{article}"
            
            # Préparation des données
            df_prophet = self.preparer_donnees_prophet(
                self.df_historique, 
                etablissement, 
                article
            )
            
            # Configuration du modèle Prophet avec paramètres optimisés
            model = Prophet(
                changepoint_prior_scale=0.05,    # Augmenter légèrement pour plus de flexibilité
                seasonality_prior_scale=1.0,     # Réduire davantage
                seasonality_mode='multiplicative', # Tester le mode multiplicatif
                daily_seasonality=True           # Activer la saisonnalité journalière
            )
            
            # Entraînement du modèle
            model.fit(df_prophet)
            
            # Stockage du modèle
            self.models[model_key] = model
            
            self.logger.info(f"✅ Modèle entraîné pour {model_key}")
            return model
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de l'entraînement: {str(e)}")
            raise e

    def predire(self, dates_prediction, etablissement=None, article=None):
        """Prédit les quantités pour des dates futures"""
        try:
            # Conversion en DatetimeIndex si nécessaire
            if isinstance(dates_prediction, (str, pd.Timestamp)):
                dates_prediction = pd.DatetimeIndex([pd.to_datetime(dates_prediction)])
            elif isinstance(dates_prediction, tuple):
                start_date, end_date = pd.to_datetime(dates_prediction[0]), pd.to_datetime(dates_prediction[1])
                dates_prediction = pd.date_range(start=start_date, end=end_date, freq='D')
            
            # Assurer que dates_prediction est un DatetimeIndex
            dates_prediction = pd.DatetimeIndex(dates_prediction)

            # Filtrage des données
            df_filtered = self.df_historique.copy()
            
            if etablissement:
                df_filtered = df_filtered[df_filtered['ETBDES'] == etablissement]
            if article:
                df_filtered = df_filtered[df_filtered['ARTDES'] == article]

            # Calculer les statistiques de base
            moyenne = df_filtered['QUANTITE'].mean() if not df_filtered.empty else 100
            min_historique = df_filtered['QUANTITE'].min() if not df_filtered.empty else 10
            max_historique = df_filtered['QUANTITE'].max() if not df_filtered.empty else 200
            
            # Si pas assez de données ou moyenne trop faible
            if len(df_filtered) < 2:
                # Cas spécial pour un article spécifique
                if article:
                    moyenne_article = self.df_historique[self.df_historique['ARTDES'] == article]['QUANTITE'].mean()
                    prediction_base = round(max(50, moyenne_article if not pd.isna(moyenne_article) else 100))
                    message = "Prédiction basée sur la moyenne globale de l'article"
                # Cas spécial pour un établissement spécifique
                elif etablissement:
                    moyenne_etab = self.df_historique[self.df_historique['ETBDES'] == etablissement]['QUANTITE'].mean()
                    prediction_base = round(max(50, moyenne_etab if not pd.isna(moyenne_etab) else 100))
                    message = "Prédiction basée sur la moyenne globale de l'établissement"
                else:
                    prediction_base = round(max(100, moyenne if not pd.isna(moyenne) else 100))
                    message = "Prédiction basée sur la moyenne globale"

                resultats = []
                for date in dates_prediction:
                    resultat = {
                        'date': date.strftime('%Y-%m-%d'),
                        'prediction': prediction_base,
                        'message': message,
                        'statistiques': {
                            'moyenne_historique': round(moyenne) if not pd.isna(moyenne) else None,
                            'minimum_historique': round(min_historique) if not pd.isna(min_historique) else None,
                            'maximum_historique': round(max_historique) if not pd.isna(max_historique) else None,
                            'nombre_donnees': len(df_filtered),
                            'fiabilite': 'basse'
                        }
                    }
                    resultats.append(resultat)
                return resultats

            # Si assez de données, utiliser Prophet
            df_prophet = self.preparer_donnees_prophet(df_filtered)
            
            # Création ou récupération du modèle
            model_key = f"{etablissement}_{article}"
            if model_key not in self.models:
                self.entrainer_modele(etablissement, article)
            
            model = self.models[model_key]
            
            # Préparation des dates pour Prophet
            future_dates = pd.DataFrame({'ds': dates_prediction})
            
            # Prédiction
            forecast = model.predict(future_dates)
            
            # S'assurer que nous avons une prédiction pour chaque date
            resultats = []
            for date in dates_prediction:
                forecast_row = forecast[forecast['ds'] == date].iloc[0]
                prediction = max(min_historique, round(forecast_row['yhat']))
                if prediction < 10:
                    prediction = max(50, round(moyenne))
                
                resultat = {
                    'date': date.strftime('%Y-%m-%d'),
                    'prediction': prediction,
                    'intervalle_confiance': {
                        'min': max(min_historique, round(forecast_row['yhat_lower'])),
                        'max': round(forecast_row['yhat_upper'])
                    },
                    'statistiques': {
                        'moyenne_historique': round(moyenne),
                        'minimum_historique': round(min_historique),
                        'maximum_historique': round(max_historique),
                        'nombre_donnees': len(df_filtered),
                        'fiabilite': 'haute' if len(df_filtered) > 30 else 'moyenne',
                        'tendance': round(forecast_row['trend'], 2),
                        'saisonnalite': round(forecast_row.get('yearly', 0), 2)
                    }
                }
                resultats.append(resultat)
            
            return resultats
            
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de la prédiction: {str(e)}")
            raise e

    def evaluer_performances(self, date_debut, date_fin, etablissement=None, article=None):
        """
        Évalue les performances du modèle sur une période donnée
        """
        try:
            # Convertir les dates en datetime si nécessaire
            date_debut = pd.to_datetime(date_debut)
            date_fin = pd.to_datetime(date_fin)
            
            # Créer la période de test
            dates_test = pd.date_range(start=date_debut, end=date_fin)
            
            # Obtenir les données réelles d'abord
            df_reel = self.preparer_donnees_prophet(
                self.df_historique[self.df_historique['DATE'].isin(dates_test)],
                etablissement,
                article
            )
            
            if df_reel.empty:
                self.logger.warning("⚠️ Pas de données réelles disponibles pour cette période")
                return None
            
            # Ne garder que les dates pour lesquelles nous avons des données réelles
            dates_disponibles = df_reel['ds'].tolist()
            
            # Obtenir les prédictions pour ces dates spécifiques
            predictions = self.predire(dates_disponibles, etablissement, article)
            
            # Création des arrays pour les métriques
            y_true = df_reel['y'].values
            y_pred = np.array([pred['prediction'] for pred in predictions])
            
            # Vérification de la cohérence des données
            if len(y_true) != len(y_pred):
                raise ValueError(f"Nombre différent de valeurs réelles ({len(y_true)}) et prédites ({len(y_pred)})")
            
            # Calcul des métriques
            metrics = {
                'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
                'mae': mean_absolute_error(y_true, y_pred),
                'mape': np.mean(np.abs((y_true - y_pred) / y_true)) * 100,
                'r2': r2_score(y_true, y_pred),
                'me': np.mean(y_pred - y_true)
            }
            
            # Calcul de la précision directionnelle
            if len(y_true) > 1:  # On ne peut calculer la direction que s'il y a au moins 2 points
                direction_reelle = np.diff(y_true) > 0
                direction_pred = np.diff(y_pred) > 0
                metrics['precision_directionnelle'] = np.mean(direction_reelle == direction_pred) * 100
            
            # Calcul de l'intervalle de confiance à 95%
            residuals = y_pred - y_true
            metrics['ic_95'] = {
                'lower': np.percentile(residuals, 2.5),
                'upper': np.percentile(residuals, 97.5)
            }
            
            # Création des visualisations
            plt.figure(figsize=(15, 10))
            
            # Plot 1: Prédictions vs Réel
            plt.subplot(2, 1, 1)
            plt.plot(dates_disponibles, y_true, 'b-', label='Réel', linewidth=2)
            plt.plot(dates_disponibles, y_pred, 'r--', label='Prédictions', linewidth=2)
            plt.fill_between(dates_disponibles, 
                            [pred['intervalle_confiance']['min'] for pred in predictions],
                            [pred['intervalle_confiance']['max'] for pred in predictions],
                            color='r', alpha=0.1, label='Intervalle de confiance')
            plt.title('Prédictions vs Réel')
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
            
            # Plot 2: Distribution des erreurs
            plt.subplot(2, 1, 2)
            plt.hist(residuals, bins=20, edgecolor='black')
            plt.axvline(x=0, color='r', linestyle='--', label='Erreur nulle')
            plt.axvline(x=metrics['me'], color='g', linestyle='-', label='Erreur moyenne')
            plt.title('Distribution des erreurs de prédiction')
            plt.xlabel('Erreur')
            plt.ylabel('Fréquence')
            plt.legend()
            plt.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # Affichage du rapport
            print("\n📊 Rapport de performances du modèle")
            print("=" * 50)
            print(f"Période: du {date_debut.strftime('%Y-%m-%d')} au {date_fin.strftime('%Y-%m-%d')}")
            if etablissement:
                print(f"Établissement: {etablissement}")
            if article:
                print(f"Article: {article}")
            print(f"\nNombre de points de données: {len(y_true)}")
            print("\n📈 Métriques principales:")
            print(f"RMSE: {metrics['rmse']:.2f}")
            print(f"MAE: {metrics['mae']:.2f}")
            print(f"MAPE: {metrics['mape']:.2f}%")
            print(f"R²: {metrics['r2']:.4f}")
            print(f"Erreur moyenne: {metrics['me']:.2f}")
            if 'precision_directionnelle' in metrics:
                print(f"Précision directionnelle: {metrics['precision_directionnelle']:.2f}%")
            print(f"Intervalle de confiance à 95%: [{metrics['ic_95']['lower']:.2f}, {metrics['ic_95']['upper']:.2f}]")
            
            return metrics, plt.gcf()
            
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de l'évaluation des performances: {str(e)}")
            raise e

    def generate_prediction(self, data, params):
        # Obtenir les prédictions
        predictions = self.predire(data, params.get('etablissement'), params.get('article'))
        
        # Calculer les métriques de performance
        y_true = self.df_historique['QUANTITE'].values[-30:]  # Derniers 30 jours réels
        y_pred = np.array([p['prediction'] for p in predictions])[:30]  # Prédictions correspondantes
        
        mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        mae = mean_absolute_error(y_true, y_pred)
        
        # Calculer la tendance
        trend = [p.get('statistiques', {}).get('tendance', 0) for p in predictions]
        trend_direction = 'up' if trend[-1] > trend[0] else 'down'
        trend_strength = abs(trend[-1] - trend[0]) / abs(trend[0]) * 100 if trend[0] != 0 else 0
        
        # Préparer la réponse
        response = {
            'predictions': predictions,  # Utiliser directement les prédictions
            'model_stats': {
                'accuracy': 1 - (mape / 100),
                'mape': mape,
                'rmse': rmse,
                'mae': mae,
                'confidence_level': 0.95,
                'sample_size': len(y_true),
                'trend_direction': trend_direction,
                'trend_strength': trend_strength
            }
        }
        
        return response

# Code de test
if __name__ == "__main__":
    try:
        # Initialisation du prédicteur
        predicteur = PredicteurTemporel()
        
        # Paramètres de test
        test_params = {
            'etablissement': "CHU ROUEN OISSEL",
            'article': None,  # None pour tous les types
            'date_debut': '2025-01-20',
            'date_fin': '2025-01-24'
        }

        # Création de la plage de dates
        dates = pd.date_range(
            start=test_params['date_debut'],
            end=test_params['date_fin'],
            freq='D'
        )

        print("\n=== Test de prédiction sur une période ===")
        print(f"Établissement: {test_params['etablissement']}")
        print(f"Article: {'Tous' if test_params['article'] is None else test_params['article']}")
        print(f"Période: du {test_params['date_debut']} au {test_params['date_fin']}\n")

        # Obtention des prédictions
        predictions = predicteur.predire(
            dates_prediction=dates,
            etablissement=test_params['etablissement'],
            article=test_params['article']
        )

        # Affichage des résultats
        for pred in predictions:
            print(f"\nDate: {pred['date']}")
            print(f"Quantité prédite: {pred['prediction']} unités")
            if 'intervalle_confiance' in pred:
                print(f"Intervalle de confiance: [{pred['intervalle_confiance']['min']} - {pred['intervalle_confiance']['max']}]")
            if 'message' in pred:
                print(f"Message: {pred['message']}")
            print("-" * 50)

    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")