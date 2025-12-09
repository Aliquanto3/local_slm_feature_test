import os
import time
import pypdf
import pandas as pd
import psutil
import platform
from io import StringIO
import streamlit as st

# --- CONSTANTES GREEN IT (METHODOLOGIE ROBUSTE) ---
# 1. SCOPE 3 : Empreinte de fabrication amortie sur la durée de vie
# Hypothèse : Laptop business (350 kg CO2e) / Durée de vie 4 ans (usage pro)
# 350,000g / (4 ans * 365j * 24h * 3600s) ≈ 0.0028 g/s
LAPTOP_EMBODIED_G_PER_SEC = 0.0028 

# 2. SCOPE 2 : Correction PUE / Périphériques
# CodeCarbon mesure le CPU (ex: 20W). Il manque l'écran, le SSD, le Wifi (~10-15W constants).
# On ajoute une consommation fixe estimée pour le reste du châssis.
LAPTOP_PERIPHERALS_WATT = 12.0 # Watts constants (Écran allumé, Wifi ON)

# --- GESTION DES IMPORTS OPTIONNELS ---
try:
    from llama_cpp import Llama
    HAS_LOCAL_LIB = True
except ImportError:
    HAS_LOCAL_LIB = False

try:
    from mistralai import Mistral
    HAS_MISTRAL_LIB = True
except ImportError:
    HAS_MISTRAL_LIB = False

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
        return Llama(model_path=abs_path, n_ctx=min(ctx_size, 8192), n_gpu_layers=-1, verbose=True)
    except Exception as e:
        raise RuntimeError(f"Erreur Llama-cpp : {str(e)}")


