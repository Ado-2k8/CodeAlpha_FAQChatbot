"""
Modern Streamlit interface for the FAQ Chatbot.
Run with: streamlit run app.py
"""
import html
import json
import time
from pathlib import Path

import streamlit as st
from streamlit.components.v1 import html as components_html

from chatbot import FAQChatbot

st.set_page_config(page_title="FAQ Chatbot", page_icon="", layout="wide")

HISTORY_PATH = Path(__file__).parent / "data" / "chat_history.json"


def get_theme_css(theme: str) -> str:
    if theme == "light":
        return """
        <style>
        :root { color-scheme: light; --bg-1: #f8fafc; --bg-2: #eef2ff; --panel: #ffffff; --text: #0f172a; --muted: #475569; --sidebar-text: #0b1220; --primary-1: #3b82f6; --primary-2: #2563eb; }
        [data-testid="stAppViewContainer"] { background: linear-gradient(135deg, var(--bg-1) 0%, var(--bg-2) 45%, var(--bg-1) 100%); }
        [data-testid="stSidebar"] { background: linear-gradient(180deg, var(--panel) 0%, var(--bg-1) 100%); border-right: 1px solid rgba(15, 23, 42, 0.06); color: var(--sidebar-text) !important; }

        /* Layout padding to make room for a fixed input area and avoid top header overlap */
        .block-container { padding-top: 72px; padding-bottom: 130px; }

        /* ensure title has breathing room beneath the top chrome */
        .main-title { color: var(--text); font-size: 1.8rem; font-weight: 700; margin-top: 8px; }
        .subtle-text { color: var(--muted); font-size: 0.95rem; }

        /* Chat rows & avatars */
        .chat-row { display:flex; gap:0.6rem; align-items:flex-end; margin-bottom:0.6rem; }
        .chat-row.user { justify-content:flex-end; }
        .avatar { width:36px; height:36px; border-radius:50%; display:inline-flex; align-items:center; justify-content:center; font-size:16px; color:white; background: linear-gradient(135deg, var(--primary-1), var(--primary-2)); flex-shrink:0; }
        .assistant-avatar { background: linear-gradient(135deg, #0ea5a3, #06b6d4); color: white; }
        .user-avatar { background: linear-gradient(135deg, var(--primary-1), var(--primary-2)); color: white; }

        .chat-bubble { padding:0.8rem 0.95rem; border-radius:14px; line-height:1.5; box-shadow: 0 8px 20px rgba(15,23,42,0.06); max-width:86%; white-space:pre-wrap; }
        .user-bubble { background: linear-gradient(135deg, var(--primary-1), var(--primary-2)); color: #fff; border-bottom-right-radius:6px; }
        .assistant-bubble { background: #fff; color: var(--text); border-bottom-left-radius:6px; border:1px solid rgba(15,23,42,0.03); }

        .faq-button { border:1px solid rgba(15,23,42,0.04); border-radius:12px; padding:0.65rem 0.8rem; margin-bottom:0.4rem; background: transparent; color: var(--sidebar-text); text-align:left; }

        /* Sidebar readability fixes: ensure numbers, labels and captions contrast */
        [data-testid="stSidebar"] { color: var(--sidebar-text) !important; }
        [data-testid="stSidebar"] * { color: inherit !important; }
        /* Streamlit metric / number selectors (best-effort) */
        [data-testid="stSidebar"] .stMetric, [data-testid="stSidebar"] .stMetricValue, [data-testid="stSidebar"] .stMetricDelta, [data-testid="stSidebar"] .stMetricLabel, [data-testid="stSidebar"] .stMetric > div { color: var(--sidebar-text) !important; background: transparent !important; }
        [data-testid="stSidebar"] label, [data-testid="stSidebar"] .stCheckbox { color: var(--sidebar-text) !important; opacity: 1 !important; }

        /* Force metric numbers to a darker shade and remove background highlights */
        [data-testid="stSidebar"] .stMetricValue {
            background: transparent !important;
            color: var(--sidebar-text) !important;
            box-shadow: none !important;
        }
        [data-testid="stSidebar"] .stMetricLabel { color: rgba(11,18,32,0.85) !important; }

        /* Typing indicator */
        .typing-dots { display:inline-flex; gap:0.3rem; align-items:center; padding:0.45rem 0.7rem; border-radius:999px; background: rgba(255,255,255,0.95); }
        .typing-dots span { width:8px; height:8px; border-radius:50%; background:#64748b; animation:bounce 1.2s infinite ease-in-out; }
        .typing-dots span:nth-child(2) { animation-delay:0.12s; }
        .typing-dots span:nth-child(3) { animation-delay:0.24s; }
        @keyframes bounce { 0%,80%,100% { transform:translateY(0); opacity:0.4; } 40% { transform:translateY(-4px); opacity:1; } }

        /* Input area styling when using Streamlit's chat_input / text_input */
        .stChatInput, .stTextInput { border-radius:12px !important; }
        .stButton > button { border-radius:10px !important; }

        /* Ensure native chat input is readable in light mode */
        textarea[placeholder="Type your question here..."], input[placeholder="Type your question here..."] {
            background: #ffffff !important;
            color: var(--text) !important;
            padding: 12px 18px !important;
            border-radius: 999px !important;
            box-shadow: 0 8px 20px rgba(15,23,42,0.04) !important;
            border: 1px solid rgba(15,23,42,0.06) !important;
        }
        /* try to style the send button if present */
        button[title="Send"], button[aria-label="Send"] { border-radius: 999px !important; background: linear-gradient(135deg, #3b82f6, #2563eb) !important; color: white !important; }

        /* Ensure captions and subtle text contrast */
        .stCaption, .st-caption, .caption, .subtle-text { color: var(--muted) !important; }

        /* Custom starter info box to ensure readable text on light-blue background */
        .starter-info {
            background: linear-gradient(180deg, rgba(59,130,246,0.12), rgba(96,165,250,0.12));
            color: #0f172a !important;
            padding: 14px 18px;
            border-radius: 12px;
            border: 1px solid rgba(59,130,246,0.18);
            box-shadow: 0 6px 18px rgba(15,23,42,0.04);
            font-size: 0.95rem;
        }

        </style>
        """

    return """
    <style>
    :root { color-scheme: dark; --bg-a: #07111f; --bg-b: #111827; --panel: #0f172a; --muted: #94a3b8; --accent-1: #06b6d4; --accent-2: #0ea5a3; --primary-1: #3b82f6; --primary-2: #2563eb; }
    [data-testid="stAppViewContainer"] { background: linear-gradient(135deg, var(--bg-a) 0%, var(--bg-b) 45%, var(--panel) 100%); }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, var(--bg-b) 0%, var(--panel) 100%); border-right: 1px solid rgba(255,255,255,0.06); }

    /* Make room for the fixed input area and avoid top chrome overlap */
    .block-container { padding-top: 72px; padding-bottom: 140px; }

    /* ensure title isn't hidden under the Streamlit top bar */
    .main-title { font-size: 1.9rem; font-weight:700; margin-top:8px; margin-bottom:0.2rem; color: #f8fafc; }
    .subtle-text { color: var(--muted); font-size:0.95rem; }

    /* Chat rows & avatars */
    .chat-row { display:flex; gap:0.6rem; align-items:flex-end; margin-bottom:0.6rem; }
    .chat-row.user { justify-content:flex-end; }
    .avatar { width:36px; height:36px; border-radius:50%; display:inline-flex; align-items:center; justify-content:center; font-size:16px; color:white; background: linear-gradient(135deg, var(--primary-1), var(--primary-2)); flex-shrink:0; }
    .assistant-avatar { background: linear-gradient(135deg, var(--accent-1), var(--accent-2)); }
    .user-avatar { background: linear-gradient(135deg, var(--primary-1), var(--primary-2)); }

    .chat-bubble { padding:0.8rem 0.95rem; border-radius:14px; line-height:1.5; box-shadow: 0 12px 30px rgba(0,0,0,0.45); max-width:86%; white-space:pre-wrap; }
    .user-bubble { background: linear-gradient(135deg, var(--primary-1), var(--primary-2)); color: #fff; border-bottom-right-radius:6px; }
    .assistant-bubble { background: rgba(255,255,255,0.04); color: #e6eef8; border-bottom-left-radius:6px; border:1px solid rgba(255,255,255,0.03); }

    .faq-button { border:1px solid rgba(255,255,255,0.04); border-radius:12px; padding:0.65rem 0.8rem; margin-bottom:0.4rem; background: transparent; color: #e6eef8; text-align:left; }

    /* Typing indicator */
    .typing-dots { display:inline-flex; gap:0.3rem; align-items:center; padding:0.45rem 0.7rem; border-radius:999px; background: rgba(255,255,255,0.06); }
    .typing-dots span { width:8px; height:8px; border-radius:50%; background:#94a3b8; animation:bounce 1.2s infinite ease-in-out; }
    .typing-dots span:nth-child(2) { animation-delay:0.12s; }
    .typing-dots span:nth-child(3) { animation-delay:0.24s; }
    @keyframes bounce { 0%,80%,100% { transform:translateY(0); opacity:0.35; } 40% { transform:translateY(-4px); opacity:1; } }

    /* Input area styling */
    .stChatInput, .stTextInput { border-radius:12px !important; }
    .stButton > button { border-radius:10px !important; }

    /* Custom starter info box for dark theme (subtle light text on dark translucent bg) */
    .starter-info {
        background: rgba(255,255,255,0.03);
        color: #e6eef8 !important;
        padding: 14px 18px;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.04);
        box-shadow: 0 6px 18px rgba(0,0,0,0.35);
        font-size: 0.95rem;
    }

    </style>
    """


