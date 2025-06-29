import platform
import shutil
import subprocess
import sys
import os

# Core system packages (updated and expanded)
MACOS_PACKAGES = [
    "python@3.12", "python@3.13", "pip", "pipx",
    "autoconf", "automake", "cmake", "ninja", "meson", "pkgconf",
    "gnupg", "gpgme", "libgpg-error", "libgcrypt", "libassuan", "libksba", "npth", "pinentry",
    "openssl@3", "ca-certificates", "nss", "nspr", "p11-kit", "libtasn1", "nettle", "gnutls", "unbound",
    "curl", "wget", "git", "libgit2", "libssh2", "libnghttp2",
    "sqlite", "readline", "libedit", "ncurses",
    "zlib", "bzip2", "xz", "lz4", "zstd", "lzo",
    "libyaml", "libxml2", "libxslt", "expat",
    "jpeg-turbo", "libpng", "libtiff", "giflib", "webp", "openjpeg", "little-cms2",
    "freetype", "fontconfig", "harfbuzz", "graphite2", "fribidi", "pango", "cairo", "pixman",
    "glib", "gobject-introspection", "gettext", "icu4c@77", "libiconv",
    "libx11", "libxau", "libxcb", "libxdmcp", "libxext", "libxrender", "xcb-proto", "xorgproto", "xtrans", "util-macros",
    "tesseract", "tesseract-lang", "leptonica", "mupdf-tools",
    "libomp", "mpfr", "gmp", "mpdecimal",
    "screenfetch", "htop", "tree", "jq",
    "ollama"  # Added Ollama
]

LINUX_PACKAGES = [
    "python3.12", "python3.12-dev", "python3.12-venv", "python3-pip", "python3-setuptools", "pipx",
    "build-essential", "autoconf", "automake", "cmake", "ninja-build", "meson", "pkg-config", "libtool", "m4", "bison",
    "gnupg", "gpg", "gpg-agent", "libgpg-error-dev", "libgcrypt20-dev", "libassuan-dev", "libksba-dev", "npth-dev", "pinentry-curses",
    "openssl", "libssl-dev", "ca-certificates", "libnss3-dev", "libnspr4-dev", "libp11-kit-dev", "libtasn1-6-dev", "nettle-dev", "libgnutls28-dev", "libunbound-dev",
    "curl", "wget", "git", "libgit2-dev", "libssh2-1-dev", "libnghttp2-dev",
    "sqlite3", "libsqlite3-dev", "libreadline-dev", "libedit-dev", "libncurses5-dev",
    "zlib1g-dev", "libbz2-dev", "liblzma-dev", "liblz4-dev", "libzstd-dev", "liblzo2-dev",
    "libyaml-dev", "libxml2-dev", "libxslt1-dev", "libexpat1-dev",
    "libjpeg-turbo8-dev", "libpng-dev", "libtiff5-dev", "libgif-dev", "libwebp-dev", "libopenjp2-7-dev", "liblcms2-dev",
    "libfreetype6-dev", "libfontconfig1-dev", "libharfbuzz-dev", "libgraphite2-dev", "libfribidi-dev", "libpango1.0-dev", "libcairo2-dev", "libpixman-1-dev",
    "libglib2.0-dev", "libgirepository1.0-dev", "gettext", "libicu-dev", "libiconv-hook-dev",
    "libx11-dev", "libxau-dev", "libxcb1-dev", "libxdmcp-dev", "libxext-dev", "libxrender-dev", "libxcb-proto0-dev", "x11proto-dev", "xtrans-dev", "xutils-dev",
    "tesseract-ocr", "tesseract-ocr-all", "libleptonica-dev", "mupdf-tools",
    "libomp-dev", "libmpfr-dev", "libgmp-dev", "libmpdec-dev",
    "screenfetch", "htop", "tree", "jq", "unzip", "zip",
    "software-properties-common", "apt-transport-https", "gnupg", "lsb-release"
]

WINDOWS_PACKAGES = [
    "python312", "python313", "pip", "pipx",
    "msys2", "mingw", "cmake", "ninja", "pkgconfiglite",
    "git", "curl", "wget",
    "7zip", "unzip",
    "vcredist140", "vcredist2019",
    "openssl", "sqlite",
    "tesseract", "mupdf",
    "jq", "tree",
    "ollama"  # Added Ollama
]

