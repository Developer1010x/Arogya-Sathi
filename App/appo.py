import streamlit as st
import subprocess
import sys
import os
import platform
import socket
import time
import webbrowser
from threading import Timer

# Page configuration
st.set_page_config(
    page_title="Arogya Sathi - Health Suite Launcher",
    page_icon="🏥",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for beautiful UI
st.markdown("""
<style>
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom background and styling */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    /* Main container */
    .main-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 40px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        text-align: center;
        margin: 20px 0;
        backdrop-filter: blur(10px);
    }
    
    /* Title styling */
    .app-title {
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Subtitle */
    .app-subtitle {
        font-size: 1.3rem;
        color: #666;
        margin-bottom: 30px;
        font-weight: 300;
    }
    
    /* Feature cards */
    .feature-card {
        background: linear-gradient(135deg, #ff6b6b, #4ecdc4);
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin: 10px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        transform: translateY(0);
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.2);
    }
    
    /* Launch button */
    .launch-container {
        margin: 40px 0;
    }
    
    /* Status indicator */
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-active {
        background-color: #4CAF50;
        box-shadow: 0 0 10px #4CAF50;
    }
    
    .status-inactive {
        background-color: #f44336;
        box-shadow: 0 0 10px #f44336;
    }
    
    /* Progress bar */
    .progress-container {
        background-color: #f0f0f0;
        border-radius: 10px;
        overflow: hidden;
        margin: 20px 0;
    }
    
    .progress-bar {
        height: 8px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        border-radius: 10px;
        animation: progress 3s ease-in-out;
    }
    
    @keyframes progress {
        0% { width: 0%; }
        100% { width: 100%; }
    }
    
    /* Footer */
    .app-footer {
        margin-top: 40px;
        padding-top: 20px;
        border-top: 1px solid #eee;
        color: #888;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

def is_port_in_use(port):
    """Check if a port is in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def launch_main_app():
    """Launch the main app on port 8501"""
    try:
        app_path = os.path.join(os.getcwd(), "app.py")
        
        # Check if app.py exists
        if not os.path.exists(app_path):
            st.error(f"app.py not found at: {app_path}")
            return False
        
        python_exec = sys.executable
        
        if platform.system() == 'Windows':
            # Windows command
            cmd = f'"{python_exec}" -m streamlit run "{app_path}" --server.port=8501 --server.headless=true'
            subprocess.Popen(cmd, shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            # macOS/Linux command
            cmd = [python_exec, "-m", "streamlit", "run", app_path, "--server.port=8501", "--server.headless=true"]
            subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)
        
        return True
    except Exception as e:
        st.error(f"Error launching main app: {e}")
        st.error(f"Current directory: {os.getcwd()}")
        st.error(f"Python executable: {sys.executable}")
        return False

def open_main_app():
    """Open the main app in browser"""
    webbrowser.open("http://localhost:8501")

def close_launcher():
    """Close the launcher app"""
    # This will stop the Streamlit server
    os._exit(0)

# Main UI
st.markdown("""
<div class="main-container">
    <h1 class="app-title">🏥 Arogya Sathi</h1>
    <p class="app-subtitle">Your Complete Health Management Suite</p>
</div>
""", unsafe_allow_html=True)

# Feature highlights
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-card">
        <h3>📊 Health Analytics</h3>
        <p>AI-powered health record analysis and symptom checking</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <h3>🦴 Medical Imaging</h3>
        <p>X-ray fracture detection and medical image analysis</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <h3>🏥 Management Tools</h3>
        <p>Hospital planning, prescriptions, and wellness tracking</p>
    </div>
    """, unsafe_allow_html=True)

# Check if main app is running
main_app_running = is_port_in_use(8501)

# Status display
st.markdown("<div class='launch-container'>", unsafe_allow_html=True)

if main_app_running:
    st.markdown("""
    <div style="text-align: center; padding: 20px; background-color: #d4edda; border-radius: 10px; margin: 20px 0;">
        <span class="status-indicator status-active"></span>
        <strong>Main Health App is Running</strong>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Open Health Suite", type="primary", use_container_width=True):
            with st.spinner("Opening main application..."):
                time.sleep(1)
                open_main_app()
                st.success("Opening main app in your browser...")
                # Close launcher after 3 seconds
                Timer(3.0, close_launcher).start()
else:
    st.markdown("""
    <div style="text-align: center; padding: 20px; background-color: #f8d7da; border-radius: 10px; margin: 20px 0;">
        <span class="status-indicator status-inactive"></span>
        <strong>Main Health App is Not Running</strong>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Launch Health Suite", type="primary", use_container_width=True):
            with st.spinner("Launching main application..."):
                # Show progress bar
                st.markdown("""
                <div class="progress-container">
                    <div class="progress-bar"></div>
                </div>
                """, unsafe_allow_html=True)
                
                success = launch_main_app()
                if success:
                    st.success("✅ Main app launching...")
                    
                    # Wait and check if port becomes active
                    max_wait = 15  # Maximum wait time in seconds
                    wait_time = 0
                    
                    while wait_time < max_wait:
                        time.sleep(1)
                        wait_time += 1
                        if is_port_in_use(8501):
                            st.success("✅ Main app is now running!")
                            time.sleep(1)
                            open_main_app()
                            st.success("Opening in your browser...")
                            # Close launcher after 3 seconds
                            Timer(3.0, close_launcher).start()
                            break
                        
                        # Update progress
                        progress_percent = min((wait_time / max_wait) * 100, 100)
                        st.write(f"Waiting for app to start... ({wait_time}s)")
                    
                    if not is_port_in_use(8501):
                        st.error("❌ App didn't start within expected time. Please check manually at http://localhost:8501")
                else:
                    st.error("❌ Failed to launch main app. Please check if app.py exists.")

st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="app-footer">
    <p>🌟 Arogya Sathi Health Suite - Powered by AI for Better Healthcare</p>
    <p>Port: 8510 → Main App: 8501</p>
</div>
""", unsafe_allow_html=True)

# Auto-refresh every 5 seconds to check app status
if not main_app_running:
    time.sleep(0.1)  # Small delay to prevent too frequent refreshes
    if st.button("🔄 Refresh Status", key="refresh"):
        st.rerun()

# Debug information
with st.expander("🔧 Debug Information"):
    st.write(f"**Current Directory:** {os.getcwd()}")
    st.write(f"**Python Executable:** {sys.executable}")
    st.write(f"**app.py exists:** {os.path.exists('app.py')}")
    st.write(f"**Platform:** {platform.system()}")
    st.write(f"**Port 8501 in use:** {is_port_in_use(8501)}")
    
    # Manual launch option
    st.write("---")
    st.write("**Manual Launch Command:**")
    manual_cmd = f"{sys.executable} -m streamlit run app.py --server.port=8501"
    st.code(manual_cmd)
    
    if st.button("🔧 Try Manual Launch"):
        try:
            result = subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py", "--server.port=8501"],
                                  capture_output=True, text=True, timeout=5)
            st.write("**Output:**", result.stdout)
            if result.stderr:
                st.write("**Errors:**", result.stderr)
        except subprocess.TimeoutExpired:
            st.success("Command started (timeout reached, which is normal)")
        except Exception as e:
            st.error(f"Error: {e}")
