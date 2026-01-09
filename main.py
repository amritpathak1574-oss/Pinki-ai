import streamlit as st
import google.generativeai as genai
import streamlit.components.v1 as components

# --- API Configuration ---
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Models Definition
# Chatting ke liye super-fast 2.5 Flash (Ya 1.5-flash agar 2.5 available nahi)
chat_model = genai.GenerativeModel('gemini-2.5-flash') # Keep this for chat
# Image prompt banane ke liye powerful 1.5 Pro (Ya 1.5-flash agar 1.5-pro unavailable)
image_prompt_generator_model = genai.GenerativeModel('gemini-1.5-flash') # Use a stronger model for complex image prompts

# --- PinkiAI System Instruction ---
instruction = """
Tumhara naam 'PinkiAI' hai. Tum ek intelligent school teacher assistant ho.
Rules:
1. Hamesha polite raho aur '🌸' use karo.
2. Default bhasha Hinglish rakho, par agar koi kisi aur language mein bole toh usi mein jawab do.

3. AGAR USER '/diagram' likhe:
   - Tum ek Mermaid.js flowchart code likhna.
   - Code ko hamesha ```mermaid se shuru aur ``` se khatam karna.
   - Diagram ekdum saaf aur labels ke sath hona chahiye.
   - Example: ```mermaid\\n flowchart TD\\n A[Start] --> B{Is it true?}\\n B -- Yes --> C[Do something]\\n B -- No --> D[Do nothing]\\n```

4. AGAR USER '/image' likhe:
   - Tum ek **EXTREMELY DETAILED ENGLISH PROMPT** likhna image generation engine ke liye.
   - Prompt mein "illustration style", "background", "colors", "mood", aur especially "clear text labels" ka mention karna.
   - Example: 'A vibrant watercolor illustration of a tropical rainforest ecosystem, with clear labels for "Canopy", "Understory", and "Forest Floor". Bright green and blue colors, daylight, realistic yet artistic.'
   - JAB TUM YE PROMPT LIKH DO, TOH USKE BAAD SIRF WOH PROMPT LIKHNA, AUR KUCH NAHI.
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
st.info("💡 Tip: Normal chat, **/diagram** for flowcharts, **/image** for creative pictures.")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history and render mermaid diagrams if present
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "```mermaid" in message["content"]:
            code_match = message["content"].find("```mermaid")
            if code_match != -1:
                code_start = code_match + len("```mermaid")
                code_end = message["content"].find("```", code_start)
                if code_end != -1:
                    mermaid_code = message["content"][code_start:code_end].strip()
                    render_mermaid(mermaid_code)

if prompt := st.chat_input("Puchiye Mam..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Image generation logic (use stronger model for prompt generation)
        if "/image" in prompt.lower():
            with st.spinner("PinkiAI aapke liye ek creative tasveer bana rahi hai..."):
                # Use image_prompt_generator_model (e.g., gemini-1.5-pro) for detailed prompt
                image_gen_response = image_prompt_generator_model.generate_content(
                    f"{instruction}\n\nUser wants an image for: {prompt}. Generate ONLY the EXTREMELY DETAILED ENGLISH PROMPT for the image generation AI, focusing on clarity, style, and text labels."
                )
                generated_image_prompt = image_gen_response.text.strip()
                
                # Clean prompt for URL (Pollinations.ai)
                clean_prompt_for_url = generated_image_prompt.replace(" ", "%20").replace("\n", "")
                image_url = f"https://image.pollinations.ai/prompt/{clean_prompt_for_url}?width=1024&height=768&nologo=true"
                
                st.markdown(f"Zaroor Mam! Aapke liye ye tasveer taiyar hai: \n\n**Prompt:** *{generated_image_prompt}*")
                st.image(image_url, caption=f"Created by PinkiAI 🌸", use_column_width=True)
                st.session_state.messages.append({"role": "assistant", "content": f"Image Generated: {generated_image_prompt}"})

        # Diagram generation logic
        elif "/diagram" in prompt.lower():
            with st.spinner("PinkiAI aapke liye saaf flowchart bana rahi hai..."):
                # Use chat_model for Mermaid code generation
                diagram_response = chat_model.generate_content(f"{instruction}\n\nUser wants a diagram for: {prompt}. Generate ONLY the Mermaid.js code.")
                full_text = diagram_response.text
                
                st.markdown(full_text) # Show the mermaid code in markdown
                if "```mermaid" in full_text:
                    code_match = full_text.find("```mermaid")
                    if code_match != -1:
                        code_start = code_match + len("```mermaid")
                        code_end = full_text.find("```", code_start)
                        if code_end != -1:
                            mermaid_code = full_text[code_start:code_end].strip()
                            render_mermaid(mermaid_code)
                st.session_state.messages.append({"role": "assistant", "content": full_text})

        # Normal chat logic
        else:
            with st.spinner("PinkiAI soch rahi hai..."):
                response = chat_model.generate_content(f"{instruction}\n\nUser: {prompt}")
                full_text = response.text
                st.markdown(full_text)
                st.session_state.messages.append({"role": "assistant", "content": full_text})