# --- HELPERS (TOKENS & FICHIERS) ---
def count_tokens_approx(text: str) -> int:
    """Estimation rapide : 1 token ~= 2.7 caractères."""
    if not text: return 0
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
    Gère l'inférence streamée + Calcul Green IT (Fallback Manuel pour API).
    """
    response_placeholder = st.empty()
    
    # Check Sécurité
    if model_type == "local" and llm_local is None:
        response_placeholder.error("❌ Modèle local non chargé.")
        return ""

    response_placeholder.markdown("⏳ _Réflexion..._")
    
    # --- SETUP MONITORING LOCAL (CodeCarbon) ---
    cc_tracker = None
    if model_type == "local" and HAS_CODECARBON:
        try:
            cc_tracker = OfflineEmissionsTracker(
                country_iso_code="FRA", 
                measure_power_secs=0.1, 
                log_level="error", 
                save_to_file=False
            )
            cc_tracker.start()
        except Exception: pass

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
        prompt_str = " ".join([m["content"] for m in messages])
        input_tokens = count_tokens_approx(prompt_str)
        
        try:
            stream = llm_local.create_chat_completion(
                messages=messages, stream=True, temperature=temperature, 
                top_p=top_p, top_k=top_k, max_tokens=max_tokens
            )
            for chunk in stream:
                if "content" in chunk["choices"][0]["delta"]:
                    content = chunk["choices"][0]["delta"]["content"]
                    full_response += content
                    output_tokens += 1
                    response_placeholder.markdown(full_response + "▌")
        except ValueError as e:
            # Fallback (Gemma/System role)
            if "System role not supported" in str(e):
                system_msg = next((m for m in messages if m['role'] == 'system'), None)
                new_msgs = [m for m in messages if m['role'] != 'system']
                if system_msg and new_msgs and new_msgs[0]['role'] == 'user':
                    new_msgs[0]['content'] = f"CTX: {system_msg['content']}\n\nQ: {new_msgs[0]['content']}"
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
                    except Exception: return ""
            else: return ""
        except Exception: return ""

    # --- STOP & CALCULS GREEN IT ---
    # --- STOP & CALCULS GREEN IT ---
    duration = time.time() - start_time
    speed = output_tokens / duration if duration > 0 else 0
    
    energy_kwh = 0.0
    total_co2_g = 0.0
    
    # 1. CALCUL RÉEL (Celui du modèle utilisé)
    if model_type == "api":
        # Mistral (Cloud FR) - Méthode EcoLogits (Scope 2 + Scope 3 inclus dans les facteurs)
        eco = model_conf.get("eco_ops", {"kwh_1k_in": 0.0002, "kwh_1k_out": 0.0004, "embodied_g_1k": 0.05})
        e_in = (input_tokens / 1000) * eco["kwh_1k_in"]
        e_out = (output_tokens / 1000) * eco["kwh_1k_out"]
        energy_kwh = e_in + e_out
        
        scope2 = energy_kwh * 56.0 # France fixe (Datacenter)
        scope3 = ((input_tokens + output_tokens) / 1000) * eco["embodied_g_1k"]
        total_co2_g = scope2 + scope3

    else:
        # Local (CodeCarbon + Périphériques + Amortissement)
        cpu_energy_kwh = 0.0
        
        # A. Mesure CPU (Active) via CodeCarbon
        if cc_tracker:
            try:
                cc_tracker.stop()
                cpu_energy_kwh = cc_tracker.final_emissions_data.energy_consumed
            except Exception: pass
            
        # B. Estimation Périphériques (Passive : Écran, SSD...)
        # Formule : Puissance (kW) * Temps (h)
        peripherals_energy_kwh = (LAPTOP_PERIPHERALS_WATT / 1000) * (duration / 3600)
        
        # Total Énergie (Scope 2 complet)
        energy_kwh = cpu_energy_kwh + peripherals_energy_kwh
        
        # Calcul Carbone
        scope2 = energy_kwh * carbon_intensity
        
        # C. Ajout Scope 3 (Amortissement Matériel)
        scope3 = duration * LAPTOP_EMBODIED_G_PER_SEC
        
        total_co2_g = scope2 + scope3

    energy_wh = energy_kwh * 1000
    
    # 2. CALCUL COMPARATIF "ChatGPT" (Simulation USA)
    # Hypothèse : GPT-4o est un modèle "Large" (facteurs Mistral Large) hébergé aux USA.
    # Facteurs "Large" (MoE)
    gpt_factors = {"kwh_1k_in": 0.0003, "kwh_1k_out": 0.0006, "embodied_g_1k": 0.12}
    
    gpt_energy_kwh = ((input_tokens / 1000) * gpt_factors["kwh_1k_in"]) + \
                     ((output_tokens / 1000) * gpt_factors["kwh_1k_out"])
    
    INTENSITY_USA = 367.0 # Moyenne USA (Source OWID 2023)
    gpt_co2_g = (gpt_energy_kwh * INTENSITY_USA) + \
                (((input_tokens + output_tokens) / 1000) * gpt_factors["embodied_g_1k"])

    response_placeholder.markdown(full_response)

    # --- AJOUT : MESURE MÉMOIRE RAM ---
    process = psutil.Process(os.getpid())
    # On divise par 1024^3 pour avoir des Go
    ram_usage_gb = process.memory_info().rss / (1024 * 1024 * 1024)
    
    # --- TABLEAU RÉCAPITULATIF (3 COLONNES) ---
    st.markdown("#### 📊 Métriques de la session")
    
    metrics_data = {
        "Indicateur": [
            "⏱️ Durée (s)", "⚡ Vitesse (tok/s)", "📥 Input (tok)", "📤 Output (tok)", 
            "💾 RAM Actuelle (Go)", # <--- Label modifié
            "🔋 Énergie (Wh)", "🌍 Empreinte (mg CO₂e)" 
        ],
        "Ce Run": [
            f"{duration:.2f}", f"{speed:.1f}", f"{input_tokens}", f"{output_tokens}",
            f"{ram_usage_gb:.2f}",  # <--- Valeur modifiée (2 décimales)
            f"{energy_wh:.5f}", f"{total_co2_g * 1000:.2f}"
        ],
        "Si ChatGPT (USA) 🇺🇸": [
            "~", "~", f"{input_tokens}", f"{output_tokens}",
            "N/A", # <--- PAS DE COMPARAISON PERTINENTE POUR LE CLOUD
            f"{gpt_energy_kwh * 1000:.5f}", f"{gpt_co2_g * 1000:.2f}"
        ]
    }
    
    # Légendes contextuelles
    if model_type == "api":
        st.caption("ℹ️ *Ce Run (Mistral) : Datacenter France (56g).*")
    else:
        st.caption(f"ℹ️ *Ce Run (Local) : Mix Pays sélectionné ({carbon_intensity:.0f}g).*")
    
    st.caption("ℹ️ *Comparatif ChatGPT : Estimation 'Large Model' hébergé aux USA (367g).*")

    df_metrics = pd.DataFrame(metrics_data)
    
    # Affichage avec surbrillance
    st.dataframe(
        df_metrics, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "Indicateur": st.column_config.TextColumn("Métrique", width="small"),
            "Ce Run": st.column_config.TextColumn("Résultat Actuel", width="medium"),
            "Si ChatGPT (USA) 🇺🇸": st.column_config.TextColumn("Estimation ChatGPT", width="medium"),
        }
    )
    
    return full_response

# --- CONFIGURATION & HARDWARE ---
def get_hardware_specs():
    """Récupère les spécifications du PC avec explications pédagogiques."""
    try:
        # RAM
        mem = psutil.virtual_memory()
        total_ram_gb = round(mem.total / (1024**3), 2)
        avail_ram_gb = round(mem.available / (1024**3), 2)
        
        # CPU
        cpu_name = platform.processor()
        phys_cores = psutil.cpu_count(logical=False)
        log_cores = psutil.cpu_count(logical=True)
        freq = psutil.cpu_freq().max if psutil.cpu_freq() else "N/A"
        
        # On structure les données pour le tableau
        data = [
            {
                "Composant": "OS", 
                "Détail": f"{platform.system()} {platform.release()}",
                "Rôle": "Le système d'exploitation hôte."
            },
            {
                "Composant": "CPU", 
                "Détail": f"{cpu_name} ({phys_cores} Coeurs)",
                "Rôle": "Le moteur de calcul. Plus de coeurs aide au traitement parallèle."
            },
            {
                "Composant": "Fréquence", 
                "Détail": f"{freq} Mhz" if isinstance(freq, (int, float)) else "N/A",
                "Rôle": "Vitesse d'horloge du CPU."
            },
            {
                "Composant": "RAM Totale", 
                "Détail": f"{total_ram_gb} Go",
                "Rôle": "Capacité maximale. Le modèle doit tenir dedans."
            },
            {
                "Composant": "RAM Dispo", 
                "Détail": f"{avail_ram_gb} Go",
                "Rôle": "Espace libre réel maintenant. Si < Taille Modèle, ça ralentit fort."
            },
            {
                "Composant": "Architecture", 
                "Détail": platform.machine(),
                "Rôle": "Type d'instructions (souvent AMD64 ou ARM64)."
            }
        ]
        
        return data
    except Exception as e:
        return [{"Composant": "Erreur", "Détail": str(e), "Rôle": "Erreur de lecture"}]
    
def estimate_model_performance(model_size_gb, total_ram_gb):
    """
    Estime la vitesse (Tokens/s) basée sur la bande passante mémoire théorique.
    Heuristique : La vitesse d'inférence est limitée par la vitesse de lecture RAM (Memory Bandwidth Bound).
    Hypothèse 'PC Portable Pro' (DDR4/DDR5) : ~35 GB/s de bande passante effective.
    """
    
    # 1. Vérification Capacité (Si le modèle est plus gros que la RAM, ça va swapper -> 0.1 t/s)
    # On garde une marge de 2 Go pour l'OS
    if model_size_gb > (total_ram_gb - 2):
        return "⚠️ Trop lourd (Swap)", 0.1
    
    # 2. Calcul théorique
    # Formule : Bandwidth (GB/s) / Model Size (GB) = Tokens/s (approx)
    # On prend une moyenne conservatrice de 30 GB/s pour un laptop moderne
    estimated_bandwidth_gbs = 30.0 
    
    # Pénalité pour les très petits modèles (overhead CPU/Python)
    tps = estimated_bandwidth_gbs / max(model_size_gb, 0.1)
    
    # Plafond réaliste pour CPU (rarement au dessus de 100 t/s sans GPU dédié optimisé)
    tps = min(tps, 80.0)
    
    return f"~{int(tps * 0.8)} - {int(tps * 1.2)} t/s", tps