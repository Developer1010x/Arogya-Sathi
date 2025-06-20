import streamlit as st
from ocr import recognize_handwriting
from llm import ask_llm
from deep_translator import GoogleTranslator
from gtts import gTTS
import requests
import os
import sys
import platform
import subprocess
import socket
import json
import tempfile
from datetime import datetime

# --- Config ---
st.set_page_config(page_title="Arogya-Sathi", layout="wide", page_icon="🩺")

# --- Custom CSS for Gradient Background and Interactive UI ---
st.markdown("""
<style>
/* Base App Styling */
body, .stApp, [data-testid="stAppViewContainer"] {
    background: linear-gradient(145deg, #0f172a, #1e293b) !important;
    color: #f8fafc !important;
    font-family: 'Segoe UI', sans-serif;
}

/* Typography */
h1, h2, h3, h4, h5, h6, p, span, label, div {
    color: #f1f5f9 !important;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.4);
}

/* Input fields */
input, textarea, select {
    background-color: rgba(255,255,255,0.05) !important;
    border: 1px solid #475569 !important;
    color: white !important;
    border-radius: 8px;
    padding: 0.5rem;
}

/* Header / Welcome */
.welcome-header {
    font-size: 2.75rem;
    font-weight: bold;
    color: #f1f5f9;
    text-align: center;
    margin: 2rem 0;
}

/* Feature Cards */
.feature-card {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(12px);
    border-radius: 20px;
    padding: 2rem;
    margin: 1rem;
    border: 1px solid rgba(255,255,255,0.1);
    box-shadow: 0 8px 32px rgba(0,0,0,0.5);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.feature-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 30px rgba(0,0,0,0.7);
}

/* Continue Button */
.continue-button {
    background: linear-gradient(135deg, #16a34a, #0ea5e9);
    color: white;
    font-weight: bold;
    border: none;
    padding: 1rem 2.5rem;
    border-radius: 40px;
    font-size: 1.1rem;
    margin: 2rem auto;
    display: block;
    cursor: pointer;
    box-shadow: 0 6px 15px rgba(0,0,0,0.3);
    transition: all 0.25s ease;
}

.continue-button:hover {
    transform: translateY(-3px);
    background: linear-gradient(135deg, #22c55e, #3b82f6);
    box-shadow: 0 8px 24px rgba(0,0,0,0.5);
}

/* Language Selector */
.language-corner {
    position: fixed;
    top: 20px;
    right: 20px;
    background: rgba(30, 41, 59, 0.85);
    color: white;
    border-radius: 999px;
    padding: 10px 20px;
    z-index: 1000;
    cursor: pointer;
    border: 1px solid rgba(255,255,255,0.15);
    box-shadow: 0 4px 12px rgba(0,0,0,0.4);
}

.language-dropdown {
    display: none;
    position: absolute;
    right: 0;
    top: 100%;
    margin-top: 10px;
    background: rgba(15, 23, 42, 0.95);
    border-radius: 10px;
    border: 1px solid rgba(255,255,255,0.15);
    padding: 1rem;
    min-width: 180px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.6);
}

.language-dropdown.show {
    display: block;
}

/* Mobile Styles */
@media screen and (max-width: 768px) {
    .welcome-header {
        font-size: 2rem;
        margin: 1.5rem 1rem;
    }

    .feature-card {
        margin: 1rem 0.5rem;
        padding: 1.5rem;
    }

    .continue-button {
        width: 90%;
        font-size: 1rem;
        padding: 0.8rem 1.5rem;
    }

    .language-corner {
        top: 10px;
        right: 10px;
        padding: 8px 14px;
    }
}

/* Hide Streamlit header */
header[data-testid="stHeader"] {
    display: none;
}
</style>

<script>
function toggleLanguageDropdown() {
    const dropdown = document.querySelector('.language-dropdown');
    dropdown.classList.toggle('show');
}

document.addEventListener('click', function(event) {
    const dropdown = document.querySelector('.language-dropdown');
    const toggle = document.querySelector('.language-corner');
    if (!toggle.contains(event.target)) {
        dropdown.classList.remove('show');
    }
});
</script>
""", unsafe_allow_html=True)


# --- Supported languages ---
indian_languages = {
    "English": "en",
    "हिंदी (Hindi)": "hi",
    "தமிழ் (Tamil)": "ta",
    "తెలుగు (Telugu)": "te",
    "বাংলা (Bengali)": "bn",
    "मराठी (Marathi)": "mr",
    "ગુજરાતી (Gujarati)": "gu",
    "ಕನ್ನಡ (Kannada)": "kn",
    "മലയാളം (Malayalam)": "ml",
    "ਪੰਜਾਬੀ (Punjabi)": "pa",
    "ଓଡ଼ିଆ (Odia)": "or",
    "অসমীয়া (Assamese)": "as"
}

# --- Helper Functions ---
def translate_text(text, target_lang_code):
    """Translate text to target language"""
    try:
        translated = GoogleTranslator(source="auto", target=target_lang_code).translate(text)
        return translated
    except Exception as e:
        st.error(f"Translation error: {e}")
        return text

def text_to_speech(text, lang_code):
    """Convert text to speech and return audio file path"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tts = gTTS(text=text, lang=lang_code)
            tts.save(tmp_file.name)
            return tmp_file.name
    except Exception as e:
        st.error(f"Text-to-speech error: {e}")
        return None

# --- Home Page ---
def show_home():
    # Language selector in corner
    if 'selected_language' not in st.session_state:
        st.session_state.selected_language = "English"
    
    # Create columns for language selector positioning
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col3:
        selected_lang = st.selectbox(
            "🌐",
            list(indian_languages.keys()),
            index=list(indian_languages.keys()).index(st.session_state.selected_language),
            key="lang_selector",
            help="Choose your language"
        )
        st.session_state.selected_language = selected_lang
        lang_code = indian_languages[selected_lang]
    
    # Welcome header
    st.markdown('<h1 class="welcome-header">Welcome to Arogya-Sathi</h1>', unsafe_allow_html=True)
    
    # Translated welcome message
    welcome_text = translate_text("Holistic Health Care Using AI", lang_code)
    st.markdown(f'<p style="text-align:center; font-size:1.5rem; color:#ffffff; margin-bottom: 40px;">{welcome_text}</p>', unsafe_allow_html=True)
    
    # Feature cards
    health_tools_text = translate_text("Health Tools", lang_code)
    st.markdown(f"## 🌐 {'Our Apps'}")
    
    cols = st.columns(3)
    
    with cols[0]:
        card_title = translate_text("Health Report", lang_code)
        card_desc = translate_text("Upload and analyze medical reports with AI", lang_code)
        st.markdown(f"""
        <div class="feature-card">
            <h3>📝 {card_title}</h3>
            <p>{card_desc}</p>
        </div>
        """, unsafe_allow_html=True)
        
    with cols[1]:
        card_title = translate_text("Ask a Doctor", lang_code)
        card_desc = translate_text("Get answers to your medical questions", lang_code)
        st.markdown(f"""
        <div class="feature-card">
            <h3>❓ {card_title}</h3>
            <p>{card_desc}</p>
        </div>
        """, unsafe_allow_html=True)
        
    with cols[2]:
        card_title = translate_text("Symptom Checker", lang_code)
        card_desc = translate_text("Comprehensive symptom analysis", lang_code)
        st.markdown(f"""
        <div class="feature-card">
            <h3>🤒 {card_title}</h3>
            <p>{card_desc}</p>
        </div>
        """, unsafe_allow_html=True)
    
    cols = st.columns(3)
    with cols[0]:
        card_title = translate_text("Deep Analysis", lang_code)
        card_desc = translate_text("Detailed medical interview", lang_code)
        st.markdown(f"""
        <div class="feature-card">
            <h3>🧠 {card_title}</h3>
            <p>{card_desc}</p>
        </div>
        """, unsafe_allow_html=True)
        
    with cols[1]:
        card_title = translate_text("Buy Medicine", lang_code)
        card_desc = translate_text("Search and purchase medicines", lang_code)
        st.markdown(f"""
        <div class="feature-card">
            <h3>💊 {card_title}</h3>
            <p>{card_desc}</p>
        </div>
        """, unsafe_allow_html=True)
        
    with cols[2]:
        card_title = translate_text("Find Clinics", lang_code)
        card_desc = translate_text("Locate nearby healthcare providers", lang_code)
        st.markdown(f"""
        <div class="feature-card">
            <h3>🏥 {card_title}</h3>
            <p>{card_desc}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Compact continue button
    st.markdown('<div class="continue-container">', unsafe_allow_html=True)
    continue_text = translate_text("Continue", lang_code)
    
    if st.button(continue_text, key="continue_btn", help="Start using Arogya-Sathi"):
        st.session_state.show_home = False
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- Main App Logic ---
if 'show_home' not in st.session_state:
    st.session_state.show_home = True
    st.session_state.lang_code = "en"  # Default to English

