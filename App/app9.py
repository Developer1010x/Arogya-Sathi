import streamlit as st
import json
import datetime
from typing import List, Dict, Any
import re
import pandas as pd
from dataclasses import dataclass, asdict
import uuid
import requests
import os
import tempfile
import base64
try:
    from gtts import gTTS
    import pyttsx3
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    st.warning("⚠️ TTS libraries not available. Install with: pip install gtts pyttsx3")

# TTS Integration Functions
def get_gtts_language_code(lang_code: str) -> str:
    """Map our language codes to gTTS supported codes"""
    gtts_mapping = {
        "en": "en",
        "hi": "hi",
        "bn": "bn",
        "te": "te",
        "mr": "mr",
        "ta": "ta",
        "gu": "gu",
        "kn": "kn",
        "ml": "ml",
        "pa": "pa",
        "ur": "ur",
        "es": "es",
        "fr": "fr",
        "de": "de",
        "it": "it",
        "pt": "pt",
        "ar": "ar",
        "zh": "zh"
    }
    return gtts_mapping.get(lang_code, "en")

def text_to_speech_gtts(text: str, lang_code: str) -> str:
    """Convert text to speech using gTTS and return base64 audio"""
    if not GTTS_AVAILABLE:
        return None
    
    try:
        # Get appropriate language code for gTTS
        gtts_lang = get_gtts_language_code(lang_code)
        
        # Create gTTS object
        tts = gTTS(text=text, lang=gtts_lang, slow=False)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tts.save(tmp_file.name)
            
            # Read the audio file and encode as base64
            with open(tmp_file.name, "rb") as audio_file:
                audio_bytes = audio_file.read()
                audio_base64 = base64.b64encode(audio_bytes).decode()
            
            # Clean up temp file
            os.unlink(tmp_file.name)
            
            return audio_base64
            
    except Exception as e:
        st.error(f"TTS Error: {str(e)}")
        return None

