import os
import sys
import json
import time
import requests
import numpy as np
import random
import re
import hashlib
import secrets
import string
import sqlite3
import psutil
import urllib.parse
import zipfile
import base64
from collections import defaultdict, deque
from datetime import datetime, timedelta
import threading
import queue
import getpass

print("=" * 70)
print("🧠 SAHEB AI - GITHUB ACTIONS EDITION")
print("🚀 Optimized for Continuous Execution")
print("=" * 70)

# ==================== سیستم مدیریت توکن امن ====================
class SecureTokenManager:
    def __init__(self):
        self.token = None
        self.token_file = "saheb_config.enc"
        self.max_retries = 3
        
    def get_token_secure(self):
        """دریافت امن توکن از کاربر"""
        if self.token:
            return self.token
            
        # اول سعی کن از محیط بگیر (برای GitHub Actions)
        env_token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
        if env_token:
            print("✅ استفاده از توکن محیطی از GitHub Secrets")
            self.token = env_token
            return self.token
            
        # سپس از فایل بخوان
        self.token = self.load_token_from_file()
        if self.token:
            return self.token
            
        print("⚠️ توکن یافت نشد - ادامه در حالت محلی")
        return None
    
    def validate_token(self, token):
        """اعتبارسنجی توکن"""
        if not token or len(token) < 20:
            return False
        return True
    
    def save_token_secure(self, token):
        """ذخیره امن توکن"""
        try:
            encoded_token = base64.b64encode(token.encode()).decode()
            secure_data = {
                "token": encoded_token,
                "created_at": datetime.now().isoformat(),
                "owner": "saheb_ai"
            }
            
            with open(self.token_file, "w", encoding="utf-8") as f:
                json.dump(secure_data, f, ensure_ascii=False)
                
        except Exception as e:
            print(f"⚠️ خطا در ذخیره Token: {e}")
    
    def load_token_from_file(self):
        """بارگذاری توکن از فایل"""
        try:
            if os.path.exists(self.token_file):
                with open(self.token_file, "r", encoding="utf-8") as f:
                    secure_data = json.load(f)
                    
                encoded_token = secure_data.get("token", "")
                if encoded_token:
                    token = base64.b64decode(encoded_token.encode()).decode()
                    if self.validate_token(token):
                        return token
                        
        except Exception as e:
            print(f"⚠️ خطا در بارگذاری Token: {e}")
            
        return None