def get_python_executable():
    """Get the correct Python 3.12 executable path."""
    # Try different possible Python 3.12 paths
    possible_paths = [
        "python3.12",
        "python3",
        "python",
        "/usr/bin/python3.12",
        "/usr/local/bin/python3.12",
        "/opt/homebrew/bin/python3.12",
        "C:\\Python312\\python.exe",
        "C:\\Program Files\\Python312\\python.exe"
    ]
    
    for path in possible_paths:
        try:
            result = subprocess.run([path, "--version"],
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and "Python 3.12" in result.stdout:
                return path
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue
    
    return "python"  # Fallback

def install_chocolatey():
    """Install Chocolatey on Windows."""
    print("Chocolatey not found. Installing Chocolatey...")
    cmd = (
        r'powershell -NoProfile -ExecutionPolicy Bypass -Command "'
        r'Set-ExecutionPolicy Bypass -Scope Process -Force; '
        r'[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12; '
        r'iex ((New-Object System.Net.WebClient).DownloadString(\'https://community.chocolatey.org/install.ps1\'))"'
    )
    try:
        subprocess.run(cmd, shell=True, check=True)
        return shutil.which("choco") is not None
    except subprocess.CalledProcessError as e:
        print(f"Failed to install Chocolatey: {e}")
        return False

def install_homebrew():
    """Install Homebrew on macOS."""
    print("Homebrew not found. Installing Homebrew...")
    cmd = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
    try:
        subprocess.run(cmd, shell=True, check=True)
        return shutil.which("brew") is not None
    except subprocess.CalledProcessError as e:
        print(f"Failed to install Homebrew: {e}")
        return False

def update_package_manager():
    """Update the package manager."""
    os_name = platform.system()
    
    try:
        if os_name == "Darwin":
            if shutil.which("brew"):
                print("Updating Homebrew...")
                subprocess.run(["brew", "update"], check=True)
                subprocess.run(["brew", "upgrade"], check=True)
        elif os_name == "Linux":
            print("Updating apt...")
            subprocess.run(["sudo", "apt", "update"], check=True)
            subprocess.run(["sudo", "apt", "upgrade", "-y"], check=True)
        elif os_name == "Windows":
            if shutil.which("choco"):
                print("Updating Chocolatey packages...")
                subprocess.run(["choco", "upgrade", "all", "-y"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to update package manager: {e}")

def install_system_packages():
    """Install system packages based on the operating system."""
    os_name = platform.system()
    success = True

    if os_name == "Darwin":
        if shutil.which("brew") is None:
            if not install_homebrew():
                print("Failed to install Homebrew. Cannot continue with system packages.")
                return False
        
        update_package_manager()
        
        for pkg in MACOS_PACKAGES:
            try:
                print(f"Installing {pkg} with brew...")
                subprocess.run(["brew", "install", pkg], check=True)
            except subprocess.CalledProcessError:
                print(f"Failed to install {pkg}, continuing...")
                success = False

    elif os_name == "Linux":
        update_package_manager()
        
        for pkg in LINUX_PACKAGES:
            try:
                print(f"Installing {pkg} with apt...")
                subprocess.run(["sudo", "apt", "install", "-y", pkg], check=True)
            except subprocess.CalledProcessError:
                print(f"Failed to install {pkg}, continuing...")
                success = False

    elif os_name == "Windows":
        if shutil.which("choco") is None:
            if not install_chocolatey():
                print("Failed to install Chocolatey. Cannot continue with system packages.")
                return False
        
        update_package_manager()
        
        for pkg in WINDOWS_PACKAGES:
            try:
                print(f"Installing {pkg} with choco...")
                subprocess.run(["choco", "install", pkg, "-y"], check=True)
            except subprocess.CalledProcessError:
                print(f"Failed to install {pkg}, continuing...")
                success = False

    else:
        print(f"Unsupported OS: {os_name}")
        return False
    
    return success

def setup_python_environment():
    """Set up Python 3.12 environment and ensure pip is working."""
    python_exe = get_python_executable()
    
    try:
        # Verify Python version
        result = subprocess.run([python_exe, "--version"],
                              capture_output=True, text=True, check=True)
        print(f"Using Python: {result.stdout.strip()}")
        
        # Upgrade pip
        print("Upgrading pip...")
        subprocess.run([python_exe, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        
        # Install essential Python packages
        essential_packages = [
            "setuptools", "wheel", "virtualenv", "pipenv",
            "requests", "psutil", "packaging"
        ]
        
        for pkg in essential_packages:
            try:
                print(f"Installing {pkg}...")
                subprocess.run([python_exe, "-m", "pip", "install", pkg], check=True)
            except subprocess.CalledProcessError:
                print(f"Failed to install {pkg}, continuing...")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to set up Python environment: {e}")
        return False

def install_python_requirements(requirements_file="requirements.txt"):
    """Install Python packages from requirements file."""
    if not os.path.exists(requirements_file):
        print(f"{requirements_file} not found. Skipping Python requirements installation.")
        return True
    
    python_exe = get_python_executable()
    
    try:
        print(f"Installing Python packages from {requirements_file}...")
        subprocess.run([python_exe, "-m", "pip", "install", "-r", requirements_file], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install Python requirements: {e}")
        return False

def install_ollama():
    """Install Ollama if not present."""
    if shutil.which("ollama"):
        print("Ollama already installed.")
        return True
    
    os_name = platform.system()
    
    try:
        if os_name == "Darwin":
            subprocess.run(["brew", "install", "ollama"], check=True)
        elif os_name == "Linux":
            subprocess.run([
                "curl", "-fsSL", "https://ollama.com/install.sh", "|", "sh"
            ], shell=True, check=True)
        elif os_name == "Windows":
            subprocess.run(["choco", "install", "ollama", "-y"], check=True)
        
        print("Ollama installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install Ollama: {e}")
        return False

def main():
    """Main setup function."""
    print("Starting comprehensive system setup...")
    print(f"Detected OS: {platform.system()}")
    print(f"Python version: {sys.version}")
    
    # Install system packages
    print("\n=== Installing System Packages ===")
    if not install_system_packages():
        print("System package installation had some failures.")
    
    # Set up Python environment
    print("\n=== Setting up Python Environment ===")
    if not setup_python_environment():
        print("Python environment setup failed.")
    
    # Install Python requirements
    print("\n=== Installing Python Requirements ===")
    if not install_python_requirements():
        print("Python requirements installation failed.")
    
    # Install Ollama
    print("\n=== Installing Ollama ===")
    if not install_ollama():
        print("Ollama installation failed.")
    
    print("\n=== Setup Complete ===")
    print("System setup finished. Some packages may have failed to install.")
    print("Please check the output above for any errors.")

if __name__ == "__main__":
    main()
