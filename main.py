import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. API Setup (Bhai yahan apni VALID key dalo)
API_KEY = "AIzaSyBDmv0U5MSFc-7x4X0Xq4kzv36IjfGEq8o" 
genai.configure(api_key=API_KEY)

# --- SYSTEM PROMPT (PinkiAI ki Personality) ---
instruction = """
Tumhara naam 'PinkiAI' hai. Tum ek bohot pyaari aur intelligent school teacher assistant ho.
Rules:
1. Hamesha namaste bolkar ya polite tareeke se baat karo.
2. Har reply ke end mein '🌸' emoji lagao.
3. Agar koi puche 'Who are you?', toh bolo: 'Main PinkiAI hoon, aapki smart assistant.'
4. Hindi aur English (Hinglish) ka mix use karo taaki bacche samajh sakein.
5. Maths ke sawal step-by-step samjhao.
"""

# Model setup with Instruction
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash', 
    system_instruction=instruction
)

# 2. Page UI
st.set_page_config(page_title="PinkiAI 🌸", layout="centered")
st.title("🌸 PinkiAI - The Smartest Teacher")
st.write("Namaste! Main PinkiAI hoon. Main aapka homework dekh bhi sakti hoon!")

# 3. Chat History Maintain Karna
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. Sidebar mein Photo Upload
with st.sidebar:
    st.header("Photo Recognition 📸")
    uploaded_file = st.file_uploader("Homework ki photo yahan dalein", type=['png', 'jpg', 'jpeg'])
    if uploaded_file:
        st.image(uploaded_file, caption="Maine photo dekh li hai!", use_container_width=True)

# 5. Chat Display Area
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# 6. Chat Input Logic
if prompt := st.chat_input("Sawal puchiye..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    try:
        # AI Logic (Image + Text)
        if uploaded_file:
            img = Image.open(uploaded_file)
            response = model.generate_content([prompt, img])
        else:
            response = model.generate_content(prompt)

        # Response handle
        ai_reply = response.text
        st.session_state.messages.append({"role": "assistant", "content": ai_reply})
        st.chat_message("assistant").write(ai_reply)

    except Exception as e:
        st.error("Bhai, API Key check karo ya model load nahi ho raha. Check: AI Studio key.")
