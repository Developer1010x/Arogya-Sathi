import streamlit as st
import tempfile
import os
import time
from gtts import gTTS  # No longer used, but left here in case you re-enable
from fpdf import FPDF

# Import with error handling
try:
    from deep_translator import GoogleTranslator
    from llm import ask_llm  # Your custom module
except ImportError as e:
    st.error(f"Missing required package: {e}")
    st.stop()

# Supported languages
available_languages = {
    "English": "en", "Spanish": "es", "French": "fr", "Hindi": "hi", "Tamil": "ta",
    "Telugu": "te", "Mandarin": "zh-cn", "German": "de", "Italian": "it", "Portuguese": "pt",
    "Arabic": "ar", "Bengali": "bn", "Russian": "ru", "Japanese": "ja", "Korean": "ko",
    "Dutch": "nl", "Turkish": "tr", "Greek": "el", "Swedish": "sv", "Polish": "pl",
    "Ukrainian": "uk", "Punjabi": "pa", "Marathi": "mr", "Gujarati": "gu", "Malayalam": "ml",
    "Kannada": "kn", "Hebrew": "he", "Thai": "th", "Vietnamese": "vi", "Indonesian": "id",
    "Swahili": "sw", "Filipino": "tl",
}

# UI Translation helper
@st.cache_data(show_spinner=False)
def translate_ui(text, lang_code):
    if lang_code == "en":
        return text
    try:
        return GoogleTranslator(source="auto", target=lang_code).translate(text)
    except:
        return text

def translate_text(text, target_language):
    try:
        translator = GoogleTranslator(source='auto', target=target_language)
        return translator.translate(text)
    except Exception as e:
        st.error(f"Translation error: {e}")
        return text

def generate_pdf(content, user_data):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "Diet, Exercise & Nutrition Planner Assistant", ln=True, align='C')
        pdf.line(10, 30, 200, 30)
        pdf.ln(15)

        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "User Information:", ln=True)

        pdf.set_font("Arial", '', 11)
        for label, value in {
            "Age": f"{user_data['age']} years",
            "Weight": f"{user_data['weight']} kg",
            "Height": f"{user_data['height']} cm",
            "BMI": f"{user_data['bmi']:.1f} ({user_data['bmi_category']})",
            "Health conditions": user_data['conditions'],
            "Lifestyle & Profession": user_data['lifestyle'],
            "Country/Community": user_data['country'],
        }.items():
            pdf.cell(0, 8, f"{label}: {value}", ln=True)

        pdf.ln(10)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(10)

        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "Personalized Health Recommendations", ln=True)
        pdf.set_font("Arial", '', 11)

        for line in content.split('\n'):
            line = ''.join(char for char in line if ord(char) < 128)
            if line.strip().startswith(('##', '1.', '2.', '3.')):
                pdf.set_font("Arial", 'B', 12)
                pdf.ln(5)
                pdf.cell(0, 8, line.replace('#', '').strip(), ln=True)
                pdf.set_font("Arial", '', 11)
            else:
                pdf.multi_cell(0, 6, line)

        pdf.set_y(-30)
        pdf.set_font("Arial", 'I', 8)
        pdf.cell(0, 10, "This plan is AI-generated and should be reviewed by a healthcare professional.", ln=True, align='C')
        pdf.cell(0, 10, f"Generated on: {time.strftime('%Y-%m-%d')}", ln=True, align='C')

        file_path = os.path.join(tempfile.gettempdir(), "health_recommendations.pdf")
        pdf.output(file_path)
        return file_path
    except Exception as e:
        st.error(f"PDF generation error: {e}")
        return None

def calculate_bmi(weight, height):
    height_m = height / 100
    bmi = weight / (height_m ** 2)
    if bmi < 18.5:
        return bmi, "Underweight"
    elif bmi < 25:
        return bmi, "Normal weight"
    elif bmi < 30:
        return bmi, "Overweight"
    else:
        return bmi, "Obese"

# App setup
st.set_page_config(
    page_title="Diet, Exercise & Nutrition Planner Assistant",
    page_icon="🥗",
    layout="centered"
)