# Initialize option variable
option = None
interface_lang_code = "en"  # Default language code

if st.session_state.show_home:
    show_home()
else:
    # Language settings in sidebar
    st.sidebar.title("🌐 Language Settings")
    interface_language = st.sidebar.selectbox("Choose Language", list(indian_languages.keys()), index=0)
    interface_lang_code = indian_languages[interface_language]
    enable_tts = st.sidebar.checkbox("🔊 Enable Text-to-Speech", value=False)
    
    # Navigation options in sidebar
    st.sidebar.title("🩺 Health Tools")
    option = st.sidebar.selectbox(
        "Choose a tool:",
        [
            "📝 Health Report Summary",
            "❓ Ask a Doctor",
            "🤒 Symptom Checker",
            "🧠 Deep Analysis",
            "💊 Buy Medicine",
            "🏥 Find Clinics & Pharmacies",
            "🏠 Home"
        ]
    )
# --- OCR and Summarize ---
if option == "📝 Health Report Summary":
    # Translate section headers based on selected language
    header_text = translate_text("📷 Upload Report ", interface_lang_code) if interface_language != "English" else "📷 Upload Report "
    st.header(header_text)
    
    upload_text = translate_text("Upload an image", interface_lang_code) if interface_language != "English" else "Upload an image"
    uploaded_file = st.file_uploader(upload_text, type=["png", "jpg", "jpeg"])
    
    if uploaded_file:
        st.image(uploaded_file, caption=translate_text("Uploaded Note", interface_lang_code), use_container_width=True)
        
        with st.spinner(translate_text("Reading report...", interface_lang_code)):
            extracted_text = recognize_handwriting(uploaded_file)
            extracted_subheader = translate_text("📝 Extracted Text", interface_lang_code)
            st.subheader(extracted_subheader)
            st.write(extracted_text)
            
            # Add translation option for extracted text
            if interface_language != "English":
                translated_extraction = translate_text(extracted_text, interface_lang_code)
                st.write(f"**{translate_text('Translated Extraction', interface_lang_code)}:**")
                st.write(translated_extraction)
                
                # Add TTS for translated extraction if enabled
                if enable_tts:
                    audio_path = text_to_speech(translated_extraction, interface_lang_code)
                    if audio_path:
                        st.audio(audio_path)
        
        with st.spinner(translate_text("Summarizing with LLM...", interface_lang_code)):
            summary = ask_llm(f"This is a doctor's note: \"{extracted_text}\". Can you summarize this in simple terms?")
            summary_subheader = translate_text("🧠 Summary", interface_lang_code)
            st.subheader(summary_subheader)
            st.write(summary)
            
            # Add translation option for summary
            if interface_language != "English":
                translated_summary = translate_text(summary, interface_lang_code)
                st.write(f"**{translate_text('Translated Summary', interface_lang_code)}:**")
                st.write(translated_summary)
                
                # Add TTS for translated summary if enabled
                if enable_tts:
                    audio_path = text_to_speech(translated_summary, interface_lang_code)
                    if audio_path:
                        st.audio(audio_path)

# --- Health Q&A ---
elif option ==  "❓ Ask a Doctor":
    header_text = translate_text("💬 Ask a Medical Question", interface_lang_code) if interface_language != "English" else "💬 Ask a Medical Question"
    st.header(header_text)
    
    question_text = translate_text("What would you like to know?", interface_lang_code) if interface_language != "English" else "What would you like to know?"
    question = st.text_input(question_text)
    
    ask_text = translate_text("Ask", interface_lang_code) if interface_language != "English" else "Ask"
    if st.button(ask_text):
        with st.spinner(translate_text("Thinking...", interface_lang_code)):
            # If non-English question, translate to English for the LLM
            llm_question = question
            if interface_language != "English":
                # Keep original question but also send translated version to LLM
                eng_question = translate_text(question, "en")
                llm_question = eng_question
            
            answer = ask_llm(llm_question)
            
            # Show original answer
            st.success(answer)
            
            # If interface language is not English, translate and speak the answer
            if interface_language != "English":
                translated_answer = translate_text(answer, interface_lang_code)
                st.write(f"**{translate_text('Translated Answer', interface_lang_code)}:**")
                st.success(translated_answer)
                
                # Add TTS for translated answer if enabled
                if enable_tts:
                    audio_path = text_to_speech(translated_answer, interface_lang_code)
                    if audio_path:
                        st.audio(audio_path)

