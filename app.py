import streamlit as st
import os
import time
import pypdf 
import pandas as pd
from io import StringIO

# Import de la configuration externalisée
from models_config import MODELS_DB

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

st.title("🧪 Wavestone Local AI Workbench")
st.markdown("Plateforme hybride de démonstration : **SLM Locaux (CPU)** & **API Mistral (Cloud)**.")

# --- CSS CUSTOM POUR LISIBILITÉ ---
st.markdown("""
<style>
    .stProgress > div > div > div > div { background-color: #4CAF50; }
    .stAlert { padding: 0.5rem; }
</style>
""", unsafe_allow_html=True)

# --- FILTRAGE DYNAMIQUE ---
def get_available_models(db):
    """Filtre les modèles pour ne garder que ceux présents sur le disque ou l'API"""
    available_db = {}
    local_models_found = 0
    
    for family, models in db.items():
        # Toujours inclure les familles API
        if "API" in family:
            available_db[family] = models
            continue
            
        # Pour les familles locales, vérifier les fichiers
        valid_models = {}
        for name, config in models.items():
            if config["type"] == "local":
                # Vérification robuste du chemin
                abs_path = os.path.abspath(config["file"])
                if os.path.exists(abs_path):
                    valid_models[name] = config
                    local_models_found += 1
                # Pas de else : on cache silencieusement les modèles manquants
                    
        if valid_models:
            available_db[family] = valid_models
            
    return available_db, local_models_found

# Chargement initial des modèles disponibles
AVAILABLE_DB, COUNT_LOCAL_MODELS = get_available_models(MODELS_DB)

# --- HELPER DATAFRAME ---
def create_model_dataframe(source_db, model_type_filter):
    """Génère un DataFrame pandas pour l'affichage tabulaire avec liens"""
    data = []
    for family, variants in source_db.items():
        is_api_fam = "API" in family
        if (model_type_filter == "local" and is_api_fam) or (model_type_filter == "api" and not is_api_fam):
            continue
            
        for name, config in variants.items():
            info = config["info"]
            # Vérif présence fichier pour statut
            status = "✅ Prêt"
            if config["type"] == "local" and not os.path.exists(config["file"]):
                status = "❌ Manquant"
            elif config["type"] == "api":
                status = "☁️ Cloud"

            data.append({
                "Modèle": name,
                "Statut": status,
                "Famille": info["fam"],
                "Éditeur": info["editor"],
                "Description": info["desc"],
                "Params Totaux (B)": info["params_tot"],
                "Params Actifs (B)": info["params_act"],
                "Ctx Max": config["ctx"],
                "Taille Disque (Go)": info["disk"],
                "Documentation": info["link"]
            })
    return pd.DataFrame(data)

# --- SIDEBAR: SÉLECTION DU MOTEUR ---
with st.sidebar:
    st.header("⚙️ Moteur IA")
    
    if not AVAILABLE_DB:
        st.error("🚫 Aucun modèle disponible.")
        st.info("Lancez `python download_gguf_models.py` dans votre terminal.")
        st.stop()

    # Affichage du nombre de modèles locaux détectés
    if COUNT_LOCAL_MODELS > 0:
        st.success(f"💾 {COUNT_LOCAL_MODELS} modèles locaux détectés")
    else:
        st.warning("⚠️ Aucun modèle local trouvé")

    selected_family = st.selectbox("Famille de modèles", list(AVAILABLE_DB.keys()))
    
    available_variants = list(AVAILABLE_DB[selected_family].keys())
    selected_variant = st.selectbox("Version", available_variants)
    current_config = AVAILABLE_DB[selected_family][selected_variant]

    # --- INPUT CLÉ API ---
    api_key = None
    if "API" in selected_family:
        st.info("☁️ **Mode Cloud Connecté**")
        # Tentative de récupération depuis variable d'environnement
        env_key = os.getenv("MISTRAL_API_KEY", "")
        api_key = st.text_input("Clé API Mistral", value=env_key, type="password", placeholder="sk-...")
        
        if not HAS_MISTRAL_LIB:
            st.error("Librairie manquante : `pip install mistralai`")
        if not api_key:
            st.caption("⚠️ Clé requise. Définissez MISTRAL_API_KEY ou entrez-la ici.")
    
    st.divider()
    st.markdown("### 🎛️ Paramètres")
    
    temp = st.slider("Température", 0.0, 1.5, 0.7, 0.1, 
                      help="Créativité. 0 = Robotique, 1.0+ = Artistique")
    
    top_p = st.slider("Top P", 0.0, 1.0, 0.9, 0.05, 
                      help="Nucleus sampling.")
    
    top_k = st.slider("Top K", 0, 100, 40, 5, 
                      help="Limite vocabulaire.")
    
    max_tokens_ui = st.slider("Max Tokens", 128, 4096, 1024, 128)

    # Infos techniques debug
    if current_config["type"] == "local":
        st.caption(f"📁 Source: `{os.path.basename(current_config['file'])}`")

    st.markdown("---")
    st.caption("Developed for **Wavestone**\nby Anaël YAHI (2025)")