@st.cache_resource(show_spinner=False)
def load_bot():
    return FAQChatbot()


def load_history() -> list[dict]:
    if HISTORY_PATH.exists():
        try:
            with HISTORY_PATH.open("r", encoding="utf-8") as file:
                loaded = json.load(file)
                if isinstance(loaded, list):
                    return loaded
        except (json.JSONDecodeError, OSError):
            return []
    return []


def save_history() -> None:
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with HISTORY_PATH.open("w", encoding="utf-8") as file:
        json.dump(st.session_state.history, file, ensure_ascii=False, indent=2)


bot = load_bot()

if "theme" not in st.session_state:
    st.session_state.theme = "dark"

if "history" not in st.session_state:
    st.session_state.history = load_history()

st.markdown(get_theme_css(st.session_state.theme), unsafe_allow_html=True)


def render_message(message: dict) -> None:
    """
    Render a chat row with a small SVG avatar and a styled bubble.
    """
    role = message["role"]
    content = message["content"]
    bubble_class = "user-bubble" if role == "user" else "assistant-bubble"
    safe_content = html.escape(content).replace("\n", "<br>")

    if role == "user":
        # User: bubble on the right, avatar to the right
        markup = f'''
        <div class="chat-row user">
            <div class="chat-bubble {bubble_class}">{safe_content}</div>
            <div class="avatar user-avatar" aria-hidden="true">
                <svg viewBox="0 0 24 24" width="20" height="20" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                    <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4z" fill="white" />
                    <path d="M4 20c0-2.21 3.58-4 8-4s8 1.79 8 4v1H4v-1z" fill="white" />
                </svg>
            </div>
        </div>
        '''
        st.markdown(markup, unsafe_allow_html=True)
    else:
        # Assistant: avatar to the left, bubble on the left
        markup = f'''
        <div class="chat-row">
            <div class="avatar assistant-avatar" aria-hidden="true">
                <svg viewBox="0 0 24 24" width="20" height="20" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                    <rect x="3" y="4" width="18" height="12" rx="2" fill="white" />
                    <circle cx="8.5" cy="9" r="1" fill="#0f172a" />
                    <circle cx="15.5" cy="9" r="1" fill="#0f172a" />
                    <rect x="9" y="13.5" width="6" height="1.5" rx="0.75" fill="#0f172a" />
                </svg>
            </div>
            <div class="chat-bubble {bubble_class}">{safe_content}</div>
        </div>
        '''
        st.markdown(markup, unsafe_allow_html=True)
        if message.get("score") is not None:
            st.caption(f"Confidence: {message['score']:.0%} · Related FAQ: *{message['matched_question']}*")


