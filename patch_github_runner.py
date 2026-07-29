import re

with open("github_runner.py", "r", encoding="utf-8") as f:
    content = f.read()

helper_function = """def post_to_platforms(platforms_str, local_video_path, url, caption, first_comment, video_name):
    import os
    platforms = platforms_str.split(',') if platforms_str else ["ig", "yt", "fb", "tg"]
    status_messages = []
    
    # --- INSTAGRAM ---
    if "ig" in platforms or "both" in platforms:
        print(f"📝 Instagramga joylanmoqda...")
        from agent_tools import post_to_instagram, post_ig_comment
        ig_media_id = post_to_instagram(url, caption, video_name)
        if ig_media_id:
            status_messages.append("✅ Instagram")
            try:
                post_ig_comment(ig_media_id, first_comment)
            except: pass
        else:
            status_messages.append("❌ Instagram")
    else:
        status_messages.append("⏭ Instagram: Tanlanmagan")

    # --- YOUTUBE SHORTS ---
    if "yt" in platforms or "both" in platforms:
        yt_client_id = os.getenv("YOUTUBE_CLIENT_ID")
        yt_client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
        yt_refresh_token = os.getenv("YOUTUBE_REFRESH_TOKEN")
        if yt_client_id and yt_client_secret and yt_refresh_token:
            try:
                print("📺 YouTubega joylanmoqda...")
                from youtube_api import YouTubeAPI
                yt_api = YouTubeAPI(yt_client_id, yt_client_secret, yt_refresh_token)
                title = caption.split('\\n')[0][:100]
                if os.path.exists(local_video_path):
                    yt_video_id = yt_api.upload_shorts(local_video_path, title, caption)
                    if yt_video_id:
                        status_messages.append("✅ YouTube")
                        try:
                            yt_api.post_comment(yt_video_id, first_comment)
                        except: pass
                    else:
                        status_messages.append("❌ YouTube (Fayl topilmadi)")
            except Exception as e:
                status_messages.append(f"❌ YouTube Xatolik: {str(e)[:50]}")
        else:
            status_messages.append("⚠️ YouTube API kalitlar kiritilmagan")
    else:
        status_messages.append("⏭ YouTube: Tanlanmagan")

    # --- TELEGRAM CHANNEL ---
    if "tg" in platforms:
        from agent_tools import post_to_telegram
        if os.path.exists(local_video_path):
            if post_to_telegram(local_video_path, caption):
                status_messages.append("✅ Telegram Channel")
            else:
                status_messages.append("❌ Telegram Channel")
        else:
            status_messages.append("❌ Telegram Channel: Fayl topilmadi")
            
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
                status_messages.append(f"❌ Facebook Xatolik: {str(e)[:50]}")
        else:
            status_messages.append("⚠️ Facebook API kalitlar yo'q")

    return "\\n".join(status_messages)
"""

# We need to insert this function before 'def run():'
content = content.replace("def run():", helper_function + "\ndef run():")

# Replace manual logic block
manual_regex = re.compile(r'        if platform in \["ig", "both"\]:.*?send_alert\(f"✅ Boss, video holati \(Qo\'lda yozilgan izoh bilan\):\\n\\nVideo: \{video_name\}\\n\\n\{yt_status_msg\}"\)', re.DOTALL)
new_manual = """        status_str = post_to_platforms(platform, local_video_path, url, manual_caption, first_comment, video_name)
        send_alert(f"✅ Boss, video holati (Qo'lda yozilgan izoh bilan):\\n\\nVideo: {video_name}\\n\\n{status_str}")"""
content = manual_regex.sub(new_manual, content)

# Replace fallback logic block
fallback_regex = re.compile(r'    if platform in \["ig", "both"\]:.*?send_alert\(f"📋 <b>Yangi video yakuniy hisoboti\!</b>\\n\\nNomi: <code>\{video_name\}</code>\\n\\n\{yt_status_msg\}"\)', re.DOTALL)
new_fallback = """    status_str = post_to_platforms(platform, local_video_path, url, final_fallback_caption, first_comment, video_name)
    send_alert(f"📋 <b>Yangi video yakuniy hisoboti!</b>\\n\\nNomi: <code>{video_name}</code>\\n\\n{status_str}")"""
content = fallback_regex.sub(new_fallback, content)

with open("github_runner.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Patch applied to github_runner.py")
