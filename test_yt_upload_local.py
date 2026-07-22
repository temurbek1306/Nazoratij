import os
import time
from dotenv import load_dotenv
from youtube_api import YouTubeAPI
import agent_tools

load_dotenv()

print("📺 YouTube Auto Reels Bot - Test Script")
print("--------------------------------------")

# Get a pending video
filename = agent_tools.get_pending_video()
if not filename:
    print("❌ Hozircha pending papkasida video yo'q!")
    exit(1)

local_video_path = f"videos/pending/{filename}"
print(f"🎬 Video topildi: {local_video_path}")

caption = "YouTube Shorts Test: Hayvonlar o'zini odamdek tutganda 😅 #shorts #funny"

yt_client_id = os.getenv("YOUTUBE_CLIENT_ID")
yt_client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
yt_refresh_token = os.getenv("YOUTUBE_REFRESH_TOKEN")

if yt_client_id and yt_client_secret and yt_refresh_token:
    try:
        print("🔗 YouTube API'ga ulanilmoqda...")
        yt_api = YouTubeAPI(yt_client_id, yt_client_secret, yt_refresh_token)
        
        print(f"📤 YouTube Shorts yuklash boshlanmoqda...")
        video_id = yt_api.upload_shorts(video_path=local_video_path, title="YouTube Shorts Test 🚀", description=caption)
        
        if video_id:
            print(f"\n🎉 TABRIKLAYMIZ! Video YouTube'ga muvaffaqiyatli yuklandi!")
            print(f"URL: https://youtube.com/shorts/{video_id}")
    except Exception as e:
        print(f"\n❌ YouTube yuklash xatosi: {e}")
else:
    print("❌ Kalitlar topilmadi (.env yoki secrets).")
