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
            "chatInput": message
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            WEBHOOK_URL,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            return {
                "success": True,
                "data": response.json()
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
    st.header("🎵 Assistant Musical William")
    st.write("Posez vos questions sur les données Spotify de William !")
    
    # Initialiser l'historique du chat
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        # Message d'accueil
        welcome_msg = {
            "role": "assistant",
            "content": "Bonjour ! Je suis l'assistant musical de William. Je peux analyser ses données Spotify : artistes préférés, tendances d'écoute, découvertes musicales, etc. Que voulez-vous savoir ?",
            "timestamp": time.time()
        }
        st.session_state.chat_history.append(welcome_msg)
    
    # Afficher l'historique du chat
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            
            # Si le message contient des données de graphique, les afficher
            if "chart_data" in message and message["chart_data"]:
                try:
                    chart_data = message["chart_data"]
                    # Adapter selon le type de graphique retourné par N8N
                    st.json(chart_data)  # Pour le moment, afficher en JSON
                except Exception as e:
                    st.error(f"Erreur d'affichage du graphique: {e}")
    
    # Zone de saisie du message
    if prompt := st.chat_input("Tapez votre message ici..."):
        # Ajouter le message utilisateur à l'historique
        user_message = {
            "role": "user",
            "content": prompt,
            "timestamp": time.time()
        }
        st.session_state.chat_history.append(user_message)
        
        # Afficher le message utilisateur
        with st.chat_message("user"):
            st.write(prompt)
        
        # Afficher un spinner pendant le traitement
        with st.chat_message("assistant"):
            with st.spinner("William réfléchit..."):
                # Envoyer le message au chatbot N8N
                response = send_message_to_chatbot(prompt)
                
                if response["success"]:
                    try:
                        # Parser la réponse du chatbot
                        bot_data = response["data"]
                        
                        # Extraire le texte de réponse
                        if isinstance(bot_data, dict):
                            bot_text = bot_data.get("text", "Réponse reçue sans texte")
                            chart_data = bot_data.get("chart", None)
                        else:
                            bot_text = str(bot_data)
                            chart_data = None
                        
                        # Afficher la réponse
                        st.write(bot_text)
                        
                        # Afficher le graphique si présent
                        if chart_data:
                            try:
                                st.json(chart_data)  # À adapter selon votre format
                            except Exception as e:
                                st.error(f"Erreur d'affichage du graphique: {e}")
                        
                        # Ajouter à l'historique
                        assistant_message = {
                            "role": "assistant",
                            "content": bot_text,
                            "chart_data": chart_data,
                            "timestamp": time.time()
                        }
                        st.session_state.chat_history.append(assistant_message)
                        
                    except Exception as e:
                        error_msg = f"Erreur lors du traitement de la réponse: {str(e)}"
                        st.error(error_msg)
                        
                        # Ajouter le message d'erreur à l'historique
                        error_message = {
                            "role": "assistant",
                            "content": error_msg,
                            "timestamp": time.time()
                        }
                        st.session_state.chat_history.append(error_message)
                else:
                    error_msg = f"Erreur: {response['error']}"
                    st.error(error_msg)
                    
                    # Ajouter le message d'erreur à l'historique
                    error_message = {
                        "role": "assistant",
                        "content": error_msg,
                        "timestamp": time.time()
                    }
                    st.session_state.chat_history.append(error_message)

def main():
    """
    Fonction principale de l'application Streamlit
    """
    st.set_page_config(
        page_title="Spotify Personal Insights - Chat",
        page_icon="🎵",
        layout="wide"
    )
    
    # Interface de chat
    display_chat_interface()
    
    # Bouton pour vider l'historique (optionnel)
    if st.button("🗑️ Vider l'historique"):
        st.session_state.chat_history = []
        st.rerun()

if __name__ == "__main__":
    main()