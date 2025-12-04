"""
Configuration centralisée des modèles pour Wavestone Local AI Workbench.
Fait le lien entre l'interface Streamlit et les fichiers GGUF téléchargés.
"""
import os

# Chemin vers le dossier des modèles (doit correspondre au script de download)
LOCAL_MODEL_DIR = "models_gguf"

MODELS_DB = {
    # -------------------------------------------------------------------------
    # 🌩️ API MISTRAL (Cloud) - Sélection Spécifique (Déc. 2025)
    # -------------------------------------------------------------------------
    "☁️ API - Mistral AI": {
        "Mistral Large 3": {
            "type": "api",
            "api_id": "mistral-large-latest", # v25.12
            "ctx": 128000, 
            "info": {
                "fam": "Mistral Large", "editor": "Mistral AI",
                "desc": "Modèle SOTA multimodal généraliste (Déc. 2025).",
                "params_tot": 123, "params_act": 123, "disk": 0,
                "link": "https://docs.mistral.ai/models/mistral-large-3"
            }
        },
        "Mistral Small 3.2": {
            "type": "api",
            "api_id": "mistral-small-latest", # v25.06
            "ctx": 128000,
            "info": {
                "fam": "Mistral Small", "editor": "Mistral AI",
                "desc": "Modèle efficient (24B) optimisé pour la latence et le coût.",
                "params_tot": 24, "params_act": 24, "disk": 0,
                "link": "https://docs.mistral.ai/models/mistral-small-3-2"
            }
        },
        "Magistral Small 1.2": {
            "type": "api",
            "api_id": "magistral-small-latest", # v25.09
            "ctx": 32000,
            "info": {
                "fam": "Magistral", "editor": "Mistral AI",
                "desc": "Modèle de 'Reasoning' (System 2). Utilise des tags <think> pour réfléchir avant de répondre.",
                "params_tot": 24, "params_act": 24, "disk": 0,
                "link": "https://docs.mistral.ai/models/magistral-small-1-2"
            }
        },
        "Ministral 3 14B": {
            "type": "api",
            "api_id": "ministral-14b-latest", # v25.12
            "ctx": 256000,
            "info": {
                "fam": "Ministral 3", "editor": "Mistral AI",
                "desc": "Le plus puissant de la gamme Edge. Multimodal & Contexte long (256k).",
                "params_tot": 14, "params_act": 14, "disk": 0,
                "link": "https://docs.mistral.ai/models/ministral-3-14b"
            }
        },
        "Ministral 3 8B": {
            "type": "api",
            "api_id": "ministral-8b-latest",
            "ctx": 128000,
            "info": {
                "fam": "Ministral 3", "editor": "Mistral AI",
                "desc": "Intermédiaire Edge puissant. Excellent rapport qualité/vitesse.",
                "params_tot": 8, "params_act": 8, "disk": 0,
                "link": "https://mistral.ai/news/ministral-3b/"
            }
        },
        "Ministral 3 3B": {
            "type": "api",
            "api_id": "ministral-3b-latest",
            "ctx": 128000,
            "info": {
                "fam": "Ministral 3", "editor": "Mistral AI",
                "desc": "Modèle ultra-compact pour l'embarqué. Très rapide.",
                "params_tot": 3, "params_act": 3, "disk": 0,
                "link": "https://mistral.ai/news/ministral-3b/"
            }
        }
    },

    # -------------------------------------------------------------------------
    # 🏠 LOCAUX (CPU / GGUF)
    # -------------------------------------------------------------------------
    "🏠 Local - Meta Llama": {
        "Llama 3.2 1B Instruct": {
            "type": "local",
            "file": os.path.join(LOCAL_MODEL_DIR, "Llama-3.2-1B-Instruct-Q4_K_M.gguf"),
            "ctx": 8192,
            "info": {
                "fam": "Llama 3.2", "editor": "Meta",
                "desc": "Très léger, optimisé pour l'instruction simple et le résumé rapide.",
                "params_tot": 1.2, "params_act": 1.2, "disk": 0.8,
                "link": "https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct"
            }
        },
        "Llama 3.2 3B Instruct": {
            "type": "local",
            "file": os.path.join(LOCAL_MODEL_DIR, "Llama-3.2-3B-Instruct-Q4_K_M.gguf"),
            "ctx": 8192,
            "info": {
                "fam": "Llama 3.2", "editor": "Meta",
                "desc": "Excellent équilibre performance/taille. Bon en nuance.",
                "params_tot": 3.2, "params_act": 3.2, "disk": 2.0,
                "link": "https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct"
            }
        }
    },
    
    "🏠 Local - Qwen & Alibaba": {
        "Qwen 2.5 1.5B Instruct": {
            "type": "local",
            "file": os.path.join(LOCAL_MODEL_DIR, "qwen2.5-1.5b-instruct-q4_k_m.gguf"),
            "ctx": 8192,
            "info": {
                "fam": "Qwen 2.5", "editor": "Alibaba Cloud",
                "desc": "Modèle très performant en code et mathématiques pour sa taille.",
                "params_tot": 1.5, "params_act": 1.5, "disk": 1.0,
                "link": "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct"
            }
        },
        "Qwen 2.5 3B Instruct": {
            "type": "local",
            "file": os.path.join(LOCAL_MODEL_DIR, "qwen2.5-3b-instruct-q4_k_m.gguf"),
            "ctx": 8192,
            "info": {
                "fam": "Qwen 2.5", "editor": "Alibaba Cloud",
                "desc": "Concurrent direct de Llama 3.2 3B, souvent meilleur en code/logique.",
                "params_tot": 3.0, "params_act": 3.0, "disk": 2.0,
                "link": "https://huggingface.co/Qwen/Qwen2.5-3B-Instruct"
            }
        }
    },

    "🏠 Local - Microsoft & Google": {
        "Phi-3.5 Mini Instruct": {
            "type": "local",
            "file": os.path.join(LOCAL_MODEL_DIR, "Phi-3.5-mini-instruct-Q4_K_M.gguf"),
            "ctx": 4096,
            "info": {
                "fam": "Phi-3.5", "editor": "Microsoft",
                "desc": "Très dense en connaissances. Excellent raisonnement pour 3.8B.",
                "params_tot": 3.8, "params_act": 3.8, "disk": 2.4,
                "link": "https://huggingface.co/microsoft/Phi-3.5-mini-instruct"
            }
        },
        "Gemma 2 2B Instruct": {
            "type": "local",
            "file": os.path.join(LOCAL_MODEL_DIR, "gemma-2-2b-it-Q4_K_M.gguf"),
            "ctx": 4096,
            "info": {
                "fam": "Gemma 2", "editor": "Google",
                "desc": "Modèle ouvert de Google. Très bonnes capacités littéraires.",
                "params_tot": 2.6, "params_act": 2.6, "disk": 1.5,
                "link": "https://huggingface.co/google/gemma-2-2b-it"
            }
        },
         "SmolLM2 1.7B": {
            "type": "local",
            "file": os.path.join(LOCAL_MODEL_DIR, "SmolLM2-1.7B-Instruct-Q4_K_M.gguf"),
            "ctx": 2048,
            "info": {
                "fam": "SmolLM2", "editor": "HuggingFace",
                "desc": "Micro-modèle extrêmement rapide. Idéal pour classification simple.",
                "params_tot": 1.7, "params_act": 1.7, "disk": 1.1,
                "link": "https://huggingface.co/HuggingFaceTB/SmolLM2-1.7B-Instruct"
            }
        }
    }
}