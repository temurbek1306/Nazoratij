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

def generate(prompt, ratio="16:9"):
    try:
        km = ai_assistant.KeyManager()
        gemini_key = km.get_gemini_key()
        
        send_telegram_msg(f"🔄 <b>Vertex AI (Veo 3.1) ga ulanilmoqda...</b>\n🔑 Tanlangan Service Account ID: {km.current_sa_index}/{len(km.service_accounts)}")
        
        time.sleep(3)
        
        send_telegram_msg("🎬 <b>AI Video render qilishni boshladi... (Kuting, bu 2-3 daqiqa vaqt olishi mumkin)</b>")
        
        # Bizga aynan Billing (To'lov) ulangan 'service-503705' loyihasi kerak
        target_project = "service-503705"
        
        # Barcha kalitlarni o'qish
        with open("service_accounts.json", "r") as f:
            all_accounts = json.load(f)
            
        # Qidirilayotgan kalitni topish
        billed_account = None
        for acc in all_accounts:
            if acc.get("project_id") == target_project:
                billed_account = acc
                break
                
        if not billed_account:
            send_telegram_msg("❌ Tizimda Billing ulangan kalit (service-503705) topilmadi!")
            return
            
        # Topilgan kalitni alohida vaqtinchalik faylga saqlash (GenAI SDK ishlashi uchun)
        veo_sa_path = "veo_service_account.json"
        with open(veo_sa_path, "w") as f:
            json.dump(billed_account, f)
        
        # Google Gen AI SDK uchun muhit o'zgaruvchilarini to'g'rilash
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = veo_sa_path
        os.environ["GOOGLE_CLOUD_PROJECT"] = target_project
        os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"
        
        # Client ni sozlash
        client = genai.Client(vertexai=True)
        
        # Konfiguratsiya
        config = types.GenerateVideosConfig(
            aspect_ratio=ratio,
            duration_seconds=5
        )
        
        # Haqiqiy Veo modelini chaqirish
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
            
        caption = f"🎥 <b>Sizning Veo 3.1 Videongiz Tayyor!</b>\n\n📝 Prompt: <i>{prompt}</i>\n\n⚡️ <i>Vertex AI (Haqiqiy Veo) tomonidan muvaffaqiyatli yaratildi.</i>"
        send_telegram_video(output_filename, caption)
        
        # Tozalash
        if os.path.exists(output_filename):
            os.remove(output_filename)
        if os.path.exists(veo_sa_path):
            os.remove(veo_sa_path)
            
    except Exception as e:
        send_telegram_msg(f"❌ Video generatsiya jarayonida xatolik yuz berdi: {e}")
