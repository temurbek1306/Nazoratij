import os
import time
import requests
import json
import ai_assistant
from google import genai
from google.genai import types

def send_telegram_msg(msg):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_ADMIN_ID")
    if not bot_token or not chat_id:
        return
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": msg, "parse_mode": "HTML"}
    requests.post(url, json=payload)

def send_telegram_video(video_path, caption=""):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_ADMIN_ID")
    if not bot_token or not chat_id:
        return
    url = f"https://api.telegram.org/bot{bot_token}/sendVideo"
    with open(video_path, 'rb') as f:
        files = {'video': f}
        data = {'chat_id': chat_id, 'caption': caption, "parse_mode": "HTML"}
        requests.post(url, data=data, files=files)

def generate(prompt):
    try:
        km = ai_assistant.KeyManager()
        gemini_key = km.get_gemini_key()
        
        send_telegram_msg(f"🔄 <b>Vertex AI (Veo 3.1) ga ulanilmoqda...</b>\n🔑 Tanlangan Service Account ID: {km.current_sa_index}/{len(km.service_accounts)}")
        
        time.sleep(3)
        
        send_telegram_msg("🎬 <b>AI Video render qilishni boshladi... (Kuting, bu 2-3 daqiqa vaqt olishi mumkin)</b>")
        
        # O'qib olingan SA faylidan project_id ni olish
        with open("service_account.json", "r") as f:
            sa_info = json.load(f)
        project_id = sa_info.get("project_id")
        
        # Google Gen AI SDK uchun muhit o'zgaruvchilarini sozlash
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "service_account.json"
        os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
        os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"
        
        # Client ni sozlash
        client = genai.Client(vertexai=True)
        
        # Konfiguratsiya
        config = types.GenerateVideosConfig(
            aspect_ratio="16:9",
            duration_seconds=5 # Yoki kerak bo'lsa ko'paytirish mumkin
        )
        
        # Veo modelini chaqirish
        operation = client.models.generate_videos(
            model="veo-3.1-generate-001", 
            prompt=prompt,
            config=config
        )
        
        # Natijani kutish (Video generatsiya uzoq davom etadi)
        result = operation.result()
        
        # Videoni saqlash
        output_filename = "veo_generated_output.mp4"
        for video in result.generated_videos:
            with open(output_filename, "wb") as f:
                f.write(video.video.data)
            break
            
        caption = f"🎥 <b>Sizning Veo 3.1 Videongiz Tayyor!</b>\n\n📝 Prompt: <i>{prompt}</i>\n\n⚡️ <i>Vertex AI tomonidan muvaffaqiyatli yaratildi.</i>"
        send_telegram_video(output_filename, caption)
        
        if os.path.exists(output_filename):
            os.remove(output_filename)
            
    except Exception as e:
        send_telegram_msg(f"❌ Video generatsiya jarayonida xatolik yuz berdi: {e}")
