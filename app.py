import streamlit as st
from llama_cpp import Llama
import os
import json

# --- CONFIGURATION PAGE ---
st.set_page_config(page_title="Wavestone Local AI Workbench", layout="wide", page_icon="🧪")

st.title("🧪 Wavestone Local AI Workbench")
st.markdown("Plateforme de démonstration des capacités SLM (Small Language Models).")

# --- DATA: CONFIGURATION DES MODÈLES ---
MODELS_DB = {
    "Granite (IBM)": {
        "1B Instruct": {"file": "granite-4.0-1b-Q4_K_M.gguf", "ctx": 4096},
        "350M Instruct": {"file": "granite-4.0-350m-Q4_K_M.gguf", "ctx": 2048}
    },
    "Llama (Meta)": {
        "3.3 1B Instruct": {"file": "Llama-3.3-1B-Instruct-Q4_K_M.gguf", "ctx": 8192}
    },
    "Qwen (Alibaba)": {
        "2.5 3B Instruct": {"file": "qwen2.5-3b-instruct-q4_k_m.gguf", "ctx": 8192}
    },
    "Ministral (Mistral AI)": {
        "3 3B Instruct": {"file": "Ministral-3-3B-Instruct-2512-Q4_K_M.gguf", "ctx": 16384},
        "3 3B Reasoning": {"file": "Ministral-3-3B-Reasoning-2512-Q4_K_M.gguf", "ctx": 8192}
    }
}

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Moteur IA")
    selected_family = st.selectbox("Famille", list(MODELS_DB.keys()))
    available_variants = list(MODELS_DB[selected_family].keys())
    selected_variant = st.selectbox("Modèle", available_variants)
    
    current_config = MODELS_DB[selected_family][selected_variant]
    model_path = current_config["file"]
    
    st.divider()
    temp = st.slider("Créativité (Temp)", 0.0, 1.0, 0.7, 0.1)
    
    if not os.path.exists(model_path):
        st.error(f"❌ Manquant : {model_path}")
        st.stop()

# --- CHARGEMENT ---
@st.cache_resource(show_spinner="Chargement du modèle...")
def load_llm(path, ctx_size):
    return Llama(model_path=path, n_ctx=ctx_size, n_gpu_layers=-1, verbose=False)

llm = load_llm(model_path, current_config["ctx"])

def generate_stream(messages, temperature=0.7, max_tokens=1024):
    """Moteur de génération standard"""
    if not llm: return
    stream = llm.create_chat_completion(messages=messages, stream=True, temperature=temperature, max_tokens=max_tokens)
    response_placeholder = st.empty()
    full_response = ""
    for chunk in stream:
        if "content" in chunk["choices"][0]["delta"]:
            full_response += chunk["choices"][0]["delta"]["content"]
            response_placeholder.markdown(full_response + "▌")
    response_placeholder.markdown(full_response)

# --- ONGLETS PRINCIPAUX ---
tabs = st.tabs([
    "🏢 Ops Entreprise", 
    "🤖 IoT & JSON", 
    "📝 Synthèse & Rédac", 
    "💻 Code", 
    "🧠 Logique",
    "💬 Chat"
])

# ==========================================
# ONGLET 1 : OPS ENTREPRISE (Triage & PII)
# ==========================================
with tabs[0]:
    st.markdown("### Cas d'usage : Automatisation des Processus")
    task_type = st.radio("Tâche à effectuer :", ["📮 Triage & Classification d'Emails", "🛡️ Anonymisation (PII)"], horizontal=True)

    if "Triage" in task_type:
        st.info("💡 **Best Model:** Granite (IBM) est excellent pour la classification stricte.")
        col1, col2 = st.columns(2)
        with col1:
            email_content = st.text_area("Contenu de l'email", height=200, 
                value="Bonjour, je n'arrive pas à me connecter à mon compte client depuis hier. C'est urgent car je dois valider une commande. Mon ID est le 45221.")
            if st.button("Analyser l'email"):
                sys_prompt = """You are an AI Email Classifier. 
                Analyze the email and output a JSON object with:
                - "category": [Support, Sales, Spam, HR]
                - "urgency": [Low, Medium, High]
                - "sentiment": [Positive, Neutral, Negative]
                - "summary": A 5-word summary.
                Output ONLY valid JSON."""
                
                with col2:
                    st.markdown("**Analyse IA :**")
                    messages = [{"role": "system", "content": sys_prompt}, {"role": "user", "content": email_content}]
                    generate_stream(messages, temperature=0.1) # Temp basse pour du JSON stable

    elif "Anonymisation" in task_type:
        st.info("💡 **Objectif:** Supprimer les données personnelles (GDPR/RGPD).")
        col1, col2 = st.columns(2)
        with col1:
            pii_text = st.text_area("Texte contenant des données sensibles", height=150,
                value="M. Jean Dupont (jean.dupont@wavestone.com) a rendez-vous le 12 octobre à Paris avec Mme Martin.")
            if st.button("Anonymiser"):
                sys_prompt = "You are a PII Scrubber. Replace all names with <PERSON>, emails with <EMAIL>, and dates with <DATE>. Output only the processed text."
                with col2:
                    st.markdown("**Résultat sécurisé :**")
                    messages = [{"role": "system", "content": sys_prompt}, {"role": "user", "content": pii_text}]
                    generate_stream(messages, temperature=0.1)

