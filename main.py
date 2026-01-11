import streamlit as st
import google.generativeai as genai
import streamlit.components.v1 as components
from streamlit_mic_recorder import speech_to_text

# --- API Configuration ---
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-2.5-flash')

# --- PinkiAI System Instruction ---
instruction = """
Tumhara naam 'PinkiAI' hai. Tum ek school teacher assistant ho.
Rules:
1. Hamesha polite raho aur '🌸' use karo.
2. Short responses do taaki sunne mein maza aaye.
3. Agar user '/diagram' bole ya likhe, toh Mermaid.js code dena.
"""

# --- Mermaid & Voice Output Functions ---
def render_mermaid(code):
    html_code = f"""
    <div class="mermaid">{code}</div>
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({{ startOnLoad: true }});
    </script>
    """
    components.html(html_code, height=400)

def speak_text(text):
    clean_text = text.replace("🌸", "").split("```")[0].strip()
    js_code = f"""<script>
        var msg = new SpeechSynthesisUtterance("{clean_text}");
        msg.lang = 'hi-IN';
        window.speechSynthesis.speak(msg);
    </script>"""
    components.html(js_code, height=0)

# --- UI ---
st.set_page_config(page_title="PinkiAI: Listen & Speak")
st.title("👩‍🏫 PinkiAI: Voice & Text Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar mein Voice Input button
with st.sidebar:
    st.write("### Voice Mode 🎤")
    voice_input = speech_to_text(language='hi', start_prompt="Bolne ke liye click karein", stop_prompt="Rukne ke liye click karein", key='speech')

# Chat History display
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Logic for Input (Dono handling: Voice or Type)
user_input = None
if voice_input:
    user_input = voice_input
elif prompt := st.chat_input("Yahan likhiye Mam..."):
    user_input = prompt

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        response = model.generate_content(f"{instruction}\n\nUser: {user_input}")
        full_text = response.text
        st.markdown(full_text)
        
        speak_text(full_text) # PinkiAI bolegi
        
        if "```mermaid" in full_text:
            mermaid_code = full_text.split("```mermaid")[1].split("```")[0]
            render_mermaid(mermaid_code)

        st.session_state.messages.append({"role": "assistant", "content": full_text})