def create_audio_player(audio_base64: str, key: str = None):
    """Create an audio player widget for the base64 encoded audio"""
    if audio_base64:
        audio_html = f"""
        <audio controls style="width: 100%;">
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            Your browser does not support the audio element.
        </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)

def text_to_speech_offline(text: str, lang_code: str = "en"):
    """Offline TTS using pyttsx3 (fallback option)"""
    if not GTTS_AVAILABLE:
        return False
    
    try:
        engine = pyttsx3.init()
        
        # Set voice properties based on language
        voices = engine.getProperty('voices')
        
        # Try to find appropriate voice for the language
        for voice in voices:
            if lang_code in voice.id.lower() or lang_code in voice.name.lower():
                engine.setProperty('voice', voice.id)
                break
        
        # Set speech rate and volume
        engine.setProperty('rate', 150)  # Speed of speech
        engine.setProperty('volume', 0.8)  # Volume level (0.0 to 1.0)
        
        # Speak the text
        engine.say(text)
        engine.runAndWait()
        return True
        
    except Exception as e:
        st.error(f"Offline TTS Error: {str(e)}")
        return False

DEFAULT_LLM = "llama3.2:latest"
LLM_CONFIG_FILE = "llm_model.txt"

def get_model_name():
    """Reads the LLM model name from file or returns the default."""
    try:
        if os.path.exists(LLM_CONFIG_FILE):
            with open(LLM_CONFIG_FILE, "r") as f:
                model_name = f.read().strip()
                if model_name:
                    return model_name
    except Exception as e:
        print(f"Error reading LLM config: {e}")
    return DEFAULT_LLM

def ask_llm(prompt):
    """Sends a prompt to the selected LLM model."""
    model = get_model_name()
    try:
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": model,
            "prompt": prompt,
            "stream": False
        })
        response.raise_for_status()
        return response.json().get("response", "")
    except Exception as e:
        return f"Error communicating with LLM: {e}"

def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    """LLM-powered translation function with support for Indian languages"""
    
    # Language code to full name mapping
    lang_names = {
        "en": "English",
        "hi": "Hindi",
        "bn": "Bengali",
        "te": "Telugu",
        "mr": "Marathi",
        "ta": "Tamil",
        "gu": "Gujarati",
        "kn": "Kannada",
        "ml": "Malayalam",
        "pa": "Punjabi",
        "or": "Odia",
        "as": "Assamese",
        "ur": "Urdu",
        "es": "Spanish",
        "fr": "French",
        "de": "German",
        "it": "Italian",
        "pt": "Portuguese",
        "ar": "Arabic",
        "zh": "Chinese"
    }
    
    source_lang_name = lang_names.get(source_lang, source_lang)
    target_lang_name = lang_names.get(target_lang, target_lang)
    
    prompt = f"""
    You are a professional medical translator. Translate the following text from {source_lang_name} to {target_lang_name}.
    
    CRITICAL INSTRUCTIONS:
    1. Provide ONLY the direct translation
    2. Do NOT add any explanations, notes, or additional text
    3. Do NOT use phrases like "Note:", "Translation:", or any meta-commentary
    4. Maintain medical accuracy and terminology
    5. Preserve the tone appropriate for doctor-patient communication
    6. For Indian languages, use proper script without romanization
    7. Return ONLY the translated text, nothing else
    
    Text to translate: "{text}"
    """
    
    try:
        translation = ask_llm(prompt).strip()
        
        # Clean up the response more aggressively
        # Remove common prefixes that might appear
        prefixes_to_remove = [
            "Translation:",
            "translation:",
            "The translation is:",
            "Here is the translation:",
            "Note:",
            "Answer:",
            "Response:",
        ]
        
        for prefix in prefixes_to_remove:
            if translation.startswith(prefix):
                translation = translation[len(prefix):].strip()
        
        # Remove any sentences that start with "Note:" or similar
        lines = translation.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if not any(line.startswith(prefix.lower()) or line.startswith(prefix)
                      for prefix in ["note:", "Note:", "explanation:", "Explanation:",
                                   "this means:", "This means:", "in", "In "]):
                cleaned_lines.append(line)
        
        # Take only the first non-empty line (should be the translation)
        for line in cleaned_lines:
            if line.strip():
                translation = line.strip()
                break
        
        # Additional cleanup: remove parenthetical explanations
        if '(' in translation and ')' in translation:
            # Remove content in parentheses that looks like explanations
            translation = re.sub(r'\s*\([^)]*(?:meaning|literally|which means|i\.e\.|that is)[^)]*\)', '', translation, flags=re.IGNORECASE)
            # Remove any remaining empty parentheses
            translation = re.sub(r'\s*\(\s*\)', '', translation)
        
        return translation.strip() if translation.strip() else f"[Translation Error: {text}]"
        
    except Exception as e:
        return f"[Translation Error: {text}]"

def analyze_medical_conversation(conversation: List[Dict]) -> Dict:
    """LLM-powered medical conversation analysis"""
    
    # Prepare conversation text for analysis
    conversation_text = ""
    for msg in conversation:
        conversation_text += f"{msg['speaker'].upper()}: {msg['content']}\n"
    
    analysis_prompt = f"""
    You are an expert medical AI assistant specialized in analyzing doctor-patient conversations for potential issues, anomalies, and diagnosis problems. 

    Please analyze the following medical conversation and identify:

    1. DIAGNOSIS ISSUES (High Priority):
       - Prescriptions without proper examination
       - Potential misdiagnosis based on symptoms
       - Missing critical diagnostic steps
       - Inappropriate treatment recommendations
       - Drug interactions or contraindications not considered

    2. CONVERSATION ANOMALIES (Medium Priority):
       - Contradictory statements about symptoms
       - Incomplete medical history collection
       - Missing allergy information
       - Inconsistent pain or symptom descriptions
       - Communication gaps or misunderstandings

    3. RECOMMENDATIONS:
       - Specific actionable suggestions for improvement
       - Additional tests or examinations needed
       - Follow-up care recommendations

    CONVERSATION TO ANALYZE:
    {conversation_text}

    Please respond in the following JSON format:
    {{
        "diagnosis_issues": [
            {{
                "type": "Issue description",
                "message": "Relevant message from conversation",
                "speaker": "doctor/patient",
                "severity": "High/Medium/Low",
                "explanation": "Why this is an issue"
            }}
        ],
        "anomalies": [
            {{
                "type": "Anomaly description", 
                "message": "Relevant message from conversation",
                "speaker": "doctor/patient",
                "severity": "High/Medium/Low",
                "explanation": "Why this is concerning"
            }}
        ],
        "recommendations": [
            "Specific recommendation 1",
            "Specific recommendation 2"
        ],
        "overall_assessment": "Brief overall assessment of the conversation quality and safety",
        "risk_score": 5
    }}

    Provide only the JSON response, no additional text.
    """
    
    try:
        response = ask_llm(analysis_prompt)
        
        # Try to parse JSON response
        try:
            # Clean the response to extract JSON
            response = response.strip()
            if response.startswith("```json"):
                response = response.replace("```json", "").replace("```", "").strip()
            elif response.startswith("```"):
                response = response.replace("```", "").strip()
            
            analysis_data = json.loads(response)
            
            # Add timestamps to issues and anomalies
            for issue in analysis_data.get('diagnosis_issues', []):
                issue['timestamp'] = datetime.datetime.now().isoformat()
            
            for anomaly in analysis_data.get('anomalies', []):
                anomaly['timestamp'] = datetime.datetime.now().isoformat()
            
            return {
                'anomalies': analysis_data.get('anomalies', []),
                'diagnosis_issues': analysis_data.get('diagnosis_issues', []),
                'recommendations': analysis_data.get('recommendations', []),
                'overall_risk_score': analysis_data.get('risk_score', 0),
                'overall_assessment': analysis_data.get('overall_assessment', ''),
                'analysis_timestamp': datetime.datetime.now().isoformat()
            }
            
        except json.JSONDecodeError as e:
            # Fallback: Create a basic analysis if JSON parsing fails
            return {
                'anomalies': [{
                    'type': 'Analysis parsing error',
                    'message': 'Could not parse LLM response',
                    'speaker': 'system',
                    'timestamp': datetime.datetime.now().isoformat(),
                    'severity': 'Low',
                    'explanation': f'JSON parsing error: {str(e)}'
                }],
                'diagnosis_issues': [],
                'recommendations': ['Review conversation manually due to analysis error'],
                'overall_risk_score': 1,
                'overall_assessment': 'Analysis could not be completed automatically',
                'analysis_timestamp': datetime.datetime.now().isoformat()
            }
            
    except Exception as e:
        # Fallback for LLM communication errors
        return {
            'anomalies': [{
                'type': 'LLM Communication Error',
                'message': 'Could not connect to LLM service',
                'speaker': 'system',
                'timestamp': datetime.datetime.now().isoformat(),
                'severity': 'Low',
                'explanation': f'LLM error: {str(e)}'
            }],
            'diagnosis_issues': [],
            'recommendations': ['Check LLM service connection'],
            'overall_risk_score': 0,
            'overall_assessment': 'Analysis unavailable due to technical issues',
            'analysis_timestamp': datetime.datetime.now().isoformat()
        }

@dataclass
class ConversationMessage:
    id: str
    speaker: str  # 'doctor' or 'patient'
    content: str
    original_language: str
    translated_content: str
    target_language: str
    timestamp: str
    audio_original: str = None  # Base64 encoded audio
    audio_translated: str = None  # Base64 encoded audio

class MedicalTranslationApp:
    def __init__(self):
        if 'conversation_history' not in st.session_state:
            st.session_state.conversation_history = []
        if 'current_session_id' not in st.session_state:
            st.session_state.current_session_id = str(uuid.uuid4())
        if 'analysis_reports' not in st.session_state:
            st.session_state.analysis_reports = []

    def add_message(self, speaker: str, content: str, original_lang: str, target_lang: str, enable_tts: bool = True):
        """Add a new message to the conversation with optional TTS"""
        translated_content = translate_text(content, original_lang, target_lang)
        
        # Generate TTS audio if enabled
        audio_original = None
        audio_translated = None
        
        if enable_tts and GTTS_AVAILABLE:
            with st.spinner("Generating audio..."):
                audio_original = text_to_speech_gtts(content, original_lang)
                if translated_content and not translated_content.startswith("[Translation Error"):
                    audio_translated = text_to_speech_gtts(translated_content, target_lang)
        
        message = ConversationMessage(
            id=str(uuid.uuid4()),
            speaker=speaker,
            content=content,
            original_language=original_lang,
            translated_content=translated_content,
            target_language=target_lang,
            timestamp=datetime.datetime.now().isoformat(),
            audio_original=audio_original,
            audio_translated=audio_translated
        )
        
        st.session_state.conversation_history.append(asdict(message))

    def display_conversation(self):
        """Display the conversation history with translations and audio"""
        st.subheader("💬 Conversation History")
        
        if not st.session_state.conversation_history:
            st.info("No conversation yet. Start by adding messages below.")
            return
        
        for msg in st.session_state.conversation_history:
            speaker_icon = "👨‍⚕️" if msg['speaker'] == 'doctor' else "🤒"
            
            with st.container():
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown(f"**{speaker_icon} {msg['speaker'].title()} ({msg['original_language'].upper()})**")
                    st.write(msg['content'])
                    
                    # Audio player for original message
                    if msg.get('audio_original') and GTTS_AVAILABLE:
                        st.markdown("🔊 **Listen (Original):**")
                        create_audio_player(msg['audio_original'], key=f"orig_{msg['id']}")
                    
                    st.caption(f"Time: {msg['timestamp'][:19]}")
                
                with col2:
                    st.markdown(f"**Translation ({msg['target_language'].upper()})**")
                    st.write(msg['translated_content'])
                    
                    # Audio player for translated message
                    if msg.get('audio_translated') and GTTS_AVAILABLE:
                        st.markdown("🔊 **Listen (Translation):**")
                        create_audio_player(msg['audio_translated'], key=f"trans_{msg['id']}")
                
                st.divider()
        
        # TTS Settings
        st.subheader("🔊 Audio Settings")
        
        tts_enabled = st.checkbox("Enable Text-to-Speech", value=True, help="Generate audio for messages and translations")
        
        if GTTS_AVAILABLE:
            st.success("✅ TTS Available (gTTS + pyttsx3)")
        else:
            st.error("❌ TTS Not Available")
            st.info("Install with: `pip install gtts pyttsx3`")
        
        st.divider()

    def generate_analysis_report(self):
        """Generate AI analysis report of the conversation"""
        if not st.session_state.conversation_history:
            st.warning("No conversation to analyze.")
            return None
        
        # Prepare conversation for analysis
        conversation_for_analysis = [
            {
                'speaker': msg['speaker'],
                'content': msg['content'],
                'timestamp': msg['timestamp']
            }
            for msg in st.session_state.conversation_history
        ]
        
        # Perform AI analysis
        analysis = analyze_medical_conversation(conversation_for_analysis)
        
        # Create comprehensive report
        report = {
            'session_id': st.session_state.current_session_id,
            'conversation_summary': {
                'total_messages': len(st.session_state.conversation_history),
                'doctor_messages': len([m for m in st.session_state.conversation_history if m['speaker'] == 'doctor']),
                'patient_messages': len([m for m in st.session_state.conversation_history if m['speaker'] == 'patient']),
                'languages_used': list(set([m['original_language'] for m in st.session_state.conversation_history])),
                'conversation_duration': self.get_conversation_duration()
            },
            'analysis': analysis,
            'full_conversation': st.session_state.conversation_history,
            'report_generated': datetime.datetime.now().isoformat()
        }
        
        st.session_state.analysis_reports.append(report)
        return report

    def get_conversation_duration(self):
        """Calculate conversation duration"""
        if len(st.session_state.conversation_history) < 2:
            return "N/A"
        
        start_time = datetime.datetime.fromisoformat(st.session_state.conversation_history[0]['timestamp'])
        end_time = datetime.datetime.fromisoformat(st.session_state.conversation_history[-1]['timestamp'])
        duration = end_time - start_time
        
        return str(duration).split('.')[0]  # Remove microseconds

    def display_analysis_report(self, report: Dict, report_key_suffix: str = ""):
        """Display the analysis report with unique keys for buttons"""
        st.subheader("📊 AI Analysis Report")
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Messages", report['conversation_summary']['total_messages'])
        
        with col2:
            st.metric("Risk Score", f"{report['analysis']['overall_risk_score']}/10")
        
        with col3:
            st.metric("Anomalies Found", len(report['analysis']['anomalies']))
        
        with col4:
            st.metric("Diagnosis Issues", len(report['analysis']['diagnosis_issues']))
        
        # Detailed analysis
        if report['analysis']['diagnosis_issues']:
            st.subheader("🚨 Diagnosis Issues")
            for issue in report['analysis']['diagnosis_issues']:
                severity_color = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}
                st.error(f"{severity_color.get(issue['severity'], '⚪')} **{issue['type']}** (Severity: {issue['severity']})")
                st.write(f"**Speaker:** {issue['speaker'].title()}")
                st.write(f"**Message:** {issue['message']}")
                st.write(f"**Explanation:** {issue['explanation']}")
                st.write(f"**Time:** {issue['timestamp'][:19]}")
                st.divider()
        
        if report['analysis']['anomalies']:
            st.subheader("⚠️ Anomalies Detected")
            for anomaly in report['analysis']['anomalies']:
                severity_color = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}
                st.warning(f"{severity_color.get(anomaly['severity'], '⚪')} **{anomaly['type']}** (Severity: {anomaly['severity']})")
                st.write(f"**Speaker:** {anomaly['speaker'].title()}")
                st.write(f"**Message:** {anomaly['message']}")
                st.write(f"**Explanation:** {anomaly['explanation']}")
                st.write(f"**Time:** {anomaly['timestamp'][:19]}")
                st.divider()
        
        if report['analysis']['recommendations']:
            st.subheader("💡 AI Recommendations")
            for i, rec in enumerate(report['analysis']['recommendations'], 1):
                st.info(f"{i}. {rec}")
        
        # Export options with unique keys
        st.subheader("📥 Export Report")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Download JSON Report", key=f"json_download_{report_key_suffix}_{report['session_id'][:8]}"):
                st.download_button(
                    label="Download Full Report (JSON)",
                    data=json.dumps(report, indent=2),
                    file_name=f"medical_analysis_report_{report['session_id'][:8]}.json",
                    mime="application/json",
                    key=f"json_dl_btn_{report_key_suffix}_{report['session_id'][:8]}"
                )
        
        with col2:
            if st.button("Download Summary (CSV)", key=f"csv_download_{report_key_suffix}_{report['session_id'][:8]}"):
                summary_data = {
                    'Session_ID': [report['session_id']],
                    'Total_Messages': [report['conversation_summary']['total_messages']],
                    'Risk_Score': [report['analysis']['overall_risk_score']],
                    'Anomalies_Count': [len(report['analysis']['anomalies'])],
                    'Diagnosis_Issues_Count': [len(report['analysis']['diagnosis_issues'])],
                    'Languages_Used': [', '.join(report['conversation_summary']['languages_used'])],
                    'Report_Generated': [report['report_generated']]
                }
                
                df = pd.DataFrame(summary_data)
                csv = df.to_csv(index=False)
                
                st.download_button(
                    label="Download Summary (CSV)",
                    data=csv,
                    file_name=f"medical_summary_{report['session_id'][:8]}.csv",
                    mime="text/csv",
                    key=f"csv_dl_btn_{report_key_suffix}_{report['session_id'][:8]}"
                )

def main():
    st.set_page_config(
        page_title="Medical Translation & Monitoring System",
        page_icon="🏥",
        layout="wide"
    )
    
    st.title("🏥 Medical Translation & AI Monitoring System")
    st.markdown("Real-time translation between doctors and patients with AI-powered conversation analysis")
    
    app = MedicalTranslationApp()
    
    # Sidebar for session management
    with st.sidebar:
        st.header("🔧 Session Controls")
        
        st.info(f"**Current Session:** {st.session_state.current_session_id[:8]}...")
        
        if st.button("🔄 New Session"):
            st.session_state.conversation_history = []
            st.session_state.current_session_id = str(uuid.uuid4())
            st.rerun()
        
        st.divider()
        
        # Language settings
        st.subheader("🌍 Language Settings")
        
        languages = {
            # Indian Languages
            "हिंदी (Hindi)": "hi",
            "বাংলা (Bengali)": "bn",
            "తెలుగు (Telugu)": "te",
            "मराठी (Marathi)": "mr",
            "தமிழ் (Tamil)": "ta",
            "ગુજરાતી (Gujarati)": "gu",
            "ಕನ್ನಡ (Kannada)": "kn",
            "മലയാളം (Malayalam)": "ml",
            "ਪੰਜਾਬੀ (Punjabi)": "pa",
            "ଓଡ଼ିଆ (Odia)": "or",
            "অসমীয়া (Assamese)": "as",
            "اردو (Urdu)": "ur",
            
            # International Languages
            "English": "en",
            "Español (Spanish)": "es",
            "Français (French)": "fr",
            "Deutsch (German)": "de",
            "Italiano (Italian)": "it",
            "Português (Portuguese)": "pt",
            "العربية (Arabic)": "ar",
            "中文 (Chinese)": "zh"
        }
        
        doctor_lang = st.selectbox("Doctor's Language", list(languages.keys()), index=0)
        patient_lang = st.selectbox("Patient's Language", list(languages.keys()), index=1)
        
        st.divider()
        
        # Quick stats
        if st.session_state.conversation_history:
            st.subheader("📈 Session Stats")
            st.write(f"Messages: {len(st.session_state.conversation_history)}")
            st.write(f"Duration: {app.get_conversation_duration()}")
    
    # Main interface tabs
    tab1, tab2, tab3, tab4 = st.tabs(["💬 Live Conversation", "📊 AI Analysis", "📋 Reports History", "ℹ️ Help"])
    
    with tab1:
        # Message input section
        st.subheader("💬 Add New Message")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            speaker = st.radio("Speaker", ["doctor", "patient"], horizontal=True)
            message_input = st.text_area(
                f"Message in {doctor_lang if speaker == 'doctor' else patient_lang}:",
                placeholder=f"Type your message in {doctor_lang if speaker == 'doctor' else patient_lang}...",
                height=100
            )
        
        with col2:
            st.write("**Translation Settings**")
            source_lang = languages[doctor_lang] if speaker == 'doctor' else languages[patient_lang]
            target_lang = languages[patient_lang] if speaker == 'doctor' else languages[doctor_lang]
            
            st.write(f"From: {doctor_lang if speaker == 'doctor' else patient_lang}")
            st.write(f"To: {patient_lang if speaker == 'doctor' else doctor_lang}")
            
            if st.button("➕ Add Message", type="primary"):
                if message_input.strip():
                    app.add_message(
                        speaker,
                        message_input.strip(),
                        source_lang,
                        target_lang,
                        st.session_state.get('tts_enabled', True)
                    )
                    st.success("Message added and translated!")
                    st.rerun()
                else:
                    st.error("Please enter a message.")
        
        st.divider()
        
        # Display conversation
        app.display_conversation()
    
    with tab2:
        st.subheader("🤖 AI Analysis & Monitoring")
        
        if st.button("🔍 Analyze Current Conversation", type="primary"):
            if st.session_state.conversation_history:
                with st.spinner("Analyzing conversation for anomalies and diagnosis issues..."):
                    report = app.generate_analysis_report()
                    if report:
                        app.display_analysis_report(report, "current_analysis")
            else:
                st.warning("No conversation to analyze. Please add some messages first.")
        
        # Display latest report if available
        if st.session_state.analysis_reports:
            latest_report = st.session_state.analysis_reports[-1]
            with st.expander("📊 Latest Analysis Report", expanded=True):
                app.display_analysis_report(latest_report, "latest_report")
                
                # Show overall assessment if available
                if latest_report['analysis'].get('overall_assessment'):
                    st.subheader("🎯 Overall Assessment")
                    st.info(latest_report['analysis']['overall_assessment'])
    
    with tab3:
        st.subheader("📋 Analysis Reports History")
        
        if not st.session_state.analysis_reports:
            st.info("No analysis reports generated yet.")
        else:
            for i, report in enumerate(reversed(st.session_state.analysis_reports)):
                with st.expander(f"Report #{len(st.session_state.analysis_reports) - i} - Risk Score: {report['analysis']['overall_risk_score']}/10"):
                    app.display_analysis_report(report, f"history_{i}")
    
    with tab4:
        st.subheader("ℹ️ How to Use This System")
        
        st.markdown("""
        ### 🎯 Purpose
        This system facilitates communication between doctors and patients who speak different languages while monitoring the conversation for potential medical issues using advanced AI analysis.
        
        ### 🌏 Supported Languages
        **Indian Languages:**
        - हिंदी (Hindi) 
        - বাংলা (Bengali)
        - తెలుగు (Telugu)
        - मराठी (Marathi)
        - தமிழ் (Tamil)
        - ગુજરાતી (Gujarati)
        - ಕನ್ನಡ (Kannada)
        - മലയാളം (Malayalam)
        - ਪੰਜਾਬੀ (Punjabi)
        - ଓଡ଼ିଆ (Odia)
        - অসমীয়া (Assamese)
        - اردو (Urdu)
        
        **International Languages:**
        English, Spanish, French, German, Italian, Portuguese, Arabic, Chinese
        
        ### 🚀 How to Use
        1. **Set Languages**: Choose the doctor's and patient's languages in the sidebar
        2. **Add Messages**: Use the "Live Conversation" tab to add translated messages
        3. **AI Monitoring**: The system continuously analyzes conversations using your local LLM for:
           - Potential misdiagnoses and treatment issues
           - Medical anomalies and inconsistencies  
           - Missing critical information
           - Communication gaps
        4. **Generate Reports**: Click "Analyze Current Conversation" for detailed AI analysis
        5. **Export Data**: Download comprehensive reports in JSON or CSV format
        
      
        ### ⚙️ Technical Requirements
        - **Local LLM Server**: Requires Ollama running on `localhost:11434`
        - **Model Configuration**: Uses model specified in `llm_model.txt` or defaults to `llama3.2:latest`
 
        
      
        
        ### ⚠️ Important Notes
        - This system assists medical professionals but does not replace clinical judgment
        - All processing happens locally - no data is sent to external servers
        - The AI analysis provides suggestions that should be verified by medical professionals
        - For Indian languages, cultural and linguistic context is preserved in translations
        - Always follow institutional protocols for medical decision-making
        """)
        
        # LLM Status Check
        st.subheader("🔧 System Status")
        col1, col2 = st.columns(2)
        
        with col1:
            # Check LLM connection
            try:
                test_response = ask_llm("Hello")
                if "Error" not in test_response:
                    st.success("✅ LLM Service: Connected")
                    st.info(f"📋 Current Model: {get_model_name()}")
                else:
                    st.error("❌ LLM Service: Connection Error")
                    st.error(test_response)
            except Exception as e:
                st.error("❌ LLM Service: Not Available")
                st.error(f"Error: {str(e)}")
        
        with col2:
            st.info("💡 **Setup Instructions:**")
            st.markdown("""
            Rerun Config.py for packages <Deve Comm 2012, Check the Arogya-Sathi/App path also this col 1,2 to be removed for final git push>
            """)
            
            # TTS Status
            st.subheader("🔊 TTS Status")
            if GTTS_AVAILABLE:
                st.success("✅ Text-to-Speech: Available")
                st.info("🌐 Google TTS: Online")
                st.info("💻 System TTS: Offline")
            else:
                st.error("❌ Text-to-Speech: Not Available")
                st.error("Run: `pip install gtts pyttsx3`")

if __name__ == "__main__":
    main()
