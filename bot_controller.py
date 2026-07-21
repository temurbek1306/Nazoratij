import os
import glob
import requests
import github_runner

def send_telegram_msg(text):
    tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
    tg_admin = os.getenv("TELEGRAM_ADMIN_ID")
    if tg_token and tg_admin:
        try:
            requests.post(f"https://api.telegram.org/bot{tg_token}/sendMessage", data={
                "chat_id": tg_admin,
                "text": text,
                "parse_mode": "HTML"
            })
        except Exception as e:
            print(f"Telegram xatosi: {e}")

def handle_list():
    os.makedirs("videos/pending", exist_ok=True)
    files = [f for f in os.listdir("videos/pending") if f.endswith(('.mp4', '.mov'))]
    if not files:
        send_telegram_msg("📭 Navbatda hech qanday video yo'q.")
        return
    
    msg = f"📋 <b>Navbatdagi videolar ({len(files)} ta):</b>\n\n"
    for i, f in enumerate(files, 1):
        msg += f"{i}. {f}\n"
    
    send_telegram_msg(msg)

def handle_clear():
    files = glob.glob("videos/pending/*")
    count = 0
    for f in files:
        if f.endswith(('.mp4', '.mov', '.txt')):
            os.remove(f)
            count += 1
            
    send_telegram_msg(f"🧹 <b>Navbat tozalandi!</b>\n\n{count} ta fayl o'chirib tashlandi.")

def handle_stats():
    os.makedirs("videos/posted", exist_ok=True)
    os.makedirs("videos/pending", exist_ok=True)
    
    # Local stats
    posted_files = [f for f in os.listdir("videos/posted") if f.endswith(('.mp4', '.mov'))]
    pending_files = [f for f in os.listdir("videos/pending") if f.endswith(('.mp4', '.mov'))]
    
    msg = "📊 <b>AvtoReels Statistikasi</b>\n\n"
    msg += f"✅ Joylangan videolar: <b>{len(posted_files)}</b> ta\n"
    msg += f"⏳ Kutilayotgan videolar: <b>{len(pending_files)}</b> ta\n\n"
    
    # YouTube stats
    yt_client_id = os.getenv("YOUTUBE_CLIENT_ID")
    yt_client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
    yt_refresh_token = os.getenv("YOUTUBE_REFRESH_TOKEN")
    
    if yt_client_id and yt_client_secret and yt_refresh_token:
        try:
            from youtube_api import YouTubeAPI
            yt_api = YouTubeAPI(yt_client_id, yt_client_secret, yt_refresh_token)
            yt_stats = yt_api.get_channel_stats()
            
            if yt_stats:
                msg += "📺 <b>YouTube Kanalingiz:</b>\n"
                msg += f"👥 Obunachilar: <b>{yt_stats['subscribers']}</b>\n"
                msg += f"👁 Prosmotrlar jami: <b>{yt_stats['views']}</b>\n"
                msg += f"🎥 Videolar jami: <b>{yt_stats['videos']}</b>\n"
            else:
                msg += "⚠️ <i>YouTube statistikasini olish imkonsiz (Ruxsat/Scope cheklangan bo'lishi mumkin)</i>"
        except Exception as e:
            msg += f"⚠️ <i>YouTube ma'lumotlarini olishda xatolik yuz berdi.</i>"
            
    send_telegram_msg(msg)

def run():
    command = os.getenv("TELEGRAM_COMMAND", "").lower().strip()
    prompt = os.getenv("TELEGRAM_PROMPT", "").strip()
    
    if not command:
        print("Hech qanday komanda berilmadi.")
        return
        
    print(f"Qabul qilingan komanda: {command}")
    
    if command == "list":
        handle_list()
    elif command == "clear":
        handle_clear()
    elif command == "stats":
        handle_stats()
    elif command == "post_now":
        send_telegram_msg("🚀 AI'lar jangi boshlanmoqda! (30-40 soniya...)")
        github_runner.run()
    elif command.startswith("post_a_") or command.startswith("post_b_") or command.startswith("post_c_") or command.startswith("cancel_"):
        send_telegram_msg("🚀 Tasdiqlandi! Yakuniy post jarayoni boshlandi...")
        import github_runner_approved
        github_runner_approved.run()
    elif command == "strategy":
        try:
            import ai_assistant
            import requests
            send_telegram_msg("🧠 AI Profilingizni analiz qilmoqda... (Kuting)")
            
            ig_token = os.getenv("IG_ACCESS_TOKEN")
            ig_account_id = os.getenv("IG_ACCOUNT_ID")
            
            profile_data = "Ayni paytda Instagram hisobi ulanmagan yoki postlar yo'q. Shuning uchun umumiy trendlarga asoslan!"
            if ig_token and ig_account_id:
                try:
                    url = f"https://graph.facebook.com/v18.0/{ig_account_id}/media?fields=caption,like_count,comments_count,media_type&limit=15&access_token={ig_token}"
                    res = requests.get(url).json()
                    if "data" in res and len(res["data"]) > 0:
                        posts = res["data"]
                        sorted_posts = sorted(posts, key=lambda x: x.get('like_count', 0), reverse=True)
                        top_posts = sorted_posts[:3]
                        profile_data = "Foydalanuvchining Instagramdagi eng omadli (Top 3) postlari haqida faktik ma'lumotlar:\n"
                        for i, p in enumerate(top_posts):
                            cpt = p.get('caption', 'Sarlavha yoq')[:150].replace('\n', ' ')
                            lks = p.get('like_count', 0)
                            cms = p.get('comments_count', 0)
                            profile_data += f"{i+1}-post. Layklar: {lks}, Kommentlar: {cms}. Sarlavhasi: '{cpt}'\n"
                except Exception as e:
                    print("IG Data fetch error:", e)
            
            ai_response = ai_assistant.generate_data_driven_strategy(profile_data)
            if not ai_response: ai_response = "Kechirasiz, Groq ishlamadi."
            send_telegram_msg("📊 <b>Analiz Yakunlandi! 30 Kunlik Kontent Rejangiz:</b>\n\n" + ai_response)
        except Exception as e:
            send_telegram_msg(f"⚠️ Xatolik: {e}")
    elif command == "brainstorm":
        if prompt.startswith("http"):
            send_telegram_msg("📥 Bu linkka o'xshaydi. Link orqali yuklab olish funksiyasi tez kunda (Keyingi qadamda) qo'shiladi!")
        else:
            try:
                import ai_assistant
                ai_response = ai_assistant.brainstorm_idea(prompt)
                send_telegram_msg(ai_response)
            except Exception as e:
                send_telegram_msg(f"⚠️ AI yordamchisida xatolik: {e}")
    else:
        send_telegram_msg("❓ Noma'lum komanda.")

if __name__ == "__main__":
    run()
