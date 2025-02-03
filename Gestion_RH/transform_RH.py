import pandas as pd

# Configuration des chemins
input_files = {
    2022: 'PRESENCE_2022.xlsx',
    2023: 'PRESENCE_2023.xlsx',
    2024: 'PRESENCE_2024.xlsx'
}
output_files = {
    2022: 'Total_Presents_2022.xlsx',
    2023: 'Total_Presents_2023.xlsx',
    2024: 'Total_Presents_2024.xlsx'
}
final_output_file = 'Total_Presents_Final.xlsx'

# Fonction pour traiter un fichier donné et générer un fichier avec une colonne "Année"
def process_file(file_path, year, output_path):
    print(f"\n=== Traitement du fichier {file_path} pour l'année {year} ===")
    print("Lecture du fichier Excel...")
    excel_data = pd.ExcelFile(file_path)
    week_sheets = sorted([sheet for sheet in excel_data.sheet_names if sheet.startswith('S')])
    print(f"Nombre de feuilles hebdomadaires trouvées : {len(week_sheets)}")
    
    results = []
    for sheet in week_sheets:
        print(f"\nAnalyse de la feuille : {sheet}")
        data = pd.read_excel(file_path, sheet_name=sheet, header=None)
        row_index = data.apply(lambda row: row.astype(str).str.contains("Total présents", case=False, na=False).any(), axis=1)
        row_indices = row_index[row_index].index.tolist()
        
        if row_indices:
            target_row = data.iloc[row_indices[0]]
            row_sum = pd.to_numeric(target_row, errors='coerce').sum()
            
            # Soustraire 14 pour les années 2022 et 2023
            if year in [2022, 2023]:
                print(f"Ajustement du total pour {year} : soustraction de 14")
                row_sum = max(0, row_sum - 14)  # Assure que le total reste positif
            
            print(f"Total des présences pour {sheet} : {row_sum}")
            results.append({'Annee': year, 'Semaines': sheet, 'Presences': row_sum})
        else:
            print(f"Aucun total trouvé pour {sheet}, enregistrement de 0")
            results.append({'Annee': year, 'Semaines': sheet, 'Presences': 0})
    
    results_df = pd.DataFrame(results)
    results_df.to_excel(output_path, index=False)
    print(f"\nFichier de sortie créé : {output_path}")

# Traitement des fichiers (2022, 2023, 2024)
print("\n=== Début du traitement des fichiers ===")
for year, input_file in input_files.items():
    print(f"\nTraitement de l'année {year}")
    process_file(input_file, year, output_files[year])

# Fusionner les fichiers en un seul fichier final
print("\n=== Fusion des fichiers en un fichier final ===")
final_results = []
for year, output_file in output_files.items():
    print(f"Lecture du fichier {output_file}")
    year_df = pd.read_excel(output_file)
    final_results.append(year_df)

# Consolider toutes les données en une seule DataFrame
final_df = pd.concat(final_results, ignore_index=True)
final_df.to_excel(final_output_file, index=False)

print("✅ Transformation des fichiers terminée. Fichier final généré :", final_output_file)