import streamlit as st
import os
import time
import pypdf 
import pandas as pd
from io import StringIO

# Import de la configuration externalisée
from config.models_config import MODELS_DB

# Gestion des imports optionnels
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
    /* Correction contraste texte */
    .stTextArea textarea, .stTextInput input {
        background-color: #2b313e;
        color: #ffffff;
    }
    .stProgress > div > div > div > div { background-color: #4C3C92; }
    div[data-testid="column"] { padding: 0.5rem; }
    
    /* Ajustement esthétique pour la navigation par Radio Boutons */
    div[role="radiogroup"] {
        background-color: #262730;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 20px;
        overflow-x: auto; /* Permet le scroll horizontal sur petit écran */
    }
</style>
""", unsafe_allow_html=True)

# --- FILTRAGE DYNAMIQUE ---
def get_available_models(db):
    available_db = {}
    local_models_found = 0
    for family, models in db.items():
        # Détection "Cloud" via mot clé API ou emoji Nuage
        if "API" in family or "☁️" in family:
            available_db[family] = models
            continue
        valid_models = {}
        for name, config in models.items():
            if config["type"] == "local":
                abs_path = os.path.abspath(config["file"])
                if os.path.exists(abs_path):
                    valid_models[name] = config
                    local_models_found += 1
        if valid_models:
            available_db[family] = valid_models
    return available_db, local_models_found

AVAILABLE_DB, COUNT_LOCAL_MODELS = get_available_models(MODELS_DB)

# --- HELPER DATAFRAME ---
def create_model_dataframe(source_db, model_type_filter):
    data = []
    for family, variants in source_db.items():
        is_api_fam = "API" in family or "☁️" in family
        
        if (model_type_filter == "local" and is_api_fam) or (model_type_filter == "api" and not is_api_fam):
            continue
        for name, config in variants.items():
            info = config["info"]
            status = "✅ Prêt"
            if config["type"] == "local" and not os.path.exists(config["file"]):
                status = "❌ Manquant"
            elif config["type"] == "api":
                status = "☁️ Cloud"

            # Gestion de l'affichage RAM (On cache 0.0 pour l'API)
            ram_display = info.get("ram", 0)
            if ram_display == 0:
                ram_display = None # Affichera une case vide ou un tiret

            data.append({
                "Modèle": name,
                "Éditeur": info["editor"],
                "Description": info["desc"],
                "Params Totaux": info["params_tot"],
                "Params Actifs": info["params_act"],
                "Ctx Max": config["ctx"],
                "Taille Disque": info["disk"],
                "RAM": ram_display,
                "Documentation": info["link"]
            })
    return pd.DataFrame(data)

# ==========================================
# ⬅️ SIDEBAR
# ==========================================
with st.sidebar:
    # 1. LOGO WAVESTONE
    try:
        logo_path = os.path.join("assets", "Wavestone_Logo.svg")
        if os.path.exists(logo_path):
            st.image(logo_path, use_container_width=True)
        else:
            st.title("Wavestone AI")
    except Exception:
        st.title("Wavestone AI")

    st.header("⚙️ Moteur IA")
    
    if not AVAILABLE_DB:
        st.error("🚫 Aucun modèle disponible.")
        st.stop()

    selected_family = st.selectbox("Famille de modèles", list(AVAILABLE_DB.keys()))
    available_variants = list(AVAILABLE_DB[selected_family].keys())
    selected_variant = st.selectbox("Version", available_variants)
    current_config = AVAILABLE_DB[selected_family][selected_variant]

    api_key = None
    if "API" in selected_family or "☁️" in selected_family:
        st.info("☁️ **Mode Cloud Connecté**")
        env_key = os.getenv("MISTRAL_API_KEY", "")
        api_key = st.text_input("Clé API Mistral", value=env_key, type="password", placeholder="xyz...")
        if not HAS_MISTRAL_LIB:
            st.error("Manque : `pip install mistralai`")
        if not api_key:
            st.caption("⚠️ Clé requise.")

    if current_config["type"] == "local":
        st.caption(f"📁 Source: `{os.path.basename(current_config['file'])}`")

    st.divider()
    st.caption(
        """
        Developed for [**Wavestone**](https://www.wavestone.com/fr/) 
        by [**Anaël YAHI**](https://www.linkedin.com/in/anaël-yahi/) (2025)  
        🔓 Open Source (**Apache 2.0**) • [Code Source GitHub](https://github.com/Aliquanto3/local_slm_feature_test)
        """
    )

# --- CHARGEMENT MOTEUR ---
llm_local = None
if "loaded_model_name" not in st.session_state:
    st.session_state.loaded_model_name = None

if current_config["type"] == "local" and HAS_LOCAL_LIB:
    if st.session_state.loaded_model_name != selected_variant:
        st.cache_resource.clear()
        st.session_state.loaded_model_name = selected_variant
        st.toast(f"Chargement de {selected_variant}...", icon="🔄")

    @st.cache_resource(show_spinner="Chargement du modèle en mémoire RAM...", max_entries=1)
    def load_local_llm(path, ctx_size):
        abs_path = os.path.abspath(path)
        print(f"\n🔄 [DEBUG] Chargement : {abs_path}")
        try:
            return Llama(model_path=abs_path, n_ctx=min(ctx_size, 8192), n_gpu_layers=-1, verbose=True)
        except Exception as e:
            raise RuntimeError(f"Erreur Llama-cpp : {str(e)}")
    
    try:
        llm_local = load_local_llm(current_config["file"], current_config["ctx"])
        st.sidebar.success(f"✅ Chargé : {selected_variant}")
    except RuntimeError as e:
        st.error(f"🚨 Erreur : {e}")
        llm_local = None

# --- HELPERS ---
def count_tokens_local(text: str) -> int:
    if not text or not llm_local: return 0
    try: return len(llm_local.tokenize(text.encode("utf-8")))
    except: return 0

def extract_text_from_file(uploaded_file):
    text = ""
    if uploaded_file.type == "application/pdf":
        try:
            pdf_reader = pypdf.PdfReader(uploaded_file)
            for page in pdf_reader.pages: text += page.extract_text() + "\n"
        except: st.error("Erreur PDF")
    elif uploaded_file.type == "text/plain":
        text = StringIO(uploaded_file.getvalue().decode("utf-8")).read()
    return text

# --- GENERATION ENGINE ---
def generate_stream(messages, temperature=0.7, max_tokens=1024, top_p=0.9, top_k=40):
    response_placeholder = st.empty()
    if current_config["type"] == "local" and llm_local is None:
        response_placeholder.error("❌ Modèle non chargé.")
        return ""

    response_placeholder.markdown("⏳ _Réflexion..._")
    start_time = time.time()
    full_response = ""
    input_tokens = 0
    output_tokens = 0
    
    if current_config["type"] == "api":
        if not api_key: return
        try:
            client = Mistral(api_key=api_key)
            stream = client.chat.stream(
                model=current_config["api_id"], messages=messages, 
                temperature=temperature, top_p=top_p, max_tokens=max_tokens
            )
            for chunk in stream:
                content = chunk.data.choices[0].delta.content
                if content:
                    full_response += content
                    output_tokens += 1
                    response_placeholder.markdown(full_response + "▌")
                if chunk.data.usage: input_tokens = chunk.data.usage.prompt_tokens
        except Exception as e: response_placeholder.error(f"API Error: {e}")
    else:
        prompt_str = " ".join([m["content"] for m in messages])
        input_tokens = count_tokens_local(prompt_str)
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
            if "System role not supported" in str(e):
                sys_msg = next((m for m in messages if m['role'] == 'system'), None)
                new_msgs = [m for m in messages if m['role'] != 'system']
                if sys_msg and new_msgs and new_msgs[0]['role'] == 'user':
                    new_msgs[0]['content'] = f"Context: {sys_msg['content']}\n\nUser: {new_msgs[0]['content']}"
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
                    except: pass
            else: response_placeholder.error(f"Error: {e}")
        except Exception as e: response_placeholder.error(f"Error: {e}")

    duration = time.time() - start_time
    speed = output_tokens / duration if duration > 0 else 0
    response_placeholder.markdown(full_response)
    cols = st.columns(4)
    cols[0].info(f"⏱️ {duration:.2f} s")
    cols[1].info(f"⚡ {speed:.1f} t/s")
    cols[2].info(f"📥 {input_tokens} tok")
    cols[3].info(f"📤 {output_tokens} tok")
    return full_response

# ==========================================
# UI PRINCIPALE
# ==========================================
st.title("🧪 Wavestone Local AI Workbench")
st.markdown("Plateforme hybride de démonstration : **SLM Locaux (CPU)** & **API Mistral (Cloud)**.")

main_col, param_col = st.columns([4, 1], gap="medium")

with param_col:
    st.markdown("### 🎛️ Réglages")
    with st.container(border=True):
        temp = st.slider("Température", 0.0, 1.5, 0.7, 0.1)
        top_p = st.slider("Top P", 0.0, 1.0, 0.9, 0.05)
        top_k = st.slider("Top K", 0, 100, 40, 5)
        max_tokens_ui = st.slider("Max Tokens", 128, 4096, 1024, 128)

with main_col:
    # MODIFICATION : Remplacement de st.tabs par st.radio pour persistance
    # Ceci empêche le retour à l'onglet "Ops" lors du re-run du script
    
    tabs_labels = ["🏢 Ops", "🤖 IoT", "📝 Synthèse", "🌐 Traduction", "💻 Code", "🧠 Logique", "💬 Chat", "ℹ️ Documentation"]
    
    selected_tab = st.radio(
        "Navigation", 
        tabs_labels, 
        horizontal=True, 
        label_visibility="collapsed",
        key="main_navigation"
    )
    
    st.markdown("---") # Séparateur visuel

    def edit_system_prompt(default_text, key_id):
        with st.expander("👁️ Voir / Modifier le Prompt Système", expanded=False):
            return st.text_area("Instruction :", value=default_text, height=100, key=f"sys_{key_id}")

    # 1. OPS
    if selected_tab == tabs_labels[0]: 
        st.markdown("### Automatisation Ops & RGPD")
        task = st.radio("Tâche :", ["📮 Triage Emails", "🛡️ Anonymisation PII"], horizontal=True)
        col1, col2 = st.columns(2)
        with col1:
            if "Triage" in task:
                content = st.text_area("Email", "Objet: Urgent #45221\nBonjour, commande toujours pas reçue.", height=150)
                sys_prompt = edit_system_prompt('Output JSON: {"category", "urgency", "sentiment"}.', "ops_triage")
                if st.button("Analyser"):
                    with col2: generate_stream([{"role":"system", "content": sys_prompt}, {"role":"user", "content": content}], 0.1, 512, top_p, top_k)
            else:
                content = st.text_area("Texte PII", "M. Dupont (j.d@w.com) à Paris.", height=150)
                sys_prompt = edit_system_prompt('Replace names with [PERSON], emails [EMAIL].', "ops_pii")
                if st.button("Anonymiser"):
                    with col2: generate_stream([{"role":"system", "content": sys_prompt}, {"role":"user", "content": content}], 0.1, 512, top_p, top_k)

    # 2. IOT
    elif selected_tab == tabs_labels[1]:
        st.markdown("### Contrôleur IoT")
        col1, col2 = st.columns(2)
        with col1:
            cmd = st.text_input("Commande", "Allume la clim salon 22°C.")
            sys_prompt = edit_system_prompt("Convert to JSON command. Tools: set_light, set_ac.", "iot")
            if st.button("Interpréter"):
                with col2: 
                    st.markdown("```json")
                    generate_stream([{"role":"system", "content": sys_prompt}, {"role":"user", "content": cmd}], 0.1, 512, top_p, top_k)
                    st.markdown("```")

    # 3. SYNTHESE
    elif selected_tab == tabs_labels[2]:
        st.markdown("### Synthèse & RAG")
        col1, col2 = st.columns([2, 1])
        with col1:
            up = st.file_uploader("Doc", type=["txt", "pdf"], key="rag")
            txt = extract_text_from_file(up) if up else ""
            instr = st.text_area("Instruction", "Résumé structuré.")
        sys_prompt = edit_system_prompt("You are a helpful assistant specialized in analysis. Answer the user instruction based strictly on the provided context.", "rag")
        if st.button("Générer") and (txt or instr):
            with col2: generate_stream([{"role":"system", "content": sys_prompt}, {"role":"user", "content": f"CTX:\n{txt[:20000]}\nREQ: {instr}"}], temp, max_tokens_ui, top_p, top_k)

    # 4. TRADUCTION
    elif selected_tab == tabs_labels[3]:
        st.markdown("### Traduction")
        col1, col2 = st.columns([1, 1])
        with col1: src = st.text_area("Texte", "L'IA générative transforme les métiers.", height=200)
        with col2: lang = st.selectbox("Langue", ["Anglais", "Espagnol", "Allemand", "Chinois"])
        sys_prompt = edit_system_prompt(f"Translate to {lang}. Preserve the tone and formatting. Output ONLY the translation.", "trans")
        if st.button("Traduire"): generate_stream([{"role":"system", "content": sys_prompt}, {"role":"user", "content": src}], 0.3, max_tokens_ui, top_p, top_k)

    # 5. CODE
    elif selected_tab == tabs_labels[4]:
        st.markdown("### Code")
        lang = st.selectbox("Langage", ["Python", "SQL", "JS"])
        req = st.text_area("Besoin", "Fonction fibonacci.")
        sys_prompt = edit_system_prompt(f"Expert {lang} coder. Code only.", "code")
        if st.button("Coder"): generate_stream([{"role":"system", "content": sys_prompt}, {"role":"user", "content": req}], 0.2, max_tokens_ui, top_p, top_k)

    # 6. LOGIQUE
    elif selected_tab == tabs_labels[5]:
        st.markdown("### Logique")
        q = st.text_input("Problème", "Résous pas à pas : Un fermier a 17 moutons, 9 meurent et 4 s'échappent. Combien en reste-t-il et pourquoi ?")
        sys_prompt = edit_system_prompt("Logic expert. Think step-by-step.", "logic")
        if st.button("Raisonner"): generate_stream([{"role":"system", "content": sys_prompt}, {"role":"user", "content": q}], 0.6, max_tokens_ui, top_p, top_k)

    # 7. CHAT
    elif selected_tab == tabs_labels[6]:
        st.markdown("### Chat")
        sys_prompt = edit_system_prompt("Helpful assistant.", "chat")
        if "history" not in st.session_state: st.session_state.history = []
        if st.button("Reset"): st.session_state.history = []; st.rerun()
        for m in st.session_state.history:
            with st.chat_message(m["role"]): st.markdown(m["content"])
        if p := st.chat_input("Message..."):
            st.session_state.history.append({"role": "user", "content": p})
            with st.chat_message("user"): st.markdown(p)
            with st.chat_message("assistant"):
                resp = generate_stream([{"role": "system", "content": sys_prompt}] + st.session_state.history[-10:], temp, max_tokens_ui, top_p, top_k)
                st.session_state.history.append({"role": "assistant", "content": resp})

    # 8. DOC
    elif selected_tab == tabs_labels[7]: 
        st.markdown("### 📚 Documentation Interactive")
        
        doc_tab1, doc_tab2 = st.tabs(["🤖 Modèles", "🔑 API Mistral"])

        with doc_tab1:
            st.info("💡 Double-cliquez sur une cellule pour voir tout le contenu si celui-ci est coupé.")
            
            # Note méthodologique pour la RAM
            st.markdown("""
            > **ℹ️ Note méthodologique sur la RAM estimée :** > La valeur indiquée correspond à une estimation empirique pour garantir une inférence fluide sur CPU : 
            > **~2.5 × Taille du fichier GGUF**.  
            > *Cette marge couvre le chargement du modèle, le contexte (KV Cache) et l'overhead système.* > Les colonnes *Params* et *Taille Disque* sont basées sur les spécifications techniques officielles.
            """)

            def display_model_table(model_type, title):
                st.markdown(f"#### {title}")
                df = create_model_dataframe(MODELS_DB, model_type)
                st.dataframe(
                    df,
                    column_config={
                        "Modèle": st.column_config.TextColumn("Modèle", width="medium"),
                        "Documentation": st.column_config.LinkColumn("Lien", display_text="🔗 Doc"),
                        "Description": st.column_config.TextColumn("Description", width="large"),
                        "Params Totaux": st.column_config.NumberColumn(format="%.1f B"),
                        "Params Actifs": st.column_config.NumberColumn(format="%.1f B"),
                        "Taille Disque": st.column_config.NumberColumn(format="%.1f Go"),
                        "RAM": st.column_config.NumberColumn(format="%.1f Go"),
                    },
                    use_container_width=True,
                    hide_index=True
                )
            
            display_model_table("local", "🏠 Modèles Locaux")
            display_model_table("api", "☁️ Modèles API")

        with doc_tab2:
            st.markdown("#### Comment obtenir une clé API Mistral ?")
            st.markdown("""
            1. Rendez-vous sur [console.mistral.ai](https://console.mistral.ai/).
            2. Créez un compte ou connectez-vous.
            3. Allez dans la section **API Keys**.
            4. Créez une nouvelle clé et copiez-la.
            5. Collez-la dans la barre latérale ou définissez la variable `MISTRAL_API_KEY`.
            """)