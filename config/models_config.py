"""
Configuration centralisée (Unique Source of Truth) pour Wavestone Local AI Workbench.
Utilisé par :
1. app.py (pour l'affichage et le chargement)
2. download_gguf_models.py (pour le téléchargement)
"""
import os

# Paramètres globaux
LOCAL_MODEL_DIR = "models_gguf"

# Configuration du téléchargement
DOWNLOAD_SETTINGS = {
    "local_dir": LOCAL_MODEL_DIR,
    "resume_download": True,
    "max_workers": 2
}

# =========================================================================
# 🧩 Taxonomie des rôles (role_pref)
# -------------------------------------------------------------------------
# Chaque modèle peut déclarer un ou plusieurs rôles préférés dans info["role_pref"].
#
# - "assistant_generalist"   : Assistant de chat polyvalent (génération, Q&A, résumé…)
# - "assistant_light"        : Assistant léger / réactif pour ressources limitées (CPU, petite RAM)
# - "rag"                    : Bon candidat pour du RAG (surtout si long contexte)
# - "code"                   : Bon en programmation (explications, génération, debug)
# - "reasoning"              : Raisonnement avancé / logique, chaînes d’explication
# - "math_stem"              : Mathématiques, physique, problèmes quantitatifs / STEM
# - "tool_calling"           : Spécialisé ou très à l’aise en function calling / orchestration d’outils
# - "routing_classification" : Classification, détection d’intention, filtrage, routage de requêtes
# - "edge_on_device"         : Pensé pour tourn­er on-device / edge / CPU faible
# - "enterprise"             : Particulièrement adapté aux cas d’usage entreprise, conformité, gouvernance
# - "educational_tutor"      : Tutorat, pédagogie, explications pas-à-pas
#
# Exemple d’accès :
#   info = MODELS_DB["🏠 Alibaba"]["Qwen 2.5 1.5B Instruct"]["info"]
#   roles = info.get("role_pref", [])
# =========================================================================

