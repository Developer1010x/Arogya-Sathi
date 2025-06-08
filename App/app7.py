import streamlit as st
from datetime import datetime, timedelta
import pytz
from ics import Calendar, Event
import io
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
import qrcode
import requests
import os

# ---------------------------
# Streamlit Configuration
# ---------------------------
st.set_page_config(page_title="💊 Medicine Reminder", layout="centered")
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>💊 Smart Medicine Reminder + AI Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Set your reminders, export to calendar, and ask AI for guidance!</p>", unsafe_allow_html=True)
st.markdown("---")

# ---------------------------
# Timezone & Helpers
# ---------------------------
timezone = "Asia/Kolkata"
tz = pytz.timezone(timezone)

timing_map = {
    "Morning": 9,
    "Afternoon": 13,
    "Evening": 18,
    "Night": 21
}

# ---------------------------
# LLM Helper Functions
# ---------------------------
DEFAULT_LLM = "llama3.2:latest"
LLM_CONFIG_FILE = "llm_model.txt"

def get_model_name():
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
        return f"❌ Error communicating with LLM: {e}"

# ---------------------------
# Medicine Input
# ---------------------------
st.header("📝 Prescription Details")

num_meds = st.number_input("How many medicines are you taking?", min_value=1, max_value=10, value=1)

medicines = []

for i in range(num_meds):
    st.markdown(f"<h4 style='color:#333;'>💊 Medicine {i+1}</h4>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    name = col1.text_input("Name", key=f"name_{i}")
    dosage = col2.text_input("Dosage", key=f"dosage_{i}")

    col3, col4 = st.columns(2)
    timings = col3.multiselect("When to take it?", ["Morning", "Afternoon", "Evening", "Night"], key=f"timing_{i}")
    duration = col4.number_input("For how many days?", 1, 30, key=f"duration_{i}")

    custom_time = st.time_input("⏰ Custom Time (Optional)", key=f"time_{i}")
    pill_image = st.file_uploader("📷 Upload Pill Image (optional)", type=["jpg", "png"], key=f"img_{i}")

    st.markdown("<hr style='margin-top: 1em;'>", unsafe_allow_html=True)

    if name and dosage and timings:
        medicines.append({
            "name": name,
            "dosage": dosage,
            "timings": timings,
            "duration": duration,
            "custom_time": custom_time,
            "image": pill_image
        })

# ---------------------------
# Generate Reminders
# ---------------------------
submit = st.button("📅 Generate Calendar File")

if submit:
    if not medicines:
        st.warning("⚠️ Please fill out medicine details first.")
        st.stop()

    st.success("✅ Generating your reminders...")
    cal = Calendar()
    today = datetime.now(tz).date()
    events_df = []

    for med in medicines:
        for timing in med['timings']:
            for day in range(med['duration']):
                base_time = datetime.combine(today + timedelta(days=day), datetime.min.time())

                if med["custom_time"]:
                    start_time = base_time.replace(hour=med["custom_time"].hour, minute=med["custom_time"].minute)
                else:
                    start_time = base_time + timedelta(hours=timing_map[timing])

                start_time = tz.localize(start_time)
                end_time = start_time + timedelta(minutes=15)

                event = Event()
                event.name = f"{med['name']} - {med['dosage']}"
                event.begin = start_time
                event.end = end_time
                event.description = f"Take {med['name']} ({med['dosage']})"
                cal.events.add(event)

                events_df.append({
                    "Medicine": med["name"],
                    "Dosage": med["dosage"],
                    "Time": start_time.strftime("%Y-%m-%d %H:%M"),
                    "Day": f"Day {day+1}"
                })

    ics_content = str(cal)
    ics_file = io.StringIO(ics_content)
    st.download_button("📥 Download Calendar (.ics)", data=ics_file.getvalue(), file_name="medicine_reminders.ics")

    st.markdown("### 📱 QR Code for Mobile Import")
    qr = qrcode.make("https://example.com/medicine_reminders.ics")  # Replace with real link if hosted
    buf = io.BytesIO()
    qr.save(buf)
    st.image(buf, caption="Scan with your phone (if hosted)", width=200)

    st.markdown("### 📅 Your Schedule")
    df = pd.DataFrame(events_df)
    st.dataframe(df)

    st.markdown("### 📊 Frequency Chart")
    chart_data = df["Medicine"].value_counts()
    fig, ax = plt.subplots()
    chart_data.plot(kind="barh", ax=ax, color="#4CAF50")
    ax.set_xlabel("Times Scheduled")
    ax.set_ylabel("Medicine")
    ax.set_title("Medicine Frequency")
    st.pyplot(fig)

    st.markdown("### 🧪 Pill Images")
    for med in medicines:
        if med["image"]:
            st.image(Image.open(med["image"]), caption=med["name"], width=150)

# ---------------------------
# LLM Assistant
# ---------------------------
st.markdown("---")
st.header("🤖 Ask the Health AI")

user_question = st.text_area("💬 Ask anything about your medicines, dosage, side effects, etc.", placeholder="e.g., What is the best time to take Vitamin D?")

if st.button("🧠 Ask AI"):
    if user_question.strip():
        with st.spinner("Thinking..."):
            response = ask_llm(user_question)
            st.success("AI Response:")
            st.markdown(f"```\n{response}\n```")
    else:
        st.warning("⚠️ Please type your question.")
