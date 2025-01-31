"""
Ce script Python combine deux fonctionnalités :
1. Transformation des fichiers Excel avec des colonnes journalières (J1-J31) en format ligne par date
2. Concaténation des fichiers transformés en fichiers CSV par année et un fichier global
"""

import pandas as pd
from datetime import datetime, timedelta
import calendar
import os
import logging

def setup_logging(log_file="Logs/execution_logs.log"):
    """Configure le système de logging."""
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    log_format = "%(asctime)s | %(levelname)s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8', mode='a'),
            logging.StreamHandler()
        ]
    )
    
    logging.info("="*50)
    logging.info("🚀 Début du traitement complet")

def create_directory_if_not_exists(directory):
    """Crée un dossier s'il n'existe pas."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        logging.info(f"📁 Dossier créé : {directory}")

def transform_excel_file(input_file, output_file, month_number):
    """Transforme un fichier Excel du format colonnes vers le format lignes."""
    logging.info(f"📄 Début du traitement de {input_file}")
    data = pd.read_excel(input_file, header=1)
    
    year = int(output_file.split(os.sep)[-2])
    num_days = calendar.monthrange(year, month_number)[1]
    start_date = datetime(year, month_number, 1)
    
    date_columns = [(start_date + timedelta(days=i)).strftime("%d/%m/%Y") for i in range(num_days)]
    
    logging.info(f"📅 Nombre de jours dans le mois {month_number}: {num_days}")
    
    columns_to_keep = ['ETBDES', 'ARTDES'] + [f'J{i+1}' for i in range(num_days)]
    if 'PTLDES' in data.columns:
        columns_to_keep.insert(1, 'PTLDES')
        
    data = data[columns_to_keep]
    
    new_columns = []
    for col in data.columns:
        if col.startswith("J"):
            day_num = int(col[1:])
            if 1 <= day_num <= num_days:
                new_columns.append(date_columns[day_num - 1])
            else:
                logging.warning(f"⚠️ Colonne ignorée: {col} (le mois n'a que {num_days} jours)")
        else:
            new_columns.append(col)
    
    data.columns = new_columns
    
    new_rows = []
    for idx, row in data.iterrows():
        etbdes = row['ETBDES']
        artdes = row['ARTDES']
        
        for col in data.columns:
            if len(col.split('/')) == 3:
                quantite = row[col]
                if pd.notna(quantite) and quantite != 0:
                    new_rows.append({
                        'ETBDES': etbdes,
                        'ARTDES': artdes,
                        'DATE': datetime.strptime(col, '%d/%m/%Y').strftime('%Y-%m-%d'),
                        'QUANTITE': quantite
                    })
    
    if not new_rows:
        logging.warning(f"⚠️ Attention : Aucune donnée valide trouvée dans {input_file}")
        return
        
    new_df = pd.DataFrame(new_rows)
    new_df = new_df.sort_values(['ETBDES', 'ARTDES', 'DATE'])
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    new_df.to_excel(output_file, index=False)
    logging.info(f"✅ Fichier {output_file} créé avec succès")

def process_year_directory(year_dir, output_base_dir):
    """Traite tous les fichiers d'une année."""
    month_map = {
        '1-janvier': 1, '2-fevrier': 2, '3-mars': 3, '4-avril': 4, '5-mai': 5, '6-juin': 6,
        '7-juillet': 7, '8-aout': 8, '9-septembre': 9, '10-octobre': 10, '11-novembre': 11, '12-decembre': 12
    }
    
    year = os.path.basename(year_dir)
    output_year_dir = os.path.join(output_base_dir, year)
    create_directory_if_not_exists(output_year_dir)
    
    files = [f for f in os.listdir(year_dir) if f.endswith('.xlsx') and not f.endswith('-final.xlsx') 
             and not f == f'{year}.xlsx' and not f.startswith('global')]
    
    for file in sorted(files):
        file_prefix = file.split(year + '.xlsx')[0]
        month_number = month_map.get(file_prefix)
        
        if month_number:
            input_file = os.path.join(year_dir, file)
            output_file = os.path.join(output_year_dir, file.replace('.xlsx', '-final.xlsx'))
            logging.info(f"🔄 Traitement de {file}...")
            try:
                transform_excel_file(input_file, output_file, month_number)
            except Exception as e:
                logging.error(f"❌ Erreur lors du traitement de {file}: {str(e)}")
        else:
            logging.warning(f"⚠️ Format de nom de fichier non reconnu pour {file}")

