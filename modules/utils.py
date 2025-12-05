import os
import time
import pypdf
import pandas as pd  # INDISPENSABLE : Requis pour le tableau de métriques
from io import StringIO
import streamlit as st

# --- GESTION DES IMPORTS OPTIONNELS ---
# Permet à l'application de ne pas crasher si une lib manque

# 1. Backend Local (Llama.cpp)
try:
    from llama_cpp import Llama
    HAS_LOCAL_LIB = True
except ImportError:
    HAS_LOCAL_LIB = False

# 2. Backend Cloud (Mistral Client)
try:
    from mistralai import Mistral
    HAS_MISTRAL_LIB = True
except ImportError:
    HAS_MISTRAL_LIB = False

# 3. Green IT (CodeCarbon) - INDISPENSABLE pour la mesure d'énergie
try:
    from codecarbon import OfflineEmissionsTracker
    HAS_CODECARBON = True
except ImportError:
    HAS_CODECARBON = False


# --- CHARGEMENT DU MOTEUR (LOCAL) ---
@st.cache_resource(show_spinner="Chargement du modèle en mémoire RAM...", max_entries=1)
def load_local_llm(path, ctx_size):
    """Charge un modèle GGUF en mémoire avec Llama-cpp"""
    abs_path = os.path.abspath(path)
    print(f"\n🔄 [DEBUG] Chargement : {abs_path}")
    
    if not HAS_LOCAL_LIB:
        raise ImportError("Librairie `llama-cpp-python` manquante.")
        
    try:
        # n_gpu_layers=-1 : Utilise le GPU si dispo, sinon CPU
        return Llama(model_path=abs_path, n_ctx=min(ctx_size, 8192), n_gpu_layers=-1, verbose=True)
    except Exception as e:
        raise RuntimeError(f"Erreur Llama-cpp : {str(e)}")


# --- HELPERS (TOKENS & FICHIERS) ---

def count_tokens_approx(text: str) -> int:
    """
    Estimation rapide et légère du nombre de tokens.
    Ratio conservateur : 1 token ~= 2.7 caractères.
    Ne nécessite aucun chargement de modèle ni de tokenizer externe (transformers).
    """
    if not text: 
        return 0
    return int(len(text) / 2.7)

def extract_text_from_file(uploaded_file):
    """Extrait le texte brut d'un PDF ou TXT"""
    text = ""
    if uploaded_file.type == "application/pdf":
        try:
            pdf_reader = pypdf.PdfReader(uploaded_file)
            for page in pdf_reader.pages: 
                extracted = page.extract_text()
                if extracted: text += extracted + "\n"
        except Exception as e:
            return f"[Erreur lecture PDF: {str(e)}]"
    elif uploaded_file.type == "text/plain":
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
        text = stringio.read()
    return text


# --- MOTEUR DE GÉNÉRATION PRINCIPAL ---

