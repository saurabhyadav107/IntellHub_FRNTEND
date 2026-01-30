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
    page_title="CII Intelligence Portal",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================
# Advanced Custom CSS (Premium Glassmorphism)
# ============================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    :root {
        --primary-color: #10A37F;
        --bg-dark: #090B0F;
        --card-bg: rgba(30, 32, 40, 0.7);
        --glass-border: rgba(255, 255, 255, 0.1);
    }

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background-color: var(--bg-dark);
        color: #E0E0E0;
    }

    .stApp {
        background: radial-gradient(circle at 50% 0%, #1a1c24 0%, #090b0f 100%);
    }

    /* Message Containers */
    .chat-bubble {
        padding: 1.5rem;
        border-radius: 1.2rem;
        margin-bottom: 1.2rem;
        border: 1px solid var(--glass-border);
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        animation: slideIn 0.4s cubic-bezier(0.16, 1, 0.3, 1);
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
    }

    /* Hero Section */
    .hero-box {
        text-align: center;
        padding: 4rem 2rem;
        border-radius: 2rem;
        background: linear-gradient(180deg, rgba(16, 163, 127, 0.15) 0%, rgba(16, 163, 127, 0) 100%);
        border: 1px solid rgba(16, 163, 127, 0.2);
        margin-bottom: 3rem;
    }

    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #FFFFFF, #10A37F);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }

    /* Input & Interactive */
    .stTextInput > div > div > input {
        background-color: #1E2028 !important;
        border-radius: 10px !important;
        border: 1px solid var(--glass-border) !important;
    }

    .example-btn {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid var(--glass-border);
        padding: 1rem;
        border-radius: 12px;
        cursor: pointer;
        transition: all 0.3s ease;
        text-align: left;
    }

    .example-btn:hover {
        background: rgba(16, 163, 127, 0.1);
        border-color: var(--primary-color);
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

# ============================
# API & Logic
# ============================
API_URL = "https://stagingchatbotapi.mycii.in/search"
# The execution environment provides the key at runtime
API_KEY = "" 

def call_imagen_api(prompt):
    """Generates an image using the Imagen 4.0 model."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-generate-001:predict?key={API_KEY}"
    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {"sampleCount": 1}
    }
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        res_json = response.json()
        b64_data = res_json["predictions"][0]["bytesBase64Encoded"]
        return f"data:image/png;base64,{b64_data}"
    except Exception as e:
        return None

def extract_response_text(api_data) -> str:
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
        except: pass
    return api_data.strip()

def call_chatbot_api(query: str, top_k: int):
    payload = {"query": query, "top_k": top_k}
    try:
        response = requests.post(API_URL, headers={"accept": "application/json", "Content-Type": "application/json"}, json=payload, timeout=30)
        response.raise_for_status()
        return {"success": True, "data": response.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ============================
# Session State
# ============================
if "messages" not in st.session_state:
    st.session_state.messages = []

# ============================
# Sidebar
# ============================
with st.sidebar:
    st.image("https://i.ibb.co/4Z0ngTfD/upload.png", width=140)
    
    st.markdown("### 🏛️ Knowledge Hub")
    tabs = st.radio("Navigation", ["Intelligence Chat"], label_visibility="collapsed")
    
    st.divider()
    
    st.markdown("### ⚙️ Search Settings")
    top_k = st.slider("Retrieval Depth", 5, 50, 25)
    
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.caption("v2.5.0 • Enterprise Edition")

# ============================
# Main Content Logic
# ============================
if tabs == "Intelligence Chat":
    # Hero
    if not st.session_state.messages:
        st.markdown("""
        <div class="hero-box">
            <div class="hero-title">CII Intelligence Portal</div>
            <p style="font-size: 1.2rem; opacity: 0.8;">The definitive AI interface for Confederation of Indian Industry knowledge and economic insights.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🚀 Quick Start")
        col1, col2 = st.columns(2)
        examples = [
            ("📈 Growth Trends", "What are the latest industrial growth projections for the next quarter?"),
            ("🌱 Sustainability", "Tell me about CII's Green Co rating system and ESG initiatives."),
            ("🏛️ Policy Insights", "What are the key highlights of CII's pre-budget memorandum?"),
            ("🔧 MSME Support", "How is CII helping MSMEs with digital transformation?")
        ]
        
        for i, (label, text) in enumerate(examples):
            with col1 if i % 2 == 0 else col2:
                if st.button(f"**{label}**\n\n{text}", key=f"ex_{i}", use_container_width=True):
                    st.session_state.messages.append({"role": "user", "content": text, "time": datetime.now().strftime("%H:%M")})
                    with st.spinner("Connecting to Knowledge Base..."):
                        res = call_chatbot_api(text, top_k)
                        bot_text = extract_response_text(res["data"]) if res["success"] else f"Error: {res['error']}"
                        st.session_state.messages.append({"role": "assistant", "content": bot_text, "time": datetime.now().strftime("%H:%M")})
                    st.rerun()

    # Chat Feed
    for msg in st.session_state.messages:
        is_user = msg["role"] == "user"
        st.markdown(f"""
        <div class="chat-bubble {'user-bubble' if is_user else 'assistant-bubble'}">
            <div class="sender-meta">
                <span>{'USER' if is_user else 'CII INTELLIGENCE'}</span>
                <span>{msg['time']}</span>
            </div>
            <div>{msg['content']}</div>
        </div>
        """, unsafe_allow_html=True)

    # Input
    query = st.chat_input("Enter your industry research query...")
    if query:
        st.session_state.messages.append({"role": "user", "content": query, "time": datetime.now().strftime("%H:%M")})
        with st.spinner("Analyzing Database..."):
            res = call_chatbot_api(query, top_k)
            bot_text = extract_response_text(res["data"]) if res["success"] else f"Error: {res['error']}"
            st.session_state.messages.append({"role": "assistant", "content": bot_text, "time": datetime.now().strftime("%H:%M")})
        st.rerun()

# elif tabs == "Brand Identity Lab":
#     st.markdown("## 🎨 Brand Identity Lab")
#     st.write("Generate high-quality CII-themed logos, social media headers, or report covers.")
    
#     prompt_input = st.text_area("Describe the asset you want to generate:", 
#                                placeholder="A professional modern 3D logo for 'CII Tech Summit', minimal design, navy blue and silver, futuristic aesthetic.")
    
#     col_a, col_b = st.columns([1, 4])
#     with col_a:
#         if st.button("✨ Generate", use_container_width=True):
#             if prompt_input:
#                 with st.spinner("Creating Visual Asset..."):
#                     img_data = call_imagen_api(f"Professional corporate branding, {prompt_input}, high quality, 4k, studio lighting")
#                     if img_data:
#                         st.session_state.generated_img = img_data
#                     else:
#                         st.error("Failed to generate image. Please try again.")
#             else:
#                 st.warning("Please enter a prompt first.")
                
#     if "generated_img" in st.session_state:
#         st.markdown("### 🖼️ Result")
#         st.image(st.session_state.generated_img, use_container_width=True)
#         st.download_button("💾 Download Asset", 
#                           data=st.session_state.generated_img.split(",")[1], 
#                           file_name="cii_logo_concept.png", 
#                           mime="image/png")