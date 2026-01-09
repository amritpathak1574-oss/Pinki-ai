import streamlit as st
import google.generativeai as genai
import streamlit.components.v1 as components

# --- API Configuration ---
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Model selection
model = genai.GenerativeModel('gemini-1.5-flash')

# --- PinkiAI System Instruction ---
instruction = """
Tumhara naam 'PinkiAI' hai. Tum ek intelligent school teacher assistant ho.
Rules:
1. Hamesha polite raho aur '🌸' use karo.
2. Agar user '/diagram' likhe, toh tum ek Mermaid.js flowchart code likhna.
   - Code ko hamesha ```mermaid se shuru aur ``` se khatam karna.
   - Diagram ekdum saaf aur labels ke sath hona chahiye.
3. Agar user '/image' likhe, toh pehle ki tarah artistic description dena.
"""

# --- Mermaid Renderer Function ---
def render_mermaid(code):
    html_code = f"""
    <div class="mermaid">
        {code}
    </div>
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({{ startOnLoad: true }});
    </script>
    """
    components.html(html_code, height=400, scrolling=True)

# --- Streamlit UI ---
st.set_page_config(page_title="PinkiAI - Smart Assistant")
st.title("👩‍🏫 PinkiAI: Smart Teacher Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "```mermaid" in message["content"]:
            code = message["content"].split("```mermaid")[1].split("```")[0]
            render_mermaid(code)

if prompt := st.chat_input("Puchiye Mam..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = model.generate_content(f"{instruction}\n\nUser: {prompt}")
        full_text = response.text
        st.markdown(full_text)
        
        # Check if diagram needs to be rendered
        if "```mermaid" in full_text:
            mermaid_code = full_text.split("```mermaid")[1].split("```")[0]
            render_mermaid(mermaid_code)
        
        # Keep image logic same for /image
        elif "/image" in prompt.lower():
            clean_prompt = full_text.replace(" ", "%20").replace("\n", "")
            image_url = f"https://image.pollinations.ai/prompt/{clean_prompt}"
            st.image(image_url, caption="Artistic View 🌸")

        st.session_state.messages.append({"role": "assistant", "content": full_text})
