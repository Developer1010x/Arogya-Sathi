import platform
import shutil
import subprocess
import sys
import os

# System packages your app needs (adjust if needed)
SYSTEM_PACKAGES = [
    "autoconf", "gnupg", "libgpg-error", "libxdmcp", "nettle", "readline",
    "automake", "gnutls", "libidn2", "libxext", "ninja", "screenfetch",
    "bison", "gobject-introspection", "libksba", "libxrender", "npth", "sqlite",
    "ca-certificates", "gpgme", "libnghttp2", "libyaml", "nspr", "swig",
    "cairo", "graphite2", "libomp", "lit", "nss", "tesseract",
    "cmake", "harfbuzz", "libpng", "little-cms2", "openjpeg", "tesseract-lang",
    "doxygen", "icu4c@77", "libssh2", "lz4", "openssl@3", "unbound",
    "expat", "jpeg-turbo", "libtasn1", "lzip", "p11-kit", "util-macros",
    "fontconfig", "leptonica", "libtiff", "lzo", "pango", "webp",
    "freetype", "libarchive", "libtool", "m4", "pcre2", "xcb-proto",
    "fribidi", "libassuan", "libunistring", "meson", "pinentry", "xorgproto",
    "gettext", "libb2", "libusb", "mpdecimal", "pixman", "xtrans",
    "giflib", "libevent", "libx11", "mpfr", "pkgconf", "xz",
    "glib", "libgcrypt", "libxau", "mupdf-tools", "python-setuptools", "zstd",
    "gmp", "libgit2", "libxcb", "nasm", "python@3.13"
]

def install_chocolatey():
    print("Chocolatey not found. Installing Chocolatey...")
    cmd = (
        r'''powershell -NoProfile -ExecutionPolicy Bypass -Command "'''
        r'''Set-ExecutionPolicy Bypass -Scope Process -Force; '''
        r'''[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12; '''
        r'''iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"'''
    )
    subprocess.call(cmd, shell=True)
    return shutil.which("choco") is not None

def install_system_packages():
    os_name = platform.system()

    if os_name == "Darwin":
        for pkg in SYSTEM_PACKAGES:
            if shutil.which(pkg) is None:
                print(f"Installing {pkg} with brew...")
                subprocess.call(["brew", "install", pkg])
    elif os_name == "Linux":
        for pkg in SYSTEM_PACKAGES:
            if shutil.which(pkg) is None:
                print(f"Installing {pkg} with apt-get...")
                subprocess.call(["sudo", "apt-get", "install", "-y", pkg])
    elif os_name == "Windows":
        if shutil.which("choco") is None:
            success = install_chocolatey()
            if not success:
                print("Failed to install Chocolatey. Cannot continue with system packages.")
                return False

        for pkg in SYSTEM_PACKAGES:
            if shutil.which(pkg) is None:
                print(f"Installing {pkg} with choco...")
                subprocess.call(["choco", "install", pkg, "-y"])

    else:
        print(f"Unsupported OS: {os_name}")
        return False
    return True

def install_python_requirements(requirements_file="requirements.txt"):
    if not os.path.exists(requirements_file):
        print(f"{requirements_file} not found.")
        return False
    print(f"Installing Python packages from {requirements_file}...")
    subprocess.call([sys.executable, "-m", "pip", "install", "-r", requirements_file])
    return True

def main():
    print("Starting system dependency check and installation...")
    if not install_system_packages():
        print("System package installation failed or incomplete.")

    print("Installing Python requirements...")
    if not install_python_requirements():
        print("Python package installation failed or incomplete.")

if __name__ == "__main__":
    main()