# --- Symptom Checker ---
elif option == "🤒 Symptom Checker":
    header_text = translate_text("🧪 Symptom Checker", interface_lang_code) if interface_language != "English" else "🧪 Disease Predicitor"
    st.header(header_text)
    
    # Add a brief description of the symptom checker
    description_text = translate_text("Describe your symptoms in detail to get possible conditions, recommended tests, and specialist information.", interface_lang_code) if interface_language != "English" else "Describe your symptoms in detail to get possible conditions, recommended tests, and specialist information."
    st.markdown(description_text)
    
    # Disclaimer about medical advice
    disclaimer_text = translate_text("⚠️ **Note:** This is under testing please proceed with cation", interface_lang_code) if interface_language != "English" else "⚠️ **Note:** This is under testing please proceed with cation"
    st.markdown(disclaimer_text)
    
    # Input section with example
    st.subheader(translate_text("Your Symptoms", interface_lang_code) if interface_language != "English" else "Your Symptoms")
    example_text = translate_text("Example: I've had a persistent headache for 3 days, mild fever, and feel tired", interface_lang_code) if interface_language != "English" else "Example: I've had a persistent headache for 3 days, mild fever, and feel tired"
    symptoms = st.text_area(translate_text("Describe your symptoms", interface_lang_code) if interface_language != "English" else "Describe your symptoms", placeholder=example_text, height=150)
    
    # Add age and gender for better context
    col1, col2 = st.columns(2)
    with col1:
        age_text = translate_text("Age (optional)", interface_lang_code) if interface_language != "English" else "Age (optional)"
        age = st.number_input(age_text, min_value=0, max_value=120, value=None, step=1)
    with col2:
        gender_text = translate_text("Gender (optional)", interface_lang_code) if interface_language != "English" else "Gender (optional)"
        gender = st.selectbox(gender_text, ["-", translate_text("Male", interface_lang_code) if interface_language != "English" else "Male", translate_text("Female", interface_lang_code) if interface_language != "English" else "Female", translate_text("Other", interface_lang_code) if interface_language != "English" else "Other"])
    
    # Check button
    check_text = translate_text("Check Symptoms", interface_lang_code) if interface_language != "English" else "Check Symptoms"
    if st.button(check_text, type="primary"):
        if not symptoms.strip():
            st.error(translate_text("Please describe your symptoms first.", interface_lang_code) if interface_language != "English" else "Please describe your symptoms first.")
        else:
            with st.spinner(translate_text("Analyzing symptoms...", interface_lang_code) if interface_language != "English" else "Analyzing symptoms..."):
                # If non-English symptoms, translate to English for the LLM
                llm_symptoms = symptoms
                if interface_language != "English":
                    # Keep original symptoms but also send translated version to LLM
                    eng_symptoms = translate_text(symptoms, "en")
                    llm_symptoms = eng_symptoms
                
                # Build prompt with additional context if provided
                additional_context = ""
                if age is not None:
                    additional_context += f" Age: {age}."
                if gender != "-":
                    additional_context += f" Gender: {gender}."
                
                prompt = f"""The patient describes: "{llm_symptoms}".{additional_context}
                
                Analyze these symptoms and provide the following:
                1. Most likely possible conditions (3-5 possibilities)
                2. For each condition, list key symptoms to watch for
                3. Recommended tests or examinations
                4. Type of specialist doctor to consult
                5. When to seek immediate medical attention (if applicable)
                
                Format the response in clear sections with headings."""
                
                try:
                    output = ask_llm(prompt)
                    
                    # Create tabs for results
                    result_tab, doctor_tab = st.tabs([
                        translate_text("Analysis Results", interface_lang_code) if interface_language != "English" else "Analysis Results",
                        translate_text("Find a Doctor", interface_lang_code) if interface_language != "English" else "Find a Doctor"
                    ])
                    
                    with result_tab:
                        # Show original output
                        st.markdown("### " + translate_text("Medical Analysis", interface_lang_code) if interface_language != "English" else "Medical Analysis")
                        st.markdown(output)
                        
                        # If interface language is not English, translate and speak the output
                        if interface_language != "English":
                            translated_output = translate_text(output, interface_lang_code)
                            st.markdown("### " + translate_text("Translated Analysis", interface_lang_code))
                            st.markdown(translated_output)
                            
                            # Add TTS for translated output if enabled
                            if enable_tts:
                                audio_path = text_to_speech(translated_output, interface_lang_code)
                                if audio_path:
                                    st.audio(audio_path)
                    
                    with doctor_tab:
                        st.markdown("### " + translate_text("Find a Medical Professional", interface_lang_code) if interface_language != "English" else "Find a Medical Professional")
                        
                        # Add multiple options to find doctors
                        st.markdown(translate_text("Find specialists near you:", interface_lang_code) if interface_language != "English" else "Find specialists near you:")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("🔍 [Practo](https://www.practo.com/)")
                            st.markdown("🔍 [Apollo 24/7](https://www.apollo247.com/)")
                        with col2:
                            st.markdown("🔍 [DocOnline](https://www.doconline.com/)")
                            st.markdown("🔍 [MFine](https://www.mfine.co/)")
                        
                        st.markdown("### " + translate_text("Emergency Services", interface_lang_code) if interface_language != "English" else "Emergency Services")
                        st.markdown("🚑 " + translate_text("Emergency: Call 102 or 108 (India)", interface_lang_code) if interface_language != "English" else "Emergency: Call 102 or 108 (India)")
                
                except Exception as e:
                    st.error(translate_text(f"An error occurred: {str(e)}", interface_lang_code) if interface_language != "English" else f"An error occurred: {str(e)}")
                    st.markdown(translate_text("Please try again or refine your symptom description.", interface_lang_code) if interface_language != "English" else "Please try again or refine your symptom description.")
    
    # Add extra information about symptom tracking
    with st.expander(translate_text("📋 Tips for tracking symptoms", interface_lang_code) if interface_language != "English" else "📋 Tips for tracking symptoms"):
        tips_text = translate_text("""
        - Note when symptoms started and their severity
        - Track any changes over time
        - List any medications you're taking
        - Record any factors that make symptoms better or worse
        - Document your medical history
        """, interface_lang_code) if interface_language != "English" else """
        - Note when symptoms started and their severity
        - Track any changes over time
        - List any medications you're taking
        - Record any factors that make symptoms better or worse
        - Document your medical history
        """
        st.markdown(tips_text)
        
        
        
        
        
# Enhanced Symptom Checker Section with Comprehensive Patient Interview






