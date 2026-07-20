import time
from agent_tools import get_pending_video, expose_video_url, post_to_instagram

captions = [
    "Bu videoni hamma qidiryapti, lekin hech qayerda yo'q... 🤯 To'liq sirlarni bilish uchun profilimdagi botga ulaning! 🚀👇\n\n#rek #rekka #kino #telegrambot #temurbekdev #trend #uzbekistan #foryou",
    
    "Sun'iy intellekt orqali shunday natijaga erishish mumkinligini bilarmidingiz? 🔥 Eng so'nggi trendlar faqat bizda! Profilga o'ting va o'zingiz sinab ko'ring 🤖✨\n\n#suniyintellekt #aiuzb #rek #dasturlash #temurbekdev #trendvideo #uzb"
]

print("🚀 Viral Video Uploader ishga tushdi...")

for i in range(1):
    video_name = get_pending_video()
    if not video_name:
        print("Boshqa video qolmadi!")
        break
        
    print(f"\n[{i+1}] Video topildi: {video_name}")
    print(f"[{i+1}] Server ishga tushmoqda va Ngrok URL olinmoqda...")
    url = expose_video_url(video_name)
    print(f"[{i+1}] Public URL: {url}")
    
    caption = captions[0]
    
    print(f"[{i+1}] Instagramga '{caption[:30]}...' yozuvi bilan yuklanmoqda (Kuting...)")
    
    success = post_to_instagram(url, caption, video_name)
    if success:
        print(f"[{i+1}] ✅ MUVAFFAQIYATLI yuklandi!")
    else:
        print(f"[{i+1}] ❌ XATOLIK yuz berdi.")
        
    print("5 soniya kutilmoqda...")
    time.sleep(5)

print("\n🎉 Barcha ishlar yakunlandi!")
