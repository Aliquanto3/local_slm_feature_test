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

# ==========================================
# ONGLETS MÉTIERS (Refactorés pour Layout Haut)
# ==========================================

def render_ops_tab(gen_kwargs):
    """Onglet 1 : Opérations"""
    st.markdown("### Automatisation Ops & RGPD")
    
    # LAYOUT OPTIMISÉ : On crée les colonnes D'ABORD
    col1, col2 = st.columns([1, 1]) 
    
    with col1:
        # Tous les inputs sont dans col1
        task = st.radio("Tâche :", ["📮 Triage Emails", "🛡️ Anonymisation PII"], horizontal=True)
        
        if "Triage" in task:
            content = st.text_area("Email", "Objet: Urgent #45221\nServeur prod down...", height=150)
            sys_prompt = edit_system_prompt('Output JSON: {"category": "...", "priority": "..."}', "ops_triage")
            can_run = token_guardrail(content, sys_prompt, gen_kwargs)
            
            # Bouton dans col1
            launch = st.button("Analyser", disabled=not can_run)
            
            # Action différée vers col2
            if launch:
                with col2: 
                    st.markdown("##### Résultat JSON") # Titre explicite
                    generate_stream(messages=[{"role":"system", "content": sys_prompt}, {"role":"user", "content": content}], **gen_kwargs)
        else:
            content = st.text_area("Texte PII", "M. Dupont habite au 12 rue de la Paix...", height=150)
            sys_prompt = edit_system_prompt('Replace names/locations with [ANON].', "ops_pii")
            can_run = token_guardrail(content, sys_prompt, gen_kwargs)
            
            launch = st.button("Anonymiser", disabled=not can_run)
            
            if launch:
                with col2: 
                    st.markdown("##### Texte Anonymisé")
                    generate_stream(messages=[{"role":"system", "content": sys_prompt}, {"role":"user", "content": content}], **gen_kwargs)

def render_iot_tab(gen_kwargs):
    """Onglet 2 : IoT"""
    st.markdown("### Contrôleur IoT")
    col1, col2 = st.columns([1, 1]) # Layout haut
    
    with col1:
        cmd = st.text_input("Commande", "Allume la clim salon 22°C.")
        sys_prompt = edit_system_prompt("Convert to JSON command...", "iot")
        can_run = token_guardrail(cmd, sys_prompt, gen_kwargs)
        
        if st.button("Interpréter", disabled=not can_run):
            with col2: 
                st.markdown("##### Commande JSON")
                st.markdown("```json") # Ouverture bloc code
                generate_stream(messages=[{"role":"system", "content": sys_prompt}, {"role":"user", "content": cmd}], **gen_kwargs)
                st.markdown("```")

def render_rag_tab(gen_kwargs):
    """Onglet 3 : Synthèse & RAG"""
    st.markdown("### Synthèse & RAG")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        up = st.file_uploader("Doc", type=["txt", "pdf"], key="rag")
        txt = extract_text_from_file(up) if up else ""
        if txt: st.success(f"Document chargé ({len(txt)} cars)")
        
        instr = st.text_area("Instruction", "Résumé structuré points clés.")
        sys_prompt = edit_system_prompt("You are a helpful assistant...", "rag")
        full_user_prompt = f"CTX:\n{txt}\nREQ: {instr}"
        
        can_run = token_guardrail(full_user_prompt, sys_prompt, gen_kwargs)
        
        if st.button("Générer", disabled=not can_run) and (txt or instr):
            with col2: 
                st.markdown("##### Synthèse")
                generate_stream(messages=[{"role":"system", "content": sys_prompt}, {"role":"user", "content": full_user_prompt}], **gen_kwargs)

def render_translation_tab(gen_kwargs):
    """Onglet 4 : Traduction"""
    st.markdown("### Traduction")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        lang = st.selectbox("Langue Cible", ["Anglais", "Espagnol", "Allemand", "Chinois", "Italien"])
        src = st.text_area("Texte Source", "L'IA générative transforme les métiers du conseil.", height=150)
        
        sys_prompt = edit_system_prompt(f"Translate to {lang}. Output ONLY the translation.", "trans")
        can_run = token_guardrail(src, sys_prompt, gen_kwargs)
        
        if st.button("Traduire", disabled=not can_run): 
            with col2:
                st.markdown(f"##### Traduction ({lang})")
                generate_stream(messages=[{"role":"system", "content": sys_prompt}, {"role":"user", "content": src}], **gen_kwargs)

