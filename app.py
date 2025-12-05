import streamlit as st
import os
from config.models_config import MODELS_DB
from modules.utils import load_local_llm, HAS_LOCAL_LIB, HAS_MISTRAL_LIB
import modules.views as views # On importe notre nouveau module de vues

# --- CONFIGURATION PAGE ---
st.set_page_config(
    page_title="Wavestone Local AI Workbench", 
    layout="wide", 
    page_icon="🧪",
    initial_sidebar_state="expanded"
)

# --- CSS CUSTOM ---
st.markdown("""
<style>
    .stTextArea textarea, .stTextInput input { background-color: #2b313e; color: #ffffff; }
    .stProgress > div > div > div > div { background-color: #4C3C92; }
    div[data-testid="column"] { padding: 0.5rem; }
    div[role="radiogroup"] { background-color: #262730; padding: 10px; border-radius: 10px; margin-bottom: 20px; overflow-x: auto; }
</style>
""", unsafe_allow_html=True)

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
    # Gestion du cache RAM (Nettoyage si changement)
    if "loaded_model_name" not in st.session_state: st.session_state.loaded_model_name = None
    
    if st.session_state.loaded_model_name != selected_variant:
        st.cache_resource.clear()
        st.session_state.loaded_model_name = selected_variant
        st.toast(f"Chargement : {selected_variant}", icon="🔄")
    
    try:
        # On appelle le loader défini dans utils.py
        llm_local = load_local_llm(current_config["file"], current_config["ctx"])
        st.sidebar.success(f"✅ Prêt : {selected_variant}")
    except Exception as e:
        st.error(f"🚨 Erreur Chargement : {e}")

# ==========================================
# UI PRINCIPALE (LAYOUT)
# ==========================================
st.title("🧪 Wavestone Local AI Workbench")
st.markdown("Plateforme hybride : **SLM Locaux (CPU)** & **API Mistral**.")

main_col, param_col = st.columns([4, 1], gap="medium")

# --- COLONNE DROITE : RÉGLAGES ---
with param_col:
    st.markdown("### 🎛️ Réglages")
    with st.container(border=True):
        temp = st.slider("Température", 0.0, 1.5, 0.7, 0.1)
        top_p = st.slider("Top P", 0.0, 1.0, 0.9, 0.05)
        top_k = st.slider("Top K", 0, 100, 40, 5)
        max_tokens_ui = st.slider("Max Tokens", 128, 4096, 1024, 128)

# --- COLONNE GAUCHE : NAVIGATION ---
with main_col:
    # Menu de navigation persistant
    tabs_labels = ["🏢 Ops", "🤖 IoT", "📝 Synthèse", "🌐 Traduction", "💻 Code", "🧠 Logique", "💬 Chat", "ℹ️ Documentation"]
    selected_tab = st.radio("Nav", tabs_labels, horizontal=True, label_visibility="collapsed", key="nav")
    st.markdown("---")

    # Dictionnaire d'arguments communs pour la génération (pour éviter de répéter)
    gen_kwargs = {
        "model_type": current_config["type"],
        "model_conf": current_config,
        "llm_local": llm_local,
        "api_key": api_key,
        "temperature": temp,
        "max_tokens": max_tokens_ui,
        "top_p": top_p,
        "top_k": top_k
    }

    # ROUTING VERS LES VUES
    if selected_tab == tabs_labels[0]:   views.render_ops_tab(gen_kwargs)
    elif selected_tab == tabs_labels[1]: views.render_iot_tab(gen_kwargs)
    elif selected_tab == tabs_labels[2]: views.render_rag_tab(gen_kwargs)
    elif selected_tab == tabs_labels[3]: views.render_translation_tab(gen_kwargs)
    elif selected_tab == tabs_labels[4]: views.render_code_tab(gen_kwargs)
    elif selected_tab == tabs_labels[5]: views.render_logic_tab(gen_kwargs)
    elif selected_tab == tabs_labels[6]: views.render_chat_tab(gen_kwargs)
    elif selected_tab == tabs_labels[7]: views.render_doc_tab(MODELS_DB)