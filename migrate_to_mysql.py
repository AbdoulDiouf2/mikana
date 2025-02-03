import pandas as pd
import mysql.connector
from sqlalchemy import create_engine
import os

def migrate_data():
    # Configuration MySQL
    mysql_config = {
        'user': 'mikana_user',
        'password': 'mikana_password',
        'host': 'localhost',  # Changez à 'mysql' si vous utilisez Docker
        'database': 'mikana_db'
    }

    # Création de la connexion SQLAlchemy
    engine = create_engine(f"mysql+pymysql://{mysql_config['user']}:{mysql_config['password']}@{mysql_config['host']}/{mysql_config['database']}")

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

    print("Migration terminée !")

if __name__ == "__main__":
    migrate_data()