MODELS_DB = {
    # =========================================================================
    # 🏠 ALIBABA (Qwen)
    # =========================================================================
    "🏠 Alibaba - Qwen": {
        "Qwen 2.5 0.5B Instruct": {
            "type": "local",
            "repo_id": "Qwen/Qwen2.5-0.5B-Instruct-GGUF",
            "filename": "qwen2.5-0.5b-instruct-q4_k_m.gguf",
            "file": os.path.join(LOCAL_MODEL_DIR, "qwen2.5-0.5b-instruct-q4_k_m.gguf"),
            "ctx": 32768,
            "info": {
                "fam": "Qwen 2.5", "editor": "Alibaba",
                "desc": (
                    "Version 'nano' de Qwen 2.5. Modèle dense d’environ 0,5B paramètres, "
                    "incroyablement léger, surprenant pour des tâches simples de "
                    "classification, routage, extraction de mots-clés ou chat basique "
                    "sur CPU modeste."
                ),
                "params_tot": 0.5, "params_act": 0.5,
                "disk": 0.40, "ram": 1.5,
                "langs": ["en", "zh", "fr", "de", "es", "it", "pt", "ja", "ko", "ar", "ru"],
                "role_pref": ["assistant_light", "routing_classification", "edge_on_device"],
                "link": "https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF"
            }
        },
        "Qwen 2.5 1.5B Instruct": {
            "type": "local",
            "repo_id": "Qwen/Qwen2.5-1.5B-Instruct-GGUF",
            "filename": "qwen2.5-1.5b-instruct-q4_k_m.gguf",
            "file": os.path.join(LOCAL_MODEL_DIR, "qwen2.5-1.5b-instruct-q4_k_m.gguf"),
            "ctx": 32768,
            "info": {
                "fam": "Qwen 2.5", "editor": "Alibaba",
                "desc": (
                    "Petit modèle dense (≈1,5B) très performant en multilingue, extraction, "
                    "résumé, recherche documentaire et code. Contexte 32K. Idéal pour des "
                    "assistants légers, du RAG court, des workflows métier automatisés ou "
                    "comme modèle par défaut sur CPU ou GPU modeste."
                ),
                "params_tot": 1.54, "params_act": 1.54,
                "disk": 1.12, "ram": 4.0,
                "langs": ["en", "zh", "fr", "de", "es", "it", "pt", "ja", "ko", "ar", "ru"],
                "role_pref": ["assistant_generalist", "rag", "code", "edge_on_device"],
                "link": "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF"
            }
        },
        "Qwen 2.5 3B Instruct": {
            "type": "local",
            "repo_id": "Qwen/Qwen2.5-3B-Instruct-GGUF",
            "filename": "qwen2.5-3b-instruct-q4_k_m.gguf",
            "file": os.path.join(LOCAL_MODEL_DIR, "qwen2.5-3b-instruct-q4_k_m.gguf"),
            "ctx": 32768,
            "info": {
                "fam": "Qwen 2.5", "editor": "Alibaba",
                "desc": (
                    "Modèle dense 3B multilingue long contexte (32K), très performant en "
                    "génération structurée, code, analyse logique et scénarios agentiques. "
                    "Excellent candidat comme SLM principal pour un assistant local "
                    "polyvalent sur CPU puissant ou GPU."
                ),
                "params_tot": 3.09, "params_act": 3.09,
                "disk": 1.93, "ram": 7.0,
                "langs": ["en", "zh", "fr", "de", "es", "it", "pt", "ja", "ko", "ar", "ru"],
                "role_pref": ["assistant_generalist", "rag", "code", "reasoning"],
                "link": "https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF"
            }
        }
    },

    # =========================================================================
    # 🏠 GOOGLE
    # =========================================================================
    "🏠 Google - Gemma": {
        "Gemma 2 2B IT": {
            "type": "local",
            "repo_id": "bartowski/gemma-2-2b-it-GGUF",
            "filename": "gemma-2-2b-it-Q4_K_M.gguf",
            "file": os.path.join(LOCAL_MODEL_DIR, "gemma-2-2b-it-Q4_K_M.gguf"),
            "ctx": 8192,
            "info": {
                "fam": "Gemma 2", "editor": "Google",
                "desc": (
                    "Modèle 2B open-weight de Google (famille Gemma / Gemini), très bon en "
                    "rédaction, Q&A, code et raisonnement léger, avec un contexte 8K. "
                    "Fiable et plutôt sécurisé, adapté aux assistants texte généraux, à la "
                    "documentation technique et au prototypage d’agents."
                ),
                "params_tot": 2.0, "params_act": 2.0,
                "disk": 1.71, "ram": 5.0,
                "langs": ["en", "fr", "de", "es", "it", "pt"],
                "role_pref": ["assistant_generalist", "code"],
                "link": "https://huggingface.co/google/gemma-2-2b-it"
            }
        }
    },

    # =========================================================================
    # 🏠 HUGGING FACE
    # =========================================================================
    "🏠 Hugging Face - SmolLM": {
        "SmolLM2 1.7B Instruct": {
            "type": "local",
            "repo_id": "bartowski/SmolLM2-1.7B-Instruct-GGUF",
            "filename": "SmolLM2-1.7B-Instruct-Q4_K_M.gguf",
            "file": os.path.join(LOCAL_MODEL_DIR, "SmolLM2-1.7B-Instruct-Q4_K_M.gguf"),
            "ctx": 2048,
            "info": {
                "fam": "SmolLM2", "editor": "HuggingFace",
                "desc": (
                    "Modèle compact 1.7B conçu pour tourner on-device (contexte 2K). "
                    "Bon en chat simple, réécriture, résumé, extraction et classification. "
                    "Idéal pour agents embarqués, micro-services NLP et pipelines légers "
                    "où la latence prime sur la profondeur de raisonnement."
                ),
                "params_tot": 1.7, "params_act": 1.7,
                "disk": 1.06, "ram": 4.0,
                "langs": ["en", "fr", "de", "es", "it", "pt"],
                "role_pref": ["assistant_light", "routing_classification", "edge_on_device"],
                "link": "https://huggingface.co/HuggingFaceTB/SmolLM2-1.7B-Instruct"
            }
        }
    },

    # =========================================================================
    # 🏠 IBM GRANITE
    # =========================================================================
    "🏠 IBM - Granite": {
        "Granite 3.0 3B Instruct": {
            "type": "local",
            "repo_id": "bartowski/granite-3.0-3b-a800m-instruct-GGUF",
            "filename": "granite-3.0-3b-a800m-instruct-Q4_K_M.gguf",
            "file": os.path.join(LOCAL_MODEL_DIR, "granite-3.0-3b-a800m-instruct-Q4_K_M.gguf"),
            "ctx": 4096,
            "info": {
                "fam": "Granite 3.0", "editor": "IBM",
                "desc": (
                    "Modèle MoE 3.3B (~800M paramètres actifs) orienté entreprise. "
                    "Multilingue, bon en résumé, classification, extraction, Q&A et code. "
                    "Très adapté aux cas d’usage d’entreprise sérieux (cybersécurité, "
                    "conformité, analyse documentaire) où la stabilité, la gouvernance "
                    "et la traçabilité sont prioritaires."
                ),
                "params_tot": 3.3, "params_act": 0.8,
                "disk": 2.06, "ram": 6.0,
                "langs": ["en", "fr", "de", "es", "it", "pt"],
                "role_pref": ["assistant_generalist", "enterprise", "rag", "routing_classification"],
                "link": "https://huggingface.co/ibm-granite/granite-3.0-3b-a800m-instruct"
            }
        },
        "Granite 3.1 2B Instruct": {
            "type": "local",
            "repo_id": "bartowski/granite-3.1-2b-instruct-GGUF",
            "filename": "granite-3.1-2b-instruct-Q4_K_M.gguf",
            "ctx": 131072,
            "info": {
                "fam": "Granite 3.1", "editor": "IBM",
                "desc": (
                    "Granite 3.1 2B dense avec contexte étendu à 128K. Meilleures "
                    "performances en instruction-following et RAG longue portée que la "
                    "v3.0. Intéressant pour analyser de longs rapports, procès-verbaux ou "
                    "dossiers de conformité sur une seule requête."
                ),
                "params_tot": 2.5, "params_act": 2.5,
                "disk": 1.55, "ram": 5.0,
                "langs": ["en", "fr", "de", "es", "it", "pt"],
                "role_pref": ["assistant_generalist", "rag", "enterprise"],
                "link": "https://huggingface.co/ibm-granite/granite-3.1-2b-instruct"
            }
        },
        "Granite 4.0 1B": {
            "type": "local",
            "repo_id": "ibm-granite/granite-4.0-1b-GGUF",
            "filename": "granite-4.0-1b-Q4_K_M.gguf",
            "file": os.path.join(LOCAL_MODEL_DIR, "granite-4.0-1b-Q4_K_M.gguf"),
            "ctx": 4096,
            "info": {
                "fam": "Granite 4.0", "editor": "IBM",
                "desc": (
                    "Modèle 'nano' 1B dense/hybride, pensé pour le edge/on-device. "
                    "Idéal pour des tâches légères : agents simples, extraction, "
                    "classification, filtrage et routage, automatisations texte sur CPU."
                ),
                "params_tot": 1.0, "params_act": 1.0,
                "disk": 1.02, "ram": 3.0,
                "langs": ["en", "fr", "de", "es", "it", "pt"],
                "role_pref": ["assistant_light", "routing_classification", "edge_on_device", "enterprise"],
                "link": "https://huggingface.co/ibm-granite/granite-4.0-1b"
            }
        },
        "Granite 4.0 350M": {
            "type": "local",
            "repo_id": "ibm-granite/granite-4.0-350m-GGUF",
            "filename": "granite-4.0-350m-Q4_K_M.gguf",
            "file": os.path.join(LOCAL_MODEL_DIR, "granite-4.0-350m-Q4_K_M.gguf"),
            "ctx": 4096,
            "info": {
                "fam": "Granite 4.0", "editor": "IBM",
                "desc": (
                    "Micro-modèle 350M (≈0,4B) ultra-léger, optimal pour classification, "
                    "détection d’intention, filtrage, normalisation ou routage. Très faible "
                    "empreinte mémoire, parfait pour environnements extrêmement contraints "
                    "ou comme brique de pré- / post-traitement."
                ),
                "params_tot": 0.4, "params_act": 0.4,
                "disk": 0.24, "ram": 1.0,
                "langs": ["en", "fr", "de", "es", "it", "pt"],
                "role_pref": ["routing_classification", "edge_on_device", "enterprise"],
                "link": "https://huggingface.co/ibm-granite/granite-4.0-350m"
            }
        }
    },

    # =========================================================================
    # 🏠 LG AI RESEARCH
    # =========================================================================
    "🏠 LG AI Research - EXAONE": {
        "EXAONE 3.5 2.4B Instruct": {
            "type": "local",
            "repo_id": "bartowski/EXAONE-3.5-2.4B-Instruct-GGUF",
            "filename": "EXAONE-3.5-2.4B-Instruct-Q4_K_M.gguf",
            "file": os.path.join(LOCAL_MODEL_DIR, "EXAONE-3.5-2.4B-Instruct-Q4_K_M.gguf"),
            "ctx": 32768,
            "info": {
                "fam": "EXAONE 3.5", "editor": "LG AI Research",
                "desc": (
                    "Modèle bilingue coréen/anglais 2.4B très performant de LG. "
                    "Architecture optimisée, long contexte 32K et bons scores sur les "
                    "benchmarks standard pour sa taille. Intéressant comme alternative "
                    "bilingue à Qwen/Gemma pour des cas d’usage EN/KR."
                ),
                "params_tot": 2.4, "params_act": 2.4,
                "disk": 1.64, "ram": 5.0,
                "langs": ["ko", "en"],
                "role_pref": ["assistant_generalist", "rag"],
                "link": "https://huggingface.co/LGAI-EXAONE/EXAONE-3.5-2.4B-Instruct"
            }
        }
    },

    # =========================================================================
    # 🏠 MadeAgents
    # =========================================================================
    "🏠 MadeAgents - Hammer": {
        "Hammer 2.1 0.5B": {
            "type": "local",
            "repo_id": "Nekuromento/Hammer2.1-0.5b-Q6_K-GGUF",
            "filename": "hammer2.1-0.5b-q6_k.gguf",
            "file": os.path.join(LOCAL_MODEL_DIR, "hammer2.1-0.5b-q6_k.gguf"),
            "ctx": 32768,
            "info": {
                "fam": "Hammer 2.1", "editor": "MadeAgents",
                "desc": (
                    "Modèle ultra-compact (~0,5B) spécialisé en function calling et "
                    "pilotage d’outils. Adapté aux workflows d’agents simples, à très "
                    "faible latence, avec un contexte 32K utile pour des traces courtes "
                    "ou de petits plans d’action."
                ),
                "params_tot": 0.5, "params_act": 0.5,
                "disk": 0.50, "ram": 2.0,
                "langs": ["en", "zh", "fr", "de", "es", "it", "pt", "ja", "ko", "ar", "ru"],
                "role_pref": ["tool_calling", "edge_on_device", "assistant_light"],
                "link": "https://huggingface.co/MadeAgents/Hammer2.1-0.5b"
            }
        },
        "Hammer 2.1 1.5B": {
            "type": "local",
            "repo_id": "mradermacher/Hammer2.1-1.5b-GGUF",
            "filename": "Hammer2.1-1.5b.Q4_K_M.gguf",
            "file": os.path.join(LOCAL_MODEL_DIR, "Hammer2.1-1.5b.Q4_K_M.gguf"),
            "ctx": 32768,
            "info": {
                "fam": "Hammer 2.1", "editor": "MadeAgents",
                "desc": (
                    "Version 1.5B de Hammer, dense, avec bon compromis taille/capacité "
                    "pour des agents locaux complexes orientés function calling "
                    "et orchestration d’API."
                ),
                "params_tot": 1.5, "params_act": 1.5,
                "disk": 1.00, "ram": 4.0,
                "langs": ["en", "zh", "fr", "de", "es", "it", "pt", "ja", "ko", "ar", "ru"],
                "role_pref": ["tool_calling", "assistant_generalist"],
                "link": "https://huggingface.co/MadeAgents/Hammer2.1-1.5b"
            }
        },
        "Hammer 2.1 3B": {
            "type": "local",
            "repo_id": "mradermacher/Hammer2.1-3b-GGUF",
            "filename": "Hammer2.1-3b.Q4_K_M.gguf",
            "file": os.path.join(LOCAL_MODEL_DIR, "Hammer2.1-3b.Q4_K_M.gguf"),
            "ctx": 32768,
            "info": {
                "fam": "Hammer 2.1", "editor": "MadeAgents",
                "desc": (
                    "Le plus capable des 'petits' Hammers (~3B). Très robuste sur les "
                    "appels d'outils complexes, les plans multi-étapes et les scénarios "
                    "agentiques riches, tout en restant raisonnable en ressources."
                ),
                "params_tot": 3.0, "params_act": 3.0,
                "disk": 2.00, "ram": 6.5,
                "langs": ["en", "zh", "fr", "de", "es", "it", "pt", "ja", "ko", "ar", "ru"],
                "role_pref": ["tool_calling", "assistant_generalist", "rag"],
                "link": "https://huggingface.co/MadeAgents/Hammer2.1-3b"
            }
        }
    },

    # =========================================================================
    # 🏠 Meta Llama
    # =========================================================================
    "🏠 Meta - Llama": {
        "Llama 3.2 1B Instruct": {
            "type": "local",
            "repo_id": "bartowski/Llama-3.2-1B-Instruct-GGUF",
            "filename": "Llama-3.2-1B-Instruct-Q4_K_M.gguf",
            "file": os.path.join(LOCAL_MODEL_DIR, "Llama-3.2-1B-Instruct-Q4_K_M.gguf"),
            "ctx": 128000,
            "info": {
                "fam": "Llama 3.2", "editor": "Meta",
                "desc": (
                    "Petit modèle 1B multilingue optimisé pour le dialogue, le résumé, "
                    "le tool calling léger et les applications embarquées, avec contexte "
                    "128K. Idéal pour des assistants simples, des agents légers ou du "
                    "traitement local à faible coût."
                ),
                "params_tot": 1.23, "params_act": 1.23,
                "disk": 0.81, "ram": 3.0,
                "langs": ["en", "fr", "de", "es", "it", "pt", "hi", "th"],
                "role_pref": ["assistant_light", "edge_on_device"],
                "link": "https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct"
            }
        },
        "Llama 3.2 3B Instruct": {
            "type": "local",
            "repo_id": "bartowski/Llama-3.2-3B-Instruct-GGUF",
            "filename": "Llama-3.2-3B-Instruct-Q4_K_M.gguf",
            "file": os.path.join(LOCAL_MODEL_DIR, "Llama-3.2-3B-Instruct-Q4_K_M.gguf"),
            "ctx": 128000,
            "info": {
                "fam": "Llama 3.2", "editor": "Meta",
                "desc": (
                    "Modèle 3B multilingue, très équilibré en génération, résumé, "
                    "raisonnement léger et code, avec contexte 128K. Excellent compromis "
                    "pour un assistant local généraliste sur GPU ou CPU puissant."
                ),
                "params_tot": 3.21, "params_act": 3.21,
                "disk": 2.02, "ram": 6.0,
                "langs": ["en", "fr", "de", "es", "it", "pt", "hi", "th"],
                "role_pref": ["assistant_generalist", "rag", "code"],
                "link": "https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct"
            }
        }
    },

    # =========================================================================
    # 🏠 Microsoft
    # =========================================================================
    "🏠 Microsoft - Phi": {
        "Phi-3.5 Mini Instruct": {
            "type": "local",
            "repo_id": "bartowski/Phi-3.5-mini-instruct-GGUF",
            "filename": "Phi-3.5-mini-instruct-Q4_K_M.gguf",
            "file": os.path.join(LOCAL_MODEL_DIR, "Phi-3.5-mini-instruct-Q4_K_M.gguf"),
            "ctx": 128000,
            "info": {
                "fam": "Phi-3.5", "editor": "Microsoft",
                "desc": (
                    "Modèle 3.8B très dense en données de raisonnement, contexte 128K. "
                    "Excellente qualité en logique, maths, explications pas-à-pas et "
                    "programmation. Particulièrement adapté au tutorat, au RAG analytique "
                    "et aux cas d’usage éducatifs."
                ),
                "params_tot": 3.8, "params_act": 3.8,
                "disk": 2.39, "ram": 8.0,
                "langs": ["en", "fr", "de", "es", "it", "pt", "zh"],
                "role_pref": [
                    "assistant_generalist",
                    "reasoning",
                    "math_stem",
                    "code",
                    "educational_tutor",
                    "rag"
                ],
                "link": "https://huggingface.co/microsoft/Phi-3.5-mini-instruct"
            }
        }
    },

    # =========================================================================
    # 🏠 Nvidia
    # =========================================================================
    "🏠 Nvidia - AceMath": {
        "AceMath 1.5B Instruct": {
            "type": "local",
            "repo_id": "mradermacher/AceMath-1.5B-Instruct-GGUF",
            "filename": "AceMath-1.5B-Instruct.Q4_K_M.gguf",
            "file": os.path.join(LOCAL_MODEL_DIR, "AceMath-1.5B-Instruct.Q4_K_M.gguf"),
            "ctx": 32768,
            "info": {
                "fam": "AceMath", "editor": "Nvidia",
                "desc": (
                    "Modèle spécialisé en mathématiques et raisonnement STEM, basé sur "
                    "Qwen 2.5 1.5B. Très bon sur les preuves, problèmes quantitatifs et "
                    "explications structurées, avec contexte 32K."
                ),
                "params_tot": 1.54, "params_act": 1.54,
                "disk": 1.09, "ram": 4.0,
                "langs": ["en", "zh", "fr", "de", "es", "it", "pt", "ja", "ko", "ar", "ru"],
                "role_pref": ["math_stem", "reasoning", "educational_tutor"],
                "link": "https://huggingface.co/nvidia/AceMath-1.5B-Instruct"
            }
        }
    },

    # =========================================================================
    # 🏠 Salesforce
    # =========================================================================
    "🏠 Salesforce - xLAM": {
        "xLAM-2 1B FC": {
            "type": "local",
            "repo_id": "Salesforce/xLAM-2-1b-fc-r-gguf",
            "filename": "xLAM-2-1B-fc-r-Q4_K_M.gguf",
            "file": os.path.join(LOCAL_MODEL_DIR, "xLAM-2-1B-fc-r-Q4_K_M.gguf"),
            "ctx": 32768,
            "info": {
                "fam": "xLAM-2", "editor": "Salesforce",
                "desc": (
                    "Modèle 'Large Action Model' 1B spécialisé en function calling (FC). "
                    "Idéal pour piloter des agents ou des outils API avec une très faible "
                    "latence et un contexte 32K."
                ),
                "params_tot": 1.0, "params_act": 1.0,
                "disk": 0.98, "ram": 3.5,
                "langs": ["en"],
                "role_pref": ["tool_calling", "edge_on_device"],
                "link": "https://huggingface.co/Salesforce/xLAM-2-1b-fc-r"
            }
        }
    },

    # =========================================================================
    # 🏠 TII UAE (Falcon)
    # =========================================================================
    "🏠 TII UAE - Falcon": {
        "Falcon 3 1B Instruct": {
            "type": "local",
            "repo_id": "bartowski/Falcon3-1B-Instruct-GGUF",
            "filename": "Falcon3-1B-Instruct-Q4_K_M.gguf",
            "file": os.path.join(LOCAL_MODEL_DIR, "Falcon3-1B-Instruct-Q4_K_M.gguf"),
            "ctx": 8192,
            "info": {
                "fam": "Falcon 3", "editor": "TII UAE",
                "desc": (
                    "Nouvelle génération Falcon (fin 2024). Très léger (1B), optimisé pour "
                    "l'efficacité et le déploiement edge avec contexte 8K."
                ),
                "params_tot": 1.0, "params_act": 1.0,
                "disk": 0.75, "ram": 3.0,
                "langs": ["en", "fr", "de", "es", "it", "pt", "ar"],
                "role_pref": ["assistant_light", "edge_on_device"],
                "link": "https://huggingface.co/tiiuae/Falcon3-1B-Instruct"
            }
        },
        "Falcon 3 3B Instruct": {
            "type": "local",
            "repo_id": "bartowski/Falcon3-3B-Instruct-GGUF",
            "filename": "Falcon3-3B-Instruct-Q4_K_M.gguf",
            "file": os.path.join(LOCAL_MODEL_DIR, "Falcon3-3B-Instruct-Q4_K_M.gguf"),
            "ctx": 32768,
            "info": {
                "fam": "Falcon 3", "editor": "TII UAE",
                "desc": (
                    "Grand frère du 1B. Modèle 3B performant avec contexte 32K, "
                    "rivalisant avec Llama 3.2 3B. Bon équilibre vitesse/qualité pour un "
                    "assistant local généraliste."
                ),
                "params_tot": 3.0, "params_act": 3.0,
                "disk": 2.01, "ram": 6.0,
                "langs": ["en", "fr", "de", "es", "it", "pt", "ar"],
                "role_pref": ["assistant_generalist"],
                "link": "https://huggingface.co/tiiuae/Falcon3-3B-Instruct"
            }
        }
    },

    # =========================================================================
    # ☁️ API MISTRAL (Cloud)
    # =========================================================================
    "☁️ Mistral": {
        "Mistral Large 3": {
            "type": "api",
            "api_id": "mistral-large-latest",
            "ctx": 256000,
            "eco_ops": {"kwh_1k_in": 0.0003, "kwh_1k_out": 0.0006, "embodied_g_1k": 0.12},
            "info": {
                "fam": "Mistral Large", "editor": "Mistral AI",
                "desc": (
                    "Modèle généraliste multimodal SOTA (texte + vision), MoE 675B/41B "
                    "(675B paramètres totaux, 41B actifs), contexte 256K. "
                    "Très adapté aux assistants quotidiens haut de gamme, au RAG longue "
                    "portée (rapports, bases documentaires), à l’agentique (tool calling, "
                    "workflows) et aux cas d’usage d’entreprise exigeants."
                ),
                "params_tot": 675, "params_act": 41,
                "disk": 0.0, "ram": 0.0,
                "langs": ["en", "fr", "de", "es", "it", "pt"],
                "role_pref": [
                    "assistant_generalist",
                    "rag",
                    "reasoning",
                    "code",
                    "tool_calling",
                    "enterprise"
                ],
                "link": "https://docs.mistral.ai/models/mistral-large-3-25-12"
            }
        },
        "Mistral Small 3.2": {
            "type": "api",
            "api_id": "mistral-small-latest",
            "ctx": 128000,
            "eco_ops": {"kwh_1k_in": 0.00015, "kwh_1k_out": 0.0003, "embodied_g_1k": 0.04},
            "info": {
                "fam": "Mistral Small", "editor": "Mistral AI",
                "desc": (
                    "Modèle dense 24B multimodal (texte + vision) optimisé pour couvrir "
                    "~80 % des cas d’usage génériques : chat, rédaction, résumé, RAG, "
                    "requêtes métier. Contexte 128K, très bon en suivi d’instructions et "
                    "function calling. Idéal comme 'daily driver' cloud."
                ),
                "params_tot": 24, "params_act": 24,
                "disk": 0.0, "ram": 0.0,
                "langs": ["en", "fr", "de", "es", "it", "pt"],
                "role_pref": ["assistant_generalist", "rag", "code", "tool_calling"],
                "link": "https://docs.mistral.ai/models/mistral-small-3-2-25-06"
            }
        },
        "Magistral Small 1.2": {
            "type": "api",
            "api_id": "magistral-small-latest",
            "ctx": 128000,
            "eco_ops": {"kwh_1k_in": 0.00015, "kwh_1k_out": 0.0003, "embodied_g_1k": 0.04},
            "info": {
                "fam": "Magistral", "editor": "Mistral AI",
                "desc": (
                    "Modèle 24B orienté 'reasoning' (System 2) multimodal, dérivé de "
                    "Mistral Small 3.2 avec traces de raisonnement (<think>) et "
                    "entraînement supplémentaire sur des tâches complexes. "
                    "Particulièrement adapté aux maths, au code, aux problèmes STEM et "
                    "aux chaînes de raisonnement explicites."
                ),
                "params_tot": 24, "params_act": 24,
                "disk": 0.0, "ram": 0.0,
                "langs": ["en", "fr", "de", "es", "it", "pt"],
                "role_pref": ["reasoning", "math_stem", "code", "assistant_generalist"],
                "link": "https://docs.mistral.ai/models/magistral-small-1-2-25-09"
            }
        },
        "Ministral 3 14B": {
            "type": "api",
            "api_id": "ministral-14b-latest",
            "ctx": 256000,
            "eco_ops": {"kwh_1k_in": 0.00010, "kwh_1k_out": 0.00020, "embodied_g_1k": 0.025},
            "info": {
                "fam": "Ministral 3", "editor": "Mistral AI",
                "desc": (
                    "Plus grand modèle dense de la famille edge (texte + vision, contexte "
                    "256K). Offre des performances proches de Mistral Small 3.2 tout en "
                    "restant conçu pour le déploiement local. Pertinent pour un assistant "
                    "local multimodal 'haut de gamme', du RAG avancé, du code et des cas "
                    "métier exigeants avec une ou plusieurs GPUs."
                ),
                "params_tot": 14, "params_act": 14,
                "disk": 0.0, "ram": 0.0,
                "langs": ["en", "fr", "de", "es", "it", "pt"],
                "role_pref": ["assistant_generalist", "rag", "code"],
                "link": "https://docs.mistral.ai/models/ministral-3-14b-25-12"
            }
        },
        "Ministral 3 8B": {
            "type": "api",
            "api_id": "ministral-8b-latest",
            "ctx": 256000,
            "eco_ops": {"kwh_1k_in": 0.00008, "kwh_1k_out": 0.00016, "embodied_g_1k": 0.02},
            "info": {
                "fam": "Ministral 3", "editor": "Mistral AI",
                "desc": (
                    "Modèle edge 8B multimodal, puissant et efficace, pensé pour tourner "
                    "localement (peut tenir dans ~12 Go de VRAM en FP8, moins en quantisé). "
                    "Très bon compromis qualité/latence/coût pour un assistant local, du "
                    "RAG sur documents d’entreprise et des tâches analytiques."
                ),
                "params_tot": 8, "params_act": 8,
                "disk": 0.0, "ram": 0.0,
                "langs": ["en", "fr", "de", "es", "it", "pt"],
                "role_pref": ["assistant_generalist", "rag", "code", "edge_on_device"],
                "link": "https://docs.mistral.ai/models/ministral-3-8b-25-12"
            }
        },
        "Ministral 3 3B": {
            "type": "api",
            "api_id": "ministral-3b-latest",
            "ctx": 256000,
            "eco_ops": {"kwh_1k_in": 0.00005, "kwh_1k_out": 0.00010, "embodied_g_1k": 0.01},
            "info": {
                "fam": "Ministral 3", "editor": "Mistral AI",
                "desc": (
                    "Plus petit modèle dense de la famille edge, multimodal (texte + vision) "
                    "et contexte long (256K). Conçu pour environnements très contraints "
                    "(edge devices, petits serveurs) pour de la conversation légère, "
                    "de la classification, du résumé court, du routage et des agents simples."
                ),
                "params_tot": 3, "params_act": 3,
                "disk": 0.0, "ram": 0.0,
                "langs": ["en", "fr", "de", "es", "it", "pt"],
                "role_pref": ["assistant_light", "routing_classification", "edge_on_device"],
                "link": "https://docs.mistral.ai/models/ministral-3-3b-25-12"
            }
        }
    }
}

