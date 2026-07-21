import os
import glob
import requests
import github_runner

def send_telegram_msg(text):
    tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
    tg_admin = os.getenv("TELEGRAM_ADMIN_ID")
    if tg_token and tg_admin:
        try:
            requests.post(f"https://api.telegram.org/bot{tg_token}/sendMessage", data={
                "chat_id": tg_admin,
                "text": text,
                "parse_mode": "HTML"
            })
        except Exception as e:
            print(f"Telegram xatosi: {e}")

def handle_list():
    os.makedirs("videos/pending", exist_ok=True)
    files = [f for f in os.listdir("videos/pending") if f.endswith(('.mp4', '.mov'))]
    if not files:
        send_telegram_msg("📭 Navbatda hech qanday video yo'q.")
        return
    
    msg = f"📋 <b>Navbatdagi videolar ({len(files)} ta):</b>\n\n"
    for i, f in enumerate(files, 1):
        msg += f"{i}. {f}\n"
    
    send_telegram_msg(msg)

def handle_clear():
    files = glob.glob("videos/pending/*")
    count = 0
    for f in files:
        if f.endswith(('.mp4', '.mov', '.txt')):
            os.remove(f)
            count += 1
            
    send_telegram_msg(f"🧹 <b>Navbat tozalandi!</b>\n\n{count} ta fayl o'chirib tashlandi.")

def handle_stats():
    os.makedirs("videos/posted", exist_ok=True)
    os.makedirs("videos/pending", exist_ok=True)
    
    # Local stats
    posted_files = [f for f in os.listdir("videos/posted") if f.endswith(('.mp4', '.mov'))]
    pending_files = [f for f in os.listdir("videos/pending") if f.endswith(('.mp4', '.mov'))]
    
    msg = "📊 <b>AvtoReels Statistikasi</b>\n\n"
    msg += f"✅ Joylangan videolar: <b>{len(posted_files)}</b> ta\n"
    msg += f"⏳ Kutilayotgan videolar: <b>{len(pending_files)}</b> ta\n\n"
    
    # YouTube stats
    yt_client_id = os.getenv("YOUTUBE_CLIENT_ID")
    yt_client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
    yt_refresh_token = os.getenv("YOUTUBE_REFRESH_TOKEN")
    
    if yt_client_id and yt_client_secret and yt_refresh_token:
        try:
            from youtube_api import YouTubeAPI
            yt_api = YouTubeAPI(yt_client_id, yt_client_secret, yt_refresh_token)
            yt_stats = yt_api.get_channel_stats()
            
            if yt_stats:
                msg += "📺 <b>YouTube Kanalingiz:</b>\n"
                msg += f"👥 Obunachilar: <b>{yt_stats['subscribers']}</b>\n"
                msg += f"👁 Prosmotrlar jami: <b>{yt_stats['views']}</b>\n"
                msg += f"🎥 Videolar jami: <b>{yt_stats['videos']}</b>\n"
            else:
                msg += "⚠️ <i>YouTube statistikasini olish imkonsiz (Ruxsat/Scope cheklangan bo'lishi mumkin)</i>"
        except Exception as e:
            msg += f"⚠️ <i>YouTube ma'lumotlarini olishda xatolik yuz berdi.</i>"
            
    send_telegram_msg(msg)

def run():
    command = os.getenv("TELEGRAM_COMMAND", "").lower().strip()
    
    if not command:
        print("Hech qanday komanda berilmadi.")
        return
        
    print(f"Qabul qilingan komanda: {command}")
    
    if command == "list":
        handle_list()
    elif command == "clear":
        handle_clear()
    elif command == "stats":
        handle_stats()
    elif command == "post_now":
        send_telegram_msg("🚀 Zudlik bilan post qilish jarayoni boshlandi! (github_runner ishga tushmoqda...)")
        github_runner.run()
    else:
        send_telegram_msg("❓ Noma'lum komanda.")

if __name__ == "__main__":
    run()
