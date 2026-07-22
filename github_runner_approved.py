import os
import json
from agent_tools import expose_video_url, post_to_instagram

def run():
    print("🚀 Tasdiqlangan videoni joylash boshlanmoqda...")
    
    command = os.getenv("TELEGRAM_COMMAND", "")
    
    if command.startswith("post_a_") or command.startswith("post_b_") or command.startswith("post_c_"):
        parts = command.split("_", 2)
        choice = parts[1] # a, b or c
        video_name = parts[2]
        
        json_path = f"videos/pending/{video_name}.json"
        
        if not os.path.exists(json_path):
            print(f"❌ Fayl topilmadi: {json_path}")
            return
            
        with open(json_path, "r") as f:
            data = json.load(f)
            
        caption = data.get(f"caption_{choice}", "")
        
        print(f"🎬 Video: {video_name}")
        print(f"📝 Tanlangan matn ({choice.upper()}): {caption[:50]}...")
        
        url = expose_video_url(video_name)
        if not url:
            print("❌ Ngrok URL olib bo'lmadi.")
            return
            
        print(f"📝 Instagramga joylanmoqda...")
        ig_media_id = post_to_instagram(url, caption, video_name)
        
        first_comment = "Videodagi holat kimga tanish? 😂 Fikringizni yozib qoldiring 👇"
        
        if ig_media_id:
            print("✅ Video IG ga muvaffaqiyatli yuklandi va 'posted' papkasiga o'tkazildi!")
            
            # --- IG AUTO-COMMENT ---
            from agent_tools import post_ig_comment
            post_ig_comment(ig_media_id, first_comment)
            
        else:
            print("❌ Videoni IG ga yuklashda xatolik yuz berdi.")
            
        # --- YOUTUBE SHORTS YUKLASH ---
        yt_client_id = os.getenv("YOUTUBE_CLIENT_ID")
        yt_client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
        yt_refresh_token = os.getenv("YOUTUBE_REFRESH_TOKEN")
        
        if yt_client_id and yt_client_secret and yt_refresh_token:
            try:
                print("\n📺 YouTube Shorts yuklash boshlanmoqda...")
                from youtube_api import YouTubeAPI
                yt_api = YouTubeAPI(yt_client_id, yt_client_secret, yt_refresh_token)
                title = caption.split('\n')[0][:100] 
                local_video_path = f"videos/posted/{video_name}" if ig_media_id else f"videos/pending/{video_name}"
                
                if os.path.exists(local_video_path):
                    yt_video_id = yt_api.upload_shorts(video_path=local_video_path, title=title, description=caption)
                    if yt_video_id:
                        # --- YOUTUBE AUTO-COMMENT ---
                        yt_api.post_comment(yt_video_id, first_comment)
                else:
                    print(f"❌ YouTube uchun lokal fayl topilmadi: {local_video_path}")
            except Exception as yt_error:
                print(f"⚠️ YouTube ga yuklashda xatolik: {yt_error}")
                
        # --- TELEGRAM HISOBOT ---
        tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
        tg_admin = os.getenv("TELEGRAM_ADMIN_ID")
        if tg_token and tg_admin:
            import requests
            try:
                tg_msg = f"✅ Boss, video tarmoqlarga muvaffaqiyatli joylandi!\n\nVariant: {choice.upper()}"
                requests.post(f"https://api.telegram.org/bot{tg_token}/sendMessage", data={
                    "chat_id": tg_admin,
                    "text": tg_msg
                })
            except Exception as e:
                pass
                
        # JSON faylni tozalash
        os.remove(json_path)

    elif command.startswith("cancel_"):
        video_name = command.split("_", 1)[1]
        json_path = f"videos/pending/{video_name}.json"
        if os.path.exists(json_path):
            os.remove(json_path)
            
        tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
        tg_admin = os.getenv("TELEGRAM_ADMIN_ID")
        if tg_token and tg_admin:
            import requests
            try:
                requests.post(f"https://api.telegram.org/bot{tg_token}/sendMessage", data={
                    "chat_id": tg_admin,
                    "text": f"❌ {video_name} bekor qilindi. U hali ham navbatda turibdi, qaytadan /post_now qilib yuborishingiz mumkin."
                })
            except Exception:
                pass

if __name__ == "__main__":
    run()
