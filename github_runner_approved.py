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
            
        # Platformani tekshirish
        base_name = os.path.splitext(video_name)[0]
        platform = "both"
        platform_file = f"videos/pending/{base_name}.platform.txt"
        if os.path.exists(platform_file):
            with open(platform_file, "r", encoding="utf-8") as f:
                platform = f.read().strip()
                
        if platform in ["ig", "both"]:
            print(f"📝 Instagramga joylanmoqda...")
            ig_media_id = post_to_instagram(url, caption, video_name)
            
            import ai_assistant
            try:
                first_comment = ai_assistant.get_standard_comment(caption)
            except:
                first_comment = "👇 Fikringizni izohlarda yozib qoldiring!"
            
            if ig_media_id:
                print("✅ Video IG ga muvaffaqiyatli yuklandi va 'posted' papkasiga o'tkazildi!")
                
                # --- IG AUTO-COMMENT ---
                from agent_tools import post_ig_comment
                post_ig_comment(ig_media_id, first_comment)
                
            else:
                print("❌ Videoni IG ga yuklashda xatolik yuz berdi.")
        else:
            print("⏭ Instagram tanlanmagan, tashlab o'tilmoqda...")
            import ai_assistant
            try:
                first_comment = ai_assistant.get_standard_comment(caption)
            except:
                first_comment = "👇 Fikringizni izohlarda yozib qoldiring!"
            
        yt_status_msg = ""
        # --- YOUTUBE SHORTS YUKLASH ---
        if platform in ["yt", "both"]:
            yt_client_id = os.getenv("YOUTUBE_CLIENT_ID")
            yt_client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
            yt_refresh_token = os.getenv("YOUTUBE_REFRESH_TOKEN")
            
            if yt_client_id and yt_client_secret and yt_refresh_token:
                try:
                    print("\n📺 YouTube Shorts yuklash boshlanmoqda...")
                    from youtube_api import YouTubeAPI
                    yt_api = YouTubeAPI(yt_client_id, yt_client_secret, yt_refresh_token)
                    title = caption.split('\n')[0][:100] 
                    local_video_path = f"videos/pending/{video_name}"
                    
                    if os.path.exists(local_video_path):
                        yt_video_id = yt_api.upload_shorts(video_path=local_video_path, title=title, description=caption)
                        if yt_video_id:
                            yt_status_msg = "✅ YouTube: Muvaffaqiyatli joylandi!"
                            # --- YOUTUBE AUTO-COMMENT ---
                            try:
                                yt_api.post_comment(yt_video_id, first_comment)
                            except:
                                pass
                    else:
                        yt_status_msg = "❌ YouTube: Lokal fayl topilmadi"
                except Exception as yt_error:
                    yt_status_msg = f"❌ YouTube Xatolik: {yt_error}"
            else:
                yt_status_msg = "⚠️ YouTube: API kalitlar yo'q, shuning uchun joylanmadi"
        else:
            yt_status_msg = "⏭ YouTube: Tanlanmagan"
                
        # --- TELEGRAM HISOBOT ---
        tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
        tg_admin = os.getenv("TELEGRAM_ADMIN_ID")
        if tg_token and tg_admin:
            import requests
            try:
                tg_msg = f"✅ Boss, video tarmoqlarga uzatildi!\n\nVariant: {choice.upper()}\n\n{yt_status_msg}"
                url = f"https://api.telegram.org/bot{tg_token}/sendMessage"
                res = requests.post(url, data={
                    "chat_id": tg_admin,
                    "text": tg_msg,
                    "parse_mode": "HTML"
                })
                if res.status_code != 200:
                    # Retry without HTML
                    requests.post(url, data={"chat_id": tg_admin, "text": tg_msg})
            except Exception as e:
                pass
                
        # JSON va Video fayllarni tozalash (Musur qolmasligi uchun)
        if os.path.exists(json_path):
            os.remove(json_path)
            
        from video_manager import VideoManager
        VideoManager().mark_as_posted(video_name)

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
                print("📩 Telegramga hisobot yuborildi.")
            except Exception:
                pass

if __name__ == "__main__":
    run()