elif option == "🧠 Deep Analysis":
    header_text = translate_text("🧪 Advanced Symptom Checker - Comprehensive Medical Interview", interface_lang_code) if interface_language != "English" else "🧪 Advanced Symptom Checker - Comprehensive Medical Interview"
    st.header(header_text)
    
    # Add a brief description of the enhanced symptom checker
    description_text = translate_text("This comprehensive medical interview will ask detailed questions like a real doctor to uncover all relevant information for accurate diagnosis.", interface_lang_code) if interface_language != "English" else "This comprehensive medical interview will ask detailed questions like a real doctor to uncover all relevant information for accurate diagnosis."
    st.markdown(description_text)
    
    # Disclaimer about medical advice
    disclaimer_text = translate_text("⚠️ **Note:** This is under testing please proceed with cation.", interface_lang_code) if interface_language != "English" else "⚠️ **Note:** This is under testing please proceed with cation"
    st.markdown(disclaimer_text)
    
    # Initialize session state for patient data
    if 'patient_data' not in st.session_state:
        st.session_state.patient_data = {}
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 1
    if 'interview_complete' not in st.session_state:
        st.session_state.interview_complete = False
    
    # Progress bar
    total_steps = 8
    progress = st.session_state.current_step / total_steps
    st.progress(progress)
    st.markdown(f"**{translate_text('Interview Progress', interface_lang_code) if interface_language != 'English' else 'Interview Progress'}: {st.session_state.current_step}/{total_steps}**")
    
    # Step 1: Basic Symptoms and Demographics
    if st.session_state.current_step == 1:
        st.subheader(translate_text("Step 1: Primary Symptoms & Basic Information", interface_lang_code) if interface_language != "English" else "Step 1: Primary Symptoms & Basic Information")
        
        with st.form("step1_form"):
            # Basic symptoms
            example_text = translate_text("Example: I've had a persistent headache for 3 days, mild fever, and feel tired", interface_lang_code) if interface_language != "English" else "Example: I've had a persistent headache for 3 days, mild fever, and feel tired"
            symptoms = st.text_area(translate_text("Describe your main symptoms in detail", interface_lang_code) if interface_language != "English" else "Describe your main symptoms in detail",
                                  placeholder=example_text, height=150, key="symptoms")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                age = st.number_input(translate_text("Age", interface_lang_code) if interface_language != "English" else "Age",
                                    min_value=0, max_value=120, value=None, step=1, key="age")
            with col2:
                gender = st.selectbox(translate_text("Gender", interface_lang_code) if interface_language != "English" else "Gender",
                                    ["-", "Male", "Female", "Other"], key="gender")
            with col3:
                weight = st.number_input(translate_text("Weight (kg)", interface_lang_code) if interface_language != "English" else "Weight (kg)",
                                       min_value=0.0, max_value=300.0, value=None, step=0.1, key="weight")
            
            # When did symptoms start
            symptom_duration = st.selectbox(translate_text("When did symptoms start?", interface_lang_code) if interface_language != "English" else "When did symptoms start?",
                                          ["Today", "Yesterday", "2-3 days ago", "1 week ago", "2 weeks ago", "1 month ago", "More than 1 month ago"], key="duration")
            
            # Severity scale
            severity = st.slider(translate_text("Rate symptom severity (1=mild, 10=severe)", interface_lang_code) if interface_language != "English" else "Rate symptom severity (1=mild, 10=severe)",
                               1, 10, 5, key="severity")
            
            if st.form_submit_button(translate_text("Next: Lifestyle & Habits", interface_lang_code) if interface_language != "English" else "Next: Lifestyle & Habits"):
                if symptoms.strip():
                    st.session_state.patient_data.update({
                        'symptoms': symptoms,
                        'age': age,
                        'gender': gender,
                        'weight': weight,
                        'symptom_duration': symptom_duration,
                        'severity': severity
                    })
                    st.session_state.current_step = 2
                    st.rerun()
                else:
                    st.error(translate_text("Please describe your symptoms first.", interface_lang_code) if interface_language != "English" else "Please describe your symptoms first.")
    
    # Step 2: Lifestyle and Habits (The Dr. House Questions)
    elif st.session_state.current_step == 2:
        st.subheader(translate_text("Step 2: Lifestyle & Personal Habits", interface_lang_code) if interface_language != "English" else "Step 2: Lifestyle & Personal Habits")
        st.markdown(translate_text("*Please be honest - this information is crucial for accurate diagnosis*", interface_lang_code) if interface_language != "English" else "*Please be honest - this information is crucial for accurate diagnosis*")
        
        with st.form("step2_form"):
            # Smoking and alcohol
            col1, col2 = st.columns(2)
            with col1:
                smoking = st.selectbox(translate_text("Do you smoke?", interface_lang_code) if interface_language != "English" else "Do you smoke?",
                                     ["Never", "Occasionally", "Daily (1-10/day)", "Daily (10+ /day)", "Former smoker"], key="smoking")
                alcohol = st.selectbox(translate_text("Alcohol consumption?", interface_lang_code) if interface_language != "English" else "Alcohol consumption?",
                                     ["Never", "Rarely", "1-2 drinks/week", "3-7 drinks/week", "Daily", "Heavy drinking"], key="alcohol")
            
            with col2:
                drugs = st.selectbox(translate_text("Recreational drug use?", interface_lang_code) if interface_language != "English" else "Recreational drug use?",
                                   ["Never", "Rarely", "Occasionally", "Regular use", "Prefer not to say"], key="drugs")
                exercise = st.selectbox(translate_text("Exercise frequency?", interface_lang_code) if interface_language != "English" else "Exercise frequency?",
                                      ["Never", "Rarely", "1-2 times/week", "3-4 times/week", "Daily"], key="exercise")
            
            # Sexual activity and relationships
            st.markdown("**" + translate_text("Personal & Sexual Health", interface_lang_code) if interface_language != "English" else "Personal & Sexual Health" + "**")
            col3, col4 = st.columns(2)
            with col3:
                sexual_activity = st.selectbox(translate_text("Sexual activity status?", interface_lang_code) if interface_language != "English" else "Sexual activity status?",
                                             ["Not active", "Single partner", "Multiple partners", "Prefer not to say"], key="sexual_activity")
                contraception = st.selectbox(translate_text("Use of contraceptives/protection?", interface_lang_code) if interface_language != "English" else "Use of contraceptives/protection?",
                                           ["N/A", "Always", "Sometimes", "Never", "Prefer not to say"], key="contraception")
            
            with col4:
                pregnancy = st.selectbox(translate_text("Could you be pregnant? (if applicable)", interface_lang_code) if interface_language != "English" else "Could you be pregnant? (if applicable)",
                                       ["N/A", "No", "Possible", "Yes", "Don't know"], key="pregnancy")
                menstrual = st.selectbox(translate_text("Menstrual cycle regular? (if applicable)", interface_lang_code) if interface_language != "English" else "Menstrual cycle regular? (if applicable)",
                                       ["N/A", "Regular", "Irregular", "Stopped", "Don't track"], key="menstrual")
            
            # Sleep and stress
            sleep_hours = st.slider(translate_text("Average sleep hours per night", interface_lang_code) if interface_language != "English" else "Average sleep hours per night",
                                  2, 12, 7, key="sleep")
            stress_level = st.slider(translate_text("Current stress level (1=low, 10=high)", interface_lang_code) if interface_language != "English" else "Current stress level (1=low, 10=high)",
                                   1, 10, 5, key="stress")
            
            if st.form_submit_button(translate_text("Next: Work & Environment", interface_lang_code) if interface_language != "English" else "Next: Work & Environment"):
                st.session_state.patient_data.update({
                    'smoking': smoking,
                    'alcohol': alcohol,
                    'drugs': drugs,
                    'exercise': exercise,
                    'sexual_activity': sexual_activity,
                    'contraception': contraception,
                    'pregnancy': pregnancy,
                    'menstrual': menstrual,
                    'sleep_hours': sleep_hours,
                    'stress_level': stress_level
                })
                st.session_state.current_step = 3
                st.rerun()
    
    # Step 3: Work Environment and Exposures
    elif st.session_state.current_step == 3:
        st.subheader(translate_text("Step 3: Work Environment & Exposures", interface_lang_code) if interface_language != "English" else "Step 3: Work Environment & Exposures")
        
        with st.form("step3_form"):
            occupation = st.text_input(translate_text("What is your occupation?", interface_lang_code) if interface_language != "English" else "What is your occupation?", key="occupation")
            
            col1, col2 = st.columns(2)
            with col1:
                work_environment = st.selectbox(translate_text("Work environment", interface_lang_code) if interface_language != "English" else "Work environment",
                                              ["Office", "Factory/Industrial", "Healthcare", "Outdoor", "Home", "Laboratory", "Other"], key="work_env")
                chemical_exposure = st.selectbox(translate_text("Exposure to chemicals/toxins?", interface_lang_code) if interface_language != "English" else "Exposure to chemicals/toxins?",
                                               ["None", "Minimal", "Regular", "Heavy", "Don't know"], key="chemicals")
            
            with col2:
                radiation_exposure = st.selectbox(translate_text("Radiation exposure (X-rays, etc.)?", interface_lang_code) if interface_language != "English" else "Radiation exposure (X-rays, etc.)?",
                                                ["None", "Medical only", "Occupational", "Don't know"], key="radiation")
                travel_recent = st.selectbox(translate_text("Recent travel (last 3 months)?", interface_lang_code) if interface_language != "English" else "Recent travel (last 3 months)?",
                                           ["None", "Domestic", "International", "Tropical regions"], key="travel")
            
            # Living conditions
            living_conditions = st.selectbox(translate_text("Living conditions", interface_lang_code) if interface_language != "English" else "Living conditions",
                                           ["Alone", "Family", "Shared housing", "Institutional"], key="living")
            pets = st.text_input(translate_text("Do you have pets? What type?", interface_lang_code) if interface_language != "English" else "Do you have pets? What type?", key="pets")
            
            if st.form_submit_button(translate_text("Next: Medical History", interface_lang_code) if interface_language != "English" else "Next: Medical History"):
                st.session_state.patient_data.update({
                    'occupation': occupation,
                    'work_environment': work_environment,
                    'chemical_exposure': chemical_exposure,
                    'radiation_exposure': radiation_exposure,
                    'travel_recent': travel_recent,
                    'living_conditions': living_conditions,
                    'pets': pets
                })
                st.session_state.current_step = 4
                st.rerun()
    
    # Step 4: Medical History
    elif st.session_state.current_step == 4:
        st.subheader(translate_text("Step 4: Personal Medical History", interface_lang_code) if interface_language != "English" else "Step 4: Personal Medical History")
        
        with st.form("step4_form"):
            # Previous conditions
            previous_conditions = st.text_area(translate_text("Previous medical conditions/diagnoses", interface_lang_code) if interface_language != "English" else "Previous medical conditions/diagnoses",
                                             placeholder="e.g., diabetes, hypertension, depression", key="prev_conditions")
            
            # Surgeries
            surgeries = st.text_area(translate_text("Previous surgeries/procedures", interface_lang_code) if interface_language != "English" else "Previous surgeries/procedures",
                                   placeholder="Include dates if possible", key="surgeries")
            
            # Current medications
            medications = st.text_area(translate_text("Current medications (including supplements)", interface_lang_code) if interface_language != "English" else "Current medications (including supplements)",
                                     placeholder="Include dosages and frequency", key="medications")
            
            # Allergies
            allergies = st.text_area(translate_text("Known allergies (drugs, food, environmental)", interface_lang_code) if interface_language != "English" else "Known allergies (drugs, food, environmental)",
                                   placeholder="Specify reaction if known", key="allergies")
            
            # Recent medical care
            col1, col2 = st.columns(2)
            with col1:
                recent_doctor = st.selectbox(translate_text("Seen a doctor recently?", interface_lang_code) if interface_language != "English" else "Seen a doctor recently?",
                                           ["No", "Last week", "Last month", "Last 3 months"], key="recent_doctor")
                hospitalization = st.selectbox(translate_text("Recent hospitalization?", interface_lang_code) if interface_language != "English" else "Recent hospitalization?",
                                             ["Never", "Last year", "Last 5 years", "Long time ago"], key="hospitalization")
            
            with col2:
                blood_tests = st.selectbox(translate_text("Recent blood tests/lab work?", interface_lang_code) if interface_language != "English" else "Recent blood tests/lab work?",
                                         ["None", "Last month", "Last 3 months", "Last year"], key="blood_tests")
                vaccinations = st.selectbox(translate_text("Vaccination status up to date?", interface_lang_code) if interface_language != "English" else "Vaccination status up to date?",
                                          ["Yes", "Partially", "No", "Don't know"], key="vaccinations")
            
            if st.form_submit_button(translate_text("Next: Family History", interface_lang_code) if interface_language != "English" else "Next: Family History"):
                st.session_state.patient_data.update({
                    'previous_conditions': previous_conditions,
                    'surgeries': surgeries,
                    'medications': medications,
                    'allergies': allergies,
                    'recent_doctor': recent_doctor,
                    'hospitalization': hospitalization,
                    'blood_tests': blood_tests,
                    'vaccinations': vaccinations
                })
                st.session_state.current_step = 5
                st.rerun()
    
    # Step 5: Family History
    elif st.session_state.current_step == 5:
        st.subheader(translate_text("Step 5: Family History & Genetics", interface_lang_code) if interface_language != "English" else "Step 5: Family History & Genetics")
        
        with st.form("step5_form"):
            # Family medical history
            family_conditions = st.text_area(translate_text("Family medical history (parents, siblings, grandparents)", interface_lang_code) if interface_language != "English" else "Family medical history (parents, siblings, grandparents)",
                                           placeholder="e.g., heart disease, cancer, diabetes, mental health conditions", key="family_conditions")
            
            # Recent deaths or trauma
            col1, col2 = st.columns(2)
            with col1:
                recent_death = st.selectbox(translate_text("Recent death of close family/friend?", interface_lang_code) if interface_language != "English" else "Recent death of close family/friend?",
                                          ["No", "Last month", "Last 6 months", "Last year"], key="recent_death")
                family_trauma = st.selectbox(translate_text("Recent family trauma/crisis?", interface_lang_code) if interface_language != "English" else "Recent family trauma/crisis?",
                                           ["No", "Yes - minor", "Yes - major", "Prefer not to say"], key="family_trauma")
            
            with col2:
                adopted = st.selectbox(translate_text("Are you adopted?", interface_lang_code) if interface_language != "English" else "Are you adopted?",
                                     ["No", "Yes", "Partially", "Don't know"], key="adopted")
                genetic_testing = st.selectbox(translate_text("Ever had genetic testing?", interface_lang_code) if interface_language != "English" else "Ever had genetic testing?",
                                             ["No", "Yes - normal", "Yes - abnormal", "Results pending"], key="genetic_testing")
            
            # Mental health family history
            mental_health_family = st.text_area(translate_text("Family history of mental health conditions", interface_lang_code) if interface_language != "English" else "Family history of mental health conditions",
                                               placeholder="Depression, anxiety, bipolar, schizophrenia, addiction", key="mental_health_family")
            
            if st.form_submit_button(translate_text("Next: Mental Health", interface_lang_code) if interface_language != "English" else "Next: Mental Health"):
                st.session_state.patient_data.update({
                    'family_conditions': family_conditions,
                    'recent_death': recent_death,
                    'family_trauma': family_trauma,
                    'adopted': adopted,
                    'genetic_testing': genetic_testing,
                    'mental_health_family': mental_health_family
                })
                st.session_state.current_step = 6
                st.rerun()
    
    # Step 6: Mental Health and Psychological State
    elif st.session_state.current_step == 6:
        st.subheader(translate_text("Step 6: Mental Health & Psychological State", interface_lang_code) if interface_language != "English" else "Step 6: Mental Health & Psychological State")
        
        with st.form("step6_form"):
            # Current mental state
            col1, col2 = st.columns(2)
            with col1:
                mood = st.selectbox(translate_text("How would you describe your current mood?", interface_lang_code) if interface_language != "English" else "How would you describe your current mood?",
                                  ["Normal", "Depressed", "Anxious", "Irritable", "Euphoric", "Mixed"], key="mood")
                anxiety_level = st.slider(translate_text("Anxiety level (1=calm, 10=panic)", interface_lang_code) if interface_language != "English" else "Anxiety level (1=calm, 10=panic)",
                                        1, 10, 3, key="anxiety")
            
            with col2:
                depression_symptoms = st.selectbox(translate_text("Depression symptoms?", interface_lang_code) if interface_language != "English" else "Depression symptoms?",
                                                 ["None", "Mild", "Moderate", "Severe"], key="depression")
                therapy_history = st.selectbox(translate_text("History of therapy/counseling?", interface_lang_code) if interface_language != "English" else "History of therapy/counseling?",
                                             ["Never", "Past", "Current", "Considering"], key="therapy")
            
            # Psychiatric medications
            psychiatric_meds = st.text_area(translate_text("Current/past psychiatric medications", interface_lang_code) if interface_language != "English" else "Current/past psychiatric medications",
                                          placeholder="Antidepressants, anxiety medications, etc.", key="psych_meds")
            
            # Life changes
            major_life_changes = st.text_area(translate_text("Recent major life changes", interface_lang_code) if interface_language != "English" else "Recent major life changes",
                                            placeholder="Job loss, divorce, moving, new baby, etc.", key="life_changes")
            
            # Suicidal thoughts (handle carefully)
            col3, col4 = st.columns(2)
            with col3:
                suicidal_thoughts = st.selectbox(translate_text("Thoughts of self-harm?", interface_lang_code) if interface_language != "English" else "Thoughts of self-harm?",
                                               ["Never", "Rarely", "Sometimes", "Frequently", "Prefer not to say"], key="suicidal")
            with col4:
                substance_abuse = st.selectbox(translate_text("Substance abuse concerns?", interface_lang_code) if interface_language != "English" else "Substance abuse concerns?",
                                             ["No", "Mild concern", "Moderate concern", "Seeking help"], key="substance_abuse")
            
            if st.form_submit_button(translate_text("Next: Additional Details", interface_lang_code) if interface_language != "English" else "Next: Additional Details"):
                st.session_state.patient_data.update({
                    'mood': mood,
                    'anxiety_level': anxiety_level,
                    'depression_symptoms': depression_symptoms,
                    'therapy_history': therapy_history,
                    'psychiatric_meds': psychiatric_meds,
                    'major_life_changes': major_life_changes,
                    'suicidal_thoughts': suicidal_thoughts,
                    'substance_abuse': substance_abuse
                })
                st.session_state.current_step = 7
                st.rerun()
    
    # Step 7: Additional Symptoms and Context
    elif st.session_state.current_step == 7:
        st.subheader(translate_text("Step 7: Additional Context & Hidden Symptoms", interface_lang_code) if interface_language != "English" else "Step 7: Additional Context & Hidden Symptoms")
        
        with st.form("step7_form"):
            # The "House" questions - things patients often don't mention
            st.markdown("**" + translate_text("Please be completely honest about the following:", interface_lang_code) if interface_language != "English" else "Please be completely honest about the following:" + "**")
            
            # Hidden symptoms
            col1, col2 = st.columns(2)
            with col1:
                bathroom_habits = st.selectbox(translate_text("Any changes in bathroom habits?", interface_lang_code) if interface_language != "English" else "Any changes in bathroom habits?",
                                             ["No changes", "Constipation", "Diarrhea", "Frequent urination", "Difficulty urinating"], key="bathroom")
                appetite_changes = st.selectbox(translate_text("Appetite changes?", interface_lang_code) if interface_language != "English" else "Appetite changes?",
                                              ["Normal", "Increased", "Decreased", "Cravings", "Nausea"], key="appetite")
            
            with col2:
                weight_changes = st.selectbox(translate_text("Recent weight changes?", interface_lang_code) if interface_language != "English" else "Recent weight changes?",
                                            ["Stable", "Lost weight", "Gained weight", "Fluctuating"], key="weight_changes")
                energy_levels = st.selectbox(translate_text("Energy level changes?", interface_lang_code) if interface_language != "English" else "Energy level changes?",
                                           ["Normal", "More tired", "Less tired", "Restless", "Exhausted"], key="energy")
            
            # Sexual health specifics
            sexual_dysfunction = st.selectbox(translate_text("Any sexual health concerns?", interface_lang_code) if interface_language != "English" else "Any sexual health concerns?",
                                            ["None", "Decreased interest", "Performance issues", "Pain", "Prefer not to say"], key="sexual_dysfunction")
            
            # Pain and discomfort
            pain_description = st.text_area(translate_text("Describe any pain in detail", interface_lang_code) if interface_language != "English" else "Describe any pain in detail",
                                          placeholder="Location, type (sharp, dull, throbbing), timing, what makes it better/worse", key="pain_description")
            
            # Things they might be hiding
            embarrassing_symptoms = st.text_area(translate_text("Any symptoms you're embarrassed to mention?", interface_lang_code) if interface_language != "English" else "Any symptoms you're embarrassed to mention?",
                                                placeholder="Body odors, unusual discharge, skin changes, etc.", key="embarrassing")
            
            # Self-medication
            self_medication = st.text_area(translate_text("Any self-medication or home remedies tried?", interface_lang_code) if interface_language != "English" else "Any self-medication or home remedies tried?",
                                         placeholder="Over-the-counter drugs, herbs, online purchases", key="self_medication")
            
            # Financial concerns
            financial_stress = st.selectbox(translate_text("Financial stress affecting health decisions?", interface_lang_code) if interface_language != "English" else "Financial stress affecting health decisions?",
                                          ["No", "Mild", "Moderate", "Severe - avoiding care"], key="financial_stress")
            
            if st.form_submit_button(translate_text("Final Step: Review & Analyze", interface_lang_code) if interface_language != "English" else "Final Step: Review & Analyze"):
                st.session_state.patient_data.update({
                    'bathroom_habits': bathroom_habits,
                    'appetite_changes': appetite_changes,
                    'weight_changes': weight_changes,
                    'energy_levels': energy_levels,
                    'sexual_dysfunction': sexual_dysfunction,
                    'pain_description': pain_description,
                    'embarrassing_symptoms': embarrassing_symptoms,
                    'self_medication': self_medication,
                    'financial_stress': financial_stress
                })
                st.session_state.current_step = 8
                st.rerun()
    
    # Step 8: Final Review and Analysis
    elif st.session_state.current_step == 8:
        st.subheader(translate_text("Step 8: Complete Medical Profile & Analysis", interface_lang_code) if interface_language != "English" else "Step 8: Complete Medical Profile & Analysis")
        
        # Display collected data summary
        with st.expander(translate_text("📋 Your Complete Medical Profile", interface_lang_code) if interface_language != "English" else "📋 Your Complete Medical Profile"):
            st.json(st.session_state.patient_data)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button(translate_text("🧠 Analyze Complete Medical Profile", interface_lang_code) if interface_language != "English" else "🧠 Analyze Complete Medical Profile", type="primary"):
                with st.spinner(translate_text("Performing comprehensive medical analysis...", interface_lang_code) if interface_language != "English" else "Performing comprehensive medical analysis..."):
                    
                    # Compile comprehensive prompt
                    comprehensive_prompt = f"""
                    COMPREHENSIVE PATIENT MEDICAL ANALYSIS
                    
                    I need you to analyze this complete patient profile like Dr. Gregory House would - looking for connections, hidden patterns, and considering all possibilities including rare conditions.
                    
                    PATIENT PROFILE:
                    {json.dumps(st.session_state.patient_data, indent=2)}
                    
                    Please provide a thorough analysis including:
                    
                    1. PRIMARY DIFFERENTIAL DIAGNOSIS (5-7 most likely conditions)
                       - For each condition, explain how the patient's complete profile supports this diagnosis
                       - Include probability estimates
                    
                    2. RED FLAGS & CONCERNING PATTERNS
                       - Any combinations of symptoms/history that are particularly worrying
                       - Connections between lifestyle factors and symptoms
                    
                    3. HIDDEN CONNECTIONS
                       - How lifestyle factors (alcohol, drugs, stress, work environment) might relate to symptoms
                       - Family history implications
                       - Mental health connections to physical symptoms
                    
                    4. RECOMMENDED IMMEDIATE TESTS
                       - Blood work, imaging, specialized tests
                       - Prioritize based on most likely diagnoses
                    
                    5. SPECIALIST REFERRALS
                       - Which specialists to see first
                       - What information to provide them
                    
                    6. LIFESTYLE INTERVENTIONS
                       - Immediate changes that could help
                       - Risk factors to address
                    
                    7. FOLLOW-UP QUESTIONS
                       - Additional questions that might narrow down diagnosis
                       - Symptoms to monitor
                    
                    8. EMERGENCY INDICATORS
                       - Warning signs that require immediate medical attention
                       - When to go to ER vs urgent care vs primary doctor
                    
                    9. PSYCHOLOGICAL CONSIDERATIONS
                       - How mental health factors might be contributing
                       - Psychosomatic vs organic causes
                    
                    10. HOUSE-STYLE INSIGHTS
                        - Unusual connections or patterns that might be missed
                        - Questions about what the patient might still be hiding
                        - Alternative explanations for symptoms
                    
                    Be thorough, consider rare conditions, and don't accept simple explanations if the full picture doesn't fit.
                    """
                    
                    try:
                        # Translate prompt if needed
                        if interface_language != "English":
                            eng_prompt = translate_text(comprehensive_prompt, "en")
                            analysis = ask_llm(eng_prompt)
                        else:
                            analysis = ask_llm(comprehensive_prompt)
                        
                        # Create detailed results display
                        result_tab, profile_tab, doctor_tab, emergency_tab = st.tabs([
                            translate_text("🔍 Comprehensive Analysis", interface_lang_code) if interface_language != "English" else "🔍 Comprehensive Analysis",
                            translate_text("📋 Patient Profile", interface_lang_code) if interface_language != "English" else "📋 Patient Profile",
                            translate_text("👨‍⚕️ Find Specialists", interface_lang_code) if interface_language != "English" else "👨‍⚕️ Find Specialists",
                            translate_text("🚨 Emergency Info", interface_lang_code) if interface_language != "English" else "🚨 Emergency Info"])
                        
                        with result_tab:
                            # Translate and display analysis if needed
                            if interface_language != "English":
                                translated_analysis = translate_text(analysis, interface_lang_code)
                                st.markdown(translated_analysis)
                            else:
                                st.markdown(analysis)
                            
                            # Download report button
                            if st.button(translate_text("📄 Download Full Report", interface_lang_code) if interface_language != "English" else "📄 Download Full Report"):
                                report_content = f"""
COMPREHENSIVE MEDICAL ANALYSIS REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

PATIENT PROFILE:
{json.dumps(st.session_state.patient_data, indent=2)}

ANALYSIS:
{analysis}

DISCLAIMER: This analysis is for informational purposes only and does not constitute medical advice.
Always consult with qualified healthcare professionals for diagnosis and treatment.
"""
                                st.download_button(
                                    label=translate_text("Download Report", interface_lang_code) if interface_language != "English" else "Download Report",
                                    data=report_content,
                                    file_name=f"medical_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                                    mime="text/plain"
                                )
                        
                        with profile_tab:
                            st.markdown("### " + translate_text("Complete Patient Profile", interface_lang_code) if interface_language != "English" else "Complete Patient Profile")
                            
                            # Organized display of patient data
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown("**" + translate_text("Demographics & Basic Info", interface_lang_code) if interface_language != "English" else "Demographics & Basic Info" + "**")
                                st.write(f"Age: {st.session_state.patient_data.get('age', 'Not provided')}")
                                st.write(f"Gender: {st.session_state.patient_data.get('gender', 'Not provided')}")
                                st.write(f"Weight: {st.session_state.patient_data.get('weight', 'Not provided')} kg")
                                
                                st.markdown("**" + translate_text("Primary Symptoms", interface_lang_code) if interface_language != "English" else "Primary Symptoms" + "**")
                                st.write(f"Symptoms: {st.session_state.patient_data.get('symptoms', 'Not provided')}")
                                st.write(f"Duration: {st.session_state.patient_data.get('symptom_duration', 'Not provided')}")
                                st.write(f"Severity: {st.session_state.patient_data.get('severity', 'Not provided')}/10")
                            
                            with col2:
                                st.markdown("**" + translate_text("Lifestyle Factors", interface_lang_code) if interface_language != "English" else "Lifestyle Factors" + "**")
                                st.write(f"Smoking: {st.session_state.patient_data.get('smoking', 'Not provided')}")
                                st.write(f"Alcohol: {st.session_state.patient_data.get('alcohol', 'Not provided')}")
                                st.write(f"Exercise: {st.session_state.patient_data.get('exercise', 'Not provided')}")
                                st.write(f"Sleep: {st.session_state.patient_data.get('sleep_hours', 'Not provided')} hours")
                                st.write(f"Stress Level: {st.session_state.patient_data.get('stress_level', 'Not provided')}/10")
                        
                        with doctor_tab:
                            st.markdown("### " + translate_text("Find Healthcare Providers", interface_lang_code) if interface_language != "English" else "Find Healthcare Providers")
                            
                            location = st.text_input(translate_text("Enter your city/location", interface_lang_code) if interface_language != "English" else "Enter your city/location")
                            
                            if location:
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    if st.button(translate_text("🏥 Find Emergency Rooms", interface_lang_code) if interface_language != "English" else "🏥 Find Emergency Rooms"):
                                        search_url = f"https://www.google.com/maps/search/emergency+room+near+{location.replace(' ', '+')}"
                                        st.markdown(f"[{translate_text('Search Emergency Rooms', interface_lang_code) if interface_language != 'English' else 'Search Emergency Rooms'}]({search_url})")
                                
                                with col2:
                                    if st.button(translate_text("👨‍⚕️ Find Primary Care", interface_lang_code) if interface_language != "English" else "👨‍⚕️ Find Primary Care"):
                                        search_url = f"https://www.google.com/maps/search/primary+care+doctor+near+{location.replace(' ', '+')}"
                                        st.markdown(f"[{translate_text('Search Primary Care', interface_lang_code) if interface_language != 'English' else 'Search Primary Care'}]({search_url})")
                                
                                with col3:
                                    if st.button(translate_text("🏥 Find Urgent Care", interface_lang_code) if interface_language != "English" else "🏥 Find Urgent Care"):
                                        search_url = f"https://www.google.com/maps/search/urgent+care+near+{location.replace(' ', '+')}"
                                        st.markdown(f"[{translate_text('Search Urgent Care', interface_lang_code) if interface_language != 'English' else 'Search Urgent Care'}]({search_url})")
                        
                        with emergency_tab:
                            st.markdown("### " + translate_text("🚨 Emergency Information", interface_lang_code) if interface_language != "English" else "🚨 Emergency Information")
                            
                            st.error(translate_text("**SEEK IMMEDIATE EMERGENCY CARE IF YOU EXPERIENCE:**", interface_lang_code) if interface_language != "English" else "**SEEK IMMEDIATE EMERGENCY CARE IF YOU EXPERIENCE:**")
                            
                            emergency_symptoms = [
                                "Chest pain or pressure",
                                "Difficulty breathing or shortness of breath",
                                "Severe abdominal pain",
                                "Signs of stroke (face drooping, arm weakness, speech difficulty)",
                                "Severe headache with neck stiffness",
                                "High fever (>103°F/39.4°C)",
                                "Vomiting blood or blood in stool",
                                "Severe allergic reaction",
                                "Thoughts of harming yourself or others",
                                "Loss of consciousness or confusion"
                            ]
                            
                            for symptom in emergency_symptoms:
                                if interface_language != "English":
                                    translated_symptom = translate_text(symptom, interface_lang_code)
                                    st.write(f"• {translated_symptom}")
                                else:
                                    st.write(f"• {symptom}")
                            
                            st.markdown("---")
                            st.info(translate_text("**Emergency Numbers:**\n- Emergency Services: 911 (US)\n- Poison Control: 1-800-222-1222\n- Crisis Text Line: Text HOME to 741741", interface_lang_code) if interface_language != "English" else "**Emergency Numbers:**\n- Emergency Services: 911 (US)\n- Poison Control: 1-800-222-1222\n- Crisis Text Line: Text HOME to 741741")
                    
                    except Exception as e:
                        st.error(translate_text(f"Error during analysis: {str(e)}", interface_lang_code) if interface_language != "English" else f"Error during analysis: {str(e)}")
        
        with col2:
            if st.button(translate_text("🔄 Start Over", interface_lang_code) if interface_language != "English" else "🔄 Start Over"):
                # Reset all session state
                for key in ['patient_data', 'current_step', 'interview_complete']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
        
        # Progress completion
        st.session_state.interview_complete = True
                                                    
