import pandas as pd
import os

# Liste des fichiers à concaténer
fichiers = ["2021.xlsx", "2022.xlsx", "2023.xlsx", "2024.xlsx"]

# Colonnes à conserver
colonnes_a_conserver = ["Date expédition", "Désignation article", "Poids", "Qté cdée", "Qté livrée", "Poids total"]

# Initialisation d'une liste pour stocker les DataFrames
dfs = []

# Chemin du dossier contenant les fichiers (adaptez si nécessaire)
dossier = "./Data/"

# Boucle sur les fichiers pour les lire et les concaténer
for idx, fichier in enumerate(fichiers):
    chemin_fichier = os.path.join(dossier, fichier)

    # Lecture du fichier en sautant la première ligne (l'entête est sur la 2e ligne)
    df = pd.read_excel(chemin_fichier, skiprows=1)

    # Conserver uniquement les colonnes souhaitées
    df = df[colonnes_a_conserver]

    dfs.append(df)

# Concaténation des DataFrames
resultat_final = pd.concat(dfs, ignore_index=True)

# Exportation vers un nouveau fichier Excel
resultat_final.to_excel("./Data/donnees_finales.xlsx", index=False)

print("La concaténation est terminée ! Le fichier final est 'donnees_finales.xlsx'.")
