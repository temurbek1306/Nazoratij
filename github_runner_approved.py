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
        clean_caption = data.get(f"clean_{choice}", caption)
        
        print(f"🎬 Video: {video_name}")
        print(f"📝 Tanlangan matn ({choice.upper()}): {caption[:50]}...")
        
        url = expose_video_url(video_name)
        if not url:
            print("❌ Ngrok URL olib bo'lmadi.")
            return
            
        # Platformani tekshirish
        base_name = os.path.splitext(video_name)[0]
        platforms = ["ig", "yt", "tg", "fb"] # Default if not set
        platform_file = f"videos/pending/{base_name}.platform.txt"
        if os.path.exists(platform_file):
            with open(platform_file, "r", encoding="utf-8") as f:
                platforms = f.read().strip().split(",")
                
        # 🧪 Trial Reel tekshiruvi
        is_trial = data.get("is_trial", False)
        trial_file = f"videos/pending/{base_name}.trial.txt"
        if not is_trial and os.path.exists(trial_file):
            with open(trial_file, "r", encoding="utf-8") as f:
                is_trial = f.read().strip().lower() in ["true", "1", "yes"]
                
        import ai_assistant
        try:
            first_comment = ai_assistant.get_standard_comment(caption)
        except:
            first_comment = "👇 Fikringizni izohlarda yozib qoldiring!"

        status_messages = []
        local_video_path = f"videos/pending/{video_name}"
        
        # --- INSTAGRAM ---
        if "ig" in platforms:
            print(f"📝 Instagramga joylanmoqda... (Trial: {is_trial})")
            from agent_tools import post_ig_comment
            ig_media_id = post_to_instagram(url, caption, video_name, is_trial=is_trial)
            if ig_media_id:
                status_messages.append("✅ Instagram (🧪 Trial Reel)" if is_trial else "✅ Instagram")
                try:
                    post_ig_comment(ig_media_id, first_comment)
                except: pass
            else:
                status_messages.append("❌ Instagram")
                
        # --- YOUTUBE SHORTS ---
        if "yt" in platforms:
            yt_client_id = os.getenv("YOUTUBE_CLIENT_ID")
            yt_client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
            yt_refresh_token = os.getenv("YOUTUBE_REFRESH_TOKEN")
            if yt_client_id and yt_client_secret and yt_refresh_token:
                try:
                    print("📺 YouTubega joylanmoqda...")
                    from youtube_api import YouTubeAPI
                    yt_api = YouTubeAPI(yt_client_id, yt_client_secret, yt_refresh_token)
                    title = caption.split('\n')[0][:100] 
                    if os.path.exists(local_video_path):
                        yt_video_id = yt_api.upload_shorts(video_path=local_video_path, title=title, description=caption)
                        if yt_video_id:
                            status_messages.append("✅ YouTube")
                            try:
                                yt_api.post_comment(yt_video_id, first_comment)
                            except:
                                pass
                    else:
                        status_messages.append("❌ YouTube (Fayl topilmadi)")
                except Exception as e:
                    status_messages.append(f"❌ YouTube ({str(e)[:50]})")
            else:
                status_messages.append("⚠️ YouTube (API kalitlar yo'q)")

        # --- TELEGRAM CHANNEL ---
        if "tg" in platforms:
            from agent_tools import post_to_telegram
            if os.path.exists(local_video_path):
                tg_caption = clean_caption + "\n\nTelegram kanal: @Temurbek_dev\nTelegram bot: @TemurbekDevbot"
                if post_to_telegram(local_video_path, tg_caption):
                    status_messages.append("✅ Telegram Channel")
                else:
                    status_messages.append("❌ Telegram Channel")

        # --- FACEBOOK REELS ---
        if "fb" in platforms:
            fb_page_id = os.getenv("FB_PAGE_ID")
            fb_page_token = os.getenv("FB_PAGE_ACCESS_TOKEN")
            if fb_page_id and fb_page_token:
                try:
                    from facebook_api import FacebookReelsAPI
                    fb_api = FacebookReelsAPI(fb_page_id, fb_page_token)
                    if os.path.exists(local_video_path):
                        if fb_api.upload_reel(local_video_path, caption):
                            status_messages.append("✅ Facebook")
                        else:
                            status_messages.append("❌ Facebook")
                except Exception as e:
                    status_messages.append(f"❌ Facebook ({str(e)[:50]})")
            else:
                status_messages.append("⚠️ Facebook (API kalitlar yo'q)")

        # # --- TELEGRAM HISOBOT ---
        tg_token = "8674470670:AAER3Y3EfZ44eFUhxKTpsGX_X_Vg6LvKYOQ"
        tg_admin = "5701828462"
        if tg_token and tg_admin:
            import requests
            try:
                status_str = "\n".join(status_messages)
                tg_msg = f"🚀 Video yuklash yakunlandi!\n\nVariant: {choice.upper()}\n\nNatijalar:\n{status_str}"
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
            
        tg_token = "8674470670:AAER3Y3EfZ44eFUhxKTpsGX_X_Vg6LvKYOQ"
        tg_admin = "5701828462"
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