def concatener_fichiers_annee(dossier_annee, annee):
    """Concatène tous les fichiers transformés d'une année en un seul CSV."""
    logging.info(f"📅 Concaténation des fichiers de l'année {annee}")
    
    all_dfs = []
    fichiers_traites = 0
    fichiers_erreur = 0
    
    # Modification ici : on ne prend que les fichiers qui se terminent par '-final.xlsx'
    fichiers = [f for f in os.listdir(dossier_annee) if f.endswith('-final.xlsx')]
    
    if not fichiers:
        logging.warning(f"⚠️ Aucun fichier '-final.xlsx' trouvé dans le dossier de l'année {annee}")
        return None
    
    for fichier in sorted(fichiers):
        try:
            chemin_complet = os.path.join(dossier_annee, fichier)
            df = pd.read_excel(chemin_complet)
            
            # Vérification des colonnes requises
            colonnes_requises = ['ETBDES', 'ARTDES', 'DATE', 'QUANTITE']
            if not all(col in df.columns for col in colonnes_requises):
                logging.error(f"❌ Colonnes manquantes dans {fichier}. Colonnes requises : {colonnes_requises}")
                fichiers_erreur += 1
                continue
            
            all_dfs.append(df)
            fichiers_traites += 1
            logging.info(f"✅ Fichier {fichier} lu avec succès ({len(df)} lignes)")
        except Exception as e:
            logging.error(f"❌ Erreur lors de la lecture de {fichier}: {str(e)}")
            fichiers_erreur += 1
    
    if not all_dfs:
        logging.error(f"❌ Aucun fichier valide traité pour l'année {annee}")
        return None
    
    df_final = pd.concat(all_dfs, ignore_index=True)
    df_final = df_final.sort_values(['DATE', 'ETBDES', 'ARTDES'])
    
    nom_fichier_sortie = f"donnees_completes_{annee}.csv"
    df_final.to_csv(nom_fichier_sortie, index=False)
    
    logging.info(f"📊 Résumé {annee}:")
    logging.info(f"   - Fichiers traités avec succès: {fichiers_traites}")
    logging.info(f"   - Fichiers en erreur: {fichiers_erreur}")
    logging.info(f"   - Nombre total de lignes: {len(df_final)}")
    logging.info(f"   - Fichier de sortie: {nom_fichier_sortie}")
    
    return df_final

def main():
    """Fonction principale qui orchestre tout le processus."""
    setup_logging()
    
    # Configuration des chemins
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(script_dir, 'Logistique-old')
    output_dir = os.path.join(script_dir, 'Logistique-new')
    
    if not os.path.exists(input_dir):
        logging.error(f"❌ Erreur : Le dossier {input_dir} n'existe pas")
        return
    
    # 1. Transformation des fichiers
    create_directory_if_not_exists(output_dir)
    year_dirs = ['2022', '2023', '2024']
    
    logging.info("🔄 Phase 1: Transformation des fichiers")
    for year in year_dirs:
        year_dir = os.path.join(input_dir, year)
        if os.path.exists(year_dir):
            logging.info(f"📂 Traitement du dossier {year}...")
            process_year_directory(year_dir, output_dir)
    
    # 2. Concaténation des fichiers
    logging.info("🔄 Phase 2: Concaténation des fichiers")
    all_years_dfs = []
    
    for year in year_dirs:
        year_dir = os.path.join(output_dir, year)
        if os.path.exists(year_dir):
            df_year = concatener_fichiers_annee(year_dir, year)
            if df_year is not None:
                all_years_dfs.append(df_year)
    
    if all_years_dfs:
        df_final_global = pd.concat(all_years_dfs, ignore_index=True)
        df_final_global = df_final_global.sort_values(['DATE', 'ETBDES', 'ARTDES'])
        
        nom_fichier_global = f"donnees_completes_{min(year_dirs)}-{max(year_dirs)}.csv"
        df_final_global.to_csv(nom_fichier_global, index=False)
        logging.info(f"✨ Fichier final créé : {nom_fichier_global} ({len(df_final_global)} lignes)")
    
    logging.info("🎉 Traitement terminé avec succès!")

if __name__ == "__main__":
    main()