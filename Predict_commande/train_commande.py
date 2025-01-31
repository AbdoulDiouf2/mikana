import pandas as pd
import numpy as np
from prophet import Prophet
import logging
import joblib
import json
import os
from datetime import datetime
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import gc

class UnifiedModelTrainer:
    def __init__(self, data_path='donnees_completes_logistique_formatted.csv', batch_size=1000):
        """Initialise l'entraîneur avec configuration améliorée"""
        self.data_path = data_path
        self.batch_size = batch_size
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        try:
            # Chargement et prétraitement des données
            self.df_historique = pd.read_csv(self.data_path, low_memory=False)
            self.df_historique['DATE'] = pd.to_datetime(self.df_historique['DATE'])
            
            # Supprimer les valeurs aberrantes
            Q1 = self.df_historique['QUANTITE'].quantile(0.25)
            Q3 = self.df_historique['QUANTITE'].quantile(0.75)
            IQR = Q3 - Q1
            self.df_historique = self.df_historique[
                (self.df_historique['QUANTITE'] >= Q1 - 1.5 * IQR) & 
                (self.df_historique['QUANTITE'] <= Q3 + 1.5 * IQR)
            ]
            
            # Extraire les établissements et articles significatifs
            min_occurrences = 30  # Minimum de points de données requis
            etb_counts = self.df_historique['ETBDES'].value_counts()
            art_counts = self.df_historique['ARTDES'].value_counts()
            
            valid_etbs = etb_counts[etb_counts >= min_occurrences].index
            valid_arts = art_counts[art_counts >= min_occurrences].index
            
            self.df_historique = self.df_historique[
                self.df_historique['ETBDES'].isin(valid_etbs) & 
                self.df_historique['ARTDES'].isin(valid_arts)
            ]
            
            self.establishments = valid_etbs.tolist()
            self.articles = valid_arts.tolist()
            
            self.logger.info("✅ Données nettoyées et chargées avec succès")
            self.logger.info(f"Établissements retenus: {len(self.establishments)}")
            self.logger.info(f"Articles retenus: {len(self.articles)}")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur lors du chargement: {str(e)}")
            raise e

    def prepare_training_data(self):
        """Prépare les données avec caractéristiques enrichies"""
        try:
            # Agrégation avec features temporelles
            df_grouped = self.df_historique.groupby(['DATE', 'ETBDES', 'ARTDES'])['QUANTITE'].agg([
                'sum',
                'count',
                'mean',
                'std'
            ]).reset_index()
            
            df_grouped['ds'] = df_grouped['DATE']
            df_grouped['y'] = df_grouped['sum']
            
            # Features temporelles
            df_grouped['dayofweek'] = df_grouped['DATE'].dt.dayofweek
            df_grouped['month'] = df_grouped['DATE'].dt.month
            df_grouped['year'] = df_grouped['DATE'].dt.year
            
            # Encodage des établissements et articles
            df_grouped['establishment_id'] = pd.Categorical(df_grouped['ETBDES']).codes
            df_grouped['article_id'] = pd.Categorical(df_grouped['ARTDES']).codes
            
            # Features d'interaction
            df_grouped['etb_art_interaction'] = df_grouped['establishment_id'] * df_grouped['article_id']
            
            # Ajout des moyennes mobiles
            for window in [7, 14, 30]:
                df_grouped[f'moving_avg_{window}d'] = df_grouped.groupby(['ETBDES', 'ARTDES'])['y'].transform(
                    lambda x: x.rolling(window, min_periods=1).mean()
                )
            
            return df_grouped
            
        except Exception as e:
            self.logger.error(f"❌ Erreur préparation données: {str(e)}")
            raise e

    def calculate_metrics_batch(self, model, data):
        """Calcule les métriques par lots pour économiser la mémoire"""
        try:
            self.logger.info("Calcul des métriques par lots...")
            total_mse = 0
            total_mae = 0
            total_samples = 0
            y_true_all = []
            y_pred_all = []
            
            # Traiter les données par lots
            n_batches = len(data) // self.batch_size + (1 if len(data) % self.batch_size > 0 else 0)
            
            for batch_idx in range(n_batches):
                start_idx = batch_idx * self.batch_size
                end_idx = min(start_idx + self.batch_size, len(data))
                
                self.logger.info(f"Traitement du lot {batch_idx + 1}/{n_batches}")
                batch = data.iloc[start_idx:end_idx]
                
                # Prédictions sur le batch
                forecast = model.predict(batch[['ds', 'establishment_id', 'article_id']])
                
                y_true = batch['y'].values
                y_pred = forecast['yhat'].values
                
                y_true_all.extend(y_true)
                y_pred_all.extend(y_pred)
                
                # Libérer la mémoire
                del forecast
                gc.collect()
            
            # Calculer les métriques finales
            y_true_all = np.array(y_true_all)
            y_pred_all = np.array(y_pred_all)
            
            metrics = {
                'mse': float(mean_squared_error(y_true_all, y_pred_all)),
                'rmse': float(np.sqrt(mean_squared_error(y_true_all, y_pred_all))),
                'mae': float(mean_absolute_error(y_true_all, y_pred_all)),
                'r2': float(r2_score(y_true_all, y_pred_all)),
                'data_points': int(len(y_true_all)),
                'last_updated': datetime.now().isoformat()
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"❌ Erreur lors du calcul des métriques: {str(e)}")
            raise e

    def train_unified_model(self):
        """Entraîne le modèle avec configuration optimisée"""
        try:
            training_data = self.prepare_training_data()
            
            model = Prophet(
                changepoint_prior_scale=0.001,  # Réduit pour plus de stabilité
                seasonality_prior_scale=10.0,   # Augmenté pour capturer la saisonnalité
                seasonality_mode='multiplicative',
                daily_seasonality=True,
                yearly_seasonality=True,
                weekly_seasonality=True,
                uncertainty_samples=50
            )
            
            # Ajout des régresseurs
            for col in ['establishment_id', 'article_id', 'etb_art_interaction']:
                model.add_regressor(col)
            
            # Ajout des moyennes mobiles comme régresseurs
            for window in [7, 14, 30]:
                model.add_regressor(f'moving_avg_{window}d')
            
            # Colonnes pour l'entraînement
            train_cols = ['ds', 'y', 'establishment_id', 'article_id', 'etb_art_interaction'] + \
                        [f'moving_avg_{window}d' for window in [7, 14, 30]]
            
            model.fit(training_data[train_cols])
            
            # Calcul des métriques et sauvegarde
            metrics = self.calculate_metrics_batch(model, training_data)
            
            # Créer le dossier trained_models s'il n'existe pas
            os.makedirs('trained_models', exist_ok=True)
            
            # Préparer les métriques et informations pour le JSON
            metrics_data = {
                'model_metrics': metrics,
                'model_info': {
                    'establishments_count': len(self.establishments),
                    'articles_count': len(self.articles),
                    'total_data_points': len(training_data),
                    'training_date': datetime.now().isoformat(),
                    'prophet_params': {
                        'changepoint_prior_scale': 0.05,
                        'seasonality_prior_scale': 1.0,
                        'seasonality_mode': 'multiplicative'
                    }
                },
                'data_summary': {
                    'date_range': {
                        'start': training_data['ds'].min().strftime('%Y-%m-%d'),
                        'end': training_data['ds'].max().strftime('%Y-%m-%d')
                    },
                    'establishments': self.establishments.tolist(),
                    'articles': self.articles.tolist()
                }
            }
            
            # Sauvegarder les métriques dans un fichier JSON
            metrics_path = os.path.join('trained_models', 'model_metrics.json')
            with open(metrics_path, 'w', encoding='utf-8') as f:
                json.dump(metrics_data, f, ensure_ascii=False, indent=4)
            
            self.logger.info(f"✅ Métriques sauvegardées dans {metrics_path}")
            
            # Sauvegarder le modèle
            self.logger.info("Sauvegarde du modèle...")
            unified_model = {
                'model': model,
                'establishments': self.establishments.tolist(),
                'articles': self.articles.tolist(),
                'establishment_mapping': dict(enumerate(self.establishments)),
                'article_mapping': dict(enumerate(self.articles)),
                'last_training_date': datetime.now().isoformat()
            }
            
            model_path = os.path.join('trained_models', 'unified_model.joblib')
            joblib.dump(unified_model, model_path)
            
            self.logger.info(f"✅ Modèle unifié sauvegardé dans {model_path}")
            self.logger.info("✅ Entraînement terminé avec succès")
            
            # Afficher un résumé des métriques
            self.logger.info("\nRésumé des performances du modèle:")
            self.logger.info(f"RMSE: {metrics['rmse']:.2f}")
            self.logger.info(f"MAE: {metrics['mae']:.2f}")
            self.logger.info(f"R²: {metrics['r2']:.4f}")
            self.logger.info(f"Nombre de points de données: {metrics['data_points']}")
            
            return unified_model, metrics_data
            
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de l'entraînement du modèle unifié: {str(e)}")
            raise e

if __name__ == "__main__":
    trainer = UnifiedModelTrainer(batch_size=1000)
    unified_model, metrics = trainer.train_unified_model()