def render_code_tab(gen_kwargs):
    """Onglet 5 : Code"""
    st.markdown("### Assistant Code")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        lang = st.selectbox("Langage", ["Python", "SQL", "JavaScript", "HTML/CSS"])
        req = st.text_area("Besoin", "Une fonction récursive pour calculer Fibonacci.", height=150)
        
        sys_prompt = edit_system_prompt(f"You are an expert {lang} coder...", "code")
        can_run = token_guardrail(req, sys_prompt, gen_kwargs)
        
        if st.button("Générer Code", disabled=not can_run): 
            with col2:
                st.markdown(f"##### Snippet {lang}")
                generate_stream(messages=[{"role":"system", "content": sys_prompt}, {"role":"user", "content": req}], **gen_kwargs)

def render_logic_tab(gen_kwargs):
    """Onglet 6 : Logique"""
    st.markdown("### Raisonnement & Logique")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        q = st.text_area("Énigme / Problème", "Un fermier a 17 moutons...", height=150)
        sys_prompt = edit_system_prompt("You are a logic expert. Think step-by-step...", "logic")
        can_run = token_guardrail(q, sys_prompt, gen_kwargs)
        
        if st.button("Raisonner", disabled=not can_run): 
            with col2:
                st.markdown("##### Chain of Thought")
                generate_stream(messages=[{"role":"system", "content": sys_prompt}, {"role":"user", "content": q}], **gen_kwargs)

def render_chat_tab(gen_kwargs):
    """Onglet 7 : Chat (Avec gestion d'historique)"""
    st.markdown("### Chat Interactif")
    sys_prompt = edit_system_prompt("You are a helpful assistant.", "chat")
    if "history" not in st.session_state: st.session_state.history = []
    if st.button("🗑️ Reset Conversation"): 
        st.session_state.history = []
        st.rerun()
    for m in st.session_state.history:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    if p := st.chat_input("Votre message..."):
        st.session_state.history.append({"role": "user", "content": p})
        with st.chat_message("user"): st.markdown(p)
        msgs_to_send = [{"role": "system", "content": sys_prompt}] + st.session_state.history[-10:]
        full_conversation_text = "\n".join([m["content"] for m in msgs_to_send])
        can_run = token_guardrail(full_conversation_text, "", gen_kwargs, display=False)
        with st.chat_message("assistant"):
            if can_run:
                resp = generate_stream(messages=msgs_to_send, **gen_kwargs)
                st.session_state.history.append({"role": "assistant", "content": resp})
            else:
                st.error("⚠️ Limite contexte.")
                st.session_state.history.pop() # On annule le message utilisateur

