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
    
    clean_title = video_name.replace('.mp4', '').replace('_', ' ')
    caption = f"{clean_title} 😂👇\n\nFikringizni izohlarda qoldiring!\n\n#rek #rekka #kino #dasturlash #temurbekdev #trend #uzbekistan #foryou"
    
    try:
        import google.generativeai as genai
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            print("🧠 Gemini AI ishga tushmoqda, ssenariy yozilmoqda...")
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-1.5-flash-latest")
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
        print("✅ Video muvaffaqiyatli yuklandi va 'posted' papkasiga o'tkazildi!")
    else:
        print("❌ Videoni yuklashda xatolik yuz berdi.")
        # Agar xato bo'lsa, workflow failure berishi uchun exit(1) qilish mumkin, lekin kerak emas, oddiygina yopiladi.

if __name__ == "__main__":
    run()
