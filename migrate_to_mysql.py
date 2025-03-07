import pandas as pd
import sqlite3
import mysql.connector
from sqlalchemy import create_engine, Table, Column, Integer, Float, String, DateTime, MetaData
from datetime import datetime
import os

def migrate_data():
    # Connexion à l'ancienne base SQLite
    sqlite_conn = sqlite3.connect('predictions.db')

    # Lire toutes les tables de SQLite
    tables = pd.read_sql_query(
        "SELECT name FROM sqlite_master WHERE type='table'", 
        sqlite_conn
    )

    # Configuration MySQL
    mysql_config = {
        'user': 'mikana_user',
        'password': 'mikana_password',
        'host': 'localhost',  # Changez à 'mysql' si vous utilisez Docker
        'database': 'mikana_db'
    }

    # Création de la connexion SQLAlchemy
    engine = create_engine(f"mysql+pymysql://{mysql_config['user']}:{mysql_config['password']}@{mysql_config['host']}/{mysql_config['database']}")

    # Migration de chaque table
    for table_name in tables['name']:
        # Lire les données de SQLite
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", sqlite_conn)
        
        # Écrire dans MySQL
        df.to_sql(
            table_name, 
            engine, 
            if_exists='replace', 
            index=False
        )
    sqlite_conn.close()

    # Migration des commandes
    print("Migration des commandes...")
    df_commandes = pd.read_csv('donnees_completes_logistique_formatted.csv', low_memory=False)
    df_commandes.rename(columns={
        'ETBDES': 'etablissement',
        'ARTDES': 'article',
        'DATE': 'date_commande',
        'QUANTITE': 'quantite',
        'PTLDES': 'point_livraison',
        'Jour': 'jour',
        'Mois': 'mois',
        'Année': 'annee'
    }, inplace=True)
    df_commandes.to_sql('commandes', engine, if_exists='replace', index=False)

    # Migration des livraisons
    print("Migration des livraisons...")
    df_livraisons = pd.read_excel('Planif_Livraisons/Planif livraisons.xlsx')
    df_livraisons.rename(columns={
        'Année': 'annee',
        'Client': 'client',
        'Catégorie': 'categorie',
        'Libellé': 'libelle',
        'Poids (kg)': 'poids_kg',
        'Qté': 'quantite'
    }, inplace=True)
    df_livraisons.to_sql('livraisons', engine, if_exists='replace', index=False)

    # Migration des présences
    print("Migration des présences RH...")
    # Lire directement le fichier qui contient toutes les années
    df_presences = pd.read_excel('Gestion_RH/Total_Presents_Final.xlsx')
    
    # Ajouter une colonne année si elle n'existe pas déjà
    if 'annee' not in df_presences.columns:
        # Nous supposons que l'année est spécifiée quelque part dans les données
        # Vous devrez peut-être ajuster cette logique selon la structure de votre fichier
        print("Structure du DataFrame des présences:", df_presences.columns)
        print("Premières lignes:", df_presences.head())
        
    # Renommer les colonnes
    df_presences.rename(columns={
        'Semaines': 'semaine',
        'Présences': 'nombre_presences'
    }, inplace=True)
    
    # Suppression des lignes vides ou NaN si nécessaire
    df_presences = df_presences.dropna(how='all')
    
    print("Données des présences avant import:", df_presences.head())
    print("Types de données:", df_presences.dtypes)
    
    # Import dans MySQL
    try:
        df_presences.to_sql('presences', engine, if_exists='replace', index=False)
        print("Import des présences réussi!")
    except Exception as e:
        print(f"Erreur lors de l'import des présences: {str(e)}")

    # Création de la table metrics_history
    print("Création de la table metrics_history...")
    try:
        # Créer la table metrics_history avec SQLAlchemy
        metadata = MetaData()
        metrics_history = Table('metrics_history', metadata,
            Column('id', Integer, primary_key=True, autoincrement=True),
            Column('model_name', String(100), nullable=False),
            Column('r2_score', Float),
            Column('mae', Float),
            Column('rmse', Float),
            Column('training_date', DateTime, default=datetime.utcnow),
            Column('additional_info', String(500))  # Pour stocker des informations supplémentaires si nécessaire
        )

        # Créer la table dans la base de données
        metadata.create_all(engine)
        print("Table metrics_history créée avec succès!")
    except Exception as e:
        print(f"Erreur lors de la création de la table metrics_history: {str(e)}")

    print("Migration terminée !")

if __name__ == "__main__":
    migrate_data()