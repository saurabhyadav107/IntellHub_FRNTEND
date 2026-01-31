import streamlit as st
import requests
import json
import re
from datetime import datetime
import time
import base64

# ============================
# Page configuration
# ============================
st.set_page_config(
    page_title="Intellhub",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================
# Advanced Custom CSS (Static Dark Mode Implementation)
# ============================
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    /* ====================================
       GLOBAL VARIABLES & ROOT SETUP
       ==================================== */
    :root {
        --primary-color: #10A37F;
        --bg-dark: #090B0F;
        --card-bg: rgba(30, 32, 40, 0.7);
        --glass-border: rgba(255, 255, 255, 0.1);
        --text-main: #E0E0E0;
        --text-muted: #A0A0A0;
        --input-bg: #1E2028;
    }

    /* ====================================
       FORCE DARK BACKGROUND EVERYWHERE
       ==================================== */
    html, body {
        background-color: #090B0F !important;
    }

    .stApp {
        background: radial-gradient(circle at 50% 0%, #1a1c24 0%, #090b0f 100%) !important;
        color: var(--text-main) !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    .stAppViewContainer {
        background: #090B0F !important;
    }

    section[data-testid="stMain"] {
        background: transparent !important;
    }

    /* ====================================
       SIDEBAR STYLING
       ==================================== */
    [data-testid="stSidebar"] {
        background-color: #0d0f14 !important;
        border-right: 1px solid var(--glass-border) !important;
    }
    
    [data-testid="stSidebar"] * {
        color: var(--text-main) !important;
    }

    /* ====================================
       TEXT ELEMENTS
       ==================================== */
    h1, h2, h3, p, span, label, .stMarkdown {
        color: var(--text-main) !important;
    }

    /* ====================================
       COMPLETE BOTTOM INPUT AREA FIX
       ==================================== */
    
    /* Target the outermost bottom container */
    [data-testid="stBottom"] {
        background-color: #090B0F !important;
    }

    /* The chat input parent wrapper */
    [data-testid="stChatInputContainer"] {
        background-color: #090B0F !important;
        border: none !important;
        padding-bottom: 2rem !important;
    }

    /* All child divs inside the container */
    [data-testid="stChatInputContainer"] > div,
    [data-testid="stChatInputContainer"] > div > div,
    [data-testid="stChatInputContainer"] > div > div > div {
        background-color: #090B0F !important;
    }

    /* The actual input box */
    [data-testid="stChatInput"] {
        background-color: #1E2028 !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 14px !important;
    }

    /* The textarea inside */
    [data-testid="stChatInput"] textarea {
        background-color: #1E2028 !important;
        color: var(--text-main) !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    /* Placeholder text */
    [data-testid="stChatInput"] textarea::placeholder {
        color: #8b90a0 !important;
    }

    /* Send button */
    [data-testid="stChatInput"] button {
        background-color: var(--primary-color) !important;
        color: white !important;
        border-radius: 8px !important;
    }

    /* Force the bottom block container */
    [data-testid="stBottomBlockContainer"],
    [data-testid="stBottomBlockContainer"] > div {
        background-color: #090B0F !important;
    }

    /* Target BaseWeb layer specifically */
    div[data-baseweb="base-input"] {
        background-color: #1E2028 !important;
    }

    /* ====================================
       EMOTION CACHE OVERRIDE
       ==================================== */
    div[class^="st-emotion-cache"],
    div[class*=" st-emotion-cache"] {
        background-color: transparent !important;
    }

    /* ====================================
       CHAT MESSAGE BUBBLES
       ==================================== */
    [data-testid="stChatMessageContainer"] {
        background-color: transparent !important;
    }

    .chat-bubble {
        padding: 1.5rem;
        border-radius: 1.2rem;
        margin-bottom: 1.2rem;
        border: 1px solid var(--glass-border);
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        animation: slideIn 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        color: var(--text-main);
    }

    @keyframes slideIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .user-bubble {
        background: linear-gradient(135deg, #2D2F39 0%, #1E2028 100%);
        margin-left: auto;
        max-width: 80%;
        border-bottom-right-radius: 0.2rem;
    }

    .assistant-bubble {
        background: var(--card-bg);
        margin-right: auto;
        max-width: 85%;
        border-left: 4px solid var(--primary-color);
        border-bottom-left-radius: 0.2rem;
    }

    .sender-meta {
        font-size: 0.75rem;
        font-weight: 700;
        margin-bottom: 0.6rem;
        display: flex;
        justify-content: space-between;
        opacity: 0.7;
        color: var(--text-muted);
    }

    /* ====================================
       HERO SECTION
       ==================================== */
    .hero-box {
        text-align: center;
        padding: 4rem 2rem;
        border-radius: 2rem;
        background: linear-gradient(180deg, rgba(16, 163, 127, 0.15) 0%, rgba(16, 163, 127, 0) 100%);
        border: 1px solid rgba(16, 163, 127, 0.2);
        margin-bottom: 3rem;
    }

    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #FFFFFF, #10A37F);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }

    /* ====================================
       BUTTON STYLING
       ==================================== */
    div.stButton > button {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    div.stButton > button:hover {
        background-color: rgba(16, 163, 127, 0.2) !important;
        border-color: var(--primary-color) !important;
        transform: translateY(-2px);
    }

    /* ====================================
       SLIDER STYLING
       ==================================== */
    .stSlider [data-baseweb="slider"] {
        background-color: transparent !important;
    }

    /* ====================================
       AGGRESSIVE NUCLEAR FIX (LAST RESORT)
       ==================================== */
    [data-testid="stChatInputContainer"] * {
        background-color: #090B0F !important;
    }

    [data-testid="stChatInput"],
    [data-testid="stChatInput"] *:not(button) {
        background-color: #1E2028 !important;
    }

    /* ====================================
       HIDE STREAMLIT BRANDING
       ==================================== */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
</style>
""",
    unsafe_allow_html=True,
)

# ============================
# API Configuration
# ============================
API_URL = "https://stagingchatbotapi.mycii.in/search"
API_KEY = ""


def extract_response_text(api_data) -> str:
    """Extract clean response text from API data."""
    if isinstance(api_data, dict):
        return api_data.get("results", json.dumps(api_data, indent=2))
    if not isinstance(api_data, str):
        return str(api_data)
    pattern = r"```json\s*(\{.*?\})\s*```"
    match = re.search(pattern, api_data, re.DOTALL)
    if match:
        try:
            parsed = json.loads(match.group(1))
            return parsed.get("results", "")
        except:
            pass
    return api_data.strip()


def call_chatbot_api(query: str, top_k: int):
    """Call the CII chatbot API with error handling."""
    payload = {"query": query, "top_k": top_k}
    try:
        response = requests.post(
            API_URL,
            headers={"accept": "application/json", "Content-Type": "application/json"},
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        return {"success": True, "data": response.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================
# Session State Initialization
# ============================
if "messages" not in st.session_state:
    st.session_state.messages = []

# ============================
# Sidebar Configuration
# ============================
with st.sidebar:
    st.markdown(
        '<div style="text-align: center; margin-bottom: 20px;">', unsafe_allow_html=True
    )
    st.image("https://i.ibb.co/4Z0ngTfD/upload.png", width=140)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### 🏛️ Knowledge Hub")
    tabs = st.radio("Navigation", ["Intelligence Chat"], label_visibility="collapsed")

    st.divider()

    st.markdown("### ⚙️ Search Settings")
    top_k = st.slider("Retrieval Depth", 5, 50, 25)

    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.caption("v2.5.0 • Enterprise Edition")

# ============================
# Main Content Logic
# ============================
if tabs == "Intelligence Chat":
    # Hero Section (shown when no messages)
    if not st.session_state.messages:
        st.markdown(
            """
        <div class="hero-box">
            <div class="hero-title">CII Intelligence Portal</div>
            <p style="font-size: 1.2rem; opacity: 0.8; color: white !important;">The definitive AI interface for Confederation of Indian Industry knowledge and economic insights.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown("### Start with a suggested query:")
        col1, col2 = st.columns(2)
        examples = [
            (
                "📈 Growth Trends",
                "Expected change in Madhya Pradesh’s GSDP share by 2047–48?",
            ),
            (
                "🌱 Sustainability",
                "Tell me about CII's Green Co rating system and ESG initiatives.",
            ),
            (
                "🏛️ Policy Insights",
                "What are the key highlights of CII's pre-budget memorandum?",
            ),
            (
                "🔧 MSME Support",
                "How is CII helping MSMEs with digital transformation?",
            ),
        ]

        for i, (label, text) in enumerate(examples):
            with col1 if i % 2 == 0 else col2:
                if st.button(
                    f"**{label}**\n\n{text}", key=f"ex_{i}", use_container_width=True
                ):
                    st.session_state.messages.append(
                        {
                            "role": "user",
                            "content": text,
                            "time": datetime.now().strftime("%H:%M"),
                        }
                    )
                    with st.spinner("Connecting to Knowledge Base..."):
                        res = call_chatbot_api(text, top_k)
                        bot_text = (
                            extract_response_text(res["data"])
                            if res["success"]
                            else f"Error: {res['error']}"
                        )
                        st.session_state.messages.append(
                            {
                                "role": "assistant",
                                "content": bot_text,
                                "time": datetime.now().strftime("%H:%M"),
                            }
                        )
                    st.rerun()

    # Chat Message Feed
    for msg in st.session_state.messages:
        is_user = msg["role"] == "user"
        st.markdown(
            f"""
        <div class="chat-bubble {'user-bubble' if is_user else 'assistant-bubble'}">
            <div class="sender-meta">
                <span>{'USER' if is_user else 'CII INTELLIGENCE'}</span>
                <span>{msg['time']}</span>
            </div>
            <div style="color: white !important;">{msg['content']}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Chat Input
    query = st.chat_input("Enter your industry research query...")
    if query:
        st.session_state.messages.append(
            {"role": "user", "content": query, "time": datetime.now().strftime("%H:%M")}
        )
        st.rerun()

# ============================
# API Call Logic (After Rerun)
# ============================
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    last_query = st.session_state.messages[-1]["content"]
    with st.spinner("Analyzing Database..."):
        res = call_chatbot_api(last_query, top_k)
        bot_text = (
            extract_response_text(res["data"])
            if res["success"]
            else f"Error: {res['error']}"
        )
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": bot_text,
                "time": datetime.now().strftime("%H:%M"),
            }
        )
    st.rerun()