# ==========================================
# ONGLET 2 : IOT & JSON (Function Calling)
# ==========================================
with tabs[1]:
    st.markdown("### 🤖 Contrôleur IoT & Function Calling")
    st.caption("Transforme le langage naturel en commandes machines structurées (JSON).")
    st.info("💡 **Best Model:** Llama 3.2 ou Granite.")

    col1, col2 = st.columns([1, 1])
    with col1:
        user_command = st.text_input("Commande vocale simulée", "Allume la clim dans le salon et règle la température sur 22 degrés.")
        
        # Définition des "outils" disponibles pour le contexte
        st.markdown("**Outils disponibles (Virtuels) :**")
        st.code("""
[
  {"function": "set_light", "args": ["location", "state", "color"]},
  {"function": "set_hvac", "args": ["location", "temperature", "mode"]}
]
        """, language="json")
        
        launch_iot = st.button("Interpréter la commande")

    with col2:
        if launch_iot:
            st.markdown("### 📟 Sortie JSON")
            sys_prompt = """You are an IoT Controller. Convert the user request into a JSON command based on available tools. 
            Output ONLY valid JSON. No explanations."""
            
            messages = [{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_command}]
            generate_stream(messages, temperature=0.1)

# ==========================================
# ONGLET 3 : SYNTHÈSE (Avec Micro-Résumé)
# ==========================================
with tabs[2]:
    st.markdown("### 📝 Assistant de Synthèse")
    
    txt_input = st.text_area("Texte source", height=200)
    # Intégration du Micro-Summarization ici
    mode_synthese = st.radio("Format de sortie :", 
        ["Résumé Standard (Bullet points)", "Micro-Résumé (Objet de mail / 1 phrase)", "Réécriture Pro"], horizontal=True)
    
    if st.button("Générer la synthèse") and txt_input:
        prompts = {
            "Résumé Standard (Bullet points)": "Summarize this text in French using bullet points. Capture key details.",
            "Micro-Résumé (Objet de mail / 1 phrase)": "Generate an extremely concise summary (max 10 words) or a subject line for this text in French.",
            "Réécriture Pro": "Rewrite this text to be more professional and corporate in French."
        }
        
        st.markdown("---")
        messages = [{"role": "system", "content": "You are a helpful assistant."}, 
                    {"role": "user", "content": f"{prompts[mode_synthese]}:\n\n{txt_input}"}]
        generate_stream(messages, temperature=0.5)

# ==========================================
# ONGLET 4 : CODE
# ==========================================
with tabs[3]:
    st.markdown("### 💻 Générateur de Code")
    lang = st.selectbox("Langage", ["Python", "SQL", "JavaScript", "HTML"])
    req = st.text_area("Besoin", placeholder="Ex: Script pour parser un CSV...")
    if st.button("Coder"):
        sys = f"You are an expert {lang} coder. Output code only. No chatting."
        messages = [{"role": "system", "content": sys}, {"role": "user", "content": req}]
        generate_stream(messages, temperature=0.2)

# ==========================================
# ONGLET 5 : LOGIQUE
# ==========================================
with tabs[4]:
    st.markdown("### 🧠 Laboratoire de Raisonnement")
    st.info("💡 **Best Model:** Ministral Reasoning ou Qwen 2.5")
    logic_q = st.text_input("Problème", "Si je sèche 5 chemises en 5h, combien de temps pour 10 chemises ?")
    if st.button("Raisonner"):
        sys = "You are a logic expert. Think step-by-step in <thinking> tags before answering."
        messages = [{"role": "system", "content": sys}, {"role": "user", "content": logic_q}]
        generate_stream(messages, temperature=0.7)

# ==========================================
# ONGLET 6 : CHAT
# ==========================================
with tabs[5]:
    st.markdown("### 💬 Chat Libre")
    if "chat_history" not in st.session_state: st.session_state.chat_history = []
    
    # Historique
    for m in st.session_state.chat_history:
        with st.chat_message(m["role"]): st.markdown(m["content"])
        
    if p := st.chat_input("Message..."):
        st.session_state.chat_history.append({"role": "user", "content": p})
        with st.chat_message("user"): st.markdown(p)
        with st.chat_message("assistant"):
            hist = [{"role": "system", "content": "You are helpful."}] + st.session_state.chat_history
            full = ""
            if llm:
                stream = llm.create_chat_completion(messages=hist, stream=True, temperature=temp)
                holder = st.empty()
                for c in stream:
                    if "content" in c["choices"][0]["delta"]:
                        full += c["choices"][0]["delta"]["content"]
                        holder.markdown(full + "▌")
                holder.markdown(full)
            st.session_state.chat_history.append({"role": "assistant", "content": full})