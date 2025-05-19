import subprocess
import sys
import os

def install_requirements():
    print("Installing base requirements...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "wheel"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "setuptools"])
    
    # Install numpy first as it's a dependency for pandas
    print("Installing numpy...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy==1.24.3"])
    
    # Install pandas
    print("Installing pandas...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas==2.0.3"])
    
    # Install remaining requirements
    print("Installing remaining requirements...")
    with open("requirements.txt", "r") as f:
        requirements = f.readlines()
    
    for req in requirements:
        req = req.strip()
        if req and not req.startswith("#"):
            if "numpy" not in req and "pandas" not in req:  # Skip already installed packages
                print(f"Installing {req}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", req])

if __name__ == "__main__":
    install_requirements() 