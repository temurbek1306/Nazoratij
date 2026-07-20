import agent_tools
import time

print("Instagram Auto Reels Bot - Test Script")
print("--------------------------------------")

print("[1] Pending (kutilayotgan) videolar tekshirilmoqda...")
filename = agent_tools.get_pending_video()
if not filename:
    print("Hozircha pending papkasida video yo'q!")
    exit(1)

print(f"[2] Video topildi: {filename}")
print("[3] Ngrok orqali video internetga ochiq (public) qilinmoqda...")
try:
    video_url = agent_tools.expose_video_url(filename)
    print(f"Public URL: {video_url}")
except Exception as e:
    print(f"Ngrok xatosi: {e}")
    exit(1)

caption = "Instagram Auto Reels Bot orqali yuklangan birinchi test video! 🚀 #test #autoreels"
print(f"[4] Instagramga jo'natilmoqda... (bu jarayon bir necha daqiqa olishi mumkin)")

try:
    success = agent_tools.post_to_instagram(video_url, caption, filename)
    if success:
        print("\n🎉 TABRIKLAYMIZ! Video Instagramga muvaffaqiyatli yuklandi!")
    else:
        print("\n❌ XATOLIK: Videoni Instagramga yuklab bo'lmadi.")
except Exception as e:
    print(f"\n❌ Dasturda xatolik yuz berdi: {e}")
