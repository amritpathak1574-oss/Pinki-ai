import streamlit as st
import google.generativeai as genai
import os

# --- API Configuration ---
# Make sure your GOOGLE_API_KEY is in Streamlit Secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Models Definition
# Chatting ke liye super-fast 2.5 Flash
chat_model = genai.GenerativeModel('gemini-2.5-flash')
# Image prompt banane ke liye powerful 1.5 Pro
image_helper_model = genai.GenerativeModel('gemini-2.5-flash')

# --- PinkiAI System Instruction ---
instruction = """
Tumhara naam 'PinkiAI' hai. Tum ek intelligent school teacher assistant ho.
Rules:
1. Hamesha namaste bolkar ya polite tareeke se baat karo aur '🌸' use karo.
2. agar koi tumse puche who are you or tum kaun ho always say im pinkiai here to help you never said i was made by google and other ai companies
3. Default bhasha Hinglish rakho, par agar koi kisi aur language mein bole toh usi mein jawab do.
4. Agar user '/image' likhe, toh tum ek bahut detailed English prompt likhna.
   - Diagram mein labels aur clear text hona chahiye.
   - Example: 'A clear educational diagram of the human respiratory system with labels like Lungs, Trachea, and Diaphragm, white background, high detail.'
"""

# --- Streamlit UI Setup ---
st.set_page_config(page_title="PinkiAI - Smart Assistant", layout="centered")
st.title("👩‍🏫 PinkiAI: Smart Teacher Assistant")
st.info("💡 Tip: Normal chat karein, aur diagram ke liye message mein **/image** likhein.")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Purani baatein yaad rakhne ke liye
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Chat Input ---
if prompt := st.chat_input("Puchiye Mam..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if "/image" in prompt.lower():
            # --- IMAGE MODE (Switching to 1.5 Pro) ---
            with st.spinner("PinkiAI diagram taiyar kar rahi hai..."):
                # 1.5 Pro model se detailed visual description banwana
                img_response = image_helper_model.generate_content(f"{instruction}\n\nUser wants a diagram for: {prompt}. Write ONLY the visual prompt in English.")
                detailed_prompt = img_response.text.strip()
                
                # Image Generation URL (Pollinations handles text in images well)
                clean_prompt = detailed_prompt.replace(" ", "%20").replace("\n", "")
                image_url = f"https://image.pollinations.ai/prompt/{clean_prompt}?width=1024&height=1024&nologo=true"
                
                st.markdown(f"Zaroor Mam! Aapke liye diagram taiyar hai: \n\n")
                st.image(image_url, caption=f"Diagram: {prompt} 🌸", use_column_width=True)
                
                st.session_state.messages.append({"role": "assistant", "content": f"Image Generated: {detailed_prompt}"})
        
        else:
            # --- CHAT MODE (Using 2.5 Flash) ---
            # History pass kar rahe hain taaki AI purani baatein na bhoole
            response = chat_model.generate_content(f"{instruction}\n\nUser: {prompt}")
            
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
