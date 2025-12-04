import os
import sys

# Installation auto des dépendances si manquantes
try:
    from huggingface_hub import hf_hub_download
except ImportError:
    print("📦 Installation de huggingface_hub...")
    os.system(f"{sys.executable} -m pip install huggingface_hub")
    from huggingface_hub import hf_hub_download

# --- CONFIGURATION ---
MODEL_DIR = "." 

MODELS_TO_DOWNLOAD = {
    # --- GRANITE (IBM) ---
    "granite-4.0-1b-Q4_K_M.gguf": {
        "repo_id": "bartowski/granite-3.0-1b-instruct-GGUF",
        "filename": "granite-3.0-1b-instruct-Q4_K_M.gguf"
    },
    "granite-4.0-350m-Q4_K_M.gguf": {
        "repo_id": "bartowski/granite-3.0-2b-instruct-GGUF", 
        "filename": "granite-3.0-2b-instruct-Q4_K_M.gguf" 
    },

    # --- LLAMA (META) ---
    "Llama-3.3-1B-Instruct-Q4_K_M.gguf": {
        "repo_id": "bartowski/Llama-3.2-1B-Instruct-GGUF",
        "filename": "Llama-3.2-1B-Instruct-Q4_K_M.gguf"
    },

    # --- QWEN (ALIBABA) ---
    "qwen2.5-3b-instruct-q4_k_m.gguf": {
        "repo_id": "Qwen/Qwen2.5-3B-Instruct-GGUF",
        "filename": "qwen2.5-3b-instruct-q4_k_m.gguf"
    },

    # --- MINISTRAL (MISTRAL AI) - CORRIGÉ via Unsloth ---
    # Nous utilisons Unsloth qui a des noms de fichiers plus propres
    "Ministral-3-3B-Instruct-2512-Q4_K_M.gguf": {
        "repo_id": "unsloth/Ministral-3-3B-Instruct-2512-GGUF", 
        "filename": "Ministral-3-3B-Instruct-2512-Q4_K_M.gguf"
    },
    "Ministral-3-3B-Reasoning-2512-Q4_K_M.gguf": {
        "repo_id": "unsloth/Ministral-3-3B-Reasoning-2512-GGUF", 
        "filename": "Ministral-3-3B-Reasoning-2512-Q4_K_M.gguf" 
    }
}

def setup():
    print(f"🚀 Démarrage de la vérification dans : {os.path.abspath(MODEL_DIR)}\n")
    
    for local_name, info in MODELS_TO_DOWNLOAD.items():
        local_path = os.path.join(MODEL_DIR, local_name)
        
        if os.path.exists(local_path):
            print(f"✅ [OK] {local_name}")
        else:
            print(f"⬇️ [Téléchargement] {local_name}...")
            print(f"   Source : {info['repo_id']} / {info['filename']}")
            
            try:
                hf_hub_download(
                    repo_id=info['repo_id'],
                    filename=info['filename'],
                    local_dir=MODEL_DIR,
                    local_dir_use_symlinks=False
                )
                
                # Renommage explicite si le fichier téléchargé n'a pas le nom local voulu
                original_path = os.path.join(MODEL_DIR, info['filename'])
                if original_path != local_path and os.path.exists(original_path):
                    os.rename(original_path, local_path)
                
                print(f"✨ Succès : {local_name}")
                
            except Exception as e:
                print(f"❌ Échec sur {local_name}")
                print(f"   Erreur : {e}")
                if "401" in str(e) or "403" in str(e):
                    print("   💡 IMPORTANT : Ce modèle nécessite une authentification.")
                    print("      1. Acceptez la licence ici : https://huggingface.co/mistralai/Ministral-3-3B-Instruct-2512")
                    print("      2. Lancez 'huggingface-cli login' dans votre terminal.")

    print("\n🏁 Opération terminée.")

if __name__ == "__main__":
    setup()