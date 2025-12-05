"""
Configuration centralisée des modèles pour Wavestone Local AI Workbench.
Fait le lien entre l'interface Streamlit et les fichiers GGUF téléchargés.
"""
import os

LOCAL_MODEL_DIR = "models_gguf"

MODELS_DB = {
    # -------------------------------------------------------------------------
    # ☁️ MISTRAL API
    # -------------------------------------------------------------------------
    "☁️ Mistral": {
        "Mistral Large 3": {
            "type": "api",
            "api_id": "mistral-large-latest",
            "ctx": 256000,
            "info": {
                "fam": "Mistral Large", "editor": "Mistral AI",
                "desc": (
                    "Modèle généraliste multimodal SOTA (texte + vision), MoE 41B/675B, "
                    "avec contexte 256K. Très adapté aux assistants quotidiens haut de gamme, "
                    "au RAG longue portée (rapports, bases documentaires), à l’agentique "
                    "(tool calling, workflows) et aux cas d’usage d’entreprise exigeants "
                    "où la robustesse et la qualité priment sur le coût."
                ),
                "params_tot": 675, "params_act": 41, "disk": 0.0, "ram": 0.0,
                "link": "https://docs.mistral.ai/models/mistral-large-3-25-12"
            }
        },
        "Mistral Small 3.2": {
            "type": "api",
            "api_id": "mistral-small-latest",
            "ctx": 128000,
            "info": {
                "fam": "Mistral Small", "editor": "Mistral AI",
                "desc": (
                    "Modèle 24B multimodal (texte + vision) optimisé pour couvrir ~80 % des "
                    "cas d’usage génériques : chat, rédaction, résumé, RAG, requêtes métier. "
                    "Long contexte (128K), très bon en suivi d’instructions, réduction des "
                    "répétitions et function calling. Idéal comme 'daily driver' cloud "
                    "performant mais plus économique que Large 3."
                ),
                "params_tot": 24, "params_act": 24, "disk": 0.0, "ram": 0.0,
                "link": "https://docs.mistral.ai/models/mistral-small-3-2-25-06"
            }
        },
        "Magistral Small 1.2": {
            "type": "api",
            "api_id": "magistral-small-latest",
            "ctx": 128000,
            "info": {
                "fam": "Magistral", "editor": "Mistral AI",
                "desc": (
                    "Modèle 24B orienté 'reasoning' (System 2) multimodal, dérivé de Mistral "
                    "Small 3.2 avec traces de raisonnement (<think>) et entraînement "
                    "supplémentaire sur des tâches complexes. Particulièrement adapté aux "
                    "maths, au code, aux problèmes STEM et aux chaînes de raisonnement "
                    "explicites, tout en restant utilisable comme assistant généraliste."
                ),
                "params_tot": 24, "params_act": 24, "disk": 0.0, "ram": 0.0,
                "link": "https://docs.mistral.ai/models/magistral-small-1-2-25-09"
            }
        },
        "Ministral 3 14B": {
            "type": "api",
            "api_id": "ministral-14b-latest",
            "ctx": 256000,
            "info": {
                "fam": "Ministral 3", "editor": "Mistral AI",
                "desc": (
                    "Plus grand modèle dense de la famille edge (texte + vision, contexte 256K). "
                    "Offre des performances proches de Mistral Small 3.2 tout en restant "
                    "conçu pour le déploiement local. Pertinent pour un assistant local "
                    "multimodal 'haut de gamme', du RAG avancé, du code et des cas métier "
                    "demandant une bonne robustesse, avec une ou plusieurs GPUs."
                ),
                "params_tot": 14, "params_act": 14, "disk": 0.0, "ram": 0.0,
                "link": "https://docs.mistral.ai/models/ministral-3-14b-25-12"
            }
        },
        "Ministral 3 8B": {
            "type": "api",
            "api_id": "ministral-8b-latest",
            "ctx": 256000,
            "info": {
                "fam": "Ministral 3", "editor": "Mistral AI",
                "desc": (
                    "Modèle edge 8B multimodal, puissant et efficace, pensé pour tourner "
                    "localement (peut tenir dans ~12 Go de VRAM en FP8, moins en quantisé). "
                    "Très bon compromis qualité/latence/coût pour un assistant local, du RAG "
                    "sur documents d’entreprise, du code et des tâches analytiques."
                ),
                "params_tot": 8, "params_act": 8, "disk": 0.0, "ram": 0.0,
                "link": "https://docs.mistral.ai/models/ministral-3-8b-25-12"
            }
        },
        "Ministral 3 3B": {
            "type": "api",
            "api_id": "ministral-3b-latest",
            "ctx": 256000,
            "info": {
                "fam": "Ministral 3", "editor": "Mistral AI",
                "desc": (
                    "Plus petit modèle dense de la famille edge, multimodal (texte + vision) "
                    "et contexte long (256K). Conçu pour environnements très contraints "
                    "(edge devices, petits serveurs), pour de la conversation légère, "
                    "de la classification, du résumé court, du routage et des agents simples."
                ),
                "params_tot": 3, "params_act": 3, "disk": 0.0, "ram": 0.0,
                "link": "https://docs.mistral.ai/models/ministral-3-3b-25-12"
            }
        }
    },

    # -------------------------------------------------------------------------
    # 🏠 IBM GRANITE
    # -------------------------------------------------------------------------
    "🏠 IBM - Granite": {
        "Granite 3.0 3B Instruct": {
            "type": "local",
            "file": os.path.join(LOCAL_MODEL_DIR, "granite-3.0-3b-a800m-instruct-Q4_K_M.gguf"),
            "ctx": 4096,
            "info": {
                "fam": "Granite 3.0", "editor": "IBM",
                "desc": (
                    "Modèle MoE 3B (~800M paramètres actifs) orienté entreprise, open-source. "
                    "Multilingue, bon en résumé, classification, extraction, Q&A et code. "
                    "Très adapté aux cas d’usage d’entreprise sérieux (cybersécurité, "
                    "conformité, analyse documentaire) où la stabilité et la gouvernance "
                    "sont prioritaires."
                ),
                "params_tot": 3.3, "params_act": 0.8,
                "disk": 2.06, "ram": 6.0,
                "link": "https://huggingface.co/ibm-granite/granite-3.0-3b-a800m-instruct"
            }
        },
        "Granite 4.0 1B": {
            "type": "local",
            "file": os.path.join(LOCAL_MODEL_DIR, "granite-4.0-1b-Q4_K_M.gguf"),
            "ctx": 4096,
            "info": {
                "fam": "Granite 4.0", "editor": "IBM",
                "desc": (
                    "Modèle 'nano' 1B dense/hybride, pensé pour le edge/on-device. "
                    "Idéal pour des tâches légères : agents simples, extraction, "
                    "classification, routage, automatisations texte sur CPU."
                ),
                "params_tot": 1.0, "params_act": 1.0,
                "disk": 1.02, "ram": 3.0,
                "link": "https://huggingface.co/ibm-granite/granite-4.0-1b"
            }
        },
        "Granite 4.0 350M": {
            "type": "local",
            "file": os.path.join(LOCAL_MODEL_DIR, "granite-4.0-350m-Q4_K_M.gguf"),
            "ctx": 4096,
            "info": {
                "fam": "Granite 4.0", "editor": "IBM",
                "desc": (
                    "Micro-modèle 350M ultra-léger, optimal pour classification, "
                    "détection d’intention, filtrage, normalisation ou routage. "
                    "Très faible empreinte mémoire, parfait pour environnements "
                    "extrêmement contraints."
                ),
                "params_tot": 0.35, "params_act": 0.35,
                "disk": 0.22, "ram": 1.0,
                "link": "https://huggingface.co/ibm-granite/granite-4.0-350m"
            }
        }
    },

    # -------------------------------------------------------------------------
    # 🏠 META LLAMA
    # -------------------------------------------------------------------------
    "🏠 Meta - Llama": {
        "Llama 3.2 1B Instruct": {
            "type": "local",
            "file": os.path.join(LOCAL_MODEL_DIR, "Llama-3.2-1B-Instruct-Q4_K_M.gguf"),
            "ctx": 128000,
            "info": {
                "fam": "Llama 3.2", "editor": "Meta",
                "desc": (
                    "Petit modèle 1B multilingue optimisé pour le dialogue, le résumé, "
                    "le tool calling léger et les applications embarquées. Idéal pour "
                    "des assistants simples, des agents légers, ou du traitement local "
                    "à faible coût."
                ),
                "params_tot": 1.23, "params_act": 1.23,
                "disk": 0.81, "ram": 3.0,
                "link": "https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct"
            }
        },
        "Llama 3.2 3B Instruct": {
            "type": "local",
            "file": os.path.join(LOCAL_MODEL_DIR, "Llama-3.2-3B-Instruct-Q4_K_M.gguf"),
            "ctx": 128000,
            "info": {
                "fam": "Llama 3.2", "editor": "Meta",
                "desc": (
                    "Modèle 3B multilingue, très équilibré en génération, résumé, "
                    "raisonnement léger et code. Excellent compromis pour un assistant "
                    "local généraliste sur GPU ou CPU puissant."
                ),
                "params_tot": 3.21, "params_act": 3.21,
                "disk": 2.02, "ram": 6.0,
                "link": "https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct"
            }
        }
    },

    # -------------------------------------------------------------------------
    # 🏠 QWEN
    # -------------------------------------------------------------------------
    "🏠 Alibaba - Qwen": {
        "Qwen 2.5 1.5B Instruct": {
            "type": "local",
            "file": os.path.join(LOCAL_MODEL_DIR, "qwen2.5-1.5b-instruct-q4_k_m.gguf"),
            "ctx": 32768,
            "info": {
                "fam": "Qwen 2.5", "editor": "Alibaba",
                "desc": (
                    "Petit modèle 1.5B très performant en multilingue, extraction, "
                    "résumé, recherche documentaire et code. Long contexte (32K). "
                    "Idéal pour assistants légers, RAG courts et automatisation métier."
                ),
                "params_tot": 1.54, "params_act": 1.31,
                "disk": 1.07, "ram": 4.0,
                "link": "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct"
            }
        },
        "Qwen 2.5 3B Instruct": {
            "type": "local",
            "file": os.path.join(LOCAL_MODEL_DIR, "qwen2.5-3b-instruct-q4_k_m.gguf"),
            "ctx": 32768,
            "info": {
                "fam": "Qwen 2.5", "editor": "Alibaba",
                "desc": (
                    "Modèle 3B multilingue long contexte (32K), très performant en "
                    "génération structurée, code, analyse logique et agentique. Excellent "
                    "candidat comme SLM principal pour un assistant local polyvalent."
                ),
                "params_tot": 3.09, "params_act": 2.77,
                "disk": 2.10, "ram": 7.0,
                "link": "https://huggingface.co/Qwen/Qwen2.5-3B-Instruct"
            }
        }
    },

    # -------------------------------------------------------------------------
    # 🏠 MICROSOFT / GOOGLE / HF
    # -------------------------------------------------------------------------
    "🏠 Microsoft, Google & HF": {
        "Phi-3.5 Mini Instruct": {
            "type": "local",
            "file": os.path.join(LOCAL_MODEL_DIR, "Phi-3.5-mini-instruct-Q4_K_M.gguf"),
            "ctx": 128000,
            "info": {
                "fam": "Phi-3.5", "editor": "Microsoft",
                "desc": (
                    "Modèle 3.8B très dense en données de raisonnement, avec contexte 128K. "
                    "Excellente qualité en logique, maths, explications pas-à-pas et "
                    "programmation. Particulièrement adapté au tutorat, au RAG analytique "
                    "et aux cas d’usage éducatifs."
                ),
                "params_tot": 3.8, "params_act": 3.8,
                "disk": 2.39, "ram": 8.0,
                "link": "https://huggingface.co/microsoft/Phi-3.5-mini-instruct"
            }
        },
        "Gemma 2 2B Instruct": {
            "type": "local",
            "file": os.path.join(LOCAL_MODEL_DIR, "gemma-2-2b-it-Q4_K_M.gguf"),
            "ctx": 8192,
            "info": {
                "fam": "Gemma 2", "editor": "Google",
                "desc": (
                    "Modèle 2B open-weight de Google (techno Gemini), très bon en rédaction, "
                    "Q&A, code et raisonnement. Fiable et sûr, adapté aux assistants texte, "
                    "documentation technique et prototypage d’agents."
                ),
                "params_tot": 2.0, "params_act": 2.0,
                "disk": 1.71, "ram": 5.0,
                "link": "https://huggingface.co/google/gemma-2-2b-it"
            }
        },
        "SmolLM2 1.7B": {
            "type": "local",
            "file": os.path.join(LOCAL_MODEL_DIR, "SmolLM2-1.7B-Instruct-Q4_K_M.gguf"),
            "ctx": 2048,
            "info": {
                "fam": "SmolLM2", "editor": "HuggingFace",
                "desc": (
                    "Modèle compact 1.7B conçu pour tourner on-device. Bon en chat simple, "
                    "réécriture, résumé, extraction et classification. Idéal pour agents "
                    "embarqués, micro-services NLP et pipelines légers."
                ),
                "params_tot": 1.7, "params_act": 1.7,
                "disk": 1.06, "ram": 4.0,
                "link": "https://huggingface.co/HuggingFaceTB/SmolLM2-1.7B-Instruct"
            }
        }
    }
}