# --- Buy Medicine via LLM + Purchase Link (using Google search) ---
elif option == "💊 Buy Medicine":
    header_text = translate_text("🛒 Search Medicine and Purchase", interface_lang_code) if interface_language != "English" else "🛒 Search Medicine and Purchase"
    st.header(header_text)
    
    med_query_text = translate_text("Enter medicine name", interface_lang_code) if interface_language != "English" else "Enter medicine name"
    med_query = st.text_input(med_query_text)
    
    search_text = translate_text("Search", interface_lang_code) if interface_language != "English" else "Search"
    if st.button(search_text):
        with st.spinner(translate_text("Fetching details...", interface_lang_code)):
            # If non-English medicine name, translate to English for the LLM and search
            llm_med_query = med_query
            search_med_query = med_query
            
            if interface_language != "English":
                # For medicine names, we should be careful with translation
                eng_med_query = translate_text(med_query, "en")
                llm_med_query = eng_med_query
                search_med_query = eng_med_query
            
            medicine_info = ask_llm(f"Can you provide detailed information about {llm_med_query} including its uses, side effects, and recommended dosage?")
            
            info_header = translate_text(f"Information about {med_query}", interface_lang_code) if interface_language != "English" else f"Information about {med_query}"
            st.subheader(info_header)
            st.write(medicine_info)
            
            # If interface language is not English, translate and speak the medicine info
            if interface_language != "English":
                translated_info = translate_text(medicine_info, interface_lang_code)
                st.write(f"**{translate_text('Translated Information', interface_lang_code)}:**")
                st.write(translated_info)
                
                # Add TTS for translated info if enabled
                if enable_tts:
                    audio_path = text_to_speech(translated_info, interface_lang_code)
                    if audio_path:
                        st.audio(audio_path)

            # Link to Google search results for the medicine on MedPlusMart
            search_query = f"site:medplusmart.com {search_med_query}"
            google_search_link = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
            
            buy_text = translate_text(f"Buy {med_query} online from MedPlusMart (Google Search)", interface_lang_code) if interface_language != "English" else f"Buy {med_query} online from MedPlusMart (Google Search)"
            st.markdown(f"🔗 [{buy_text}]({google_search_link})")

