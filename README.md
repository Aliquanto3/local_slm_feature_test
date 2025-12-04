# 🤖 Wavestone Local AI Workbench

Une application **Streamlit** conçue pour benchmarker, démontrer et expérimenter avec des "Small Language Models" (SLM) directement en local (CPU/GPU), sans connexion internet ni envoi de données vers le cloud.

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red)
![Models](https://img.shields.io/badge/Models-Granite%20%7C%20Ministral%20%7C%20Llama%20%7C%20Qwen-green)

## 📂 Structure du Projet

Voici l'organisation des fichiers telle que configurée :

```text
📁 wavestone-local-ai/
├── 📄 app.py                  # L'application principale (Interface Streamlit)
├── 📄 setup_models.py         # Script d'automatisation des téléchargements (HuggingFace)
├── 📄 requirements.txt        # Liste des dépendances Python
├── 📄 TEST_PROTOCOL.md        # Scénarios de test pour les démos clients
├── 📄 README.md               # Documentation du projet (ce fichier)
└── 📦 *.gguf                  # Les modèles quantifiés (stockés à la racine)
```

## 🏗️ Les Modèles Intégrés

L'application est configurée pour "hot-swapper" (changer à la volée) entre les modèles suivants, présents à la racine :

| Famille | Fichier GGUF | Cas d'Usage Privilégié |
| :--- | :--- | :--- |
| **IBM Granite** | `granite-4.0-1b-Q4_K_M.gguf` | **Triage JSON strict, Anonymisation** (Ops Entreprise) |
| **IBM Granite** | `granite-4.0-350m-Q4_K_M.gguf` | Version ultra-légère pour tests rapides |
| **Mistral AI** | `Ministral-3-3B-Instruct...` | **Rédaction, Synthèse**, Culture Française |
| **Mistral AI** | `Ministral-3-3B-Reasoning...` | **Logique complexe**, Chaîne de pensée (CoT) |
| **Meta Llama** | `Llama-3.3-1B-Instruct...` | **Polyvalent**, Function Calling (IoT) |
| **Alibaba Qwen** | `qwen2.5-3b-instruct...` | **Mathématiques**, Code complexe |

## 🚀 Installation & Démarrage

### 1. Prérequis
Assurez-vous d'avoir Python 3.10+ installé.

```bash
# Créer un environnement virtuel (recommandé)
python -m venv venv
# Activer l'environnement (Windows)
.\venv\Scripts\activate
```

### 2. Installation des dépendances
```bash
pip install -r requirements.txt
```
*Si `requirements.txt` n'existe pas encore, installez manuellement :*
```bash
pip install streamlit llama-cpp-python huggingface_hub
```

### 3. Vérification des modèles
Si vous n'avez pas encore tous les fichiers `.gguf` listés ci-dessus, lancez le script de setup :
```bash
python setup_models.py
```
> ⚠️ **Important pour Ministral :** Ces modèles sont "Gated". Si le téléchargement échoue, loguez-vous avec `huggingface-cli login` après avoir accepté la licence sur le site Hugging Face.

### 4. Lancer le Workbench
```bash
streamlit run app.py
```

## 🧪 Guide des Démonstrations (Onglets)

L'application est divisée en pôles de compétences pour simuler des cas réels Wavestone :

1.  **🏢 Ops Entreprise :**
    * *Triage d'Emails :* Le modèle analyse un email et retourne un JSON `{catégorie, urgence, sentiment}`.
    * *Anonymisation :* Nettoyage automatique des noms et emails (RGPD).
2.  **🤖 IoT & JSON :**
    * Démonstration "Agentique" où le modèle transforme une phrase ("Allume la clim") en commande technique JSON.
3.  **📝 Synthèse & Rédac :**
    * Inclut la feature "Micro-Summarization" pour générer des objets de mails ou des résumés en 10 mots.
4.  **💻 Code :**
    * Génération de Python/SQL propre, sans texte superflu (prompt système strict).
5.  **🧠 Labo Logique :**
    * Utilise `Ministral Reasoning` pour montrer le processus de pensée interne ("Thinking process") avant de répondre.

---
*Projet interne pour évaluation des SLM.*