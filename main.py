import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. API Setup (Secrets se link kiya hai)
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except:
    st.error("Bhai, Streamlit Secrets mein 'GEMINI_API_KEY' nahi mili!")

# --- SYSTEM PROMPT ---
instruction = """
Tumhara naam 'PinkiAI' hai. Tum ek bohot pyaari aur intelligent school teacher assistant ho.
Rules:
1. Hamesha namaste bolkar ya polite tareeke se baat karo.
2. Har reply ke end mein '🌸' emoji lagao.
3. Agar koi puche 'Who are you?', toh bolo: 'Main PinkiAI hoon, aapki smart assistant.'
4. Hindi aur English (Hinglish) ka mix use karo.
5. Maths ke sawal step-by-step samjhao.
"""

# Model setup (Fixed Version Name)
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash', 
    system_instruction=instruction
)

# 2. Page UI
st.set_page_config(page_title="PinkiAI 🌸", layout="centered")
st.title("🌸 PinkiAI - The Smartest Teacher")

# 3. Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. Sidebar Photo Upload
with st.sidebar:
    st.header("Photo Recognition 📸")
    uploaded_file = st.file_uploader("Homework ki photo dalo", type=['png', 'jpg', 'jpeg'])
    if uploaded_file:
        st.image(uploaded_file, caption="Maine photo dekh li hai!", use_container_width=True)

# 5. Display History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 6. Chat Logic
if prompt := st.chat_input("Sawal puchiye..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    try:
        if uploaded_file:
            img = Image.open(uploaded_file)
            response = model.generate_content([prompt, img])
        else:
            response = model.generate_content(prompt)

        ai_reply = response.text
        st.session_state.messages.append({"role": "assistant", "content": ai_reply})
        with st.chat_message("assistant"):
            st.write(ai_reply)

    except Exception as e:
        st.error("AI thak gaya hai! Ek baar key check karlo.")
        st.write(f"Error: {e}")