# --- Find Nearby Hospitals/Pharmacies using OpenStreetMap ---
elif option == "🏥 Find Clinics & Pharmacies":
    header_text = translate_text("📍 Find Nearby Hospitals/Pharmacies/Doctors (OpenStreetMap)", interface_lang_code) if interface_language != "English" else "📍 Find Nearby Hospitals/Pharmacies/Doctors (OpenStreetMap)"
    st.header(header_text)

    # Translate place type options
    place_types = {"hospital": translate_text("hospital", interface_lang_code),
                   "pharmacy": translate_text("pharmacy", interface_lang_code),
                   "doctor": translate_text("doctor", interface_lang_code)}
    
    if interface_language == "English":
        place_type_display = ["hospital", "pharmacy", "doctor"]
        place_type_values = ["hospital", "pharmacy", "doctor"]
    else:
        place_type_display = [translate_text("hospital", interface_lang_code),
                             translate_text("pharmacy", interface_lang_code),
                             translate_text("doctor", interface_lang_code)]
        place_type_values = ["hospital", "pharmacy", "doctor"]
    
    select_type_text = translate_text("Select place type", interface_lang_code) if interface_language != "English" else "Select place type"
    place_type_index = st.selectbox(select_type_text, range(len(place_type_display)), format_func=lambda x: place_type_display[x])
    place_type = place_type_values[place_type_index]
    
    city_text = translate_text("Enter your city or location", interface_lang_code) if interface_language != "English" else "Enter your city or location"
    placeholder_text = translate_text("e.g. Mumbai", interface_lang_code) if interface_language != "English" else "e.g. Mumbai"
    city = st.text_input(city_text, placeholder=placeholder_text)

    search_text = translate_text("Search Nearby", interface_lang_code) if interface_language != "English" else "Search Nearby"
    if st.button(search_text):
        if not city:
            warning_text = translate_text("Please enter a city or location.", interface_lang_code) if interface_language != "English" else "Please enter a city or location."
            st.warning(warning_text)
        else:
            spinner_text = translate_text("Searching OpenStreetMap...", interface_lang_code) if interface_language != "English" else "Searching OpenStreetMap..."
            with st.spinner(spinner_text):
                # If non-English city name, translate to English for search
                search_city = city
                if interface_language != "English":
                    eng_city = translate_text(city, "en")
                    search_city = eng_city
                
                query = f"{place_type} near {search_city}"
                url = f"https://nominatim.openstreetmap.org/search.php?q={query}&format=json&limit=10"
                headers = {"User-Agent": "LocalHealthAssistant/1.0"}
                try:
                    res = requests.get(url, headers=headers)
                    data = res.json()

                    if not data:
                        no_results_text = translate_text("No results found.", interface_lang_code) if interface_language != "English" else "No results found."
                        st.warning(no_results_text)
                    else:
                        for place in data:
                            name = place.get("display_name", "Unknown")
                            lat = place.get("lat")
                            lon = place.get("lon")
                            
                            # Optionally translate place name
                            if interface_language != "English":
                                translated_name = translate_text(name, interface_lang_code)
                                st.write(f"**{translated_name}**")
                                st.write(f"*{name}*")  # Show original name as well
                            else:
                                st.write(f"**{name}**")
                                
                            map_text = translate_text("View on Map", interface_lang_code) if interface_language != "English" else "View on Map"
                            map_url = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=18/{lat}/{lon}"
                            st.markdown(f"[🗺 {map_text}]({map_url})")
                            st.markdown("---")
                except Exception as e:
                    error_text = translate_text(f"Error fetching data: {e}", interface_lang_code) if interface_language != "English" else f"Error fetching data: {e}"
                    st.error(error_text)


