# 🧪 Wavestone Local AI Workbench

**Auteur :** [Anaël YAHI](https://www.linkedin.com/in/anaël-yahi/) (Consultant Senior IA & Data Science, Wavestone)  
**Licence :** [Apache 2.0](https://fr.wikipedia.org/wiki/Licence_Apache) 
*(cette application est libre et open source, si elle inclut les mentions de copyright)*

Ce projet est une application **Streamlit** conçue pour benchmarker et démontrer les capacités des **Small Language Models (SLM)** tournant localement sur CPU, et les comparer avec les modèles Cloud de l'API Mistral AI (Large, Small, Ministral).

L'objectif est de prouver la viabilité de l'IA Générative "Edge" (offline) pour des cas d'usage métiers spécifiques (Triage, RGPD, RAG, IoT) sans nécessiter de GPU coûteux.

![Workbench Screenshot](https://raw.githubusercontent.com/Aliquanto3/local_slm_feature_test/refs/heads/main/documentation/workbench_screenshot.png)

## 🚀 Fonctionnalités

* **Moteur Hybride :** Basculez instantanément entre Inférence Locale (CPU via `llama.cpp`) et Inférence Cloud (API Mistral).
* **Modèles Supportés :**
    * 🏠 **Local :** 
        * [granite-4.0-350m](https://huggingface.co/ibm-granite/granite-4.0-350m)
        * [granite-4.0-1b](https://huggingface.co/ibm-granite/granite-4.0-1b)
        * [granite-3.0-3b-a800m-instruct](https://huggingface.co/ibm-granite/granite-3.0-3b-a800m-instruct)
        * [gemma-2-2b-it](https://huggingface.co/google/gemma-2-2b-it)
        * [Llama-3.2-1B-Instruct](https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct)
        * [Llama-3.2-3B-Instruct](https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct)
        * [Phi-3.5-mini-instruct](https://huggingface.co/microsoft/Phi-3.5-mini-instruct)
        * [Qwen2.5-1.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct)
        * [Qwen2.5-3B-Instruct](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct)
        * [SmolLM2-1.7B-Instruct](https://huggingface.co/HuggingFaceTB/SmolLM2-1.7B-Instruct)     
    * ☁️ **API :** Mistral Large 3, Mistral Small 3.2, Magistral (Reasoning), Ministral 3 (3B/8B/14B).
        * [Mistral Large 3](https://docs.mistral.ai/models/mistral-large-3-25-12)
        * [Mistral Small 3.2](https://docs.mistral.ai/models/mistral-small-3-2-25-06) 
        * [Magistral Small 1.2](https://docs.mistral.ai/models/magistral-small-1-2-25-09)
        * [Ministral 3 14B](https://docs.mistral.ai/models/ministral-3-14b-25-12)
        * [Ministral 3 8B](https://docs.mistral.ai/models/ministral-3-8b-25-12)
        * [Ministral 3 3B](https://docs.mistral.ai/models/ministral-3-3b-25-12)
* **Cas d'Usage Intégrés :**
    * 🏢 **Ops :** Triage d'emails et Anonymisation RGPD.
    * 🤖 **IoT :** Simulation de commandes via Function Calling.
    * 📝 **RAG :** Synthèse de documents PDF/TXT.
    * 💻 **Code & Logique :** Génération de code et Chain of Thought.
* **Gestion Intelligente :** Téléchargement automatique des modèles GGUF et gestion dynamique de la RAM (cache clearing).

## 🛠️ Prérequis Techniques

Pour reproduire cet environnement (spécifiquement sous Windows), il est **impératif** de respecter la version de Python ci-dessous pour éviter les erreurs de compilation C++.

* **OS :** Windows 10/11 *(testé sur 11)* ou Linux/Mac.
* **Python :** **Version 3.11** (Requis pour la compatibilité des roues pré-compilées `llama-cpp-python`).
* **Matériel :** CPU (8GB+ RAM recommandé). Pas de GPU nécessaire.

## 📦 Installation

### 1. Cloner le projet
```bash
git clone [https://github.com/Aliquanto3/local_slm_feature_test](https://github.com/Aliquanto3/local_slm_feature_test)
cd local_slm_feature_test
```

### 2. Créer l'environnement virtuel (Python 3.11)
Assurez-vous d'avoir [Python 3.11](https://www.python.org/downloads/release/python-3119/) installé *(testé sur 3.11.9)*.
```powershell
# Windows (PowerShell)
py -3.11 -m venv .venv
```

### 3. Installer les dépendances
C'est l'étape critique. Nous installons une version pré-compilée de `llama-cpp-python` pour CPU pour éviter d'avoir à installer Visual Studio Build Tools.

```powershell
# 1. Installer llama-cpp-python (Version CPU pré-compilée pour Windows/3.11)
.\.venv\Scripts\python.exe -m pip install "https://github.com/abetlen/llama-cpp-python/releases/download/v0.3.2/llama_cpp_python-0.3.2-cp311-cp311-win_amd64.whl" --force-reinstall --no-cache-dir
```

```powershell
# 2. Installer le reste des dépendances (Streamlit, Mistral, etc.)
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```
*__Remarque__ : il est proposé ici d'utiliser ".\.venv\Scripts\python.exe" plutôt que de passer complètement dans le venv pour pouvoir exécuter ce code sur les PC bloquant l'exécution de scripts.*

## ⬇️ Téléchargement des Modèles

Le projet inclut un script utilitaire qui télécharge automatiquement les versions quantifiées (GGUF Q4_K_M) optimisées pour CPU.

```powershell
.\.venv\Scripts\python.exe download_gguf_models.py
```
*Le script vérifiera l'existence des fichiers dans le dossier `models_gguf/` et ne téléchargera que les manquants.*

__Remarque__ : avant de commencer les téléchargements, vous pouvez essayer le paramètre -dry-run pour vérifier que toutes les sources fonctionnent.

```powershell
.\.venv\Scripts\python.exe download_gguf_models.py --dry-run
```

Le paramètre --force vous permet de réinstaller des modèles déjà existants (par exemple si vous craignez que le fichier initial soit corrompu).

```powershell
.\.venv\Scripts\python.exe download_gguf_models.py --force
```

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

## 😊 Test de l'application
Tout est correctement installé et fonctionnel ? Regardez le fichier [Test Protocol](https://github.com/Aliquanto3/local_slm_feature_test/blob/main/documentation/TEST_PROTOCOL.md) pour des idées de fonctionnalités à tester !

## 💡 Et pour aller plus loin ?
Vous souhaitez essayer d'autres modèles ? 
Modifiez directement le JSON du fichier [models_config.py](https://github.com/Aliquanto3/local_slm_feature_test/blob/main/config/models_config.py) pour y intégrer les caractéristiques du modèle de votre choix. Si vous remplissez correctement le JSON, vous pourrez alors télécharger le modèle via le script de téléchargement, puis le voir s'afficher directement dans l'application.
*__Remarque__ : Assurez-vous de trouver un lien de téléchargement pour un modèle "GGUF", pour qu'il soit compatible avec la libraire "llama-cpp-python" utilisée pour l'inférence locale.*

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
Copyright © 2025 [Wavestone](https://www.wavestone.com/fr/).
Veuillez créditer [Anaël Yahi](https://www.linkedin.com/in/anaël-yahi/) lors de la réutilisation de ce projet.