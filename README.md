# 🩺 Arogya-Sathi: An LLM-Powered Multilingual Healthcare Platform

**Arogya-Sathi** is an AI-driven, modular, and multilingual healthcare support system designed to deliver personalized, intelligent, and inclusive medical assistance. Built using Streamlit, OCR, YOLO, and Large Language Models (LLMs) like LLaMA 3.2, the platform empowers users—especially in underserved communities—with accessible, end-to-end healthcare tools.

---

## 🚀 Features

- **🧠 LLM Integration**  
  Ask health-related questions, get symptom-based triage, and understand reports with contextual responses powered by LLaMA 3.2 (configurable via Ollama).

- **📝 OCR + Report Summary**  
  Upload scanned medical reports and receive simplified, easy-to-understand summaries.

- **🩺 Symptom Checker & Checker+**  
  An 8-stage guided triage system providing probabilistic disease estimation and doctor referral recommendations.

- **📷 X-ray Analyzer**  
  Analyze medical images using advanced models such as YOLOv8, VGG, or ResNet with adjustable confidence levels.

- **💊 Medicine Information & Reminders**  
  Access detailed medicine info, side effects, and export medication reminders in .ics or .csv formats.

- **📍 Nearby Hospital/Pharmacy Locator**  
  Real-time location-based assistance via OpenStreetMap API to find nearby healthcare facilities.

- **📄 Prescription Writer**  
  A doctor-oriented AI-assisted prescription generation tool with PDF export capability.

- **🍎 Diet Planner**  
  AI-generated personalized diet and fitness plans tailored to individual health needs.

- **🧘 Mental Wellness Chat**  
  An empathetic conversational bot for emotional health support and mental wellness.

- **🌐 Multilingual Support**  
  Supports 12+ Indian languages and several foreign languages with real-time translation.

- **⚙️ LLM Settings Panel**  
  Easily switch between LLMs for testing, performance tuning, and flexibility.

---

## 🏗️ Tech Stack

- **Frontend:** Streamlit  
- **Backend:** Python, LangChain, FastAPI (optional)  
- **AI/ML Models:** LLaMA 3.2, YOLOv8, ResNet, VGG  
- **NLP:** Ollama (for local LLM hosting), HuggingFace Transformers  
- **OCR:** Tesseract  
- **Maps:** OpenStreetMap API  
- **File Outputs:** PDF, CSV, ICS

---

## 🧪 Project Status

- ✅ **TRL-5 Validated:** Functionally integrated and tested in simulated clinical environments  
- 🧩 **Modular Architecture:** All sub-apps work independently  
- 📱 **Cross-Device Compatibility:** Accessible via browser on mobile, desktop, or tablet  
- 💡 **Lightweight Deployment:** Runs smoothly on devices with 8–16 GB RAM; Raspberry Pi tested

---

## 📂 Modules Breakdown

<!-- Add details about each module here, e.g.: -->

- **Symptom Checker**  
- **OCR & Report Summary**  
- **X-ray Analyzer**  
- **Medicine Info & Reminder**  
- **Nearby Locator**  
- **Prescription Writer**  
- **Diet Planner**  
- **Mental Wellness Chat**  
- **Multilingual Support**

---

## 📥 Installation & Usage

<!-- Add instructions here for cloning repo, installing dependencies, running the app, etc. -->

```bash
git clone https://github.com/your-repo/arogya-sathi.git
cd arogyasathi
pip install -r requirements.txt
streamlit run app.py
```



---

## 🤝 Creators

- [S Prajwall Narayana](https://github.com/Developer1010x)  
- [Smit_Patel](https://github.com/smitpatel0x9)

---

## 🤝 Contribution

Contributions are welcome! Please open an issue or submit a pull request for any improvements, suggestions, or bug fixes.

> **Note:**  
> This project was developed and tested on a variety of systems, including MacBooks (Intel i5 and Apple M4) and Microsoft Surface devices running Ubuntu. Most packages used are compatible across these platforms.  
> 
> - Python 3.12 and 3.13 are supported.
> - Refer to the `req_txt/` folder for specific package requirements.
> - The application is designed with cross-platform compatibility in mind.
> 
> ⚠️ Please avoid committing all changes directly to the `main` branch. Use feature branches and pull requests for collaborative development.

---

## 🙏 Acknowledgments

Special thanks to the creators and communities behind:  
LLaMA, Ollama, YOLOv8, Streamlit, Tesseract, OpenStreetMap, HuggingFace, and all open-source contributors who make innovation like this possible.
