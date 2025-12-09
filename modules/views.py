import streamlit as st
import pandas as pd
import psutil
from modules.utils import generate_stream, extract_text_from_file, count_tokens_approx, get_hardware_specs, estimate_model_performance

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
    """Onglet 8 : Documentation Interactive (Améliorée avec Emojis & Libellés)"""
    st.markdown("### 📚 Documentation Interactive")
    
    # --- 1. DICTIONNAIRES DE MAPPING (CONFIG UX) ---
    # Pour afficher des jolis noms au lieu des codes techniques
    
    LANG_MAP = {
        "en": "🇬🇧 Anglais", "fr": "🇫🇷 Français", "de": "🇩🇪 Allemand",
        "es": "🇪🇸 Espagnol", "it": "🇮🇹 Italien", "pt": "🇵🇹 Portugais",
        "zh": "🇨🇳 Chinois", "ja": "🇯🇵 Japonais", "ko": "🇰🇷 Coréen",
        "ru": "🇷🇺 Russe", "ar": "🇸🇦 Arabe", "hi": "🇮🇳 Hindi", "th": "🇹🇭 Thaï"
    }

    ROLE_MAP = {
        "assistant_generalist":   "🧠 Assistant Polyvalent",
        "assistant_light":        "⚡ Assistant Léger / Rapide",
        "rag":                    "📝 Synthèse & RAG",
        "code":                   "💻 Code & Dev",
        "reasoning":              "🧩 Raisonnement & Logique",
        "math_stem":              "📐 Maths & Sciences",
        "tool_calling":           "🛠️ Agents & Outils",
        "routing_classification": "🔀 Routage & Classification",
        "edge_on_device":         "📱 Edge / Embarqué",
        "enterprise":             "🏢 Entreprise & Conformité",
        "educational_tutor":      "🎓 Tutorat & Pédagogie"
    }

    doc_tab1, doc_tab2, doc_tab3 = st.tabs(["🤖 Catalogue & Filtres", "☁️ Mode Hybride", "🌱 Méthodologie Green IT"])

    with doc_tab1:
        st.markdown("#### 🔍 Trouver le modèle idéal")
        
        # --- 2. COLLECTE DES DONNÉES BRUTES ---
        raw_langs = set()
        raw_roles = set()
        
        for family, variants in models_db.items():
            for _, config in variants.items():
                info = config.get("info", {})
                raw_langs.update(info.get("langs", []))
                raw_roles.update(info.get("role_pref", []))
        
        # --- 3. CONVERSION EN LISTES FORMATEES POUR L'UI ---
        # On utilise .get(k, k) pour garder le code brut si jamais il manque dans le dictionnaire
        fmt_lang_options = sorted([LANG_MAP.get(k, k) for k in raw_langs])
        fmt_role_options = sorted([ROLE_MAP.get(k, k) for k in raw_roles])

        # --- 4. ZONE DE FILTRAGE (WIDGETS) ---
        col_fil1, col_fil2 = st.columns(2)
        with col_fil1:
            sel_langs_fmt = st.multiselect("🌍 Filtrer par Langue", fmt_lang_options)
        with col_fil2:
            sel_roles_fmt = st.multiselect("🎯 Filtrer par Cas d'usage", fmt_role_options)

        if sel_langs_fmt or sel_roles_fmt:
            st.caption(f"ℹ️ Filtres actifs : {len(sel_langs_fmt)} langue(s), {len(sel_roles_fmt)} rôle(s).")
        
        # --- 5. LOGIQUE DE FILTRAGE ET CRÉATION DATAFRAME ---
        def _create_filtered_df(model_type_filter):
            data = []
            for family, variants in models_db.items():
                # Filtre Type (Local vs API)
                is_api_fam = "API" in family or "☁️" in family
                if (model_type_filter == "local" and is_api_fam) or (model_type_filter == "api" and not is_api_fam):
                    continue
                
                for name, config in variants.items():
                    info = config["info"]
                    # Récupération des données brutes du modèle
                    m_langs_raw = info.get("langs", [])
                    m_roles_raw = info.get("role_pref", [])

                    # Conversion en format "Joli" pour la comparaison avec le filtre et l'affichage
                    m_langs_fmt = [LANG_MAP.get(k, k) for k in m_langs_raw]
                    m_roles_fmt = [ROLE_MAP.get(k, k) for k in m_roles_raw]

                    # LOGIQUE DE FILTRAGE (Mode "ET" strict / Subset)
                    # On ne garde le modèle que si TOUS les éléments sélectionnés sont présents dans ses capacités
                    
                    # 1. Filtre Langues (ET)
                    if sel_langs_fmt and not set(sel_langs_fmt).issubset(set(m_langs_fmt)):
                        continue
                        
                    # 2. Filtre Cas d'usage (ET)
                    if sel_roles_fmt and not set(sel_roles_fmt).issubset(set(m_roles_fmt)):
                        continue

                    data.append({
                        "Famille": family,
                        "Modèle": name,
                        "Langues": ", ".join(m_langs_fmt),
                        "Rôles Clés": ", ".join(m_roles_fmt),
                        "Description": info["desc"],
                        "Taille": f"{info['disk']} Go" if "disk" in info else "N/A",
                        "Params Totaux": f"{info['params_tot']}B",
                        "Params Actifs": f"{info['params_act']}B",
                    })
            return pd.DataFrame(data)

        # --- 6. AFFICHAGE DES TABLEAUX ---
        
        st.markdown("##### 🏠 Modèles Locaux (Edge)")
        df_local = _create_filtered_df("local")
        
        if not df_local.empty:
            st.dataframe(
                df_local, 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "Langues": st.column_config.TextColumn("Langues", width="medium"),
                    "Rôles Clés": st.column_config.TextColumn("Rôles Recommandés", width="medium"),
                    "Description": st.column_config.TextColumn("Description", width="large"),
                    "Taille": st.column_config.TextColumn("Poids", width="small"),
                    # 👇 CONFIGURATION VISUELLE ICI
                    "Params Totaux": st.column_config.TextColumn("Params Tot.", width="small"),
                    "Params Actifs": st.column_config.TextColumn("Params Act.", width="small"),
                }
            )
        else:
            st.warning("Aucun modèle local ne correspond aux filtres.")
        
        st.divider()
        
        st.markdown("##### ☁️ Modèles Cloud (Comparaison)")
        df_api = _create_filtered_df("api")
        if not df_api.empty:
            st.dataframe(
                df_api, 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "Langues": st.column_config.TextColumn("Langues", width="medium"),
                    "Rôles Clés": st.column_config.TextColumn("Rôles Recommandés", width="medium"),
                    "Description": st.column_config.TextColumn("Description", width="large"),
                    "Taille": st.column_config.TextColumn("Poids", width="small"),
                    # 👇 CONFIGURATION VISUELLE ICI
                    "Params Totaux": st.column_config.TextColumn("Params Tot.", width="small"),
                    "Params Actifs": st.column_config.TextColumn("Params Act.", width="small"),
                }
            )
        else:
            st.info("Aucun modèle cloud ne correspond aux filtres.")

    # --- CONTENU STATIQUE (Doc Tabs 2 & 3 inchangés) ---
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

