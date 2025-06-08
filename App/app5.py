# app6.py

import streamlit as st
import subprocess
import os

LLM_CONFIG_FILE = "llm_model.txt"
DEFAULT_MODELS = ["llama3.2:latest", "mistral:latest", "gemma:latest", "custom"]

st.set_page_config(page_title="LLM Manager", page_icon="🧠")
st.title("🧠 Local LLM Manager (Ollama)")

# --- 1. Read current model ---
def get_current_model():
    try:
        with open(LLM_CONFIG_FILE, "r") as f:
            return f.read().strip()
    except:
        return None

# --- 2. Save model ---
def save_model(model_name):
    with open(LLM_CONFIG_FILE, "w") as f:
        f.write(model_name.strip())

# --- 3. List local Ollama models ---
def list_ollama_models():
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout
        else:
            return "No models found or Ollama not installed."
    except FileNotFoundError:
        return "Ollama not installed."

# --- 4. Pull model ---
def pull_model(model_name):
    try:
        result = subprocess.run(["ollama", "pull", model_name], capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return str(e)

# --- 5. Test model via llm.py ---
def test_model(prompt):
    try:
        from llm import ask_llm
        return ask_llm(prompt)
    except Exception as e:
        return f"Error testing model: {e}"

# --- UI Section ---

st.subheader("🎛️ Model Selection")
model_choice = st.selectbox("Choose a model:", DEFAULT_MODELS)
custom_model = ""

if model_choice == "custom":
    custom_model = st.text_input("Enter custom model name (e.g. dolphin:latest)")

final_model = custom_model.strip() if model_choice == "custom" else model_choice

if st.button("💾 Save Model"):
    if final_model:
        save_model(final_model)
        st.success(f"Model '{final_model}' saved.")
    else:
        st.warning("Please enter a model name.")

st.divider()

st.subheader("🔎 Ollama Model List")
if st.button("📃 List Installed Models"):
    output = list_ollama_models()
    st.code(output)

st.subheader("⬇️ Pull a Model")
model_to_pull = st.text_input("Model to pull (e.g. llama3.2, mistral)", key="pull")
if st.button("⬇️ Pull from Ollama"):
    output = pull_model(model_to_pull)
    st.text_area("Pull Output", output, height=150)

st.divider()

st.subheader("🧪 Test Your LLM")
prompt = st.text_area("Enter a prompt to test your current model", height=100)
if st.button("🚀 Test Prompt"):
    result = test_model(prompt)
    st.text_area("LLM Response", result, height=150)

st.divider()

st.subheader("🗑️ Utilities")
if st.button("🧹 Clear Selected Model"):
    try:
        os.remove(LLM_CONFIG_FILE)
        st.success("Model selection reset.")
    except:
        st.warning("Nothing to clear.")

current_model = get_current_model()
if current_model:
    st.info(f"🔧 Currently selected model: `{current_model}`")
else:
    st.info("No model selected. Using default: `llama3.2:latest`")

st.divider()

st.subheader("📘 About LLMs in Ollama")
st.markdown("""
- ✅ Ollama runs LLMs locally (CPU or GPU).
- 🔄 You can use `ollama pull modelname` to download more.
- 💡 Common models:
  - `llama3.2:latest` (Meta)
  - `mistral:latest` (lightweight + fast)
  - `gemma:latest` (Google)
  - `codellama`, `dolphin`, etc.
- 🌐 [Browse Ollama Models](https://ollama.com/library)
""")

