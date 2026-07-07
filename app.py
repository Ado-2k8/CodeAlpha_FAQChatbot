"""
Streamlit interface for the FAQ Chatbot.
Run with: streamlit run app.py
"""
import streamlit as st

from chatbot import FAQChatbot

st.set_page_config(page_title="FAQ Chatbot", page_icon="🤖", layout="centered")

st.title("🤖 FAQ Chatbot")
st.caption("Ask a question, the bot finds the closest answer in the FAQ database (TF-IDF + cosine similarity).")


@st.cache_resource
def load_bot():
    return FAQChatbot()


bot = load_bot()

if "history" not in st.session_state:
    st.session_state.history = []

with st.sidebar:
    st.header("ℹ️ About")
    st.write(f"Knowledge base: **{len(bot.faqs)} questions/answers**")
    st.write("Technique: NLTK preprocessing (tokenization, stopword removal, lemmatization) "
             "+ hybrid TF-IDF vectorization (words + character n-grams) "
             "+ cosine similarity.")
    if st.button("🗑️ Clear conversation"):
        st.session_state.history = []
        st.rerun()

# Display chat history
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg["role"] == "assistant" and msg.get("score") is not None:
            st.caption(f"Confidence: {msg['score']:.0%}")

# User input
user_input = st.chat_input("Type your question here...")

if user_input:
    st.session_state.history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    answer, matched_question, score = bot.get_response(user_input)

    with st.chat_message("assistant"):
        st.write(answer)
        if matched_question:
            st.caption(f"Confidence: {score:.0%} · Matched FAQ question: *{matched_question}*")

    st.session_state.history.append(
        {"role": "assistant", "content": answer, "score": score if matched_question else None}
    )
