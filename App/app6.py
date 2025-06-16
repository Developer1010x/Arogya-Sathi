import streamlit as st
from gtts import gTTS
from deep_translator import GoogleTranslator
from gtts.lang import tts_langs
import tempfile
import os

# Set page configuration FIRST
st.set_page_config(page_title="Mental Health Companion", layout="centered")

# Supported languages
available_languages = {
    "English": "en", "Spanish": "es", "French": "fr", "Hindi": "hi", "Tamil": "ta",
    "Telugu": "te", "Mandarin (Chinese)": "zh-cn", "German": "de", "Italian": "it",
    "Portuguese": "pt", "Arabic": "ar", "Bengali": "bn", "Russian": "ru",
    "Japanese": "ja", "Korean": "ko", "Dutch": "nl", "Turkish": "tr",
    "Greek": "el", "Swedish": "sv", "Polish": "pl", "Ukrainian": "uk",
    "Punjabi": "pa", "Marathi": "mr", "Gujarati": "gu", "Malayalam": "ml",
    "Kannada": "kn", "Hebrew": "he", "Thai": "th", "Vietnamese": "vi",
    "Indonesian": "id"
}

# TTS-supported languages
tts_supported_langs = tts_langs()

# Translate interface text
def _(text):
    if selected_language != "English":
        try:
            return GoogleTranslator(source='auto', target=target_lang_code).translate(text)
        except:
            return text
    return text

# Translate any given message
def translate_text(text, lang_code):
    try:
        return GoogleTranslator(source='auto', target=lang_code).translate(text)
    except Exception as e:
        st.error(f"Translation error: {e}")
        return text

# Generate TTS audio
def text_to_speech(text, lang_code):
    try:
        if not text.strip():
            return None
        if lang_code not in tts_supported_langs:
            lang_code = "en"
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tts = gTTS(text=text, lang=lang_code)
            tts.save(tmp.name)
            return tmp.name
    except Exception as e:
        st.error(f"TTS error: {e}")
        return None

# Sidebar
st.sidebar.title("🌍 Language Settings")
selected_language = st.sidebar.selectbox("Choose Interface Language", list(available_languages.keys()))
target_lang_code = available_languages[selected_language]
enable_tts = st.sidebar.checkbox("🔊 Enable Text-to-Speech", value=True)

# Title
st.title(_("🧘‍♀️ Mental Health Companion"))
st.markdown(_("Welcome! This space is for emotional support, mindfulness, and self-check-ins."))

st.info(_("💡 Note: This tool does not replace professional mental health care."))

# Mood input
mood = st.selectbox(_("How are you feeling today?"),
                    [_("😊 Happy"), _("😔 Sad"), _("😠 Angry"), _("😨 Anxious"), _("😴 Tired"), _("😐 Neutral")])
st.markdown(_("You can start talking to the bot below."))

# Session state for chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Chat input
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input(_("You:"))
    submitted = st.form_submit_button(_("Send"))

if submitted and user_input:
    st.session_state.messages.append(("user", user_input))

    # Dummy bot response (replace with LLM if needed)
    bot_reply = f"I'm here for you. I understand you're feeling {mood.lower()}. Try a short breathing exercise: Inhale for 4, hold for 4, exhale for 6."

    # Translate reply if needed
    if selected_language != "English":
        bot_reply = translate_text(bot_reply, target_lang_code)

    st.session_state.messages.append(("bot", bot_reply))

# Chat history
st.markdown("---")
for i, (role, msg) in enumerate(st.session_state.messages):
    if role == "user":
        st.markdown(f"**🧍 You:** {msg}")
    else:
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f"**🤖 Companion:** {msg}")
        with col2:
            if enable_tts:
                if st.button("🔊", key=f"tts_{i}"):
                    audio_path = text_to_speech(msg, target_lang_code)
                    if audio_path:
                        st.audio(audio_path, format="audio/mp3")

# Clear chat
if st.session_state.messages:
    if st.button(_("🗑️ Clear Chat")):
        st.session_state.messages = []
        st.experimental_rerun()

# Wellness tips
with st.expander(_("🌿 Quick Wellness Tips")):
    tips = [
        _("Take 5 deep breaths: In for 4, hold for 4, out for 6"),
        _("Practice the 5-4-3-2-1 grounding technique"),
        _("Try a 2-minute mindfulness meditation"),
        _("Step outside for fresh air"),
        _("Drink a glass of water mindfully")
    ]
    for tip in tips:
        st.markdown(f"- {tip}")

# Emergency resources
with st.expander(_("🆘 Emergency Resources")):
    st.markdown(_("""**If you're in crisis, please reach out:**
- National Suicide Prevention Lifeline (US): 988
- Crisis Text Line: Text HOME to 741741
- IASP (International help): https://www.iasp.info/resources/Crisis_Centres/

This chatbot does not replace professional care.
"""))
