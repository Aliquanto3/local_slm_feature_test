from llama_cpp import Llama
import os
import traceback

# ⚠️ On pointe spécifiquement sur le fichier qui pose problème
model_path = "models_gguf/Ministral-3-3B-Instruct-2512-Q4_K_M.gguf"

print(f"🔍 Test du chemin : {os.path.abspath(model_path)}")

if not os.path.exists(model_path):
    print("❌ Le fichier n'existe pas !")
else:
    size_mb = os.path.getsize(model_path) / (1024 * 1024)
    print(f"📦 Fichier trouvé ({size_mb:.1f} MB).")
    
    # Vérification corruption (taille trop petite)
    if size_mb < 100:
        print("⚠️ ALERTE : Le fichier semble beaucoup trop petit (téléchargement échoué ?).")
    
    print("Tentative de chargement...")
    try:
        llm = Llama(model_path=model_path, verbose=True)
        print("✅ SUCCÈS : Le modèle fonctionne !")
    except Exception:
        print("\n🚨 ERREUR DÉTAILLÉE :")
        traceback.print_exc()