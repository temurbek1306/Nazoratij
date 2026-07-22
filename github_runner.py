import time
import os
from agent_tools import get_pending_video, expose_video_url, post_to_instagram
from instagram_api import InstagramAPI
import requests

def send_alert(msg):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_ADMIN_ID")
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, data={"chat_id": chat_id, "text": msg, "parse_mode": "HTML"})

def run():
    print("🚀 GitHub Actions: Avtomatik Video Yuklash boshlandi...")
    
    video_name = get_pending_video()
    if not video_name:
        print("📁 Hozircha yangi videolar yo'q. Dastur to'xtatildi.")
        send_alert("⚠️ <b>Diqqat! Video qolmadi!</b>\n\nNavbatdagi (Pending) papkada videolar tugadi. Iltimos, tizim ishlashda davom etishi uchun yana yangi videolar yuboring!")
        return
        
    print(f"🎬 Video topildi: {video_name}")
    print("🌐 Lokal server va Ngrok ishga tushmoqda...")
    url = expose_video_url(video_name)
    
    if not url:
        print("❌ Ngrok URL olib bo'lmadi.")
        return
        
    print(f"🔗 Public URL: {url}")
    
    local_video_path = f"videos/pending/{video_name}"
    
    # Standart zaxira (fallback) caption (SMM qoidalari bo'yicha)
    caption = "Buni oxirigacha ko'ring! 😅 Hayotda hammamiz bilan kamida bir marta shunaqasi bo'lgan, to'g'rimi? 👇\n\nSiz-chi, bunday vaziyatda nima qilgan bo'lardingiz? Fikrlar kutyapman!"
    
    import ai_assistant
    km = ai_assistant.KeyManager()
    
    for attempt in range(5):
        gemini_key = km.get_gemini_key()
        if not gemini_key:
            break
            
        try:
            import google.generativeai as genai
            print(f"🧠 Gemini AI ishga tushmoqda (Urinish {attempt+1})...")
            genai.configure(api_key=gemini_key)
            
            print(f"📤 Video Gemini serveriga yuklanmoqda: {local_video_path}")
            video_file = genai.upload_file(path=local_video_path)
            
            print("⏳ Gemini videoni qayta ishlashini kutyapmiz (bu 10-30 soniya olishi mumkin)...")
            while video_file.state.name == "PROCESSING":
                print(".", end="", flush=True)
                time.sleep(5)
                video_file = genai.get_file(video_file.name)
            
            if video_file.state.name == "FAILED":
                print("\n❌ Gemini videoni qayta ishlashda xatoga yo'l qo'ydi.")
            else:
                print("\n✨ Video tayyor. Ssenariy yozilmoqda...")
                model = genai.GenerativeModel("gemini-1.5-flash")
                prompt = """Sen O'zbekistondagi eng mashhur SMM va Video tahlilchisan! Shu videoni IPI-IDAN IGASIGACHA, har bir detalini (yuz harakatlari, emotsiyalar, ekrandagi yozuvlar, kiyimlar, ovoz) diqqat bilan ko'r va tahlil qil.
1. Kadrda nima bo'lyapti o'zi? (To'liq voqea)
2. Ekranda qanday so'zlar/yozuvlar bor?
3. Ovozda nima deyilmoqda?

Shularni tahlil qilib, batafsil SUMMARY yoz. 
Keyin Instagram Reels uchun videoning AYNAN SHU voqeasiga 100% bog'langan, hazil aralash yoki kreativ O'ZBEKCHA CAPTION (post matni) yoz.
QOIDALAR: 
- Caption aynan videodagi holat bilan bog'lanishi SHART! Umumiy, zerikarli gaplarni (masalan: "Hayotda shunaqa", "Bugun ajoyib video") umuman yozma.
- Matn qisqa, odamni tortadigan va qiziqarli savol bilan tugasin.
- Hashtag umuman ishlatma.

Formati:
SUMMARY: (videoni chuqur tahlili)
CAPTION_A: (videoga to'liq mos yozilgan caption)"""
                response = model.generate_content([prompt, video_file])
                
                caption_a = caption
                summary = "Video haqida umumiy ma'lumot yo'q."
                
                if response.text:
                    full_text = response.text.strip()
                    if "CAPTION_A:" in full_text:
                        parts = full_text.split("CAPTION_A:")
                        summary = parts[0].replace("SUMMARY:", "").strip()
                        caption_a = parts[1].strip()
                    else:
                        caption_a = full_text
                    print("✅ Gemini Matni tayyor!")
                
                # Faylni tozalash
                genai.delete_file(video_file.name)
                print("🧹 Video Gemini serveridan o'chirib tashlandi.")
                
                print("🧠 Groq va OpenRouter ga ulanilmoqda (A/B Testing)...")
                caption_b = ai_assistant.generate_caption_groq(summary)
                caption_c = ai_assistant.generate_caption_openrouter(summary)
                
                if not caption_b: caption_b = caption_a + "\n\n(Groq ishlamadi, zaxira)"
                if not caption_c: caption_c = caption_a + "\n\n(OpenRouter ishlamadi, zaxira)"
                
                # Hashtaglarni to'g'ri biriktirish (Data-driven)
                caption_a = ai_assistant.append_viral_hashtags(caption_a)
                caption_b = ai_assistant.append_viral_hashtags(caption_b)
                caption_c = ai_assistant.append_viral_hashtags(caption_c)
                
                import json
                # Saqlash
                data = {
                    "video_name": video_name,
                    "caption_a": caption_a,
                    "caption_b": caption_b,
                    "caption_c": caption_c
                }
                with open(f"videos/pending/{video_name}.json", "w") as f:
                    json.dump(data, f)
                    
                # Telegramga yuborish
                tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
                tg_admin = os.getenv("TELEGRAM_ADMIN_ID")
                if tg_token and tg_admin:
                    import requests
                    msg = f"🎬 <b>Video tayyor: {video_name}</b>\n\nAI'lar jangi boshlandi! Qaysi matnni post qilamiz?\n\n"
                    msg += f"<b>🅰️ Gemini (Kreativ):</b>\n{caption_a}\n\n"
                    msg += f"<b>🅱️ Groq (SMM Ekspert):</b>\n{caption_b}\n\n"
                    msg += f"<b>©️ OpenRouter (Faylasuf):</b>\n{caption_c}"
                    
                    keyboard = json.dumps({
                        "inline_keyboard": [
                            [
                                {"text": "🅰️ A ni joylash", "callback_data": f"post_a_{video_name}"},
                                {"text": "🅱️ B ni joylash", "callback_data": f"post_b_{video_name}"}
                            ],
                            [
                                {"text": "©️ C ni joylash", "callback_data": f"post_c_{video_name}"},
                                {"text": "❌ Bekor qilish", "callback_data": f"cancel_{video_name}"}
                            ]
                        ]
                    })
                    
                    requests.post(f"https://api.telegram.org/bot{tg_token}/sendMessage", data={
                        "chat_id": tg_admin,
                        "text": msg,
                        "parse_mode": "HTML",
                        "reply_markup": keyboard
                    })
                    print("📩 Telegramga tasdiq so'rovi yuborildi.")
                    
                # To'xtaymiz. Tasdiq kelgach, boshqa fayl orqali joylanadi.
                return
                
        except Exception as e:
            print(f"\n⚠️ Gemini ishlatishda xatolik yuz berdi: {e}")
            continue

    # Agar Gemini umuman ishlamay qolsa, eski usulda birdaniga joylab yuboramiz. (Zaxira)
    print(f"📝 Instagramga joylanmoqda (Zaxira rejim)...")
    
    try:
        final_fallback_caption = ai_assistant.append_viral_hashtags(caption)
    except:
        final_fallback_caption = caption + "\n\n#rek #trend #uzbekistan #foryou #temurbekdev"
        
    ig_media_id = post_to_instagram(url, final_fallback_caption, video_name)
    
    first_comment = "Videodagi holat kimga tanish? 😂 Fikringizni yozib qoldiring 👇"
    if ig_media_id:
        from agent_tools import post_ig_comment
        post_ig_comment(ig_media_id, first_comment)
    
    print(f"📺 YouTubega joylanmoqda (Zaxira rejim)...")
    from youtube_api import YouTubeAPI
    yt_client_id = os.getenv("YOUTUBE_CLIENT_ID")
    yt_client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
    yt_refresh_token = os.getenv("YOUTUBE_REFRESH_TOKEN")
    
    if yt_client_id and yt_client_secret and yt_refresh_token:
        try:
            yt_api = YouTubeAPI(yt_client_id, yt_client_secret, yt_refresh_token)
            final_video_path = f"videos/posted/{video_name}" if ig_media_id else f"videos/pending/{video_name}"
            
            if os.path.exists(final_video_path):
                yt_video_id = yt_api.upload_shorts(final_video_path, "Kulgili Holat! 😂", final_fallback_caption)
                if yt_video_id:
                    yt_api.post_comment(yt_video_id, first_comment)
            else:
                print(f"❌ YouTube uchun fayl topilmadi: {final_video_path}")
        except Exception as e:
            print(f"⚠️ YouTube zaxira yuklashda xatolik: {e}")

if __name__ == "__main__":
    run()
