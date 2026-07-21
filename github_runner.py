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
    
    local_video_path = f"videos/pending/{video_name}"
    
    # Standart xeshteglar bilan zaxira (fallback) caption
    caption = "Yana bir ajoyib video! 😂 Sizda ham shunday holatlar bo'lganmi? 👇 \n\nFikringizni izohlarda qoldiring!\n\n#rek #rekka #kino #dasturlash #temurbekdev #trend #uzbekistan #foryou"
    
    import ai_assistant
    km = ai_assistant.KeyManager()
    gemini_key = km.get_gemini_key()
    
    if gemini_key:
        try:
            import google.generativeai as genai
            print("🧠 Gemini AI ishga tushmoqda...")
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
                prompt = "Shu videoni diqqat bilan ko'r va eshit. Yuzidagi yozuvlar va audiodagi gaplardan kelib chiqib, avval videoning to'liq ma'nosini (summary) yoz. Keyin esa Instagram Reels uchun odamlarni o'ziga tortadigan, qiziqarli o'zbekcha izoh (caption) yoz. Formati shunday bo'lsin:\n\nSUMMARY: (video haqida ma'lumot)\nCAPTION_A: (sen yozgan zo'r caption)"
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
            print(f"\n⚠️ Gemini ishlatishda xatolik yuz berdi (shablondan foydalaniladi): {e}")

    # Agar Gemini ishlamay qolsa (exception bo'lsa), eski usulda birdaniga joylab yuboramiz. (Zaxira)
    print(f"📝 Instagramga joylanmoqda (Zaxira rejim)...")
    success = post_to_instagram(url, caption, video_name)

if __name__ == "__main__":
    run()
