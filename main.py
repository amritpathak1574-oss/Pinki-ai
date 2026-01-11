import streamlit as st
import google.generativeai as genai
import streamlit.components.v1 as components
from streamlit_mic_recorder import speech_to_text
import time

# --- API Configuration ---
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# --- PinkiAI System Instruction ---
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
    # Text cleaning to avoid JS errors
    clean_text = text.replace("🌸", "").replace("`", "").replace('"', "").replace("'", "").replace("\n", " ").strip()
    
    # Is baar hum thoda unique key denge har baar taaki browser har baar naya trigger pakde
    unique_id = str(int(time.time()))
    js_code = f"""
    <div id="voice-{unique_id}"></div>
    <script>
        (function() {{
            window.speechSynthesis.cancel();
            var msg = new SpeechSynthesisUtterance("{clean_text}");
            msg.lang = 'hi-IN';
            msg.rate = 1.1;
            window.speechSynthesis.speak(msg);
        }})();
    </script>
    """
    components.html(js_code, height=0)

# --- UI Setup ---
st.set_page_config(page_title="PinkiAI Voice Fixed", layout="centered")
st.title("👩‍🏫 PinkiAI: Smart Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Fixed Input Section ---
st.write("---")
# Mic Button
v_input = speech_to_text(language='hi', start_prompt="Bolo 🎤", stop_prompt="Ruko 🔴", key='voice_input_btn')

# Text Input
t_input = st.chat_input("Yahan likhiye Mam...")

# Logic handling: Mic ko priority do agar dono ho
final_input = None
if v_input:
    final_input = v_input
elif t_input:
    final_input = t_input

if final_input:
    st.session_state.messages.append({"role": "user", "content": final_input})
    with st.chat_message("user"):
        st.markdown(final_input)

    with st.chat_message("assistant"):
        with st.spinner("PinkiAI bol rahi hai..."):
            response = model.generate_content(f"{instruction}\n\nUser: {final_input}")
            full_text = response.text
            st.markdown(full_text)
            
            # Voice Trigger (Mic ke liye bhi forced chalega)
            speak_text(full_text)
            
            if "```mermaid" in full_text:
                m_code = full_text.split("```mermaid")[1].split("```")[0]
                render_mermaid(m_code)
            
            st.session_state.messages.append({"role": "assistant", "content": full_text})
