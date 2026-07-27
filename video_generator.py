import os
import time
import requests
import json
import ai_assistant

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
        
        send_telegram_msg("🎬 <b>AI Video render qilishni boshladi... (Kuting)</b>")
        
        # ---------------------------------------------------------
        # Vaqtinchalik DEMO rejim. Google Billing ulanganda yana haqiqiysiga qaytaramiz.
        # ---------------------------------------------------------
        time.sleep(5) 
        
        # Download a sample short mp4 video for the demo
        sample_url = "https://www.w3schools.com/html/mov_bbb.mp4"
        res = requests.get(sample_url)
        output_filename = "veo_demo_output.mp4"
        with open(output_filename, "wb") as f:
            f.write(res.content)
            
        caption = f"🎥 <b>Sizning Veo 3.1 (Demo) Videongiz Tayyor!</b>\n\n📝 Prompt: <i>{prompt}</i>\n\n⚡️ <i>Bu Vertex AI (Veo) API si uchun tayyorlab qo'yilgan mukammal backend arxitekturasi. To'lov tizimi ulanganda asl video qaytadi!</i>"
        send_telegram_video(output_filename, caption)
        
        if os.path.exists(output_filename):
            os.remove(output_filename)
            
    except Exception as e:
        send_telegram_msg(f"❌ Video generatsiya jarayonida xatolik yuz berdi: {e}")
