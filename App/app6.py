import streamlit as st
from llm import ask_llm
import time

st.set_page_config(page_title="Mental Health Companion", page_icon="🧠", layout="centered")

st.title("🧘‍♂️ Mental Health Companion")
st.markdown("Chat with your friendly mental wellness bot to get emotional support, mindfulness tips, or simply a space to talk.")

st.info("💡 This bot is under testing and it cant  substitute for professional mental health care under testing")

# Mood check-in
mood = st.selectbox("How are you feeling today?", ["😊 Happy", "😔 Sad", "😠 Angry", "😨 Anxious", "😴 Tired", "😐 Neutral"])
st.markdown("You can start chatting with the bot below:")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.text_input("You:", key="user_input")

if st.button("Send"):
    if user_input.strip():
        st.session_state.chat_history.append(("You", user_input))
        full_context = "\n".join([f"{role}: {msg}" for role, msg in st.session_state.chat_history])

        prompt = f"""You are a compassionate, calm, and thoughtful mental health assistant. 
You respond in a friendly tone, offering support, breathing exercises, and mindfulness advice.

Here's the conversation so far:
{full_context}

Respond supportively to the last user message."""
        with st.spinner("Bot is thinking..."):
            try:
                bot_reply = ask_llm(prompt)
                st.session_state.chat_history.append(("Companion", bot_reply))
            except Exception as e:
                st.error(f"Bot error: {e}")

# Display chat
for role, msg in st.session_state.chat_history:
    if role == "You":
        st.markdown(f"**You:** {msg}")
    else:
        st.markdown(f"**🧠 Companion:** {msg}")
