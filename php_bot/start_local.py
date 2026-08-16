import os
import subprocess
import time
import requests
import socket
from dotenv import load_dotenv

# dotenv'ni yuklash (agar bot tokeni .env da bo'lsa)
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

try:
    from pyngrok import ngrok
except ImportError:
    print("❌ 'pyngrok' kutubxonasi o'rnatilmagan! O'rnatish uchun: pip install pyngrok")
    exit(1)

def find_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()
    return port

def start_server():
    print("==========================================")
    print("🚀 PHP Lokal Server va Ngrok ishga tushmoqda")
    print("==========================================")
    
    port = find_free_port()
    
    # 1. PHP built-in serverini ishga tushirish
    php_process = subprocess.Popen(
        ["php", "-S", f"127.0.0.1:{port}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    print(f"✅ PHP lokal server ishga tushdi (Port: {port})")
    
    # 2. Ngrok tunnelini ochish
    tunnel = ngrok.connect(port)
    public_url = tunnel.public_url
    print(f"✅ Ngrok tunnel ochildi: {public_url}")
    
    # 3. Webhook'ni Telegram'ga o'rnatish
    webhook_url = f"{public_url}/bot.php"
    if TELEGRAM_BOT_TOKEN:
        print(f"⏳ Telegram Webhook ulanmoqda: {webhook_url}")
        res = requests.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook?url={webhook_url}")
        if res.status_code == 200 and res.json().get('ok'):
            print("✅ Webhook muvaffaqiyatli o'rnatildi!")
        else:
            print(f"❌ Webhook o'rnatishda xatolik: {res.text}")
    else:
        print("⚠️ .env faylida TELEGRAM_BOT_TOKEN topilmadi!")
        print(f"Qo'lda Webhook ulash uchun link:\nhttps://api.telegram.org/bot<BOT_TOKEN>/setWebhook?url={webhook_url}")
    
    print("\n💡 Tizim tayyor! Telegramdan botga xabar yozib test qilib ko'rishingiz mumkin.")
    print("O'chirish uchun CTRL+C bosing...")
    
    try:
        # Dasturni to'xtamasligi uchun cheksiz loop
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n⏹️ Server to'xtatilmoqda...")
        php_process.terminate()
        ngrok.kill()
        print("✅ Yopildi.")

if __name__ == "__main__":
    start_server()