# --- MOTEUR: CHARGEMENT (LOCAL) ---
llm_local = None

# On initialise un état de session pour suivre quel modèle est chargé
if "loaded_model_name" not in st.session_state:
    st.session_state.loaded_model_name = None

if current_config["type"] == "local" and HAS_LOCAL_LIB:
    
    # 1. LOGIQUE DE CHANGEMENT DE MODÈLE (Nettoyage Cache)
    if st.session_state.loaded_model_name != selected_variant:
        st.cache_resource.clear() # 🧹 On vide la RAM brutalement
        st.session_state.loaded_model_name = selected_variant
        # On force un petit toast pour prévenir l'utilisateur
        st.toast(f"Changement de modèle : Chargement de {selected_variant}...", icon="🔄")

    # 2. FONCTION DE CHARGEMENT
    @st.cache_resource(show_spinner="Chargement du modèle en mémoire RAM...", max_entries=1)
    def load_local_llm(path, ctx_size):
        abs_path = os.path.abspath(path)
        safe_ctx = min(ctx_size, 8192) # Sécurité RAM
        print(f"\n🔄 [DEBUG] Chargement physique du fichier : {abs_path}")
        try:
            # verbose=False pour ne pas spammer la console Streamlit, mais on a le print au dessus
            return Llama(
                model_path=abs_path, 
                n_ctx=safe_ctx, 
                n_gpu_layers=-1, 
                verbose=True
            )
        except Exception as e:
            raise RuntimeError(f"Erreur Llama-cpp : {str(e)}")
    
    # 3. APPEL DU CHARGEUR
    try:
        llm_local = load_local_llm(current_config["file"], current_config["ctx"])
        # Indicateur visuel de succès
        st.sidebar.success(f"✅ Chargé : {selected_variant}")
    except RuntimeError as e:
        st.error(f"🚨 Impossible de charger le modèle : {e}")
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
            for page in pdf_reader.pages: 
                extracted = page.extract_text()
                if extracted: text += extracted + "\n"
        except Exception as e: st.error(f"Erreur lecture PDF: {e}")
    elif uploaded_file.type == "text/plain":
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
        text = stringio.read()
    return text

