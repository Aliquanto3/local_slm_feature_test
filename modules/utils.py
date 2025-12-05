import os
import time
import pypdf
from io import StringIO
import streamlit as st

# Gestion des imports optionnels (évite de planter si libs manquantes)
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

# --- FONCTION DE CHARGEMENT DE MODÈLE (CACHÉE) ---
@st.cache_resource(show_spinner="Chargement du modèle en mémoire RAM...", max_entries=1)
def load_local_llm(path, ctx_size):
    """Charge un modèle GGUF en mémoire avec Llama-cpp"""
    abs_path = os.path.abspath(path)
    print(f"\n🔄 [DEBUG] Chargement : {abs_path}")
    
    if not HAS_LOCAL_LIB:
        raise ImportError("Librairie `llama-cpp-python` manquante.")
        
    try:
        # n_gpu_layers=-1 permet d'utiliser le GPU si dispo/configuré, sinon CPU
        return Llama(model_path=abs_path, n_ctx=min(ctx_size, 8192), n_gpu_layers=-1, verbose=True)
    except Exception as e:
        raise RuntimeError(f"Erreur Llama-cpp : {str(e)}")

# --- HELPERS FICHIERS ---
def count_tokens_local(text: str, llm_instance) -> int:
    """Compte les tokens pour estimer la charge"""
    if not text or not llm_instance: return 0
    try: return len(llm_instance.tokenize(text.encode("utf-8")))
    except: return 0

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
def generate_stream(model_type, model_conf, llm_local, api_key, messages, temperature=0.7, max_tokens=1024, top_p=0.9, top_k=40):
    """
    Fonction unique pour gérer l'inférence (Streamée)
    Compatible : Mistral API & Llama.cpp Local
    Retourne : Le texte final généré (tout en mettant à jour l'UI via un placeholder passé en arg si besoin, 
               mais ici on gère l'UI dans la vue, donc on va faire un générateur python)
    """
    # Note: Pour simplifier l'intégration existante dans votre app.py,
    # cette fonction va gérer l'affichage direct via st.empty() comme avant.
    
    response_placeholder = st.empty()
    
    # Check Sécurité
    if model_type == "local" and llm_local is None:
        response_placeholder.error("❌ Modèle local non chargé.")
        return ""

    response_placeholder.markdown("⏳ _Réflexion..._")
    
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
        # Estimation tokens input (Approximatif)
        prompt_str = " ".join([m["content"] for m in messages])
        input_tokens = count_tokens_local(prompt_str, llm_local)
        
        try:
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
            # FIX AUTOMATIQUE : Si le modèle (ex: Gemma) ne supporte pas le role "system"
            if "System role not supported" in str(e):
                # On fusionne le system prompt dans le premier message user
                system_msg = next((m for m in messages if m['role'] == 'system'), None)
                new_msgs = [m for m in messages if m['role'] != 'system']
                
                if system_msg and new_msgs and new_msgs[0]['role'] == 'user':
                    new_msgs[0]['content'] = f"Context/Instruction: {system_msg['content']}\n\nUser Query: {new_msgs[0]['content']}"
                    
                    try:
                        # Seconde tentative avec le prompt fusionné
                        stream = llm_local.create_chat_completion(
                            messages=new_msgs, stream=True, temperature=temperature, 
                            top_p=top_p, top_k=top_k, max_tokens=max_tokens
                        )
                        for chunk in stream:
                            if "content" in chunk["choices"][0]["delta"]:
                                full_response += chunk["choices"][0]["delta"]["content"]
                                output_tokens += 1
                                response_placeholder.markdown(full_response + "▌")
                    except Exception as e2:
                        response_placeholder.error(f"Erreur Fatale (Fallback): {e2}")
                        return ""
            else:
                response_placeholder.error(f"Erreur Template Chat : {e}")
                return ""
        except Exception as e:
            response_placeholder.error(f"Erreur Inférence : {e}")
            return ""

    # --- METRICS FINALES ---
    duration = time.time() - start_time
    speed = output_tokens / duration if duration > 0 else 0
    
    response_placeholder.markdown(full_response)
    
    # Affichage des métriques en bas de réponse
    cols = st.columns(4)
    cols[0].info(f"⏱️ {duration:.2f} s")
    cols[1].info(f"⚡ {speed:.1f} t/s")
    cols[2].info(f"📥 {input_tokens} tok")
    cols[3].info(f"📤 {output_tokens} tok")
    
    return full_response