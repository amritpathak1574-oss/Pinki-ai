import streamlit as st
import google.generativeai as genai
import streamlit.components.v1 as components
from streamlit_mic_recorder import speech_to_text
import time

# --- API Configuration ---
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-2.5-flash')

instruction = "Tumhara naam 'PinkiAI' hai. Tum ek school teacher assistant ho. Polite raho aur 🌸 use karo. Short answers do."

# --- Functions ---
def render_mermaid(code):
    html_code = f"""
    <div class="mermaid" style="background: white; padding: 10px; border-radius: 10px;">{code}</div>
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({{ startOnLoad: true }});
    </script>
    """
    components.html(html_code, height=400)

def speak_text(text):
    clean_text = text.replace("🌸", "").replace("`", "").replace('"', "").replace("'", "").replace("\n", " ").strip()
    unique_id = str(int(time.time()))
    js_code = f"""
    <script>
        window.speechSynthesis.cancel();
        var msg = new SpeechSynthesisUtterance("{clean_text}");
        msg.lang = 'hi-IN';
        window.speechSynthesis.speak(msg);
    </script>
    """
    components.html(js_code, height=0)

# --- UI Setup ---
st.set_page_config(page_title="PinkiAI Fixed", layout="centered")
st.title("👩‍🏫 PinkiAI: Smart Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_processed" not in st.session_state:
    st.session_state.last_processed = None

# Display History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Input Section ---
st.write("---")
v_input = speech_to_text(language='hi', start_prompt="Bolo 🎤", stop_prompt="Ruko 🔴", key='voice_input')
t_input = st.chat_input("Yahan likhiye Mam...")

# Logic to prevent repeating old messages
current_input = v_input if v_input else t_input

# SIRF tabhi process karo jab input naya ho aur purane wale se alag ho
if current_input and current_input != st.session_state.last_processed:
    st.session_state.last_processed = current_input # Lock laga diya
    
    st.session_state.messages.append({"role": "user", "content": current_input})
    with st.chat_message("user"):
        st.markdown(current_input)

    with st.chat_message("assistant"):
        response = model.generate_content(f"{instruction}\n\nUser: {current_input}")
        full_text = response.text
        st.markdown(full_text)
        
        speak_text(full_text)
        
        if "```mermaid" in full_text:
            m_code = full_text.split("```mermaid")[1].split("```")[0]
            render_mermaid(m_code)
            
        st.session_state.messages.append({"role": "assistant", "content": full_text})
    
    # Refresh taaki logic reset ho jaye
    st.rerun()
