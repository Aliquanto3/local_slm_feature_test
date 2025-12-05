#!/usr/bin/env python3
"""
Script de téléchargement de modèles GGUF pour Wavestone Local AI Workbench.
Lit la configuration directement depuis models_config.py.
"""

import os
import argparse
import sys
from pathlib import Path
from huggingface_hub import hf_hub_download, HfApi
import logging

# ✅ IMPORT DE LA CONFIGURATION PYTHON
try:
    from config.models_config import MODELS_DB, DOWNLOAD_SETTINGS
except ImportError:
    print("❌ Erreur : Impossible d'importer 'models_config.py'. Vérifiez qu'il est dans le même dossier.")
    sys.exit(1)

# Configuration du logging avec des couleurs si possible, sinon simple
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

def check_model_availability(repo_id, filename):
    """Vérifie si le modèle existe sur HF sans le télécharger (Dry Run)"""
    api = HfApi()
    try:
        # Vérifie si le fichier existe dans le repo
        exists = api.file_exists(repo_id=repo_id, filename=filename)
        return exists
    except Exception as e:
        logger.error(f"    └── ⚠️ Erreur d'accès API: {e}")
        return False

def download_gguf_model(model_name, model_conf, local_dir, force=False, dry_run=False):
    """
    Gère la logique de téléchargement ou de vérification d'un modèle.
    """
    repo_id = model_conf.get('repo_id')
    filename = model_conf.get('filename')
    
    if not repo_id or not filename:
        logger.warning(f"⚠️ Configuration incomplète pour {model_name} (repo_id ou filename manquant)")
        return None
    
    target_path = os.path.join(local_dir, filename)
    
    logger.info(f"🤖 {model_name}")
    logger.info(f"    ├── Repo: {repo_id}")
    logger.info(f"    └── File: {filename}")

    # --- MODE DRY RUN (Test de connexion) ---
    if dry_run:
        logger.info("    ├── 🧪 Mode Test (Dry Run)...")
        is_available = check_model_availability(repo_id, filename)
        if is_available:
            logger.info("    └── ✅ DISPONIBLE (Connexion OK)")
            return "dry_run_ok"
        else:
            logger.error("    └── ❌ INACCESSIBLE (Vérifier nom ou token)")
            return None

    # --- MODE TÉLÉCHARGEMENT ---
    
    # 1. Vérification de l'existant
    if os.path.exists(target_path) and not force:
        file_size_mb = os.path.getsize(target_path) / (1024 * 1024)
        logger.info(f"    ├── ⏭️  DÉJÀ PRÉSENT ({file_size_mb:.1f} MB)")
        logger.info(f"    └── 📍 {target_path}")
        return target_path

    # 2. Téléchargement réel
    try:
        logger.info("    ├── 🚀 Démarrage du téléchargement...")
        
        file_path = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            local_dir=local_dir,
            local_dir_use_symlinks=False,
            resume_download=True
        )
        
        logger.info("    └── ✅ TÉLÉCHARGEMENT TERMINÉ")
        return file_path
        
    except Exception as e:
        logger.error(f"    └── ❌ ERREUR: {str(e)}")
        return None

def main():
    # Gestion des arguments en ligne de commande
    parser = argparse.ArgumentParser(description="Téléchargeur de modèles GGUF Wavestone Workbench")
    parser.add_argument("--dry-run", action="store_true", help="Vérifie uniquement l'accès aux fichiers sans télécharger")
    parser.add_argument("--force", action="store_true", help="Force le re-téléchargement même si le fichier existe")
    args = parser.parse_args()

    # 1. Charger les settings depuis la config Python
    local_dir = DOWNLOAD_SETTINGS.get('local_dir', './models_gguf')
    Path(local_dir).mkdir(parents=True, exist_ok=True)

    # 2. Convertir MODELS_DB (structure imbriquée) en une liste plate pour le téléchargement
    models_to_download = []
    
    for family, variants in MODELS_DB.items():
        for model_variant, config in variants.items():
            # On ne traite que les modèles de type "local"
            if config.get("type") == "local":
                # On injecte le nom du variant pour l'affichage
                # On crée une copie pour ne pas modifier le dictionnaire original en mémoire
                download_item = config.copy()
                download_item['name'] = f"{family} - {model_variant}"
                models_to_download.append(download_item)

    # Header
    mode_str = "🧪 MODE TEST (DRY RUN)" if args.dry_run else "⬇️  MODE TÉLÉCHARGEMENT"
    logger.info("=" * 60)
    logger.info(f"📦 WAVESTONE LOCAL AI WORKBENCH - MODEL DOWNLOADER")
    logger.info(f"{mode_str}")
    logger.info(f"📂 Destination: {local_dir}")
    logger.info(f"🔢 Modèles locaux identifiés: {len(models_to_download)}")
    logger.info("=" * 60 + "\n")

    success_count = 0
    
    if not models_to_download:
        logger.warning("⚠️ Aucun modèle local trouvé dans models_config.py.")
        return

    for i, model_conf in enumerate(models_to_download, 1):
        logger.info(f"[{i}/{len(models_to_download)}]")
        result = download_gguf_model(
            model_name=model_conf['name'], 
            model_conf=model_conf, 
            local_dir=local_dir, 
            force=args.force, 
            dry_run=args.dry_run
        )
        
        if result:
            success_count += 1
        logger.info("-" * 60)

    # Résumé
    logger.info("\n" + "=" * 60)
    if args.dry_run:
        logger.info(f"📋 RÉSULTAT DU TEST: {success_count}/{len(models_to_download)} modèles accessibles")
    else:
        logger.info(f"📋 RÉSULTAT FINAL: {success_count}/{len(models_to_download)} modèles prêts")
        if success_count == len(models_to_download):
            logger.info("\n🎉 Tout est prêt ! Vous pouvez lancer: streamlit run app.py")
    logger.info("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n🛑 Interrompu par l'utilisateur")