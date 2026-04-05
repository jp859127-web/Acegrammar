import streamlit as st
import google.generativeai as genai
import json
import os

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="AceGrammar: Banking English Master",
    page_icon="📚",
    layout="wide"
)

# --- STYLING ---
st.markdown("""
    <style>
    .main { background-color: #f7fafc; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .decode-card { background-color: white; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 20px; }
    .pos-tag { background-color: #ebf8ff; color: #2b6cb0; padding: 2px 6px; border-radius: 4px; font-size: 0.8em; font-weight: bold; }
    </style>
    """, unsafe_allow_stdio=True)

# --- SIDEBAR: API CONFIG ---
st.sidebar.title("⚙️ Configuration")
api_key = st.sidebar.text_input("Enter Gemini API Key", type="password", help="Get your key from https://aistudio.google.com/")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-3.1-pro-preview')
else:
    st.sidebar.warning("Please enter your Gemini API Key to start.")
    st.stop()

# --- FUNCTIONS ---
def analyze_grammar(text):
    prompt = f"""
    Analyze the following text for English grammar and vocabulary, specifically for Indian banking exams (SBI/IBPS PO/Clerk). 
    1. Break it down sentence by sentence. For each sentence, provide:
       - Subject, verb, and object.
       - Tense and voice (active/passive).
       - Word-by-word parts of speech analysis with logical explanations.
       - A logical breakdown of sentence construction.
    2. Extract important vocabulary words with meanings, synonyms, antonyms, and usage.
    3. Identify any idioms or phrases.

    Return the result in STRICT JSON format.
    Text: "{text}"
    """
    response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
    return json.loads(response.text)

def generate_questions(text, level, q_type, count):
    prompt = f"""
    Based on the following text, generate {count} {level} level banking exam questions.
    Question Type: {q_type} (e.g., Error Spotting, Fillers, Reading Comprehension, Cloze Test).
    Ensure the questions match the pattern of SBI PO, IBPS PO, and Clerk exams.
    Provide clear explanations for each answer.

    Return the result in STRICT JSON format as a list of objects.
    Text: "{text}"
    """
    response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
    return json.loads(response.text)

# --- MAIN UI ---
st.title("🏦 AceGrammar: Banking Exam English Master")
st.caption("Logical Grammar Decoder & Question Generator for SBI, IBPS, and RRB Aspirants")

col1, col2 = st.columns([2, 3])

with col1:
    st.subheader("📝 Source Content")
    input_text = st.text_area("Paste Editorial / Article here:", height=300, placeholder="Example: The Reserve Bank of India has maintained its repo rate...")
    
    st.divider()
    st.subheader("🛠️ Question Settings")
    q_level = st.selectbox("Exam Level", ["Prelims", "Mains", "Mix (Pre + Mains)"])
    q_type = st.selectbox("Question Type", ["Mixed Pattern", "Error Spotting", "Cloze Test", "Reading Comprehension", "Fillers"])
    q_count = st.slider("Number of Questions", 1, 10, 5)

with col2:
    tab1, tab2 = st.tabs(["🔍 Grammar Decoder", "✍️ Exam Practice"])
    
    if input_text:
        with tab1:
            if st.button("🚀 Decode Full Grammar"):
                with st.spinner("Decoding logically..."):
                    data = analyze_grammar(input_text)
                    
                    # Vocabulary Section
                    st.markdown("### 📖 High-Yield Vocabulary")
                    v_cols = st.columns(2)
                    for i, v in enumerate(data.get('vocabulary', [])):
                        with v_cols[i % 2]:
                            st.info(f"**{v['word']}**: {v['meaning']}\n\n*Usage:* {v['usage']}")
                    
                    # Sentence Breakdown
                    st.markdown("### 🧠 Sentence-by-Sentence Decoding")
                    for i, s in enumerate(data.get('sentences', [])):
                        with st.expander(f"Sentence {i+1}: {s['text'][:50]}..."):
                            st.write(f"**Full Text:** {s['text']}")
                            c1, c2, c3 = st.columns(3)
                            c1.metric("Subject", s['analysis']['subject'])
                            c2.metric("Verb", s['analysis']['verb'])
                            c3.metric("Object", s['analysis']['object'])
                            
                            st.markdown(f"**Tense:** {s['analysis']['tense']} | **Voice:** {s['analysis']['voice']}")
                            
                            st.markdown("**Word Analysis:**")
                            for word in s['analysis']['parts_of_speech']:
                                st.markdown(f"- **{word['word']}** <span class='pos-tag'>{word['pos']}</span>: {word['explanation']}", unsafe_allow_stdio=True)
                            
                            st.markdown("**Logical Implementation:**")
                            st.info(s['analysis']['logical_breakdown'])

        with tab2:
            if st.button("✨ Generate Practice Questions"):
                with st.spinner("Creating exam-level questions..."):
                    qs = generate_questions(input_text, q_level, q_type, q_count)
                    for i, q in enumerate(qs):
                        st.markdown(f"#### Q{i+1}. {q['question']}")
                        if 'options' in q:
                            for opt in q['options']:
                                st.write(f"- {opt}")
                        
                        with st.expander("Show Answer & Explanation"):
                            st.success(f"**Answer:** {q['answer']}")
                            st.write(q['explanation'])
    else:
        st.info("Please paste some text in the left panel to begin analysis.")
