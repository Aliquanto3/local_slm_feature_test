# 🧪 Wavestone Local AI Workbench

**Auteur :** Anaël YAHI (Consultant Senior IA & Data Science, Wavestone)  
**Licence :** Apache 2.0

Ce projet est une application **Streamlit** conçue pour benchmarker et démontrer les capacités des **Small Language Models (SLM)** tournant localement sur CPU, et les comparer avec les modèles Cloud de l'API Mistral AI (Large, Small, Ministral).

L'objectif est de prouver la viabilité de l'IA Générative "Edge" (offline) pour des cas d'usage métiers spécifiques (Triage, RGPD, RAG, IoT) sans nécessiter de GPU coûteux.

![Workbench Screenshot](https://via.placeholder.com/800x400?text=Wavestone+Local+AI+Workbench+Preview)

## 🚀 Fonctionnalités

* **Moteur Hybride :** Basculez instantanément entre Inférence Locale (CPU via `llama.cpp`) et Inférence Cloud (API Mistral).
* **Modèles Supportés :**
    * 🏠 **Local :** Llama 3.2 (1B/3B), Qwen 2.5, Gemma 2, Phi-3.5, SmolLM2.
    * ☁️ **API :** Mistral Large 3, Mistral Small 3.2, Magistral (Reasoning), Ministral 3 (3B/8B/14B).
* **Cas d'Usage Intégrés :**
    * 🏢 **Ops :** Triage d'emails et Anonymisation RGPD.
    * 🤖 **IoT :** Simulation de commandes via Function Calling.
    * 📝 **RAG :** Synthèse de documents PDF/TXT.
    * 💻 **Code & Logique :** Génération de code et Chain of Thought.
* **Gestion Intelligente :** Téléchargement automatique des modèles GGUF et gestion dynamique de la RAM (cache clearing).

## 🛠️ Prérequis Techniques

Pour reproduire cet environnement (spécifiquement sous Windows), il est **impératif** de respecter la version de Python ci-dessous pour éviter les erreurs de compilation C++.

* **OS :** Windows 10/11 (Testé) ou Linux/Mac.
* **Python :** **Version 3.11** (Requis pour la compatibilité des roues pré-compilées `llama-cpp-python`).
* **Matériel :** CPU (8GB+ RAM recommandé). Pas de GPU nécessaire.

## 📦 Installation

### 1. Cloner le projet
```bash
git clone [https://github.com/votre-username/wavestone-local-ai-workbench.git](https://github.com/votre-username/wavestone-local-ai-workbench.git)
cd wavestone-local-ai-workbench
```

### 2. Créer l'environnement virtuel (Python 3.11)
Assurez-vous d'avoir Python 3.11 installé.
```powershell
# Windows (PowerShell)
py -3.11 -m venv .venv
```

### 3. Installer les dépendances
C'est l'étape critique. Nous installons une version pré-compilée de `llama-cpp-python` pour CPU pour éviter d'avoir à installer Visual Studio Build Tools.

```powershell
# 1. Installer llama-cpp-python (Version CPU pré-compilée pour Windows/3.11)
.\.venv\Scripts\python.exe -m pip install llama-cpp-python --extra-index-url [https://abetlen.github.io/llama-cpp-python/whl/cpu](https://abetlen.github.io/llama-cpp-python/whl/cpu)

# 2. Installer le reste des dépendances (Streamlit, Mistral, etc.)
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## ⬇️ Téléchargement des Modèles

Le projet inclut un script utilitaire qui télécharge automatiquement les versions quantifiées (GGUF Q4_K_M) optimisées pour CPU.

```powershell
.\.venv\Scripts\python.exe download_gguf_models.py
```
*Le script vérifiera l'existence des fichiers dans le dossier `models_gguf/` et ne téléchargera que les manquants.*

## ⚙️ Configuration API (Optionnel)

Pour utiliser les modèles **Cloud** (Mistral Large, Ministral API, Magistral), vous avez besoin d'une clé API Mistral.

1.  Obtenez une clé sur [console.mistral.ai](https://console.mistral.ai/).
2.  Deux méthodes pour l'utiliser :
    * **Directement dans l'interface :** Entrez la clé dans la barre latérale de l'application.
    * **Variable d'environnement :** Définissez `MISTRAL_API_KEY` dans votre système.

## ▶️ Lancement de l'Application

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```
L'application s'ouvrira automatiquement dans votre navigateur à l'adresse `http://localhost:8501`.

## 🐛 Dépannage Courant

**Erreur : `Failed to load model from file` / `tensor not found`**
* Vous utilisez probablement une version obsolète de `llama-cpp-python`. Assurez-vous d'avoir installé la version via la commande indiquée ci-dessus (étape 3).
* Vérifiez que le fichier GGUF a bien été téléchargé complètement (taille > 500Mo).

**Erreur : `ModuleNotFoundError: No module named 'streamlit'`**
* Vous n'utilisez pas l'exécutable python de votre environnement virtuel. Utilisez bien `.\.venv\Scripts\python.exe ...`.

**Lenteur extrême :**
* C'est normal sur CPU pour les gros modèles (>7B). Préférez les modèles "Tiny" (Llama 3.2 1B, Gemma 2 2B, Qwen 2.5 1.5B) pour une expérience fluide sur PC portable standard.

## 🤝 Contribution

Les contributions sont les bienvenues ! Merci d'ouvrir une issue avant de proposer une PR majeure.

## 📜 Licence

Ce projet est sous licence **Apache 2.0**.
Copyright © 2025 Wavestone.