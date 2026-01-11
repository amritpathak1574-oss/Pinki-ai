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
2. Short answers do.
3. Agar user '/diagram' bole, toh Mermaid.js code dena.
"""

# --- Functions ---
def render_mermaid(code):
    html_code = f"""
    <div class="mermaid" style="background: white; padding: 10px; border-radius: 5px;">{code}</div>
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({{ startOnLoad: true }});
    </script>
    """
    components.html(html_code, height=400)

def speak_text(text):
    clean_text = text.replace("🌸", "").replace("`", "").replace('"', "'").strip()
    js_code = f"""<script>
        var msg = new SpeechSynthesisUtterance("{clean_text}");
        msg.lang = 'hi-IN';
        window.speechSynthesis.speak(msg);
    </script>"""
    components.html(js_code, height=0)

# --- UI Layout ---
st.set_page_config(page_title="PinkiAI - Voice & Text", layout="centered")
st.title("👩‍🏫 PinkiAI: Smart Assistant")

# --- Session State for Input Handling ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Combined Input Area ---
st.write("---")
col1, col2 = st.columns([1, 4])

with col1:
    # Mic button hamesha samne rahega
    v_input = speech_to_text(language='hi', start_prompt="🎤", stop_prompt="🔴", key='voice')

with col2:
    # Text input hamesha samne rahega
    t_input = st.chat_input("Yahan likhiye Mam...")

# Logic to pick which input to use
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
        with st.spinner("PinkiAI soch rahi hai..."):
            response = model.generate_content(f"{instruction}\n\nUser: {final_input}")
            full_text = response.text
            st.markdown(full_text)
            
            speak_text(full_text) # AI bolegi
            
            if "```mermaid" in full_text:
                mermaid_code = full_text.split("```mermaid")[1].split("```")[0]
                render_mermaid(mermaid_code)

            st.session_state.messages.append({"role": "assistant", "content": full_text})
