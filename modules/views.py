import streamlit as st
import pandas as pd
from modules.utils import generate_stream, extract_text_from_file, count_tokens_approx

# --- WIDGETS UI COMMUNS ---

def edit_system_prompt(default_text, key_id):
    """Widget réutilisable pour éditer le prompt système"""
    with st.expander("👁️ Voir / Modifier le Prompt Système", expanded=False):
        return st.text_area("Instruction :", value=default_text, height=100, key=f"sys_{key_id}")

def token_guardrail(user_text, sys_text, gen_kwargs, display=True):
    """
    Barre de progression basée sur une estimation heuristique (/2.7 chars).
    Mentionne clairement que c'est une approximation.
    """
    # Récupération sécurisée de la config
    model_conf = gen_kwargs.get("model_conf")
    if not model_conf:
        ctx_limit = 32768
    else:
        ctx_limit = model_conf.get("ctx", 32768)
    
    # Comptage purement mathématique (ultra rapide)
    n_user = count_tokens_approx(user_text)
    n_sys = count_tokens_approx(sys_text)
    total = n_user + n_sys
    
    # Sécurité division par zéro
    usage_pct = min(total / ctx_limit, 1.0) if ctx_limit > 0 else 0
    is_valid = total <= ctx_limit
    
    if display:
        col_g1, col_g2 = st.columns([3, 1])
        
        if not is_valid:
            col_g1.error(f"⚠️ **CONTEXTE DÉPASSÉ (Est.)** : ~{total} / {ctx_limit}")
            col_g1.caption("La limite du modèle est atteinte. Réduisez le texte.")
        else:
            col_g1.caption(f"📊 **Contexte (Estimation)** : ~{total} / {ctx_limit} tokens")
            col_g1.progress(usage_pct)
    
    return is_valid

# --- ONGLETS MÉTIERS ---

