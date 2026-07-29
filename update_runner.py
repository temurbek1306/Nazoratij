import os
import re

with open("github_runner_approved.py", "r", encoding="utf-8") as f:
    content = f.read()

# We need to replace everything from `# Platformani tekshirish` up to `# --- TELEGRAM HISOBOT ---`
start_marker = "# Platformani tekshirish"
end_marker = "# --- TELEGRAM HISOBOT ---"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

new_logic = """# Platformani tekshirish
        base_name = os.path.splitext(video_name)[0]
        platforms = ["ig", "yt", "tg", "fb", "tt"] # Default if not set
        platform_file = f"videos/pending/{base_name}.platform.txt"
        if os.path.exists(platform_file):
            with open(platform_file, "r", encoding="utf-8") as f:
                platforms = f.read().strip().split(",")
                
        import ai_assistant
        try:
            first_comment = ai_assistant.get_standard_comment(caption)
        except:
            first_comment = "👇 Fikringizni izohlarda yozib qoldiring!"

        status_messages = []
        local_video_path = f"videos/pending/{video_name}"
        
        # --- INSTAGRAM ---
        if "ig" in platforms:
            print(f"📝 Instagramga joylanmoqda...")
            ig_media_id = post_to_instagram(url, caption, video_name)
            if ig_media_id:
                status_messages.append("✅ Instagram")
                from agent_tools import post_ig_comment
                post_ig_comment(ig_media_id, first_comment)
            else:
                status_messages.append("❌ Instagram")
                
        # --- YOUTUBE SHORTS ---
        if "yt" in platforms:
            yt_client_id = os.getenv("YOUTUBE_CLIENT_ID")
            yt_client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
            yt_refresh_token = os.getenv("YOUTUBE_REFRESH_TOKEN")
            if yt_client_id and yt_client_secret and yt_refresh_token:
                try:
                    print("\\n📺 YouTube Shorts yuklash boshlanmoqda...")
                    from youtube_api import YouTubeAPI
                    yt_api = YouTubeAPI(yt_client_id, yt_client_secret, yt_refresh_token)
                    title = caption.split('\\n')[0][:100] 
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
                if post_to_telegram(local_video_path, caption):
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

        # --- TIKTOK ---
        if "tt" in platforms:
            tt_client_key = os.getenv("TIKTOK_CLIENT_KEY")
            tt_client_secret = os.getenv("TIKTOK_CLIENT_SECRET")
            tt_refresh_token = os.getenv("TIKTOK_REFRESH_TOKEN")
            if tt_client_key and tt_client_secret and tt_refresh_token:
                try:
                    from tiktok_api import TikTokAPI
                    tt_api = TikTokAPI(tt_client_key, tt_client_secret, tt_refresh_token)
                    if os.path.exists(local_video_path):
                        if tt_api.upload_video(local_video_path, caption):
                            status_messages.append("✅ TikTok")
                        else:
                            status_messages.append("❌ TikTok")
                except Exception as e:
                    status_messages.append(f"❌ TikTok ({str(e)[:50]})")
            else:
                status_messages.append("⚠️ TikTok (API kalitlar yo'q)")

        # """

new_content = content[:start_idx] + new_logic + content[end_idx:]

# Also update the telegram report part
old_report = """tg_msg = f"✅ Boss, video tarmoqlarga uzatildi!\\n\\nVariant: {choice.upper()}\\n\\n{yt_status_msg}\""""
new_report = """status_str = "\\n".join(status_messages)
                tg_msg = f"🚀 Video yuklash yakunlandi!\\n\\nVariant: {choice.upper()}\\n\\nNatijalar:\\n{status_str}\""""
new_content = new_content.replace(old_report, new_report)

with open("github_runner_approved.py", "w", encoding="utf-8") as f:
    f.write(new_content)
    
print("Updated github_runner_approved.py successfully.")