def render_config_tab(models_db):
    """Onglet 9 : Configuration & Hardware"""
    
    st.markdown("### ⚙️ Configuration & Hardware")
    
    # --- 1. TABLEAU HARDWARE ---
    st.markdown("#### 🖥️ Votre Machine")
    # Récupération des données (format liste de dicts maintenant)
    specs_data = get_hardware_specs()
    df_specs = pd.DataFrame(specs_data)
    
    st.dataframe(
        df_specs, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "Composant": st.column_config.TextColumn("Composant", width="small"),
            "Détail": st.column_config.TextColumn("Valeur Technique", width="medium"),
            "Rôle": st.column_config.TextColumn("💡 À quoi ça sert ?", width="large"),
        }
    )
    
    # Récupération RAM totale pour les calculs (en float)
    mem_total_gb = psutil.virtual_memory().total / (1024**3)

    # --- 2. TABLEAU PERFORMANCE ---
    st.markdown("#### 🚀 Estimation de Performance (Locales)")
    
    perf_data = []
    
    # On boucle uniquement sur les modèles LOCAUX
    for family, variants in models_db.items():
        # On saute les catégories cloud
        if "API" in family or "Mistral" in family: continue 
        
        for name, conf in variants.items():
            if conf["type"] == "local":
                size_gb = conf["info"]["disk"]
                est_str, est_val = estimate_model_performance(size_gb, mem_total_gb)
                
                # Petit indicateur visuel
                status = "🟢 Fluide"
                if est_val < 10: status = "🟠 Lent"
                if est_val < 1: status = "🔴 Critique"
                
                perf_data.append({
                    "Famille": family.replace("🏠 ", ""), # On retire l'emoji pour la lisibilité
                    "Modèle": name,
                    "Poids (Go)": f"{size_gb} Go",
                    "Estimation Vitesse": est_str,
                    "Statut": status
                })
    
    if perf_data:
        df_perf = pd.DataFrame(perf_data)
        st.dataframe(
            df_perf, 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "Statut": st.column_config.TextColumn("Verdict", width="small")
            }
        )
    else:
        st.info("Aucun modèle local configuré pour l'estimation.")

    # --- 3. EXPLICATION ---
    with st.expander("ℹ️ Comment est calculée cette estimation ?"):
        st.markdown("""
        **La "Physique" des LLM Locaux :**
        Sur un CPU, la vitesse de génération de texte est rarement limitée par la puissance de calcul pur (GFLOPS), 
        mais par la **Bande Passante Mémoire** (Memory Bandwidth).
        
        Le processeur doit lire l'intégralité du modèle en RAM pour générer *chaque* mot (token).
        
        **La Formule utilisée :**
        $$
        \\text{Vitesse (t/s)} \\approx \\frac{\\text{Bande Passante (Go/s)}}{\\text{Taille Modèle (Go)}}
        $$
        
        *Nous utilisons une hypothèse de bande passante moyenne de **30 Go/s** (Standard DDR4/DDR5 Laptop).*
        * *Exemple :* Un modèle de **3 Go** sur une RAM à **30 Go/s** tournera à environ **10 t/s**.
        * *Note :* Si le modèle dépasse la RAM physique disponible, la vitesse chute drastiquement (Swap disque).
        """)