def render_doc_tab(models_db):
    """Onglet 8 : Documentation (Mise à jour méthodologie Iso-Scope)"""
    st.markdown("### 📚 Documentation Interactive")
    
    doc_tab1, doc_tab2, doc_tab3 = st.tabs(["🤖 Modèles & Architecture", "☁️ Mode Hybride", "🌱 Méthodologie Green IT"])

    with doc_tab1:
        st.markdown("#### Philosophie du Workbench")
        st.info("""
        **Objectif :** Démontrer qu'un SLM (Small Language Model) exécuté localement sur un CPU standard 
        peut rivaliser avec le Cloud pour des tâches ciblées (Triage, PII, Synthèse), tout en garantissant 
        la confidentialité des données et une empreinte carbone maîtrisée.
        """)
        
        st.markdown("#### 🏗️ Architecture Technique")
        st.markdown("""
        * **Moteur d'inférence :** `llama.cpp` (via `llama-cpp-python`).
        * **Format de modèle :** GGUF (GPT-Generated Unified Format).
        * **Quantization (Q4_K_M) :** Compression des poids du modèle sur 4 bits. Cela réduit la VRAM/RAM nécessaire par 4 sans perte significative de "QI" du modèle.
        """)

        st.markdown("#### 📋 Catalogue des Modèles")
        
        # Helper pour créer le dataframe (identique à avant)
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
                        "Params": f"{info['params_tot']} (Actifs: {info['params_act']})",
                        "Taille": info["disk"],
                        "RAM Req.": info.get("ram", "N/A"),
                    })
            return pd.DataFrame(data)

        st.markdown("##### 🏠 Modèles Locaux (Edge)")
        st.dataframe(_create_df("local"), use_container_width=True, hide_index=True)
        
        st.markdown("##### ☁️ Modèles Cloud (Comparaison)")
        st.dataframe(_create_df("api"), use_container_width=True, hide_index=True)

    with doc_tab2:
        st.markdown("#### Configuration API Mistral")
        st.markdown("""
        Ce workbench permet un mode **hybride**. Si le local ne suffit pas, vous pouvez basculer sur les modèles **Mistral Large** ou **Ministral** via API.
        
        **Comment l'activer ?**
        1. Générez une clé API sur [console.mistral.ai](https://console.mistral.ai/).
        2. Saisissez la clé dans la barre latérale (le champ apparaît si vous sélectionnez un modèle avec l'icône ☁️).
        3. **Note de Sécurité :** La clé n'est jamais stockée sur disque, elle reste en mémoire vive le temps de la session.
        """)

    with doc_tab3:
        st.markdown("### 🌱 Méthodologie d'Impact Environnemental (Iso-Scope)")
        
        st.success("""
        **Nouveauté Méthodologique :** Pour garantir une comparaison honnête ("Fair-play") entre le Local et le Cloud, nous calculons désormais l'empreinte sur un périmètre identique : 
        **Scope 2 (Usage complet) + Scope 3 (Amortissement Matériel).**
        """)
        
        st.markdown("#### 1. Formule Générale")
        st.latex(r'''
        Empreinte_{totale} = \underbrace{(Energie_{système} \times Intensité_{pays})}_{\text{Scope 2 : Usage}} + \underbrace{Empreinte_{fabrication}}_{\text{Scope 3 : Matériel}}
        ''')
        
        col_m1, col_m2 = st.columns(2)
        
        with col_m1:
            st.markdown("#### 🏠 Calcul Local (Votre PC)")
            st.markdown("""
            Nous ne mesurons pas seulement le processeur, mais tout l'environnement nécessaire à l'inférence.
            
            * **⚡ Énergie (Scope 2) :**
                * `CPU` : Mesuré en temps réel par **CodeCarbon** (Intel RAPL).
                * `Périphériques` : Ajout forfaitaire de **12W** (Écran, SSD, Wifi, RAM) pour refléter la consommation réelle à la prise.
            * **🌍 Intensité Carbone :**
                * Dépend du mix électrique du pays choisi (ex: France ~44g, Pologne ~700g). Source : *OWID 2023*.
            * **🏭 Fabrication (Scope 3) :**
                * Nous amortissons l'empreinte de fabrication d'un laptop professionnel standard (350 kgCO₂e) sur 4 ans d'usage.
                * Soit environ **2.8 mgCO₂e par seconde** d'inférence.
            """)
            
        with col_m2:
            st.markdown("#### ☁️ Calcul Cloud (Mistral/GPT)")
            st.markdown("""
            Nous utilisons les facteurs d'impact de la méthodologie **EcoLogits** / **Boavizta**.
            
            * **⚡ Énergie (Scope 2) :**
                * Estimée par token (Input vs Output).
                * Inclut le **PUE** (Power Usage Effectiveness) des datacenters (Refroidissement, onduleurs...).
            * **🌍 Intensité Carbone :**
                * **Mistral :** Fixé à **56g** (Datacenters France).
                * **ChatGPT :** Fixé à **367g** (Mix moyen USA).
            * **🏭 Fabrication (Scope 3) :**
                * Incluse dans le facteur par token. Elle représente la part d'usure des GPU (H100) partagés allouée à votre requête.
            """)

        st.divider()
        st.markdown("#### 📊 Pourquoi ces résultats ?")
        st.info("""
        Même en pénalisant le calcul local avec l'amortissement du matériel (Scope 3) et la consommation de l'écran (Périphériques), 
        **l'IA Locale en France reste 2x à 10x moins émissive** que les grands modèles Cloud hébergés aux USA.
        
        Cela s'explique par :
        1.  La sobriété des modèles SLM (1B à 3B paramètres vs 100B+).
        2.  Le mix électrique bas-carbone français.
        3.  L'absence de transfert réseau complexe.
        """)