def render_ops_tab(gen_kwargs):
    """Onglet 1 : Opérations"""
    st.markdown("### Automatisation Ops & RGPD")
    task = st.radio("Tâche :", ["📮 Triage Emails", "🛡️ Anonymisation PII"], horizontal=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if "Triage" in task:
            content = st.text_area("Email", "Objet: Urgent #45221\nServeur prod down...", height=150)
            sys_prompt = edit_system_prompt('Output JSON: {"category": "...", "priority": "..."}', "ops_triage")
            
            can_run = token_guardrail(content, sys_prompt, gen_kwargs)
            
            if st.button("Analyser", disabled=not can_run):
                with col2: 
                    st.markdown("**Résultat JSON :**")
                    generate_stream(messages=[{"role":"system", "content": sys_prompt}, {"role":"user", "content": content}], **gen_kwargs)
        else:
            content = st.text_area("Texte PII", "M. Dupont habite au 12 rue de la Paix...", height=150)
            sys_prompt = edit_system_prompt('Replace names/locations with [ANON].', "ops_pii")
            
            can_run = token_guardrail(content, sys_prompt, gen_kwargs)
            
            if st.button("Anonymiser", disabled=not can_run):
                with col2: 
                    st.markdown("**Texte Anonymisé :**")
                    generate_stream(messages=[{"role":"system", "content": sys_prompt}, {"role":"user", "content": content}], **gen_kwargs)

def render_iot_tab(gen_kwargs):
    """Onglet 2 : IoT"""
    st.markdown("### Contrôleur IoT")
    col1, col2 = st.columns(2)
    with col1:
        cmd = st.text_input("Commande", "Allume la clim salon 22°C.")
        sys_prompt = edit_system_prompt("Convert to JSON command. Tools: set_light, set_ac.", "iot")
        
        can_run = token_guardrail(cmd, sys_prompt, gen_kwargs)
        
        if st.button("Interpréter", disabled=not can_run):
            with col2: 
                st.markdown("```json")
                generate_stream(messages=[{"role":"system", "content": sys_prompt}, {"role":"user", "content": cmd}], **gen_kwargs)
                st.markdown("```")

def render_rag_tab(gen_kwargs):
    """Onglet 3 : Synthèse & RAG"""
    st.markdown("### Synthèse & RAG")
    col1, col2 = st.columns([2, 1])
    with col1:
        up = st.file_uploader("Doc", type=["txt", "pdf"], key="rag")
        txt = extract_text_from_file(up) if up else ""
        if txt: st.success(f"Document chargé ({len(txt)} cars)")
        
        instr = st.text_area("Instruction", "Résumé structuré points clés.")
        
    sys_prompt = edit_system_prompt("You are a helpful assistant. Use the Context provided.", "rag")
    
    # Simulation du prompt complet pour le calcul
    full_user_prompt = f"CTX:\n{txt}\nREQ: {instr}"
    
    can_run = token_guardrail(full_user_prompt, sys_prompt, gen_kwargs)
    
    if st.button("Générer", disabled=not can_run) and (txt or instr):
        with col2: 
            generate_stream(messages=[{"role":"system", "content": sys_prompt}, {"role":"user", "content": full_user_prompt}], **gen_kwargs)

def render_translation_tab(gen_kwargs):
    """Onglet 4 : Traduction"""
    st.markdown("### Traduction")
    col1, col2 = st.columns([1, 1])
    with col1: 
        src = st.text_area("Texte Source", "L'IA générative transforme les métiers du conseil.", height=200)
    with col2: 
        lang = st.selectbox("Langue Cible", ["Anglais", "Espagnol", "Allemand", "Chinois", "Italien"])
    
    sys_prompt = edit_system_prompt(f"Translate to {lang}. Output ONLY the translation.", "trans")
    
    can_run = token_guardrail(src, sys_prompt, gen_kwargs)
    
    if st.button("Traduire", disabled=not can_run): 
        generate_stream(messages=[{"role":"system", "content": sys_prompt}, {"role":"user", "content": src}], **gen_kwargs)

def render_code_tab(gen_kwargs):
    """Onglet 5 : Code"""
    st.markdown("### Assistant Code")
    lang = st.selectbox("Langage", ["Python", "SQL", "JavaScript", "HTML/CSS"])
    req = st.text_area("Besoin", "Une fonction récursive pour calculer Fibonacci.", height=150)
    
    sys_prompt = edit_system_prompt(f"You are an expert {lang} coder. Provide code only, no chatter.", "code")
    
    can_run = token_guardrail(req, sys_prompt, gen_kwargs)
    
    if st.button("Générer Code", disabled=not can_run): 
        generate_stream(messages=[{"role":"system", "content": sys_prompt}, {"role":"user", "content": req}], **gen_kwargs)

def render_logic_tab(gen_kwargs):
    """Onglet 6 : Logique"""
    st.markdown("### Raisonnement & Logique")
    q = st.text_area("Énigme / Problème", "Un fermier a 17 moutons, 9 meurent et 4 s'échappent. Combien en reste-t-il ?", height=100)
    
    sys_prompt = edit_system_prompt("You are a logic expert. Think step-by-step using Chain of Thought.", "logic")
    
    can_run = token_guardrail(q, sys_prompt, gen_kwargs)
    
    if st.button("Raisonner", disabled=not can_run): 
        generate_stream(messages=[{"role":"system", "content": sys_prompt}, {"role":"user", "content": q}], **gen_kwargs)

def render_chat_tab(gen_kwargs):
    """Onglet 7 : Chat (Avec gestion d'historique)"""
    st.markdown("### Chat Interactif")
    sys_prompt = edit_system_prompt("You are a helpful assistant.", "chat")
    
    if "history" not in st.session_state: st.session_state.history = []
    
    # Bouton Reset
    if st.button("🗑️ Reset Conversation"): 
        st.session_state.history = []
        st.rerun()
    
    # Affichage historique
    for m in st.session_state.history:
        with st.chat_message(m["role"]): st.markdown(m["content"])
        
    # Input Utilisateur
    if p := st.chat_input("Votre message..."):
        # 1. Ajout message user temporaire pour le calcul
        st.session_state.history.append({"role": "user", "content": p})
        with st.chat_message("user"): st.markdown(p)
        
        # 2. Préparation contexte (System + 10 derniers messages)
        msgs_to_send = [{"role": "system", "content": sys_prompt}] + st.session_state.history[-10:]
        
        # 3. Calcul Tokens TOTAL (System + History + New Msg)
        full_conversation_text = "\n".join([m["content"] for m in msgs_to_send])
        
        # On appelle le guardrail (sans l'afficher deux fois)
        can_run = token_guardrail(full_conversation_text, "", gen_kwargs, display=False)
        
        with st.chat_message("assistant"):
            if can_run:
                resp = generate_stream(messages=msgs_to_send, **gen_kwargs)
                st.session_state.history.append({"role": "assistant", "content": resp})
            else:
                st.error("⚠️ **ERREUR : Limite de contexte dépassée.** Veuillez réduire l'historique (Reset) ou changer de modèle.")
                st.session_state.history.pop() # On annule le message utilisateur

def render_doc_tab(models_db):
    """Onglet 8 : Documentation"""
    st.markdown("### 📚 Documentation Interactive")
    
    doc_tab1, doc_tab2 = st.tabs(["🤖 Modèles", "🔑 API Mistral"])

    with doc_tab1:
        st.info("💡 Double-cliquez sur une cellule pour voir tout le contenu.")
        
        def _create_df(model_type_filter):
            data = []
            for family, variants in models_db.items():
                is_api_fam = "API" in family or "☁️" in family
                if (model_type_filter == "local" and is_api_fam) or (model_type_filter == "api" and not is_api_fam):
                    continue
                for name, config in variants.items():
                    info = config["info"]
                    data.append({
                        "Modèle": name,
                        "Éditeur": info["editor"],
                        "Description": info["desc"],
                        "Params Totaux": info["params_tot"],
                        "Params Actifs": info["params_act"],
                        "Taille Disque": info["disk"],
                        "RAM": info.get("ram", None),
                        "Documentation": info["link"]
                    })
            return pd.DataFrame(data)

        def display_table(m_type, title):
            st.markdown(f"#### {title}")
            df = _create_df(m_type)
            st.dataframe(
                df,
                column_config={
                    "Modèle": st.column_config.TextColumn("Modèle", width="medium"),
                    "Documentation": st.column_config.LinkColumn("Lien", display_text="🔗 Doc"),
                    "Description": st.column_config.TextColumn("Description", width="large"),
                    "Params Totaux": st.column_config.NumberColumn(format="%.1f B"),
                    "RAM": st.column_config.NumberColumn(format="%.1f Go"),
                },
                use_container_width=True,
                hide_index=True
            )
        
        display_table("local", "🏠 Modèles Locaux")
        display_table("api", "☁️ Modèles API")

    with doc_tab2:
        st.markdown("#### Configuration API")
        st.write("Pour utiliser les modèles Cloud, définissez `MISTRAL_API_KEY` dans vos variables d'environnement.")