def render_typing_indicator(container) -> None:
    with container:
        st.markdown(
            "<div class='typing-dots'><span></span><span></span><span></span></div>",
            unsafe_allow_html=True,
        )


def handle_user_message(user_input: str) -> None:
    if not user_input or not user_input.strip():
        return

    cleaned_input = user_input.strip()
    st.session_state.history.append({"role": "user", "content": cleaned_input})
    save_history()
    render_message(st.session_state.history[-1])

    # show typing indicator in a placeholder while computing response
    typing_placeholder = st.empty()
    render_typing_indicator(typing_placeholder)
    time.sleep(0.6)
    typing_placeholder.empty()

    answer, matched_question, score = bot.get_response(cleaned_input)

    # render assistant message with avatar + bubble
    assistant_markup = f'''
    <div class="chat-row">
        <div class="avatar assistant-avatar" aria-hidden="true">
            <svg viewBox="0 0 24 24" width="20" height="20" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                <rect x="3" y="4" width="18" height="12" rx="2" fill="white" />
                <circle cx="8.5" cy="9" r="1" fill="#0f172a" />
                <circle cx="15.5" cy="9" r="1" fill="#0f172a" />
                <rect x="9" y="13.5" width="6" height="1.5" rx="0.75" fill="#0f172a" />
            </svg>
        </div>
        <div class="chat-bubble assistant-bubble">{html.escape(answer).replace("\\n","<br>")}</div>
    </div>
    '''
    st.markdown(assistant_markup, unsafe_allow_html=True)

    if matched_question:
        st.caption(f"Confidence: {score:.0%} · Related FAQ: *{matched_question}*")
    else:
        st.caption("I could not find a strong match. Try rephrasing your question.")

    st.session_state.history.append(
        {
            "role": "assistant",
            "content": answer,
            "score": score if matched_question else None,
            "matched_question": matched_question,
        }
    )
    save_history()


