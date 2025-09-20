import streamlit as st
import requests
import json
import time
from typing import Dict, Any

# Configuration du chatbot N8N
WEBHOOK_URL = "https://wip.app.n8n.cloud/webhook/spotibot"

def send_message_to_chatbot(message: str) -> Dict[str, Any]:
    """
    Envoie un message au chatbot N8N et récupère la réponse
    """
    try:
        payload = {
            "message": message  # ← CHANGÉ ICI (était "chatInput")
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            WEBHOOK_URL,
            json=payload,
            headers=headers,
            timeout=60
        )
        
        if response.status_code == 200:
            try:
                # Nettoyer la réponse (enlever le '=' au début)
                response_text = response.text.strip()
                if response_text.startswith('='):
                    response_text = response_text[1:]
                
                # Parser le JSON
                data = json.loads(response_text)
                return {
                    "success": True,
                    "data": data
                }
            except json.JSONDecodeError as e:
                return {
                    "success": False,
                    "error": f"Erreur de parsing JSON: {str(e)}"
                }
        else:
            return {
                "success": False,
                "error": f"Erreur HTTP {response.status_code}: {response.text}"
            }
            
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Timeout: Le chatbot met trop de temps à répondre"
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Erreur de connexion: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Erreur inattendue: {str(e)}"
        }

def display_chat_interface():
    """
    Interface de chat dans Streamlit
    """
    st.header("Explore William's Spotify Data")
    
    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        welcome_msg = {
            "role": "assistant",
            "content": """Welcome! I'm Spotibot. 

I can analyze and visualize William's Spotify data to reveal:
- His favorite artists and music genres
- The evolution of his musical taste over time
- Audio features of his tracks (energy, tempo, valence...)
- His listening patterns (hours, days, seasonality)
- Surprising insights about his personality through music

**Sample questions:** 
- "What are the top 10 most played artists?"
- "How do his music tastes evolve throughout the year?"
- "What time of day does William listen to music most?"
- "Show me the energy distribution of his favorite tracks"

Feel free to explore the data to get to know William better!""",
            "timestamp": time.time()
        }
        st.session_state.chat_history.append(welcome_msg)
    
    # Afficher l'historique du chat
    for message in st.session_state.chat_history:
        if message["role"] == "assistant":
            with st.chat_message("assistant", avatar="https://jdvrbnajcupzrsneacbm.supabase.co/storage/v1/object/public/Spotibot_img/spotibot-icon-purple.png"):
                st.write(message["content"])
        else:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        
        if "chart_data" in message and message["chart_data"]:
            try:
                st.json(message["chart_data"])
            except Exception as e:
                st.error(f"Erreur d'affichage du graphique: {e}")
    
    # Zone de saisie du message
    if prompt := st.chat_input("Type your message here..."):
        # Ajouter le message utilisateur
        user_message = {
            "role": "user",
            "content": prompt,
            "timestamp": time.time()
        }
        st.session_state.chat_history.append(user_message)
        
        # Afficher le message utilisateur
        with st.chat_message("user"):
            st.write(prompt)
        
        # Réponse du bot
        with st.chat_message("assistant", avatar="https://jdvrbnajcupzrsneacbm.supabase.co/storage/v1/object/public/Spotibot_img/spotibot-icon-purple.png"):
            with st.spinner("Processing..."):
                response = send_message_to_chatbot(prompt)
                
                if response["success"]:
                    try:
                        bot_data = response["data"]
                        
                        if isinstance(bot_data, dict):
                            bot_text = bot_data.get("text", "Réponse reçue sans texte")
                            chart_data = bot_data.get("chart", None)
                        else:
                            bot_text = str(bot_data)
                            chart_data = None
                        
                        st.write(bot_text)
                        
                        if chart_data:
                            try:
                                st.json(chart_data)
                            except Exception as e:
                                st.error(f"Erreur d'affichage du graphique: {e}")
                        
                        assistant_message = {
                            "role": "assistant",
                            "content": bot_text,
                            "chart_data": chart_data,
                            "timestamp": time.time()
                        }
                        st.session_state.chat_history.append(assistant_message)
                        
                    except Exception as e:
                        error_msg = f"Erreur: {str(e)}"
                        st.error(error_msg)
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": error_msg,
                            "timestamp": time.time()
                        })
                else:
                    error_msg = f"Erreur: {response['error']}"
                    st.error(error_msg)
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": error_msg,
                        "timestamp": time.time()
                    })

def main():
    """
    Fonction principale de l'application Streamlit
    """
    st.set_page_config(
    page_title="Spotibot",
    page_icon="🎵"
    # layout par défaut = "centered" (pas besoin de le spécifier)
)
    
    # CSS personnalisé pour les polices et les headers
    st.markdown("""
    <style>
    /* Import des polices */
    @import url('https://fonts.googleapis.com/css2?family=Tiempos+Text:wght@400;500;600&display=swap');
    
    /* Note: Styrene nécessite une licence commerciale. 
       J'utilise Work Sans comme alternative open-source similaire */
    @import url('https://fonts.googleapis.com/css2?family=Work+Sans:wght@400;500;600;700&display=swap');
    
    /* Headers avec Styrene/Work Sans et couleur personnalisée */
    h1, h2, h3 {
        font-family: 'Work Sans', sans-serif !important;
        color: #D97757 !important;
        font-weight: 600 !important;
    }
    
    /* Corps de texte avec Tiempos (ou fallback serif) */
    p, .stMarkdown, .stText, div[data-testid="stMarkdownContainer"] {
        font-family: 'Tiempos Text', Georgia, serif !important;
    }
    
    /* Messages du chat */
    .stChatMessage p {
        font-family: 'Tiempos Text', Georgia, serif !important;
    }
    
    /* Input du chat */
    .stChatInput textarea {
        font-family: 'Tiempos Text', Georgia, serif !important;
    }
    
    /* Boutons avec la police des titres */
    .stButton button {
        font-family: 'Work Sans', sans-serif !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Interface de chat
    display_chat_interface()

if __name__ == "__main__":
    main()
