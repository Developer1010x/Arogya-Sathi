import requests
import os
import subprocess
import time
import platform
import psutil

DEFAULT_LLM = "llama3.2:latest"
LLM_CONFIG_FILE = "llm_model.txt"
OLLAMA_PORT = 11434
OLLAMA_HOST = "localhost"

def is_ollama_running():
    """Check if Ollama is running on the specified port."""
    try:
        response = requests.get(f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/tags", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def is_ollama_installed():
    """Check if Ollama is installed on the system."""
    return subprocess.run(["ollama", "--version"],
                         capture_output=True, text=True).returncode == 0

def install_ollama():
    """Install Ollama based on the operating system."""
    os_name = platform.system()
    print("Installing Ollama...")
    
    try:
        if os_name == "Darwin":  # macOS
            subprocess.run(["brew", "install", "ollama"], check=True)
        elif os_name == "Linux":
            # Install using the official script
            subprocess.run([
                "curl", "-fsSL", "https://ollama.com/install.sh"
            ], stdout=subprocess.PIPE, check=True)
            subprocess.run(["sh", "-c", "curl -fsSL https://ollama.com/install.sh | sh"],
                         shell=True, check=True)
        elif os_name == "Windows":
            print("Please install Ollama manually from https://ollama.com/download")
            return False
        
        print("Ollama installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install Ollama: {e}")
        return False

def start_ollama():
    """Start Ollama service."""
    os_name = platform.system()
    print("Starting Ollama service...")
    
    try:
        if os_name in ["Darwin", "Linux"]:
            # Start Ollama in background
            subprocess.Popen(["ollama", "serve"],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
        elif os_name == "Windows":
            subprocess.Popen(["ollama", "serve"],
                           creationflags=subprocess.CREATE_NEW_CONSOLE)
        
        # Wait for Ollama to start
        for _ in range(30):  # Wait up to 30 seconds
            if is_ollama_running():
                print("Ollama started successfully!")
                return True
            time.sleep(1)
        
        print("Ollama failed to start within timeout period")
        return False
    except Exception as e:
        print(f"Failed to start Ollama: {e}")
        return False

def update_ollama():
    """Update Ollama to the latest version."""
    print("Updating Ollama...")
    try:
        # Stop Ollama if running
        stop_ollama()
        time.sleep(2)
        
        # Update based on OS
        os_name = platform.system()
        if os_name == "Darwin":
            subprocess.run(["brew", "upgrade", "ollama"], check=True)
        elif os_name == "Linux":
            subprocess.run(["curl", "-fsSL", "https://ollama.com/install.sh", "|", "sh"],
                         shell=True, check=True)
        elif os_name == "Windows":
            print("Please update Ollama manually from https://ollama.com/download")
            return False
        
        print("Ollama updated successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to update Ollama: {e}")
        return False

def stop_ollama():
    """Stop Ollama service."""
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            if 'ollama' in proc.info['name'].lower():
                proc.terminate()
                proc.wait(timeout=5)
        print("Ollama stopped successfully!")
    except Exception as e:
        print(f"Error stopping Ollama: {e}")

def ensure_ollama_ready():
    """Ensure Ollama is installed, updated, and running."""
    print("Checking Ollama status...")
    
    # Check if Ollama is installed
    if not is_ollama_installed():
        print("Ollama not found. Installing...")
        if not install_ollama():
            return False
    
    # Update Ollama
    print("Updating Ollama...")
    update_ollama()
    
    # Start Ollama if not running
    if not is_ollama_running():
        print("Ollama not running. Starting...")
        if not start_ollama():
            return False
    else:
        print("Ollama is already running!")
    
    return True

def pull_model_if_needed(model_name):
    """Pull the model if it's not available locally."""
    try:
        # Check if model exists
        response = requests.get(f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/tags")
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [model['name'] for model in models]
            
            if model_name not in model_names:
                print(f"Model {model_name} not found locally. Pulling...")
                subprocess.run(["ollama", "pull", model_name], check=True)
                print(f"Model {model_name} pulled successfully!")
        
        return True
    except Exception as e:
        print(f"Error checking/pulling model: {e}")
        return False

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
    # Ensure Ollama is ready
    if not ensure_ollama_ready():
        return "Error: Could not establish Ollama connection"
    
    model = get_model_name()
    
    # Pull model if needed
    if not pull_model_if_needed(model):
        return f"Error: Could not ensure model {model} is available"
    
    try:
        response = requests.post(f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/generate",
                               json={
                                   "model": model,
                                   "prompt": prompt,
                                   "stream": False
                               }, timeout=60)
        response.raise_for_status()
        return response.json().get("response", "")
    except requests.exceptions.Timeout:
        return "Error: Request timed out"
    except requests.exceptions.RequestException as e:
        return f"Error communicating with LLM: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"

def test_llm_connection():
    """Test the LLM connection with a simple prompt."""
    test_response = ask_llm("Hello! Please respond with 'Connection successful!'")
    return "Connection successful!" in test_response

if __name__ == "__main__":
    # Test the setup
    print("Testing LLM setup...")
    if test_llm_connection():
        print("LLM setup is working correctly!")
    else:
        print("LLM setup test failed!")