# --- GENERATION ENGINE ---
def generate_stream(messages, temperature=0.7, max_tokens=1024, top_p=0.9, top_k=40):
    response_placeholder = st.empty()
    
    # Check simple
    if current_config["type"] == "local" and llm_local is None:
        response_placeholder.error("❌ Modèle local non chargé.")
        return ""

    response_placeholder.markdown("⏳ _Réflexion en cours..._")
    
    start_time = time.time()
    full_response = ""
    input_tokens = 0
    output_tokens = 0
    
    # --- API MISTRAL ---
    if current_config["type"] == "api":
        if not api_key:
            response_placeholder.error("Clé API manquante. Voir Sidebar.")
            return ""
        try:
            client = Mistral(api_key=api_key)
            stream_response = client.chat.stream(
                model=current_config["api_id"],
                messages=messages,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens
            )
            for chunk in stream_response:
                content = chunk.data.choices[0].delta.content
                if content:
                    full_response += content
                    output_tokens += 1
                    response_placeholder.markdown(full_response + "▌")
                if hasattr(chunk.data, "usage") and chunk.data.usage:
                    input_tokens = chunk.data.usage.prompt_tokens
        except Exception as e:
            response_placeholder.error(f"Erreur API Mistral : {e}")
            return ""

    # --- LOCAL LLAMA ---
    else:
        # Estimation tokens input
        prompt_str = " ".join([m["content"] for m in messages])
        input_tokens = count_tokens_local(prompt_str)
        
        try:
            # 1. Tentative normale (pour Llama 3, Mistral, Qwen...)
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
            # 2. GESTION D'ERREUR SPÉCIFIQUE GEMMA / PHI
            if "System role not supported" in str(e):
                # On fusionne le système dans le premier message utilisateur
                system_msg = next((m for m in messages if m['role'] == 'system'), None)
                new_messages = [m for m in messages if m['role'] != 'system']
                
                if system_msg and new_messages and new_messages[0]['role'] == 'user':
                    # On "injecte" l'instruction système au début du message user
                    original_user_content = new_messages[0]['content']
                    new_messages[0]['content'] = f"Context/Instruction: {system_msg['content']}\n\nUser Query: {original_user_content}"
                    
                    # On réessaie avec la nouvelle liste
                    try:
                        stream = llm_local.create_chat_completion(
                            messages=new_messages, 
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
                    except Exception as e2:
                        response_placeholder.error(f"Erreur Secondaire : {e2}")
                        return ""
            else:
                response_placeholder.error(f"Erreur Template Chat : {e}")
                return ""
        except Exception as e:
            response_placeholder.error(f"Erreur Inférence : {e}")
            return ""

    # --- METRICS & DISPLAY ---
    end_time = time.time()
    duration = end_time - start_time
    speed = output_tokens / duration if duration > 0 else 0
    
    response_placeholder.markdown(full_response)
    
    # Footer de stats
    cols = st.columns(4)
    cols[0].info(f"⏱️ {duration:.2f} s")
    cols[1].info(f"⚡ {speed:.1f} t/s")
    cols[2].info(f"📥 {input_tokens} tok")
    cols[3].info(f"📤 {output_tokens} tok")
    
    return full_response

# --- HELPER UI PROMPT ---
def show_system_prompt(prompt_text):
    with st.expander("👁️ Voir le Prompt Système (Instruction interne)"):
        st.code(prompt_text, language="markdown")

# --- ONGLETS ---
tabs = st.tabs(["🏢 Ops", "🤖 IoT", "📝 Synthèse", "🌐 Traduction", "💻 Code", "🧠 Logique", "💬 Chat", "ℹ️ Documentation"])

with tabs[0]: # OPS
    st.markdown("### Automatisation Ops & RGPD")
    task = st.radio("Tâche :", ["📮 Triage Emails", "🛡️ Anonymisation PII"], horizontal=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if "Triage" in task:
            default_email = """Objet: Problème Urgent Commande #45221
Bonjour, je n'ai toujours pas reçu ma commande validée il y a 10 jours. C'est inadmissible. Merci de rembourser."""
            content = st.text_area("Contenu de l'email", default_email, height=150)
            sys_prompt = 'You are a support automation bot. Analyze the email. Output strictly valid JSON with keys: {"category" (Delivery/Refund/Tech), "urgency" (Low/Medium/High), "sentiment" (Positive/Neutral/Negative)}.'
            show_system_prompt(sys_prompt)
            if st.button("Analyser l'email", type="primary"):
                with col2: 
                    st.markdown("**Résultat JSON :**")
                    generate_stream([{"role":"system", "content": sys_prompt}, {"role":"user", "content": content}], 0.1, 512, top_p, top_k)
        else:
            default_pii = "M. Jean Dupont (jean.dupont@wavestone.com) habite au 12 rue de la Paix, 75000 Paris."
            content = st.text_area("Texte contenant des PII", default_pii, height=150)
            sys_prompt = 'You are a GDPR assistant. Replace all proper names with [PERSON], emails with [EMAIL], and addresses with [ADDRESS]. Output only the anonymized text.'
            show_system_prompt(sys_prompt)
            if st.button("Anonymiser", type="primary"):
                with col2: 
                    st.markdown("**Texte Anonymisé :**")
                    generate_stream([{"role":"system", "content": sys_prompt}, {"role":"user", "content": content}], 0.1, 512, top_p, top_k)

with tabs[1]: # IOT
    st.markdown("### Contrôleur IoT (Function Calling Simulé)")
    col1, col2 = st.columns(2)
    with col1:
        cmd = st.text_input("Commande Utilisateur", "Allume la climatisation du salon et règle sur 22°C.")
        sys_prompt = """You are an IoT Controller. Convert user request to JSON command.
Available tools: 
- set_light(room, state, color)
- set_ac(room, state, temp)
- set_blind(room, level)
Output ONLY the JSON."""
        show_system_prompt(sys_prompt)
        if st.button("Interpréter la commande", type="primary"):
            with col2: 
                st.markdown("```json")
                generate_stream([{"role":"system", "content": sys_prompt}, {"role":"user", "content": cmd}], 0.1, 512, top_p, top_k)
                st.markdown("```")

with tabs[2]: # SYNTHESE
    st.markdown("### Synthèse de Documents & RAG")
    col1, col2 = st.columns([2, 1])
    with col1:
        up = st.file_uploader("Document source (PDF/TXT)", type=["txt", "pdf"], key="rag")
        txt = extract_text_from_file(up) if up else ""
        if txt: st.success(f"Document chargé : {len(txt)} caractères")
        
        instr = st.text_area("Instruction spécifique", "Fais un résumé structuré en 3 points clés.")
    
    sys_prompt = "You are a helpful assistant specialized in analysis. Answer the user instruction based strictly on the provided context."
    
    if st.button("Générer la synthèse", type="primary") and (txt or instr):
        prompt = f"CONTEXTE:\n{txt[:20000]}\n\nINSTRUCTION: {instr}" # Coupe brute pour éviter overflow
        with col2:
            st.markdown("### Résultat")
            generate_stream([{"role":"system", "content": sys_prompt}, {"role":"user", "content": prompt}], temp, max_tokens_ui, top_p, top_k)

with tabs[3]: # TRADUCTION
    st.markdown("### Traducteur Universel")
    col1, col2 = st.columns([1, 1])
    with col1:
        src = st.text_area("Texte à traduire", "L'intelligence artificielle générative transforme les processus métiers.", height=200)
    with col2:
        lang = st.selectbox("Langue cible", ["Anglais", "Espagnol", "Allemand", "Chinois", "Japonais", "Italien"])
        sys_prompt = f"You are a professional translator. Translate the following text to {lang}. Preserve the tone and formatting. Output ONLY the translation."
        if st.button("Traduire 🌐", type="primary"):
            generate_stream([{"role":"system", "content": sys_prompt}, {"role":"user", "content": src}], 0.3, max_tokens_ui, top_p, top_k)

with tabs[4]: # CODE
    st.markdown("### Assistant de Code")
    lang = st.selectbox("Langage", ["Python", "SQL", "JavaScript", "HTML/CSS", "Shell"])
    req = st.text_area("Description du besoin", "Écris une fonction pour calculer la suite de Fibonacci de manière récursive avec mémoïsation.")
    
    sys_prompt = f"You are an expert {lang} developer. Write efficient, commented code based on the request. Output markdown code blocks."
    show_system_prompt(sys_prompt)
    
    if st.button("Générer le Code", type="primary"):
        generate_stream([{"role":"system", "content": sys_prompt}, {"role":"user", "content": req}], 0.2, max_tokens_ui, top_p, top_k)

with tabs[5]: # LOGIQUE
    st.markdown("### Test de Raisonnement (Chain of Thought)")
    q = st.text_input("Problème Logique", "Si 3 chats attrapent 3 souris en 3 minutes, combien de temps faut-il à 100 chats pour attraper 100 souris ?")
    sys_prompt = "You are an expert logic professor. Think step-by-step to solve the problem. Explain your reasoning clearly before giving the final answer."
    
    if st.button("Raisonner", type="primary"):
        generate_stream([{"role":"system", "content": sys_prompt}, {"role":"user", "content": q}], 0.6, max_tokens_ui, top_p, top_k)

with tabs[6]: # CHAT
    st.markdown("### Discussion Libre")
    sys_prompt = "You are a helpful and concise assistant from Wavestone."
    
    # Gestion historique
    if "history" not in st.session_state: st.session_state.history = []
    
    # Reset btn
    if st.button("🗑️ Effacer la conversation"):
        st.session_state.history = []
        st.rerun()

    # Affichage
    for m in st.session_state.history:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    
    # Input
    if p := st.chat_input("Votre message..."):
        st.session_state.history.append({"role": "user", "content": p})
        with st.chat_message("user"): st.markdown(p)
        
        with st.chat_message("assistant"):
            # Contexte glissant (les 10 derniers messages pour garder de la mémoire sans exploser le contexte)
            recent_history = st.session_state.history[-10:]
            hist = [{"role": "system", "content": sys_prompt}] + recent_history
            resp = generate_stream(hist, temp, max_tokens_ui, top_p, top_k)
            st.session_state.history.append({"role": "assistant", "content": resp})

# ==========================================
# ONGLET 7 : DOCUMENTATION
# ==========================================
with tabs[7]:
    st.markdown("### 📚 Documentation Interactive")
    st.info("Cette table se met à jour automatiquement en fonction des fichiers détectés dans `/models_gguf`.")
    
    # Affichage du DataFrame global
    df_all = create_model_dataframe(MODELS_DB, "all") # "all" n'est pas utilisé dans le filtre actuel mais on garde la logique
    
    # On sépare pour l'affichage propre
    st.markdown("#### 🏠 Modèles Locaux")
    df_local = create_model_dataframe(MODELS_DB, "local")
    st.dataframe(
        df_local,
        column_config={
            "Documentation": st.column_config.LinkColumn("Lien", display_text="🔗 Doc"),
            "Taille Disque (Go)": st.column_config.NumberColumn(format="%.1f Go"),
            "Params Totaux (B)": st.column_config.NumberColumn(format="%.1f B"),
        },
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("#### ☁️ Modèles API")
    df_api = create_model_dataframe(MODELS_DB, "api")
    st.dataframe(
        df_api,
        column_config={
            "Documentation": st.column_config.LinkColumn("Lien", display_text="🔗 Doc"),
             "Taille Disque (Go)": st.column_config.TextColumn(), # Pas de taille pour API
        },
        use_container_width=True,
        hide_index=True
    )