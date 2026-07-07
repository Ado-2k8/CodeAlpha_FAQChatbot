"""
Interface Streamlit pour le Chatbot FAQ.
Lancer avec : streamlit run app.py
"""
import streamlit as st

from chatbot import FAQChatbot

st.set_page_config(page_title="Chatbot FAQ", page_icon="🤖", layout="centered")

st.title("🤖 Chatbot FAQ")
st.caption("Posez une question, le bot cherche la réponse la plus proche dans la base de FAQ (TF-IDF + similarité cosinus).")


@st.cache_resource
def load_bot():
    return FAQChatbot()


bot = load_bot()

if "history" not in st.session_state:
    st.session_state.history = []

with st.sidebar:
    st.header("ℹ️ À propos")
    st.write(f"Base de connaissances : **{len(bot.faqs)} questions/réponses**")
    st.write("Technique : préprocessing NLTK (tokenisation, stopwords, lemmatisation) "
             "+ vectorisation TF-IDF hybride (mots + n-grammes de caractères) "
             "+ similarité cosinus.")
    if st.button("🗑️ Effacer la conversation"):
        st.session_state.history = []
        st.rerun()

# Affichage de l'historique
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg["role"] == "assistant" and msg.get("score") is not None:
            st.caption(f"Confiance : {msg['score']:.0%}")

# Saisie utilisateur
user_input = st.chat_input("Écrivez votre question ici...")

if user_input:
    st.session_state.history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    answer, matched_question, score = bot.get_response(user_input)

    with st.chat_message("assistant"):
        st.write(answer)
        if matched_question:
            st.caption(f"Confiance : {score:.0%} · Question FAQ correspondante : *{matched_question}*")

    st.session_state.history.append(
        {"role": "assistant", "content": answer, "score": score if matched_question else None}
    )