def generate_stream(model_type, model_conf, llm_local, api_key, messages, temperature=0.7, max_tokens=1024, top_p=0.9, top_k=40, carbon_intensity=475.0):
    """
    Gère l'inférence streamée + Monitoring Green IT + Affichage Tableau
    """
    response_placeholder = st.empty()
    
    # Check Sécurité
    if model_type == "local" and llm_local is None:
        response_placeholder.error("❌ Modèle local non chargé.")
        return ""

    response_placeholder.markdown("⏳ _Réflexion..._")
    
    # --- SETUP CODECARBON ---
    tracker = None
    energy_kwh = 0.0
    
    # On lance le tracker SEULEMENT si c'est un modèle local ET que la lib est présente
    if HAS_CODECARBON and model_type == "local":
        try:
            # On utilise CodeCarbon uniquement pour mesurer l'énergie brute (kWh)
            # On force "FRA" pour l'init interne (sans impact car on recalcule le CO2 nous-mêmes après)
            # measure_power_secs=0.1 : Sampling rapide pour capturer les pics brefs d'inférence
            tracker = OfflineEmissionsTracker(
                country_iso_code="FRA", 
                measure_power_secs=0.1, 
                log_level="error", 
                save_to_file=False
            )
            tracker.start()
        except Exception as e:
            print(f"⚠️ CodeCarbon Error: {e}")

    start_time = time.time()
    full_response = ""
    input_tokens = 0
    output_tokens = 0
    
    # --- BRANCHE API ---
    if model_type == "api":
        if not api_key:
            response_placeholder.error("Clé API manquante.")
            return ""
        if not HAS_MISTRAL_LIB:
            response_placeholder.error("Librairie `mistralai` manquante.")
            return ""
            
        try:
            client = Mistral(api_key=api_key)
            stream = client.chat.stream(
                model=model_conf["api_id"],
                messages=messages,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens
            )
            for chunk in stream:
                content = chunk.data.choices[0].delta.content
                if content:
                    full_response += content
                    output_tokens += 1
                    response_placeholder.markdown(full_response + "▌")
                if hasattr(chunk.data, "usage") and chunk.data.usage:
                    input_tokens = chunk.data.usage.prompt_tokens
                    
        except Exception as e:
            response_placeholder.error(f"API Error: {e}")
            return ""

    # --- BRANCHE LOCALE ---
    else:
        # Estimation tokens input (Approximation rapide)
        prompt_str = " ".join([m["content"] for m in messages])
        input_tokens = count_tokens_approx(prompt_str)
        
        try:
            stream = llm_local.create_chat_completion(
                messages=messages, 
                stream=True, 
                temperature=temperature, 
                top_p=top_p, 
                top_k=top_k, 
                max_tokens=max_tokens
            )
            
            for chunk in stream:
                if "content" in chunk["choices"][0]["delta"]:
                    content = chunk["choices"][0]["delta"]["content"]
                    full_response += content
                    output_tokens += 1
                    response_placeholder.markdown(full_response + "▌")
                    
        except ValueError as e:
            # FIX AUTOMATIQUE (Fallback Gemma/System role)
            if "System role not supported" in str(e):
                system_msg = next((m for m in messages if m['role'] == 'system'), None)
                new_msgs = [m for m in messages if m['role'] != 'system']
                
                if system_msg and new_msgs and new_msgs[0]['role'] == 'user':
                    new_msgs[0]['content'] = f"Context: {system_msg['content']}\n\nUser: {new_msgs[0]['content']}"
                    
                    try:
                        stream = llm_local.create_chat_completion(
                            messages=new_msgs, stream=True, temperature=temperature, 
                            top_p=top_p, top_k=top_k, max_tokens=max_tokens
                        )
                        for chunk in stream:
                            if "content" in chunk["choices"][0]["delta"]:
                                full_response += chunk["choices"][0]["delta"]["content"]
                                output_tokens += 1
                                response_placeholder.markdown(full_response + "▌")
                    except Exception: 
                        return ""
            else:
                return ""
        except Exception:
            return ""

    # --- STOP & CALCULS METRICS ---
    duration = time.time() - start_time
    
    if tracker:
        try:
            tracker.stop()
            # Récupération de l'énergie brute mesurée par le tracker
            energy_kwh = tracker.final_emissions_data.energy_consumed
        except Exception:
            pass

    speed = output_tokens / duration if duration > 0 else 0
    
    # Calcul manuel du CO2 : Energie (kWh) * Intensité (g/kWh) = gCO2
    co2_g = energy_kwh * carbon_intensity
    energy_wh = energy_kwh * 1000

    response_placeholder.markdown(full_response)
    
    # --- CONSTRUCTION DU TABLEAU RÉCAPITULATIF ---
    st.markdown("#### 📊 Métriques de la session")
    
    # On prépare les données pour le DataFrame
    metrics_data = {
        "Indicateur": [
            "⏱️ Durée (s)", 
            "⚡ Vitesse (tok/s)", 
            "📥 Input (tok)", 
            "📤 Output (tok)", 
            "🔋 Énergie (Wh)", 
            "🌍 Empreinte (mg CO₂e)" # mg car chiffres souvent très petits pour une requête
        ],
        "Valeur": [
            f"{duration:.2f}",
            f"{speed:.1f}",
            f"{input_tokens}",
            f"{output_tokens}",
            "N/A (Cloud)" if model_type == "api" else f"{energy_wh:.5f}",
            "N/A (Cloud)" if model_type == "api" else f"{co2_g * 1000:.2f}"
        ]
    }
    
    df_metrics = pd.DataFrame(metrics_data)
    
    # Affichage en tableau interactif (triable, exportable CSV)
    st.dataframe(
        df_metrics, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "Indicateur": st.column_config.TextColumn("Indicateur", width="medium"),
            "Valeur": st.column_config.TextColumn("Résultat", width="medium")
        }
    )
    
    return full_response