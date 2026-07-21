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
    
    # Keling agentimiz kabi sun'iy intellekt matnini ishlatmaymiz yoki 
    # hozircha o'zingiz yozgan viral shablonni beramiz (chunki AI ulanmagan bo'lishi mumkin)
    # Agar OpenAI bo'lsa uni ham shu yerda ulash mumkin.
    
    caption = "Yana bir ajoyib video! 😂 Sizda ham shunday holatlar bo'lganmi? 👇 \n\nFikringizni izohlarda qoldiring!\n\n#rek #rekka #kino #dasturlash #temurbekdev #trend #uzbekistan #foryou"
    
    try:
        import google.generativeai as genai
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            print("🧠 Gemini AI ishga tushmoqda, ssenariy yozilmoqda...")
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-flash-latest")
            prompt = f"Men Instagram Reels uchun '{video_name}' deb nomlangan videoni yuklayapman. Iltimos, menga shu videoga mos, odamlarni o'ziga tortadigan (viral bo'ladigan) qisqa o'zbekcha zo'r matn (caption) va trenddagi heshteglarni yozib ber. Boshqa narsa yozma, faqat caption va heshteglar kerak."
            response = model.generate_content(prompt)
            if response.text:
                caption = response.text.strip()
                print("✨ Gemini AI matni tayyor!")
    except Exception as e:
        print(f"⚠️ Gemini ishlatishda xatolik (shablondan foydalaniladi): {e}")
    
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