# --- App Navigator (NEW FEATURE) ---
elif option == "🏠 Home":
    header_text = translate_text("🔄 App Navigator", interface_lang_code) if interface_language != "English" else "🏠 Home"
    st.header(header_text)

    # Function definitions remain unchanged
    def is_port_in_use(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0

    def launch_streamlit_app(app_file, port):
        try:
            abs_path = os.path.abspath(app_file)
            python_exec = sys.executable
            if platform.system() == 'Windows':
                subprocess.Popen(f'start "" "{python_exec}" -m streamlit run "{abs_path}" --server.port={port}', shell=True)
            else:
                subprocess.Popen(f'nohup "{python_exec}" -m streamlit run "{abs_path}" --server.port={port} > /dev/null 2>&1 &', shell=True, executable='/bin/bash')
            return True
        except Exception as e:
            st.error(f"Error launching app: {e}")
            return False

    # Description
    description_text = translate_text(
        "Access all health-related applications from one place. Click on any tile to navigate to the corresponding application. If an app is not running, you can launch it from here.",
        interface_lang_code
    ) if interface_language != "English" else "Access all health-related applications from one place. Click on any tile to open or launch it."

    st.markdown(f"<p style='font-size:16px;'>{description_text}</p>", unsafe_allow_html=True)

    # App data
    other_apps = [
        {"name": "LLM Based Health Care Application", "icon": "📊", "description": "Analyze health records and symptoms using language models.", "port": 8501, "file": "app.py"},
        {"name": "Xray-Fracture Application", "icon": "🦴", "description": "View and diagnose X-ray fractures using AI.", "port": 8502, "file": "app1.py"},
        {"name": "L Hospital Planner and manager", "icon": "🏥", "description": "Manage and plan hospital operations.", "port": 8503, "file": "app2.py"},
        {"name": "Diet, Exec & Nutrition Planner", "icon": "🍎", "description": "Plan personalized diet and exercise routines.", "port": 8504, "file": "app3.py"},
        {"name": "Doctor Prescription writter", "icon": "📝", "description": "Generate and manage doctor prescriptions.", "port": 8505, "file": "app4.py"},
        {"name": "Medi Reminder ", "icon": "🧠", "description": "Medicine Reminder App", "port": 8506, "file": "app7.py"},
        {"name": "Mental wellness", "icon": "💊", "description": "Personalized Mental Wellness Coach.", "port": 8507, "file": "app6.py"},
        {"name": "LLM Settings", "icon": "🤖", "description": "LLM Settings to change and modify LLM on user requir...", "port": 8508, "file": "app5.py"},
        {"name": "Translator app", "icon": "🏥", "description": "Translator with a 3rd party observer ", "port": 8510, "file": "app9.py"},

    ]

    # Custom CSS
    st.markdown("""
    <style>
    .app-card {
    background: linear-gradient(135deg, #ff4e50, #1e90ff); /* red to blue gradient */
    border-radius: 15px;
    padding: 20px;
    margin-bottom: 15px;
    box-shadow: 2px 4px 12px rgba(0,0,0,0.1);
    transition: transform 0.2s ease-in-out;
    color: white; /* ensure text remains readable */
}
.app-card:hover {
    transform: translateY(-4px);
    box-shadow: 4px 6px 16px rgba(0,0,0,0.2);
}
    }
    .status-badge {
        font-size: 12px;
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: bold;
    }
    .active {
        background-color: #d4edda;
        color: #155724;
    }
    .inactive {
        background-color: #f8d7da;
        color: #721c24;
    }
    </style>
    """, unsafe_allow_html=True)

    # Session state
    if 'app_statuses' not in st.session_state:
        st.session_state.app_statuses = {}

    for app in other_apps:
        st.session_state.app_statuses[app['port']] = is_port_in_use(app['port'])

    # Display app tiles
    cols = st.columns(2)
    for i, app in enumerate(other_apps):
        col = cols[i % 2]
        with col:
            is_running = st.session_state.app_statuses[app['port']]
            status_text = "Active" if is_running else "Not Running"
            badge_class = "active" if is_running else "inactive"
            app_url = f"http://localhost:{app['port']}/"

            st.markdown(f"""
            <div class="app-card">
                <h4>{app['icon']} {app['name']}</h4>
                <p>{app['description']}</p>
                <span class="status-badge {badge_class}">{status_text}</span>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            if not is_running:
                if col1.button(f"Launch", key=f"launch_{app['port']}"):
                    with st.spinner(f"Launching {app['name']}..."):
                        success = launch_streamlit_app(app['file'], app['port'])
                        if success:
                            st.success(f"{app['name']} launched successfully.")
                        else:
                            st.error(f"Failed to launch {app['name']}.")
            if is_running:
                if col2.button("Open", key=f"open_{app['port']}"):
                    js = f"""<script>window.open("{app_url}", "_blank");</script>"""
                    st.markdown(js, unsafe_allow_html=True)
            else:
                col2.button("Open", key=f"open_{app['port']}_disabled", disabled=True)

    st.markdown("---")
    st.subheader("Current App")
    st.markdown("""
    <div style="background-color: #ad6a1d; border-radius: 15px; padding: 20px;">
        <h4>🩺 Local Health Assistant (This app)</h4>
        <p>Main health assistant with OCR, translation, symptom checking, and more.</p>
        <p style="color: green; font-weight: bold;">✓ Currently Active</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("System Status")
    if st.button("🔄 Refresh Status"):
        for app in other_apps:
            st.session_state.app_statuses[app['port']] = is_port_in_use(app['port'])
        st.success("Status refreshed")
        st.rerun()

    running_count = sum(st.session_state.app_statuses.values())
    st.info(f"{running_count} of {len(other_apps)} apps are currently running.")
