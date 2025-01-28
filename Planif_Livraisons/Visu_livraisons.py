import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64

class DeliveryVisualizer:
    def __init__(self, excel_file_path):
        """Initialise le visualiseur avec le chemin du fichier Excel."""
        self.df = pd.read_excel(excel_file_path)
        self.df['Date expédition'] = pd.to_datetime(self.df['Date expédition'])
        self.df['Année'] = self.df['Date expédition'].dt.year
        self.df['Mois'] = self.df['Date expédition'].dt.month

    def _fig_to_base64(self, fig):
        """Convertit une figure matplotlib en string base64."""
        buf = BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode()
        buf.close()
        plt.close(fig)
        return img_str

    def yearly_delivery_trend(self):
        """Génère le graphique de tendance annuelle des livraisons."""
        df_filtered = self.df[self.df['Année'].isin([2022, 2023, 2024])]
        quantite_livree_par_annee = df_filtered.groupby('Année')['Qté livrée'].sum().reset_index()
        
        fig = plt.figure(figsize=(10, 6))
        plt.plot(quantite_livree_par_annee['Année'], 
                quantite_livree_par_annee['Qté livrée'], 
                marker='o', color='b', linestyle='-', markersize=6)
        
        plt.title('Quantité totale livrée par année (2022-2024)')
        plt.xlabel('Année')
        plt.ylabel('Quantité livrée')
        plt.xticks([2022, 2023, 2024])
        plt.grid(True)
        plt.tight_layout()
        
        return self._fig_to_base64(fig)

    def monthly_delivery_comparison(self):
        """Génère l'histogramme mensuel comparatif des livraisons."""
        df_filtered = self.df[self.df['Année'].isin([2022, 2023, 2024])]
        quantite_livree_par_annee_mois = df_filtered.groupby(['Mois', 'Année'])['Qté livrée'].sum().unstack(fill_value=0)
        
        fig = plt.figure(figsize=(12, 6))
        quantite_livree_par_annee_mois.plot(kind='bar', width=0.8, ax=plt.gca())
        
        plt.title('Quantité livrée par mois et année')
        plt.xlabel('Mois')
        plt.ylabel('Quantité livrée')
        plt.xticks(range(12), ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 
                              'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc'], 
                  rotation=45)
        plt.legend(title="Année", bbox_to_anchor=(1.05, 1))
        plt.grid(True)
        plt.tight_layout()
        
        return self._fig_to_base64(fig)

    def article_distribution_pie(self):
        """Génère le graphique en secteurs de la distribution des articles."""
        quantite_livree_par_article = self.df.groupby('Désignation article')['Qté livrée'].sum()
        seuil = quantite_livree_par_article.sum() * 0.05
        
        importants = quantite_livree_par_article[quantite_livree_par_article >= seuil]
        autres = pd.Series({'Autres': quantite_livree_par_article[quantite_livree_par_article < seuil].sum()})
        quantite_livree_par_article = pd.concat([importants, autres])
        
        fig = plt.figure(figsize=(10, 10))
        colors = plt.cm.Paired(np.linspace(0, 1, len(quantite_livree_par_article)))
        plt.pie(quantite_livree_par_article, labels=quantite_livree_par_article.index, 
               autopct='%1.1f%%', startangle=90, colors=colors)
        
        plt.title('Quantité livrée par désignation d\'article')
        plt.legend(quantite_livree_par_article.index, 
                  title="Articles", 
                  loc='center left', 
                  bbox_to_anchor=(1, 0, 0.5, 1))
        plt.tight_layout()
        
        return self._fig_to_base64(fig)

    def order_delivery_comparison(self):
        """Génère le graphique en anneau comparant commandes et livraisons."""
        quantite_totale_par_annee = self.df.groupby('Année').agg({
            'Qté cdée': 'sum',
            'Qté livrée': 'sum'
        })
        
        fig = plt.figure(figsize=(10, 10))
        colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0', '#ffb3e6']
        
        labels = []
        sizes = []
        colors_for_pie = []
        
        for year in quantite_totale_par_annee.index:
            commande = quantite_totale_par_annee.loc[year, 'Qté cdée']
            livree = quantite_totale_par_annee.loc[year, 'Qté livrée']
            
            sizes.extend([commande, livree])
            labels.extend([f"{year} Commandée", f"{year} Livrée"])
            colors_for_pie.extend([colors[2 * (year - 2022)], 
                                 colors[2 * (year - 2022) + 1]])
        
        plt.pie(sizes, labels=labels, autopct='%1.2f%%', startangle=90,
                colors=colors_for_pie, 
                wedgeprops={'width': 0.4, 'edgecolor': 'black'})
        
        plt.title('Quantités commandées et livrées par année')
        plt.legend(title="Année et Catégorie", 
                  loc="center left", 
                  bbox_to_anchor=(1, 0, 0.5, 1))
        plt.tight_layout()
        
        return self._fig_to_base64(fig)