with st.sidebar:
    st.markdown("## Quick topics")
    st.caption("Select a common question to get started quickly.")

    for index, faq in enumerate(bot.faqs[:8]):
        if st.button(faq["question"], key=f"faq_{index}", use_container_width=True):
            handle_user_message(faq["question"])

    st.divider()
    st.markdown("## Appearance")
    dark_mode = st.checkbox("Dark mode (Recommended)", value=st.session_state.theme == "dark")
    st.session_state.theme = "dark" if dark_mode else "light"
    st.caption("Theme and conversation history are saved automatically.")

    st.divider()
    st.markdown("## Knowledge base")
    st.metric("FAQ entries", len(bot.faqs))
    st.caption("Technique: NLTK preprocessing + TF-IDF + cosine similarity")

    # Clear conversation with confirmation
    if "clear_confirm" not in st.session_state:
        st.session_state.clear_confirm = False

    if st.session_state.clear_confirm:
        st.warning("Are you sure you want to clear the conversation? This will remove the local session history.")
        c1, c2 = st.columns([1,1])
        if c1.button("Yes, clear", key="confirm_clear"):
            st.session_state.history = []
            save_history()
            st.session_state.clear_confirm = False
            st.success("Conversation cleared.")
            st.experimental_rerun()
        if c2.button("Cancel", key="cancel_clear"):
            st.session_state.clear_confirm = False
    else:
        if st.button("Clear conversation", use_container_width=True):
            st.session_state.clear_confirm = True


st.markdown('<div class="main-title">Smart FAQ Assistant</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtle-text">Ask anything about returns, shipping, payments, support, or account issues.</div>',
    unsafe_allow_html=True,
)

if not st.session_state.history:
    # Use a custom styled info box so text is always readable in both themes
    st.markdown(
        '<div class="starter-info">Start by typing a question below or choosing one of the suggested topics in the sidebar.</div>',
        unsafe_allow_html=True,
    )

for message in st.session_state.history:
    render_message(message)

components_html(
    """
    <script>
    (function() {
        // Smooth auto-scroll when the DOM changes (new messages arrive).
        function scrollToBottom(smooth) {
            const root = document.scrollingElement || document.documentElement || document.body;
            try {
                root.scrollTo({ top: root.scrollHeight, behavior: smooth ? 'smooth' : 'auto' });
            } catch (e) {
                root.scrollTop = root.scrollHeight;
            }
        }

        // Initial jump to bottom after page load
        window.addEventListener('load', function() { setTimeout(function(){ scrollToBottom(false); }, 60); });

        // Observe changes in the main app container and scroll when children change
        const target = document.querySelector('main') || document.querySelector('[data-testid="stAppViewContainer"]') || document.body;
        if (target) {
            const observer = new MutationObserver(function(mutations) {
                for (const m of mutations) {
                    if (m.addedNodes && m.addedNodes.length > 0) {
                        scrollToBottom(true);
                        break;
                    }
                }
            });
            observer.observe(target, { childList: true, subtree: true });
        }
    })();
    </script>
    """,
    height=0,
)

# keep default Streamlit chat_input as a robust fallback
# The custom footer has been removed; native st.chat_input is used exclusively.
user_input = st.chat_input("Type your question here...")

if user_input:
    handle_user_message(user_input)
