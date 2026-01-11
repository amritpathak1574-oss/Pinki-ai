import streamlit as st
import google.generativeai as genai
import streamlit.components.v1 as components

# --- API Configuration ---
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-2.5-flash')

# --- PinkiAI System Instruction ---
instruction = """
Tumhara naam 'PinkiAI' hai. Tum ek school teacher assistant ho.
Rules:
1. Hamesha polite raho aur '🌸' use karo.
2. Short aur sweet answers do taaki voice mode mein sunne mein acha lage.
3. Agar user '/diagram' likhe, toh Mermaid.js code dena.
"""

# --- Mermaid Renderer ---
def render_mermaid(code):
    html_code = f"""
    <div class="mermaid">{code}</div>
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({{ startOnLoad: true }});
    </script>
    """
    components.html(html_code, height=400)

# --- Voice Logic (Javascript) ---
def speak_text(text):
    # Text se emojis aur code hatane ke liye taaki awaz saaf aaye
    clean_text = text.replace("🌸", "").split("```")[0].strip()
    js_code = f"""
    <script>
        var msg = new SpeechSynthesisUtterance();
        msg.text = "{clean_text}";
        msg.lang = 'hi-IN'; 
        window.speechSynthesis.speak(msg);
    </script>
    """
    components.html(js_code, height=0)

# --- UI ---
st.title("👩‍🏫 PinkiAI: Voice Enabled Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Puchiye Mam..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = model.generate_content(f"{instruction}\n\nUser: {prompt}")
        full_text = response.text
        st.markdown(full_text)
        
        # Voice Output trigger
        speak_text(full_text)
        
        if "```mermaid" in full_text:
            mermaid_code = full_text.split("```mermaid")[1].split("```")[0]
            render_mermaid(mermaid_code)

        st.session_state.messages.append({"role": "assistant", "content": full_text})