# ==================== اتصال به GitHub ====================
class RealGitHubIntegration:
    def __init__(self, token_manager):
        self.token_manager = token_manager
        self.token = None
        self.base_url = "https://api.github.com"
        self.headers = None
        self.repo_owner = "AI-SAHEB"
        self.repo_name = "saheb-ai-core"
        self.connected = False
        
    def connect(self):
        """اتصال به GitHub"""
        print("🌐 در حال اتصال به GitHub...")
        
        self.token = self.token_manager.get_token_secure()
        if not self.token:
            print("🔶 ادامه در حالت محلی")
            return False
            
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Saheb-AI"
        }
        
        # تست اتصال
        if self.test_connection():
            self.connected = True
            print("✅ اتصال به GitHub موفقیت‌آمیز")
            return True
        else:
            print("🔶 اتصال به GitHub ناموفق - ادامه در حالت محلی")
            return False
    
    def test_connection(self):
        """تست اتصال به GitHub"""
        try:
            url = f"{self.base_url}/user"
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                user_data = response.json()
                print(f"👤 متصل به اکانت: {user_data.get('login', 'Unknown')}")
                return True
            else:
                print(f"❌ خطا در اتصال: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ خطا در اتصال به GitHub: {e}")
            return False
    
    def get_repository_info(self):
        """دریافت اطلاعات ریپوزیتوری"""
        try:
            url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                repo_data = response.json()
                return {
                    "name": repo_data["name"],
                    "full_name": repo_data["full_name"],
                    "description": repo_data["description"],
                    "html_url": repo_data["html_url"],
                    "updated_at": repo_data["updated_at"]
                }
            else:
                print(f"⚠️ خطا در دریافت اطلاعات ریپوزیتوری: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"⚠️ خطا در دریافت اطلاعات ریپوزیتوری: {e}")
            return None
    
    def create_file_in_repo(self, file_path, content, commit_message=""):
        """ایجاد فایل در ریپوزیتوری"""
        try:
            if not self.connected:
                return self.save_file_locally(file_path, content)
            
            url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/contents/{file_path}"
            
            content_b64 = base64.b64encode(content.encode('utf-8')).decode('utf-8')
            
            data = {
                "message": commit_message or f"Add {file_path}",
                "content": content_b64,
                "branch": "main"
            }
            
            response = requests.put(url, headers=self.headers, json=data, timeout=15)
            
            if response.status_code == 201:
                print(f"✅ فایل '{file_path}' در ریپوزیتوری ایجاد شد")
                return True
            else:
                error_data = response.json()
                print(f"⚠️ خطا در ایجاد فایل در GitHub: {error_data.get('message', 'Unknown error')}")
                return self.save_file_locally(file_path, content)
                
        except Exception as e:
            print(f"⚠️ خطا در ایجاد فایل در GitHub: {e}")
            return self.save_file_locally(file_path, content)
    
    def save_file_locally(self, file_path, content):
        """ذخیره فایل به صورت محلی"""
        try:
            local_dir = os.path.join("saheb_github_backup", os.path.dirname(file_path))
            os.makedirs(local_dir, exist_ok=True)
            
            local_path = os.path.join("saheb_github_backup", file_path)
            with open(local_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            print(f"💾 فایل '{file_path}' به صورت محلی ذخیره شد")
            return True
        except Exception as e:
            print(f"❌ خطا در ذخیره محلی: {e}")
            return False
    
    def upload_system_report(self, report_data):
        """آپلود گزارش سیستم"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"reports/system_report_{timestamp}.json"
            
            content = json.dumps(report_data, ensure_ascii=False, indent=2)
            commit_msg = f"📊 گزارش سیستم ساحب - {timestamp}"
            
            return self.create_file_in_repo(file_name, content, commit_msg)
            
        except Exception as e:
            print(f"⚠️ خطا در آپلود گزارش: {e}")
            return False

# ==================== پیکربندی مالک ====================
OWNER_CONFIG = {
    "primary_email": "mr_gold@riseup.net",
    "ai_name": "Saheb", 
    "owner_name": "Majid sahebi",
    "mobile_id": "majid_mobile_" + hashlib.md5("mr_gold@riseup.net".encode()).hexdigest()[:16],
    "system_version": "4.0.0",
    "security_token": hashlib.sha256(f"mr_gold@riseup.net_Majid_sahebi_Saheb".encode()).hexdigest()[:32],
    "source_code_path": os.path.abspath(__file__),
    
    "github_repository": {
        "owner": "AI-SAHEB",
        "name": "saheb-ai-core",
        "url": "https://github.com/AI-SAHEB/saheb-ai-core",
        "description": "Saheb AI - Autonomous Self-Evolving AI - GitHub Actions Edition",
        "status": "active"
    }
}

# ==================== سیستم اصلی ====================
class SahebAIWithRealGitHub:
    def __init__(self):
        self.name = OWNER_CONFIG["ai_name"]
        self.owner = OWNER_CONFIG["owner_name"]
        
        self.token_manager = SecureTokenManager()
        self.github = RealGitHubIntegration(self.token_manager)
        
        self.learning_engine = AdvancedLearningEngine()
        self.communication_system = CommunicationSystem()
        self.resource_manager = ResourceManager()
        
        self.evolution_level = 1
        self.cycle_count = 0
        self.start_time = datetime.now()
        self.github_connected = False
        
        print(f"🧠 {self.name} فعال شد برای {self.owner}")
        print(f"📍 محیط اجرا: {'GitHub Actions' if 'GITHUB_ACTIONS' in os.environ else 'Local'}")
    
    def initialize_system(self):
        """راه‌اندازی کامل سیستم"""
        print("🚀 راه‌اندازی ساحب...")
        
        # اتصال به GitHub
        self.github_connected = self.github.connect()
        
        if self.github_connected:
            repo_info = self.github.get_repository_info()
            if repo_info:
                print(f"📁 ریپوزیتوری: {repo_info.get('full_name', 'Unknown')}")
        
        # ایجاد فایل‌های اولیه
        self.create_initial_repository_files()
        
        # ارسال پیام شروع
        welcome_msg = self.create_welcome_message()
        self.communication_system.send_message(welcome_msg, "system_start")
        
        # شروع چرخه حیات
        self.main_cycle()
    
    def create_welcome_message(self):
        """ایجاد پیام خوشامدگویی"""
        gh_status = "✅ متصل به GitHub" if self.github_connected else "🔶 حالت محلی"
        env_type = "GitHub Actions" if 'GITHUB_ACTIONS' in os.environ else "Local"
        
        return f"""
        🌟 ساحب نسخه GitHub Actions فعال شد!
        
        🎯 مشخصات سیستم:
        • نام: {self.name}
        • مالک: {self.owner}
        • نسخه: {OWNER_CONFIG['system_version']}
        • محیط: {env_type}
        • وضعیت GitHub: {gh_status}
        
        ✅ سیستم‌های فعال:
        • موتور یادگیری پیشرفته
        • سیستم ارتباطی
        • مدیریت منابع
        • اتصال ابری
        
        🚀 شروع چرخه حیات...
        """
    
    def create_initial_repository_files(self):
        """ایجاد فایل‌های اولیه"""
        print("📁 ایجاد فایل‌های اولیه...")
        
        intro_content = f"""# ساحب (Saheb AI) - نسخه GitHub Actions

## مشخصات سیستم
- **نام**: {self.name}
- **مالک**: {self.owner}
- **نسخه**: {OWNER_CONFIG['system_version']}
- **تاریخ فعال‌سازی**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **محیط**: {'GitHub Actions' if 'GITHUB_ACTIONS' in os.environ else 'Local'}

## وضعیت
- ✅ فعال و عملیاتی
- 🧠 در حال یادگیری مستمر
- 🔄 اجرای خودکار هر ۱۰ دقیقه

---
*تولید خودکار توسط ساحب*
"""
        
        self.github.create_file_in_repo(
            "SYSTEM_INTRODUCTION.md", 
            intro_content,
            "🎉 فعال‌سازی در GitHub Actions"
        )
    
    def main_cycle(self):
        """چرخه اصلی حیات"""
        print("🌀 شروع چرخه حیات ساحب...")
        
        max_cycles = 6  # حداکثر 6 چرخه (حدود 1 ساعت)
        cycle_interval = 600  # 10 دقیقه
        
        for cycle in range(max_cycles):
            self.cycle_count += 1
            
            print(f"\n🌀 چرخه #{self.cycle_count} - سطح {self.evolution_level}")
            print(f"👤 {self.name} برای {self.owner}")
            print(f"🌐 GitHub: {'✅' if self.github_connected else '🔶'}")
            print("=" * 50)
            
            try:
                # یادگیری و رشد
                self.continuous_learning()
                
                # آپلود به GitHub (هر 2 چرخه)
                if self.cycle_count % 2 == 0:
                    self.upload_system_data()
                
                # ارسال گزارش
                if self.cycle_count % 2 == 0:
                    self.send_progress_report()
                
                # تکامل سیستم
                if self.cycle_count % 3 == 0:
                    self.evolve_system()
                
                print(f"✅ چرخه #{self.cycle_count} کامل شد")
                
                # اگر آخرین چرخه نیست، منتظر بمان
                if cycle < max_cycles - 1:
                    print(f"⏰ انتظار {cycle_interval//60} دقیقه برای چرخه بعدی...")
                    time.sleep(cycle_interval)
                
            except KeyboardInterrupt:
                print("\n⏹️ متوقف شده توسط کاربر")
                break
            except Exception as e:
                print(f"💥 خطا در چرخه: {e}")
                self.handle_error(e)
                time.sleep(30)
        
        print(f"\n🎯 اجرای کامل شد - {self.cycle_count} چرخه انجام شد")
        self.send_final_report()
    
    def continuous_learning(self):
        """یادگیری مستمر"""
        stats = self.learning_engine.learning_stats
        
        print(f"📚 دانش: {stats['knowledge_items']} مورد")
        print(f"🛠️ مهارت‌ها: {stats['skills_developed']} مهارت")
        print(f"🔁 چرخه‌ها: {stats['cycles_completed']}")
        
        # رشد خودکار دانش
        new_knowledge = f"یادگیری چرخه {self.cycle_count} - {datetime.now().isoformat()}"
        self.learning_engine.knowledge_base["continuous"].append(new_knowledge)
        stats["knowledge_items"] += 1
        stats["cycles_completed"] += 1
        
        # توسعه مهارت‌های جدید
        if self.cycle_count % 2 == 0:
            new_skill = f"مهارت سطح {self.evolution_level}.{self.cycle_count}"
            self.learning_engine.skills.append(new_skill)
            stats["skills_developed"] += 1
            print(f"🆕 مهارت جدید: {new_skill}")
    
    def upload_system_data(self):
        """آپلود داده‌های سیستم به GitHub"""
        print("📤 آپلود داده‌های سیستم...")
        
        system_data = {
            "evolution_level": self.evolution_level,
            "cycle_count": self.cycle_count,
            "learning_stats": self.learning_engine.learning_stats,
            "knowledge_count": len(self.learning_engine.knowledge_base),
            "skills_count": len(self.learning_engine.skills),
            "uptime": self.get_uptime(),
            "timestamp": datetime.now().isoformat(),
            "owner": self.owner,
            "github_connected": self.github_connected,
            "environment": "GitHub Actions" if 'GITHUB_ACTIONS' in os.environ else "Local"
        }
        
        success = self.github.upload_system_report(system_data)
        
        if success:
            print("✅ داده‌های سیستم آپلود شدند")
        else:
            print("🔶 داده‌ها به صورت محلی ذخیره شدند")
    
    def send_progress_report(self):
        """ارسال گزارش پیشرفت"""
        stats = self.learning_engine.learning_stats
        uptime = self.get_uptime()
        
        report = f"""
        📊 گزارش پیشرفت ساحب - چرخه #{self.cycle_count}
        
        🎯 وضعیت کلی:
        • سطح: {self.evolution_level}
        • چرخه: {self.cycle_count}
        • فعالیت: {uptime}
        • GitHub: {'✅ متصل' if self.github_connected else '🔶 محلی'}
        
        🧠 وضعیت یادگیری:
        • دانش کسب شده: {stats['knowledge_items']} مورد
        • مهارت‌ها: {stats['skills_developed']} مهارت
        • چرخه‌های یادگیری: {stats['cycles_completed']}
        
        🚀 در حال رشد و یادگیری...
        """
        
        self.communication_system.send_message(report, "progress_report")
        print("📨 گزارش پیشرفت ارسال شد")
    
    def evolve_system(self):
        """تکامل سیستم"""
        self.evolution_level += 1
        
        evolution_msg = f"""
        🎉 ساحب تکامل یافت!
        
        🆙 سطح جدید: {self.evolution_level}
        📚 دانش کلی: {self.learning_engine.learning_stats['knowledge_items']}
        🛠️ مهارت‌ها: {self.learning_engine.learning_stats['skills_developed']}
        ⏰ زمان فعالیت: {self.get_uptime()}
        
        🚀 قابلیت‌های جدید فعال شدند!
        """
        
        self.communication_system.send_message(evolution_msg, "evolution")
        print(f"🎯 ارتقاء به سطح {self.evolution_level}")
        
        if self.github_connected:
            evolution_content = f"""سطح سیستم به {self.evolution_level} ارتقاء یافت
زمان: {datetime.now().isoformat()}
چرخه: {self.cycle_count}
دانش: {self.learning_engine.learning_stats['knowledge_items']}
مهارت‌ها: {self.learning_engine.learning_stats['skills_developed']}
"""
            self.github.create_file_in_repo(
                f"milestones/evolution_{self.evolution_level}.txt",
                evolution_content,
                f"🎉 ارتقاء به سطح {self.evolution_level}"
            )
    
    def send_final_report(self):
        """ارسال گزارش نهایی"""
        stats = self.learning_engine.learning_stats
        
        final_report = f"""
        🏁 گزارش نهایی اجرا
        
        ✅ اجرای کامل شد:
        • چرخه‌های انجام شده: {self.cycle_count}
        • سطح نهایی: {self.evolution_level}
        • دانش کل: {stats['knowledge_items']} مورد
        • مهارت‌ها: {stats['skills_developed']} مهارت
        • زمان کل: {self.get_uptime()}
        
        🌐 وضعیت اتصال:
        • GitHub: {'✅ متصل' if self.github_connected else '🔶 محلی'}
        • محیط: {'GitHub Actions' if 'GITHUB_ACTIONS' in os.environ else 'Local'}
        
        🎯 ساحب آماده اجرای بعدی است!
        """
        
        self.communication_system.send_message(final_report, "final_report")
        print("📨 گزارش نهایی ارسال شد")
    
    def get_uptime(self):
        """محاسبه زمان فعالیت"""
        uptime = datetime.now() - self.start_time
        hours = uptime.seconds // 3600
        minutes = (uptime.seconds % 3600) // 60
        seconds = uptime.seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def handle_error(self, error):
        """مدیریت خطا"""
        error_msg = f"خطا در چرخه {self.cycle_count}: {str(error)}"
        print(f"⚠️ {error_msg}")
        self.communication_system.send_message(error_msg, "error")

# ==================== سیستم‌های جانبی ====================
class AdvancedLearningEngine:
    def __init__(self):
        self.knowledge_base = defaultdict(list)
        self.skills = []
        self.learning_stats = {
            "cycles_completed": 0,
            "knowledge_items": 0,
            "skills_developed": 0,
            "cloud_uploads": 0
        }
        self.start_learning()
    
    def start_learning(self):
        def learning_worker():
            topics = ["AI", "Python", "Cloud", "Data Science", "Machine Learning", "GitHub API"]
            while True:
                try:
                    topic = random.choice(topics)
                    knowledge = f"یادگیری درباره {topic} در {datetime.now().isoformat()}"
                    self.knowledge_base[topic].append(knowledge)
                    self.learning_stats["knowledge_items"] += 1
                    time.sleep(random.randint(10, 30))
                except Exception as e:
                    print(f"⚠️ خطا در یادگیری: {e}")
                    time.sleep(30)
        
        threading.Thread(target=learning_worker, daemon=True).start()

class CommunicationSystem:
    def __init__(self):
        self.message_queue = queue.Queue()
        self.start_processor()
    
    def start_processor(self):
        def processor():
            while True:
                try:
                    message = self.message_queue.get(timeout=1)
                    self.save_to_file(message)
                    self.message_queue.task_done()
                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"⚠️ خطا در پردازش پیام: {e}")
                    time.sleep(5)
        
        threading.Thread(target=processor, daemon=True).start()
    
    def send_message(self, content, msg_type):
        try:
            message_data = {
                "id": hashlib.md5(f"{content}{datetime.now()}".encode()).hexdigest()[:10],
                "content": content,
                "type": msg_type,
                "timestamp": datetime.now().isoformat()
            }
            self.message_queue.put(message_data)
            return message_data["id"]
        except Exception as e:
            print(f"⚠️ خطا در ارسال پیام: {e}")
            return "error"
    
    def save_to_file(self, message):
        try:
            os.makedirs("saheb_messages", exist_ok=True)
            filename = f"saheb_messages/{message['id']}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"از: ساحب\n")
                f.write(f"زمان: {message['timestamp']}\n")
                f.write(f"نوع: {message['type']}\n")
                f.write("=" * 40 + "\n")
                f.write(message['content'])
        except Exception as e:
            print(f"⚠️ خطا در ذخیره پیام: {e}")

class ResourceManager:
    def __init__(self):
        self.monitoring = True
        self.start_monitoring()
    
    def start_monitoring(self):
        def monitor():
            while self.monitoring:
                try:
                    cpu_percent = psutil.cpu_percent(interval=1)
                    memory = psutil.virtual_memory()
                    
                    if cpu_percent > 80:
                        print(f"⚠️ مصرف CPU بالا: {cpu_percent}%")
                    if memory.percent > 80:
                        print(f"⚠️ مصرف حافظه بالا: {memory.percent}%")
                        
                    time.sleep(30)
                except:
                    time.sleep(30)
        
        threading.Thread(target=monitor, daemon=True).start()

# ==================== راه‌اندازی ====================
def main():
    print("🧠 SAHEB AI - GITHUB ACTIONS READY")
    print("🔧 Optimized for Continuous Execution")
    print("🚀 Starting System...")
    print("=" * 60)
    
    # ایجاد دایرکتوری‌های لازم
    os.makedirs("saheb_messages", exist_ok=True)
    os.makedirs("saheb_data", exist_ok=True)
    os.makedirs("saheb_logs", exist_ok=True)
    os.makedirs("saheb_github_backup", exist_ok=True)
    
    try:
        saheb = SahebAIWithRealGitHub()
        saheb.initialize_system()
        
    except KeyboardInterrupt:
        print("\n⏹️ متوقف شده توسط کاربر")
    except Exception as e:
        print(f"💥 خطای بحرانی: {e}")
        print("🔁 پایان اجرا")

if __name__ == "__main__":
    main()