# Language selection
language = st.selectbox("Select output language", list(available_languages.keys()))
lang_code = available_languages[language]
_ = lambda x: translate_ui(x, lang_code)

# Sidebar
with st.sidebar:
    st.title(_("About the Assistant"))
    st.info(_("""
    This AI Health Assistant provides personalized recommendations based on your inputs.

    **Note:**
    - These are AI-generated suggestions
    - Consult a professional before making changes
    - This is not medical advice
    """))
    st.markdown("---")
    st.markdown(_("### How it works"))
    st.markdown(_("1. Enter your details\n2. Get AI-powered insights\n3. Download your plan"))

# Main UI
st.title(_("Diet, Exercise & Nutrition Planner Assistant"))
st.markdown(_("Get personalized recommendations for diet, exercise, and wellness."))

tab1, tab2 = st.tabs([_("Input Your Details"), _("Your Recommendations")])

with tab1:
    st.subheader(_("Personal Details"))
    col1, col2, col3 = st.columns(3)
    with col1:
        age = st.number_input(_("Age (years)"), min_value=1, max_value=120, step=1)
    with col2:
        weight = st.number_input(_("Weight (kg)"), min_value=1.0, max_value=300.0, step=0.5)
    with col3:
        height = st.number_input(_("Height (cm)"), min_value=30.0, max_value=250.0, step=0.5)

    if age and weight and height:
        bmi, bmi_category = calculate_bmi(weight, height)
        st.info(_(f"BMI: {bmi:.1f} - Category: {bmi_category}"))

    st.subheader(_("Additional Information"))
    disease_history = st.text_area(_("Any previous diseases or health conditions?"), placeholder=_("e.g. diabetes, joint pain"))
    lifestyle = st.text_area(_("Describe your lifestyle and profession"), placeholder=_("e.g. desk job, shift worker"))
    country = st.text_input(_("Country or Community"), placeholder=_("e.g. India, USA"))

    st.subheader(_("Output Preferences"))
    generate_button = st.button(_("Generate Health Recommendations"))

if generate_button:
    if all([age, weight, height, lifestyle, country]):
        with st.spinner(_("Generating your health recommendations...")):
            bmi, bmi_category = calculate_bmi(weight, height)
            user_data = {
                "age": age, "weight": weight, "height": height,
                "bmi": bmi, "bmi_category": bmi_category,
                "conditions": disease_history or "None reported",
                "lifestyle": lifestyle, "country": country
            }

            prompt = f"""
You are a health assistant AI. Based on the following inputs, generate a comprehensive personalized health recommendation.

Age: {age} years
Weight: {weight} kg
Height: {height} cm
BMI: {bmi:.1f} ({bmi_category})
Health conditions: {disease_history or 'None reported'}
Lifestyle & Profession: {lifestyle}
Country/Community: {country}

Include:
1. A suitable **diet plan**
2. A **personalized exercise routine**
3. **Mental wellness advice**

Use markdown headers (##) and structured formatting.
"""
            try:
                response = ask_llm(prompt)
                with tab2:
                    st.success(_("✅ Recommendations generated!"))
                    st.markdown("## 🧾 " + _("AI-Generated Health Plan"))
                    st.markdown(response)

                    if lang_code != "en":
                        with st.spinner(_(f"Translating to {language}...")):
                            translated = translate_text(response, lang_code)
                            st.markdown("## 🌐 " + _(f"Translated Output ({language})"))
                            st.markdown(translated)

                    with st.spinner(_("Preparing PDF download...")):
                        pdf_path = generate_pdf(response, user_data)
                        if pdf_path:
                            with open(pdf_path, "rb") as f:
                                st.download_button(
                                    label=_("📥 Download Complete Health Plan (PDF)"),
                                    data=f,
                                    file_name=f"health_plan_{user_data['country']}_{age}yrs.pdf",
                                    mime="application/pdf"
                                )
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning(_("⚠️ Please complete all required fields."))

with tab2:
    if "response" not in locals():
        st.info(_("Generate your health plan to see recommendations here."))

st.markdown("---")
st.caption(_("AI Health Assistant | Not a substitute for professional medical advice"))
