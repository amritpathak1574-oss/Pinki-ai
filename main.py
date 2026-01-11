import streamlit as st
import google.generativeai as genai
import streamlit.components.v1 as components
from streamlit_mic_recorder import speech_to_text

# --- API Configuration ---
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-2.5-flash')

instruction = """Tumhara naam 'PinkiAI' hai. Tum ek school teacher assistant ho. 
Hamesha polite raho aur 🌸 use karo. 
AGAR user 'diagram' shabd use kare, toh hamesha Mermaid.js code dena ```mermaid se shuru karke."""

# --- Fixed Functions ---
def render_mermaid(code):
    # Markdown rendering for stability
    st.markdown(f"```mermaid\n{code}\n```")
    html_code = f"""
    <div class="mermaid" style="background: white; padding: 10px; border-radius: 10px;">{code}</div>
    <script type="module">
        import mermaid from '[https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs](https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs)';
        mermaid.initialize({{ startOnLoad: true, theme: 'forest' }});
    </script>
    """
    components.html(html_code, height=450, scrolling=True)

def speak_text(text):
    # Text clean up for JS
    clean_text = text.replace("🌸", "").replace("`", "").replace('"', "").replace("'", "").replace("\n", " ").strip()
    js_code = f"""
    <script>
        window.speechSynthesis.cancel();
        var msg = new SpeechSynthesisUtterance("{clean_text}");
        msg.lang = 'hi-IN';
        msg.rate = 1.0;
        window.speechSynthesis.speak(msg);
    </script>
    """
    components.html(js_code, height=0)

# --- UI ---
st.set_page_config(page_title="PinkiAI Pro", layout="centered")
st.title("👩‍🏫 PinkiAI: Smart Voice Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

# History Display
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Fixed Input Section ---
st.write("---")
# Mic button upar taaki chat box niche rahe
col1, col2 = st.columns([1, 5])
with col1:
    v_input = speech_to_text(language='hi', start_prompt="🎤", stop_prompt="🔴", key='lp_mic')

t_input = st.chat_input("Yahan likhiye Mam...")

# Logic handling
user_query = v_input if v_input else t_input

if user_query:
    # 1. User Message
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    # 2. Assistant Response
    with st.chat_message("assistant"):
        with st.spinner("PinkiAI kaam kar rahi hai..."):
            response = model.generate_content(f"{instruction}\n\nUser: {user_query}")
            res_text = response.text
            st.markdown(res_text)
            
            # Voice trigger
            speak_text(res_text)
            
            # Diagram check (Har tarah se)
            if "```mermaid" in res_text:
                m_code = res_text.split("```mermaid")[1].split("```")[0].strip()
                render_mermaid(m_code)
            
            st.session_state.messages.append({"role": "assistant", "content": res_text})
