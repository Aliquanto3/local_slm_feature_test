import streamlit as st
import pandas as pd
from modules.utils import generate_stream, extract_text_from_file

def edit_system_prompt(default_text, key_id):
    """Widget réutilisable pour éditer le prompt système"""
    with st.expander("👁️ Voir / Modifier le Prompt Système", expanded=False):
        return st.text_area("Instruction :", value=default_text, height=100, key=f"sys_{key_id}")

def render_ops_tab(gen_kwargs):
    """Onglet 1 : Opérations"""
    st.markdown("### Automatisation Ops & RGPD")
    task = st.radio("Tâche :", ["📮 Triage Emails", "🛡️ Anonymisation PII"], horizontal=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if "Triage" in task:
            content = st.text_area("Email", "Objet: Urgent #45221\nBonjour, commande toujours pas reçue.", height=150)
            sys_prompt = edit_system_prompt('Output JSON: {"category", "urgency", "sentiment"}.', "ops_triage")
            if st.button("Analyser"):
                with col2: 
                    st.markdown("**Résultat JSON :**")
                    generate_stream(messages=[{"role":"system", "content": sys_prompt}, {"role":"user", "content": content}], **gen_kwargs)
        else:
            content = st.text_area("Texte PII", "M. Dupont (j.d@w.com) à Paris.", height=150)
            sys_prompt = edit_system_prompt('Replace names with [PERSON], emails [EMAIL].', "ops_pii")
            if st.button("Anonymiser"):
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
        if st.button("Interpréter"):
            with col2: 
                st.markdown("```json")
                generate_stream(messages=[{"role":"system", "content": sys_prompt}, {"role":"user", "content": cmd}], **gen_kwargs)
                st.markdown("```")

def render_rag_tab(gen_kwargs):
    """Onglet 3 : Synthèse"""
    st.markdown("### Synthèse & RAG")
    col1, col2 = st.columns([2, 1])
    with col1:
        up = st.file_uploader("Doc", type=["txt", "pdf"], key="rag")
        txt = extract_text_from_file(up) if up else ""
        if txt: st.success(f"Document chargé ({len(txt)} cars)")
        instr = st.text_area("Instruction", "Résumé structuré.")
        
    sys_prompt = edit_system_prompt("You are a helpful assistant specialized in analysis.", "rag")
    
    if st.button("Générer") and (txt or instr):
        with col2: 
            prompt = f"CTX:\n{txt[:20000]}\nREQ: {instr}"
            generate_stream(messages=[{"role":"system", "content": sys_prompt}, {"role":"user", "content": prompt}], **gen_kwargs)

def render_translation_tab(gen_kwargs):
    """Onglet 4 : Traduction"""
    st.markdown("### Traduction")
    col1, col2 = st.columns([1, 1])
    with col1: 
        src = st.text_area("Texte", "L'IA générative transforme les métiers.", height=200)
    with col2: 
        lang = st.selectbox("Langue", ["Anglais", "Espagnol", "Allemand", "Chinois"])
    
    sys_prompt = edit_system_prompt(f"Translate to {lang}. Output ONLY the translation.", "trans")
    if st.button("Traduire"): 
        generate_stream(messages=[{"role":"system", "content": sys_prompt}, {"role":"user", "content": src}], **gen_kwargs)

def render_code_tab(gen_kwargs):
    """Onglet 5 : Code"""
    st.markdown("### Code")
    lang = st.selectbox("Langage", ["Python", "SQL", "JS"])
    req = st.text_area("Besoin", "Fonction fibonacci.")
    sys_prompt = edit_system_prompt(f"Expert {lang} coder. Code only.", "code")
    if st.button("Coder"): 
        generate_stream(messages=[{"role":"system", "content": sys_prompt}, {"role":"user", "content": req}], **gen_kwargs)

def render_logic_tab(gen_kwargs):
    """Onglet 6 : Logique"""
    st.markdown("### Logique")
    q = st.text_input("Problème", "Un fermier a 17 moutons, 9 meurent et 4 s'échappent. Combien en reste-t-il et pourquoi ? ")
    sys_prompt = edit_system_prompt("Logic expert. Think step-by-step.", "logic")
    if st.button("Raisonner"): 
        generate_stream(messages=[{"role":"system", "content": sys_prompt}, {"role":"user", "content": q}], **gen_kwargs)

def render_chat_tab(gen_kwargs):
    """Onglet 7 : Chat"""
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
            hist = [{"role": "system", "content": sys_prompt}] + st.session_state.history[-10:]
            # On passe les mêmes arguments de génération
            resp = generate_stream(messages=hist, **gen_kwargs)
            st.session_state.history.append({"role": "assistant", "content": resp})

def render_doc_tab(models_db):
    """Onglet 8 : Documentation"""
    st.markdown("### 📚 Documentation Interactive")
    
    doc_tab1, doc_tab2 = st.tabs(["🤖 Modèles", "🔑 API Mistral"])

    with doc_tab1:
        st.info("💡 Double-cliquez sur une cellule pour voir tout le contenu.")
        
        # Helper interne pour créer le DataFrame
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
        st.write("Pour utiliser les modèles Cloud, définissez `MISTRAL_API_KEY`.")