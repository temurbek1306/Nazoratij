import time
import os
from agent_tools import get_pending_video, expose_video_url, post_to_instagram
from instagram_api import InstagramAPI

def run():
    print("🚀 GitHub Actions: Avtomatik Video Yuklash boshlandi...")
    
    video_name = get_pending_video()
    if not video_name:
        print("📁 Hozircha yangi videolar yo'q. Dastur to'xtatildi.")
        return
        
    print(f"🎬 Video topildi: {video_name}")
    print("🌐 Lokal server va Ngrok ishga tushmoqda...")
    url = expose_video_url(video_name)
    
    if not url:
        print("❌ Ngrok URL olib bo'lmadi.")
        return
        
    print(f"🔗 Public URL: {url}")
    
    # User requested hardcoded Japanese caption for all videos
    caption = """今夜、
@thvはハリウッドで行われた @gracieabrams
と@dojacatのパフォーマンスを観客席から鑑賞しました。
ファッションショーにも慣れている
@bts.bighitofficialのスターは、ランウェイに登場してもおかしくないような装いで登場しました。
#onepiece#loki#mindcatalyst_snr#bhaichara"""

    print(f"📝 Instagramga joylanmoqda...")
    success = post_to_instagram(url, caption, video_name)
    
    if success:
        print("✅ Video IG ga muvaffaqiyatli yuklandi va 'posted' papkasiga o'tkazildi!")
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
            
            # Instagram ssenariysining birinchi qatorini sarlavha qilib olamiz
            title = caption.split('\n')[0][:100] 
            
            # local path for youtube upload
            local_video_path = f"videos/posted/{video_name}" if success else f"videos/pending/{video_name}"
            
            if os.path.exists(local_video_path):
                yt_api.upload_shorts(
                    video_path=local_video_path,
                    title=title,
                    description=caption
                )
            else:
                print(f"❌ YouTube uchun lokal fayl topilmadi: {local_video_path}")
        except Exception as yt_error:
            print(f"⚠️ YouTube ga yuklashda xatolik: {yt_error}")
    else:
        print("⚠️ YouTube API sirlari topilmadi. Shorts yuklash tashlab o'tildi.")

if __name__ == "__main__":
    run()
