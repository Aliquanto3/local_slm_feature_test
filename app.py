import streamlit as st
import os
import pandas as pd
from config.models_config import MODELS_DB
from modules.utils import load_local_llm, HAS_LOCAL_LIB, HAS_MISTRAL_LIB
import modules.views as views 

# --- CONFIGURATION PAGE ---
st.set_page_config(
    page_title="Wavestone Local AI Workbench", 
    layout="wide", 
    page_icon="🧪",
    initial_sidebar_state="expanded"
)

# --- CSS CUSTOM (Optimisation Espace) ---
st.markdown("""
<style>
    /* Ajustement marge haute pour ne pas couper le titre (3rem au lieu de 1rem) */
    .block-container { padding-top: 3rem; padding-bottom: 2rem; }
    
    div[data-testid="column"] { padding: 0.3rem; }
    
    /* Inputs et TextAreas plus compacts */
    .stTextArea textarea, .stTextInput input, .stNumberInput input { 
        background-color: #2b313e; color: #ffffff; min-height: 0px; 
    }
    
    /* Titres plus serrés */
    h1, h2, h3 { margin-top: 0 !important; margin-bottom: 0.5rem !important; padding-top: 0 !important;}
    
    /* Métriques compactes */
    div[data-testid="stMetricValue"] { font-size: 1.1rem !important; }
    div[data-testid="stMetricLabel"] { font-size: 0.8rem !important; }
    
    /* Barre de progression custom */
    .stProgress > div > div > div > div { background-color: #4C3C92; }
</style>
""", unsafe_allow_html=True)

# --- CHARGEMENT DATA CARBONE (ROBUSTE & MISE À JOUR) ---
@st.cache_data(ttl=3600)
def load_carbon_data():
    csv_path = os.path.join("data", "carbon-intensity-electricity", "carbon-intensity-electricity.csv")
    
    # Données par défaut (Fallback)
    default_data = {"France": {"val": 56, "year": 2023, "code": "FRA"}}
    
    if not os.path.exists(csv_path):
        return default_data, ["France"]

    try:
        df = pd.read_csv(csv_path)
        
        # 1. Détection dynamique de la colonne Intensité
        # On définit les candidats connus (nouveau format API vs ancien format CSV manuel)
        known_columns = [
            "co2_intensity__gco2_kwh",                  # Nouveau format API
            "Carbon intensity of electricity - gCO2/kWh" # Ancien format
        ]
        
        # On cherche d'abord une correspondance exacte
        intensity_col = next((c for c in known_columns if c in df.columns), None)
        
        # Sinon, recherche plus large (insensible à la casse) contenant "gco2" ou "intensity"
        if not intensity_col:
            intensity_col = next((c for c in df.columns if "gco2" in c.lower() or "intensity" in c.lower()), None)
        
        if not intensity_col:
            st.warning("⚠️ Colonne intensité introuvable. Utilisation des données par défaut.")
            return default_data, ["France"]

        # 2. Renommage normalisé pour la suite du script
        # On renomme 'Entity' en 'Country' si présent, sinon on suppose que c'est déjà bon
        if "Entity" in df.columns:
            df = df.rename(columns={"Entity": "Country"})
            
        df = df.rename(columns={intensity_col: "Intensity"})
        
        # 3. Filtrage : On ne garde que la dernière année disponible pour chaque pays
        if "Year" in df.columns:
            df_sorted = df.sort_values(by="Year", ascending=False)
            df_latest = df_sorted.drop_duplicates(subset=["Country"])
        else:
            df_latest = df # Si pas d'année, on prend tel quel
            
        df_final = df_latest.sort_values(by="Country")
        
        # 4. Construction du dictionnaire
        carbon_db = {}
        for _, row in df_final.iterrows():
            code = row["Code"] if "Code" in row and pd.notna(row["Code"]) else ""
            year = int(row["Year"]) if "Year" in row else 2024
            
            carbon_db[row["Country"]] = {
                "val": row["Intensity"],
                "year": year,
                "code": code
            }
            
        return carbon_db, list(carbon_db.keys())
        
    except Exception as e:
        st.error(f"Erreur lecture CSV Carbone : {e}")
        return default_data, ["France"]

CARBON_DB, SORTED_COUNTRIES = load_carbon_data()

# --- SIDEBAR & SETUP ---
with st.sidebar:
    try:
        if os.path.exists("assets/Wavestone_Logo.svg"):
            st.image("assets/Wavestone_Logo.svg", use_container_width=True)
        else:
            st.title("Wavestone AI")
    except: st.title("Wavestone AI")

    st.header("⚙️ Moteur IA")
    
    # Sélecteurs de Modèles
    fam_list = list(MODELS_DB.keys())
    if not fam_list:
        st.error("Aucun modèle configuré.")
        st.stop()
        
    selected_family = st.selectbox("Famille", fam_list)
    available_variants = list(MODELS_DB[selected_family].keys())
    selected_variant = st.selectbox("Version", available_variants)
    current_config = MODELS_DB[selected_family][selected_variant]

    # Gestion API Key
    api_key = None
    if current_config["type"] == "api":
        st.info("☁️ **Mode Cloud**")
        api_key = st.text_input("Clé API Mistral", value=os.getenv("MISTRAL_API_KEY", ""), type="password")
        if not HAS_MISTRAL_LIB: st.error("Manque: `mistralai`")
    
    if current_config["type"] == "local":
        st.caption(f"📁 `{os.path.basename(current_config['file'])}`")

    st.divider()
    st.caption("""
    Developed for [**Wavestone**](https://www.wavestone.com/fr/) 
    by [**Anaël YAHI**](https://www.linkedin.com/in/anaël-yahi/) (2025)  
    🔓 Open Source ([**Apache 2.0**](https://fr.wikipedia.org/wiki/Licence_Apache))
    """)

