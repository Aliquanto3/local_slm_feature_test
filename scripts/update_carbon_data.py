"""
Script utilitaire pour mettre à jour les données d'intensité carbone.
Source : Our World in Data (OWID)
"""
import os
import requests
import pandas as pd

# URLs et Chemins
DATA_URL = "https://ourworldindata.org/grapher/carbon-intensity-electricity.csv?v=1&csvType=full&useColumnShortNames=true"
OUTPUT_DIR = os.path.join("data", "carbon-intensity-electricity")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "carbon-intensity-electricity.csv")

def update_data():
    print(f"🌍 Téléchargement des données depuis : {DATA_URL}")
    
    try:
        response = requests.get(DATA_URL)
        response.raise_for_status()
        
        # Création du dossier si inexistant
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # Sauvegarde brute
        with open(OUTPUT_FILE, "wb") as f:
            f.write(response.content)
            
        # Vérification rapide
        df = pd.read_csv(OUTPUT_FILE)
        print(f"✅ Succès ! Fichier sauvegardé : {OUTPUT_FILE}")
        print(f"📊 Lignes : {len(df)} | Pays uniques : {df['Entity'].nunique()}")
        print(f"📅 Plage années : {df['Year'].min()} - {df['Year'].max()}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour : {e}")

if __name__ == "__main__":
    update_data()