# --- CHARGEMENT DU MOTEUR (LOCAL) ---
llm_local = None
if current_config["type"] == "local" and HAS_LOCAL_LIB:
    if "loaded_model_name" not in st.session_state: st.session_state.loaded_model_name = None
    
    if st.session_state.loaded_model_name != selected_variant:
        st.cache_resource.clear()
        st.session_state.loaded_model_name = selected_variant
        st.toast(f"Chargement : {selected_variant}", icon="🔄")
    
    try:
        llm_local = load_local_llm(current_config["file"], current_config["ctx"])
        st.sidebar.success(f"✅ Prêt : {selected_variant}")
    except Exception as e:
        st.error(f"🚨 Erreur Chargement : {e}")

# ==========================================
# UI PRINCIPALE (LAYOUT)
# ==========================================
st.title("🧪 Wavestone Local AI Workbench")

main_col, param_col = st.columns([7, 2], gap="small") # Ratio ajusté pour donner plus de place au contenu

# --- COLONNE DROITE : RÉGLAGES (ULTRA-COMPACTS) ---
with param_col:
    # On utilise des st.columns à l'intérieur pour gagner de la place verticale
    with st.container(border=True):
        st.markdown("##### 🎛️ Inférence")
        c1, c2 = st.columns(2)
        with c1:
            temp = st.number_input("Temperature", 0.0, 1.5, 0.7, 0.1)
            top_k = st.number_input("Top K", 0, 100, 40, 5)
        with c2:
            top_p = st.number_input("Top P", 0.0, 1.0, 0.9, 0.05)
            max_tokens_ui = st.number_input("Max Tokens", 128, 8192, 1024, 256)

    with st.container(border=True):
        st.markdown("##### 🌱 Green IT")
        
        # Trouver l'index par défaut
        default_idx = SORTED_COUNTRIES.index("France") if "France" in SORTED_COUNTRIES else 0
        
        country_choice = st.selectbox(
            "Pays", 
            ["Personnalisé"] + SORTED_COUNTRIES,
            index=default_idx + 1,
            label_visibility="collapsed" # Gain de place
        )
        
        if country_choice == "Personnalisé":
            carbon_intensity = st.number_input("gCO₂e/kWh", 0.0, 1000.0, 475.0)
        else:
            data_c = CARBON_DB[country_choice]
            carbon_intensity = data_c["val"]
            # Affichage sur une seule ligne : Drapeau/Code | Intensité | Année
            c_info1, c_info2 = st.columns([1, 1])
            c_info1.metric("Intensité", f"{carbon_intensity:.0f} g")
            c_info2.caption(f"📅 {data_c['year']}\nSource: OWID")
            
        st.caption("[Ember (2025); Energy Institute - Statistical Review of World Energy (2025)](https://ourworldindata.org/electricity-mix)")

# --- COLONNE GAUCHE : NAVIGATION ---
with main_col:
    # Menu de navigation
    tabs_labels = ["🏢 Ops", "🤖 IoT", "📝 Synthèse", "🌐 Traduction", "💻 Code", "🧠 Logique", "💬 Chat", "ℹ️ Documentation"]
    selected_tab = st.radio("Nav", tabs_labels, horizontal=True, label_visibility="collapsed", key="nav")
    st.markdown("---")

    gen_kwargs = {
        "model_type": current_config["type"],
        "model_conf": current_config,
        "llm_local": llm_local,
        "api_key": api_key,
        "temperature": temp,
        "max_tokens": max_tokens_ui,
        "top_p": top_p,
        "top_k": top_k,
        "carbon_intensity": carbon_intensity
    }

    # ROUTING
    if selected_tab == tabs_labels[0]:   views.render_ops_tab(gen_kwargs)
    elif selected_tab == tabs_labels[1]: views.render_iot_tab(gen_kwargs)
    elif selected_tab == tabs_labels[2]: views.render_rag_tab(gen_kwargs)
    elif selected_tab == tabs_labels[3]: views.render_translation_tab(gen_kwargs)
    elif selected_tab == tabs_labels[4]: views.render_code_tab(gen_kwargs)
    elif selected_tab == tabs_labels[5]: views.render_logic_tab(gen_kwargs)
    elif selected_tab == tabs_labels[6]: views.render_chat_tab(gen_kwargs)
    elif selected_tab == tabs_labels[7]: views.render_doc_tab(MODELS_DB)